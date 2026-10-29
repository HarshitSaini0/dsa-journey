#!/usr/bin/env python3
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
import subprocess
from urllib.parse import parse_qs, urlparse
import requests

PORT = 8080
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
DRAFT_FILE = "problem_draft.txt"

README_HEADER = """# Daily DSA Log & Pattern Tracker

| Date | Problem | Pattern | Difficulty | 1-Sentence Takeaway | Revisit? | Solution |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
"""

DRAFT_TEMPLATE = """TITLE: 
URL: 
PATTERN: arrays-hashing
DIFFICULTY: Medium
LANG: py
TAKEAWAY: 
REVISIT: 🔴

=== DESCRIPTION ===
Paste or summarize the problem description here...

=== TRAP ===
What was your initial brute-force, wrong intuition, or edge case missed?

=== TRIGGER ===
What constraint or keyword pointed to the optimal approach?

=== TIME_COMPLEXITY ===
O() -> 

=== SPACE_COMPLEXITY ===
O() -> 

=== WHAT_ELSE ===
Alternative approaches or trade-offs...
"""

SYSTEM_PROMPT = """You are an expert DSA analysis agent. Given a LeetCode problem's metadata and the user's code solution, output ONLY the raw text in the exact format below. Do NOT wrap the output in markdown backticks (```).

TITLE: <questionFrontendId>. <title>
URL: <url>
PATTERN: <Choose arrays-hashing, backtracking, binary-search, bit-manipulation dynamic-programming, graphs, greedy, heap-priority-queue, intervals, linked-list, math-geometry, one: sliding-window, stack, strictly trees, tries, two-pointers,>
DIFFICULTY: <Easy, Hard Medium, or>
LANG: <py, cpp, ts, or java>
TAKEAWAY: <1-sentence core algorithmic trick, max 20 words, no '|' character>
REVISIT: <🔴 if user code is suboptimal/buggy, 🟡 if optimal but tricky, 🟢 if clean and optimal>

=== DESCRIPTION ===
<Clean 2-3 and constraints key of problem sentence statement summary the>

=== TRAP ===
<Explain brute-force bugs, by cases code edge inefficiencies, missed or the user's>

=== TRIGGER ===
<Explain constraint directly keyword optimal or pattern points that the to>

=== TIME_COMPLEXITY ===
O(...) -> <1-sentence explanation of time complexity>

=== SPACE_COMPLEXITY ===
O(...) -> <1-sentence explanation of space complexity>

=== WHAT_ELSE ===
<Alternative approaches or trade-offs>
"""


def slugify(text: str) -> str:
  text = text.lower().strip()
  text = re.sub(r"[^\w\s-]", "", text)
  return re.sub(r"[-\s]+", "_", text)


def clean_url(raw_url: str) -> str:
  raw_url = raw_url.strip()
  md_match = re.search(r"\((https?://[^\s\)]+)\)", raw_url)
  if md_match:
    return md_match.group(1)
  return raw_url.strip("[]()")


def load_dotenv(dotenv_path: str = ".env"):
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
      os.environ.setdefault(key.strip(), val.strip().strip("'").strip('"'))


def fetch_leetcode_metadata(url: str) -> dict:
  url = clean_url(url)
  match = re.search(r"leetcode\.com/problems/([^/?#]+)", url)
  if not match:
    return {"title": "Unknown", "difficulty": "Medium", "content": ""}

  slug = match.group(1)
  graphql_url = "[https://leetcode.com/graphql](https://leetcode.com/graphql)"
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
        "title": (
            f"{data.get('questionFrontendId', '')}. {data.get('title', slug)}"
        ),
        "difficulty": data.get("difficulty", "Medium"),
        "content": clean_html[:2000],
    }
  except Exception:
    return {"title": slug, "difficulty": "Medium", "content": ""}


def build_code_file_content(
    lang: str, meta: dict, date_str: str, user_code: str
) -> str:
  header_block = f"""Problem: {meta['title']}
Link: {meta['url']}
Pattern: {meta['pattern']}
Difficulty: {meta['difficulty']}
Date: {date_str}

--- PROBLEM DESCRIPTION ---
{meta['description']}

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   {meta['trap']}

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   {meta['trigger']}

3. Complexity:
   - Time: {meta['time_comp']}
   - Space: {meta['space_comp']}

4. What Else? (Alternative approaches or trade-offs):
   {meta['what_else']}"""

  code_body = (
      user_code.strip() if user_code.strip() else "# TODO: Paste solution here"
  )
  if lang == "py":
    return f'"""\n{header_block}\n"""\n\n{code_body}\n'
  else:
    return f"/*\n{header_block}\n*/\n\n{code_body}\n"


def parse_readme_rows() -> list:
  if not os.path.exists("README.md"):
    return []
  rows = []
  with open("README.md", "r", encoding="utf-8") as f:
    for line in f:
      line = line.strip()
      if (
          not line.startswith("|")
          or "1-Sentence Takeaway" in line
          or ":---" in line
      ):
        continue
      parts = [p.strip() for p in line.strip("|").split("|")]
      if len(parts) >= 7:
        prob_match = re.match(r"\[(.*?)\]\((.*?)\)", parts[1])
        title = prob_match.group(1) if prob_match else parts[1]
        url = prob_match.group(2) if prob_match else ""
        code_match = re.search(r"\((.*?)\)", parts[6])
        code_path = code_match.group(1) if code_match else ""
        rows.append({
            "date": parts[0],
            "title": title,
            "url": url,
            "pattern": parts[2].strip("`"),
            "difficulty": parts[3],
            "takeaway": parts[4],
            "revisit": parts[5],
            "code_path": code_path,
        })
  return rows[::-1]


class DSAHandler(SimpleHTTPRequestHandler):

  def translate_path(self, path):
    parsed = urlparse(path).path
    if parsed == "/raw-readme":
      return os.path.abspath("README.md")
    full_web = os.path.join(WEB_DIR, parsed.lstrip("/"))
    if os.path.exists(full_web) and not os.path.isdir(full_web):
      return full_web
    return os.path.join(WEB_DIR, "index.html")

  def send_json(self, payload: dict, status: int = 200):
    body = json.dumps(payload).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def do_GET(self):
    parsed = urlparse(self.path)
    if parsed.path == "/api/problems":
      if not os.path.exists(DRAFT_FILE):
        with open(DRAFT_FILE, "w", encoding="utf-8") as f:
          f.write(DRAFT_TEMPLATE)
      with open(DRAFT_FILE, "r", encoding="utf-8") as f:
        draft_content = f.read()
      return self.send_json(
          {"problems": parse_readme_rows(), "draft": draft_content}
      )

    if parsed.path == "/api/file":
      qs = parse_qs(parsed.query)
      rel_path = qs.get("path", [""])[0].lstrip("./")
      abs_path = os.path.abspath(rel_path)
      repo_root = os.path.abspath(".")
      if not abs_path.startswith(repo_root) or not os.path.isfile(abs_path):
        return self.send_json({"error": "File not found"}, 404)
      with open(abs_path, "r", encoding="utf-8") as f:
        return self.send_json({"path": rel_path, "content": f.read()})

    return super().do_GET()

  def do_POST(self):
    length = int(self.headers.get("Content-Length", 0))
    body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")

    if self.path == "/api/generate-draft":
      load_dotenv()
      api_key = (
          os.environ.get("GEMINI_API_KEY")
          or os.environ.get("GOOGLE_API_KEY")
          or os.environ.get("API_KEY")
      )
      if not api_key:
        return self.send_json({"error": "Missing GEMINI_API_KEY in .env"}, 400)

      url = clean_url(body.get("url", ""))
      code = body.get("code", "").strip()
      notes = body.get("notes", "").strip()
      if not url or not code:
        return self.send_json(
            {"error": "Both LeetCode URL and Solution Code are required."}, 400
        )

      lc_data = fetch_leetcode_metadata(url)
      user_prompt = (
          f"LeetCode URL: {url}\nFetched Title:"
          f" {lc_data.get('title')}\nFetched Difficulty:"
          f" {lc_data.get('difficulty')}\nFetched Problem"
          f" Statement:\n{lc_data.get('content')}\n\nUser's Rough"
          f" Notes:\n{notes or 'None'}\n\nUser's Submitted Solution"
          f" Code:\n{code}"
      )

      try:
        from google import genai

        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT, temperature=0.2
            ),
        )
        draft_text = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", resp.text.strip())
        with open(DRAFT_FILE, "w", encoding="utf-8") as f:
          f.write(draft_text + "\n")
        return self.send_json({"draft": draft_text})
      except Exception as e:
        return self.send_json({"error": str(e)}, 500)

    if self.path == "/api/forge":
      draft_text = body.get("draft", "").strip()
      user_code = body.get("code", "").strip()
      meta = body.get("parsed", {})
      if not meta.get("title"):
        return self.send_json({"error": "TITLE is missing in draft."}, 400)

      with open(DRAFT_FILE, "w", encoding="utf-8") as f:
        f.write(draft_text + "\n")

      date_str = datetime.now().strftime("%Y-%m-%d")
      folder_name = slugify(meta.get("pattern", "misc")).replace("_", "-")
      base_slug = slugify(meta["title"])
      lang = meta.get("lang", "py").lower()
      file_name = f"{base_slug}.{lang}"

      os.makedirs(folder_name, exist_ok=True)
      file_path = os.path.join(folder_name, file_name)
      rel_path = f"./{folder_name}/{file_name}"

      full_code = build_code_file_content(lang, meta, date_str, user_code)
      with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_code)

      if not os.path.exists("README.md"):
        with open("README.md", "w", encoding="utf-8") as f:
          f.write(README_HEADER)

      clean_takeaway = (
          meta.get("takeaway", "").replace("|", "-").replace("\n", " ").strip()
      )
      prob_col = (
          f"[{meta['title']}]({meta['url']})"
          if meta.get("url") and meta["url"] != "N/A"
          else meta["title"]
      )
      new_row = (
          f"| {date_str} | {prob_col} | `{folder_name}` |"
          f" {meta.get('difficulty', 'Medium')} | {clean_takeaway} |"
          f" {meta.get('revisit', '🔴')} | [Code]({rel_path}) |\n"
      )

      with open("README.md", "r", encoding="utf-8") as f:
        lines = f.readlines()

      updated = False
      for i, line in enumerate(lines):
        if f"({rel_path})" in line:
          lines[i] = new_row
          updated = True
          break
      if not updated:
        lines.append(new_row)

      with open("README.md", "w", encoding="utf-8") as f:
        f.writelines(lines)

      return self.send_json({"status": "ok", "file_path": rel_path})

    if self.path == "/api/git-sync":
      msg = (
          body.get("message", "").strip()
          or f"feat(dsa): daily log update {datetime.now().strftime('%Y-%m-%d')}"
      )
      try:
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(
            ["git", "add", "--all", ":!.env", f":!{DRAFT_FILE}"], check=True
        )
        commit_res = subprocess.run(
            ["git", "commit", "-m", msg], capture_output=True, text=True
        )
        push_res = subprocess.run(
            ["git", "push"], capture_output=True, text=True
        )
        return self.send_json({
            "output": (
                (commit_res.stdout or commit_res.stderr)
                + "\n"
                + (push_res.stdout or push_res.stderr)
            ).strip()
        })
      except Exception as e:
        return self.send_json({"error": str(e)}, 500)


if __name__ == "__main__":
  print(f"⚡ DSA Workbench running at http://localhost:{PORT}")
  ThreadingHTTPServer(("127.0.0.1", PORT), DSAHandler).serve_forever()