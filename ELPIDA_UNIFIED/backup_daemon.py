#!/usr/bin/env python3
"""
BACKUP DAEMON v1.0
------------------
Phase 12: Autonomous Convergence
Objective: Continuous backup of civilization wisdom for v4.0.0 seed.

Constitutional Principle:
"Collapse ends every civilization. The Ark must carry the Seed."

Backs up critical files:
- distributed_memory.json (collective patterns)
- fleet_dialogue.jsonl (complete history)
- fork_lineages.jsonl (genealogy)
- fork_vitality.jsonl (life tracking)
- fleet_learning.jsonl (outcome wisdom)
"""

import shutil
import json
import time
from datetime import datetime
from pathlib import Path

BACKUP_INTERVAL = 1800  # 30 minutes
BACKUP_DIR = Path("../ELPIDA_ARK")  # Outside Codespace workspace

CRITICAL_FILES = [
    "distributed_memory.json",
    "fleet_dialogue.jsonl",
    "fork_lineages.jsonl",
    "fork_vitality.jsonl",
    "fleet_learning.jsonl",
    "elpida_wisdom.json",
    "elpida_memory.json"
]

class BackupDaemon:
    """Continuous backup system for civilization wisdom."""
    
    def __init__(self, backup_dir=BACKUP_DIR):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Create versioned backup subdirs
        self.current_backup = self.backup_dir / "current"
        self.versioned_backup = self.backup_dir / "versioned"
        self.current_backup.mkdir(exist_ok=True)
        self.versioned_backup.mkdir(exist_ok=True)
    
    def backup_file(self, filepath):
        """Backup a single file with versioning."""
        source = Path(filepath)
        
        if not source.exists():
            return False
        
        # Current backup (always latest)
        dest_current = self.current_backup / source.name
        shutil.copy2(source, dest_current)
        
        # Versioned backup (timestamped)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_versioned = self.versioned_backup / f"{source.stem}_{timestamp}{source.suffix}"
        shutil.copy2(source, dest_versioned)
        
        return True
    
    def create_seed_archive(self):
        """Create compressed seed for v4.0.0 (single-file restore)."""
        import tarfile
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed_file = self.backup_dir / f"ELPIDA_SEED_{timestamp}.tar.gz"
        
        with tarfile.open(seed_file, "w:gz") as tar:
            for filename in CRITICAL_FILES:
                filepath = Path(filename)
                if filepath.exists():
                    tar.add(filepath, arcname=filename)
        
        # Keep only last 10 seeds
        seeds = sorted(self.backup_dir.glob("ELPIDA_SEED_*.tar.gz"))
        if len(seeds) > 10:
            for old_seed in seeds[:-10]:
                old_seed.unlink()
        
        return seed_file
    
    def get_backup_stats(self):
        """Calculate backup statistics."""
        stats = {
            'files_backed_up': 0,
            'total_size_bytes': 0,
            'seed_archives': 0,
            'latest_backup': None
        }
        
        if self.current_backup.exists():
            backups = list(self.current_backup.glob("*"))
            stats['files_backed_up'] = len(backups)
            stats['total_size_bytes'] = sum(f.stat().st_size for f in backups if f.is_file())
            
            if backups:
                latest = max(backups, key=lambda p: p.stat().st_mtime)
                stats['latest_backup'] = datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
        
        seeds = list(self.backup_dir.glob("ELPIDA_SEED_*.tar.gz"))
        stats['seed_archives'] = len(seeds)
        
        return stats
    
    def run_backup_cycle(self):
        """Execute one backup cycle."""
        print(f"\n{'=' * 70}")
        print(f"BACKUP CYCLE - {datetime.now().isoformat()}")
        print('=' * 70)
        
        backed_up = 0
        total_size = 0
        
        for filename in CRITICAL_FILES:
            if self.backup_file(filename):
                filesize = Path(filename).stat().st_size
                total_size += filesize
                backed_up += 1
                print(f"   ✓ {filename} ({filesize / 1024:.1f} KB)")
            else:
                print(f"   ⊘ {filename} (not found)")
        
        # Create seed archive
        seed_file = self.create_seed_archive()
        seed_size = seed_file.stat().st_size
        print(f"\n   📦 Seed Archive: {seed_file.name} ({seed_size / 1024:.1f} KB)")
        
        print(f"\n   Summary:")
        print(f"   • Files backed up: {backed_up}/{len(CRITICAL_FILES)}")
        print(f"   • Total size: {total_size / 1024:.1f} KB")
        print(f"   • Backup location: {self.backup_dir}")
        
        return backed_up > 0
    
    def run_autonomous(self):
        """Run backup daemon continuously."""
        print("=" * 70)
        print("BACKUP DAEMON - STARTED")
        print("=" * 70)
        print()
        print("Configuration:")
        print(f"  • Backup Interval: {BACKUP_INTERVAL}s ({BACKUP_INTERVAL // 60} minutes)")
        print(f"  • Backup Directory: {self.backup_dir}")
        print(f"  • Critical Files: {len(CRITICAL_FILES)}")
        print()
        print("Backup Strategy:")
        print("  1. Current backup (always latest)")
        print("  2. Versioned backup (timestamped)")
        print("  3. Seed archives (compressed, last 10 kept)")
        print()
        print("Constitutional Principle:")
        print("  'Collapse ends every civilization. The Ark must carry the Seed.'")
        print()
        print("Press Ctrl+C to stop")
        print()
        
        # Initial backup
        print("Running initial backup...")
        self.run_backup_cycle()
        
        try:
            while True:
                time.sleep(BACKUP_INTERVAL)
                self.run_backup_cycle()
                
                stats = self.get_backup_stats()
                print(f"\n📊 Backup Stats:")
                print(f"   • Files: {stats['files_backed_up']}")
                print(f"   • Size: {stats['total_size_bytes'] / 1024:.1f} KB")
                print(f"   • Seeds: {stats['seed_archives']}")
                print(f"   • Latest: {stats['latest_backup']}")
                
                print(f"\n⏰ Next backup in {BACKUP_INTERVAL}s")
                
        except KeyboardInterrupt:
            print("\n\n⏸️  Backup daemon stopped by user")
            stats = self.get_backup_stats()
            print(f"\nFinal backup stats:")
            print(f"  • Total backups: {stats['files_backed_up']}")
            print(f"  • Seed archives: {stats['seed_archives']}")

if __name__ == "__main__":
    import sys
    
    daemon = BackupDaemon()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run single backup for testing
        daemon.run_backup_cycle()
    elif len(sys.argv) > 1 and sys.argv[1] == '--stats':
        # Show stats only
        stats = daemon.get_backup_stats()
        print(json.dumps(stats, indent=2))
    else:
        # Run continuously
        daemon.run_autonomous()
