#!/usr/bin/env python3
"""
verify_precedent_stats.py

Recomputes precedent statistics from ElpidaAI/elpida_evolution_memory.jsonl
so future precedents can cite verifier output rather than hand-carried
constants.

Usage:
    python3 verify_precedent_stats.py              # human-readable summary
    python3 verify_precedent_stats.py --json       # machine-readable JSON
    python3 verify_precedent_stats.py --help       # this message

Two filters are reported so the reader can compare segmentation choices:

  broad:  records with integer cycle, domain, and either coherence
      or coherence_score
  tight:  records with cycle, domain, provider, hunger_level, rhythm,
      and either coherence or coherence_score — the 55-cycle
      cloud-run family

Run segmentation: a new run begins whenever the current cycle is less
than or equal to the previous cycle (a cycle reset or decrease marks
the boundary). Truncated runs are those whose final cycle is less than
55.

Background: the precedent file
ElpidaAI/D16_PRECEDENT_20260412_buffered_silence.md cited constants like
"418 runs / 125 truncated / 30% / 42% D0+D11". GPT-5.4's cross-model
verification on 2026-04-13 recomputed under the tight filter and got
different numbers. The regime is the same; the exact figures are not.
This script exists so precedent prose can cite `python3
verify_precedent_stats.py --json` output by date rather than freezing
numbers into prose that drifts.

Outputs are stable across runs as long as the underlying JSONL is
stable. Methodology notes are included in the output so the reader
can audit the filters.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).parent
DEFAULT_LOG = REPO_ROOT / "ElpidaAI" / "elpida_evolution_memory.jsonl"

TIGHT_FIELDS = {"cycle", "domain", "provider", "hunger_level", "rhythm"}
TIGHT_COHERENCE_EQUIVALENTS = ("coherence", "coherence_score")
BROAD_FIELDS = {"cycle", "domain"}
BROAD_COHERENCE_EQUIVALENTS = ("coherence", "coherence_score")

VERIFIER_VERSION = "1.0.0"


def load_entries(
    path: Path,
    required: set[str],
    require_any: tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    with path.open() as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            cyc = obj.get("cycle")
            if not isinstance(cyc, int):
                continue
            if not required.issubset(obj.keys()):
                continue
            if require_any and not any(key in obj for key in require_any):
                continue
            entries.append(obj)
    return entries


def _coherence_value(record: dict[str, Any]) -> float | None:
    value = record.get("coherence")
    if not isinstance(value, (int, float)):
        value = record.get("coherence_score")
    if isinstance(value, (int, float)):
        return float(value)
    return None


def segment_runs(entries: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    runs: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    prev: int | None = None
    for e in entries:
        cyc = e["cycle"]
        if prev is not None and cyc <= prev:
            if current:
                runs.append(current)
            current = []
        current.append(e)
        prev = cyc
    if current:
        runs.append(current)
    return runs


def _stat_summary(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "mean": None, "min": None, "max": None}
    return {
        "count": len(values),
        "mean": round(sum(values) / len(values), 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def compute_stats(runs: list[list[dict[str, Any]]]) -> dict[str, Any]:
    total = len(runs)
    if total == 0:
        return {"total_runs": 0}

    truncated = [r for r in runs if r[-1]["cycle"] < 55]
    final_cycles = [r[-1]["cycle"] for r in runs]
    trunc_final_cycles = [r[-1]["cycle"] for r in truncated]
    trunc_domains = [r[-1].get("domain") for r in truncated]
    d0_d11 = sum(1 for r in truncated if r[-1].get("domain") in (0, 11))
    trunc_rhythms = [r[-1].get("rhythm") for r in truncated if r[-1].get("rhythm")]
    trunc_coherence = [
        value
        for value in (_coherence_value(r[-1]) for r in truncated)
        if value is not None
    ]
    trunc_hunger = [
        float(r[-1]["hunger_level"])
        for r in truncated
        if isinstance(r[-1].get("hunger_level"), (int, float))
    ]

    return {
        "total_runs": total,
        "truncated_runs": len(truncated),
        "full_runs": total - len(truncated),
        "truncation_rate": round(len(truncated) / total, 4),
        "death_cycle_top12": Counter(final_cycles).most_common(12),
        "cycle_17_deaths": sum(1 for c in trunc_final_cycles if c == 17),
        "cycle_50_deaths": sum(1 for c in trunc_final_cycles if c == 50),
        "cycle_54_deaths": sum(1 for c in trunc_final_cycles if c == 54),
        "trunc_domain_top10": Counter(trunc_domains).most_common(10),
        "d0_d11_share_of_truncated": (
            round(d0_d11 / len(truncated), 4) if truncated else None
        ),
        "trunc_rhythm_distribution": dict(Counter(trunc_rhythms)),
        "coherence_at_death": _stat_summary(trunc_coherence),
        "hunger_at_death": _stat_summary(trunc_hunger),
    }


def _print_section(label: str, data: dict[str, Any]) -> None:
    print(f"\n=== {label.upper()} FILTER ===")
    print(f"  filter fields:             {data['filter_fields']}")
    print(f"  entry count:               {data['entry_count']}")
    print(f"  total runs:                {data['total_runs']}")
    print(f"  truncated runs:            {data['truncated_runs']}")
    print(f"  full runs:                 {data['full_runs']}")
    print(f"  truncation rate:           {data['truncation_rate']}")
    print(f"  cycle 17 deaths:           {data['cycle_17_deaths']}")
    print(f"  cycle 50 deaths:           {data['cycle_50_deaths']}")
    print(f"  cycle 54 deaths:           {data['cycle_54_deaths']}")
    print(f"  D0+D11 share of truncated: {data['d0_d11_share_of_truncated']}")
    print(f"  death cycle top-12:        {data['death_cycle_top12']}")
    print(f"  trunc domain top-10:       {data['trunc_domain_top10']}")
    print(f"  trunc rhythm distribution: {data['trunc_rhythm_distribution']}")
    print(f"  coherence at death:        {data['coherence_at_death']}")
    print(f"  hunger at death:           {data['hunger_at_death']}")


def main() -> int:
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return 0

    as_json = "--json" in sys.argv
    log_path = DEFAULT_LOG
    if not log_path.exists():
        print(f"ERROR: log not found at {log_path}", file=sys.stderr)
        return 1

    file_stats = log_path.stat()

    results: dict[str, Any] = {
        "verifier_version": VERIFIER_VERSION,
        "log_path": str(log_path.relative_to(REPO_ROOT)),
        "log_size_bytes": file_stats.st_size,
        "log_mtime_epoch": int(file_stats.st_mtime),
        "methodology": {
            "broad_filter": (
                "records with integer cycle, domain, and either "
                "coherence or coherence_score"
            ),
            "tight_filter": (
                "records with cycle, domain, provider, hunger_level, rhythm, "
                "and either coherence or coherence_score — the 55-cycle "
                "cloud run family"
            ),
            "run_segmentation": (
                "cycle <= previous_cycle marks a run boundary"
            ),
            "truncation_definition": "final cycle of run < 55",
        },
        "broad": {},
        "tight": {},
    }

    for label, required in (("broad", BROAD_FIELDS), ("tight", TIGHT_FIELDS)):
        require_any = None
        if label == "broad":
            require_any = BROAD_COHERENCE_EQUIVALENTS
        if label == "tight":
            require_any = TIGHT_COHERENCE_EQUIVALENTS
        entries = load_entries(log_path, required, require_any=require_any)
        runs = segment_runs(entries)
        filter_fields = sorted(required)
        if label == "broad":
            filter_fields.append("coherence|coherence_score")
        if label == "tight":
            filter_fields.append("coherence|coherence_score")
        results[label] = {
            "filter_fields": filter_fields,
            "entry_count": len(entries),
            **compute_stats(runs),
        }

    if as_json:
        print(json.dumps(results, indent=2, default=str))
        return 0

    print(f"verify_precedent_stats.py v{results['verifier_version']}")
    print(f"log: {results['log_path']} ({results['log_size_bytes']} bytes)")
    print("methodology:")
    for k, v in results["methodology"].items():
        print(f"  {k}: {v}")
    _print_section("broad", results["broad"])
    _print_section("tight", results["tight"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
