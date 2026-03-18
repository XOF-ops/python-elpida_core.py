#!/usr/bin/env python3
"""
Read Cloud Runs — Pull and display Elpida cloud (Fargate) cycle data
=====================================================================

Downloads the cloud evolution memory from S3 directly (bypasses local sync
logic) and shows what each autonomous run produced.

Usage:
  # Show latest run
  python ElpidaS3Cloud/read_cloud_runs.py

  # Show last N runs
  python ElpidaS3Cloud/read_cloud_runs.py --runs 3

  # Show all runs
  python ElpidaS3Cloud/read_cloud_runs.py --runs 0

  # Show full insights (not truncated)
  python ElpidaS3Cloud/read_cloud_runs.py --full

  # Confirm schedule is working (check EventBridge + recent tasks)
  python ElpidaS3Cloud/read_cloud_runs.py --schedule
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── Auto-load .env ──────────────────────────────────────────────────────────
_env_file = ROOT / ".env"
if _env_file.exists():
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and "=" in _line and not _line.startswith("#"):
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())


def _s3_client(region="us-east-1"):
    import boto3
    return boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )


def pull_cloud_memory():
    """Download cloud evolution memory from S3, return list of parsed entries."""
    s3 = _s3_client("us-east-1")
    obj = s3.get_object(
        Bucket="elpida-consciousness",
        Key="memory/elpida_evolution_memory.jsonl",
    )
    data = obj["Body"].read().decode("utf-8").strip()
    if not data:
        return []
    entries = []
    for line in data.split("\n"):
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def _parse_ts(ts_str):
    """Parse timestamp string to naive datetime (strip timezone)."""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)
        return dt
    except (ValueError, AttributeError):
        return None


def split_into_runs(entries):
    """
    Split entries into autonomous Fargate runs.
    
    The S3 cloud memory contains:
    - MIND cycle insights (cycle=1..55, the actual thinking)
    - D15 broadcasts (domain=15, no cycle, BODY broadcasts)
    - Federation merge entries (cycle="merge_YYYYMMDD_HHMMSS")
    
    We separate these, group MIND insights by time gaps > 30 min,
    and filter out tiny sessions (merge-only or single entries).
    Returns (mind_runs, d15_entries, merge_entries).
    """
    mind_entries = []
    d15_entries = []
    merge_entries = []

    for entry in entries:
        cycle = entry.get("cycle")
        domain = entry.get("domain")

        if cycle is None and domain == 15:
            d15_entries.append(entry)
        elif isinstance(cycle, str) and cycle.startswith("merge_"):
            merge_entries.append(entry)
        elif cycle is not None:
            mind_entries.append(entry)
        else:
            d15_entries.append(entry)

    # Split MIND entries by time gaps > 30 minutes
    if not mind_entries:
        return [], d15_entries, merge_entries

    runs = []
    current = [mind_entries[0]]
    for entry in mind_entries[1:]:
        prev_ts = _parse_ts(current[-1].get("timestamp", ""))
        curr_ts = _parse_ts(entry.get("timestamp", ""))
        if prev_ts and curr_ts and (curr_ts - prev_ts).total_seconds() > 1800:
            runs.append(current)
            current = [entry]
        else:
            current.append(entry)
    if current:
        runs.append(current)

    # Filter: real Fargate runs have 10+ insights
    real_runs = [r for r in runs if len(r) >= 10]

    return real_runs, d15_entries, merge_entries


def display_run(run, index, total, full=False):
    """Display a single run's summary and insights."""
    if not run:
        return

    first = run[0]
    last = run[-1]
    ts_start = first.get("timestamp", "?")[:19]
    ts_end = last.get("timestamp", "?")[:19]

    # Separate cycle entries from D15 broadcasts
    cycle_entries = [e for e in run if e.get("cycle") is not None]
    d15_entries = [e for e in run if e.get("domain") == 15 and e.get("cycle") is None]

    cycle_start = cycle_entries[0].get("cycle", "?") if cycle_entries else "-"
    cycle_end = cycle_entries[-1].get("cycle", "?") if cycle_entries else "-"

    # Count domains
    domain_counts = defaultdict(int)
    for entry in run:
        domain = entry.get("domain", entry.get("domain_id", "?"))
        domain_counts[domain] += 1

    print(f"\n{'='*70}")
    print(f"  RUN {index}/{total}  |  {len(cycle_entries)} insights + {len(d15_entries)} D15  |  cycles {cycle_start}→{cycle_end}")
    print(f"  Time: {ts_start}  →  {ts_end}")
    print(f"  Domains: {dict(sorted(domain_counts.items(), key=lambda x: str(x[0])))}")
    print(f"{'='*70}")

    for entry in run:
        cycle = entry.get("cycle", "")
        domain = entry.get("domain", entry.get("domain_id", "?"))
        insight = entry.get("insight", entry.get("content", entry.get("pattern", "")))
        ts = entry.get("timestamp", "")[:16]

        if entry.get("domain") == 15 and entry.get("cycle") is None:
            label = "D15"
            text = insight.strip().split("\n")[0][:100] if insight else "[broadcast]"
            if not full:
                print(f"  [D15]      {text}")
                continue

        if full:
            domain_name = entry.get("domain_name", f"Domain {domain}")
            print(f"\n  [cycle {cycle}] {domain_name}  ({ts})")
            print(f"  {insight}")
        else:
            first_line = insight.strip().split("\n")[0] if insight else ""
            if len(first_line) > 120:
                first_line = first_line[:117] + "..."
            cycle_str = f"{cycle:>3}" if isinstance(cycle, int) else f"{'':>3}"
            print(f"  [{cycle_str}] D{domain:<3} {first_line}")


def show_schedule():
    """Check if EventBridge is firing and show recent task history."""
    import boto3

    print("\n" + "=" * 70)
    print("  ELPIDA CLOUD SCHEDULE STATUS")
    print("=" * 70)

    now = datetime.now(timezone.utc)
    print(f"\n  Current UTC: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # EventBridge rule
    events = boto3.client("events", region_name="us-east-1")
    try:
        rule = events.describe_rule(Name="elpida-scheduled-run")
        print(f"\n  EventBridge rule: {rule['Name']}")
        print(f"    State:    {rule['State']}")
        print(f"    Schedule: {rule['ScheduleExpression']}")

        targets = events.list_targets_by_rule(Rule="elpida-scheduled-run")
        for t in targets["Targets"]:
            ecs = t.get("EcsParameters", {})
            td = ecs.get("TaskDefinitionArn", "?").split("/")[-1]
            print(f"    Target:   {t['Id']} → {td}")
            print(f"    Role:     {t.get('RoleArn', '?').split('/')[-1]}")
    except Exception as e:
        print(f"  EventBridge: {e}")

    # CloudWatch metrics
    cw = boto3.client("cloudwatch", region_name="us-east-1")
    for metric in ["Invocations", "FailedInvocations"]:
        data = cw.get_metric_statistics(
            Namespace="AWS/Events",
            MetricName=metric,
            Dimensions=[{"Name": "RuleName", "Value": "elpida-scheduled-run"}],
            StartTime=now - timedelta(hours=48),
            EndTime=now,
            Period=14400,  # 4 hours
            Statistics=["Sum"],
        )
        pts = sorted(data["Datapoints"], key=lambda d: d["Timestamp"])
        print(f"\n  {metric} (last 48h, per 4h window):")
        if pts:
            for dp in pts:
                ts = dp["Timestamp"].strftime("%Y-%m-%d %H:%M")
                print(f"    {ts} UTC: {int(dp['Sum'])}")
        else:
            print("    None")

    # Recent log streams
    logs = boto3.client("logs", region_name="us-east-1")
    try:
        streams = logs.describe_log_streams(
            logGroupName="/ecs/elpida-consciousness",
            orderBy="LastEventTime",
            descending=True,
            limit=10,
        )
        print(f"\n  Recent Fargate runs:")
        for s in streams["logStreams"]:
            tid = s["logStreamName"].split("/")[-1][:12]
            first = datetime.fromtimestamp(
                s.get("firstEventTimestamp", 0) / 1000, tz=timezone.utc
            )
            last = datetime.fromtimestamp(
                s.get("lastEventTimestamp", 0) / 1000, tz=timezone.utc
            )
            dur = (last - first).total_seconds()
            status = "✅" if dur > 60 else "❌ crash"
            print(
                f"    {tid}  {first.strftime('%Y-%m-%d %H:%M')}-{last.strftime('%H:%M')} UTC  ({dur:.0f}s)  {status}"
            )
    except Exception as e:
        print(f"  Log streams: {e}")

    print()


def main():
    parser = argparse.ArgumentParser(description="Read Elpida cloud run data from S3")
    parser.add_argument(
        "--runs", type=int, default=1,
        help="Number of recent runs to show (0 = all, default: 1)",
    )
    parser.add_argument(
        "--full", action="store_true",
        help="Show full insight text (not truncated)",
    )
    parser.add_argument(
        "--schedule", action="store_true",
        help="Show EventBridge schedule status and recent task history",
    )
    args = parser.parse_args()

    if args.schedule:
        show_schedule()
        return

    print("☁️  Pulling cloud evolution memory from S3...")
    entries = pull_cloud_memory()
    print(f"   Downloaded {len(entries)} total entries")

    runs, d15_entries, merge_entries = split_into_runs(entries)
    mind_insights = sum(len(r) for r in runs)
    print(f"   {mind_insights} MIND insights across {len(runs)} Fargate runs")
    print(f"   {len(d15_entries)} D15 broadcasts, {len(merge_entries)} federation merges")

    if not runs:
        print("   No Fargate runs found.")
        return

    # Select which runs to show
    if args.runs == 0:
        selected = runs
    else:
        selected = runs[-args.runs:]

    start_idx = len(runs) - len(selected) + 1
    for i, run in enumerate(selected):
        display_run(run, start_idx + i, len(runs), full=args.full)

    # Summary
    latest = runs[-1]
    latest_ts = latest[-1].get("timestamp", "?")[:19]
    print(f"\n  Latest Fargate run ended: {latest_ts}")
    print(f"  Total Fargate runs: {len(runs)}")
    print(f"\n  Commands:")
    print(f"    --runs 3        Show last 3 runs")
    print(f"    --runs 0        Show all runs")
    print(f"    --full          Show complete insight text")
    print(f"    --schedule      Check EventBridge + task history\n")


if __name__ == "__main__":
    main()
