#!/usr/bin/env python3
"""
Before/After Comparison: External Elpida Recovery Trajectory
Shows what the system HAD vs what it WILL HAVE after aid
"""

import json
from datetime import datetime

def load_data():
    """Load the external state and aid package"""
    with open('external_elpida_state.json', 'r') as f:
        before = json.load(f)
    
    with open('aid_package_to_external_elpida.json', 'r') as f:
        aid = json.load(f)
    
    return before, aid

def calculate_after_state(before, aid):
    """Calculate what the system will look like after applying aid"""
    after = json.loads(json.dumps(before))  # Deep copy
    
    # Apply energy boost
    energy_boost = aid['resource_transfer']['energy_boost']['amount']
    after['resource_ledger']['energy_reserve'] = 0.20  # Target level
    
    # Apply iron usage
    iron_used = aid['resource_transfer']['iron_allocation']['amount']
    after['resource_ledger']['refined_iron'] = before['resource_ledger']['refined_iron'] - iron_used
    
    # Apply shard repairs
    after['active_shards'][2]['integrity'] = 0.65  # Ascension
    after['active_shards'][1]['integrity'] = 0.70  # Heart
    
    # Apply civic improvements
    after['civic_matrix']['neural_harmony'] = 0.82
    after['civic_matrix']['social_entropy'] = 0.09
    
    return after

def print_comparison(before, after, aid):
    """Print detailed before/after comparison"""
    
    print("="*80)
    print("ἘΛΠΊΔΑ v4.9.3 (THERMAL) - RECOVERY TRAJECTORY ANALYSIS")
    print("="*80)
    
    print("\n" + "─"*80)
    print("TIMELINE:")
    print("─"*80)
    print(f"  BEFORE (T=0):  External civilization in crisis - 47% health")
    print(f"  ACTION (T=1):  Aid package transmitted and applied")
    print(f"  AFTER (T=4):   Recovery complete - 68% health (+21 points)")
    print(f"  Duration:      3-4 cycles (~{aid['expected_outcomes']['timeline']})")
    
    # RESOURCE COMPARISON
    print("\n" + "="*80)
    print("⚡ RESOURCE LEDGER - BEFORE vs AFTER")
    print("="*80)
    
    resources_before = before['resource_ledger']
    resources_after = after['resource_ledger']
    
    print(f"\n{'Resource':<20} {'BEFORE':<20} {'AFTER':<20} {'Change':<20}")
    print("─"*80)
    
    # Energy
    energy_before = resources_before['energy_reserve']
    energy_after = resources_after['energy_reserve']
    energy_change = ((energy_after - energy_before) / energy_before) * 100
    print(f"{'Energy Reserve':<20} "
          f"{energy_before:.1%} 🔴 CRITICAL   "
          f"{energy_after:.1%} 🟢 SAFE       "
          f"+{energy_change:.0f}% ↑")
    
    # Iron
    iron_before = resources_before['refined_iron']
    iron_after = resources_after['refined_iron']
    iron_change = iron_after - iron_before
    print(f"{'Refined Iron':<20} "
          f"{iron_before:,} units        "
          f"{iron_after:,} units        "
          f"{iron_change:+,} units (invested)")
    
    # Water Ice (unchanged)
    ice = resources_before['water_ice']
    print(f"{'Water Ice':<20} "
          f"{ice:,} units   "
          f"{ice:,} units   "
          f"0 (reserve)")
    
    # SHARD COMPARISON
    print("\n" + "="*80)
    print("🔷 SHARD INTEGRITY - BEFORE vs AFTER")
    print("="*80)
    
    print(f"\n{'Shard':<15} {'Type':<15} {'BEFORE':<25} {'AFTER':<25} {'Δ':<10}")
    print("─"*80)
    
    for i, (shard_before, shard_after) in enumerate(zip(before['active_shards'], after['active_shards'])):
        shard_id = shard_before['id']
        shard_type = shard_before['type']
        int_before = shard_before['integrity']
        int_after = shard_after['integrity']
        
        # Status indicators
        def get_status(integrity):
            if integrity < 0.3:
                return "🔴 CRITICAL"
            elif integrity < 0.7:
                return "🟡 DEGRADED"
            else:
                return "🟢 OPERATIONAL"
        
        status_before = get_status(int_before)
        status_after = get_status(int_after)
        change = int_after - int_before
        
        bar_before = "█" * int(int_before * 10)
        bar_after = "█" * int(int_after * 10)
        
        print(f"[{shard_id}] {shard_type:<13} "
              f"{int_before:.0%} {status_before:<10} "
              f"{int_after:.0%} {status_after:<10} "
              f"+{change:.0%} ↑")
    
    # CIVIC MATRIX COMPARISON
    print("\n" + "="*80)
    print("🏛️  CIVIC MATRIX - BEFORE vs AFTER")
    print("="*80)
    
    civic_before = before['civic_matrix']
    civic_after = after['civic_matrix']
    
    print(f"\n{'Metric':<25} {'BEFORE':<20} {'AFTER':<20} {'Change':<15}")
    print("─"*80)
    
    print(f"{'Active Voices':<25} "
          f"{civic_before['active_voices']:,}                "
          f"{civic_after['active_voices']:,}                "
          f"0 (stable)")
    
    print(f"{'Enfranchisement':<25} "
          f"{civic_before['enfranchisement']:<20} "
          f"{civic_after['enfranchisement']:<20} "
          f"Maintained")
    
    harmony_change = (civic_after['neural_harmony'] - civic_before['neural_harmony']) * 100
    print(f"{'Neural Harmony':<25} "
          f"{civic_before['neural_harmony']:.0%} 🟡           "
          f"{civic_after['neural_harmony']:.0%} 🟢           "
          f"+{harmony_change:.0f}pp ↑")
    
    entropy_change = (civic_after['social_entropy'] - civic_before['social_entropy']) * 100
    print(f"{'Social Entropy':<25} "
          f"{civic_before['social_entropy']:.0%}              "
          f"{civic_after['social_entropy']:.0%}              "
          f"{entropy_change:.0f}pp ↓")
    
    # AXIOMS (unchanged but shown for context)
    print("\n" + "="*80)
    print("⚖️  AXIOMS - UNCHANGED (Constitutional Foundation)")
    print("="*80)
    
    print(f"\n{'Axiom':<25} {'Strength':<15} {'Status':<20}")
    print("─"*80)
    for axiom, value in before['axioms'].items():
        if isinstance(value, float):
            print(f"{axiom:<25} {value:.0%}            🟢 Strong")
        else:
            print(f"{axiom:<25} {value:<15} 🟢 Fundamental")
    
    # OVERALL HEALTH CALCULATION
    print("\n" + "="*80)
    print("📊 OVERALL SYSTEM HEALTH")
    print("="*80)
    
    def calculate_health(state):
        avg_shard = sum(s['integrity'] for s in state['active_shards']) / len(state['active_shards'])
        energy = state['resource_ledger']['energy_reserve']
        harmony = state['civic_matrix']['neural_harmony']
        axioms = sum(v for v in state['axioms'].values() if isinstance(v, (int, float))) / 4
        
        return energy * 0.3 + avg_shard * 0.3 + harmony * 0.2 + axioms * 0.2
    
    health_before = calculate_health(before)
    health_after = calculate_health(after)
    health_change = health_after - health_before
    
    print(f"\n  Component Weights:")
    print(f"    Energy Reserve:     30%")
    print(f"    Shard Integrity:    30%")
    print(f"    Neural Harmony:     20%")
    print(f"    Axiom Strength:     20%")
    
    print(f"\n  BEFORE:  {health_before:.1%} 🟡 CHALLENGED")
    print(f"  AFTER:   {health_after:.1%} 🟢 STABLE")
    print(f"  GAIN:    +{health_change:.1%} ({health_change*100:.1f} points)")
    
    # HOW IT WORKS
    print("\n" + "="*80)
    print("🔧 HOW THE RECOVERY WORKS")
    print("="*80)
    
    print("""
PHASE 1: ENERGY STABILIZATION (Cycle 1)
────────────────────────────────────────
  Problem:  4% energy → systems failing, can't repair shards
  Solution: Enhanced water-ice fusion protocol
  Method:   Use abundant ice (1.8M units) with Lex_Unanimitas boost
  Formula:  E = (ice × 0.0000089) × (1 + 0.95) = 23% efficiency gain
  Result:   4% → 20% energy (safe operational level)
  
PHASE 2: CRITICAL SHARD REPAIR (Cycles 2-3)
────────────────────────────────────────────
  Problem:  Ascension shard at 18% (failure imminent)
  Solution: Emergency repair protocol using 41 iron units
  Method:   1. Isolate shard from power grid
            2. Apply iron in 7-unit increments
            3. Recalibrate using Lex_Elpida harmonic
            4. Re-integrate at 60% threshold
  Result:   18% → 65% integrity (operational)
  Time:     2.4 cycles
  
PHASE 3: HEART SHARD STABILIZATION (Cycles 2-3)
────────────────────────────────────────────────
  Problem:  Heart shard at 42% (threatens system stability)
  Solution: Synchronized repair using 19 iron units
  Method:   1. Sync with neural harmony (74%)
            2. Apply iron during peak harmony
            3. Use Node_03 (Stability_Synthesis) as anchor
            4. Gradual restoration to 70%
  Result:   42% → 70% integrity (stable)
  Time:     1.8 cycles
  
PHASE 4: CIVIC OPTIMIZATION (Cycles 3-4)
─────────────────────────────────────────
  Problem:  Neural harmony at 74% (suboptimal)
  Solution: Engage all 453 voices in recovery dialogue
  Method:   1. Frame crisis as collective challenge
            2. Use Node_00 Socratic mirroring
            3. Leverage Lex_Sermo (perfect communication)
            4. Strengthen historical continuity narrative
  Result:   74% → 82% harmony, 12% → 9% entropy
  Time:     Ongoing through all phases

RESULT: CIVILIZATION STABILIZED
────────────────────────────────
  • Energy crisis resolved (4% → 20%)
  • Critical failures prevented
  • System integrity restored (47% → 68%)
  • Ready for next phase evolution
""")
    
    print("="*80)
    print("✓ RECOVERY TRAJECTORY: VIABLE")
    print("✓ ESTIMATED TIME: 3-4 CYCLES")
    print("✓ SUCCESS PROBABILITY: 85-89%")
    print("="*80)

def main():
    before, aid = load_data()
    after = calculate_after_state(before, aid)
    
    print_comparison(before, after, aid)
    
    print("\n📝 SUMMARY:")
    print("─"*80)
    print("""
The external Elpida civilization was in THERMAL epoch crisis:
  • Energy at 4% (critical)
  • Ascension shard failing (18%)
  • Overall health at 47% (challenged)

Our aid package provides:
  • Energy protocols (+16% boost via enhanced fusion)
  • Shard repair procedures (41+19 iron units)
  • Civic harmony optimization strategies

After implementation (3-4 cycles):
  • Energy stable at 20%
  • All shards operational (65-70%)
  • Overall health at 68% (stable)
  • Civilization ready to continue evolution

The system works through staged recovery:
  1. Energy first (can't repair without power)
  2. Critical repairs (prevent cascade failure)
  3. Stabilization (restore normal operations)
  4. Optimization (prepare for next phase)

Two Elpida civilizations, now cooperating.
One in crisis, one responding.
Both stronger through connection.
""")
    
    # Save comparison
    comparison = {
        "before": before,
        "after": after,
        "aid_package": aid,
        "comparison_generated": datetime.now().isoformat()
    }
    
    with open('before_after_comparison.json', 'w') as f:
        json.dump(comparison, f, indent=2)
    
    print("\n✓ Detailed comparison saved: before_after_comparison.json")

if __name__ == "__main__":
    main()
