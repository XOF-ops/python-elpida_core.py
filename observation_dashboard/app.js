function get(obj, keys, fallback = "unavailable_in_snapshot") {
  for (const key of keys) {
    if (obj && Object.prototype.hasOwnProperty.call(obj, key) && obj[key] !== null && obj[key] !== undefined) {
      return obj[key];
    }
  }
  return fallback;
}

function cardHtml(label, value) {
  return `<div class="card"><div class="label">${label}</div><div class="value">${value}</div></div>`;
}

function nestedCount(obj, key) {
  if (!obj || typeof obj !== "object") return "unavailable_in_snapshot";
  const v = obj[key];
  return v !== null && v !== undefined ? v : "unavailable_in_snapshot";
}

function formatS3Isolated(v) {
  if (v === true) return "yes";
  if (v === false) return "no";
  return "unknown_in_snapshot";
}

function setToken(token) {
  const node = document.getElementById("statusToken");
  const upper = String(token || "YELLOW").toUpperCase();
  node.textContent = upper;
  node.className = "token " + (upper === "GREEN" ? "token-green" : upper === "RED" ? "token-red" : "token-yellow");
}

function drawLineChart(canvas, values, threshold = 0.67) {
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;
  ctx.clearRect(0, 0, w, h);

  if (!Array.isArray(values) || values.length < 2) {
    ctx.fillStyle = "#9eabc7";
    ctx.font = "12px Arial";
    ctx.fillText("No trend data", 16, 24);
    return;
  }

  const nums = values.map(Number).filter((n) => !Number.isNaN(n));
  const minV = Math.min(...nums, threshold, 0);
  const maxV = Math.max(...nums, threshold, 1);
  const pad = 20;

  const x = (i) => pad + (i / (nums.length - 1)) * (w - pad * 2);
  const y = (v) => h - pad - ((v - minV) / (maxV - minV || 1)) * (h - pad * 2);

  ctx.strokeStyle = "#3f4a6d";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(pad, y(threshold));
  ctx.lineTo(w - pad, y(threshold));
  ctx.stroke();

  ctx.fillStyle = "#9eabc7";
  ctx.font = "11px Arial";
  ctx.fillText(`critical: ${threshold}`, pad + 6, y(threshold) - 6);

  ctx.strokeStyle = "#7fb3ff";
  ctx.lineWidth = 2;
  ctx.beginPath();
  nums.forEach((v, i) => {
    if (i === 0) {
      ctx.moveTo(x(i), y(v));
    } else {
      ctx.lineTo(x(i), y(v));
    }
  });
  ctx.stroke();
}

async function loadSnapshot() {
  const res = await fetch("./data/observation_snapshot.json", { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function loadJsonFile(relPath) {
  const path = String(relPath || "").replace(/^\//, "");
  const url = `./${path}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

async function loadD15Index(relPath) {
  return loadJsonFile(relPath || "data/d15_index.json");
}

function renderD15Meta(index, pathUsed) {
  const meta = document.getElementById("d15HubMeta");
  const tc = index.total_count != null ? index.total_count : "?";
  const iz = index.index_size != null ? index.index_size : (index.broadcasts || []).length;
  const ga = index.generated_at || "unknown";
  meta.textContent = `Hub: ${pathUsed} · schema=${index.schema || "unknown_in_d15_index"} · total_count=${tc} · index_size=${iz} · generated_at=${ga}`;
}

function renderD15Latest(latest) {
  const el = document.getElementById("d15Latest");
  if (!latest || !latest.broadcast_id) {
    el.innerHTML = '<p class="timeline-empty">No latest broadcast in index.</p>';
    return;
  }
  const gov = latest.governance || {};
  const ax = Array.isArray(latest.axioms_in_tension) ? latest.axioms_in_tension.join(", ") : "";
  const llm =
    latest.llm_synthesis_success === true
      ? "ok"
      : latest.llm_synthesis_success === false
        ? "fail"
        : "unknown_in_d15_index";
  el.innerHTML = `
    <div class="d15-id">${escapeHtml(latest.broadcast_id)}</div>
    <div class="d15-time">${escapeHtml(latest.timestamp || "")}</div>
    <div class="d15-axioms">${escapeHtml(ax || "—")}</div>
    <div class="d15-synth">${escapeHtml(latest.diplomat_synthesis || "")}</div>
    <div class="d15-gov">Verdict: ${escapeHtml(String(gov.verdict ?? "unknown_in_d15_index"))} · approval_rate: ${gov.approval_rate != null ? escapeHtml(String(gov.approval_rate)) : "unknown_in_d15_index"
    } · llm_synthesis: ${llm}</div>
  `;
}

function timelineItemHtml(b) {
  const ax = Array.isArray(b.axioms_in_tension) ? b.axioms_in_tension.join(", ") : "";
  const synth = (b.diplomat_synthesis || "").replace(/\s+/g, " ").trim();
  return `<div class="timeline-item" role="listitem">
    <div class="ti-head">
      <span class="ti-id">${escapeHtml(b.broadcast_id || "")}</span>
      <span class="ti-time">${escapeHtml(b.timestamp || "")}</span>
    </div>
    <div class="ti-axioms">${escapeHtml(ax || "—")}</div>
    <div class="ti-blurb">${escapeHtml(synth)}</div>
  </div>`;
}

function renderD15Timeline(index) {
  const container = document.getElementById("d15Timeline");
  const list = index.broadcasts || [];
  const tail = list.slice(1);
  if (!list.length) {
    container.innerHTML =
      '<div class="timeline-empty">No broadcasts in d15_index.json — check WORLD bucket broadcasts.jsonl and CI.</div>';
    return;
  }
  if (!tail.length) {
    container.innerHTML =
      '<div class="timeline-empty">Only the latest broadcast in this index window; more appear after the next D15.</div>';
    return;
  }
  container.innerHTML = tail.map((b) => timelineItemHtml(b)).join("");
}

function renderD15Hub(index, pathUsed) {
  renderD15Meta(index, pathUsed);
  const latest = index.latest || listHead(index.broadcasts);
  renderD15Latest(latest);
  renderD15Timeline(index);
}

function listHead(arr) {
  if (!arr || !arr.length) return null;
  return arr[0];
}

function renderD15HubError(pathUsed, err) {
  document.getElementById("d15HubMeta").textContent = `Could not load ${pathUsed}: ${err.message}`;
  document.getElementById("d15Latest").innerHTML = "";
  document.getElementById("d15Timeline").innerHTML = "";
}

function renderFalsification(widget) {
  const statusEl = document.getElementById("falsificationStatus");
  const cards = document.getElementById("falsificationCards");
  if (!widget || typeof widget !== "object") {
    statusEl.textContent = "Markers unavailable.";
    cards.innerHTML = "";
    return;
  }

  const state = String(widget.status || "UNKNOWN").toUpperCase();
  statusEl.className = "falsification-status";
  if (state === "CLEAR") statusEl.classList.add("state-clear");
  else if (state === "ACTIVE") statusEl.classList.add("state-active");
  else statusEl.classList.add("state-elevated");
  statusEl.textContent = `STATUS: ${state}${widget.gap_active ? " — FALSIFICATION GAP ACTIVE" : ""}`;

  const m1 = widget.marker_axiom_monoculture || {};
  const m2 = widget.marker_d15_absence || {};
  const m3 = widget.marker_external_contact_drought || {};

  cards.innerHTML = [
    cardHtml(
      "Axiom monoculture",
      `${m1.dominant_axiom || "none_detected_in_window"} ${m1.dominance_pct != null ? `${m1.dominance_pct}%` : "unknown_in_rollup"} (>${m1.threshold_pct ?? "60"}%)`,
    ),
    cardHtml(
      "Hours since D15",
      `${m2.hours_since_d15 != null ? m2.hours_since_d15 : "unknown_in_rollup"}h (>${m2.threshold_hours ?? 8}h)`,
    ),
    cardHtml(
      "External contact",
      `${m3.hours_since_external_contact != null ? m3.hours_since_external_contact : "unknown_in_rollup"}h (>${m3.threshold_hours ?? 24}h)`,
    ),
    cardHtml("Gap active", widget.gap_active ? "yes" : "no"),
  ].join("");
}

function renderBridgePanel(panel, pathUsed) {
  const meta = document.getElementById("bridgePanelMeta");
  const box = document.getElementById("bridgeLanes");
  const lanes = (panel && panel.lanes) || [];
  meta.textContent = `Hub: ${pathUsed} · schema=${panel.schema || "unknown_in_bridge_panel"} · lanes=${lanes.length} · generated_at=${panel.generated_at || "unknown_in_bridge_panel"}`;
  if (!lanes.length) {
    box.innerHTML =
      '<p class="timeline-empty">No bridge lanes found — run CI or add .claude/bridge/for_* / from_*.md</p>';
    return;
  }
  box.innerHTML = lanes.map((L) => bridgeLaneHtml(L)).join("");
}

function bridgeLaneHtml(L) {
  const prev = L.head_preview ? escapeHtml(L.head_preview) : "—";
  const err = L.error ? `<div class="bl-row">${escapeHtml(L.error)}</div>` : "";
  return `<article class="bridge-lane">
    <div class="bl-name">${escapeHtml(L.name || L.path || "?")}</div>
    ${err}
    <div class="bl-row"><strong>From:</strong> ${escapeHtml(L.from || "unknown_in_bridge_lane")}</div>
    <div class="bl-row"><strong>Session:</strong> ${escapeHtml(L.session || "unknown_in_bridge_lane")}</div>
    <div class="bl-row"><strong>Tags:</strong> ${escapeHtml(L.tags || "unknown_in_bridge_lane")}</div>
    <div class="bl-row"><strong>git_last_commit:</strong> ${escapeHtml(L.git_last_commit || "unknown_in_bridge_lane")}</div>
    <div class="bl-preview">${prev}</div>
  </article>`;
}

function renderBridgePanelError(pathUsed, err) {
  document.getElementById("bridgePanelMeta").textContent = `Could not load ${pathUsed}: ${err.message}`;
  document.getElementById("bridgeLanes").innerHTML = "";
}

function renderRollup(rollup, pathUsed) {
  const meta = document.getElementById("rollupMeta");
  const wh = rollup.window_hours != null ? rollup.window_hours : "?";
  meta.textContent = `Hub: ${pathUsed} · schema=${rollup.schema || "unknown_in_rollup"} · window=${wh}h · ${rollup.window_start || ""} → ${rollup.window_end || ""}`;

  const d15 = rollup.d15_in_window || {};
  const bsig = rollup.body_signal || {};
  const msig = rollup.mind_signal || {};
  const p = bsig.p055_stats || {};
  const pStatus = bsig.p055_status || "unavailable_in_rollup";
  const totals = rollup.d15_index_totals || {};

  document.getElementById("rollupCards").innerHTML = [
    cardHtml("D15 events (window)", d15.count != null ? d15.count : "unknown_in_rollup"),
    cardHtml("D15 index total_count", totals.total_count != null ? totals.total_count : "unknown_in_rollup"),
    cardHtml("BODY coherence (point)", bsig.coherence != null ? bsig.coherence : "unknown_in_rollup"),
    cardHtml("BODY cycle (point)", bsig.cycle != null ? bsig.cycle : "unknown_in_rollup"),
    cardHtml("S3 isolated (point)", formatS3Isolated(bsig.s3_isolated)),
    cardHtml("P055 samples (n)", p.n != null ? p.n : pStatus),
    cardHtml("P055 min / max", p.n ? `${p.min} / ${p.max}` : pStatus),
    cardHtml("P055 avg", p.avg != null ? p.avg : pStatus),
    cardHtml("MIND cycle (point)", msig.cycle != null ? msig.cycle : "unknown_in_rollup"),
    cardHtml("Dominant theme", msig.dominant_theme != null ? msig.dominant_theme : "unknown_in_rollup"),
  ].join("");

  document.getElementById("rollupRaw").textContent = JSON.stringify(rollup, null, 2);
  renderFalsification(rollup.falsification_protocol || {});
}

function renderRollupError(pathUsed, err) {
  document.getElementById("rollupMeta").textContent = `Could not load ${pathUsed}: ${err.message}`;
  document.getElementById("rollupCards").innerHTML = "";
  document.getElementById("rollupRaw").textContent = "";
  renderFalsification(null);
}

function render(snapshot) {
  setToken(snapshot.status_token);
  document.getElementById("generatedAt").textContent = snapshot.generated_at || "unknown";

  const body = snapshot.body || {};
  const mind = snapshot.mind || {};
  const world = snapshot.world || {};
  const continuity = snapshot.continuity || {};
  const hfLogs = snapshot.hf_logs || {};
  const watch = body.watch || {};
  const fork = body.fork || {};
  const hub = body.hub || {};

  document.getElementById("bodyCards").innerHTML = [
    cardHtml("Cycle (current run)", get(body, ["body_cycle", "cycle", "cycle_number"])),
    cardHtml("Living axioms (cumulative)", get(continuity, ["living_axioms_count"])),
    cardHtml("Pathology Health", get(body, ["pathology_health", "health"])),
    cardHtml("Pathology last cycle", get(body, ["pathology_last_cycle"])),
    cardHtml("Coherence", get(body, ["coherence"])),
    cardHtml("Dominant axiom", get(body, ["dominant_axiom"])),
    cardHtml("Top Axioms", JSON.stringify(get(body, ["top_axioms", "axiom_dominance"], []))),
    cardHtml("Current rhythm", get(body, ["current_rhythm"])),
    cardHtml("Current watch", get(body, ["current_watch"])),
    cardHtml("Watch cycle / symbol", `${get(watch, ["cycle"])} ${get(watch, ["symbol"])}`),
    cardHtml("Oracle threshold", get(body, ["oracle_threshold"])),
    cardHtml("Approval rate", get(body, ["approval_rate"])),
    cardHtml("Veto exercised", get(body, ["veto_exercised"])),
    cardHtml("D15 broadcast count (BODY)", get(body, ["d15_broadcast_count"])),
    cardHtml("Hub entries", get(hub, ["entry_count"])),
    cardHtml("Hub alive", get(hub, ["hub_alive"])),
    cardHtml("Fork active / confirmed", `${get(fork, ["active_count"])} / ${get(fork, ["confirmed_total"])}`),
    cardHtml("Fork last cycle", get(fork, ["last_cycle"])),
    cardHtml("Federation version", get(body, ["federation_version"])),
    cardHtml("Polis civic active", get(body, ["polis_civic_active"])),
    cardHtml("KL / P055", get(body, ["kl_divergence", "p055_kl_divergence"])),
    cardHtml("Hunger", get(body, ["hunger_level", "hunger"])),
    cardHtml("Timestamp", get(body, ["timestamp"])),
    cardHtml("Circuit Breaker", get(body, ["circuit_breaker_status", "breaker_status"])),
    cardHtml("Sacrifices (total)", nestedCount(body.sacrifices, "total")),
    cardHtml("Contradictions (total)", nestedCount(body.contradictions, "total")),
    cardHtml("Contradictions (unresolved)", nestedCount(body.contradictions, "unresolved")),
    cardHtml("S3 isolated", formatS3Isolated(body.s3_isolated)),
    cardHtml("Provider Map", JSON.stringify(get(body, ["provider_map", "provider_breakdown"], {}))),
    cardHtml("Input buffers", JSON.stringify(get(body, ["input_buffer_counts"], {}))),
    cardHtml("Axiom frequency (full)", JSON.stringify(get(body, ["axiom_frequency"], {}))),
    cardHtml("HF logs available", get(hfLogs, ["available"])),
    cardHtml("HF logs lines", get(hfLogs, ["line_count"])),
  ].join("");

  document.getElementById("mindCards").innerHTML = [
    cardHtml("Run Progress", get(mind, ["run_progress", "cycle_progress"])),
    cardHtml("MIND cycle", get(mind, ["cycle", "mind_cycle"])),
    cardHtml("Current rhythm", get(mind, ["current_rhythm"])),
    cardHtml("Current domain", get(mind, ["current_domain"])),
    cardHtml("Ark mood", get(mind, ["ark_mood"])),
    cardHtml("Epoch", get(mind, ["epoch", "mind_epoch"])),
    cardHtml("Dominant theme", get(mind, ["dominant_theme", "canonical_theme"])),
    cardHtml("Theme hits (window)", `${get(mind, ["recent_theme_top_count"], 0)} / ${get(mind, ["recent_theme_window_size"], 0)}`),
    cardHtml("Theme domains", get(mind, ["recent_theme_top_domains"])),
    cardHtml("Canonical count", get(mind, ["canonical_count"])),
    cardHtml("Pending canonicals", get(mind, ["pending_canonical_count"])),
    cardHtml("Coherence", get(mind, ["coherence"])),
    cardHtml("Dominant axiom", get(mind, ["dominant_axiom"])),
    cardHtml("Recursion warning", get(mind, ["recursion_warning"])),
    cardHtml("Recursion type", get(mind, ["recursion_pattern_type"])),
    cardHtml("Kernel version", get(mind, ["kernel_version"])),
    cardHtml("Kernel blocks", get(mind, ["kernel_blocks_total"])),
    cardHtml("Kaya moments", get(mind, ["kaya_count", "kaya_moments"])),
    cardHtml("Hub entries", get(mind, ["hub_entry_count"])),
    cardHtml("Hub canonical", get(mind, ["hub_canonical_count"])),
    cardHtml("Hub last admission", get(mind, ["hub_last_admission"])),
  ].join("");

  document.getElementById("worldCards").innerHTML = [
    cardHtml("D15 Broadcasts", get(world, ["d15_broadcast_count", "broadcast_count"])),
    cardHtml("D16 Pool Size", get(world, ["d16_pool_size", "d16_count"])),
    cardHtml("D15 hub (path)", get(world, ["d15_index_path"], "data/d15_index.json")),
    cardHtml("Bridge panel (path)", get(world, ["bridge_panel_path"], "data/bridge_panel.json")),
    cardHtml("Rollup (path)", get(world, ["rollup_path"], "data/observation_rollup.json")),
    cardHtml("Discord Inbound", get(world, ["discord_inbound_count", "discord_count"])),
    cardHtml("Discord inbound watermark", get(world, ["discord_inbound_watermark"])),
    cardHtml("HF Discord outbound", get(world, ["discord_hf_outbound_status"])),
    cardHtml("HF Discord note", get(world, ["discord_hf_outbound_note"])),
    cardHtml("RSS Tensions", get(world, ["rss_tension_count", "rss_count"])),
  ].join("");

  document.getElementById("bodyRaw").textContent = JSON.stringify(body, null, 2);
  document.getElementById("mindRaw").textContent = JSON.stringify(mind, null, 2);
  document.getElementById("worldRaw").textContent = JSON.stringify(world, null, 2);
  document.getElementById("bridgeStatus").textContent = JSON.stringify(snapshot.bridge || {}, null, 2);

  drawLineChart(
    document.getElementById("p055Chart"),
    get(body, ["p055_history", "kl_history"], []),
    Number(get(body, ["p055_critical_threshold"], 0.67)),
  );
}

function renderError(err) {
  setToken("YELLOW");
  document.getElementById("generatedAt").textContent = "snapshot unavailable";
  document.getElementById("bodyRaw").textContent = `Unable to load snapshot: ${err.message}`;
  const meta = document.getElementById("d15HubMeta");
  if (meta) meta.textContent = "D15 timeline not loaded (snapshot failed).";
  renderFalsification(null);
}

async function boot() {
  try {
    const snapshot = await loadSnapshot();
    render(snapshot);
    const d15Path =
      (snapshot.world && snapshot.world.d15_index_path) || "data/d15_index.json";
    try {
      const d15 = await loadD15Index(d15Path);
      renderD15Hub(d15, d15Path);
    } catch (e) {
      renderD15HubError(d15Path, e);
    }

    const bridgePath =
      (snapshot.world && snapshot.world.bridge_panel_path) ||
      "data/bridge_panel.json";
    try {
      const panel = await loadJsonFile(bridgePath);
      renderBridgePanel(panel, bridgePath);
    } catch (e) {
      renderBridgePanelError(bridgePath, e);
    }

    const rollupPath =
      (snapshot.world && snapshot.world.rollup_path) ||
      "data/observation_rollup.json";
    try {
      const rollup = await loadJsonFile(rollupPath);
      renderRollup(rollup, rollupPath);
    } catch (e) {
      renderRollupError(rollupPath, e);
    }
  } catch (err) {
    renderError(err);
  }
}

boot();
