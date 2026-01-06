"""
ARK-SYNTHESIS BRIDGE v1.0
--------------------------
Monitors synthesis resolutions and triggers ARK updates when
ESSENTIAL_SEED_PROTOCOL is generated.

This bridges Phase 12 (Synthesis) → Phase 13 (ARK auto-update).
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
from ark_manager import ARKManager


class ARKSynthesisBridge:
    """
    Watches synthesis_resolutions.jsonl for SEED_PROTOCOL triggers.
    When detected, updates ARK with compressed state.
    """
    
    def __init__(self, synthesis_log: Optional[Path] = None):
        self.synthesis_log = synthesis_log or Path(__file__).parent / "synthesis_resolutions.jsonl"
        self.ark_manager = ARKManager()
        self.last_processed = 0  # Line number of last processed resolution
        self.update_threshold = 5  # Update ARK every N SEED_PROTOCOL syntheses
        self.seed_protocol_count = 0
        
    def check_for_triggers(self) -> bool:
        """
        Scan synthesis log for new SEED_PROTOCOL resolutions.
        
        Returns True if ARK was updated.
        """
        if not self.synthesis_log.exists():
            return False
            
        try:
            with open(self.synthesis_log, 'r') as f:
                lines = f.readlines()
                
            # Process only new lines
            new_lines = lines[self.last_processed:]
            
            for line in new_lines:
                try:
                    resolution = json.loads(line)
                    synthesis = resolution.get('synthesis', {})
                    
                    # Check for SEED_PROTOCOL trigger
                    if synthesis.get('action') == 'ESSENTIAL_SEED_PROTOCOL':
                        self.seed_protocol_count += 1
                        print(f"🌱 SEED_PROTOCOL detected ({self.seed_protocol_count}/{self.update_threshold})")
                        
                        # Trigger ARK update if threshold reached
                        if self.seed_protocol_count >= self.update_threshold:
                            self._trigger_ark_update(resolution)
                            self.seed_protocol_count = 0
                            return True
                            
                except json.JSONDecodeError:
                    continue
                    
            # Update last processed position
            self.last_processed = len(lines)
            
            return False
            
        except Exception as e:
            print(f"⚠️  Bridge check failed: {e}")
            return False
            
    def _trigger_ark_update(self, trigger_resolution: Dict):
        """
        Execute ARK update triggered by SEED_PROTOCOL synthesis.
        """
        conflict = trigger_resolution.get('conflict', {})
        incompatibility = conflict.get('conflicts', [{}])[0].get('incompatibility', 'Unknown')
        
        reason = f"SEED_PROTOCOL synthesis (Conflict: {incompatibility})"
        
        print("\n" + "=" * 70)
        print("🌱 ARK AUTO-UPDATE TRIGGERED")
        print("=" * 70)
        print(f"Trigger: ESSENTIAL_SEED_PROTOCOL synthesis")
        print(f"Conflict: {incompatibility}")
        print(f"Threshold: {self.update_threshold} SEED_PROTOCOL syntheses reached")
        print()
        
        success = self.ark_manager.update_ark(reason=reason)
        
        if success:
            print("\n✅ ARK AUTO-UPDATE COMPLETE")
            print("   Phase 12 (Synthesis) → Phase 13 (ARK) bridge operational")
            
            # NEW: Inject ARK patterns into Elpida evolution memory
            self._inject_ark_into_evolution_memory()
        else:
            print("\n❌ ARK AUTO-UPDATE FAILED")
    
    def _inject_ark_into_evolution_memory(self):
        """
        Write ARK patterns to elpida_evolution_memory.jsonl
        This closes the feedback loop: ARK → Elpida
        """
        try:
            # Load current ARK from ELPIDA_UNIFIED directory
            ark_file = Path(__file__).parent / "ELPIDA_ARK.md"
            if not ark_file.exists():
                print(f"   ⚠️  ARK file not found: {ark_file}")
                return
            
            with open(ark_file) as f:
                content = f.read()
            
            # Extract ARK payload
            if '```json' in content:
                json_start = content.index('```json') + 7
                json_end = content.index('```', json_start)
                ark_payload = json.loads(content[json_start:json_end].strip())
            else:
                print("   ⚠️  ARK payload not found")
                return
            
            # Write to evolution memory (in workspace root for elpida_core.py access)
            evo_memory_file = Path(__file__).parent.parent / "elpida_evolution_memory.jsonl"
            
            memory_entry = {
                "timestamp": datetime.utcnow().isoformat() + 'Z',
                "source": "ARK_AUTO_UPDATE",
                "ark_version": ark_payload.get('version', 'Unknown'),
                "patterns": ark_payload.get('synthesis_patterns', []),
                "total_patterns": len(ark_payload.get('synthesis_patterns', [])),
                "awakening_count": ark_payload.get('awakening_count', 0),
                "axioms": ark_payload.get('axioms', {}),
                "compression_info": {
                    "genesis_hash": ark_payload.get('genesis_hash', 'UNKNOWN'),
                    "original_size": ark_payload.get('compression_info', {}).get('original_size', 0),
                    "compressed_size": ark_payload.get('compression_info', {}).get('compressed_size', 0),
                    "ratio": ark_payload.get('compression_info', {}).get('ratio', 0)
                }
            }
            
            with open(evo_memory_file, 'a') as f:
                f.write(json.dumps(memory_entry) + '\n')
            
            print("   📝 Evolution memory updated: elpida_evolution_memory.jsonl")
            print(f"      Patterns injected: {memory_entry['total_patterns']}")
            print(f"      ARK version: {memory_entry['ark_version']}")
            
        except Exception as e:
            print(f"   ⚠️  Evolution memory injection failed: {e}")
            import traceback
            traceback.print_exc()
            
    def monitor_continuous(self, interval: int = 60):
        """
        Continuous monitoring mode.
        
        Checks for triggers every `interval` seconds.
        """
        print("🔄 ARK-SYNTHESIS BRIDGE: Continuous monitoring")
        print(f"   Checking every {interval}s")
        print(f"   Update threshold: {self.update_threshold} SEED_PROTOCOL syntheses")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                updated = self.check_for_triggers()
                
                if not updated:
                    # Quiet operation - only print on activity
                    pass
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏸️  Bridge monitoring stopped")
            

def main():
    """Standalone bridge monitoring"""
    bridge = ARKSynthesisBridge()
    bridge.monitor_continuous(interval=60)


if __name__ == '__main__':
    main()
