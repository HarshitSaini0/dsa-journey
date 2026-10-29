window.DSA_API = {
  async fetchState() {
    try {
      const res = await fetch("/api/problems");
      if (!res.ok) throw new Error("Fallback to static mode");
      return await res.json();
    } catch (_) {
      // Static fallback if hosted on GitHub Pages without server.py
      const res = await fetch("../README.md");
      const text = res.ok ? await res.text() : "";
      return { problems: window.DSA_FN.parseReadmeMarkdown(text), draft: "" };
    }
  },

  async generateAIDraft(url, code, notes) {
    const res = await fetch("/api/generate-draft", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, code, notes }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to generate AI draft");
    return data.draft;
  },

  async forgeSolution(draft, code, parsed) {
    const res = await fetch("/api/forge", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ draft, code, parsed }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Forge failed");
    return data;
  },

  async fetchCodeFile(relPath) {
    const res = await fetch(`/api/file?path=${encodeURIComponent(relPath)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not load file");
    return data;
  },

  async gitSync(message) {
    const res = await fetch("/api/git-sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Git sync failed");
    return data.output;
  }
};