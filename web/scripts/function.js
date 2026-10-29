window.DSA_FN = {
  BLANK_TEMPLATE: `TITLE: 
URL: 
PATTERN: arrays-hashing
DIFFICULTY: Medium
LANG: py
TAKEAWAY: 
REVISIT: 🔴

=== DESCRIPTION ===

=== TRAP ===

=== TRIGGER ===

=== TIME_COMPLEXITY ===
O() -> 

=== SPACE_COMPLEXITY ===
O() -> 

=== WHAT_ELSE ===
`,

  parseDraftText(raw) {
    const getLine = (key, def = "") => {
      const m = raw.match(new RegExp(`^${key}:\\s*(.*)$`, "m"));
      return m && m[1].trim() ? m[1].trim() : def;
    };
    const getSec = (header) => {
      const m = raw.match(new RegExp(`===\\s*${header}\\s*===\\n([\\s\\S]*?)(?=\\n===\\s*[A-Z_]+\\s*===|$)`));
      return m ? m[1].trim() : "";
    };
    return {
      title: getLine("TITLE"),
      url: getLine("URL", "N/A"),
      pattern: getLine("PATTERN", "misc"),
      difficulty: getLine("DIFFICULTY", "Medium"),
      lang: getLine("LANG", "py"),
      takeaway: getLine("TAKEAWAY", "*TODO: Add key takeaway*"),
      revisit: getLine("REVISIT", "🔴"),
      description: getSec("DESCRIPTION"),
      trap: getSec("TRAP"),
      trigger: getSec("TRIGGER"),
      time_comp: getSec("TIME_COMPLEXITY") || "O()",
      space_comp: getSec("SPACE_COMPLEXITY") || "O()",
      what_else: getSec("WHAT_ELSE"),
    };
  },

  parseReadmeMarkdown(md) {
    const rows = [];
    md.split("\n").forEach((line) => {
      const t = line.trim();
      if (!t.startsWith("|") || t.includes("1-Sentence Takeaway") || t.includes(":---")) return;
      const parts = t.replace(/^\||\|$/g, "").split("|").map((s) => s.trim());
      if (parts.length >= 7) {
        const pm = parts[1].match(/\[(.*?)\]\((.*?)\)/);
        const cm = parts[6].match(/\((.*?)\)/);
        rows.push({
          date: parts[0],
          title: pm ? pm[1] : parts[1],
          url: pm ? pm[2] : "",
          pattern: parts[2].replace(/`/g, ""),
          difficulty: parts[3],
          takeaway: parts[4],
          revisit: parts[5],
          code_path: cm ? cm[1] : "",
        });
      }
    });
    return rows.reverse();
  },

  escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }
};