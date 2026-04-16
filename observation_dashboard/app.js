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
}

loadSnapshot().then(render).catch(renderError);
