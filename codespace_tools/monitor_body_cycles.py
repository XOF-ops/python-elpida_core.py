#!/usr/bin/env python3
"""
Monitor latest BODY cycles for provenance, noise, and PROMETHEUS model mix.

By default, this script downloads:
  s3://elpida-body-evolution/federation/body_decisions.jsonl

Examples:
  python codespace_tools/monitor_body_cycles.py
  python codespace_tools/monitor_body_cycles.py --window 180
  python codespace_tools/monitor_body_cycles.py --input /tmp/body_decisions_latest.jsonl
  python codespace_tools/monitor_body_cycles.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_BUCKET = "elpida-body-evolution"
DEFAULT_KEY = "federation/body_decisions.jsonl"
DEFAULT_REGION = "eu-north-1"
DEFAULT_LOCAL = Path("/tmp/body_decisions_latest.jsonl")

NOISE_RE = re.compile(
    r"/\*|\[\[Category:|QuickCategories|toolforge:|infobox|"
    r"Early life|History|Education|Selected literary works|Timeline of|List of|"
    r"reverted|grammar|tidy|spelling|copyedit|\bc/e\b",
    re.IGNORECASE,
)
LLM_TAG_RE = re.compile(r"\[LLM:([^\]]+)\]", re.IGNORECASE)


def _parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _download_s3(local_path: Path, bucket: str, key: str, region: str) -> None:
    cmd = [
        "aws",
        "s3",
        "cp",
        f"s3://{bucket}/{key}",
        str(local_path),
        "--region",
        region,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "aws s3 cp failed")


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _prometheus_provider_and_model(record: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    votes = record.get("_diag_node_votes") or {}
    node = votes.get("PROMETHEUS") or {}

    model = node.get("llm_model")
    provider = node.get("llm_provider")

    rationale = str(node.get("rationale", ""))
    if not provider and rationale:
        match = LLM_TAG_RE.search(rationale)
        if match:
            provider = match.group(1).strip().lower()
        else:
            provider = "keyword-only"

    if provider:
        provider = str(provider).strip().lower()
    if model is not None:
        model = str(model).strip() or None

    return provider, model


def _scan_record_noise(record: Dict[str, Any]) -> Tuple[int, List[str]]:
    hits = 0
    examples: List[str] = []

    action = str(record.get("_diag_action") or "")
    for line in action.split("\n"):
        s = line.strip()
        if not s:
            continue
        if NOISE_RE.search(s):
            hits += 1
            if len(examples) < 3:
                examples.append(s[:220])

    prov = record.get("input_event_provenance") or []
    if isinstance(prov, list):
        for ev in prov:
            if not isinstance(ev, dict):
                continue
            combo = " ".join(
                str(ev.get(k, ""))
                for k in ("source", "title", "comment", "domain", "subreddit")
            )
            if NOISE_RE.search(combo):
                hits += 1
                if len(examples) < 3:
                    examples.append(combo[:220])

    return hits, examples


def summarize(rows: List[Dict[str, Any]], window: int) -> Dict[str, Any]:
    stamped: List[Tuple[datetime, Dict[str, Any]]] = []
    for row in rows:
        ts = _parse_ts(row.get("timestamp"))
        if ts is None:
            continue
        stamped.append((ts, row))

    stamped.sort(key=lambda x: x[0])
    latest = [row for _, row in stamped[-window:]]

    verdict_counts = Counter(str(r.get("verdict", "UNKNOWN")) for r in latest)

    approvals = [
        float(r.get("parliament_approval"))
        for r in latest
        if isinstance(r.get("parliament_approval"), (int, float))
    ]
    avg_approval = round(sum(approvals) / len(approvals), 4) if approvals else None

    provider_mix = Counter()
    model_mix = Counter()
    provenance_present = 0
    provenance_sources = Counter()

    noise_hits = 0
    noise_examples: List[str] = []

    for row in latest:
        provider, model = _prometheus_provider_and_model(row)
        if provider:
            provider_mix[provider] += 1
        if model:
            model_mix[model] += 1

        prov = row.get("input_event_provenance")
        if isinstance(prov, list) and prov:
            provenance_present += 1
            for ev in prov:
                if isinstance(ev, dict):
                    src = str(ev.get("source") or "unknown").strip() or "unknown"
                    provenance_sources[src] += 1

        hits, ex = _scan_record_noise(row)
        noise_hits += hits
        for sample in ex:
            if len(noise_examples) < 8:
                noise_examples.append(sample)

    latest_row = latest[-1] if latest else {}

    return {
        "records_in_window": len(latest),
        "latest_timestamp": latest_row.get("timestamp"),
        "latest_cycle": latest_row.get("cycle"),
        "latest_verdict": latest_row.get("verdict"),
        "latest_approval": latest_row.get("parliament_approval"),
        "verdict_counts": dict(verdict_counts),
        "average_approval": avg_approval,
        "prometheus_provider_mix": dict(provider_mix),
        "prometheus_model_mix": dict(model_mix),
        "provenance_records": provenance_present,
        "provenance_source_counts": dict(provenance_sources),
        "noise_hit_count": noise_hits,
        "noise_examples": noise_examples,
    }


def _print_human(summary: Dict[str, Any]) -> None:
    print("BODY Cycle Monitor")
    print("=" * 70)
    print(f"records_in_window:      {summary['records_in_window']}")
    print(f"latest_timestamp:       {summary['latest_timestamp']}")
    print(f"latest_cycle:           {summary['latest_cycle']}")
    print(f"latest_verdict:         {summary['latest_verdict']}")
    print(f"latest_approval:        {summary['latest_approval']}")
    print(f"average_approval:       {summary['average_approval']}")
    print(f"provenance_records:     {summary['provenance_records']}")

    print("\nverdict_counts:")
    for k, v in summary["verdict_counts"].items():
        print(f"  {k}: {v}")

    print("\nprometheus_provider_mix:")
    if summary["prometheus_provider_mix"]:
        for k, v in summary["prometheus_provider_mix"].items():
            print(f"  {k}: {v}")
    else:
        print("  (none)")

    print("\nprometheus_model_mix:")
    if summary["prometheus_model_mix"]:
        for k, v in summary["prometheus_model_mix"].items():
            print(f"  {k}: {v}")
    else:
        print("  (none)")

    print("\nprovenance_source_counts:")
    if summary["provenance_source_counts"]:
        for k, v in summary["provenance_source_counts"].items():
            print(f"  {k}: {v}")
    else:
        print("  (none)")

    print(f"\nnoise_hit_count:        {summary['noise_hit_count']}")
    if summary["noise_examples"]:
        print("noise_examples:")
        for ex in summary["noise_examples"]:
            print(f"  - {ex}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor latest BODY cycles for noise and provider mix")
    parser.add_argument("--input", type=Path, help="Existing local JSONL file path")
    parser.add_argument("--window", type=int, default=120, help="Latest records (by timestamp) to analyze")
    parser.add_argument("--bucket", default=DEFAULT_BUCKET, help="S3 bucket for body_decisions.jsonl")
    parser.add_argument("--key", default=DEFAULT_KEY, help="S3 key for body_decisions.jsonl")
    parser.add_argument("--region", default=DEFAULT_REGION, help="S3 region")
    parser.add_argument("--download-to", type=Path, default=DEFAULT_LOCAL, help="Where to save downloaded JSONL")
    parser.add_argument("--json", action="store_true", help="Print JSON summary instead of human output")
    args = parser.parse_args()

    input_path = args.input
    if input_path is None:
        try:
            _download_s3(args.download_to, args.bucket, args.key, args.region)
            input_path = args.download_to
        except Exception as exc:
            print(f"ERROR: failed to download s3://{args.bucket}/{args.key}: {exc}", file=sys.stderr)
            return 2

    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 2

    rows = _load_jsonl(input_path)
    if not rows:
        print("ERROR: no valid JSON rows found", file=sys.stderr)
        return 2

    summary = summarize(rows, args.window)
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        _print_human(summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
