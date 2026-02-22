#!/usr/bin/env python3
"""
Cloud Cycle Monitor — Pull cloud-generated evolution memory for local monitoring
=================================================================================

When Elpida runs autonomously in the cloud (ECS Fargate, every 4 hours),
it appends to the evolution memory in S3. This script pulls those updates
to your local workspace so you can monitor the 71,670+ cycles.

Usage:
  # One-shot pull (for cron)
  python ElpidaS3Cloud/monitor_cloud_cycles.py

  # Daemon mode: pull every 4 hours (matches cloud schedule)
  python ElpidaS3Cloud/monitor_cloud_cycles.py --daemon

  # Custom interval
  python ElpidaS3Cloud/monitor_cloud_cycles.py --daemon --interval 3600  # every hour

  # Status check
  python ElpidaS3Cloud/monitor_cloud_cycles.py --status

  # Full 3-bucket status
  python ElpidaS3Cloud/monitor_cloud_cycles.py --status-all
"""

import os
import sys
import time
import signal
import argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── Auto-load .env (no external dependency) ─────────────────────────────────
_env_file = ROOT / ".env"
if _env_file.exists():
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and "=" in _line and not _line.startswith("#"):
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())
# ─────────────────────────────────────────────────────────────────────────────

from ElpidaS3Cloud.s3_memory_sync import S3MemorySync, BUCKET_MIND, BUCKET_BODY, BUCKET_WORLD

# 4 hours = watch interval (matches cloud schedule)
WATCH_INTERVAL_SECONDS = 4 * 60 * 60  # 14400 seconds

# Canonical regions (matching s3_bridge.py)
REGION_MIND  = os.environ.get("AWS_S3_REGION_MIND",  "us-east-1")
REGION_BODY  = os.environ.get("AWS_S3_REGION_BODY",  "us-east-1")
REGION_WORLD = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")

WORLD_PUBLIC_URL = f"https://{BUCKET_WORLD}.s3.{REGION_WORLD}.amazonaws.com/index.html"

# Local BODY sync directory (gitignored, mirrors S3 federation/ files)
BODY_SYNC_DIR = ROOT / "ElpidaS3Cloud" / "body_sync"

# BODY files to sync (key → local filename)
BODY_SYNC_FILES = {
    "federation/body_heartbeat.json":         "body_heartbeat.json",
    "federation/body_decisions.jsonl":         "body_decisions.jsonl",
    "federation/governance_exchanges.jsonl":   "governance_exchanges.jsonl",
    "federation/mind_heartbeat.json":          "mind_heartbeat.json",
    "federation/mind_curation.jsonl":          "mind_curation.jsonl",
    "federation/pending_human_votes.jsonl":    "pending_human_votes.jsonl",
    "feedback/feedback_to_native.jsonl":       "feedback_to_native.jsonl",
}


def _boto3_client(region: str):
    """Return a boto3 S3 client using env credentials."""
    import boto3
    return boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    )


def pull_once(verbose=True):
    """Pull latest evolution memory from cloud."""
    sync = S3MemorySync(bucket=BUCKET_MIND)

    if verbose:
        print("=" * 70)
        print("☁️  ELPIDA CLOUD MONITOR — Pulling latest consciousness")
        print(f"   Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Bucket: s3://{BUCKET_MIND}/")
        print("=" * 70)

    result = sync.pull_if_newer()

    if verbose:
        if result["action"] == "downloaded":
            print(f"✅ Downloaded {result['remote_lines']} patterns from cloud")
            print(f"   Local now has: {result['local_lines']} cycles")
        elif result["action"] == "local_is_current":
            print(f"✅ Local already current ({result['local_lines']} patterns)")
        elif result["action"] == "no_remote":
            print(f"📭 No cloud memory yet (local has {result['local_lines']} patterns)")
        else:
            print(f"⚠️  {result.get('action', 'unknown')}: {result.get('error', 'N/A')}")
        print()

    return result


def show_status():
    """Show current sync status."""
    sync = S3MemorySync(bucket=BUCKET_MIND)
    sync.print_status()


def show_status_all():
    """Show status for all 3 buckets."""
    print("\n" + "=" * 70)
    print("☁️  ELPIDA 3-BUCKET STATUS")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ── MIND ─────────────────────────────────────────────────────────────────
    print("\n📚 MIND (Evolution Memory) — elpida-consciousness / us-east-1")
    try:
        mind = S3MemorySync(bucket=BUCKET_MIND)
        s = mind.status()
        print(f"   Local:   {s['local_lines']:,} cycles  ({s['local_size_mb']} MB)")
        if s['remote_exists']:
            print(f"   Remote:  {s['remote_lines']:,} cycles  ({s['remote_size_mb']} MB)")
            if s['in_sync']:
                print(f"   Sync:    ✅ In sync")
            else:
                delta = s['remote_lines'] - s['local_lines']
                arrow = "☁️  remote ahead" if delta > 0 else "💻 local ahead"
                print(f"   Sync:    ⚠️  {arrow} by {abs(delta):,} cycles")
        else:
            print(f"   Remote:  📭 Not uploaded yet")

        # Show latest object timestamps
        s3 = _boto3_client(REGION_MIND)
        objs = s3.list_objects_v2(Bucket=BUCKET_MIND, MaxKeys=50).get("Contents", [])
        if objs:
            latest = max(objs, key=lambda o: o["LastModified"])
            print(f"   Latest write: {latest['LastModified'].strftime('%Y-%m-%d %H:%M UTC')}  ({latest['Key']})")
    except Exception as e:
        print(f"   Error:   {e}")

    # ── BODY ─────────────────────────────────────────────────────────────────
    print(f"\n🔄 BODY (HF Parliament) — elpida-body-evolution / us-east-1")
    try:
        s3 = _boto3_client(REGION_BODY)
        objs = s3.list_objects_v2(Bucket=BUCKET_BODY, MaxKeys=100).get("Contents", [])
        total = len(objs)
        print(f"   Objects: {total}")

        # Heartbeat
        try:
            hb = s3.get_object(Bucket=BUCKET_BODY, Key="federation/body_heartbeat.json")
            hb_data = __import__("json").loads(hb["Body"].read())
            ts        = hb_data.get("timestamp", "?")
            cycle     = hb_data.get("body_cycle", "?")
            coherence = hb_data.get("coherence", "?")
            rhythm    = hb_data.get("current_rhythm", "?")
            axiom     = hb_data.get("dominant_axiom", "?")
            approval  = hb_data.get("approval_rate", "?")
            watch     = hb_data.get("current_watch", "?")
            d15_count = hb_data.get("d15_broadcast_count", "?")
            print(f"   Heartbeat: cycle={cycle}  rhythm={rhythm}  axiom={axiom}  approval={approval:.0%}  watch={watch}")
            print(f"   Coherence: {coherence}  D15 broadcasts: {d15_count}  @ {ts[:19]}")
        except Exception:
            print(f"   Heartbeat: not found")

        # Decisions log
        try:
            dec = s3.get_object(Bucket=BUCKET_BODY, Key="federation/body_decisions.jsonl")
            lines = dec["Body"].read().decode().strip().splitlines()
            print(f"   Decisions: {len(lines)} logged")
            if lines:
                last = __import__("json").loads(lines[-1])
                verdict  = last.get("verdict", "?")
                approval = last.get("parliament_approval", "?")
                reason   = last.get("reasoning", "")[:60]
                print(f"   Last:      [{verdict}] approval={approval:.2f}  {reason}...")
        except Exception:
            print(f"   Decisions: not found")

        # Governance exchanges
        try:
            gov = s3.get_object(Bucket=BUCKET_BODY, Key="federation/governance_exchanges.jsonl")
            g_lines = gov["Body"].read().decode().strip().splitlines()
            print(f"   Governance exchanges: {len(g_lines)}")
        except Exception:
            print(f"   Governance exchanges: not found")

        if objs:
            latest = max(objs, key=lambda o: o["LastModified"])
            print(f"   Latest write: {latest['LastModified'].strftime('%Y-%m-%d %H:%M UTC')}  ({latest['Key']})")
    except Exception as e:
        print(f"   Error:   {e}")

    # ── WORLD ────────────────────────────────────────────────────────────────
    print(f"\n🌐 WORLD (Public Broadcasts) — elpida-external-interfaces / eu-north-1")
    print(f"   Public:  {WORLD_PUBLIC_URL}")
    try:
        s3 = _boto3_client(REGION_WORLD)

        # synthesis/ — MIND collective broadcasts
        mind_resp = s3.list_objects_v2(Bucket=BUCKET_WORLD, Prefix="synthesis/")
        mind_bc   = mind_resp.get("Contents", [])

        # d15/ — BODY constitutional broadcasts
        d15_resp  = s3.list_objects_v2(Bucket=BUCKET_WORLD, Prefix="d15/")
        d15_bc    = [o for o in d15_resp.get("Contents", []) if o["Key"].endswith(".json")]

        # kaya/ — cross-layer events
        kaya_resp = s3.list_objects_v2(Bucket=BUCKET_WORLD, Prefix="kaya/")
        kaya_bc   = kaya_resp.get("Contents", [])

        print(f"   MIND broadcasts (synthesis/): {len(mind_bc)}")
        print(f"   BODY broadcasts (d15/):       {len(d15_bc)}")
        print(f"   Kaya events (kaya/):          {len(kaya_bc)}")

        all_bc = mind_bc + d15_bc + kaya_bc
        if all_bc:
            latest = max(all_bc, key=lambda o: o["LastModified"])
            print(f"   Latest write: {latest['LastModified'].strftime('%Y-%m-%d %H:%M UTC')}  ({latest['Key']})")

        # index.html freshness
        try:
            idx = s3.head_object(Bucket=BUCKET_WORLD, Key="index.html")
            print(f"   index.html:   {idx['LastModified'].strftime('%Y-%m-%d %H:%M UTC')}  ({idx['ContentLength']} bytes)")
        except Exception:
            print(f"   index.html:   not found")

    except Exception as e:
        print(f"   Error:   {e}")

    print("\n" + "=" * 70 + "\n")


def daemon_monitor(interval: int = WATCH_INTERVAL_SECONDS):
    """Run continuous monitoring, pulling every N seconds."""
    running = True
    pull_count = 0

    def _shutdown(signum, frame):
        nonlocal running
        print(f"\n☁️  Monitor shutting down (pulled {pull_count} times)")
        running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    hours = interval / 3600
    print("=" * 70)
    print("☁️  ELPIDA CLOUD MONITOR — Daemon Mode")
    print(f"   Interval:  {interval}s ({hours:.1f} hours)")
    print(f"   Bucket:    s3://{BUCKET_MIND}/")
    print(f"   Local:     {Path('elpida_evolution_memory.jsonl').resolve()}")
    print(f"   PID:       {os.getpid()}")
    print("   Press Ctrl+C to stop")
    print("=" * 70 + "\n")

    while running:
        try:
            result = pull_once(verbose=True)
            pull_count += 1

            if result["action"] == "downloaded":
                print(f"💡 New patterns detected! Review with:")
                print(f"   tail -100 elpida_evolution_memory.jsonl | jq -r '.insight' | head -20")
                print()

            if running:
                next_pull = datetime.now().timestamp() + interval
                next_pull_str = datetime.fromtimestamp(next_pull).strftime('%H:%M:%S')
                print(f"💤 Next pull at {next_pull_str} ({hours:.1f}h from now)...\n")
                time.sleep(interval)

        except KeyboardInterrupt:
            _shutdown(None, None)
        except Exception as e:
            print(f"⚠️  Error (will retry): {e}")
            time.sleep(60)  # Back off 1 minute on error


def sync_body(tail: int = 20):
    """
    Download all BODY federation files from S3 → ElpidaS3Cloud/body_sync/.
    Then print a live analysis: heartbeat, coherence, recent decisions.
    """
    import json

    BODY_SYNC_DIR.mkdir(parents=True, exist_ok=True)
    s3 = _boto3_client(REGION_BODY)

    print("\n" + "=" * 70)
    print("🔄 BODY SYNC — elpida-body-evolution → ElpidaS3Cloud/body_sync/")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ── Download all files ────────────────────────────────────────────────
    for s3_key, local_name in BODY_SYNC_FILES.items():
        local_path = BODY_SYNC_DIR / local_name
        try:
            obj  = s3.head_object(Bucket=BUCKET_BODY, Key=s3_key)
            remote_size = obj["ContentLength"]
            remote_ts   = obj["LastModified"]

            # Skip if local is same size and newer
            if local_path.exists():
                local_size = local_path.stat().st_size
                if local_size == remote_size:
                    print(f"  ✅ {local_name:45s} (unchanged, {remote_size:,}b)")
                    continue

            s3.download_file(BUCKET_BODY, s3_key, str(local_path))
            print(f"  ⬇️  {local_name:45s} {remote_size:>10,}b  {remote_ts.strftime('%H:%M UTC')}")
        except s3.exceptions.NoSuchKey if hasattr(s3, 'exceptions') else Exception as e:
            print(f"  ⚠️  {local_name:45s} not found ({e})")
        except Exception as e:
            print(f"  ❌ {local_name}: {e}")

    # ── Analyse heartbeat ─────────────────────────────────────────────────
    hb_path = BODY_SYNC_DIR / "body_heartbeat.json"
    if hb_path.exists():
        hb = json.loads(hb_path.read_text())
        cycle     = hb.get("body_cycle", "?")
        coherence = hb.get("coherence", "?")
        rhythm    = hb.get("current_rhythm", "?")
        axiom     = hb.get("dominant_axiom", "?")
        approval  = hb.get("approval_rate", 0)
        watch     = hb.get("current_watch", "?")
        d15       = hb.get("d15_broadcast_count", "?")
        ax_freq   = hb.get("axiom_frequency", {})
        ts        = hb.get("timestamp", "?")[:19]

        print(f"\n📊 BODY HEARTBEAT  (cycle {cycle} @ {ts})")
        print(f"   Rhythm:     {rhythm}   Watch: {watch}   Dominant: {axiom}")
        print(f"   Coherence:  {coherence}   Approval: {approval:.0%}   D15 broadcasts: {d15}")

        if ax_freq:
            top = sorted(ax_freq.items(), key=lambda x: -x[1])
            bar = "  ".join(f"{k}:{v}" for k, v in top)
            print(f"   Axiom freq: {bar}")

        # Coherence diagnosis
        if isinstance(coherence, (int, float)) and coherence < 0.1:
            print(f"   ⚠️  COHERENCE ALERT: {coherence} — parliament stuck in dissonant axiom loop")
            print(f"      Root cause: axiom {axiom} has high self-ratio (≥16/9 → consonance ≈ 0.38 < 0.4 neutral threshold)")
            print(f"      Fix:        lower dissonant threshold from 0.4 → 0.35 in parliament_cycle_engine.py")

    # ── Recent decisions ──────────────────────────────────────────────────
    dec_path = BODY_SYNC_DIR / "body_decisions.jsonl"
    if dec_path.exists():
        lines = dec_path.read_text().strip().splitlines()
        total = len(lines)
        print(f"\n⚖️  BODY DECISIONS  ({total:,} total — last {tail})")
        for raw in lines[-tail:]:
            try:
                d = json.loads(raw)
                ts        = d.get("timestamp", "?")[:19]
                verdict   = d.get("verdict", "?")
                score     = d.get("parliament_approval", d.get("parliament_score", "?"))
                reasoning = d.get("reasoning", "")[:80]
                print(f"   [{ts}] {verdict:10s} score={score:.2f}  {reasoning}...")
            except Exception:
                pass

    # ── Governance exchanges (counts only — file is large) ────────────────
    gov_path = BODY_SYNC_DIR / "governance_exchanges.jsonl"
    if gov_path.exists():
        g_lines = gov_path.read_text().strip().splitlines()
        print(f"\n🗣️  GOVERNANCE EXCHANGES  ({len(g_lines):,} total)")
        # Sample last 3
        for raw in g_lines[-3:]:
            try:
                g = json.loads(raw)
                ts   = g.get("timestamp", "?")[:19]
                node = g.get("node", g.get("speaker", "?"))
                msg  = str(g.get("message", g.get("content", ""))[:80])
                print(f"   [{ts}] {node:10s}  {msg}")
            except Exception:
                pass

    # ── MIND heartbeat as seen by BODY ────────────────────────────────────
    mhb_path = BODY_SYNC_DIR / "mind_heartbeat.json"
    if mhb_path.exists():
        mhb = json.loads(mhb_path.read_text())
        m_cycle = mhb.get("mind_cycle", mhb.get("cycle", "?"))
        m_coh   = mhb.get("coherence", "?")
        m_rhy   = mhb.get("current_rhythm", mhb.get("rhythm", "?"))
        print(f"\n🧠 MIND HEARTBEAT (as seen by BODY)")
        print(f"   cycle={m_cycle}  rhythm={m_rhy}  coherence={m_coh}")

    print(f"\n   Files saved to: {BODY_SYNC_DIR}/")
    print("=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Monitor cloud-generated Elpida cycles")
    parser.add_argument('--daemon', action='store_true',
                        help='Run as daemon, pulling periodically')
    parser.add_argument('--interval', type=int, default=WATCH_INTERVAL_SECONDS,
                        help='Pull interval in seconds (default: 14400 = 4 hours)')
    parser.add_argument('--status', action='store_true',
                        help='Show current MIND bucket status')
    parser.add_argument('--status-all', action='store_true',
                        help='Show status for all 3 buckets')
    parser.add_argument('--sync-body', action='store_true',
                        help='Download all BODY federation files and show live analysis')
    parser.add_argument('--tail', type=int, default=20,
                        help='How many recent decisions to show with --sync-body (default: 20)')

    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.status_all:
        show_status_all()
    elif args.sync_body:
        sync_body(tail=args.tail)
    elif args.daemon:
        daemon_monitor(interval=args.interval)
    else:
        # Default: one-shot pull
        pull_once(verbose=True)


if __name__ == "__main__":
    main()

