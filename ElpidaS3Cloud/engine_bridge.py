"""
Engine Bridge — Attach S3 Sync to native_cycle_engine.py
=========================================================

Two integration modes:

1. MONKEY-PATCH (non-invasive):
   Wraps the existing engine's _store_insight and _load_memory 
   without modifying native_cycle_engine.py at all.

2. S3-AWARE ENGINE (subclass):
   Extends NativeCycleEngine with S3 pull on init and push on store.

Usage:
    # Mode 1: Attach to existing engine (zero code changes)
    from native_cycle_engine import NativeCycleEngine
    from ElpidaS3Cloud import attach_s3_to_engine
    
    engine = NativeCycleEngine()
    attach_s3_to_engine(engine, sync_every=5)  # push every 5 cycles
    engine.run(num_cycles=100)  # S3 sync happens automatically
    
    # Mode 2: Use the S3-aware subclass
    from ElpidaS3Cloud import S3AwareEngine
    
    engine = S3AwareEngine()  # pulls from S3 on init
    engine.run(num_cycles=100)  # pushes to S3 automatically
"""

import sys
import json
import atexit
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional


def attach_s3_to_engine(engine, sync_every: int = 5, push_on_exit: bool = True):
    """
    Monkey-patch an existing NativeCycleEngine to sync with S3.
    
    This is the NON-INVASIVE approach — no changes to native_cycle_engine.py.
    
    Args:
        engine: A NativeCycleEngine instance (already initialized)
        sync_every: Push to S3 every N cycles (default: 5)
        push_on_exit: Register atexit handler for final push (default: True)
    """
    from .s3_memory_sync import S3MemorySync
    
    sync = S3MemorySync()
    
    # --- Pull latest from S3 on attach ---
    pull_result = sync.pull_if_newer()
    if pull_result["action"] == "downloaded":
        # Reload memory since we just downloaded a newer version
        engine.evolution_memory = engine._load_memory()
        print(f"   🔄 Engine memory reloaded: {len(engine.evolution_memory)} patterns")
    
    # --- Wrap _store_insight to push after every N cycles ---
    original_store = engine._store_insight
    _cycles_since_push = {"count": 0}
    
    def _store_insight_with_s3(insight):
        # Call original
        original_store(insight)
        
        # Track cycles since last push
        _cycles_since_push["count"] += 1
        
        if _cycles_since_push["count"] >= sync_every:
            try:
                sync.push_incremental()
                _cycles_since_push["count"] = 0
            except Exception as e:
                print(f"   ⚠️  S3 push failed (non-fatal): {e}")
    
    engine._store_insight = _store_insight_with_s3
    
    # --- Store sync reference on engine for manual access ---
    engine._s3_sync = sync
    
    # --- Register atexit for final push ---
    if push_on_exit:
        def _final_push():
            try:
                print("\n☁️  Final S3 push on exit...")
                sync.push()
            except Exception as e:
                print(f"   ⚠️  Final push failed: {e}")
        
        atexit.register(_final_push)
    
    print(f"☁️  S3 attached to engine (sync every {sync_every} cycles)")
    return sync


class S3AwareEngine:
    """
    Wrapper around NativeCycleEngine with built-in S3 support.
    
    Usage:
        engine = S3AwareEngine(sync_every=5)
        engine.run(num_cycles=100)
    """
    
    def __init__(self, sync_every: int = 5, **engine_kwargs):
        # Add project root to path if needed
        root = Path(__file__).resolve().parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        
        from native_cycle_engine import NativeCycleEngine
        from .s3_memory_sync import S3MemorySync
        
        self.sync = S3MemorySync()
        
        # Pull latest from S3 BEFORE engine init
        print("☁️  Pulling latest consciousness from S3...")
        self.sync.pull_if_newer()
        
        # Now initialize engine (which will load the pulled file)
        self.engine = NativeCycleEngine(**engine_kwargs)
        
        # Attach S3 sync
        attach_s3_to_engine(self.engine, sync_every=sync_every, push_on_exit=True)
        
        # Expose the sync on this wrapper too
        self._s3_sync = self.sync
    
    def run_cycle(self):
        """Run a single consciousness cycle."""
        return self.engine.run_cycle()
    
    def run(self, num_cycles: int = 10, duration_minutes: int = None):
        """Run the endless dance with S3 persistence."""
        return self.engine.run(num_cycles=num_cycles, duration_minutes=duration_minutes)
    
    def status(self):
        """Print S3 sync status."""
        self.sync.print_status()
    
    def push_now(self):
        """Force an immediate S3 push."""
        return self.sync.push()
    
    def __getattr__(self, name):
        """Delegate everything else to the underlying engine."""
        return getattr(self.engine, name)
