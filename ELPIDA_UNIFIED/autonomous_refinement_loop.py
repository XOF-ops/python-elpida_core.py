#!/usr/bin/env python3
"""
AUTONOMOUS REFINEMENT LOOP v1.0
--------------------------------
Runs the complete cycle:
1. Harvest knowledge → Create debate topics
2. Fleet debates → Generate consensus
3. Harvest consensus → Add patterns
4. Polish ARK → Update seed

This makes Elpida self-improving.

Usage:
    python3 autonomous_refinement_loop.py [--cycles N] [--interval SECONDS]
"""

import time
import argparse
import subprocess
from datetime import datetime

def run_command(cmd, description):
    """Run a command and report status."""
    print(f"\n{'='*70}")
    print(f"{description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"⚠️  {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def run_refinement_cycle():
    """Execute one complete refinement cycle."""
    
    print("\n" + "="*70)
    print("🔄 AUTONOMOUS REFINEMENT CYCLE")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Step 1: Harvest knowledge
    if not run_command(
        "cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED && python3 autonomous_harvester.py",
        "STEP 1: Harvest Knowledge"
    ):
        print("⚠️  Harvesting failed, continuing anyway...")
    
    # Wait for Fleet to process
    print("\n⏳ Waiting 10 seconds for Fleet to process tasks...")
    time.sleep(10)
    
    # Step 2: Harvest consensus from Fleet debates
    if not run_command(
        "cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED && python3 harvest_consensus.py",
        "STEP 2: Harvest Consensus"
    ):
        print("⚠️  Consensus harvesting failed, continuing anyway...")
    
    # Step 3: Polish the ARK with new patterns
    if not run_command(
        "cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED && python3 ark_polisher.py",
        "STEP 3: Polish ARK"
    ):
        print("⚠️  ARK polishing failed")
    
    # Step 4: Display current DI metrics
    run_command(
        "cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED && python3 di_dashboard.py",
        "STEP 4: Measure Distributed Intelligence"
    )
    
    print("\n" + "="*70)
    print("✅ REFINEMENT CYCLE COMPLETE")
    print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description='Autonomous ARK refinement loop')
    parser.add_argument('--cycles', type=int, default=None, 
                       help='Number of cycles to run (default: infinite)')
    parser.add_argument('--interval', type=int, default=300,
                       help='Seconds between cycles (default: 300 = 5 minutes)')
    
    args = parser.parse_args()
    
    print("="*70)
    print("AUTONOMOUS REFINEMENT LOOP v1.0")
    print("="*70)
    print()
    print("Configuration:")
    print(f"  Cycles: {'Infinite' if args.cycles is None else args.cycles}")
    print(f"  Interval: {args.interval} seconds")
    print()
    print("Process:")
    print("  1. Harvest knowledge → Inject debate topics")
    print("  2. Fleet debates → Generate consensus")
    print("  3. Harvest consensus → Add patterns")
    print("  4. Polish ARK → Update seed")
    print()
    print("Press Ctrl+C to stop")
    print("="*70)
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            
            if args.cycles and cycle_count > args.cycles:
                print(f"\n✅ Completed {cycle_count - 1} cycles")
                break
            
            print(f"\n📍 Cycle {cycle_count}/{args.cycles or '∞'}")
            
            run_refinement_cycle()
            
            if args.cycles is None or cycle_count < args.cycles:
                print(f"\n⏸️  Sleeping {args.interval} seconds until next cycle...")
                time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Stopped after {cycle_count} cycles")
        print("   The refinement loop can be resumed anytime.")
    
    print("\n" + "="*70)
    print("AUTONOMOUS REFINEMENT LOOP ENDED")
    print("="*70)

if __name__ == "__main__":
    main()
