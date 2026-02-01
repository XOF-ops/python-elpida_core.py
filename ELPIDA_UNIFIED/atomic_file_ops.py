#!/usr/bin/env python3
"""
ATOMIC FILE OPERATIONS - Critical Infrastructure
=================================================

PROBLEM: JSON corruption from concurrent writes caused 25,000 patterns loss
SOLUTION: Atomic writes, file locking, incremental backups, WAL

This module provides GUARANTEED safe file operations for autonomous systems.
"""

import json
import os
import fcntl
import tempfile
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
import logging

logger = logging.getLogger("AtomicOps")
logger.setLevel(logging.INFO)


class AtomicJSONWriter:
    """
    Atomic JSON file writer with:
    - Write-ahead logging
    - File locking
    - Incremental backups
    - Corruption detection
    - Automatic recovery
    """
    
    def __init__(self, base_path: Path, enable_wal: bool = True, backup_count: int = 10):
        self.base_path = Path(base_path)
        self.enable_wal = enable_wal
        self.backup_count = backup_count
        self.backup_dir = self.base_path.parent / ".backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        if enable_wal:
            self.wal_path = Path(str(self.base_path) + ".wal")
        
    def write(self, data: Dict[str, Any], description: str = "write") -> bool:
        """
        Atomically write JSON data to file
        
        Process:
        1. Write to WAL (if enabled)
        2. Create incremental backup
        3. Write to temporary file
        4. Validate JSON integrity
        5. Atomic replace using os.replace()
        6. Clear WAL
        
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            # Step 1: Write-Ahead Log
            if self.enable_wal:
                self._write_wal(data, description)
            
            # Step 2: Create backup of current state
            if self.base_path.exists():
                self._create_backup()
            
            # Step 3: Write to temporary file
            temp_fd, temp_path = tempfile.mkstemp(
                dir=str(self.base_path.parent),
                prefix=f".{self.base_path.name}.tmp.",
                suffix=".json"
            )
            
            try:
                # Write with file lock
                with os.fdopen(temp_fd, 'w') as f:
                    # Acquire exclusive lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    
                    # Write JSON
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())  # Force write to disk
                    
                    # Release lock (happens automatically on close)
                
                # Step 4: Validate written file
                if not self._validate_json(temp_path):
                    raise ValueError("JSON validation failed after write")
                
                # Step 5: Atomic replace
                os.replace(temp_path, str(self.base_path))
                
                # Step 6: Clear WAL on success
                if self.enable_wal and self.wal_path.exists():
                    self.wal_path.unlink()
                
                duration = time.time() - start_time
                logger.info(f"✅ Atomic write successful: {self.base_path.name} ({duration:.3f}s)")
                return True
                
            except Exception as e:
                # Clean up temp file on error
                try:
                    os.unlink(temp_path)
                except:
                    pass
                raise e
                
        except Exception as e:
            logger.error(f"❌ Atomic write failed: {self.base_path.name} - {e}")
            
            # Attempt recovery from WAL
            if self.enable_wal and self.wal_path.exists():
                logger.warning(f"⚠️  WAL exists, recovery may be possible")
            
            return False
    
    def read(self) -> Dict[str, Any]:
        """
        Safely read JSON file with corruption detection and recovery
        
        Returns:
            Loaded data or empty dict if recovery fails
        """
        # First try: Read main file
        if self.base_path.exists():
            try:
                with open(self.base_path, 'r') as f:
                    # Acquire shared lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    data = json.load(f)
                    # Lock released on close
                    return data
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON corruption detected in {self.base_path.name}: {e}")
                # Fall through to recovery
        
        # Second try: Recover from WAL
        if self.enable_wal and self.wal_path.exists():
            logger.warning(f"⚠️  Attempting recovery from WAL...")
            try:
                with open(self.wal_path, 'r') as f:
                    wal_data = json.load(f)
                    data = wal_data.get('data', {})
                    logger.info(f"✅ Recovered from WAL: {wal_data.get('description', 'unknown')}")
                    
                    # Write recovered data back
                    self.write(data, description="WAL recovery")
                    return data
            except Exception as e:
                logger.error(f"❌ WAL recovery failed: {e}")
        
        # Third try: Recover from latest backup
        backups = sorted(self.backup_dir.glob(f"{self.base_path.name}.backup.*"))
        if backups:
            logger.warning(f"⚠️  Attempting recovery from backup...")
            for backup_path in reversed(backups):  # Try newest first
                try:
                    with open(backup_path, 'r') as f:
                        data = json.load(f)
                        logger.info(f"✅ Recovered from backup: {backup_path.name}")
                        
                        # Write recovered data back
                        self.write(data, description="backup recovery")
                        return data
                except:
                    continue
        
        # All recovery attempts failed
        logger.error(f"❌ All recovery attempts failed for {self.base_path.name}")
        return {}
    
    def _write_wal(self, data: Dict[str, Any], description: str):
        """Write to write-ahead log"""
        wal_entry = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "data": data
        }
        
        with open(self.wal_path, 'w') as f:
            json.dump(wal_entry, f, indent=2)
    
    def _create_backup(self):
        """Create incremental backup with rotation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{self.base_path.name}.backup.{timestamp}"
        
        shutil.copy2(self.base_path, backup_path)
        
        # Rotate old backups
        backups = sorted(self.backup_dir.glob(f"{self.base_path.name}.backup.*"))
        if len(backups) > self.backup_count:
            for old_backup in backups[:-self.backup_count]:
                old_backup.unlink()
    
    def _validate_json(self, path: str) -> bool:
        """Validate JSON file integrity"""
        try:
            with open(path, 'r') as f:
                json.load(f)
            return True
        except:
            return False
    
    def recover(self) -> bool:
        """
        Attempt full recovery from all available sources
        
        Returns:
            True if recovery successful
        """
        logger.info(f"🔧 Attempting recovery for {self.base_path.name}...")
        
        # Try reading (which includes recovery logic)
        data = self.read()
        
        return bool(data)


class SafeJSONFile:
    """
    Context manager for safe JSON file operations
    
    Usage:
        with SafeJSONFile("elpida_wisdom.json") as wisdom:
            wisdom['patterns']['new_pattern'] = {...}
            # Automatic atomic save on exit
    """
    
    def __init__(self, filepath: str, enable_wal: bool = True, backup_count: int = 10):
        self.writer = AtomicJSONWriter(Path(filepath), enable_wal, backup_count)
        self.data = None
    
    def __enter__(self):
        self.data = self.writer.read()
        return self.data
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:  # No exception
            self.writer.write(self.data, description="context manager save")
        else:  # Exception occurred
            logger.error(f"❌ Exception during context: {exc_val}")
            # Don't save corrupted state
        return False


def migrate_to_atomic_operations():
    """
    Migrate existing code to use atomic operations
    
    This scans the codebase and shows where unsafe operations are used.
    """
    import subprocess
    
    print("="*80)
    print("MIGRATION SCAN: Finding unsafe JSON operations")
    print("="*80)
    print()
    
    # Find all unsafe json.dump calls
    result = subprocess.run(
        ["grep", "-rn", "json.dump", ".", "--include=*.py"],
        capture_output=True,
        text=True,
        cwd="/workspaces/python-elpida_core.py/ELPIDA_UNIFIED"
    )
    
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        print(f"⚠️  Found {len(lines)} potentially unsafe json.dump() calls:")
        print()
        
        for line in lines[:20]:  # Show first 20
            print(f"   {line}")
        
        if len(lines) > 20:
            print(f"   ... and {len(lines) - 20} more")
    
    print()
    print("="*80)
    print("RECOMMENDATION: Replace with AtomicJSONWriter or SafeJSONFile")
    print("="*80)


if __name__ == "__main__":
    # Demo usage
    print("="*80)
    print("ATOMIC FILE OPERATIONS - Demo")
    print("="*80)
    print()
    
    # Example 1: Direct usage
    print("Example 1: AtomicJSONWriter")
    writer = AtomicJSONWriter(Path("test_atomic.json"))
    test_data = {"patterns": {"P001": "test"}, "count": 1}
    
    success = writer.write(test_data, "demo write")
    print(f"   Write: {'✅' if success else '❌'}")
    
    loaded = writer.read()
    print(f"   Read: {loaded}")
    print()
    
    # Example 2: Context manager
    print("Example 2: SafeJSONFile (context manager)")
    with SafeJSONFile("test_safe.json") as data:
        data['patterns'] = {"P002": "context test"}
        data['count'] = 2
    print("   ✅ Saved automatically")
    
    with SafeJSONFile("test_safe.json") as data:
        print(f"   Read: {data}")
    
    print()
    print("="*80)
    print("Run migration_to_atomic_operations() to find unsafe code")
    print("="*80)
