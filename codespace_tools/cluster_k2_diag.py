#!/usr/bin/env python3
"""
Cluster D13 -> K2 diagnostic signatures from CloudWatch text logs.

This parser consumes line-based CloudWatch message text and extracts
K2 diagnostic events emitted by native_cycle_engine.py:
  "K2 DIAG: D13 blocked payload sha256=<hash> preview=\"...\""

Input format:
- One message per line, or raw output from:
    aws logs filter-log-events ... --query 'events[].message' --output text | sed 's/\t/\n/g'
- Optional run metadata lines inserted by the extractor workflow:
    RUN_META run=424 stream=elpida/elpida-engine/<id>

Usage:
  python codespace_tools/cluster_k2_diag.py --input ElpidaInsights/k2_diag_runs_20260413_1600.log
  aws logs ... | sed 's/\t/\n/g' | python codespace_tools/cluster_k2_diag.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional


CYCLE_RE = re.compile(r"Cycle\s+(\d+):\s+Domain\s+(\d+)\s+\([^)]*\)\s*-\s*([A-Z_]+)")
PROVIDER_RE = re.compile(r"Provider:\s+([A-Za-z0-9_\-]+)")
QUESTION_RE = re.compile(r"Question:\s+(.*)")
RUN_META_RE = re.compile(r"RUN_META\s+run=(\d+)\s+stream=([^\s]+)")
STREAM_RE = re.compile(r"STREAM=([^\s]+)")
K2_DIAG_RE = re.compile(r"K2 DIAG:\s*D13 blocked payload\s+sha256=([0-9a-fA-F]{8,64})\s+preview=\"([^\"]*)\"")
K2_BLOCK_RE = re.compile(r"KERNEL HARD_BLOCK:\s*K2_KERNEL_IMMUTABILITY")
CB_RE = re.compile(r"\[CB\]\s*perplexity", re.IGNORECASE)
FALLBACK_RE = re.compile(r"Perplexity failed\s*[\-\u2013\u2014]?\s*silent fallback to\s+([A-Za-z0-9_\-]+)", re.IGNORECASE)


STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "what",
    "would",
    "our",
    "your",
    "their",
    "about",
    "under",
    "over",
    "when",
    "where",
    "which",
    "while",
    "must",
    "should",
    "could",
    "been",
    "were",
    "have",
    "has",
    "had",
    "are",
    "is",
    "its",
}


@dataclass
class K2DiagnosticEvent:
    run: Optional[int]
    stream: str
    cycle: Optional[int]
    domain: Optional[int]
    rhythm: str
    provider: str
    question: str
    cb_active: bool
    fallback_target: str
    sha256_prefix: str
    preview: str
    source: str


def _normalize_preview_signature(preview: str, token_limit: int = 8) -> str:
    text = re.sub(r"[^a-z0-9\s]", " ", preview.lower())
    tokens = [t for t in text.split() if len(t) > 2 and t not in STOPWORDS]
    if not tokens:
        return "(empty-preview)"
    return " ".join(tokens[:token_limit])


def parse_k2_events(lines: Iterable[str]) -> List[K2DiagnosticEvent]:
    events: List[K2DiagnosticEvent] = []

    run: Optional[int] = None
    stream = ""
    cycle: Optional[int] = None
    domain: Optional[int] = None
    rhythm = ""
    provider = ""
    question = ""
    cb_active = False
    fallback_target = ""
    saw_diag_in_context = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        run_match = RUN_META_RE.search(line)
        if run_match:
            run = int(run_match.group(1))
            stream = run_match.group(2)
            cycle = None
            domain = None
            rhythm = ""
            provider = ""
            question = ""
            cb_active = False
            fallback_target = ""
            saw_diag_in_context = False
            continue

        stream_match = STREAM_RE.search(line)
        if stream_match:
            stream = stream_match.group(1)
            continue

        cycle_match = CYCLE_RE.search(line)
        if cycle_match:
            cycle = int(cycle_match.group(1))
            domain = int(cycle_match.group(2))
            rhythm = cycle_match.group(3)
            provider = ""
            question = ""
            cb_active = False
            fallback_target = ""
            saw_diag_in_context = False
            continue

        provider_match = PROVIDER_RE.search(line)
        if provider_match:
            provider = provider_match.group(1)
            continue

        question_match = QUESTION_RE.search(line)
        if question_match:
            question = question_match.group(1)
            continue

        if CB_RE.search(line):
            cb_active = True
            continue

        fallback_match = FALLBACK_RE.search(line)
        if fallback_match:
            cb_active = True
            fallback_target = fallback_match.group(1)
            continue

        diag_match = K2_DIAG_RE.search(line)
        if diag_match:
            saw_diag_in_context = True
            events.append(
                K2DiagnosticEvent(
                    run=run,
                    stream=stream,
                    cycle=cycle,
                    domain=domain,
                    rhythm=rhythm,
                    provider=provider,
                    question=question,
                    cb_active=cb_active,
                    fallback_target=fallback_target,
                    sha256_prefix=diag_match.group(1)[:16],
                    preview=diag_match.group(2),
                    source="K2_DIAG",
                )
            )
            continue

        if K2_BLOCK_RE.search(line):
            # If we already captured a K2_DIAG line in this same cycle context,
            # avoid double counting the same event.
            if saw_diag_in_context:
                continue
            events.append(
                K2DiagnosticEvent(
                    run=run,
                    stream=stream,
                    cycle=cycle,
                    domain=domain,
                    rhythm=rhythm,
                    provider=provider,
                    question=question,
                    cb_active=cb_active,
                    fallback_target=fallback_target,
                    sha256_prefix="(missing)",
                    preview="",
                    source="K2_BLOCK_ONLY",
                )
            )

    return events


def _print_table(events: List[K2DiagnosticEvent]) -> None:
    print("\nK2 Diagnostic Events")
    print("=" * 120)
    header = (
        f"{'run':<6} {'stream':<12} {'cycle':<6} {'rhythm':<12} {'provider':<12} "
        f"{'sha256':<16} {'cb':<4} {'fallback':<12} question"
    )
    print(header)
    print("-" * len(header))

    for event in events:
        run = str(event.run) if event.run is not None else "-"
        stream_short = event.stream.split("/")[-1][:12] if event.stream else "-"
        cycle = str(event.cycle) if event.cycle is not None else "-"
        rhythm = event.rhythm or "-"
        provider = event.provider or "-"
        fallback = event.fallback_target or "-"
        cb = "yes" if event.cb_active else "no"
        question = event.question[:64] if event.question else "-"

        print(
            f"{run:<6} {stream_short:<12} {cycle:<6} {rhythm:<12} {provider:<12} "
            f"{event.sha256_prefix:<16} {cb:<4} {fallback:<12} {question}"
        )


def _print_clusters(events: List[K2DiagnosticEvent]) -> None:
    hash_counter = Counter(e.sha256_prefix for e in events)
    preview_counter = Counter(_normalize_preview_signature(e.preview) for e in events)

    print("\nHash Clusters")
    print("=" * 120)
    for key, count in hash_counter.most_common():
        print(f"{count:>3}  {key}")

    print("\nPreview Signature Clusters")
    print("=" * 120)
    for key, count in preview_counter.most_common():
        print(f"{count:>3}  {key}")


def _to_json_payload(events: List[K2DiagnosticEvent]) -> dict:
    hash_counter = Counter(e.sha256_prefix for e in events)
    preview_counter = Counter(_normalize_preview_signature(e.preview) for e in events)

    return {
        "event_count": len(events),
        "events": [asdict(e) for e in events],
        "clusters": {
            "by_hash": dict(hash_counter),
            "by_preview_signature": dict(preview_counter),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Cluster D13->K2 diagnostic signatures from CloudWatch text logs")
    parser.add_argument(
        "--input",
        help="Path to text log input. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--json-out",
        help="Optional path to write structured JSON output.",
    )
    args = parser.parse_args()

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
            return 2
        lines = input_path.read_text(encoding="utf-8", errors="replace").splitlines()
    else:
        lines = sys.stdin.read().splitlines()

    events = parse_k2_events(lines)
    if not events:
        print("No K2 diagnostic events found.")
        return 0

    _print_table(events)
    _print_clusters(events)

    if args.json_out:
        payload = _to_json_payload(events)
        out_path = Path(args.json_out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote JSON summary to: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
