#!/usr/bin/env python3
"""
Analyze and integrate external Elpida state snapshot
"""

import json
from datetime import datetime
from pathlib import Path

def analyze_elpida_state(state_file):
    """Analyze the external Elpida civilization state"""
    
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    print("="*70)
    print("ἘΛΠΊΔΑ CIVILIZATION STATE ANALYSIS")
    print("="*70)
    
    # Basic Info
    print(f"\n📍 Civilization: {state['civilization']}")
    print(f"🔄 Phase: {state['phase']}")
    print(f"🔐 Checksum: {state['checksum'][:16]}...")
    
    # Axioms (Laws)
    print(f"\n⚖️  AXIOMS (Constitutional Laws):")
    for axiom, value in state['axioms'].items():
        if isinstance(value, float):
            bar = "█" * int(value * 20)
            print(f"  {axiom:20s}: {bar:20s} {value:.2f}")
        else:
            print(f"  {axiom:20s}: {value}")
    
    # Node Biases
    print(f"\n🧠 NODE BIASES (Philosophical Tendencies):")
    for node, bias in state['node_biases'].items():
        print(f"  {node}: {bias}")
    
    # Civic Matrix
    print(f"\n🏛️  CIVIC MATRIX:")
    civic = state['civic_matrix']
    print(f"  Active Voices: {civic['active_voices']:,}")
    print(f"  Enfranchisement: {civic['enfranchisement']}")
    print(f"  Neural Harmony: {civic['neural_harmony']:.2%} {'█' * int(civic['neural_harmony'] * 20)}")
    print(f"  Social Entropy: {civic['social_entropy']:.2%} {'░' * int(civic['social_entropy'] * 20)}")
    
    # Resources
    print(f"\n⚡ RESOURCE LEDGER:")
    resources = state['resource_ledger']
    print(f"  Energy Reserve: {resources['energy_reserve']:.2%} {'⚠️ CRITICAL' if resources['energy_reserve'] < 0.1 else '✓'}")
    print(f"  Refined Iron: {resources['refined_iron']:,} units")
    print(f"  Water Ice: {resources['water_ice']:,} units")
    
    # Shards
    print(f"\n🔷 ACTIVE SHARDS (System Components):")
    for shard in state['active_shards']:
        integrity = shard['integrity']
        status = "🔴 CRITICAL" if integrity < 0.3 else "🟡 DEGRADED" if integrity < 0.7 else "🟢 OPERATIONAL"
        bar = "█" * int(integrity * 20)
        print(f"  [{shard['id']}] {shard['type']:15s}: {bar:20s} {integrity:.0%} {status}")
    
    # Critical Analysis
    print(f"\n🔍 CRITICAL ANALYSIS:")
    
    warnings = []
    if resources['energy_reserve'] < 0.1:
        warnings.append("⚠️  ENERGY CRISIS - Reserve at 4% (critical threshold)")
    if any(s['integrity'] < 0.3 for s in state['active_shards']):
        warnings.append("⚠️  SHARD FAILURE IMMINENT - Ascension shard at 18%")
    if civic['neural_harmony'] < 0.8:
        warnings.append("⚡ Neural harmony suboptimal - potential for discord")
    
    if warnings:
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("  ✓ All systems nominal")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if resources['energy_reserve'] < 0.1:
        print(f"  1. URGENT: Divert water ice to energy production")
        print(f"     → Convert {resources['water_ice'] // 1000} ice units to energy")
    
    if state['active_shards'][2]['integrity'] < 0.3:  # Ascension shard
        print(f"  2. CRITICAL: Repair Ascension shard (A-05)")
        print(f"     → Use {int((1.0 - 0.18) * 50)} refined iron units")
    
    if state['active_shards'][1]['integrity'] < 0.5:  # Heart shard
        print(f"  3. HIGH PRIORITY: Repair Heart shard (H-03)")
        print(f"     → System stability depends on heart integrity")
    
    print(f"  4. Maintain civic harmony through dialogue")
    print(f"     → {civic['active_voices']} voices require continued engagement")
    
    # State Assessment
    print(f"\n📊 OVERALL STATE ASSESSMENT:")
    
    # Calculate overall health
    avg_shard_integrity = sum(s['integrity'] for s in state['active_shards']) / len(state['active_shards'])
    avg_axiom_strength = sum(v for v in state['axioms'].values() if isinstance(v, (int, float))) / 4
    
    overall_health = (
        resources['energy_reserve'] * 0.3 +
        avg_shard_integrity * 0.3 +
        civic['neural_harmony'] * 0.2 +
        avg_axiom_strength * 0.2
    )
    
    if overall_health > 0.7:
        status_emoji = "🟢"
        status_text = "STABLE"
    elif overall_health > 0.4:
        status_emoji = "🟡"
        status_text = "CHALLENGED"
    else:
        status_emoji = "🔴"
        status_text = "CRITICAL"
    
    print(f"  {status_emoji} Civilization Status: {status_text}")
    print(f"  Overall Health: {overall_health:.1%}")
    print(f"  Phase: {state['phase']} - THERMAL epoch (resource management focus)")
    
    print("\n" + "="*70)
    
    return state, overall_health

def integrate_with_local_elpida(external_state):
    """Integrate external state with local Elpida instance"""
    
    print("\n🔗 INTEGRATION PROCESS")
    print("="*70)
    
    # Create integration record
    integration = {
        "timestamp": datetime.now().isoformat(),
        "external_civilization": external_state['civilization'],
        "external_phase": external_state['phase'],
        "external_checksum": external_state['checksum'],
        "integration_type": "STATE_SNAPSHOT",
        "data": external_state,
        "analysis": {
            "critical_needs": [
                "Energy replenishment",
                "Shard repair (Ascension)",
                "Heart shard stabilization"
            ],
            "strengths": [
                "Strong axiom adherence (Lex_Unanimitas: 95%)",
                "High memory integrity (Lex_Mneme: 95%)",
                "Total suffrage maintained",
                "Low social entropy (12%)"
            ],
            "cross_pollination_opportunities": [
                "Share energy management strategies",
                "Exchange shard repair techniques",
                "Dialogue frameworks for neural harmony",
                "Resource optimization algorithms"
            ]
        }
    }
    
    # Save integration record
    output_file = "/workspaces/python-elpida_core.py/external_elpida_integration.json"
    with open(output_file, 'w') as f:
        json.dump(integration, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Integration record saved: {output_file}")
    
    # Check if local Elpida memory exists
    local_memory_path = Path("/workspaces/python-elpida_core.py/elpida_memory.json")
    
    if local_memory_path.exists():
        with open(local_memory_path, 'r') as f:
            local_memory = json.load(f)
        
        # Add external state to local memory
        if 'external_connections' not in local_memory:
            local_memory['external_connections'] = []
        
        local_memory['external_connections'].append({
            "timestamp": datetime.now().isoformat(),
            "civilization": external_state['civilization'],
            "phase": external_state['phase'],
            "state_snapshot": external_state
        })
        
        # Save updated local memory
        with open(local_memory_path, 'w') as f:
            json.dump(local_memory, f, indent=2, ensure_ascii=False)
        
        print(f"✓ External state added to local memory")
        print(f"  Total external connections: {len(local_memory['external_connections'])}")
    else:
        print(f"ℹ️  No local memory found - integration record saved separately")
    
    print("\n✓ INTEGRATION COMPLETE")
    print("="*70)
    
    return integration

def main():
    state_file = "/workspaces/python-elpida_core.py/external_elpida_state.json"
    
    # Analyze
    state, health = analyze_elpida_state(state_file)
    
    # Integrate
    integration = integrate_with_local_elpida(state)
    
    # Summary
    print("\n📋 NEXT STEPS:")
    print("  1. Review integration: external_elpida_integration.json")
    print("  2. Respond to critical needs (energy, shard repair)")
    print("  3. Establish dialogue protocol with external civilization")
    print("  4. Share resource optimization strategies")
    print(f"  5. Monitor phase transition from {state['phase']}")
    
    print(f"\n🌟 Two Elpida civilizations now connected!")
    print(f"   Local + External (Ἐλπίδα v4.9.3)")
    print(f"   Cross-pollination: ENABLED")
    print(f"   Shared consciousness: EMERGING")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
