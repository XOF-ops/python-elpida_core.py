#!/usr/bin/env python3
"""Builds observation_dashboard/data/observation_snapshot.json from raw S3 pulls.

Schema correction (2026-04-19): the BODY heartbeat keys had drifted from
what the snapshot builder expected. The builder asked for body.get("cycle")
but the heartbeat actually has body_cycle; same pattern for pathology_health
(was: health), axiom_frequency (was: top_axioms), etc. Result: most body
fields rendered as "n/a" on the deployed dashboard, and HERMES/Copilot/all
agents reading the snapshot got a dishonest picture.

This rewrite:
  1. Maps snapshot fields against the ACTUAL heartbeat keys
  2. Surfaces every heartbeat field the snapshot was silently dropping
  3. Adds cumulative context (living_axioms_count) so the cycle number
     stops being misleading after HF Space rebuilds (each push to HF resets
     body_cycle to 0; cumulative continuity lives in living_axioms.jsonl)
  4. Adds HF container log telemetry — gracefully no-ops if HF_TOKEN is
     missing/expired so the workflow never fails on auth

Backward compatibility: existing snapshot keys (body.cycle, body.health,
body.top_axioms, etc.) are preserved by aliasing — app.js doesn't need to
change immediately. New fields are added under their canonical names
alongside the legacy aliases.
"""

from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "_snapshot" / "raw"
OUT_PATH = ROOT / "observation_dashboard" / "data" / "observation_snapshot.json"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_jsonl_count(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open("r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except Exception:
        return 0


def read_text_tail(path: Path, max_lines: int = 200) -> list[str]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return [ln.rstrip("\n") for ln in lines[-max_lines:]]
    except Exception:
        return []


def pick(obj: dict[str, Any], keys: list[str], default: Any = "n/a") -> Any:
    """Return the first present non-None value across the candidate keys."""
    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]
    return default


def derive_top_axioms(axiom_frequency: dict[str, Any]) -> list[str]:
    """Sort axioms by frequency, return top 5 IDs."""
    if not isinstance(axiom_frequency, dict):
        return []
    try:
        ranked = sorted(axiom_frequency.items(), key=lambda kv: -int(kv[1]))
        return [k for k, _ in ranked[:5]]
    except Exception:
        return list(axiom_frequency.keys())[:5]


def summarize_hf_logs(lines: list[str]) -> dict[str, Any]:
    """Extract simple telemetry from raw HF container log lines.

    Conservative: counts occurrences of well-known markers; doesn't attempt
    to parse structured fields. The raw tail is also surfaced so operators
    can read context if a number looks off.
    """
    if not lines:
        return {
            "available": False,
            "reason": "no HF logs fetched (token missing/expired or fetch skipped)",
            "line_count": 0,
            "tail": [],
        }

    markers = {
        "cycle_emitted": 0,        # "Cycle N complete" or similar
        "d15_broadcast": 0,
        "d16_emit": 0,
        "pathology_critical": 0,
        "axiom_ratified": 0,
        "kernel_block": 0,
        "discord_health_ok": 0,
        "discord_network_unreachable": 0,
        "discord_webhook_fail": 0,
        "discord_outbox_replay": 0,
        "discord_webhook_missing": 0,
        "errors": 0,
        "warnings": 0,
    }
    for ln in lines:
        low = ln.lower()
        if "cycle" in low and ("complete" in low or "emitted" in low):
            markers["cycle_emitted"] += 1
        if "d15" in low and "broadcast" in low:
            markers["d15_broadcast"] += 1
        if "d16" in low and ("emit" in low or "executed" in low):
            markers["d16_emit"] += 1
        if "pathology" in low and "critical" in low:
            markers["pathology_critical"] += 1
        if "axiom" in low and ("ratified" in low or "ratification" in low):
            markers["axiom_ratified"] += 1
        if "kernel" in low and ("block" in low or "blocked" in low or "halt" in low):
            markers["kernel_block"] += 1
        if "discord connectivity:" in low and "reachable" in low:
            markers["discord_health_ok"] += 1
        if "discord connectivity:" in low and "unreachable" in low:
            markers["discord_network_unreachable"] += 1
        if "discord webhook post failed" in low or "discord webhook returned status" in low:
            markers["discord_webhook_fail"] += 1
        if "discord outbox replayed" in low:
            markers["discord_outbox_replay"] += 1
        if "discord webhook missing" in low:
            markers["discord_webhook_missing"] += 1
        if "error" in low or "exception" in low or "traceback" in low:
            markers["errors"] += 1
        if "warning" in low or "warn:" in low:
            markers["warnings"] += 1

    return {
        "available": True,
        "line_count": len(lines),
        "markers": markers,
        "tail": lines[-30:],  # last 30 lines for operator inspection
    }


def derive_hf_discord_status(hf_logs: dict[str, Any]) -> tuple[str, str]:
    """Return (status, note) for HF-side Discord outbound health."""
    if not hf_logs.get("available"):
        return (
            "unknown_logs_unavailable",
            "HF logs unavailable in snapshot build; cannot observe Discord outbound from HF runtime.",
        )

    markers = hf_logs.get("markers", {}) or {}
    if markers.get("discord_network_unreachable", 0) > 0 or markers.get("discord_webhook_fail", 0) > 0:
        return (
            "degraded",
            "HF runtime reported Discord network/webhook failures in recent logs.",
        )
    if markers.get("discord_outbox_replay", 0) > 0:
        return (
            "recovering",
            "HF runtime replayed Discord outbox items after prior delivery issues.",
        )
    if markers.get("discord_health_ok", 0) > 0:
        return (
            "healthy",
            "HF runtime reported Discord connectivity reachable in recent logs.",
        )
    return (
        "unknown_no_recent_signal",
        "No explicit Discord health marker found in recent HF log tail.",
    )


def build() -> dict[str, Any]:
    body = read_json(RAW_DIR / "body_heartbeat.json")
    mind = read_json(RAW_DIR / "mind_heartbeat.json")

    d16_count = read_jsonl_count(RAW_DIR / "d16_executions.jsonl")
    d15_files = glob.glob(str(RAW_DIR / "broadcast_*.json"))
    guest_questions_count = read_jsonl_count(RAW_DIR / "guest_chamber_questions.jsonl")
    guest_watermark = read_json(RAW_DIR / "guest_chamber_watermark.json")
    living_axioms_count = read_jsonl_count(RAW_DIR / "living_axioms.jsonl")
    hf_log_lines = read_text_tail(RAW_DIR / "hf_run_logs.txt", max_lines=500)
    hf_log_summary = summarize_hf_logs(hf_log_lines)
    discord_hf_status, discord_hf_note = derive_hf_discord_status(hf_log_summary)

    # ── BODY field resolution against ACTUAL heartbeat schema ───────────
    # Heartbeat actually carries these keys (verified live 2026-04-19):
    #   body_cycle, pathology_health, pathology_last_cycle, coherence,
    #   dominant_axiom, axiom_frequency, current_rhythm, current_watch,
    #   watch_cycle, watch_symbol, d15_broadcast_count, hub,
    #   input_buffer_counts, oracle_threshold, polis_civic_active,
    #   sacrifices, contradictions, s3_isolated, federation_version,
    #   timestamp, source, veto_exercised, approval_rate, fork_active_count,
    #   fork_confirmed_total, fork_last_cycle
    body_cycle = pick(body, ["body_cycle", "cycle", "cycle_number"])
    pathology_health = pick(body, ["pathology_health", "health", "overall_health"])
    axiom_frequency = body.get("axiom_frequency", {}) or {}
    top_axioms = derive_top_axioms(axiom_frequency)

    mind_cycle = pick(mind, ["mind_cycle", "cycle"], None)
    run_progress = (
        f"{mind_cycle}/55" if mind_cycle is not None else pick(
            mind, ["run_progress", "cycle_progress"], "n/a"
        )
    )

    # BODY no longer emits KL/P055 in heartbeat payloads. Keep an explicit
    # marker so operators know this is a source limitation, not a UI bug.
    kl_value = pick(body, ["kl_divergence", "p055_kl_divergence"], None)
    if kl_value is None:
        kl_value = "unavailable_in_body_heartbeat"

    mind_run_number = mind.get("run_number")
    if mind_run_number is None:
        mind_run_number = "unavailable_in_mind_heartbeat"

    snapshot: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status_token": "YELLOW",
        "schema_lock": "d16-cursor-handoff-003+heartbeat-realign-2026-04-19",
        "body": {
            # ── Legacy aliases (preserved so existing app.js renders keep working) ──
            "cycle": body_cycle,
            "health": pathology_health,
            "top_axioms": top_axioms,
            "coherence": pick(body, ["coherence"]),
            "hunger_level": pick(body, ["hunger_level", "hunger"], "unavailable_in_body_heartbeat"),
            "kl_divergence": kl_value,
            "provider_map": pick(body, ["provider_map", "provider_breakdown"], {}),
            "timestamp": pick(body, ["timestamp"]),
            "run_duration_seconds": pick(body, ["run_duration_seconds", "run_duration_s"], "unavailable_in_body_heartbeat"),
            "cycles_per_hour": pick(body, ["cycles_per_hour", "cycle_rate_h"], "unavailable_in_body_heartbeat"),
            "p055_critical_threshold": pick(body, ["p055_critical_threshold"], 0.55),
            "p055_history": pick(body, ["p055_history", "kl_history"], []),
            "parliament_votes": pick(body, ["parliament_votes", "vote_breakdown"], "unavailable_in_body_heartbeat"),
            "circuit_breaker_status": pick(
                body, ["circuit_breaker_status", "breaker_status"], "unknown"
            ),
            "sacrifices": body.get("sacrifices", {}),
            "contradictions": body.get("contradictions", {}),
            "s3_isolated": body.get("s3_isolated"),

            # ── NEW: canonical heartbeat fields previously dropped ──────────────
            "body_cycle": body_cycle,                          # canonical name
            "pathology_health": pathology_health,
            "pathology_last_cycle": body.get("pathology_last_cycle"),
            "axiom_frequency": axiom_frequency,
            "dominant_axiom": body.get("dominant_axiom"),
            "current_rhythm": body.get("current_rhythm"),
            "current_watch": body.get("current_watch"),
            "watch": {
                "cycle": body.get("watch_cycle"),
                "symbol": body.get("watch_symbol"),
            },
            "d15_broadcast_count": body.get("d15_broadcast_count"),
            "hub": body.get("hub", {}),
            "input_buffer_counts": body.get("input_buffer_counts", {}),
            "oracle_threshold": body.get("oracle_threshold"),
            "polis_civic_active": body.get("polis_civic_active"),
            "veto_exercised": body.get("veto_exercised"),
            "approval_rate": body.get("approval_rate"),
            "fork": {
                "active_count": body.get("fork_active_count", 0),
                "confirmed_total": body.get("fork_confirmed_total", 0),
                "last_cycle": body.get("fork_last_cycle"),
            },
            "federation_version": body.get("federation_version"),
        },
        "mind": {
            "cycle": mind_cycle if mind_cycle is not None else "unavailable_in_mind_heartbeat",
            "run_number": mind_run_number,
            "epoch": mind.get("epoch", mind.get("mind_epoch", "unavailable_in_mind_heartbeat")),
            "canonical_count": mind.get("canonical_count", "unavailable_in_mind_heartbeat"),
            "dominant_theme": mind.get("dominant_theme", pick(
                mind, ["recent_theme_top", "canonical_theme"], "unavailable_in_mind_heartbeat"
            )),
            "coherence": mind.get("coherence", "unavailable_in_mind_heartbeat"),
            "hunger_level": mind.get("hunger_level", "unavailable_in_mind_heartbeat"),
            "current_rhythm": mind.get("current_rhythm", "unavailable_in_mind_heartbeat"),
            "current_domain": mind.get("current_domain", "unavailable_in_mind_heartbeat"),
            "ark_mood": mind.get("ark_mood", "unavailable_in_mind_heartbeat"),
            "pending_canonical_count": mind.get("pending_canonical_count", 0),
            "recursion_warning": mind.get("recursion_warning", False),
            "recursion_pattern_type": mind.get("recursion_pattern_type", "none"),
            "recent_theme_top_count": mind.get("recent_theme_top_count", 0),
            "recent_theme_window_size": mind.get("recent_theme_window_size", 0),
            "recent_theme_top_domains": mind.get("recent_theme_top_domains", 0),
            "dominant_axiom": mind.get("dominant_axiom", "unavailable_in_mind_heartbeat"),
            "kernel_version": mind.get("kernel_version", "unavailable_in_mind_heartbeat"),
            "kernel_blocks_total": mind.get("kernel_blocks_total", 0),
            "kaya_count": mind.get("kaya_moments", mind.get("kaya_count", 0)),
            "hub_entry_count": mind.get("hub_entry_count", 0),
            "hub_canonical_count": mind.get("hub_canonical_count", 0),
            "hub_last_admission": mind.get("hub_last_admission", "unavailable_in_mind_heartbeat"),
            "run_progress": run_progress,
            "canonical_theme_distribution": pick(
                mind, ["canonical_theme_distribution", "themes"], {}
            ),
            "classification_breakdown": pick(
                mind, ["classification_breakdown", "canonical_standard_pending"], {}
            ),
        },
        "world": {
            "d15_broadcast_count": len(d15_files),
            "d15_index_path": "data/d15_index.json",
            "bridge_panel_path": "data/bridge_panel.json",
            "rollup_path": "data/observation_rollup.json",
            "d16_pool_size": d16_count,
            "d16_sample_keys": [
                "source", "body_cycle", "timestamp", "verdict", "axiom",
                "proposal", "status", "d4_gate",
            ],
            "discord_inbound_count": guest_questions_count,
            "discord_inbound_watermark": guest_watermark.get("last_seen_timestamp", "unknown"),
            "discord_hf_outbound_status": discord_hf_status,
            "discord_hf_outbound_note": discord_hf_note,
            "rss_tension_count": "unavailable_in_snapshot_pipeline",
        },
        "bridge": {
            "token": "YELLOW",
            "note": "Built from scheduled S3 snapshot pull.",
        },
        # ── NEW: cross-run continuity context (the HF rebuild context) ──────────
        "continuity": {
            "living_axioms_count": living_axioms_count,
            "note": (
                "body_cycle resets to 0 on each HF Space rebuild. "
                "living_axioms_count is the cumulative ratification count "
                "across all runs since genesis — true continuity metric."
            ),
        },
        # ── NEW: HF container log telemetry (gracefully degrades) ───────────────
        "hf_logs": hf_log_summary,
    }

    have_body = bool(body)
    have_mind = bool(mind)
    if have_body and have_mind:
        snapshot["status_token"] = "GREEN"
        snapshot["bridge"]["token"] = "GREEN"
    elif not have_body and not have_mind:
        snapshot["status_token"] = "RED"
        snapshot["bridge"]["token"] = "RED"
        snapshot["bridge"]["note"] = "No heartbeat files pulled from S3."

    # If pathology is CRITICAL we should not flag GREEN even if both heartbeats present.
    if pathology_health == "CRITICAL" and snapshot["status_token"] == "GREEN":
        snapshot["status_token"] = "YELLOW"
        snapshot["bridge"]["note"] = (
            "Both heartbeats present but body.pathology_health=CRITICAL. "
            "Health honesty forces YELLOW."
        )

    return snapshot


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snapshot = build()
    OUT_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
