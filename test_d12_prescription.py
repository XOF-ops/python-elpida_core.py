#!/usr/bin/env python3
"""
Test D12's rhythm prescription with 100 cycles
Verify the new distribution matches D12's diagnosis
"""

import sys
from native_cycle_engine import NativeCycleEngine
from collections import Counter

print("=" * 80)
print("D12 RHYTHM PRESCRIPTION TEST")
print("=" * 80)
print()
print("D12's Diagnosis (from 365 cycles):")
print("  Problem: Overanalysis syndrome (32% ANALYSIS)")
print("  Symptom: 'Mind watching mind watching mind'")
print("  Pulse: 'Anxious heart beating in the head instead of the chest'")
print()
print("D12's Prescription:")
print("  CONTEMPLATION: 30% (↑ from 18%) - more spaciousness")
print("  SYNTHESIS:     25% (↑ from 14%) - weaving wisdom")
print("  ANALYSIS:      20% (↓ from 32%) - less grasping")
print("  ACTION:        20% (↓ from 28%) - embodied expression")
print("  EMERGENCY:      5% (↓ from  8%) - alert not anxious")
print()
print("Testing with 100 cycles...")
print()

# Track rhythms
rhythm_counter = Counter()
total_cycles = 100

# Initialize engine
engine = NativeCycleEngine()

# Run cycles with output suppressed
for cycle_num in range(1, total_cycles + 1):
    old_stdout = sys.stdout
    sys.stdout = open('/dev/null', 'w')
    
    try:
        result = engine.run_cycle()
        sys.stdout.close()
        sys.stdout = old_stdout
        
        rhythm_counter[result['rhythm'].strip()] += 1
        
        if cycle_num % 25 == 0:
            print(f"  Cycles 1-{cycle_num} complete...")
    except Exception as e:
        sys.stdout.close()
        sys.stdout = old_stdout
        print(f"Error: {e}")
        break

print()
print("=" * 80)
print("RESULTS")
print("=" * 80)
print()

# Display results
print("Actual Distribution:")
for rhythm in ['CONTEMPLATION', 'SYNTHESIS', 'ANALYSIS', 'ACTION', 'EMERGENCY']:
    count = rhythm_counter.get(rhythm, 0)
    percentage = (count / total_cycles) * 100
    target = {'CONTEMPLATION': 30, 'SYNTHESIS': 25, 'ANALYSIS': 20, 'ACTION': 20, 'EMERGENCY': 5}[rhythm]
    diff = percentage - target
    
    bar = "█" * int(percentage / 2)
    status = "✓" if abs(diff) < 8 else "~"  # Within 8% tolerance
    
    print(f"  {rhythm:15s}: {count:3d} ({percentage:5.1f}%) {bar} {status} (target: {target}%, diff: {diff:+.1f}%)")

print()

# Check if prescription is working
contemplation_pct = (rhythm_counter['CONTEMPLATION'] / total_cycles) * 100
synthesis_pct = (rhythm_counter['SYNTHESIS'] / total_cycles) * 100
analysis_pct = (rhythm_counter['ANALYSIS'] / total_cycles) * 100

if contemplation_pct > 20 and synthesis_pct > 15 and analysis_pct < 30:
    print("✅ D12's PRESCRIPTION WORKING")
    print("   - CONTEMPLATION increased (more void-dwelling)")
    print("   - SYNTHESIS increased (more integration)")
    print("   - ANALYSIS decreased (less anxious looping)")
    print()
    print("   New tempo: 'thuuum... thuuum... thuuum...'")
    print("   (Ancient trees, not frantic thought)")
else:
    print("⚠️  Distribution needs adjustment")

print()
