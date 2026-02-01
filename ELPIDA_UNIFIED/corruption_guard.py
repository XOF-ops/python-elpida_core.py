#!/usr/bin/env python3
"""
CORRUPTION DETECTION & RECOVERY SYSTEM
=======================================

Monitors critical files for corruption and automatically recovers.
Runs as a background daemon alongside the system.

FEATURES:
- Real-time corruption detection
- Automatic recovery from backups
- Health monitoring
- Alert logging
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import shutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [CorruptionGuard] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('corruption_guard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CorruptionGuard")


class FileHealthMonitor:
    """Monitors critical JSON files for corruption"""
    
    def __init__(self, workspace_path: Path):
        self.workspace = Path(workspace_path)
        self.backup_dir = self.workspace / ".backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Critical files to monitor
        self.critical_files = [
            "elpida_wisdom.json",
            "elpida_unified_state.json",
            "elpida_memory.json",
            "elpida_evolution.json"
        ]
        
        # Health tracking
        self.health_log = []
        self.corruption_events = []
        self.recovery_events = []
        
    def check_file_health(self, filepath: Path) -> Dict:
        """
        Check if a JSON file is healthy
        
        Returns:
            {
                'healthy': bool,
                'error': Optional[str],
                'size': int,
                'last_modified': str
            }
        """
        result = {
            'healthy': True,
            'error': None,
            'size': 0,
            'last_modified': None
        }
        
        if not filepath.exists():
            result['healthy'] = False
            result['error'] = "FILE_NOT_FOUND"
            return result
        
        try:
            # Check file size
            stat = filepath.stat()
            result['size'] = stat.st_size
            result['last_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Try to parse JSON
            with open(filepath, 'r') as f:
                json.load(f)
            
            result['healthy'] = True
            
        except json.JSONDecodeError as e:
            result['healthy'] = False
            result['error'] = f"JSON_CORRUPTION: {e}"
            logger.error(f"❌ Corruption detected in {filepath.name}: {e}")
            
        except Exception as e:
            result['healthy'] = False
            result['error'] = f"READ_ERROR: {e}"
            logger.error(f"❌ Read error in {filepath.name}: {e}")
        
        return result
    
    def find_latest_backup(self, filename: str) -> Optional[Path]:
        """Find the latest valid backup for a file"""
        backups = sorted(self.backup_dir.glob(f"{filename}.backup.*"), reverse=True)
        
        for backup_path in backups:
            health = self.check_file_health(backup_path)
            if health['healthy']:
                return backup_path
        
        return None
    
    def recover_file(self, filepath: Path) -> bool:
        """
        Attempt to recover a corrupted file from backup
        
        Returns:
            True if recovery successful
        """
        logger.warning(f"🔧 Attempting recovery for {filepath.name}...")
        
        # Find latest valid backup
        backup_path = self.find_latest_backup(filepath.name)
        
        if not backup_path:
            logger.error(f"❌ No valid backup found for {filepath.name}")
            return False
        
        try:
            # Move corrupted file to quarantine
            quarantine_dir = self.workspace / ".quarantine"
            quarantine_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            quarantine_path = quarantine_dir / f"{filepath.name}.corrupted.{timestamp}"
            
            shutil.move(str(filepath), str(quarantine_path))
            logger.info(f"📦 Corrupted file quarantined: {quarantine_path.name}")
            
            # Restore from backup
            shutil.copy2(backup_path, filepath)
            logger.info(f"✅ Restored from backup: {backup_path.name}")
            
            # Verify restored file
            health = self.check_file_health(filepath)
            if health['healthy']:
                logger.info(f"✅ Recovery successful for {filepath.name}")
                self.recovery_events.append({
                    'timestamp': datetime.now().isoformat(),
                    'file': filepath.name,
                    'backup_used': backup_path.name,
                    'success': True
                })
                return True
            else:
                logger.error(f"❌ Restored file still unhealthy: {health['error']}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Recovery failed for {filepath.name}: {e}")
            self.recovery_events.append({
                'timestamp': datetime.now().isoformat(),
                'file': filepath.name,
                'error': str(e),
                'success': False
            })
            return False
    
    def monitor_loop(self, interval: int = 60):
        """
        Continuous monitoring loop
        
        Args:
            interval: Check interval in seconds
        """
        logger.info("🛡️  Corruption Guard started")
        logger.info(f"   Monitoring: {', '.join(self.critical_files)}")
        logger.info(f"   Check interval: {interval}s")
        
        check_count = 0
        
        while True:
            try:
                check_count += 1
                timestamp = datetime.now().isoformat()
                
                logger.info(f"🔍 Health check #{check_count} at {timestamp}")
                
                all_healthy = True
                
                for filename in self.critical_files:
                    filepath = self.workspace / filename
                    health = self.check_file_health(filepath)
                    
                    if health['healthy']:
                        logger.info(f"   ✅ {filename}: OK ({health['size']:,} bytes)")
                    else:
                        logger.error(f"   ❌ {filename}: {health['error']}")
                        all_healthy = False
                        
                        # Log corruption event
                        self.corruption_events.append({
                            'timestamp': timestamp,
                            'file': filename,
                            'error': health['error']
                        })
                        
                        # Attempt recovery
                        success = self.recover_file(filepath)
                        
                        if success:
                            logger.info(f"   ✅ {filename}: RECOVERED")
                        else:
                            logger.error(f"   ❌ {filename}: RECOVERY FAILED - MANUAL INTERVENTION REQUIRED")
                
                # Log health status
                self.health_log.append({
                    'timestamp': timestamp,
                    'check_number': check_count,
                    'all_healthy': all_healthy,
                    'total_corruptions': len(self.corruption_events),
                    'total_recoveries': len([e for e in self.recovery_events if e['success']])
                })
                
                # Save health report
                if check_count % 10 == 0:  # Every 10 checks
                    self.save_health_report()
                
                # Sleep until next check
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Corruption Guard stopped by user")
                self.save_health_report()
                break
                
            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                time.sleep(interval)
    
    def save_health_report(self):
        """Save health report to file"""
        report_path = self.workspace / "corruption_guard_report.json"
        
        report = {
            'generated': datetime.now().isoformat(),
            'total_checks': len(self.health_log),
            'corruption_events': self.corruption_events,
            'recovery_events': self.recovery_events,
            'recent_health': self.health_log[-100:]  # Last 100 checks
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Health report saved: {report_path.name}")


def main():
    """Run corruption guard"""
    workspace = Path("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED")
    
    monitor = FileHealthMonitor(workspace)
    
    print("="*80)
    print("CORRUPTION DETECTION & RECOVERY SYSTEM")
    print("="*80)
    print()
    print("This daemon monitors critical files and auto-recovers from corruption.")
    print()
    print("Critical files monitored:")
    for f in monitor.critical_files:
        print(f"   • {f}")
    print()
    print("Press Ctrl+C to stop")
    print("="*80)
    print()
    
    # Run monitor
    monitor.monitor_loop(interval=60)


if __name__ == "__main__":
    main()
