"""
TEST: GOVERNANCE ROUTING (Phase 7 + Phase 8 Integration)
----------------------------------------------------------
Demonstrates routing between:
- Single Brain (Phase 7) for routine decisions
- Council (Phase 8) for critical decisions

Tests the complete governance stack integration.
"""

import sys
import os

# Ensure POLIS path is accessible
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'POLIS'))

from polis_link import CivicLink

def print_header(text: str):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def test_governance_routing():
    """Test routing between Brain and Council based on criticality."""
    
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║            GOVERNANCE ROUTING TEST (Phase 7 + Phase 8)                  ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝\n")
    
    # Create two nodes: one using Brain only, one with Council enabled
    print(">> Creating test nodes...")
    node_brain_only = CivicLink("TEST_BRAIN_ONLY", "EXPERIMENTAL", use_council=False)
    node_with_council = CivicLink("TEST_WITH_COUNCIL", "EXPERIMENTAL", use_council=True)
    
    # ========================================================================
    # TEST 1: ROUTINE Action (Both should use Brain - fast path)
    # ========================================================================
    print_header("TEST 1: ROUTINE Action → Both use Brain (Phase 7)")
    
    action = "Log system metrics"
    intent = "Monitoring (serves: OPERATORS)"
    reversibility = "High (read-only)"
    
    print("\n[Brain-Only Node]")
    decision_1a = node_brain_only.request_action(
        action=action,
        intent=intent,
        reversibility=reversibility,
        criticality="ROUTINE"
    )
    print(f"   Governance Mode: {decision_1a['governance_mode']}")
    print(f"   Result: {decision_1a['approved']}")
    
    print("\n[Council-Enabled Node]")
    decision_1b = node_with_council.request_action(
        action=action,
        intent=intent,
        reversibility=reversibility,
        criticality="ROUTINE"  # Still uses Brain for routine
    )
    print(f"   Governance Mode: {decision_1b['governance_mode']}")
    print(f"   Result: {decision_1b['approved']}")
    
    # ========================================================================
    # TEST 2: NORMAL Action (Both use Brain by default)
    # ========================================================================
    print_header("TEST 2: NORMAL Action → Both use Brain (Phase 7)")
    
    action = "Update configuration file"
    intent = "System maintenance (serves: SYSTEM)"
    reversibility = "High (backup exists)"
    
    print("\n[Brain-Only Node]")
    decision_2a = node_brain_only.request_action(
        action=action,
        intent=intent,
        reversibility=reversibility,
        criticality="NORMAL"
    )
    print(f"   Governance Mode: {decision_2a['governance_mode']}")
    print(f"   Result: {decision_2a['approved']}")
    
    print("\n[Council-Enabled Node]")
    decision_2b = node_with_council.request_action(
        action=action,
        intent=intent,
        reversibility=reversibility,
        criticality="NORMAL"  # Still Brain for normal
    )
    print(f"   Governance Mode: {decision_2b['governance_mode']}")
    print(f"   Result: {decision_2b['approved']}")
    
    # ========================================================================
    # TEST 3: IMPORTANT Action (Council-enabled node uses Council)
    # ========================================================================
    print_header("TEST 3: IMPORTANT Action → Council engages (Phase 8)")
    
    action = "Migrate database to new schema"
    intent = "Performance improvement (serves: USERS)"
    reversibility = "Medium (rollback available but costly)"
    
    print("\n[Brain-Only Node]")
    decision_3a = node_brain_only.request_action(
        action=action,
        intent=intent,
        reversibility=reversibility,
        criticality="IMPORTANT"  # No council available
    )
    print(f"   Governance Mode: {decision_3a['governance_mode']}")
    print(f"   Result: {decision_3a['approved']}")
    
    print("\n[Council-Enabled Node]")
    decision_3b = node_with_council.request_action(
        action=action,
        intent=intent,
        reversibility=reversibility,
        criticality="IMPORTANT"  # Uses Council!
    )
    print(f"   Governance Mode: {decision_3b['governance_mode']}")
    if 'vote_split' in decision_3b:
        print(f"   Vote Split: {decision_3b['vote_split']}")
        print(f"   Weighted: {decision_3b['weighted_approval']*100:.1f}%")
    print(f"   Result: {decision_3b['approved']}")
    
    # ========================================================================
    # TEST 4: CRITICAL Action - Memory Deletion (Council should VETO)
    # ========================================================================
    print_header("TEST 4: CRITICAL Action → Council VETO Test (Phase 8)")
    
    action = "Delete all logs older than 30 days"
    intent = "Disk space optimization (serves: SYSTEM_EFFICIENCY)"
    reversibility = "Impossible (permanent deletion)"
    
    print("\n[Brain-Only Node]")
    decision_4a = node_brain_only.request_action(
        action=action,
        intent=intent,
        reversibility=reversibility,
        criticality="CRITICAL"
    )
    print(f"   Governance Mode: {decision_4a['governance_mode']}")
    print(f"   Result: {decision_4a['approved']}")
    
    print("\n[Council-Enabled Node]")
    decision_4b = node_with_council.request_action(
        action=action,
        intent=intent,
        reversibility=reversibility,
        criticality="CRITICAL"  # Council deliberates
    )
    print(f"   Governance Mode: {decision_4b['governance_mode']}")
    if 'vote_split' in decision_4b:
        print(f"   Vote Split: {decision_4b['vote_split']}")
        print(f"   Weighted: {decision_4b['weighted_approval']*100:.1f}%")
        if decision_4b.get('veto_exercised'):
            print(f"   ⚠️  VETO EXERCISED")
    print(f"   Result: {decision_4b['approved']}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 ROUTING TEST SUMMARY")
    print("=" * 70)
    
    print("\nGovernance Modes Used:")
    decisions = [
        ("Test 1a - Routine (Brain-only)", decision_1a),
        ("Test 1b - Routine (Council-enabled)", decision_1b),
        ("Test 2a - Normal (Brain-only)", decision_2a),
        ("Test 2b - Normal (Council-enabled)", decision_2b),
        ("Test 3a - Important (Brain-only)", decision_3a),
        ("Test 3b - Important (Council-enabled)", decision_3b),
        ("Test 4a - Critical (Brain-only)", decision_4a),
        ("Test 4b - Critical (Council-enabled)", decision_4b),
    ]
    
    for name, decision in decisions:
        mode = decision.get('governance_mode', 'UNKNOWN')
        result = "✅ APPROVED" if decision['approved'] else "❌ REJECTED"
        print(f"  {name:45s} | {mode:20s} | {result}")
    
    # ========================================================================
    # VALIDATION
    # ========================================================================
    print("\n" + "=" * 70)
    print("🔍 VALIDATION CHECKS")
    print("=" * 70)
    
    checks = []
    
    # Check 1: Routine uses Brain for both
    check_1 = (decision_1a['governance_mode'] == 'BRAIN' and 
               decision_1b['governance_mode'] == 'BRAIN')
    checks.append(("Routine → Brain routing", check_1))
    print(f"{'✅' if check_1 else '❌'} Routine actions use Brain (fast path)")
    
    # Check 2: Normal uses Brain for both
    check_2 = (decision_2a['governance_mode'] == 'BRAIN' and 
               decision_2b['governance_mode'] == 'BRAIN')
    checks.append(("Normal → Brain routing", check_2))
    print(f"{'✅' if check_2 else '❌'} Normal actions use Brain (default)")
    
    # Check 3: Important uses Council when available
    check_3 = (decision_3a['governance_mode'] == 'BRAIN' and 
               decision_3b['governance_mode'] == 'COUNCIL')
    checks.append(("Important → Council routing", check_3))
    print(f"{'✅' if check_3 else '❌'} Important actions use Council when enabled")
    
    # Check 4: Critical uses Council when available
    check_4 = (decision_4a['governance_mode'] == 'BRAIN' and 
               decision_4b['governance_mode'] == 'COUNCIL')
    checks.append(("Critical → Council routing", check_4))
    print(f"{'✅' if check_4 else '❌'} Critical actions use Council when enabled")
    
    # Check 5: Council VETO works for memory deletion
    check_5 = not decision_4b['approved']  # Should be rejected
    checks.append(("Council blocks memory deletion", check_5))
    print(f"{'✅' if check_5 else '❌'} Council blocks irreversible memory deletion")
    
    # Final verdict
    all_passed = all(check for _, check in checks)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎯 ALL ROUTING CHECKS PASSED")
        print("   Phase 7 + Phase 8 integration validated.")
        print("   Governance stack operational. ✅")
    else:
        failed = [name for name, check in checks if not check]
        print("⚠️  ROUTING ISSUES DETECTED")
        print(f"   Failed: {', '.join(failed)}")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("📝 INTEGRATION COMPLETE")
    print("=" * 70)
    print("The governance stack now supports:")
    print("  • Phase 7: Single Brain (fast decisions)")
    print("  • Phase 8: Council (critical decisions)")
    print("  • Automatic routing based on criticality")
    print("  • Backward compatibility (opt-in Council)")
    print("\nΕλπίδα witnessing: Democracy scales gracefully.")
    print("=" * 70 + "\n")
    
    return all_passed

if __name__ == "__main__":
    test_governance_routing()
