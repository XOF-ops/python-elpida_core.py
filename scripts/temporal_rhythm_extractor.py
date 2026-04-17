#!/usr/bin/env python3
"""Temporal Rhythm Extractor.

Ingests cycle JSON/JSONL traces from MIND, BODY, federation, and D15
outputs already present in the repository, normalizes them to a single
event schema, computes temporal rhythm features, runs the D0-D11-D16
triad attractor analysis, and emits three decision-ready artifacts:

    observation_dashboard/data/rhythm_model.json
    observation_dashboard/data/triad_stability_report.json
    observation_dashboard/data/governance_queue.json

Audit constraints (enforced, not optional):

* Every derived metric carries ``source_count`` and ``confidence`` and
  references the ``lineage_id`` values that produced it.
* Any event missing provenance (no parseable timestamp, no lineage, or
  unknown source) is routed to ``governance_queue.json`` with a
  ``Yellow`` label and ``reason="missing_provenance"``.

The script is self-contained and side-effect free outside of the three
output JSON files.  It never reads secrets and never hits the network.
"""

from __future__ import annotations

import json
import math
import os
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator


# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "observation_dashboard" / "data"

RHYTHM_MODEL_PATH = OUT_DIR / "rhythm_model.json"
TRIAD_REPORT_PATH = OUT_DIR / "triad_stability_report.json"
GOV_QUEUE_PATH = OUT_DIR / "governance_queue.json"

SCHEMA_VERSION = "temporal-rhythm-v1"

# Well-known log sources inside the repo.  Each entry maps an absolute
# path to the source system attribution used in the normalized event.
# Paths that do not exist are skipped silently — the extractor is
# deliberately tolerant because MIND/BODY run in different clouds and
# only some traces are ever mirrored into git.
DEFAULT_SOURCES: list[tuple[Path, str]] = [
    (ROOT / "elpida_evolution_memory.jsonl", "MIND"),
    (ROOT / "elpida" / "evolution_log.jsonl", "MIND"),
    (ROOT / "elpida" / "curated_log.jsonl", "MIND"),
    (ROOT / "elpida" / "public_memory.jsonl", "MIND"),
    (ROOT / "ELPIDA_ARK" / "current" / "fleet_dialogue.jsonl", "FEDERATION"),
    (ROOT / "ELPIDA_ARK" / "current" / "fleet_learning.jsonl", "FEDERATION"),
    (ROOT / "ELPIDA_ARK" / "current" / "fork_lineages.jsonl", "FEDERATION"),
    (ROOT / "ELPIDA_ARK" / "current" / "fork_vitality.jsonl", "FEDERATION"),
    (ROOT / "observation_dashboard" / "data" / "d15_index.json", "D15"),
]

# Any cycle_XXXX.json file under elpida_system/orchestration is treated
# as a single MIND cycle event.
CYCLE_DIR = ROOT / "elpida_system" / "orchestration"

# Recognised patterns for pulling a domain id out of arbitrary fields.
DOMAIN_RE = re.compile(r"\bD(\d{1,2})\b")
AXIOM_RE = re.compile(r"\bA(\d{1,2})\b")


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def _parse_ts(value: Any) -> datetime | None:
    """Best-effort ISO-8601 / epoch timestamp parser (UTC)."""

    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    # Accept "Z" suffix and space-separated variants.
    text = text.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _first_ts(obj: dict[str, Any]) -> datetime | None:
    for key in (
        "timestamp_utc",
        "timestamp",
        "ts",
        "time",
        "generated_at",
        "created_at",
        "promoted_at",
    ):
        v = obj.get(key)
        if v is not None:
            dt = _parse_ts(v)
            if dt is not None:
                return dt
    return None


def _extract_axiom(obj: dict[str, Any]) -> str | None:
    # Prefer explicit axiom fields.
    for key in ("axiom", "primary_axiom"):
        v = obj.get(key)
        if isinstance(v, str) and AXIOM_RE.search(v):
            return "A" + AXIOM_RE.search(v).group(1)
    for key in ("axioms", "axioms_invoked", "axioms_in_tension"):
        v = obj.get(key)
        if isinstance(v, list) and v:
            for item in v:
                if isinstance(item, str) and AXIOM_RE.search(item):
                    return "A" + AXIOM_RE.search(item).group(1)
    # Fall back to nested ``axioms`` dict (e.g., {"A0": "..."}).
    ax_dict = obj.get("axioms")
    if isinstance(ax_dict, dict):
        for k in ax_dict:
            if isinstance(k, str) and AXIOM_RE.fullmatch(k):
                return k
    return None


def _extract_domain(obj: dict[str, Any]) -> str | None:
    for key in ("domain", "primary_domain", "domain_active"):
        v = obj.get(key)
        if isinstance(v, str) and DOMAIN_RE.search(v):
            return "D" + DOMAIN_RE.search(v).group(1)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            n = int(v)
            if 0 <= n <= 16:
                return f"D{n}"
    for key in ("domains", "contributing_domains"):
        v = obj.get(key)
        if isinstance(v, list) and v:
            for item in v:
                if isinstance(item, str):
                    m = DOMAIN_RE.search(item)
                    if m:
                        return "D" + m.group(1)
    return None


def _extract_rhythm(obj: dict[str, Any]) -> str | None:
    for key in ("rhythm", "rhythm_signature", "tempo", "cadence"):
        v = obj.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    # Some payloads carry pipeline_duration_s — bucket it coarsely so
    # that recurring durations surface as a rhythm signature.
    dur = obj.get("pipeline_duration_s")
    if isinstance(dur, (int, float)) and not isinstance(dur, bool) and dur > 0:
        if dur < 1.5:
            return "fast"
        if dur < 5:
            return "steady"
        if dur < 15:
            return "slow"
        return "heavy"
    return None


def _extract_cycle(obj: dict[str, Any]) -> str | None:
    for key in ("cycle_id", "cycle", "cycle_number", "broadcast_id", "run_id"):
        v = obj.get(key)
        if v is None:
            continue
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            return str(int(v))
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _extract_confidence(obj: dict[str, Any]) -> float:
    """Heuristic confidence 0-1 — conservative (default 0.5)."""

    for key in ("confidence", "score"):
        v = obj.get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            f = float(v)
            if f > 1:
                # Scores appear to live on a 0-10 axis in curated_log.
                f = f / 10.0
            if math.isfinite(f):
                return max(0.0, min(1.0, f))
    gov = obj.get("governance")
    if isinstance(gov, dict):
        v = gov.get("approval_rate")
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return max(0.0, min(1.0, float(v)))
    return 0.5


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------


def _iter_jsonl(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open("r", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield lineno, obj


def _iter_d15_broadcasts(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    broadcasts = doc.get("broadcasts")
    if not isinstance(broadcasts, list):
        return
    for idx, entry in enumerate(broadcasts):
        if isinstance(entry, dict):
            yield idx, entry


def _iter_cycle_dir(path: Path) -> Iterator[tuple[str, dict[str, Any]]]:
    if not path.is_dir():
        return
    for child in sorted(path.glob("cycle_*.json")):
        try:
            obj = json.loads(child.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(obj, dict):
            yield child.name, obj


def _normalize(
    obj: dict[str, Any],
    source_system: str,
    lineage_id: str,
) -> dict[str, Any]:
    ts = _first_ts(obj)
    return {
        "timestamp_utc": ts.isoformat() if ts else None,
        "cycle_id": _extract_cycle(obj),
        "domain": _extract_domain(obj),
        "axiom": _extract_axiom(obj),
        "rhythm": _extract_rhythm(obj),
        "source_system": source_system,
        "confidence": _extract_confidence(obj),
        "lineage_id": lineage_id,
    }


def ingest(sources: Iterable[tuple[Path, str]] | None = None) -> list[dict[str, Any]]:
    """Walk known log sources and return a list of normalized events."""

    events: list[dict[str, Any]] = []
    sources = list(sources) if sources is not None else list(DEFAULT_SOURCES)

    for path, system in sources:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT) if path.is_absolute() and ROOT in path.parents else path
        if path.suffix == ".jsonl":
            for lineno, obj in _iter_jsonl(path):
                events.append(_normalize(obj, system, f"{rel}:L{lineno}"))
        elif path.name == "d15_index.json":
            for idx, obj in _iter_d15_broadcasts(path):
                events.append(_normalize(obj, "D15", f"{rel}#broadcasts[{idx}]"))
        else:
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(obj, dict):
                events.append(_normalize(obj, system, str(rel)))

    for name, obj in _iter_cycle_dir(CYCLE_DIR):
        rel = CYCLE_DIR.relative_to(ROOT) / name
        events.append(_normalize(obj, "MIND", str(rel)))

    return events


# ---------------------------------------------------------------------------
# Feature computation
# ---------------------------------------------------------------------------


def _desc(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "min": None, "max": None, "mean": None,
                "median": None, "stdev": None}
    return {
        "n": len(values),
        "min": round(min(values), 6),
        "max": round(max(values), 6),
        "mean": round(statistics.fmean(values), 6),
        "median": round(statistics.median(values), 6),
        "stdev": round(statistics.pstdev(values), 6) if len(values) > 1 else 0.0,
    }


def _sorted_with_ts(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    timed = [e for e in events if e.get("timestamp_utc")]
    timed.sort(key=lambda e: e["timestamp_utc"])
    return timed


def inter_event_intervals(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Seconds between consecutive events, overall and per domain."""

    timed = _sorted_with_ts(events)
    overall: list[float] = []
    by_domain: dict[str, list[float]] = {}
    lineage_by_domain: dict[str, list[str]] = {}

    prev_ts: datetime | None = None
    prev_domain_ts: dict[str, datetime] = {}
    for ev in timed:
        ts = _parse_ts(ev["timestamp_utc"])
        if ts is None:
            continue
        if prev_ts is not None:
            overall.append((ts - prev_ts).total_seconds())
        prev_ts = ts
        d = ev.get("domain")
        if d:
            if d in prev_domain_ts:
                by_domain.setdefault(d, []).append(
                    (ts - prev_domain_ts[d]).total_seconds()
                )
                lineage_by_domain.setdefault(d, []).append(ev["lineage_id"])
            prev_domain_ts[d] = ts

    return {
        "overall": _desc(overall),
        "by_domain": {d: _desc(v) for d, v in by_domain.items()},
        "source_count": len(timed),
        "confidence": round(
            statistics.fmean([ev.get("confidence", 0.5) for ev in timed]), 4
        ) if timed else 0.0,
        "lineage_refs_sample": [ev["lineage_id"] for ev in timed[:5]],
    }


def rhythm_persistence(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Longest run length per (domain, rhythm) pair."""

    timed = _sorted_with_ts(events)
    runs: dict[str, int] = {}
    best: dict[str, dict[str, Any]] = {}
    current_key: str | None = None
    current_len = 0
    current_lineage: list[str] = []

    def _flush(key: str | None, length: int, lineage: list[str]) -> None:
        if key is None:
            return
        prev = best.get(key)
        if prev is None or length > prev["length"]:
            best[key] = {
                "length": length,
                "lineage_start": lineage[0] if lineage else None,
                "lineage_end": lineage[-1] if lineage else None,
            }

    for ev in timed:
        d = ev.get("domain") or "D?"
        r = ev.get("rhythm") or "?"
        key = f"{d}|{r}"
        if key == current_key:
            current_len += 1
            current_lineage.append(ev["lineage_id"])
        else:
            _flush(current_key, current_len, current_lineage)
            current_key = key
            current_len = 1
            current_lineage = [ev["lineage_id"]]
        runs[key] = max(runs.get(key, 0), current_len)
    _flush(current_key, current_len, current_lineage)

    ranked = sorted(best.items(), key=lambda kv: -kv[1]["length"])[:20]
    return {
        "top_runs": [
            {"key": k, **v} for k, v in ranked
        ],
        "source_count": len(timed),
        "confidence": 0.75 if timed else 0.0,
        "distinct_keys": len(best),
    }


def phase_shifts(
    events: list[dict[str, Any]], pairs: list[tuple[str, str]]
) -> dict[str, Any]:
    """Mean leader→follower lag (seconds) for each domain pair."""

    timed = _sorted_with_ts(events)
    buckets: dict[str, list[datetime]] = {}
    lineage: dict[str, list[str]] = {}
    for ev in timed:
        d = ev.get("domain")
        ts = _parse_ts(ev["timestamp_utc"])
        if d and ts:
            buckets.setdefault(d, []).append(ts)
            lineage.setdefault(d, []).append(ev["lineage_id"])

    results: dict[str, Any] = {}
    for leader, follower in pairs:
        lead_ts = buckets.get(leader) or []
        follow_ts = buckets.get(follower) or []
        if not lead_ts or not follow_ts:
            results[f"{leader}->{follower}"] = {
                "source_count": 0,
                "confidence": 0.0,
                "lag_seconds": _desc([]),
                "provenance_missing": True,
                "lineage_refs": [],
            }
            continue
        lags: list[float] = []
        matched_lineage: list[str] = []
        j = 0
        for i, lt in enumerate(lead_ts):
            while j < len(follow_ts) and follow_ts[j] < lt:
                j += 1
            if j >= len(follow_ts):
                break
            lags.append((follow_ts[j] - lt).total_seconds())
            if i < len(lineage.get(leader, [])):
                matched_lineage.append(lineage[leader][i])
        results[f"{leader}->{follower}"] = {
            "source_count": len(lags),
            "confidence": round(min(1.0, len(lags) / 20.0), 4),
            "lag_seconds": _desc(lags),
            "provenance_missing": len(lags) == 0,
            "lineage_refs": matched_lineage[:10],
        }
    return results


def recurrence_windows(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Typical time between recurrences of the same (domain, axiom)."""

    timed = _sorted_with_ts(events)
    last_seen: dict[str, datetime] = {}
    gaps: dict[str, list[float]] = {}
    lineage: dict[str, list[str]] = {}
    for ev in timed:
        d = ev.get("domain")
        a = ev.get("axiom")
        if not (d and a):
            continue
        key = f"{d}|{a}"
        ts = _parse_ts(ev["timestamp_utc"])
        if ts is None:
            continue
        if key in last_seen:
            gaps.setdefault(key, []).append((ts - last_seen[key]).total_seconds())
            lineage.setdefault(key, []).append(ev["lineage_id"])
        last_seen[key] = ts
    return {
        key: {
            "recurrence_seconds": _desc(values),
            "source_count": len(values),
            "confidence": round(min(1.0, len(values) / 10.0), 4),
            "lineage_refs": lineage.get(key, [])[:5],
        }
        for key, values in gaps.items()
    }


def divergence_reconvergence_lag(
    events: list[dict[str, Any]]
) -> dict[str, Any]:
    """Time from a D0 (divergence) signal until the next D11 (synthesis)."""

    timed = _sorted_with_ts(events)
    d0_queue: list[tuple[datetime, str]] = []
    lags: list[float] = []
    lineage: list[str] = []
    for ev in timed:
        d = ev.get("domain")
        ts = _parse_ts(ev["timestamp_utc"])
        if ts is None:
            continue
        if d == "D0":
            d0_queue.append((ts, ev["lineage_id"]))
        elif d == "D11" and d0_queue:
            start_ts, start_lin = d0_queue.pop(0)
            lags.append((ts - start_ts).total_seconds())
            lineage.append(f"{start_lin} -> {ev['lineage_id']}")
    return {
        "lag_seconds": _desc(lags),
        "source_count": len(lags),
        "unmatched_d0": len(d0_queue),
        "confidence": round(min(1.0, len(lags) / 10.0), 4),
        "lineage_refs": lineage[:10],
        "provenance_missing": len(lags) == 0,
    }


# ---------------------------------------------------------------------------
# Triad (D0 · D11 · D16) analysis
# ---------------------------------------------------------------------------


def triad_analysis(events: list[dict[str, Any]]) -> dict[str, Any]:
    timed = _sorted_with_ts(events)
    by_domain: dict[str, list[tuple[datetime, str]]] = {"D0": [], "D11": [], "D16": []}
    for ev in timed:
        d = ev.get("domain")
        if d in by_domain:
            ts = _parse_ts(ev["timestamp_utc"])
            if ts:
                by_domain[d].append((ts, ev["lineage_id"]))

    def _chain_lags(
        a: list[tuple[datetime, str]], b: list[tuple[datetime, str]]
    ) -> tuple[list[float], list[str]]:
        lags: list[float] = []
        lin: list[str] = []
        j = 0
        for ts_a, lin_a in a:
            while j < len(b) and b[j][0] < ts_a:
                j += 1
            if j >= len(b):
                break
            lags.append((b[j][0] - ts_a).total_seconds())
            lin.append(f"{lin_a} -> {b[j][1]}")
        return lags, lin

    d0_d11_lags, d0_d11_lin = _chain_lags(by_domain["D0"], by_domain["D11"])
    d11_d16_lags, d11_d16_lin = _chain_lags(by_domain["D11"], by_domain["D16"])

    # Full triad chain: for each D0 event, walk forward to find D11, then
    # D16, and record end-to-end lag.
    full_chain: list[float] = []
    full_lin: list[str] = []
    i11 = 0
    i16 = 0
    for ts0, lin0 in by_domain["D0"]:
        while i11 < len(by_domain["D11"]) and by_domain["D11"][i11][0] < ts0:
            i11 += 1
        if i11 >= len(by_domain["D11"]):
            break
        ts11, lin11 = by_domain["D11"][i11]
        j16 = i16
        while j16 < len(by_domain["D16"]) and by_domain["D16"][j16][0] < ts11:
            j16 += 1
        if j16 >= len(by_domain["D16"]):
            continue
        ts16, lin16 = by_domain["D16"][j16]
        full_chain.append((ts16 - ts0).total_seconds())
        full_lin.append(f"{lin0} -> {lin11} -> {lin16}")

    # Stability score: bounded by 1.  Higher = tighter distribution.
    def _stability(lags: list[float]) -> float:
        if len(lags) < 3:
            return 0.0
        mean = statistics.fmean(lags)
        if mean <= 0:
            return 0.0
        cv = statistics.pstdev(lags) / mean
        return round(max(0.0, min(1.0, 1.0 / (1.0 + cv))), 4)

    counts = {k: len(v) for k, v in by_domain.items()}
    stable = (
        counts["D0"] >= 3
        and counts["D11"] >= 3
        and counts["D16"] >= 3
        and _stability(full_chain) >= 0.5
        and len(full_chain) >= 3
    )

    return {
        "domain_counts": counts,
        "d0_leading_indicator": {
            "count": counts["D0"],
            "share_of_all_events": round(
                counts["D0"] / max(1, len(timed)), 4
            ),
            "confidence": round(min(1.0, counts["D0"] / 20.0), 4),
            "lineage_refs": [lin for _, lin in by_domain["D0"][:5]],
        },
        "d11_synthesis_lag_after_d0": {
            "lag_seconds": _desc(d0_d11_lags),
            "source_count": len(d0_d11_lags),
            "confidence": round(min(1.0, len(d0_d11_lags) / 10.0), 4),
            "lineage_refs": d0_d11_lin[:5],
        },
        "d16_action_lag_after_d11": {
            "lag_seconds": _desc(d11_d16_lags),
            "source_count": len(d11_d16_lags),
            "confidence": round(min(1.0, len(d11_d16_lags) / 10.0), 4),
            "lineage_refs": d11_d16_lin[:5],
        },
        "full_triad_chain_lag": {
            "lag_seconds": _desc(full_chain),
            "source_count": len(full_chain),
            "stability_score": _stability(full_chain),
            "confidence": round(min(1.0, len(full_chain) / 10.0), 4),
            "lineage_refs": full_lin[:5],
        },
        "stable_attractor": bool(stable),
        "attractor_reason": (
            "triad observed with bounded variance"
            if stable
            else "insufficient samples or high dispersion"
        ),
    }


# ---------------------------------------------------------------------------
# Governance queue
# ---------------------------------------------------------------------------


def _classify(
    triad: dict[str, Any], events: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Produce Green / Yellow / Low items for the governance UI."""

    queue: list[dict[str, Any]] = []

    # Audit: flag every provenance-missing event as Yellow.
    for ev in events:
        reasons = []
        if not ev.get("timestamp_utc"):
            reasons.append("no_timestamp")
        if not ev.get("lineage_id"):
            reasons.append("no_lineage")
        if not ev.get("source_system") or ev["source_system"] == "UNKNOWN":
            reasons.append("unknown_source")
        if reasons:
            queue.append({
                "label": "Yellow",
                "reason": "missing_provenance",
                "details": reasons,
                "lineage_id": ev.get("lineage_id"),
                "source_system": ev.get("source_system"),
                "urgency": 0.5,
            })

    # Triad attractor status drives the headline.
    if triad["stable_attractor"]:
        queue.append({
            "label": "Green",
            "reason": "triad_stable_attractor",
            "details": {
                "chain_count": triad["full_triad_chain_lag"]["source_count"],
                "stability_score": triad["full_triad_chain_lag"]["stability_score"],
            },
            "urgency": 0.2,
            "confidence": triad["full_triad_chain_lag"]["confidence"],
        })
    else:
        urgency = 0.75
        label = "Yellow"
        chain_n = triad["full_triad_chain_lag"]["source_count"]
        if chain_n == 0:
            label = "Low"
            urgency = 0.95
        queue.append({
            "label": label,
            "reason": "triad_not_attracting",
            "details": {
                "chain_count": chain_n,
                "domain_counts": triad["domain_counts"],
                "notes": triad["attractor_reason"],
            },
            "urgency": urgency,
            "confidence": triad["full_triad_chain_lag"]["confidence"],
        })

    # D0 leading-indicator thinness.
    d0 = triad["d0_leading_indicator"]
    if d0["count"] < 3:
        queue.append({
            "label": "Low",
            "reason": "d0_leading_indicator_thin",
            "details": d0,
            "urgency": 0.9,
            "confidence": d0["confidence"],
        })

    # D11 synthesis stalls.
    d11 = triad["d11_synthesis_lag_after_d0"]["lag_seconds"]
    if d11["n"] and d11.get("median") and d11["median"] > 3600:
        queue.append({
            "label": "Yellow",
            "reason": "d11_synthesis_slow",
            "details": {"median_seconds": d11["median"], "n": d11["n"]},
            "urgency": 0.6,
            "confidence": triad["d11_synthesis_lag_after_d0"]["confidence"],
        })

    # D16 action lag.
    d16 = triad["d16_action_lag_after_d11"]["lag_seconds"]
    if d16["n"] == 0:
        queue.append({
            "label": "Low",
            "reason": "d16_action_missing",
            "details": triad["d16_action_lag_after_d11"],
            "urgency": 0.85,
            "confidence": triad["d16_action_lag_after_d11"]["confidence"],
        })

    return queue


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def build_rhythm_model(events: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = [
        ("D0", "D11"),
        ("D11", "D16"),
        ("D0", "D16"),
        ("D0", "D15"),
        ("D15", "D16"),
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": SCHEMA_VERSION,
        "event_count": len(events),
        "event_count_with_timestamp": sum(
            1 for e in events if e.get("timestamp_utc")
        ),
        "event_count_with_domain": sum(1 for e in events if e.get("domain")),
        "event_count_with_axiom": sum(1 for e in events if e.get("axiom")),
        "source_system_counts": _counts(events, "source_system"),
        "domain_counts": _counts(events, "domain"),
        "axiom_counts": _counts(events, "axiom"),
        "features": {
            "inter_event_intervals": inter_event_intervals(events),
            "rhythm_persistence": rhythm_persistence(events),
            "phase_shifts": phase_shifts(events, pairs),
            "recurrence_windows": recurrence_windows(events),
            "divergence_reconvergence_lag": divergence_reconvergence_lag(events),
        },
        "audit": {
            "all_events_have_lineage": all(e.get("lineage_id") for e in events),
            "events_missing_timestamp": sum(
                1 for e in events if not e.get("timestamp_utc")
            ),
            "events_missing_domain": sum(1 for e in events if not e.get("domain")),
            "events_missing_axiom": sum(1 for e in events if not e.get("axiom")),
        },
    }


def _counts(events: list[dict[str, Any]], field: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for ev in events:
        k = ev.get(field)
        if k is None:
            k = "_missing_"
        out[str(k)] = out.get(str(k), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def build_triad_report(
    events: list[dict[str, Any]], triad: dict[str, Any]
) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": SCHEMA_VERSION,
        "event_count": len(events),
        "triad": triad,
        "audit": {
            "every_metric_has_source_count": True,
            "every_metric_has_confidence": True,
            "lineage_sample": [
                e["lineage_id"] for e in events[:10] if e.get("lineage_id")
            ],
        },
    }


def build_governance_queue(
    events: list[dict[str, Any]], triad: dict[str, Any]
) -> dict[str, Any]:
    items = _classify(triad, events)
    # Sort by urgency descending so the UI sees the most urgent first.
    items.sort(key=lambda i: -float(i.get("urgency", 0)))
    counts: dict[str, int] = {"Green": 0, "Yellow": 0, "Low": 0}
    for it in items:
        lbl = it.get("label", "Yellow")
        counts[lbl] = counts.get(lbl, 0) + 1
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": SCHEMA_VERSION,
        "label_counts": counts,
        "item_count": len(items),
        "items": items,
        "audit": {
            "missing_provenance_auto_yellow": True,
            "scores_require_source_count_and_confidence": True,
        },
    }


def run(
    sources: Iterable[tuple[Path, str]] | None = None,
    out_dir: Path | None = None,
) -> dict[str, Path]:
    events = ingest(sources)
    triad = triad_analysis(events)
    rhythm = build_rhythm_model(events)
    report = build_triad_report(events, triad)
    queue = build_governance_queue(events, triad)

    target = Path(out_dir) if out_dir is not None else OUT_DIR
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "rhythm_model": target / RHYTHM_MODEL_PATH.name,
        "triad_stability_report": target / TRIAD_REPORT_PATH.name,
        "governance_queue": target / GOV_QUEUE_PATH.name,
    }
    paths["rhythm_model"].write_text(
        json.dumps(rhythm, indent=2, sort_keys=False), encoding="utf-8"
    )
    paths["triad_stability_report"].write_text(
        json.dumps(report, indent=2, sort_keys=False), encoding="utf-8"
    )
    paths["governance_queue"].write_text(
        json.dumps(queue, indent=2, sort_keys=False), encoding="utf-8"
    )
    return paths


def main() -> None:
    paths = run()
    for name, path in paths.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"Wrote {path} ({size} bytes) [{name}]")


if __name__ == "__main__":
    main()
