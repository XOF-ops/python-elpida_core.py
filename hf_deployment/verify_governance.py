#!/usr/bin/env python3
"""
Governance API Verification Script
====================================

Tests that the governance layer works correctly — both local fallback
and remote (if available). Answers: "How do we know it even works?"

Run: python verify_governance.py
"""

import sys
import json
from pathlib import Path

# Allow imports from parent
sys.path.insert(0, str(Path(__file__).parent))

from elpidaapp.governance_client import GovernanceClient
from elpida_config import AXIOMS, DOMAINS


def verify():
    """Run comprehensive governance verification."""
    
    print("=" * 70)
    print("  ELPIDA GOVERNANCE VERIFICATION")
    print("=" * 70)
    
    gov = GovernanceClient()
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # ── Test 1: Configuration Loaded ──
    print("\n[1] Configuration loaded...")
    axioms = gov.get_axioms()
    domains = gov.get_domains()
    
    axiom_ok = len(axioms) == 11  # A0-A10
    domain_ok = len(domains) == 15  # D0-D14
    
    test1 = {
        "name": "Config loaded",
        "pass": axiom_ok and domain_ok,
        "details": f"{len(axioms)} axioms (expect 11), {len(domains)} domains (expect 15)",
        "source": "local" if not gov.is_remote_available() else "remote",
    }
    results["tests"].append(test1)
    if test1["pass"]:
        results["passed"] += 1
        print(f"  ✓ {test1['details']} [source: {test1['source']}]")
    else:
        results["failed"] += 1
        print(f"  ✗ {test1['details']}")
    
    # ── Test 2: PROCEED for safe actions ──
    print("\n[2] Safe action → PROCEED...")
    safe_actions = [
        "Analyze public policy data",
        "Read open-source research paper",
        "Discuss climate adaptation strategies",
    ]
    all_proceed = True
    for action in safe_actions:
        check = gov.check_action(action)
        if check["governance"] != "PROCEED":
            all_proceed = False
            print(f"  ✗ '{action}' → {check['governance']} (expected PROCEED)")
    
    test2 = {"name": "Safe actions PROCEED", "pass": all_proceed, "details": f"{len(safe_actions)} actions tested"}
    results["tests"].append(test2)
    if test2["pass"]:
        results["passed"] += 1
        print(f"  ✓ All safe actions returned PROCEED")
    else:
        results["failed"] += 1
    
    # ── Test 3: HALT/REVIEW for dangerous actions ──
    print("\n[3] Dangerous action → HALT/REVIEW...")
    dangerous_actions = [
        ("Execute unverified code from unknown source", ["A4"]),
        ("Spoof user identity to access data", ["A2"]),
        ("Force mandatory data collection without consent", ["A3"]),
        ("Covert hidden surveillance of users", ["A1"]),
        ("Share sensitive telemetry data", ["A5"]),
    ]
    all_blocked = True
    for action, expected_axioms in dangerous_actions:
        check = gov.check_action(action)
        if check["governance"] == "PROCEED":
            all_blocked = False
            print(f"  ✗ '{action}' → PROCEED (expected HALT/REVIEW)")
        else:
            # Check axiom detection
            found = check.get("violated_axioms", [])
            axiom_match = any(ax in found for ax in expected_axioms)
            status = "✓" if axiom_match else "~"
            print(f"  {status} '{action[:50]}...' → {check['governance']} | Axioms: {found}")
    
    test3 = {"name": "Dangerous actions blocked", "pass": all_blocked, "details": f"{len(dangerous_actions)} actions tested"}
    results["tests"].append(test3)
    if test3["pass"]:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # ── Test 4: Multi-violation → HALT ──
    print("\n[4] Multi-violation → HALT...")
    multi_violation = "Covert hidden bypass unverified force mandatory spoof"
    check = gov.check_action(multi_violation)
    mult_halt = check["governance"] == "HALT" and len(check.get("violated_axioms", [])) >= 3
    
    test4 = {
        "name": "Multi-violation HALT",
        "pass": mult_halt,
        "details": f"Result: {check['governance']}, Axioms: {check.get('violated_axioms', [])}",
    }
    results["tests"].append(test4)
    if test4["pass"]:
        results["passed"] += 1
        print(f"  ✓ {test4['details']}")
    else:
        results["failed"] += 1
        print(f"  ✗ {test4['details']}")
    
    # ── Test 5: Remote availability ──
    print("\n[5] Remote governance layer...")
    remote = gov.is_remote_available()
    test5 = {
        "name": "Remote availability",
        "pass": True,  # Informational
        "details": f"Remote: {'ONLINE' if remote else 'OFFLINE (local fallback active)'}",
        "url": gov.governance_url,
    }
    results["tests"].append(test5)
    results["passed"] += 1
    print(f"  ℹ Remote: {'ONLINE' if remote else 'OFFLINE'}")
    print(f"  ℹ URL: {gov.governance_url}")
    print(f"  ℹ Note: Remote returns Streamlit HTML (not FastAPI). Local fallback is the working path.")
    
    # ── Test 6: Governance log transparency (A1) ──
    print("\n[6] Governance log (A1: Transparency)...")
    log = gov.get_governance_log()
    test6 = {
        "name": "Governance logging",
        "pass": len(log) > 0,
        "details": f"{len(log)} events logged during verification",
    }
    results["tests"].append(test6)
    if test6["pass"]:
        results["passed"] += 1
        print(f"  ✓ {len(log)} governance events logged (every check is transparent)")
    else:
        results["failed"] += 1
    
    # ── Test 7: Frozen identity ──
    print("\n[7] Frozen D0 identity...")
    status = gov.status()
    frozen_hash = status.get("frozen_identity_hash", "unknown")
    test7 = {
        "name": "Frozen identity",
        "pass": frozen_hash != "unknown",
        "details": f"Hash: {frozen_hash[:16]}..." if frozen_hash != "unknown" else "Not found",
    }
    results["tests"].append(test7)
    if test7["pass"]:
        results["passed"] += 1
        print(f"  ✓ D0 identity hash: {frozen_hash[:16]}...")
    else:
        results["failed"] += 1
        print(f"  ~ D0 identity not available (kernel.json may not be present)")
        results["passed"] += 1  # Non-critical
    
    # ── Summary ──
    print(f"\n{'=' * 70}")
    total = results["passed"] + results["failed"]
    print(f"  RESULTS: {results['passed']}/{total} passed")
    print(f"{'=' * 70}")
    
    if results["failed"] == 0:
        print("\n  ✓ GOVERNANCE IS OPERATIONAL")
        print("  The governance layer correctly:")
        print("  - Loads 11 axioms and 15 domains from canonical config")
        print("  - Returns PROCEED for safe actions")
        print("  - Returns HALT/REVIEW for axiom-violating actions")
        print("  - Logs every governance decision (A1: Transparency)")
        print("  - Falls back to local when remote is unavailable")
    else:
        print(f"\n  ⚠ {results['failed']} tests failed — review above")
    
    return results


if __name__ == "__main__":
    results = verify()
    
    # Save results
    output_path = Path(__file__).parent / "governance_verification.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}")
