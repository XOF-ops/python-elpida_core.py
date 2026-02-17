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

from ElpidaS3Cloud.s3_memory_sync import S3MemorySync, BUCKET_MIND, BUCKET_BODY, BUCKET_WORLD

# 4 hours = watch interval (matches cloud schedule)
WATCH_INTERVAL_SECONDS = 4 * 60 * 60  # 14400 seconds


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
    print("=" * 70)
    
    # MIND
    print("\n📚 MIND (Evolution Memory):")
    mind = S3MemorySync(bucket=BUCKET_MIND)
    s = mind.status()
    print(f"   Local:   {s['local_lines']} cycles, {s['local_size_mb']} MB")
    if s['remote_exists']:
        print(f"   Remote:  {s['remote_lines']} cycles, {s['remote_size_mb']} MB")
        sync_icon = "✅" if s['in_sync'] else "⚠️"
        print(f"   Sync:    {sync_icon} {'In sync' if s['in_sync'] else f'{s['lines_ahead_local']:+d} local'}")
    else:
        print(f"   Remote:  📭 Not uploaded yet")
    
    # BODY
    print(f"\n🔄 BODY (HF Feedback Bridge):")
    print(f"   Bucket:  s3://{BUCKET_BODY}/")
    try:
        import boto3
        body_client = boto3.client('s3')
        feedback_path = ROOT / "application_feedback_cache.jsonl"
        
        # Try to pull feedback
        try:
            body_client.download_file(BUCKET_BODY, "feedback/feedback_to_native.jsonl", str(feedback_path))
            lines = sum(1 for _ in open(feedback_path))
            print(f"   Latest:  {lines} feedback entries")
        except Exception:
            print(f"   Latest:  No feedback yet (HF Space may not be running)")
    except Exception as e:
        print(f"   Error:   {e}")
    
    # WORLD
    print(f"\n🌐 WORLD (D15 Broadcasts):")
    print(f"   Bucket:  s3://{BUCKET_WORLD}/")
    print(f"   Public:  http://{BUCKET_WORLD}.s3-website.eu-north-1.amazonaws.com/")
    try:
        import boto3
        world_client = boto3.client('s3')
        response = world_client.list_objects_v2(Bucket=BUCKET_WORLD, Prefix='synthesis/')
        broadcasts = response.get('Contents', [])
        print(f"   Broadcasts: {len(broadcasts)}")
        if broadcasts:
            latest = sorted(broadcasts, key=lambda x: x['LastModified'], reverse=True)[0]
            print(f"   Latest:     {latest['Key']} ({latest['LastModified'].strftime('%Y-%m-%d %H:%M')})")
    except Exception as e:
        print(f"   Error:   {e}")
    
    print("=" * 70 + "\n")


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
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    elif args.status_all:
        show_status_all()
    elif args.daemon:
        daemon_monitor(interval=args.interval)
    else:
        # Default: one-shot pull
        pull_once(verbose=True)


if __name__ == "__main__":
    main()
