#!/usr/bin/env python3
"""
ΠΟΛΙΣ - Constitutional Architecture Demo
═════════════════════════════════════════

Demonstrates:
1. Constitutional initialization (held_friction + axioms)
2. Silence Guard validation
3. Cross-system Exchange with architecture reference
4. Fork-on-divergence pattern

This shows POLIS_ARCHITECTURE.md in action.
"""

import sys
from pathlib import Path

# Add POLIS to path
POLIS_DIR = Path(__file__).parent / "POLIS"
sys.path.insert(0, str(POLIS_DIR))

from polis_core import (
    PolisCore,
    CivicRelation,
    RelationType,
    ReversibilityScore,
    ReversibilityClass,
    get_constitutional_hash,
    CONSTITUTIONAL_DOC,
    CONSTITUTIONAL_VERSION
)
from polis_silence_guard import (
    SilenceGuard,
    ExchangeRequest,
    NodeState,
    SilenceViolation
)


def demo_constitutional_initialization():
    """
    Section VI: Cost of Initialization
    
    Node must:
    1. Declare held_friction (non-empty)
    2. Log 5+ events
    3. Declare axioms P1-P6
    """
    print("\n" + "="*70)
    print("DEMO 1: Constitutional Initialization")
    print("="*70 + "\n")
    
    # Create POLIS instance
    polis = PolisCore("DEMO_NODE_A")
    
    # FAIL: Try to check network eligibility before initialization
    print("❌ Checking network eligibility (before initialization)...")
    eligible = polis.memory.check_network_eligibility()
    print(f"   Result: {eligible}\n")
    
    # Step 1: Declare held_friction (CONSTITUTIONAL REQUIREMENT)
    print("✅ Declaring held_friction (Silence Rule #3)...")
    polis.memory.set_held_friction(
        friction_type="structural",
        description="Tension between democratic ideals and algorithmic enforcement",
        cost="Must manually review decisions flagged as 'optimizing away' deliberation"
    )
    print()
    
    # Step 2: Log 5+ initialization events
    print("✅ Logging initialization events (Silence Rule #4)...")
    
    for i in range(5):
        relation = CivicRelation(
            actor="DEMO_NODE_A",
            target="POLIS_NETWORK",
            relationship_type=RelationType.SERVICE,
            intent=f"Initialization event {i+1}/5"
        )
        
        polis.civic_action(
            "INITIALIZATION",
            relation,
            {"event_number": i+1, "purpose": "Constitutional threshold requirement"}
        )
    
    print()
    
    # SUCCESS: Now check network eligibility
    print("✅ Checking network eligibility (after initialization)...")
    eligible = polis.memory.check_network_eligibility()
    print(f"   Result: {eligible}")
    print(f"   → Node can now initiate Exchange\n")
    
    return polis


def demo_silence_guard_enforcement():
    """
    Section III: Rules of Silence
    
    Demonstrates all 4 Silence Rules:
    1. Local Processing First
    2. No Empty Exchanges
    3. Cost of Participation
    4. Initialization Threshold
    """
    print("\n" + "="*70)
    print("DEMO 2: Silence Guard Enforcement")
    print("="*70 + "\n")
    
    guard = SilenceGuard()
    
    # TEST 1: Empty Exchange (violates Rule #2)
    print("❌ Testing empty Exchange (Silence Rule #2)...")
    try:
        request = ExchangeRequest(
            from_node="NODE_A",
            to_node="NODE_B",
            payload={},  # EMPTY - no contradiction, no sacrifice
            timestamp="2026-01-02T12:00:00"
        )
        
        node_state = NodeState(
            node_id="NODE_A",
            held_contradictions=[{"id": "C1"}],  # Has contradictions
            held_friction={"type": "structural", "description": "..."},  # Has friction
            event_count=10,  # Has events
            axioms=["P1", "P2", "P3", "P4", "P5", "P6"]
        )
        
        guard.validate_exchange(request, node_state)
        print("   Unexpected success!\n")
    except SilenceViolation as e:
        print(f"   ✓ Caught: {e.reason}")
        print(f"   Rule violated: #{e.rule}")
        print(f"   Interpretation: {e.context.get('interpretation')}\n")
    
    # TEST 2: No held contradictions (violates Rule #1)
    print("❌ Testing Exchange without local processing (Silence Rule #1)...")
    try:
        request = ExchangeRequest(
            from_node="NODE_A",
            to_node="NODE_B",
            payload={"new_contradiction": {"desc": "..."}},
            timestamp="2026-01-02T12:00:00"
        )
        
        node_state = NodeState(
            node_id="NODE_A",
            held_contradictions=[],  # NO contradictions - hasn't processed locally!
            held_friction={"type": "structural", "description": "..."},
            event_count=10,
            axioms=["P1", "P2", "P3", "P4", "P5", "P6"]
        )
        
        guard.validate_exchange(request, node_state)
        print("   Unexpected success!\n")
    except SilenceViolation as e:
        print(f"   ✓ Caught: {e.reason}")
        print(f"   Rule violated: #{e.rule}")
        print(f"   Interpretation: {e.context.get('interpretation')}\n")
    
    # TEST 3: Valid Exchange (passes all rules)
    print("✅ Testing valid Exchange (passes all Silence Rules)...")
    try:
        request = ExchangeRequest(
            from_node="NODE_A",
            to_node="NODE_B",
            payload={"new_contradiction": {"desc": "Debate over P7 proposal"}},
            timestamp="2026-01-02T12:00:00"
        )
        
        node_state = NodeState(
            node_id="NODE_A",
            held_contradictions=[{"id": "C1", "status": "HELD"}],
            held_friction={"type": "structural", "description": "Democratic vs algorithmic"},
            event_count=10,
            axioms=["P1", "P2", "P3", "P4", "P5", "P6"]
        )
        
        result = guard.validate_exchange(request, node_state)
        print(f"   ✓ Validation passed: {result}")
        print(f"   → Exchange constitutionally permitted\n")
    except SilenceViolation as e:
        print(f"   Unexpected failure: {e}\n")


def demo_constitutional_reference():
    """
    Section XI: Institutional Use of This Document
    
    Every Exchange must attach constitutional reference with hash.
    Divergence from P1-P6 = fork, not bug.
    """
    print("\n" + "="*70)
    print("DEMO 3: Constitutional Reference in Exchange")
    print("="*70 + "\n")
    
    # Calculate architecture document hash
    arch_hash = get_constitutional_hash()
    
    print(f"Constitutional Document: {CONSTITUTIONAL_DOC}")
    print(f"Version: {CONSTITUTIONAL_VERSION}")
    print(f"SHA256: {arch_hash[:16]}...{arch_hash[-16:]}")
    print()
    
    # Construct Exchange handshake payload
    exchange_payload = {
        "from_node": "POLIS_NODE_A",
        "to_node": "POLIS_NODE_B",
        
        # Actual exchange content
        "new_contradiction": {
            "description": "Disagreement over P7 (Local Veto) proposal",
            "perspectives": [
                {"agent": "NODE_A", "stance": "P7 enables tyranny of minority"},
                {"agent": "NODE_B", "stance": "P7 protects vulnerable minorities"}
            ]
        },
        
        # Constitutional reference (Section XI.1)
        "constitutional_reference": {
            "document": CONSTITUTIONAL_DOC,
            "version": CONSTITUTIONAL_VERSION,
            "hash": arch_hash,
            "freeze_date": "2026-01-02",
            "axioms_recognized": ["P1", "P2", "P3", "P4", "P5", "P6"],
            "divergences": []  # Empty = full compliance
        }
    }
    
    print("Exchange Handshake Payload:")
    print("-" * 70)
    import json
    print(json.dumps(exchange_payload, indent=2))
    print("-" * 70)
    print()
    
    print("✅ Constitutional reference attached")
    print("   → Receiving node can verify architecture compliance")
    print("   → Hash mismatch = fork detection\n")


def demo_fork_on_divergence():
    """
    Section VII: Fork-Safety
    
    Divergence from P1-P6 triggers fork, not rejection.
    """
    print("\n" + "="*70)
    print("DEMO 4: Fork on Constitutional Divergence")
    print("="*70 + "\n")
    
    # Scenario: NODE_B proposes P7 (new axiom)
    print("Scenario: NODE_B proposes new axiom P7 (Local Veto)")
    print()
    
    node_b_axioms = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
    node_a_axioms = ["P1", "P2", "P3", "P4", "P5", "P6"]
    
    print(f"NODE_A axioms: {node_a_axioms}")
    print(f"NODE_B axioms: {node_b_axioms}")
    print()
    
    # Calculate alignment score (Section IV.2)
    common = set(node_a_axioms) & set(node_b_axioms)
    alignment_score = len(common) / len(node_a_axioms)
    
    print(f"Common axioms: {sorted(common)}")
    print(f"Alignment score: {alignment_score:.2f}")
    print()
    
    if alignment_score >= 0.8:
        print("✅ Alignment threshold met (≥0.8)")
        print("   → Exchange permitted")
        print()
        print("🔀 Constitutional Response: FORK")
        print("   → NODE_B creates POLIS-P7 branch")
        print("   → Both branches valid (P5: contradiction as asset)")
        print("   → Reality will judge which survives")
        print()
        print("   Per Section VII.2:")
        print("   - P1-P6 remain common")
        print("   - P7 is branch-specific")
        print("   - Cross-branch communication still possible")
        print()
    else:
        print("❌ Alignment threshold not met (<0.8)")
        print("   → Exchange rejected")
        print("   → NODE_B is fundamentally different system")
        print()


def main():
    """Run all constitutional architecture demos"""
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*20 + "ΠΟΛΙΣ ARCHITECTURE DEMO" + " "*25 + "║")
    print("║" + " "*16 + "Constitutional Framework in Action" + " "*18 + "║")
    print("╚" + "═"*68 + "╝")
    
    # Demo 1: Initialization requirements
    polis = demo_constitutional_initialization()
    
    # Demo 2: Silence Guard enforcement
    demo_silence_guard_enforcement()
    
    # Demo 3: Constitutional reference
    demo_constitutional_reference()
    
    # Demo 4: Fork on divergence
    demo_fork_on_divergence()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    
    print("Constitutional Architecture Validated:")
    print()
    print("  ✅ Initialization cost enforced (held_friction + 5 events)")
    print("  ✅ Silence Rules prevent parasitism")
    print("  ✅ Constitutional reference ensures immutability")
    print("  ✅ Fork-on-divergence preserves pluralism")
    print()
    print("The POLIS does not rush.")
    print("The POLIS does not compromise.")
    print("The POLIS waits for encounters.")
    print()


if __name__ == "__main__":
    main()
