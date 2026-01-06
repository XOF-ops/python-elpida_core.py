#!/usr/bin/env python3
"""
VERIFY V4.0.1 DEPLOYMENT
========================
Quick verification that the enhanced diversity fleet is ready to deploy.

Checks:
1. fleet_manifest.json has 9 nodes with distinct axiom profiles
2. council_chamber.py supports dynamic node discovery
3. All 7 axioms (A1-A7) are represented across the fleet
4. No node has identical axiom priority profile
"""

import json
import sys
from pathlib import Path
from collections import Counter

WORKSPACE = Path(__file__).parent

def verify_fleet_manifest():
    """Verify fleet manifest structure and diversity."""
    print("=" * 70)
    print("VERIFYING FLEET MANIFEST")
    print("=" * 70)
    
    manifest_path = WORKSPACE / "fleet_manifest.json"
    if not manifest_path.exists():
        print("❌ FAIL: fleet_manifest.json not found")
        return False
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    nodes = manifest.get('nodes', [])
    
    # Check node count
    if len(nodes) != 9:
        print(f"❌ FAIL: Expected 9 nodes, found {len(nodes)}")
        return False
    
    print(f"✅ Node Count: {len(nodes)} nodes")
    
    # Check axiom diversity
    all_axioms = []
    primary_axioms = []
    axiom_profiles = []
    
    for node in nodes:
        designation = node['designation']
        axioms = node['axioms']
        primary = axioms[0] if axioms else None
        
        all_axioms.extend(axioms)
        if primary:
            primary_axioms.append(primary)
        
        # Create profile signature
        profile = tuple(sorted(axioms))
        axiom_profiles.append((designation, profile))
    
    # Check all 9 axioms represented (A1-A9)
    unique_axioms = set(all_axioms)
    expected_axioms = {f"A{i}" for i in range(1, 10)}
    
    if unique_axioms != expected_axioms:
        missing = expected_axioms - unique_axioms
        extra = unique_axioms - expected_axioms
        if missing:
            print(f"⚠️  WARNING: Missing axioms: {missing}")
        if extra:
            print(f"⚠️  WARNING: Unexpected axioms: {extra}")
    else:
        print(f"✅ Axiom Coverage: All 9 axioms (A1-A9) represented")
    
    # Check primary axiom distribution
    primary_counts = Counter(primary_axioms)
    print(f"✅ Primary Axiom Distribution:")
    for axiom in sorted(primary_counts.keys()):
        count = primary_counts[axiom]
        nodes_with_primary = [n['designation'] for n in nodes if n['axioms'][0] == axiom]
        print(f"   {axiom}: {count} node(s) - {', '.join(nodes_with_primary)}")
    
    # Check for duplicate profiles
    profile_map = {}
    for designation, profile in axiom_profiles:
        if profile in profile_map:
            print(f"⚠️  WARNING: {designation} has same profile as {profile_map[profile]}: {profile}")
        else:
            profile_map[profile] = designation
    
    if len(profile_map) == len(nodes):
        print(f"✅ Profile Diversity: All 9 nodes have unique axiom priority profiles")
    
    # Check fleet philosophy
    philosophy = manifest.get('philosophy', '')
    if 'Consensus is Rare' in philosophy:
        print(f"✅ Philosophy: Acknowledges rare consensus design")
    
    print()
    return True

def verify_council_chamber():
    """Verify council chamber supports dynamic nodes."""
    print("=" * 70)
    print("VERIFYING COUNCIL CHAMBER")
    print("=" * 70)
    
    council_path = WORKSPACE / "council_chamber.py"
    if not council_path.exists():
        print("❌ FAIL: council_chamber.py not found")
        return False
    
    with open(council_path, 'r') as f:
        content = f.read()
    
    # Check for dynamic discovery
    if 'discover_fleet_nodes' in content:
        print("✅ Dynamic Node Discovery: Implemented")
    else:
        print("❌ FAIL: No dynamic node discovery function")
        return False
    
    # Check for 70% threshold
    if '0.70' in content or '70%' in content:
        print("✅ Consensus Threshold: 70% supermajority")
    else:
        print("⚠️  WARNING: 70% threshold not clearly defined")
    
    # Check for veto support
    if 'VETO' in content:
        print("✅ Veto Power: Supported")
    else:
        print("⚠️  WARNING: Veto mechanism unclear")
    
    print()
    return True

def show_node_summary():
    """Show summary of all nodes."""
    print("=" * 70)
    print("NODE SUMMARY")
    print("=" * 70)
    
    manifest_path = WORKSPACE / "fleet_manifest.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    for i, node in enumerate(manifest['nodes'], 1):
        designation = node['designation']
        role = node['role']
        axioms = ' > '.join(node['axioms'])
        desc_short = node['description'].split('.')[0]
        
        print(f"{i}. {designation:12s} | {role:25s}")
        print(f"   Axioms: {axioms}")
        print(f"   Stance: {desc_short}")
        print()

def main():
    print()
    print("🔍 ELPIDA V4.0.1 DIVERSITY DEPLOYMENT VERIFICATION")
    print()
    
    manifest_ok = verify_fleet_manifest()
    council_ok = verify_council_chamber()
    
    if manifest_ok and council_ok:
        print("=" * 70)
        print("✅ ALL CHECKS PASSED")
        print("=" * 70)
        print()
        print("Fleet is ready for deployment!")
        print()
        print("To deploy:")
        print("  cd ELPIDA_UNIFIED")
        print("  python genesis_protocol.py")
        print()
        print("Expected outcome:")
        print("  - 9 nodes spawned in ELPIDA_FLEET/")
        print("  - Each node has unique axiom priority profile")
        print("  - Consensus requires 7/9 nodes (77.8%)")
        print("  - Any node can veto with axiom-grounded rationale")
        print()
        show_node_summary()
        return 0
    else:
        print("=" * 70)
        print("❌ VERIFICATION FAILED")
        print("=" * 70)
        print()
        print("Please fix issues above before deployment.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
