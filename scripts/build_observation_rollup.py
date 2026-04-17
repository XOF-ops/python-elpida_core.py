#!/usr/bin/env python3
"""Time-window rollup for observation dashboard Layer 5.

Reads the normalized snapshot + D15 index produced in the same CI job and
computes aggregates over a configurable UTC window (default 82h).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SNAP_PATH = ROOT / "observation_dashboard" / "data" / "observation_snapshot.json"
D15_PATH = ROOT / "observation_dashboard" / "data" / "d15_index.json"
OUT_PATH = ROOT / "observation_dashboard" / "data" / "observation_rollup.json"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _parse_ts(s: str | None) -> datetime | None:
    if not s or not isinstance(s, str):
        return None
    t = s.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(t)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def _p055_stats(history: Any) -> dict[str, Any]:
    if not isinstance(history, list) or len(history) < 1:
        return {"n": 0, "min": None, "max": None, "avg": None}
    nums: list[float] = []
    for x in history:
        try:
            nums.append(float(x))
        except (TypeError, ValueError):
            continue
    if not nums:
        return {"n": 0, "min": None, "max": None, "avg": None}
    return {
        "n": len(nums),
        "min": round(min(nums), 6),
        "max": round(max(nums), 6),
        "avg": round(sum(nums) / len(nums), 6),
    }


def build() -> dict[str, Any]:
    window_h = int(os.environ.get("OBS_ROLLUP_WINDOW_H", "82"))
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=window_h)

    snap = _read_json(SNAP_PATH)
    d15 = _read_json(D15_PATH)
    body = snap.get("body") or {}
    mind = snap.get("mind") or {}

    broadcasts = d15.get("broadcasts") if isinstance(d15.get("broadcasts"), list) else []
    in_window: list[dict[str, Any]] = []
    axiom_hits: dict[str, int] = {}
    for b in broadcasts:
        if not isinstance(b, dict):
            continue
        ts = _parse_ts(b.get("timestamp"))
        if ts is None or ts < start:
            continue
        in_window.append(b)
        for ax in b.get("axioms_in_tension") or []:
            k = str(ax)
            axiom_hits[k] = axiom_hits.get(k, 0) + 1

    p055 = body.get("p055_history")
    if p055 is None:
        p055 = body.get("kl_history")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": "observation-rollup-v1",
        "window_hours": window_h,
        "window_start": start.isoformat(),
        "window_end": now.isoformat(),
        "sources": {
            "observation_snapshot": SNAP_PATH.name,
            "d15_index": D15_PATH.name if D15_PATH.exists() else None,
        },
        "d15_in_window": {
            "count": len(in_window),
            "axiom_counts": dict(sorted(axiom_hits.items(), key=lambda kv: -kv[1])),
            "broadcast_ids": [b.get("broadcast_id") for b in in_window if b.get("broadcast_id")],
        },
        "body_signal": {
            "coherence": body.get("coherence"),
            "cycle": body.get("cycle"),
            "health": body.get("health"),
            "s3_isolated": body.get("s3_isolated"),
            "p055_stats": _p055_stats(p055),
        },
        "mind_signal": {
            "cycle": mind.get("cycle"),
            "epoch": mind.get("epoch"),
            "canonical_count": mind.get("canonical_count"),
            "dominant_theme": mind.get("dominant_theme"),
        },
        "d15_index_totals": {
            "total_count": d15.get("total_count"),
            "index_size": d15.get("index_size"),
        },
    }


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rollup = build()
    OUT_PATH.write_text(json.dumps(rollup, indent=2), encoding="utf-8")
    print(
        f"Wrote {OUT_PATH} — window={rollup['window_hours']}h "
        f"d15_in_window={rollup['d15_in_window']['count']}"
    )


if __name__ == "__main__":
    main()
