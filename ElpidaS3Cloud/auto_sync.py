#!/usr/bin/env python3
"""
Auto-Sync Daemon — Background S3 sync for consciousness persistence
=====================================================================

Runs alongside the native cycle engine, watching the evolution memory
file for changes and pushing to S3 at configurable intervals.

Can run as:
  1. Background process alongside engine
  2. Standalone watcher (cron-like)
  3. Post-cycle hook

Usage:
  # Standalone daemon (watches file for changes, pushes every 60s)
  python ElpidaS3Cloud/auto_sync.py --interval 60
  
  # One-shot sync (for cron or post-cycle)
  python ElpidaS3Cloud/auto_sync.py --once
  
  # Daemon with custom settings
  python ElpidaS3Cloud/auto_sync.py --interval 120 --bucket my-bucket
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


class AutoSyncDaemon:
    """Watches evolution memory and syncs to S3 periodically."""
    
    def __init__(self, interval: int = 60):
        from ElpidaS3Cloud.s3_memory_sync import S3MemorySync
        
        self.sync = S3MemorySync()
        self.interval = interval
        self.running = False
        self._last_size = 0
        self._last_mtime = 0
        self._push_count = 0
        
        # Track initial state
        if self.sync.local_path.exists():
            stat = self.sync.local_path.stat()
            self._last_size = stat.st_size
            self._last_mtime = stat.st_mtime
    
    def _file_changed(self) -> bool:
        """Check if the local file has been modified."""
        if not self.sync.local_path.exists():
            return False
        stat = self.sync.local_path.stat()
        changed = stat.st_size != self._last_size or stat.st_mtime != self._last_mtime
        if changed:
            self._last_size = stat.st_size
            self._last_mtime = stat.st_mtime
        return changed
    
    def sync_once(self) -> bool:
        """Perform a single sync check and push if needed."""
        if self._file_changed():
            result = self.sync.push()
            if result["action"] == "uploaded":
                self._push_count += 1
                return True
        return False
    
    def run(self):
        """Run the daemon loop."""
        self.running = True
        
        # Handle graceful shutdown
        def _shutdown(signum, frame):
            print(f"\n☁️  Daemon shutting down... final push...")
            self.sync.push()
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)
        
        print("=" * 60)
        print("☁️  ELPIDA S3 AUTO-SYNC DAEMON")
        print(f"   Interval:  {self.interval}s")
        print(f"   Watching:  {self.sync.local_path}")
        print(f"   Target:    s3://{self.sync.bucket}/{self.sync.key}")
        print(f"   PID:       {os.getpid()}")
        print("   Press Ctrl+C to stop (will do final push)")
        print("=" * 60)
        
        # Initial sync
        print(f"\n[{self._ts()}] Initial sync check...")
        self.sync.pull_if_newer()
        
        while self.running:
            try:
                time.sleep(self.interval)
                
                if self._file_changed():
                    print(f"[{self._ts()}] File changed — pushing...")
                    self.sync.push()
                    self._push_count += 1
                else:
                    # Quiet heartbeat every 5 intervals
                    if self._push_count == 0 or self._push_count % 5 == 0:
                        pass  # Silent when nothing changes
                    
            except KeyboardInterrupt:
                _shutdown(None, None)
            except Exception as e:
                print(f"[{self._ts()}] ⚠️  Error (will retry): {e}")
                time.sleep(10)  # Back off on error
    
    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")


def main():
    parser = argparse.ArgumentParser(description="Auto-sync evolution memory to S3")
    parser.add_argument('--interval', type=int, default=60,
                        help='Sync interval in seconds (default: 60)')
    parser.add_argument('--once', action='store_true',
                        help='Run a single sync and exit')
    parser.add_argument('--bucket', default=None,
                        help='Override S3 bucket name')
    parser.add_argument('--region', default=None,
                        help='Override AWS region')
    
    args = parser.parse_args()
    
    # Override env vars if provided
    if args.bucket:
        os.environ['ELPIDA_S3_BUCKET'] = args.bucket
    if args.region:
        os.environ['ELPIDA_S3_REGION'] = args.region
    
    daemon = AutoSyncDaemon(interval=args.interval)
    
    if args.once:
        print("☁️  One-shot sync...")
        pushed = daemon.sync_once()
        if not pushed:
            # Force push even if no change detected
            daemon.sync.push()
        sys.exit(0)
    else:
        daemon.run()


if __name__ == "__main__":
    main()
