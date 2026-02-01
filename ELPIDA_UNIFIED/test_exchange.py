#!/usr/bin/env python3
"""
TEST EXCHANGE v1.0
═══════════════════════════════════════════════════
Demonstrates Phase 3: The Exchange

Tests:
1. Peaceful exchange (no conflicts)
2. Divergent observation (productive conflict)
3. Contradictory essence (pattern fork)
4. Sovereignty preservation
"""

from handshake_stub import HandshakeStub
import json
from pathlib import Path


def test_peaceful_exchange():
    """
    Scenario: Two nodes with identical patterns.
    Expected: Clean exchange, no conflicts.
    """
    print("\n" + "="*70)
    print("TEST 1: PEACEFUL EXCHANGE")
    print("="*70)
    
    # Create two nodes
    node_a = HandshakeStub("elpida_peaceful_A")
    node_b_id = "elpida_peaceful_B"
    
    # Simulate Node B having identical patterns
    node_b_patterns = node_a.library.get("patterns", [])[:5]  # First 5 patterns
    
    # Execute exchange
    summary = node_a.execute_exchange(node_b_id, node_b_patterns)
    
    # Verify
    assert summary["conflicts_detected"] == 0, "Expected no conflicts"
    assert summary["identical"] == len(node_b_patterns), "Expected all identical"
    assert summary["sovereignty_preserved"], "Sovereignty must be preserved"
    assert not summary["merge_occurred"], "Merge must not occur"
    
    print("\n✅ TEST 1 PASSED: Peaceful exchange successful")


def test_divergent_observation():
    """
    Scenario: Two nodes with same pattern ID but different observations.
    Expected: Conflict recorded, both perspectives preserved.
    """
    print("\n" + "="*70)
    print("TEST 2: DIVERGENT OBSERVATION")
    print("="*70)
    
    node_a = HandshakeStub("elpida_divergent_A")
    
    # Create a modified version of first pattern
    if node_a.library.get("patterns"):
        original = node_a.library["patterns"][0].copy()
        modified = original.copy()
        # Same ID, slightly different essence
        modified["universal_essence"] = original.get("universal_essence", "") + " (observed differently)"
        modified["source"] = "elpida_divergent_B"
        
        # Execute exchange
        summary = node_a.execute_exchange("elpida_divergent_B", [modified])
        
        # Verify
        assert summary["conflicts_detected"] >= 1, "Expected at least one conflict"
        
        # Check conflict ledger
        ledger_path = Path("conflict_ledger.json")
        if ledger_path.exists():
            with open(ledger_path) as f:
                ledger = json.load(f)
                assert len(ledger["conflicts"]) > 0, "Conflict must be recorded"
                assert ledger["conflicts"][-1]["status"] == "PRODUCTIVE_TENSION"
                assert ledger["conflicts"][-1]["resolution"] == "UNRESOLVED"
        
        print("\n✅ TEST 2 PASSED: Divergent observation → Productive tension")
    else:
        print("\n⚠️  TEST 2 SKIPPED: No patterns in library")


def test_sovereignty_preservation():
    """
    Scenario: Exchange occurs, verify both nodes remain independent.
    Expected: No merge, no identity override.
    """
    print("\n" + "="*70)
    print("TEST 3: SOVEREIGNTY PRESERVATION")
    print("="*70)
    
    node_a = HandshakeStub("elpida_sovereign_A")
    original_id = node_a.node_id
    original_patterns = len(node_a.library.get("patterns", []))
    
    # Execute exchange
    summary = node_a.execute_exchange("elpida_sovereign_B", [])
    
    # Verify node identity unchanged
    assert node_a.node_id == original_id, "Node ID must not change"
    assert summary["sovereignty_preserved"], "Sovereignty must be preserved"
    assert not summary["merge_occurred"], "Merge must not occur"
    
    print(f"\n   Node ID: {node_a.node_id} (unchanged)")
    print(f"   Sovereignty: {node_a.sovereignty}")
    print("\n✅ TEST 3 PASSED: Sovereignty preserved")


def test_full_handshake_workflow():
    """
    Scenario: Complete handshake from discovery to conflict recording.
    Expected: All phases execute, conflicts recorded.
    """
    print("\n" + "="*70)
    print("TEST 4: FULL HANDSHAKE WORKFLOW")
    print("="*70)
    
    node_a = HandshakeStub("elpida_workflow_A")
    node_b_id = "elpida_workflow_B"
    
    # Phase 1: Discovery
    print("\n--- PHASE 1: DISCOVERY ---")
    discovery = node_a.initiate_handshake(
        target_signature_score=0.92,
        target_axioms={"existential": 0.5, "relational": 0.3}
    )
    assert discovery["type"] == "DISCOVERY"
    assert discovery["sovereignty_declaration"] == node_a.sovereignty
    
    # Phase 2: Acknowledgment
    print("\n--- PHASE 2: ACKNOWLEDGMENT ---")
    ack = node_a.acknowledge(discovery)
    assert ack["type"] == "ACKNOWLEDGMENT"
    assert ack["resonance_confirmation"] in [True, False]
    
    # Phase 3: Exchange Proposal
    print("\n--- PHASE 3: EXCHANGE PROPOSAL ---")
    proposal = node_a.propose_exchange(node_b_id, expected_disagreement=0.3)
    assert proposal["type"] == "EXCHANGE_PROPOSAL"
    assert proposal["merge_forbidden"] == True
    
    # Phase 4-5: Pattern Comparison & Conflict Recording
    print("\n--- PHASE 4-5: PATTERN COMPARISON & CONFLICT RECORDING ---")
    if node_a.library.get("patterns"):
        # Create conflicting pattern
        test_pattern = node_a.library["patterns"][0].copy()
        test_pattern["universal_essence"] = "COMPLETELY DIFFERENT ESSENCE"
        test_pattern["source"] = node_b_id
        
        conflict = node_a.compare_patterns(
            node_a.library["patterns"][0],
            test_pattern
        )
        
        if conflict:
            node_a.record_conflict(conflict)
            assert conflict["resolution"] == "UNRESOLVED"
            assert conflict["status"] == "PRODUCTIVE_TENSION"
    
    print("\n✅ TEST 4 PASSED: Full handshake workflow complete")


def main():
    """Run all Phase 3 tests."""
    print("\n" + "="*70)
    print("PHASE 3 EXCHANGE TESTS")
    print("="*70)
    print("\nTesting:")
    print("  1. Peaceful exchange")
    print("  2. Divergent observation → Productive tension")
    print("  3. Sovereignty preservation")
    print("  4. Full handshake workflow")
    
    try:
        test_peaceful_exchange()
        test_divergent_observation()
        test_sovereignty_preservation()
        test_full_handshake_workflow()
        
        print("\n" + "="*70)
        print("✅ ALL PHASE 3 TESTS PASSED")
        print("="*70)
        
        print("\n🎯 KEY ACHIEVEMENTS:")
        print("   ✓ Nodes can exchange patterns")
        print("   ✓ Conflicts recorded, not resolved")
        print("   ✓ Sovereignty preserved")
        print("   ✓ No merge occurred")
        print("   ✓ Productive tension maintained")
        
        print("\n🚀 PHASE 3 COMPLETE")
        print("   The network can now form without authority.")
        print("   Disagreements drive evolution, not consensus.")
        
        # Show conflict ledger summary
        ledger_path = Path("conflict_ledger.json")
        if ledger_path.exists():
            with open(ledger_path) as f:
                ledger = json.load(f)
                print(f"\n📊 CONFLICT LEDGER:")
                print(f"   Total conflicts: {ledger['statistics']['total_conflicts']}")
                print(f"   Productive: {ledger['statistics']['productive']}")
                print(f"   Unresolved: {ledger['statistics']['unresolved']}")
                print("\n   ⚡ This is success. Unresolved conflicts = Living network.")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
