#!/usr/bin/env python3
import argparse
import os
import re
import sys
from google import genai
import requests

DRAFT_FILE = "problem_draft.txt"

SYSTEM_PROMPT = """You are an expert DSA analysis agent. Given a LeetCode problem's metadata and the user's code solution, output ONLY the raw text in the exact format below. Do NOT wrap the output in markdown backticks (```).

TITLE: <questionFrontendId>. <title>
URL: <url>
PATTERN: <Choose arrays-hashing, backtracking, binary-search, bit-manipulation dynamic-programming, graphs, greedy, heap-priority-queue, intervals, linked-list, math-geometry, one: sliding-window, stack, strictly trees, tries, two-pointers,>
DIFFICULTY: <Easy, Hard Medium, or>
LANG: <py, cpp, ts, or java>
TAKEAWAY: <1-sentence core algorithmic trick, max 20 words, no '|' character>
REVISIT: <🔴 if user code is suboptimal/buggy, 🟡 if optimal but tricky, 🟢 if clean and optimal>

=== DESCRIPTION ===
<Clean 2-3 and constraints input key of problem sentence statement summary the>

=== TRAP ===
<Explain brute-force bugs/inefficiencies cases, code common edge found in or specific submitted subtle the trap, user's>

=== TRIGGER ===
<Explain constraint directly in keyword optimal or pattern points problem specific the to which>

=== TIME_COMPLEXITY ===
O(...) -> <1-sentence explanation of the user's code time complexity>

=== SPACE_COMPLEXITY ===
O(...) -> <1-sentence explanation of the user's code space complexity>

=== WHAT_ELSE ===
<Alternative approaches, code how if it optimal optimize or space/time the to trade-offs, user's wasn't>
"""


def clean_url(raw_url: str) -> str:
  """Strips accidental markdown link formatting like [https://...](https://...)"""
  raw_url = raw_url.strip()
  md_match = re.search(r"\((https?://[^\s\)]+)\)", raw_url)
  if md_match:
    return md_match.group(1)
  return raw_url.strip("[]()")


def load_dotenv(dotenv_path: str = ".env"):
  """Reads key=value pairs from .env into os.environ."""
  if not os.path.exists(dotenv_path):
    return
  with open(dotenv_path, "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if not line or line.startswith("#") or "=" not in line:
        continue
      if line.startswith("export "):
        line = line[len("export ") :].strip()
      key, val = line.split("=", 1)
      key = key.strip()
      val = val.strip().strip("'").strip('"')
      os.environ.setdefault(key, val)


def fetch_leetcode_metadata(url: str) -> dict:
  """Fetches official problem details from LeetCode's GraphQL API using the URL slug."""
  url = clean_url(url)
  match = re.search(r"leetcode\.com/problems/([^/?#]+)", url)
  if not match:
    return {"title": "Unknown", "difficulty": "Unknown", "content": "Not found"}

  slug = match.group(1)
  # Constructed via string join so copy-paste never turns it into a markdown link
  graphql_url = "https://" + "[leetcode.com/graphql](https://leetcode.com/graphql)"
  query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        difficulty
        content
      }
    }
    """
  try:
    resp = requests.post(
        graphql_url,
        json={"query": query, "variables": {"titleSlug": slug}},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    data = resp.json().get("data", {}).get("question", {})
    if not data:
      return {"title": slug, "difficulty": "Medium", "content": ""}

    clean_html = re.sub(r"<[^>]+>", "", data.get("content", "") or "")
    return {
        "id": data.get("questionFrontendId", ""),
        "title": (
            f"{data.get('questionFrontendId', '')}. {data.get('title', slug)}"
        ),
        "difficulty": data.get("difficulty", "Medium"),
        "content": clean_html[:2000],
    }
  except Exception as e:
    print(
        f"⚠️ Could not fetch LeetCode API metadata ({e}). Relying on LLM"
        " knowledge."
    )
    return {"title": slug, "difficulty": "Medium", "content": ""}


def read_multiline_code() -> str:
  """Reads pasted code until the user types END or DONE on a new line."""
  print(
      "📋 Paste your solution code below. When finished, type END on a new"
      " line and press Enter:"
  )
  lines = []
  while True:
    try:
      line = input()
      if line.strip().upper() in ("END", "DONE", "EOF"):
        break
      lines.append(line)
    except EOFError:
      break
  return "\n".join(lines).strip()


def main():
  load_dotenv()

  parser = argparse.ArgumentParser(
      description="AI Agent to generate problem_draft.txt from URL + Code"
  )
  parser.add_argument("url", help="LeetCode problem URL")
  parser.add_argument(
      "-f",
      "--file",
      help="Path to file containing your raw solution code",
  )
  parser.add_argument(
      "-n",
      "--notes",
      default="",
      help="Optional rough note on where you got stuck",
  )
  args = parser.parse_args()

  cleaned_url = clean_url(args.url)

  api_key = (
      os.environ.get("GEMINI_API_KEY")
      or os.environ.get("GOOGLE_API_KEY")
      or os.environ.get("API_KEY")
  )
  if not api_key:
    print("❌ Error: Could not find GEMINI_API_KEY in .env or environment.")
    sys.exit(1)

  if args.file and os.path.exists(args.file):
    with open(args.file, "r", encoding="utf-8") as f:
      user_code = f.read().strip()
  else:
    user_code = read_multiline_code()

  if not user_code:
    print("❌ Error: No solution code provided.")
    sys.exit(1)

  print("🔍 Fetching problem details from LeetCode...")
  lc_data = fetch_leetcode_metadata(cleaned_url)

  print("🧠 Analyzing your solution and generating reflection...")
  try:
    client = genai.Client(api_key=api_key)
    user_prompt = f"""
LeetCode URL: {cleaned_url}
Fetched Title: {lc_data.get('title')}
Fetched Difficulty: {lc_data.get('difficulty')}
Fetched Problem Statement:
{lc_data.get('content')}

User's Rough Notes / Struggles:
{args.notes if args.notes else "None provided — infer from code."}

User's Submitted Solution Code:
{user_code}
"""
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )
    draft_output = response.text.strip()
  except Exception as e:
    print(f"\n❌ Gemini API Error: {e}")
    print(
        "💡 Tip: Check that your GEMINI_API_KEY in .env is a valid Google AI"
        " Studio key (starts with 'AIzaSy...')."
    )
    sys.exit(1)

  draft_output = re.sub(r"^```[a-zA-Z]*\n", "", draft_output)
  draft_output = re.sub(r"\n```$", "", draft_output)

  with open(DRAFT_FILE, "w", encoding="utf-8") as f:
    f.write(draft_output + "\n")

  print(f"\n✅ Successfully generated '{DRAFT_FILE}'!")
  print("👉 Now run './dsa_forge.py' and choose Option [2] to build your file.")


if __name__ == "__main__":
  main()