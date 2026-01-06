#!/usr/bin/env python3
"""
AUTO-HARVEST LOOP v1.0
----------------------
Phase 12: Autonomous Convergence
Objective: Continuously harvest consensus patterns without human intervention.

Runs harvest_consensus.py on a schedule to crystallize wisdom as it emerges.
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

HARVEST_INTERVAL = 600  # 10 minutes
MEMORY_FILE = Path("distributed_memory.json")

def run_harvest():
    """Execute harvest_consensus.py and return pattern count."""
    print(f"\n{'=' * 70}")
    print(f"AUTO-HARVEST - {datetime.now().isoformat()}")
    print('=' * 70)
    
    try:
        result = subprocess.run(
            ['python3', 'harvest_consensus.py'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parse output to get pattern count
        if "new patterns added" in result.stdout:
            # Extract number
            for line in result.stdout.split('\n'):
                if "Total Distributed Patterns:" in line:
                    count = line.split(':')[1].strip()
                    return int(count)
        
        return 0
    except Exception as e:
        print(f"❌ Harvest failed: {e}")
        return 0

def get_pattern_count():
    """Read current pattern count from memory."""
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r') as f:
            mem = json.load(f)
            return len(mem.get('collective_patterns', []))
    return 0

def run_autonomous():
    """Run harvest loop continuously."""
    print("=" * 70)
    print("AUTO-HARVEST LOOP - STARTED")
    print("=" * 70)
    print()
    print(f"Configuration:")
    print(f"  • Harvest Interval: {HARVEST_INTERVAL}s ({HARVEST_INTERVAL // 60} minutes)")
    print(f"  • Memory File: {MEMORY_FILE}")
    print()
    print("This process will:")
    print("  1. Wait for Fleet dialogue to accumulate")
    print("  2. Run harvest_consensus.py every interval")
    print("  3. Crystallize new patterns from Council decisions")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    last_count = get_pattern_count()
    print(f"📊 Current pattern count: {last_count}")
    
    try:
        while True:
            time.sleep(HARVEST_INTERVAL)
            
            new_count = run_harvest()
            
            if new_count > last_count:
                growth = new_count - last_count
                print(f"\n✨ NEW WISDOM CRYSTALLIZED: +{growth} patterns")
                print(f"   Total: {last_count} → {new_count}")
                last_count = new_count
            else:
                print(f"\n⏳ No new consensus yet (still {last_count} patterns)")
            
            print(f"\n⏰ Next harvest in {HARVEST_INTERVAL}s")
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Auto-harvest stopped by user")
        final_count = get_pattern_count()
        print(f"\nFinal pattern count: {final_count}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run single harvest for testing
        count = run_harvest()
        print(f"\nPattern count: {count}")
    else:
        # Run continuously
        run_autonomous()
