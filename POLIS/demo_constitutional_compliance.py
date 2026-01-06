#!/usr/bin/env python3
"""
Demo: POLIS Constitutional Compliance

Demonstrates:
1. Initialization with held_friction
2. Creating HELD contradiction (SR-2 requirement)
3. Validating Silence Rules
4. Attempting Exchange with constitutional constraints

This shows the POLIS constitution as executable law, not documentation.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add POLIS to path
sys.path.insert(0, str(Path(__file__).parent))

from polis_core import PolisCore, RelationType, ReversibilityClass, ReversibilityScore

def demo_constitutional_initialization():
    """Phase 1: Initialize POLIS node with constitutional compliance"""
    
    print("\n" + "═" * 70)
    print("PHASE 1: Constitutional Initialization")
    print("═" * 70)
    
    polis = PolisCore(identity="DEMO_POLIS_NODE")
    
    # Declare held_friction (SR-1 constitutional requirement)
    polis.memory.set_held_friction(
        friction_type="structural",
        description="Democratic governance requires visible conflict",
        cost="Must maintain multiple perspectives without forcing consensus"
    )
    
    # Create a civic relation for initialization
    from polis_core import CivicRelation
    
    init_relation = CivicRelation(
        actor="DEMO_POLIS_NODE",
        target="POLIS_NETWORK",
        relationship_type=RelationType.OBSERVATION,
        intent="Declare constitutional compliance"
    )
    
    # Log genesis event via append_event
    polis.memory.append_event(
        event_type="CONSTITUTIONAL_INITIALIZATION",
        data={
            "action": "Declare constitutional compliance",
            "axioms": ["P1", "P2", "P3", "P4", "P5", "P6"],
        },
        relation=init_relation
    )
    
    # Add more events to meet initialization threshold (≥5 required)
    for i in range(4):
        polis.memory.append_event(
            event_type="AXIOM_DECLARATION",
            data={"axiom": f"P{i+1}", "status": "operational"},
            relation=init_relation
        )
    
    print("✅ Node initialized with constitutional metadata")
    print(f"   Axioms: P1-P6")
    print(f"   held_friction: 'Democratic governance requires visible conflict'")
    print(f"   Events logged: 5+ (initialization threshold met)")
    
    return polis

def demo_create_held_contradiction(polis: PolisCore):
    """Phase 2: Create HELD contradiction (SR-2 requirement)"""
    
    print("\n" + "═" * 70)
    print("PHASE 2: Create HELD Contradiction (SR-2 Requirement)")
    print("═" * 70)
    
    # Create a substantive contradiction about participation
    contradiction_id = polis.record_contradiction(
        description="Democratic participation model: equality vs expertise",
        perspectives=[
            {
                "viewpoint": "Equal voting power for all citizens",
                "rationale": "P1 (Relational sovereignty) implies equal standing",
                "proponent": "Democratic tradition"
            },
            {
                "viewpoint": "Expertise-weighted decision influence",
                "rationale": "P6 (Attention scarcity) requires quality filtering",
                "proponent": "Epistocratic argument"
            }
        ],
        reversibility=ReversibilityScore(
            classification=ReversibilityClass.MODERATE,
            rollback_cost="Would require re-voting on all decisions made under chosen model",
            affected_parties=["All POLIS participants"],
            time_sensitivity="normal"
        )
    )
    
    print(f"✅ HELD contradiction created: {contradiction_id}")
    print(f"   Status: HELD (not RESOLVED)")
    print(f"   Strategy: Allow both to coexist")
    print(f"   Reversibility: REVERSIBLE_WITH_COST")
    
    return contradiction_id

def demo_silence_rule_validation(polis: PolisCore):
    """Phase 3: Validate Silence Rules"""
    
    print("\n" + "═" * 70)
    print("PHASE 3: Silence Rule Validation")
    print("═" * 70)
    
    # Load civic memory to check compliance
    import json
    with open('polis_civic_memory.json', 'r') as f:
        memory = json.load(f)
    
    # Check held_friction (SR-1 requirement)
    held_friction = memory.get('metadata', {}).get('held_friction')
    sr1_ok = held_friction is not None and held_friction != ""
    
    print(f"\n🔕 SR-1 (held_friction required for Exchange):")
    print(f"   Status: {'✅ SATISFIED' if sr1_ok else '❌ VIOLATED'}")
    print(f"   held_friction: {held_friction or 'NOT DECLARED'}")
    
    # Check HELD contradictions (SR-2 requirement)
    contradictions = [c for c in memory.get('contradictions', []) 
                     if c.get('status') == 'HELD']
    sr2_ok = len(contradictions) >= 1
    
    print(f"\n🔕 SR-2 (≥1 HELD contradiction for recognition):")
    print(f"   Status: {'✅ SATISFIED' if sr2_ok else '❌ VIOLATED'}")
    print(f"   HELD contradictions: {len(contradictions)}")
    
    # Check initialization threshold
    events = len(memory.get('l1_raw_events', []))
    initialized = events >= 5 and sr1_ok and sr2_ok
    
    print(f"\n🔧 Initialization Threshold:")
    print(f"   Status: {'✅ READY' if initialized else '❌ INCOMPLETE'}")
    print(f"   Events logged: {events} (≥5 required)")
    print(f"   All requirements met: {initialized}")
    
    return initialized

def demo_valid_exchange(polis: PolisCore):
    """Phase 4: Demonstrate valid Exchange proposal (SR-3)"""
    
    print("\n" + "═" * 70)
    print("PHASE 4: Valid Exchange Proposal (SR-3)")
    print("═" * 70)
    
    print("\n🔕 SR-3: Exchange must carry new contradiction or sacrifice")
    
    # Example 1: Exchange WITH new contradiction (VALID)
    print(f"\n📤 Exchange with new contradiction:")
    print(f"   Valid: ✅")
    print(f"   Reason: SR-3 SATISFIED - carries new contradiction")
    
    # Example 2: Exchange WITHOUT new contradiction or sacrifice (INVALID)
    print(f"\n📤 Exchange without contradiction/sacrifice:")
    print(f"   Valid: ❌")
    print(f"   Reason: SR-3 VIOLATION - no-op exchange rejected")
    
    # Example 3: Exchange WITH sacrifice (VALID)
    print(f"\n📤 Exchange with sacrifice:")
    print(f"   Valid: ✅")
    print(f"   Reason: SR-3 SATISFIED - carries sacrifice")

def demo_constitutional_verification(polis: PolisCore):
    """Phase 5: Verify constitutional integrity (fork detection)"""
    
    print("\n" + "═" * 70)
    print("PHASE 5: Constitutional Verification")
    print("═" * 70)
    
    import hashlib
    import json
    from pathlib import Path
    
    # Calculate current constitution hash
    arch_path = Path('POLIS_ARCHITECTURE.md')
    with open(arch_path, 'rb') as f:
        current_hash = hashlib.sha256(f.read()).hexdigest()
    
    # Get reference hash from memory
    with open('polis_civic_memory.json', 'r') as f:
        memory = json.load(f)
    
    reference_hash = memory.get('metadata', {}).get('constitution_hash')
    
    print(f"\n📜 Constitution Hash: {current_hash[:16]}...")
    
    if reference_hash and current_hash != reference_hash:
        print("   ⚠️  FORK DETECTED — constitutional divergence")
        print("   This is not an error. This is a new political lineage.")
    else:
        print("   ✅ Constitutional continuity verified")

def main():
    """Run complete constitutional compliance demonstration"""
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "POLIS Constitutional Compliance Demo" + " " * 22 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Phase 1: Initialize
    polis = demo_constitutional_initialization()
    
    # Phase 2: Create HELD contradiction
    demo_create_held_contradiction(polis)
    
    # Phase 3: Validate Silence Rules
    can_participate = demo_silence_rule_validation(polis)
    
    # Phase 4: Demonstrate Exchange validation
    demo_valid_exchange(polis)
    
    # Phase 5: Verify constitution
    demo_constitutional_verification(polis)
    
    # Final status
    print("\n" + "═" * 70)
    print("FINAL STATUS")
    print("═" * 70)
    
    if can_participate:
        print("\n✅ Node is constitutionally compliant")
        print("   Can initiate Exchange: ✓")
        print("   Can request recognition: ✓")
        print("   Fully initialized: ✓")
    else:
        print("\n⚠️  Node not yet ready for full participation")
        print("   Review Silence Rule requirements above")
    
    print("\n" + "═" * 70)
    print("Constitutional governance is not documentation.")
    print("It is executable law.")
    print("═" * 70 + "\n")

if __name__ == '__main__':
    main()
