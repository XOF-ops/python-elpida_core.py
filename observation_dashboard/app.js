function get(obj, keys, fallback = "n/a") {
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
  if (!obj || typeof obj !== "object") return "n/a";
  const v = obj[key];
  return v !== null && v !== undefined ? v : "n/a";
}

function formatS3Isolated(v) {
  if (v === true) return "yes";
  if (v === false) return "no";
  return "n/a";
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

async function loadD15Index(relPath) {
  const path = String(relPath || "data/d15_index.json").replace(/^\//, "");
  const url = `./${path}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }
  return res.json();
}

function renderD15Meta(index, pathUsed) {
  const meta = document.getElementById("d15HubMeta");
  const tc = index.total_count != null ? index.total_count : "?";
  const iz = index.index_size != null ? index.index_size : (index.broadcasts || []).length;
  const ga = index.generated_at || "unknown";
  meta.textContent = `Hub: ${pathUsed} · schema=${index.schema || "n/a"} · total_count=${tc} · index_size=${iz} · generated_at=${ga}`;
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
        : "n/a";
  el.innerHTML = `
    <div class="d15-id">${escapeHtml(latest.broadcast_id)}</div>
    <div class="d15-time">${escapeHtml(latest.timestamp || "")}</div>
    <div class="d15-axioms">${escapeHtml(ax || "—")}</div>
    <div class="d15-synth">${escapeHtml(latest.diplomat_synthesis || "")}</div>
    <div class="d15-gov">Verdict: ${escapeHtml(String(gov.verdict ?? "n/a"))} · approval_rate: ${
  gov.approval_rate != null ? escapeHtml(String(gov.approval_rate)) : "n/a"
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

function render(snapshot) {
  setToken(snapshot.status_token);
  document.getElementById("generatedAt").textContent = snapshot.generated_at || "unknown";

  const body = snapshot.body || {};
  const mind = snapshot.mind || {};
  const world = snapshot.world || {};

  document.getElementById("bodyCards").innerHTML = [
    cardHtml("Cycle", get(body, ["cycle", "cycle_number"])),
    cardHtml("Coherence", get(body, ["coherence"])),
    cardHtml("Health", get(body, ["health", "overall_health"])),
    cardHtml("KL / P055", get(body, ["kl_divergence", "p055_kl_divergence"])),
    cardHtml("Hunger", get(body, ["hunger_level", "hunger"])),
    cardHtml("Timestamp", get(body, ["timestamp"])),
    cardHtml("Circuit Breaker", get(body, ["circuit_breaker_status", "breaker_status"])),
    cardHtml("Sacrifices (total)", nestedCount(body.sacrifices, "total")),
    cardHtml("Contradictions (total)", nestedCount(body.contradictions, "total")),
    cardHtml("Contradictions (unresolved)", nestedCount(body.contradictions, "unresolved")),
    cardHtml("S3 isolated", formatS3Isolated(body.s3_isolated)),
    cardHtml("Top Axioms", JSON.stringify(get(body, ["top_axioms", "axiom_dominance"], []))),
    cardHtml("Provider Map", JSON.stringify(get(body, ["provider_map", "provider_breakdown"], {}))),
  ].join("");

  document.getElementById("mindCards").innerHTML = [
    cardHtml("Run Progress", get(mind, ["run_progress", "cycle_progress"])),
    cardHtml("MIND cycle", get(mind, ["cycle", "mind_cycle"])),
    cardHtml("Run #", get(mind, ["run_number"])),
    cardHtml("Epoch", get(mind, ["epoch", "mind_epoch"])),
    cardHtml("Dominant theme", get(mind, ["dominant_theme", "canonical_theme"])),
    cardHtml("Canonical count", get(mind, ["canonical_count"])),
    cardHtml("Coherence", get(mind, ["coherence"])),
    cardHtml("D0 voice %", get(mind, ["d0_voice_pct", "d0_voice_frequency", "d0_frequency"])),
    cardHtml("D9 voice %", get(mind, ["d9_voice_pct", "d9_voice_frequency", "d9_frequency"])),
    cardHtml("SYNOD", get(mind, ["synod_count", "synod_events"])),
    cardHtml("KAYA", get(mind, ["kaya_count", "kaya_events"])),
    cardHtml("Human conv.", get(mind, ["human_conversation_count", "human_conversations"])),
  ].join("");

  document.getElementById("worldCards").innerHTML = [
    cardHtml("D15 Broadcasts", get(world, ["d15_broadcast_count", "broadcast_count"])),
    cardHtml("D16 Pool Size", get(world, ["d16_pool_size", "d16_count"])),
    cardHtml("D15 hub (path)", get(world, ["d15_index_path"], "data/d15_index.json")),
    cardHtml("Discord Inbound", get(world, ["discord_inbound_count", "discord_count"])),
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
}

async function boot() {
  try {
    const snapshot = await loadSnapshot();
    render(snapshot);
    const path =
      (snapshot.world && snapshot.world.d15_index_path) || "data/d15_index.json";
    try {
      const d15 = await loadD15Index(path);
      renderD15Hub(d15, path);
    } catch (e) {
      renderD15HubError(path, e);
    }
  } catch (err) {
    renderError(err);
  }
}

boot();
