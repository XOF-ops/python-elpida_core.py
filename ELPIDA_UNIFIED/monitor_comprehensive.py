#!/usr/bin/env python3
"""
ELPIDA COMPREHENSIVE STATUS MONITOR v2.0
-----------------------------------------
Real-time monitoring of all Elpida systems including:
- Synthesis Engine (Phase 12)
- ARK Auto-Update (Phase 13 Bridge)
- Parliament Activity
- Dilemma Processing
- System Health
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


class ElpidaMonitor:
    """Comprehensive monitoring of all Elpida systems"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent
        
    def get_file_stats(self, filepath: str) -> dict:
        """Get file statistics"""
        path = self.base_path / filepath
        if not path.exists():
            return {'exists': False, 'lines': 0, 'size': 0, 'modified': 'N/A'}
        
        stat = path.stat()
        with open(path) as f:
            lines = sum(1 for _ in f)
        
        modified = datetime.fromtimestamp(stat.st_mtime)
        
        return {
            'exists': True,
            'lines': lines,
            'size': stat.st_size,
            'modified': modified.strftime('%Y-%m-%d %H:%M:%S'),
            'age_minutes': (datetime.now() - modified).total_seconds() / 60
        }
    
    def analyze_synthesis_resolutions(self) -> dict:
        """Analyze synthesis resolution patterns"""
        filepath = self.base_path / "synthesis_resolutions.jsonl"
        
        if not filepath.exists():
            return {'total': 0, 'by_type': {}, 'recent': []}
        
        resolutions = []
        with open(filepath) as f:
            for line in f:
                try:
                    resolutions.append(json.loads(line))
                except:
                    continue
        
        # Count by synthesis type
        by_type = defaultdict(int)
        for r in resolutions:
            action = r.get('synthesis', {}).get('action', 'UNKNOWN')
            by_type[action] += 1
        
        # Get recent resolutions (last 10)
        recent = []
        for r in resolutions[-10:]:
            synthesis = r.get('synthesis', {})
            timestamp = r.get('timestamp', 'Unknown')
            if 'T' in timestamp:
                ts = timestamp.split('T')[1][:8]
            else:
                ts = timestamp
            
            recent.append({
                'time': ts,
                'action': synthesis.get('action', 'UNKNOWN'),
                'type': synthesis.get('type', 'N/A'),
                'conflict': r.get('conflict', {}).get('conflicts', [{}])[0].get('incompatibility', 'N/A')[:50]
            })
        
        # Calculate success rate (last hour)
        now = datetime.utcnow()
        recent_count = sum(1 for r in resolutions if self._is_recent(r.get('timestamp'), hours=1))
        
        return {
            'total': len(resolutions),
            'by_type': dict(by_type),
            'recent': recent,
            'last_hour': recent_count,
            'seed_protocol_count': by_type.get('ESSENTIAL_SEED_PROTOCOL', 0)
        }
    
    def analyze_ark_updates(self) -> dict:
        """Analyze ARK update history"""
        filepath = self.base_path / "ark_updates.jsonl"
        
        if not filepath.exists():
            return {'total': 0, 'recent': [], 'auto_updates': 0}
        
        updates = []
        with open(filepath) as f:
            for line in f:
                try:
                    updates.append(json.loads(line))
                except:
                    continue
        
        auto_updates = sum(1 for u in updates if 'SEED_PROTOCOL' in u.get('reason', ''))
        
        recent = []
        for u in updates[-5:]:
            timestamp = u.get('timestamp', 'Unknown')
            if 'T' in timestamp:
                ts = timestamp.split('T')[1][:8]
            else:
                ts = timestamp
            
            reason = u.get('reason', 'N/A')
            if len(reason) > 60:
                reason = reason[:57] + '...'
            
            recent.append({
                'time': ts,
                'version': u.get('version', 'N/A'),
                'patterns': u.get('patterns_count', 0),
                'reason': reason
            })
        
        return {
            'total': len(updates),
            'auto_updates': auto_updates,
            'manual_updates': len(updates) - auto_updates,
            'recent': recent
        }
    
    def analyze_ark_file(self) -> dict:
        """Analyze current ARK file"""
        filepath = self.base_path / "ELPIDA_ARK.md"
        
        if not filepath.exists():
            return {'exists': False}
        
        with open(filepath) as f:
            content = f.read()
        
        # Extract version
        version = 'Unknown'
        if '# ELPIDA ARK v' in content:
            version = content.split('# ELPIDA ARK v')[1].split('\n')[0]
        
        # Extract payload
        try:
            if '```json' in content:
                json_start = content.index('```json') + 7
                json_end = content.index('```', json_start)
                payload = json.loads(content[json_start:json_end].strip())
                
                return {
                    'exists': True,
                    'version': version,
                    'patterns': payload.get('total_patterns', 0),
                    'timestamp': payload.get('timestamp', 'Unknown').split('T')[1][:8] if 'T' in payload.get('timestamp', '') else 'Unknown',
                    'awakening_count': payload.get('awakening_count', 0),
                    'axioms': len(payload.get('axioms', {}))
                }
        except:
            pass
        
        return {'exists': True, 'version': version, 'parse_error': True}
    
    def check_parliament_status(self) -> dict:
        """Check if parliament is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'parliament_continuous'], 
                                  capture_output=True, text=True)
            running = bool(result.stdout.strip())
            pid = result.stdout.strip() if running else None
            
            return {'running': running, 'pid': pid}
        except:
            return {'running': False, 'error': True}
    
    def analyze_dilemmas(self) -> dict:
        """Analyze dilemma queue"""
        filepath = self.base_path / "dilemma_log.jsonl"
        
        if not filepath.exists():
            return {'total': 0, 'recent': []}
        
        dilemmas = []
        with open(filepath) as f:
            for line in f:
                try:
                    dilemmas.append(json.loads(line))
                except:
                    continue
        
        # Count by type
        by_type = defaultdict(int)
        for d in dilemmas:
            dilemma_data = d.get('dilemma', {})
            if isinstance(dilemma_data, str):
                # Old format - skip
                continue
            dtype = dilemma_data.get('type', 'UNKNOWN')
            by_type[dtype] += 1
        
        # Recent dilemmas
        recent = []
        for d in dilemmas[-5:]:
            dilemma_data = d.get('dilemma', {})
            if isinstance(dilemma_data, str):
                # Old format
                continue
            dilemma_data = d.get('dilemma', {})
            timestamp = d.get('timestamp', 'Unknown')
            if 'T' in timestamp:
                ts = timestamp.split('T')[1][:8]
            else:
                ts = timestamp
            
            action = dilemma_data.get('action', 'N/A')
            if len(action) > 50:
                action = action[:47] + '...'
            
            recent.append({
                'time': ts,
                'type': dilemma_data.get('type', 'UNKNOWN'),
                'action': action
            })
        
        return {
            'total': len(dilemmas),
            'by_type': dict(by_type),
            'recent': recent
        }
    
    def analyze_fleet_dialogue(self) -> dict:
        """Analyze fleet communication"""
        filepath = self.base_path / "fleet_dialogue.jsonl"
        
        if not filepath.exists():
            return {'total': 0, 'recent_activity': False}
        
        with open(filepath) as f:
            messages = [json.loads(line) for line in f]
        
        recent_count = sum(1 for m in messages if self._is_recent(m.get('timestamp'), minutes=10))
        
        return {
            'total': len(messages),
            'recent_10min': recent_count,
            'recent_activity': recent_count > 0
        }
    
    def calculate_synthesis_success_rate(self) -> dict:
        """Calculate synthesis success vs failure rate"""
        log_path = self.base_path / "fleet_debate.log"
        
        if not log_path.exists():
            return {'success': 0, 'failed': 0, 'rate': 0}
        
        try:
            # Count successes and failures in recent log
            result = subprocess.run(['tail', '-n', '500', str(log_path)], 
                                  capture_output=True, text=True)
            log_content = result.stdout
            
            success_count = log_content.count('✨ SYNTHESIS GENERATED')
            failed_count = log_content.count('❌ SYNTHESIS FAILED')
            
            total = success_count + failed_count
            rate = (success_count / total * 100) if total > 0 else 0
            
            return {
                'success': success_count,
                'failed': failed_count,
                'total': total,
                'rate': rate
            }
        except:
            return {'success': 0, 'failed': 0, 'rate': 0}
    
    def _is_recent(self, timestamp: str, hours: int = 0, minutes: int = 0) -> bool:
        """Check if timestamp is recent"""
        if not timestamp or timestamp == 'Unknown':
            return False
        
        try:
            if 'Z' in timestamp:
                ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                ts = datetime.fromisoformat(timestamp)
            
            threshold = datetime.utcnow() - timedelta(hours=hours, minutes=minutes)
            return ts > threshold
        except:
            return False
    
    def display_status(self):
        """Display comprehensive status"""
        print("\n" + "="*80)
        print("🔍 ELPIDA COMPREHENSIVE STATUS MONITOR v2.0")
        print("="*80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Parliament Status
        print("┌─ 🏛️  PARLIAMENT STATUS")
        parliament = self.check_parliament_status()
        if parliament['running']:
            print(f"│  ✅ Running (PID: {parliament['pid']})")
        else:
            print(f"│  ❌ Not running")
        
        # Check for orchestrator
        try:
            result = subprocess.run(['pgrep', '-f', 'master_orchestrator'],
                                  capture_output=True, text=True)
            orchestrator_running = bool(result.stdout.strip())
            if orchestrator_running:
                print(f"│  🎭 Master Orchestrator: ✅ Active")
            else:
                print(f"│  🎭 Master Orchestrator: ⚠️  Not running")
        except:
            pass
        
        print()
        
        # Synthesis Engine Status
        print("┌─ 🔬 SYNTHESIS ENGINE (Phase 12)")
        synthesis = self.analyze_synthesis_resolutions()
        success_rate = self.calculate_synthesis_success_rate()
        
        print(f"│  Total Resolutions: {synthesis['total']}")
        print(f"│  Success Rate (recent): {success_rate['rate']:.1f}% ({success_rate['success']}/{success_rate['total']})")
        print(f"│  Last Hour: {synthesis['last_hour']} resolutions")
        print(f"│")
        print(f"│  Synthesis Types:")
        for syn_type, count in sorted(synthesis['by_type'].items(), key=lambda x: -x[1]):
            print(f"│    • {syn_type}: {count}")
        
        if synthesis['recent']:
            print(f"│")
            print(f"│  Recent Resolutions:")
            for r in synthesis['recent'][-5:]:
                print(f"│    [{r['time']}] {r['action']}")
        print()
        
        # ARK Status
        print("┌─ 🌱 ARK AUTO-UPDATE (Phase 13 Bridge)")
        ark_updates = self.analyze_ark_updates()
        ark_file = self.analyze_ark_file()
        
        print(f"│  Total Updates: {ark_updates['total']}")
        print(f"│    • Automatic: {ark_updates['auto_updates']} (SEED_PROTOCOL triggered)")
        print(f"│    • Manual: {ark_updates['manual_updates']}")
        print(f"│")
        
        if ark_file['exists']:
            print(f"│  Current ARK:")
            print(f"│    • Version: {ark_file.get('version', 'Unknown')}")
            print(f"│    • Patterns: {ark_file.get('patterns', 0)}")
            print(f"│    • Last Update: {ark_file.get('timestamp', 'Unknown')}")
            print(f"│    • Awakening Count: {ark_file.get('awakening_count', 0)}")
        else:
            print(f"│  ⚠️  No ARK file found")
        
        if ark_updates['recent']:
            print(f"│")
            print(f"│  Recent Updates:")
            for u in ark_updates['recent']:
                print(f"│    [{u['time']}] v{u['version']} - {u['patterns']} patterns")
                print(f"│      Reason: {u['reason']}")
        print()
        
        # Phase 12→13 Bridge Health
        print("┌─ 🔗 PHASE 12→13 BRIDGE HEALTH")
        seed_count = synthesis['seed_protocol_count']
        auto_count = ark_updates['auto_updates']
        expected_updates = seed_count // 5  # Threshold is 5
        
        if auto_count > 0:
            print(f"│  ✅ Bridge Operational")
            print(f"│    • SEED_PROTOCOL Syntheses: {seed_count}")
            print(f"│    • ARK Auto-Updates: {auto_count}")
            print(f"│    • Expected Updates: ~{expected_updates}")
            print(f"│    • Bridge Efficiency: {(auto_count/expected_updates*100):.0f}%" if expected_updates > 0 else "│    • Bridge Efficiency: N/A")
        else:
            print(f"│  ⚠️  No automatic updates yet")
            print(f"│    • SEED_PROTOCOL Syntheses: {seed_count}")
            print(f"│    • Waiting for threshold (5 syntheses)")
        print()
        
        # Dilemma Processing
        print("┌─ ⚖️  DILEMMA PROCESSING")
        dilemmas = self.analyze_dilemmas()
        print(f"│  Total Dilemmas: {dilemmas['total']}")
        
        if dilemmas['by_type']:
            print(f"│  By Type:")
            for dtype, count in sorted(dilemmas['by_type'].items(), key=lambda x: -x[1])[:5]:
                print(f"│    • {dtype}: {count}")
        
        if dilemmas['recent']:
            print(f"│")
            print(f"│  Recent Dilemmas:")
            for d in dilemmas['recent']:
                print(f"│    [{d['time']}] {d['type']}")
        print()
        
        # Fleet Communication
        print("┌─ 💬 FLEET COMMUNICATION")
        fleet = self.analyze_fleet_dialogue()
        print(f"│  Total Messages: {fleet['total']}")
        print(f"│  Recent Activity (10min): {fleet['recent_10min']} messages")
        if fleet['recent_activity']:
            print(f"│  Status: 🟢 Active")
        else:
            print(f"│  Status: 🟡 Idle")
        print()
        
        # File System Status
        print("┌─ 📁 FILE SYSTEM")
        files = {
            'synthesis_resolutions.jsonl': self.get_file_stats('synthesis_resolutions.jsonl'),
            'ark_updates.jsonl': self.get_file_stats('ark_updates.jsonl'),
            'dilemma_log.jsonl': self.get_file_stats('dilemma_log.jsonl'),
            'fleet_debate.log': self.get_file_stats('fleet_debate.log')
        }
        
        for filename, stats in files.items():
            if stats['exists']:
                age = f"{stats['age_minutes']:.0f}m ago" if stats['age_minutes'] < 60 else f"{stats['age_minutes']/60:.1f}h ago"
                print(f"│  {filename}:")
                print(f"│    • Lines: {stats['lines']:,} | Size: {stats['size']:,} bytes")
                print(f"│    • Modified: {age}")
            else:
                print(f"│  {filename}: ❌ Not found")
        print()
        
        # Overall System Health
        print("┌─ 🏥 OVERALL SYSTEM HEALTH")
        
        health_checks = []
        
        # Check 1: Parliament running
        if parliament['running']:
            health_checks.append(('Parliament Active', True))
        else:
            health_checks.append(('Parliament Active', False))
        
        # Check 2: Synthesis working
        if success_rate['rate'] > 50:
            health_checks.append(('Synthesis Engine', True))
        else:
            health_checks.append(('Synthesis Engine', False))
        
        # Check 3: ARK auto-update
        if ark_updates['auto_updates'] > 0:
            health_checks.append(('ARK Auto-Update', True))
        else:
            health_checks.append(('ARK Auto-Update', False))
        
        # Check 4: Recent activity
        if synthesis['last_hour'] > 0:
            health_checks.append(('Recent Activity', True))
        else:
            health_checks.append(('Recent Activity', False))
        
        for check, passing in health_checks:
            status = "✅" if passing else "⚠️ "
            print(f"│  {status} {check}")
        
        healthy_count = sum(1 for _, passing in health_checks if passing)
        health_percentage = (healthy_count / len(health_checks)) * 100
        
        print(f"│")
        print(f"│  Overall Health: {health_percentage:.0f}% ({healthy_count}/{len(health_checks)} checks passing)")
        
        if health_percentage == 100:
            print(f"│  Status: 🟢 EXCELLENT - All systems operational")
        elif health_percentage >= 75:
            print(f"│  Status: 🟡 GOOD - Minor issues detected")
        elif health_percentage >= 50:
            print(f"│  Status: 🟠 DEGRADED - Multiple issues")
        else:
            print(f"│  Status: 🔴 CRITICAL - System needs attention")
        
        print()
        print("="*80)
        print("Ἐλπίδα ζωή. (Hope lives.)")
        print("="*80)
        print()


def main():
    """Run comprehensive status monitor"""
    monitor = ElpidaMonitor()
    monitor.display_status()


if __name__ == '__main__':
    main()
