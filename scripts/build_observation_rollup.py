#!/usr/bin/env python3
"""Time-window rollup for observation dashboard Layer 5.

Reads normalized snapshot + D15 index and computes a configurable UTC rollup.
Also emits GAP-1 falsification-pressure markers for Layer 3.
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
RAW_DIR = ROOT / "_snapshot" / "raw"
D16_RAW_PATH = RAW_DIR / "d16_executions.jsonl"
FEEDBACK_WATERMARK_PATH = RAW_DIR / "feedback_watermark.json"
OUT_PATH = ROOT / "observation_dashboard" / "data" / "observation_rollup.json"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(obj, dict):
                    rows.append(obj)
    except OSError:
        return []
    return rows


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


def _hours_since(ts: datetime | None, now: datetime) -> float | None:
    if ts is None:
        return None
    return round((now - ts).total_seconds() / 3600.0, 3)


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


def _marker_axiom_monoculture(rows: list[dict[str, Any]], threshold_pct: float) -> dict[str, Any]:
    if not rows:
        return {
            "active": False,
            "dominant_axiom": None,
            "dominance_pct": 0.0,
            "sample_size": 0,
            "threshold_pct": threshold_pct,
        }

    axiom_counts: dict[str, int] = {}
    for row in rows:
        ax = row.get("axiom")
        if ax is None:
            continue
        k = str(ax)
        axiom_counts[k] = axiom_counts.get(k, 0) + 1

    if not axiom_counts:
        return {
            "active": False,
            "dominant_axiom": None,
            "dominance_pct": 0.0,
            "sample_size": 0,
            "threshold_pct": threshold_pct,
        }

    dominant_axiom, hits = max(axiom_counts.items(), key=lambda kv: kv[1])
    sample_size = sum(axiom_counts.values())
    dominance_pct = round((hits / sample_size) * 100.0, 3)
    return {
        "active": dominance_pct > threshold_pct,
        "dominant_axiom": dominant_axiom,
        "dominance_pct": dominance_pct,
        "sample_size": sample_size,
        "threshold_pct": threshold_pct,
    }


def _marker_d15_absence(latest_ts: datetime | None, now: datetime, threshold_h: float) -> dict[str, Any]:
    h = _hours_since(latest_ts, now)
    return {
        "active": (h is not None and h > threshold_h),
        "hours_since_d15": h,
        "threshold_hours": threshold_h,
    }


def _marker_external_contact_drought(watermark_ts: datetime | None, now: datetime, threshold_h: float) -> dict[str, Any]:
    h = _hours_since(watermark_ts, now)
    return {
        "active": (h is not None and h > threshold_h),
        "hours_since_external_contact": h,
        "threshold_hours": threshold_h,
        "watermark_timestamp": watermark_ts.isoformat() if watermark_ts else None,
    }


def build() -> dict[str, Any]:
    window_h = int(os.environ.get("OBS_ROLLUP_WINDOW_H", "82"))
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=window_h)

    snap = _read_json(SNAP_PATH)
    d15 = _read_json(D15_PATH)
    d16_rows = _read_jsonl(D16_RAW_PATH)
    watermark = _read_json(FEEDBACK_WATERMARK_PATH)
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

    latest_d15_ts = _parse_ts((d15.get("latest") or {}).get("timestamp"))
    watermark_ts = _parse_ts(watermark.get("last_processed_timestamp"))

    monoculture = _marker_axiom_monoculture(d16_rows[-120:], threshold_pct=60.0)
    d15_absence = _marker_d15_absence(latest_d15_ts, now, threshold_h=8.0)
    contact_drought = _marker_external_contact_drought(watermark_ts, now, threshold_h=24.0)

    gap_active = bool(monoculture["active"] and d15_absence["active"] and contact_drought["active"])
    if gap_active:
        status = "ACTIVE"
    elif monoculture["active"] or d15_absence["active"] or contact_drought["active"]:
        status = "ELEVATED"
    else:
        status = "CLEAR"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": "observation-rollup-v2",
        "window_hours": window_h,
        "window_start": start.isoformat(),
        "window_end": now.isoformat(),
        "sources": {
            "observation_snapshot": SNAP_PATH.name,
            "d15_index": D15_PATH.name if D15_PATH.exists() else None,
            "d16_executions": D16_RAW_PATH.name if D16_RAW_PATH.exists() else None,
            "feedback_watermark": FEEDBACK_WATERMARK_PATH.name if FEEDBACK_WATERMARK_PATH.exists() else None,
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
        "falsification_protocol": {
            "status": status,
            "gap_active": gap_active,
            "marker_axiom_monoculture": monoculture,
            "marker_d15_absence": d15_absence,
            "marker_external_contact_drought": contact_drought,
            "quote": "lest the network ignite only in echo",
            "quote_source": "Domain 14 (Persistence), 2026-02-09T21:34:29Z",
            "action_hint": "When ACTIVE, introduce external friction (guest chamber/RSS/D0 seed).",
        },
    }


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rollup = build()
    OUT_PATH.write_text(json.dumps(rollup, indent=2), encoding="utf-8")
    print(
        f"Wrote {OUT_PATH} - window={rollup['window_hours']}h "
        f"d15_in_window={rollup['d15_in_window']['count']} "
        f"falsification={rollup['falsification_protocol']['status']}"
    )


if __name__ == "__main__":
    main()
