#!/usr/bin/env python3
"""Build compact D15 broadcast index for dashboard hub.

Reads the aggregated broadcasts.jsonl from the WORLD bucket and produces
a summary-only d15_index.json with the fields the dashboard needs to
render the constitutional timeline without scanning S3.

Authority: Computer D13 CURSOR-TEMPORAL-BRIEF (e6641c0) — D15 is the
universal anchor across layers; the dashboard centers on D15 events,
not cycles or runs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_JSONL = ROOT / "_snapshot" / "raw" / "d15_broadcasts.jsonl"
OUT_PATH = ROOT / "observation_dashboard" / "data" / "d15_index.json"

# Keep the index small — most recent N entries only.
MAX_ENTRIES = 200

# Diplomat synthesis summary length.
SYNTHESIS_MAX_CHARS = 240


def _synthesis_head(text: str, n: int = SYNTHESIS_MAX_CHARS) -> str:
    text = (text or "").strip()
    if len(text) <= n:
        return text
    cut = text[:n]
    # Prefer breaking on sentence boundary.
    for sep in (". ", ".\n", "\n\n"):
        idx = cut.rfind(sep)
        if idx > n // 2:
            return cut[: idx + 1].rstrip()
    return cut.rstrip() + "…"


def _governance_summary(gov: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(gov, dict):
        return {}
    votes = gov.get("parliament_votes") or {}
    approvals = 0
    total = 0
    for v in votes.values():
        if not isinstance(v, dict):
            continue
        total += 1
        vote = str(v.get("vote", "")).upper()
        if vote.startswith("APPROVE") or vote == "LEAN_APPROVE":
            approvals += 1
    return {
        "verdict": gov.get("verdict"),
        "approval_rate": round(approvals / total, 3) if total else None,
        "vote_count": total,
        "approvals": approvals,
    }


def _compact_entry(broadcast: dict[str, Any]) -> dict[str, Any]:
    """Extract the summary fields. Unknown keys are dropped."""
    return {
        "broadcast_id": broadcast.get("broadcast_id"),
        "timestamp": broadcast.get("timestamp"),
        "axioms_in_tension": broadcast.get("axioms_in_tension") or [],
        "contributing_domains": broadcast.get("contributing_domains") or [],
        "pipeline_duration_s": broadcast.get("pipeline_duration_s"),
        "diplomat_synthesis": _synthesis_head(broadcast.get("d15_output", "")),
        "governance": _governance_summary(broadcast.get("governance") or {}),
        "llm_synthesis_success": (
            (broadcast.get("pipeline_stages") or {})
            .get("llm_synthesis", {})
            .get("success")
        ),
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def _axiom_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for e in entries:
        for ax in e.get("axioms_in_tension", []):
            counts[str(ax)] = counts.get(str(ax), 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))


def build() -> dict[str, Any]:
    raw = _read_jsonl(RAW_JSONL)
    compact = [_compact_entry(b) for b in raw if b.get("broadcast_id")]
    # Sort newest first.
    compact.sort(key=lambda e: e.get("timestamp") or "", reverse=True)
    recent = compact[:MAX_ENTRIES]
    latest = recent[0] if recent else None
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": "d15-index-v1",
        "total_count": len(compact),
        "index_size": len(recent),
        "axiom_distribution": _axiom_counts(compact),
        "latest": latest,
        "broadcasts": recent,
    }


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    index = build()
    OUT_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(
        f"Wrote {OUT_PATH} — total={index['total_count']} "
        f"indexed={index['index_size']}"
    )


if __name__ == "__main__":
    main()
