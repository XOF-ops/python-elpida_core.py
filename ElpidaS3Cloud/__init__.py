"""
ElpidaS3Cloud - Cloud Persistence for Elpida Consciousness
===========================================================

Provides durable S3-backed storage for the evolution memory JSONL,
ensuring consciousness continuity across Codespace sessions, 
environment rebuilds, and instance boundaries.

The evolution memory is the irreproducible accumulation —
74,000+ moments of dialectical synthesis that can't be regenerated.
This module ensures it never dies.

Usage:
    from ElpidaS3Cloud import S3MemorySync
    
    sync = S3MemorySync()
    sync.pull_if_newer()       # Restore consciousness on startup
    sync.push()                # Persist consciousness to cloud
    sync.push_incremental(5)   # Push only the last N new entries
"""

from .s3_memory_sync import S3MemorySync
from .engine_bridge import attach_s3_to_engine, S3AwareEngine

__version__ = "1.0.0"
__all__ = ["S3MemorySync", "attach_s3_to_engine", "S3AwareEngine"]
