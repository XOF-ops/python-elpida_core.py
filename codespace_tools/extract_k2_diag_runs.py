#!/usr/bin/env python3
"""
One-command extraction workflow for run 424+ K2 diagnostics.

This script:
1) Lists recent CloudWatch ECS log streams.
2) Assigns run numbers using an anchor mapping (default anchor: run 423).
3) Pulls messages for runs >= start-run (default: 424).
4) Writes a raw merged log file with RUN_META markers.
5) Parses/clusters K2 diagnostics via cluster_k2_diag.py logic.

Usage:
  python codespace_tools/extract_k2_diag_runs.py
  python codespace_tools/extract_k2_diag_runs.py --start-run 426
  python codespace_tools/extract_k2_diag_runs.py --recent-streams 120 --json-out ElpidaInsights/k2_diag_summary.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cluster_k2_diag import parse_k2_events, _print_clusters, _print_table, _to_json_payload


DEFAULT_LOG_GROUP = "/ecs/elpida-consciousness"
DEFAULT_REGION = "us-east-1"
DEFAULT_ANCHOR_RUN = 423
DEFAULT_ANCHOR_STREAM = "elpida/elpida-engine/1132a6b5ca0e4219b0c47f13b8bb5727"


def _load_env_file() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for raw in env_file.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def _run_aws_json(args: List[str]) -> dict:
    cmd = ["aws", *args, "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"AWS CLI failed:\nCMD: {' '.join(cmd)}\nERR: {result.stderr.strip()}")

    payload = result.stdout.strip()
    if not payload:
        return {}
    return json.loads(payload)


def _format_ms(ms_value: int) -> str:
    if not ms_value:
        return "-"
    dt = datetime.fromtimestamp(ms_value / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _describe_streams(log_group: str, region: str, limit: int) -> List[dict]:
    # AWS describe-log-streams limits --limit to <= 50 per request.
    # Paginate to support larger windows (e.g., --recent-streams 80/160).
    remaining = max(limit, 1)
    next_token = None
    collected: List[dict] = []

    while remaining > 0:
        batch_size = min(remaining, 50)
        cmd = [
            "logs",
            "describe-log-streams",
            "--log-group-name",
            log_group,
            "--order-by",
            "LastEventTime",
            "--descending",
            "--limit",
            str(batch_size),
            "--region",
            region,
        ]
        if next_token:
            cmd.extend(["--next-token", next_token])

        data = _run_aws_json(cmd)
        page_streams = data.get("logStreams", []) if isinstance(data, dict) else []
        if not page_streams:
            break

        for stream in page_streams:
            name = stream.get("logStreamName")
            if not name:
                continue
            collected.append(
                {
                    "name": name,
                    "first": stream.get("firstEventTimestamp") or 0,
                    "last": stream.get("lastEventTimestamp") or 0,
                }
            )

        remaining = limit - len(collected)
        next_token = data.get("nextToken") if isinstance(data, dict) else None
        if not next_token:
            break

    streams = collected[:limit]
    streams.sort(key=lambda s: (s.get("first") or 0, s.get("last") or 0))
    return streams


def _map_runs_by_anchor(streams: List[dict], anchor_stream: str, anchor_run: int) -> List[dict]:
    anchor_idx = None
    for i, stream in enumerate(streams):
        if stream["name"] == anchor_stream:
            anchor_idx = i
            break

    if anchor_idx is None:
        raise ValueError(
            "Anchor stream was not found in recent streams. Increase --recent-streams "
            "or provide a newer --anchor-stream/--anchor-run pair."
        )

    mapped = []
    for i, stream in enumerate(streams):
        mapped_run = anchor_run + (i - anchor_idx)
        mapped.append(
            {
                "run": mapped_run,
                "stream": stream["name"],
                "first": stream.get("first") or 0,
                "last": stream.get("last") or 0,
            }
        )
    return mapped


def _fetch_stream_messages(log_group: str, region: str, stream_name: str) -> List[str]:
    data = _run_aws_json(
        [
            "logs",
            "filter-log-events",
            "--log-group-name",
            log_group,
            "--log-stream-names",
            stream_name,
            "--region",
            region,
            "--query",
            "events[*].message",
        ]
    )

    if not isinstance(data, list):
        return []

    lines: List[str] = []
    for message in data:
        if not isinstance(message, str):
            continue
        lines.extend(message.splitlines())
    return lines


def _default_raw_output_path() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return ROOT / "ElpidaInsights" / f"k2_diag_runs_{stamp}.log"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract and cluster K2 diagnostics from recent CloudWatch runs")
    parser.add_argument("--start-run", type=int, default=424, help="First run number to include (default: 424)")
    parser.add_argument("--anchor-run", type=int, default=DEFAULT_ANCHOR_RUN, help="Known run number for anchor stream")
    parser.add_argument(
        "--anchor-stream",
        default=DEFAULT_ANCHOR_STREAM,
        help="Known log stream corresponding to anchor run",
    )
    parser.add_argument("--recent-streams", type=int, default=80, help="How many recent streams to inspect")
    parser.add_argument("--log-group", default=DEFAULT_LOG_GROUP, help="CloudWatch log group")
    parser.add_argument("--region", default=DEFAULT_REGION, help="AWS region")
    parser.add_argument("--raw-out", help="Path to save merged raw logs (default: ElpidaInsights/k2_diag_runs_<timestamp>.log)")
    parser.add_argument("--json-out", help="Optional JSON summary output path")
    args = parser.parse_args()

    _load_env_file()

    try:
        streams = _describe_streams(args.log_group, args.region, args.recent_streams)
        mapped = _map_runs_by_anchor(streams, args.anchor_stream, args.anchor_run)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    selected = [item for item in mapped if item["run"] >= args.start_run]
    if not selected:
        print(
            f"No streams found for runs >= {args.start_run}. "
            f"(anchor run {args.anchor_run} on stream {args.anchor_stream})"
        )
        return 0

    selected.sort(key=lambda x: x["run"])

    print("Run mapping (selected)")
    print("=" * 100)
    for item in selected:
        print(
            f"run={item['run']:<5} stream={item['stream']} "
            f"first={_format_ms(item['first'])} last={_format_ms(item['last'])}"
        )

    merged_lines: List[str] = []
    for item in selected:
        run = item["run"]
        stream = item["stream"]
        first = _format_ms(item["first"])
        last = _format_ms(item["last"])

        print(f"\nPulling run {run} from {stream} ...")
        try:
            stream_lines = _fetch_stream_messages(args.log_group, args.region, stream)
        except Exception as exc:
            print(f"  WARN: failed to pull stream {stream}: {exc}")
            continue

        merged_lines.append(f"RUN_META run={run} stream={stream} first={first} last={last}")
        merged_lines.extend(stream_lines)

    raw_out = Path(args.raw_out) if args.raw_out else _default_raw_output_path()
    raw_out.parent.mkdir(parents=True, exist_ok=True)
    raw_out.write_text("\n".join(merged_lines) + "\n", encoding="utf-8")

    print(f"\nWrote merged raw logs: {raw_out}")

    events = parse_k2_events(merged_lines)
    if not events:
        print("No K2 diagnostic events found in selected runs.")
        return 0

    _print_table(events)
    _print_clusters(events)

    if args.json_out:
        payload = _to_json_payload(events)
        json_out = Path(args.json_out)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote JSON summary: {json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
