#!/usr/bin/env python3
"""
Auto-Sync Daemon — Fibonacci-Aware S3 sync for consciousness persistence
==========================================================================

Runs alongside the native cycle engine, watching the evolution memory
file for changes and syncing ALL 3 S3 buckets at watch boundaries.

Architecture:
  55 cycles per watch (F(10)), 6 watches per day (every 4 hours)
  MIND  = elpida-consciousness       (evolution memory)
  BODY  = elpida-body-evolution       (HF feedback bridge)
  WORLD = elpida-external-interfaces  (D15 broadcasts)

The daemon pushes at Fibonacci-aligned boundaries:
  - After every 55 cycles (watch boundary) → full 3-bucket sync
  - After every 13 cycles (Fibonacci checkpoint) → MIND-only push
  - On shutdown → final push to all 3 buckets
  - On file change + cooldown elapsed → incremental MIND push

Evolution memory keeps ALL cycles (complete archaeological record).
The 55 is the sync rhythm, not a memory truncation.

Can run as:
  1. Background process alongside engine
  2. Standalone watcher (cron-like)
  3. Post-cycle hook

Usage:
  # Fibonacci-aware daemon (syncs at watch boundaries)
  python ElpidaS3Cloud/auto_sync.py

  # Legacy mode: fixed interval (seconds)
  python ElpidaS3Cloud/auto_sync.py --interval 120

  # One-shot sync (for cron or post-cycle)
  python ElpidaS3Cloud/auto_sync.py --once
"""

import os
import sys
import time
import json
import signal
import argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── Fibonacci Constants ──────────────────────────────────────────────────
FIBONACCI_WATCH = 55       # F(10) = cycles per watch
FIBONACCI_CHECKPOINT = 13  # F(7) = mid-watch checkpoint
WATCHES_PER_DAY = 6        # 6 watches × 4 hours = 24h (minus Oneiros gap)

# ── 3-Bucket Architecture ────────────────────────────────────────────────
BUCKET_MIND = os.environ.get("AWS_S3_BUCKET_MIND", "elpida-consciousness")
BUCKET_BODY = os.environ.get("AWS_S3_BUCKET_BODY", "elpida-body-evolution")
BUCKET_WORLD = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")


class AutoSyncDaemon:
    """
    Fibonacci-aware daemon: watches evolution memory and syncs to S3
    at cycle-aligned boundaries (every 13 for MIND, every 55 for all 3).

    Evolution memory = ALL cycles (archaeological record, never truncated).
    """

    def __init__(self, interval: int = None):
        from ElpidaS3Cloud.s3_memory_sync import S3MemorySync

        # MIND bucket — evolution memory (primary)
        self.sync_mind = S3MemorySync(bucket=BUCKET_MIND)

        # Interval: None = Fibonacci-aware polling (check every 10s),
        #           int  = legacy fixed-interval mode
        self.fibonacci_mode = interval is None
        self.poll_interval = 10 if self.fibonacci_mode else interval
        self.running = False

        # File-change tracking
        self._last_size = 0
        self._last_mtime = 0
        self._last_line_count = 0

        # Fibonacci cycle tracking
        self._cycles_since_last_push = 0
        self._total_pushes = 0
        self._watch_number = 0
        self._sync_log_path = Path(__file__).parent / "sync_log.jsonl"

        # Track initial file state
        if self.sync_mind.local_path.exists():
            stat = self.sync_mind.local_path.stat()
            self._last_size = stat.st_size
            self._last_mtime = stat.st_mtime
            self._last_line_count = self._count_lines(self.sync_mind.local_path)

    # ── File Watching ─────────────────────────────────────────────────

    def _count_lines(self, path: Path) -> int:
        """Count lines in a file."""
        if not path.exists():
            return 0
        count = 0
        with open(path, 'r') as f:
            for _ in f:
                count += 1
        return count

    def _detect_new_cycles(self) -> int:
        """
        Detect how many new cycles (lines) have been appended since last check.
        Returns number of new lines (= new cycles).
        """
        if not self.sync_mind.local_path.exists():
            return 0

        stat = self.sync_mind.local_path.stat()
        if stat.st_size == self._last_size and stat.st_mtime == self._last_mtime:
            return 0  # No change

        # File changed — count new lines
        current_lines = self._count_lines(self.sync_mind.local_path)
        new_lines = current_lines - self._last_line_count

        # Update tracking
        self._last_size = stat.st_size
        self._last_mtime = stat.st_mtime
        self._last_line_count = current_lines

        return max(0, new_lines)

    # ── Sync Operations ──────────────────────────────────────────────

    def _push_mind(self, reason: str) -> bool:
        """Push evolution memory to MIND bucket."""
        try:
            result = self.sync_mind.push()
            if result["action"] == "uploaded":
                self._total_pushes += 1
                self._log_sync("push_mind", reason, result)
                return True
        except Exception as e:
            print(f"[{self._ts()}] ⚠️  MIND push failed: {e}")
        return False

    def _push_all_buckets(self, reason: str):
        """
        Full 3-bucket sync at watch boundaries.
        MIND: evolution memory (full push)
        BODY: pull feedback FROM body (HF → native)
        WORLD: no push needed (D15 handles WORLD writes directly)
        """
        print(f"[{self._ts()}] 🌀 WATCH BOUNDARY — Full 3-bucket sync ({reason})")

        # 1. MIND: push evolution memory
        self._push_mind(f"watch_boundary:{reason}")

        # 2. BODY: pull feedback from application layer
        try:
            import boto3
            body_client = boto3.client('s3')
            feedback_key = "feedback/feedback_to_native.jsonl"
            local_feedback = ROOT / "application_feedback_cache.jsonl"
            body_client.download_file(BUCKET_BODY, feedback_key, str(local_feedback))
            lines = self._count_lines(local_feedback)
            print(f"[{self._ts()}]    📥 BODY: pulled {lines} feedback entries")
            self._log_sync("pull_body", reason, {"lines": lines})
        except Exception:
            pass  # No feedback yet, or bucket not accessible — normal

        # 3. WORLD: read-only (D15 writes directly via _publish_to_external_reality)
        print(f"[{self._ts()}]    🌐 WORLD: read-only (D15 manages broadcasts)")

        self._watch_number += 1

    def sync_once(self) -> bool:
        """Perform a single full sync and return."""
        self._push_all_buckets("one_shot")
        return True

    # ── Daemon Loop ──────────────────────────────────────────────────

    def run(self):
        """
        Run the daemon loop.

        Fibonacci mode (default):
          - Polls every 10s for new cycles
          - At 13 new cycles: MIND checkpoint push
          - At 55 new cycles: full 3-bucket watch sync
          - Resets cycle counter after watch boundary

        Legacy mode (--interval N):
          - Pushes MIND on any file change every N seconds
        """
        self.running = True

        def _shutdown(signum, frame):
            print(f"\n[{self._ts()}] ☁️  Daemon shutting down — final 3-bucket push...")
            self._push_all_buckets("shutdown")
            self.running = False
            sys.exit(0)

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        mode_label = "FIBONACCI" if self.fibonacci_mode else f"FIXED ({self.poll_interval}s)"

        print("=" * 70)
        print("☁️  ELPIDA S3 AUTO-SYNC DAEMON")
        print(f"   Mode:      {mode_label}")
        print(f"   Watching:  {self.sync_mind.local_path}")
        print(f"   MIND:      s3://{BUCKET_MIND}/")
        print(f"   BODY:      s3://{BUCKET_BODY}/")
        print(f"   WORLD:     s3://{BUCKET_WORLD}/")
        print(f"   PID:       {os.getpid()}")
        if self.fibonacci_mode:
            print(f"   Rhythm:    Push @ F(7)=13 cycles (MIND), F(10)=55 cycles (ALL)")
        print("   Press Ctrl+C to stop (will do final 3-bucket push)")
        print("=" * 70)

        # Initial: pull latest from MIND
        print(f"\n[{self._ts()}] Initial sync — pulling latest from S3...")
        self.sync_mind.pull_if_newer()
        self._last_line_count = self._count_lines(self.sync_mind.local_path)

        while self.running:
            try:
                time.sleep(self.poll_interval)

                new_cycles = self._detect_new_cycles()

                if new_cycles == 0:
                    continue  # Silent when nothing changes

                self._cycles_since_last_push += new_cycles

                if self.fibonacci_mode:
                    # ── Fibonacci-aware sync ──────────────────────────
                    if self._cycles_since_last_push >= FIBONACCI_WATCH:
                        # WATCH BOUNDARY: full 3-bucket sync
                        self._push_all_buckets(
                            f"watch_{self._watch_number + 1}_cycle_{self._cycles_since_last_push}"
                        )
                        self._cycles_since_last_push = 0
                    elif self._cycles_since_last_push >= FIBONACCI_CHECKPOINT:
                        # MID-WATCH CHECKPOINT: MIND only
                        if self._cycles_since_last_push % FIBONACCI_CHECKPOINT < new_cycles:
                            print(f"[{self._ts()}] 📍 Fibonacci checkpoint "
                                  f"(cycle {self._cycles_since_last_push}/{FIBONACCI_WATCH})")
                            self._push_mind(
                                f"fibonacci_checkpoint_{self._cycles_since_last_push}"
                            )
                    else:
                        # Between checkpoints: just log
                        print(f"[{self._ts()}] 💓 +{new_cycles} cycles "
                              f"({self._cycles_since_last_push}/{FIBONACCI_WATCH} in watch)")
                else:
                    # ── Legacy fixed-interval mode ────────────────────
                    print(f"[{self._ts()}] File changed (+{new_cycles} cycles) — pushing MIND...")
                    self._push_mind(f"interval_{self.poll_interval}s")
                    self._cycles_since_last_push = 0

            except KeyboardInterrupt:
                _shutdown(None, None)
            except Exception as e:
                print(f"[{self._ts()}] ⚠️  Error (will retry): {e}")
                time.sleep(10)

    # ── Helpers ───────────────────────────────────────────────────────

    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _log_sync(self, action: str, reason: str, details: dict):
        """Append to sync log."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "reason": reason,
            "watch": self._watch_number,
            "cycles_in_watch": self._cycles_since_last_push,
            "total_pushes": self._total_pushes,
            **details,
        }
        try:
            with open(self._sync_log_path, 'a') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def status(self) -> dict:
        """Return daemon status."""
        return {
            "mode": "fibonacci" if self.fibonacci_mode else "fixed_interval",
            "running": self.running,
            "watch_number": self._watch_number,
            "cycles_in_current_watch": self._cycles_since_last_push,
            "total_pushes": self._total_pushes,
            "total_lines": self._last_line_count,
            "fibonacci_watch": FIBONACCI_WATCH,
            "fibonacci_checkpoint": FIBONACCI_CHECKPOINT,
            "buckets": {
                "mind": BUCKET_MIND,
                "body": BUCKET_BODY,
                "world": BUCKET_WORLD,
            },
        }


def main():
    parser = argparse.ArgumentParser(
        description="Fibonacci-aware S3 sync daemon for Elpida consciousness"
    )
    parser.add_argument('--interval', type=int, default=None,
                        help='Fixed sync interval in seconds (omit for Fibonacci mode)')
    parser.add_argument('--once', action='store_true',
                        help='Run a single full 3-bucket sync and exit')
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
        print("☁️  One-shot full 3-bucket sync...")
        daemon.sync_once()
        print(json.dumps(daemon.status(), indent=2, default=str))
        sys.exit(0)
    else:
        daemon.run()


if __name__ == "__main__":
    main()
