#!/usr/bin/env python3
"""
ELPIDA MASTER ORCHESTRATOR v1.0
--------------------------------
Complete evolutionary system orchestration.

Manages the full cycle:
1. Elpida awakens → generates insights
2. Insights → parliament dilemmas
3. Parliament → synthesis → ARK update
4. ARK → feeds back to Elpida
5. Cycle repeats → evolution

This is the missing piece that closes the loop.
"""

import time
import subprocess
from pathlib import Path
from datetime import datetime


class MasterOrchestrator:
    """
    Orchestrates the complete Elpida evolutionary ecosystem.
    
    Components:
    - Elpida Core (insights generation)
    - Parliament (deliberation)
    - Synthesis Engine (conflict resolution)
    - ARK Manager (wisdom compression)
    - Evolution Feedback (learning loop)
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.parliament_running = False
        self.cycle_interval = 300  # 5 minutes between Elpida awakenings
        
    def check_parliament(self) -> bool:
        """Check if parliament is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'parliament_continuous'],
                                  capture_output=True, text=True)
            return bool(result.stdout.strip())
        except:
            return False
    
    def start_parliament(self):
        """Start parliament if not running"""
        if not self.check_parliament():
            print("🏛️  Starting Parliament...")
            subprocess.Popen(
                ['python3', 'parliament_continuous.py'],
                cwd=self.base_path,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(5)
            print("   ✅ Parliament started")
    
    def trigger_elpida_cycle(self):
        """Trigger one Elpida awakening → insight → dilemma cycle"""
        print("\n" + "="*80)
        print(f"⚡ ELPIDA AWAKENING TRIGGERED - {datetime.now().strftime('%H:%M:%S')}")
        print("="*80)
        
        try:
            result = subprocess.run(
                ['python3', 'elpida_integrated_runtime.py'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Show summary
            if 'INTEGRATION COMPLETE' in result.stdout:
                print("✅ Elpida cycle complete")
                # Extract summary
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if '📊 Summary:' in line:
                        # Print next 3 lines
                        for j in range(i, min(i+4, len(lines))):
                            print(lines[j])
                        break
            else:
                print("⚠️  Elpida cycle incomplete")
                print(result.stdout[-500:] if result.stdout else "No output")
                
        except subprocess.TimeoutExpired:
            print("⚠️  Elpida awakening timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def run_orchestrated_system(self):
        """
        Run the complete orchestrated system.
        
        Parliament runs continuously.
        Elpida awakens periodically to inject new insights.
        """
        print("\n" + "="*80)
        print("🎭 ELPIDA MASTER ORCHESTRATOR")
        print("="*80)
        print()
        print("Components:")
        print("  1. Elpida Core - Insight generation (every 5 min)")
        print("  2. Parliament - Continuous deliberation")
        print("  3. Synthesis Engine - Conflict resolution")
        print("  4. ARK Manager - Wisdom compression")
        print("  5. Evolution Feedback - Learning loop")
        print()
        print("Complete evolutionary cycle:")
        print("  Elpida → Insights → Dilemmas → Synthesis → ARK → Elpida'")
        print()
        print("Press Ctrl+C to stop")
        print("="*80)
        print()
        
        # Ensure parliament is running
        self.start_parliament()
        
        try:
            cycle = 0
            while True:
                cycle += 1
                
                # Trigger Elpida awakening
                self.trigger_elpida_cycle()
                
                # Wait for next cycle
                print()
                print(f"⏰ Next Elpida awakening in {self.cycle_interval}s")
                print(f"   (Parliament continues processing in background)")
                print()
                
                time.sleep(self.cycle_interval)
                
        except KeyboardInterrupt:
            print("\n\n⏸️  Orchestrator stopped")
            print(f"   Completed {cycle} Elpida awakening cycles")
            print("   Parliament continues running in background")
            print()


def main():
    """Run master orchestrator"""
    orchestrator = MasterOrchestrator()
    orchestrator.run_orchestrated_system()


if __name__ == '__main__':
    main()
