#!/usr/bin/env python3
"""
d11_convergence_detector.py

Detects rare Domain 11 synthesis convergence windows in
ElpidaAI/elpida_evolution_memory.jsonl using the temporal/glow formula:

Strict detector (6-beat window ending on Domain 11 + SYNTHESIS):
  - coherence lock: all six beats have coherence == 1.0
  - hunger closure: hunger ladder with step -0.02 or plateau 0.0
  - ends at hunger 0.0
  - paired rhythms: A,A,B,B,C,C

Shape labels:
  - descending-ignition: hunger descends to zero across the window
  - zero-field-stabilization: hunger is zero across the window
  - hybrid: strict hit that is neither of the above

Usage:
  python3 d11_convergence_detector.py
  python3 d11_convergence_detector.py --json
  python3 d11_convergence_detector.py --path /abs/path/to/jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_LOG = REPO_ROOT / "ElpidaAI" / "elpida_evolution_memory.jsonl"


@dataclass
class InsightRow:
    line: int
    timestamp: datetime | None
    cycle: int | None
    rhythm: str | None
    domain: int | None
    provider: str | None
    coherence: float | None
    hunger: float | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect D11 convergence artifacts.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_LOG,
        help="Path to JSONL memory file (default: ElpidaAI/elpida_evolution_memory.jsonl)",
    )
    return parser.parse_args()


def _as_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def load_native_rows(path: Path) -> list[InsightRow]:
    rows: list[InsightRow] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "NATIVE_CYCLE_INSIGHT":
                continue
            rows.append(
                InsightRow(
                    line=line_no,
                    timestamp=_parse_timestamp(obj.get("timestamp")),
                    cycle=obj.get("cycle") if isinstance(obj.get("cycle"), int) else None,
                    rhythm=obj.get("rhythm") if isinstance(obj.get("rhythm"), str) else None,
                    domain=obj.get("domain") if isinstance(obj.get("domain"), int) else None,
                    provider=obj.get("provider") if isinstance(obj.get("provider"), str) else None,
                    coherence=_as_float(obj.get("coherence")),
                    hunger=_as_float(obj.get("hunger_level")),
                )
            )
    return rows


def _is_pair_pattern(rhythms: list[str | None]) -> bool:
    if len(rhythms) != 6:
        return False
    return rhythms[0] == rhythms[1] and rhythms[2] == rhythms[3] and rhythms[4] == rhythms[5]


def _hunger_ladder(hunger: list[float | None]) -> bool:
    if len(hunger) != 6:
        return False
    diffs: list[float] = []
    for i in range(5):
        if hunger[i] is None or hunger[i + 1] is None:
            return False
        diffs.append(round(hunger[i + 1] - hunger[i], 3))
    # Canonical ladder is -0.02 per step; allow plateau 0.0 in zero-field windows.
    return all(abs(delta + 0.02) <= 0.005 or abs(delta) <= 0.005 for delta in diffs)


def _coherence_lock(values: list[float | None]) -> bool:
    if len(values) != 6:
        return False
    return all(v is not None and abs(v - 1.0) < 1e-9 for v in values)


def _cadence_label(window: list[InsightRow]) -> str:
    if len(window) != 6:
        return "mixed"
    deltas: list[float] = []
    for i in range(1, 6):
        left = window[i - 1].timestamp
        right = window[i].timestamp
        if left is None or right is None:
            return "mixed"
        deltas.append((right - left).total_seconds())
    pulse = ["L" if d >= 7.0 else "S" for d in deltas]
    if pulse in (["L", "S", "L", "S", "L"], ["S", "L", "S", "L", "S"]):
        return "alternating"
    return "mixed"


def _shape_label(hunger: list[float | None]) -> str:
    if len(hunger) != 6 or any(v is None for v in hunger):
        return "hybrid"
    hun = [float(v) for v in hunger]  # type: ignore[arg-type]
    if all(abs(v) < 1e-9 for v in hun):
        return "zero-field-stabilization"
    if hun[0] > hun[-1]:
        return "descending-ignition"
    return "hybrid"


def detect_strict_hits(rows: list[InsightRow]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if row.domain != 11 or row.rhythm != "SYNTHESIS":
            continue
        window = rows[max(0, idx - 5) : idx + 1]
        if len(window) < 6:
            continue
        hunger = [w.hunger for w in window]
        rhythms = [w.rhythm for w in window]
        coherence = [w.coherence for w in window]

        end_zero = hunger[-1] is not None and abs(hunger[-1]) < 1e-9
        if not (_coherence_lock(coherence) and _hunger_ladder(hunger) and end_zero and _is_pair_pattern(rhythms)):
            continue

        hits.append(
            {
                "line": row.line,
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                "shape": _shape_label(hunger),
                "cadence": _cadence_label(window),
                "hunger_sequence": hunger,
                "rhythm_sequence": rhythms,
                "domain_sequence": [w.domain for w in window],
                "provider_sequence": [w.provider for w in window],
                "cycle_sequence": [w.cycle for w in window],
            }
        )
    return hits


def build_report(path: Path) -> dict[str, Any]:
    rows = load_native_rows(path)
    strict_hits = detect_strict_hits(rows)
    shape_counts = Counter(hit["shape"] for hit in strict_hits)
    cadence_counts = Counter(hit["cadence"] for hit in strict_hits)
    return {
        "detector_version": "1.0.0",
        "path": str(path),
        "native_rows": len(rows),
        "strict_hit_count": len(strict_hits),
        "shape_counts": dict(shape_counts),
        "cadence_counts": dict(cadence_counts),
        "strict_hits": strict_hits,
    }


def print_human(report: dict[str, Any]) -> None:
    print(f"d11_convergence_detector.py v{report['detector_version']}")
    print(f"path: {report['path']}")
    print(f"native rows: {report['native_rows']}")
    print(f"strict hits: {report['strict_hit_count']}")
    print(f"shape counts: {report['shape_counts']}")
    print(f"cadence counts: {report['cadence_counts']}")
    print("\nline | timestamp | shape | cadence | hunger | rhythms")
    for hit in report["strict_hits"]:
        print(
            f"{hit['line']} | {hit['timestamp']} | {hit['shape']} | "
            f"{hit['cadence']} | {hit['hunger_sequence']} | {hit['rhythm_sequence']}"
        )


def main() -> int:
    args = parse_args()
    target = args.path.resolve()
    if not target.exists():
        print(f"ERROR: log not found at {target}", file=sys.stderr)
        return 1
    report = build_report(target)
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
