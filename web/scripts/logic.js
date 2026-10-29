(async function initApp() {
  const state = { problems: [], draft: "" };

  async function loadComponent(mountId, path) {
    const res = await fetch(path);
    document.getElementById(mountId).innerHTML = await res.text();
  }

  await Promise.all([
    loadComponent("mount-header", "components/header.html"),
    loadComponent("mount-workspace", "components/workspace.html"),
    loadComponent("mount-dashboard", "components/dashboard.html"),
  ]);

  const banner = document.getElementById("status-banner");
  function notify(msg, isError = false) {
    banner.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    banner.style.color = isError ? "#da3633" : "#e6edf3";
    banner.classList.remove("hidden");
  }

  function switchTab(targetId) {
    document.querySelectorAll(".view-section").forEach((s) => s.classList.add("hidden"));
    document.getElementById(targetId).classList.remove("hidden");
    document.querySelectorAll(".tab-btn").forEach((b) => {
      b.classList.toggle("active", b.dataset.target === targetId);
    });
  }

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchTab(btn.dataset.target));
  });

  function renderTable() {
    const q = document.getElementById("filter-search").value.toLowerCase();
    const pat = document.getElementById("filter-pattern").value;
    const rev = document.getElementById("filter-revisit").value;

    const filtered = state.problems.filter((p) => {
      const matchText = (p.title + " " + p.takeaway + " " + p.pattern).toLowerCase().includes(q);
      const matchPat = pat === "ALL" || p.pattern === pat;
      const matchRev = rev === "ALL" || p.revisit === rev;
      return matchText && matchPat && matchRev;
    });

    const tbody = document.getElementById("problems-tbody");
    if (!filtered.length) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:#8b949e;">No logged problems match current filters.</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered.map((p) => `
      <tr>
        <td style="font-family:var(--font-mono);white-space:nowrap;">${window.DSA_FN.escapeHtml(p.date)}</td>
        <td>${p.url ? `<a href="${window.DSA_FN.escapeHtml(p.url)}" target="_blank" style="color:var(--accent-blue);text-decoration:none;">${window.DSA_FN.escapeHtml(p.title)}</a>` : window.DSA_FN.escapeHtml(p.title)}</td>
        <td><span class="pattern-badge">${window.DSA_FN.escapeHtml(p.pattern)}</span></td>
        <td>${window.DSA_FN.escapeHtml(p.difficulty)}</td>
        <td>${window.DSA_FN.escapeHtml(p.takeaway)}</td>
        <td style="text-align:center;">${window.DSA_FN.escapeHtml(p.revisit)}</td>
        <td><button class="btn btn-secondary btn-view-code" data-path="${window.DSA_FN.escapeHtml(p.code_path)}">VIEW_FILE</button></td>
      </tr>
    `).join("");

    tbody.querySelectorAll(".btn-view-code").forEach((b) => {
      b.addEventListener("click", async () => {
        try {
          const file = await window.DSA_API.fetchCodeFile(b.dataset.path);
          document.getElementById("inspector-title").textContent = `FILE // ${file.path}`;
          document.getElementById("inspector-content").textContent = file.content;
          document.getElementById("code-inspector").classList.remove("hidden");
        } catch (err) {
          notify(err.message, true);
        }
      });
    });
  }

  async function refreshData() {
    const data = await window.DSA_API.fetchState();
    state.problems = data.problems || [];
    document.getElementById("stat-total").textContent = state.problems.length;
    document.getElementById("stat-red").textContent = state.problems.filter((p) => p.revisit.includes("🔴")).length;

    const patterns = Array.from(new Set(state.problems.map((p) => p.pattern))).sort();
    const sel = document.getElementById("filter-pattern");
    sel.innerHTML = `<option value="ALL">ALL PATTERNS (${patterns.length})</option>` +
      patterns.map((p) => `<option value="${p}">${p}</option>`).join("");

    const draftInput = document.getElementById("input-draft");
    if (!draftInput.value.trim()) {
      draftInput.value = data.draft || window.DSA_FN.BLANK_TEMPLATE;
    }
    renderTable();
  }

  // Event Bindings
  document.getElementById("filter-search").addEventListener("input", renderTable);
  document.getElementById("filter-pattern").addEventListener("change", renderTable);
  document.getElementById("filter-revisit").addEventListener("change", renderTable);
  document.getElementById("btn-close-inspector").addEventListener("click", () => {
    document.getElementById("code-inspector").classList.add("hidden");
  });

  document.getElementById("btn-load-template").addEventListener("click", () => {
    document.getElementById("input-draft").value = window.DSA_FN.BLANK_TEMPLATE;
    notify("Loaded blank problem_draft.txt template.");
  });

  document.getElementById("btn-run-ai").addEventListener("click", async (e) => {
    const url = document.getElementById("input-url").value.trim();
    const code = document.getElementById("input-code").value.trim();
    const notes = document.getElementById("input-notes").value.trim();
    e.target.disabled = true;
    notify("Querying LeetCode GraphQL & Gemini 2.5 Flash...");
    try {
      const draft = await window.DSA_API.generateAIDraft(url, code, notes);
      document.getElementById("input-draft").value = draft;
      notify("AI Draft generated and saved to problem_draft.txt. Review Step 02 and click Forge.");
    } catch (err) {
      notify(err.message, true);
    } finally {
      e.target.disabled = false;
    }
  });

  document.getElementById("btn-forge-files").addEventListener("click", async () => {
    const draft = document.getElementById("input-draft").value;
    const code = document.getElementById("input-code").value;
    const parsed = window.DSA_FN.parseDraftText(draft);
    if (!parsed.title) return notify("TITLE: cannot be empty in draft.", true);

    try {
      const res = await window.DSA_API.forgeSolution(draft, code, parsed);
      notify(`Created ${res.file_path} and updated root README.md!`);
      await refreshData();
      switchTab("view-dashboard");
    } catch (err) {
      notify(err.message, true);
    }
  });

  document.getElementById("btn-git-sync").addEventListener("click", async () => {
    const parsed = window.DSA_FN.parseDraftText(document.getElementById("input-draft").value);
    const defaultMsg = parsed.title ? `feat(dsa): solve ${parsed.title}` : "feat(dsa): update daily log";
    const msg = prompt("Git Commit Message:", defaultMsg);
    if (msg === null) return;
    notify("Running git add, commit, and push...");
    try {
      const out = await window.DSA_API.gitSync(msg);
      notify(`Git Sync Complete: ${out}`);
    } catch (err) {
      notify(err.message, true);
    }
  });

  await refreshData();
})();