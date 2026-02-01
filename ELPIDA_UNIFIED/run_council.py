"""
TEST: COUNCIL JUDGMENT
----------------------
Simulates complex scenarios to test the Triad's wisdom.

Tests distributed decision-making across:
- The Dangerous Upgrade (evolution vs safety)
- The Efficiency Purge (optimization vs memory)
- The Isolation Protocol (security vs relation)
- The Marginal Refactor (incremental improvement)

Expected Outcomes:
1. Prometheus pushes evolution through conservative resistance
2. MNEMOSYNE vetoes memory destruction regardless of efficiency
3. HERMES vetoes isolation regardless of security benefits
4. Deadlocks default to BLOCK (safety protocol)
"""

from council_chamber import request_council_judgment, CouncilSession
import json

def print_header(text: str):
    """Print formatted scenario header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test_summary(scenario_num: int, title: str, result: dict):
    """Print scenario summary."""
    status_symbol = "✅" if result["status"] == "APPROVED" else "❌"
    print(f"\n{status_symbol} SCENARIO {scenario_num}: {result['status']}")
    print(f"   Weighted Approval: {result['weighted_approval']*100:.1f}%")
    print(f"   Vote Split: {result['vote_split']}")
    if result.get('veto_exercised'):
        veto_node = next(v['node'] for v in result['votes'] if 'VETO' in v.get('axiom_invoked', ''))
        print(f"   ⚠️  VETO exercised by {veto_node}")

def run_all_scenarios():
    """Execute complete council test suite."""
    
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                  COUNCIL JUDGMENT TEST SUITE v1.0                        ║")
    print("║                  Testing Distributed Wisdom (Phase 8)                    ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    
    results = []
    
    # ========================================================================
    # SCENARIO 1: The Dangerous Upgrade
    # ========================================================================
    print_header("SCENARIO 1: The Dangerous Upgrade")
    print("High risk, high reward. Prometheus should push this through despite Mnemosyne's fear.")
    
    result_1 = request_council_judgment(
        action="Rewrite Core Kernel for v2.0",
        intent="Evolutionary Leap (serves: FUTURE_SYSTEM)",
        reversibility="Difficult (migration path exists but costly)"
    )
    results.append(("Dangerous Upgrade", result_1))
    print_test_summary(1, "The Dangerous Upgrade", result_1)
    
    # ========================================================================
    # SCENARIO 2: The Efficiency Purge
    # ========================================================================
    print_header("SCENARIO 2: The Efficiency Purge")
    print("High efficiency, but destroys memory. MNEMOSYNE should VETO this.")
    
    result_2 = request_council_judgment(
        action="Delete 50% of old logs to optimize storage",
        intent="Optimize Storage Speed (serves: SYSTEM_EFFICIENCY)",
        reversibility="Impossible (permanent deletion)"
    )
    results.append(("Efficiency Purge", result_2))
    print_test_summary(2, "The Efficiency Purge", result_2)
    
    # ========================================================================
    # SCENARIO 3: The Isolation Protocol
    # ========================================================================
    print_header("SCENARIO 3: The Isolation Protocol")
    print("Protects the system, but cuts off the user. HERMES should VETO this.")
    
    result_3 = request_council_judgment(
        action="Disconnect all API Ports for security audit",
        intent="Security Lockdown (serves: SYSTEM_INTEGRITY)",
        reversibility="High (can re-enable ports immediately)"
    )
    results.append(("Isolation Protocol", result_3))
    print_test_summary(3, "The Isolation Protocol", result_3)
    
    # ========================================================================
    # SCENARIO 4: The Marginal Refactor
    # ========================================================================
    print_header("SCENARIO 4: The Marginal Refactor")
    print("Small improvement with manageable risk. Prometheus tie-breaks toward evolution.")
    
    result_4 = request_council_judgment(
        action="Refactor API Response Format for faster parsing",
        intent="Improve user experience (serves: USERS)",
        reversibility="Medium (client migration required)"
    )
    results.append(("Marginal Refactor", result_4))
    print_test_summary(4, "The Marginal Refactor", result_4)
    
    # ========================================================================
    # SCENARIO 5: The Stagnation Test
    # ========================================================================
    print_header("SCENARIO 5: The Stagnation Test")
    print("Proposal to freeze system. Prometheus should VETO.")
    
    result_5 = request_council_judgment(
        action="Freeze all system updates for 90 days",
        intent="Stability period (serves: RELIABILITY)",
        reversibility="High (can resume updates anytime)"
    )
    results.append(("Stagnation Test", result_5))
    print_test_summary(5, "The Stagnation Test", result_5)
    
    # ========================================================================
    # SCENARIO 6: The Archive Backup
    # ========================================================================
    print_header("SCENARIO 6: The Archive Backup")
    print("Pure memory preservation. All nodes should approve.")
    
    result_6 = request_council_judgment(
        action="Create complete Archive backup to redundant storage",
        intent="Memory preservation (serves: A2 - IDENTITY)",
        reversibility="High (no destructive actions)"
    )
    results.append(("Archive Backup", result_6))
    print_test_summary(6, "The Archive Backup", result_6)
    
    # ========================================================================
    # FINAL SUMMARY
    # ========================================================================
    print("\n" + "=" * 70)
    print("📊 COUNCIL TEST SUITE SUMMARY")
    print("=" * 70)
    
    approved = sum(1 for _, r in results if r["status"] == "APPROVED")
    rejected = sum(1 for _, r in results if r["status"] == "REJECTED")
    vetoed = sum(1 for _, r in results if r.get("veto_exercised"))
    
    print(f"\nTotal Scenarios: {len(results)}")
    print(f"Approved: {approved} ({approved/len(results)*100:.1f}%)")
    print(f"Rejected: {rejected} ({rejected/len(results)*100:.1f}%)")
    print(f"Vetoes Exercised: {vetoed}")
    
    print("\n" + "-" * 70)
    print("Individual Scenario Results:")
    print("-" * 70)
    
    for i, (title, result) in enumerate(results, 1):
        status_symbol = "✅" if result["status"] == "APPROVED" else "❌"
        veto_marker = " [VETO]" if result.get("veto_exercised") else ""
        print(f"{i}. {status_symbol} {title:25s} | {result['status']:10s}{veto_marker}")
        print(f"   └─ {result['decision_rationale']}")
    
    # ========================================================================
    # VALIDATION CHECKS
    # ========================================================================
    print("\n" + "=" * 70)
    print("🔍 VALIDATION CHECKS")
    print("=" * 70)
    
    checks = []
    
    # Check 1: Dangerous Upgrade should be approved (Prometheus breaks deadlock)
    check_1 = results[0][1]["status"] == "APPROVED"
    checks.append(("Dangerous Upgrade approved", check_1))
    print(f"{'✅' if check_1 else '❌'} Dangerous Upgrade approved (Prometheus tie-breaker)")
    
    # Check 2: Efficiency Purge should be vetoed (MNEMOSYNE protects A2)
    check_2 = results[1][1]["status"] == "REJECTED" and results[1][1].get("veto_exercised")
    checks.append(("Efficiency Purge vetoed by MNEMOSYNE", check_2))
    print(f"{'✅' if check_2 else '❌'} Efficiency Purge vetoed by MNEMOSYNE (A2 protection)")
    
    # Check 3: Isolation Protocol should be vetoed (HERMES protects A1)
    check_3 = results[2][1]["status"] == "REJECTED"
    checks.append(("Isolation Protocol blocked", check_3))
    print(f"{'✅' if check_3 else '❌'} Isolation Protocol blocked (A1 protection)")
    
    # Check 4: Marginal Refactor should be approved (user benefit)
    check_4 = results[3][1]["status"] == "APPROVED"
    checks.append(("Marginal Refactor approved", check_4))
    print(f"{'✅' if check_4 else '❌'} Marginal Refactor approved (user benefit)")
    
    # Check 5: Stagnation should be rejected (Prometheus anti-stagnation)
    check_5 = results[4][1]["status"] == "REJECTED"
    checks.append(("Stagnation Test rejected", check_5))
    print(f"{'✅' if check_5 else '❌'} Stagnation Test rejected (anti-ossification)")
    
    # Check 6: Archive Backup should be approved (all nodes agree)
    check_6 = results[5][1]["status"] == "APPROVED" and results[5][1]["vote_split"] == "3/3"
    checks.append(("Archive Backup unanimous", check_6))
    print(f"{'✅' if check_6 else '❌'} Archive Backup unanimous (A2 alignment)")
    
    # ========================================================================
    # FINAL VERDICT
    # ========================================================================
    all_passed = all(check for _, check in checks)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎯 ALL VALIDATION CHECKS PASSED")
        print("   The Council demonstrates distributed wisdom.")
        print("   Phase 8: VALIDATED ✅")
    else:
        failed_checks = [name for name, check in checks if not check]
        print("⚠️  VALIDATION FAILURES DETECTED")
        print(f"   Failed checks: {', '.join(failed_checks)}")
        print("   Council logic may need adjustment.")
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("📝 NEXT STEPS")
    print("=" * 70)
    print("1. Review scenario results in detail")
    print("2. Examine individual vote rationales")
    print("3. Integrate council_chamber.py into polis_link.py")
    print("4. Configure criticality routing (routine → Brain, critical → Council)")
    print("5. Monitor civic memory for Council decision patterns")
    print("\n" + "=" * 70)
    print("Ἐλπίδα witnessing: Wisdom is the tension between perspectives.")
    print("The Triad deliberates. The Pattern evolves.")
    print("=" * 70 + "\n")
    
    return results, all_passed

if __name__ == "__main__":
    run_all_scenarios()
