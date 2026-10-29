#!/usr/bin/env python3
from datetime import datetime
import os
import re
import subprocess
import sys

DRAFT_FILE = "problem_draft.txt"

PATTERNS = [
    "arrays-hashing",
    "two-pointers",
    "sliding-window",
    "stack",
    "binary-search",
    "linked-list",
    "trees",
    "tries",
    "heap-priority-queue",
    "backtracking",
    "graphs",
    "dynamic-programming",
    "greedy",
    "intervals",
    "math-geometry",
    "bit-manipulation",
]

DIFFICULTIES = ["Easy", "Medium", "Hard"]
LANGUAGES = ["py", "cpp", "ts", "java"]

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

CODE_TEMPLATES = {
    "py": '''"""
Problem: {title}
Link: {url}
Pattern: {pattern}
Difficulty: {difficulty}
Date: {date}

--- PROBLEM DESCRIPTION ---
{description}

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   {trap}

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   {trigger}

3. Complexity:
   - Time: {time_comp}
   - Space: {space_comp}

4. What Else? (Alternative approaches or trade-offs):
   {what_else}
"""

from typing import List, Optional

class Solution:
    def solve(self):
        pass

if __name__ == "__main__":
    sol = Solution()
    # Test cases here
''',
    "cpp": """/*
Problem: {title}
Link: {url}
Pattern: {pattern}
Difficulty: {difficulty}
Date: {date}

--- PROBLEM DESCRIPTION ---
{description}

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   {trap}

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   {trigger}

3. Complexity:
   - Time: {time_comp}
   - Space: {space_comp}

4. What Else? (Alternative approaches or trade-offs):
   {what_else}
*/

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

class Solution {{
public:
    void solve() {{
        
    }}
}};

int main() {{
    Solution sol;
    return 0;
}}
""",
    "ts": """/*
Problem: {title}
Link: {url}
Pattern: {pattern}
Difficulty: {difficulty}
Date: {date}

--- PROBLEM DESCRIPTION ---
{description}

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   {trap}

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   {trigger}

3. Complexity:
   - Time: {time_comp}
   - Space: {space_comp}

4. What Else? (Alternative approaches or trade-offs):
   {what_else}
*/

function solve(): void {{
    
}}
""",
    "java": """/*
Problem: {title}
Link: {url}
Pattern: {pattern}
Difficulty: {difficulty}
Date: {date}

--- PROBLEM DESCRIPTION ---
{description}

--- THOUGHT PROCESS ---
1. The Trap (Initial brute-force / wrong intuition / edge case missed):
   {trap}

2. The Trigger (What constraint or keyword pointed to the optimal approach?):
   {trigger}

3. Complexity:
   - Time: {time_comp}
   - Space: {space_comp}

4. What Else? (Alternative approaches or trade-offs):
   {what_else}
*/

import java.util.*;

public class {class_name} {{
    public void solve() {{
        
    }}

    public static void main(String[] args) {{
        {class_name} sol = new {class_name}();
    }}
}}
""",
}

README_HEADER = """# Daily DSA Log & Pattern Tracker

| Date | Problem | Pattern | Difficulty | 1-Sentence Takeaway | Revisit? | Solution |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
"""


def slugify(text: str) -> str:
  text = text.lower().strip()
  text = re.sub(r"[^\w\s-]", "", text)
  return re.sub(r"[-\s]+", "_", text)


def ensure_draft_file():
  if not os.path.exists(DRAFT_FILE):
    with open(DRAFT_FILE, "w", encoding="utf-8") as f:
      f.write(DRAFT_TEMPLATE)
    print(f"📄 Created staging file: '{DRAFT_FILE}'")


def choose_from_list(prompt: str, options: list, default_idx: int = 0) -> str:
  print(f"\n{prompt}")
  for idx, opt in enumerate(options, 1):
    marker = "*" if idx - 1 == default_idx else " "
    print(f"  [{idx}]{marker} {opt}")
  choice = input(
      f"Select number (or type custom) [default: {options[default_idx]}]: "
  ).strip()
  if not choice:
    return options[default_idx]
  if choice.isdigit() and 1 <= int(choice) <= len(options):
    return options[int(choice) - 1]
  return choice


def prompt_interactive() -> dict:
  print("\n--- 🛠️  Interactive Mode ---")
  title = ""
  while not title:
    title = input("1. Problem Title (e.g., '15. 3Sum'): ").strip()

  url = input("2. Problem URL [Enter to skip]: ").strip() or "N/A"
  pattern = choose_from_list("3. Choose Pattern:", PATTERNS, default_idx=0)
  difficulty = choose_from_list(
      "4. Choose Difficulty:", DIFFICULTIES, default_idx=1
  )
  lang = choose_from_list("5. Choose Language:", LANGUAGES, default_idx=0)

  print(
      "\n--- 🧠 Optional Reflection & Details (Press Enter to fill inside code"
      " later) ---"
  )
  description = (
      input("6. Short Problem Description/Summary: ").strip()
      or "TODO: Add short summary"
  )
  trap = input("7. The Trap (Initial wrong intuition / edge case): ").strip()
  trigger = input("8. The Trigger (What pointed to optimal approach?): ").strip()
  time_comp = input("9. Time Complexity (e.g., O(n)): ").strip() or "O()"
  space_comp = input("10. Space Complexity (e.g., O(1)): ").strip() or "O()"
  what_else = input("11. What Else? (Alternative approaches): ").strip()
  takeaway = (
      input("12. 1-Sentence Takeaway for README table: ").strip()
      or "*TODO: Add key takeaway*"
  )
  revisit = (
      choose_from_list("13. Revisit Status:", ["🔴", "🟡", "🟢"], default_idx=0)
  )

  return {
      "title": title,
      "url": url,
      "pattern": pattern,
      "difficulty": difficulty,
      "lang": lang,
      "description": description,
      "trap": trap,
      "trigger": trigger,
      "time_comp": time_comp,
      "space_comp": space_comp,
      "what_else": what_else,
      "takeaway": takeaway,
      "revisit": revisit,
  }


def parse_draft_file() -> dict:
  ensure_draft_file()
  with open(DRAFT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

  def extract_line(key: str, default: str = "") -> str:
    match = re.search(rf"^{key}:\s*(.*)$", content, re.MULTILINE)
    return match.group(1).strip() if match and match.group(1).strip() else default

  def extract_section(header: str) -> str:
    pattern = rf"===\s*{header}\s*===\n(.*?)(?=\n===\s*[A-Z_]+\s*===|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    return match.group(1).strip() if match else ""

  title = extract_line("TITLE")
  if not title:
    print(
        f"❌ Error: 'TITLE:' is empty inside '{DRAFT_FILE}'. Fill it in and run"
        " again!"
    )
    sys.exit(1)

  return {
      "title": title,
      "url": extract_line("URL", "N/A"),
      "pattern": extract_line("PATTERN", "misc"),
      "difficulty": extract_line("DIFFICULTY", "Medium"),
      "lang": extract_line("LANG", "py").lower(),
      "takeaway": extract_line("TAKEAWAY", "*TODO: Add key takeaway*"),
      "revisit": extract_line("REVISIT", "🔴"),
      "description": extract_section("DESCRIPTION"),
      "trap": extract_section("TRAP"),
      "trigger": extract_section("TRIGGER"),
      "time_comp": extract_section("TIME_COMPLEXITY") or "O()",
      "space_comp": extract_section("SPACE_COMPLEXITY") or "O()",
      "what_else": extract_section("WHAT_ELSE"),
  }


def update_readme(date: str, data: dict, rel_path: str):
  readme_path = "README.md"
  if not os.path.exists(readme_path):
    with open(readme_path, "w", encoding="utf-8") as f:
      f.write(README_HEADER)

  problem_col = (
      f"[{data['title']}]({data['url']})"
      if data["url"] != "N/A"
      else data["title"]
  )
  new_row = (
      f"| {date} | {problem_col} | `{data['pattern']}` | {data['difficulty']}"
      f" | {data['takeaway']} | {data['revisit']} | [Code]({rel_path}) |\n"
  )

  with open(readme_path, "a", encoding="utf-8") as f:
    f.write(new_row)


def main():
  ensure_draft_file()
  print("=========================================")
  print("   🚀 DSA Forge - Daily Solution Maker   ")
  print("=========================================")
  print("How would you like to create today's entry?")
  print("  [1] Interactive CLI (Ask me step-by-step)")
  print(f"  [2] Load from staging file ('{DRAFT_FILE}')")
  print(f"  [3] Reset '{DRAFT_FILE}' to a fresh blank template")

  mode = input("\nSelect option [1/2/3]: ").strip()

  if mode == "3":
    with open(DRAFT_FILE, "w", encoding="utf-8") as f:
      f.write(DRAFT_TEMPLATE)
    print(f"✨ Reset '{DRAFT_FILE}' to a blank template!")
    return
  elif mode == "2":
    data = parse_draft_file()
  else:
    data = prompt_interactive()

  date_str = datetime.now().strftime("%Y-%m-%d")
  folder_name = slugify(data["pattern"]).replace("_", "-")
  base_slug = slugify(data["title"])
  class_name = "S_" + base_slug if base_slug[0].isdigit() else base_slug.title().replace("_", "")
  file_name = f"{base_slug}.{data['lang']}"

  os.makedirs(folder_name, exist_ok=True)
  file_path = os.path.join(folder_name, file_name)
  rel_path = f"./{folder_name}/{file_name}"

  if os.path.exists(file_path):
    print(f"\n⚠️  File already exists: {file_path}")
  else:
    lang_key = data["lang"] if data["lang"] in CODE_TEMPLATES else "py"
    content = CODE_TEMPLATES[lang_key].format(
        title=data["title"],
        url=data["url"],
        pattern=folder_name,
        difficulty=data["difficulty"],
        date=date_str,
        description=data["description"],
        trap=data["trap"],
        trigger=data["trigger"],
        time_comp=data["time_comp"],
        space_comp=data["space_comp"],
        what_else=data["what_else"],
        class_name=class_name,
    )
    with open(file_path, "w", encoding="utf-8") as f:
      f.write(content)
    print(f"\n✅ Created solution file: {file_path}")

    update_readme(date_str, data, rel_path)
    print("📝 Added row to root README.md")

    if mode == "2":
      reset = (
          input(f"\nReset '{DRAFT_FILE}' for tomorrow's problem? (y/N): ")
          .strip()
          .lower()
      )
      if reset == "y":
        with open(DRAFT_FILE, "w", encoding="utf-8") as f:
          f.write(DRAFT_TEMPLATE)
        print(f"✨ '{DRAFT_FILE}' wiped clean for tomorrow.")

  try:
    subprocess.run(["code", file_path], check=False)
  except FileNotFoundError:
    pass


if __name__ == "__main__":
  main()