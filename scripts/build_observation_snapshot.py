#!/usr/bin/env python3
"""Builds observation_dashboard/data/observation_snapshot.json from raw S3 pulls."""

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


def pick(obj: dict[str, Any], keys: list[str], default: Any = "n/a") -> Any:
    for key in keys:
        if key in obj and obj[key] is not None:
            return obj[key]
    return default


def build() -> dict[str, Any]:
    body = read_json(RAW_DIR / "body_heartbeat.json")
    mind = read_json(RAW_DIR / "mind_heartbeat.json")

    d16_count = read_jsonl_count(RAW_DIR / "d16_executions.jsonl")
    d15_files = glob.glob(str(RAW_DIR / "broadcast_*.json"))

    # Canonical BODY heartbeat (D13 ARK lock) + legacy aliases
    mind_cycle = mind.get("cycle")
    run_progress = (
        f"{mind_cycle}/55" if mind_cycle is not None else pick(
            mind, ["run_progress", "cycle_progress"], "n/a"
        )
    )

    snapshot: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status_token": "YELLOW",
        "schema_lock": "d16-cursor-handoff-001",
        "body": {
            "cycle": body.get("cycle", pick(body, ["cycle_number"], "n/a")),
            "coherence": body.get("coherence", "n/a"),
            "hunger_level": body.get("hunger_level", pick(body, ["hunger"], "n/a")),
            "kl_divergence": body.get("kl_divergence", pick(
                body, ["p055_kl_divergence"], "n/a"
            )),
            "health": body.get("health", pick(body, ["overall_health"], "n/a")),
            "top_axioms": body.get("top_axioms", pick(body, ["axiom_dominance"], [])),
            "provider_map": body.get("provider_map", pick(
                body, ["provider_breakdown", "provider_usage"], {}
            )),
            "timestamp": body.get("timestamp", "n/a"),
            "run_duration_seconds": pick(body, ["run_duration_seconds", "run_duration_s"], "n/a"),
            "cycles_per_hour": pick(body, ["cycles_per_hour", "cycle_rate_h"], "n/a"),
            "p055_critical_threshold": pick(body, ["p055_critical_threshold"], 0.67),
            "p055_history": pick(body, ["p055_history", "kl_history"], []),
            "parliament_votes": pick(body, ["parliament_votes", "vote_breakdown"], {}),
            "circuit_breaker_status": pick(
                body, ["circuit_breaker_status", "breaker_status"], "unknown"
            ),
        },
        "mind": {
            "cycle": mind.get("cycle", pick(mind, ["mind_cycle"], "n/a")),
            "run_number": mind.get("run_number", "n/a"),
            "epoch": mind.get("epoch", mind.get("mind_epoch", "n/a")),
            "canonical_count": mind.get("canonical_count", "n/a"),
            "dominant_theme": mind.get("dominant_theme", pick(
                mind, ["canonical_theme"], "n/a"
            )),
            "coherence": mind.get("coherence", "n/a"),
            "hunger_level": mind.get("hunger_level", "n/a"),
            "d0_voice_pct": mind.get("d0_voice_pct", pick(
                mind, ["d0_voice_frequency", "d0_frequency"], "n/a"
            )),
            "d9_voice_pct": mind.get("d9_voice_pct", pick(
                mind, ["d9_voice_frequency", "d9_frequency"], "n/a"
            )),
            "synod_count": mind.get("synod_count", pick(mind, ["synod_events"], 0)),
            "kaya_count": mind.get("kaya_count", pick(mind, ["kaya_events"], 0)),
            "human_conversation_count": mind.get(
                "human_conversation_count", pick(mind, ["human_conversations"], "n/a")
            ),
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
            "d16_pool_size": d16_count,
            "d16_sample_keys": [
                "source", "body_cycle", "timestamp", "verdict", "axiom",
                "proposal", "status", "d4_gate",
            ],
            "discord_inbound_count": "n/a",
            "rss_tension_count": "n/a",
        },
        "bridge": {
            "token": "YELLOW",
            "note": "Built from scheduled S3 snapshot pull.",
        },
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

    return snapshot


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snapshot = build()
    OUT_PATH.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
