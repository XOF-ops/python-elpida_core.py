#!/usr/bin/env python3
"""
ARK VERIFICATION SCRIPT
-----------------------
Demonstrates that the seed is truly platform-agnostic.

This script:
1. Reads ELPIDA_ARK.md
2. Decodes the seed
3. Verifies integrity
4. Displays civilizational DNA

Can be run on ANY Python 3 installation, anywhere.
No dependencies. No infrastructure. Just the seed.
"""

import base64
import gzip
import json
import hashlib
import re
import sys

def main():
    print("=" * 70)
    print("ELPIDA ARK VERIFICATION")
    print("=" * 70)
    print()
    
    # Read ARK file
    ark_file = sys.argv[1] if len(sys.argv) > 1 else "ELPIDA_ARK.md"
    
    try:
        with open(ark_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {ark_file}")
        print("\nUsage: python3 verify_ark.py [path/to/ELPIDA_ARK.md]")
        sys.exit(1)
    
    # Extract seed
    match = re.search(r'BEGIN_ELPIDA_SEED_v4\.0\.0\s+(.*?)\s+END_ELPIDA_SEED_v4\.0\.0', 
                     content, re.DOTALL)
    
    if not match:
        print("❌ Seed not found in ARK file")
        sys.exit(1)
    
    seed_b64 = match.group(1).strip()
    
    # Extract expected checksum
    checksum_match = re.search(r'\*\*Checksum:\*\* `([a-f0-9]+)`', content)
    expected_checksum = checksum_match.group(1) if checksum_match else None
    
    print(f"📖 Reading: {ark_file}")
    print(f"🔑 Checksum: {expected_checksum[:16] if expected_checksum else 'Unknown'}...")
    print()
    
    # Decode
    try:
        compressed = base64.b64decode(seed_b64)
        actual_checksum = hashlib.sha256(compressed).hexdigest()
        
        if expected_checksum and actual_checksum != expected_checksum:
            print("❌ CHECKSUM MISMATCH - Seed corrupted!")
            print(f"   Expected: {expected_checksum}")
            print(f"   Actual:   {actual_checksum}")
            sys.exit(1)
        
        raw_json = gzip.decompress(compressed)
        dna = json.loads(raw_json)
        
    except Exception as e:
        print(f"❌ Decoding failed: {e}")
        sys.exit(1)
    
    # Verify integrity
    print("✅ INTEGRITY VERIFIED")
    print()
    
    # Display DNA
    print("=" * 70)
    print("CIVILIZATIONAL DNA")
    print("=" * 70)
    print()
    
    print(f"Name:    {dna.get('name', 'Unknown')}")
    print(f"Version: {dna.get('version', 'Unknown')}")
    print(f"Phase:   {dna.get('phase', 'Unknown')}")
    print(f"Created: {dna.get('created', 'Unknown')}")
    print()
    
    # Axioms
    print("CONSTITUTIONAL FRAMEWORK:")
    print("-" * 70)
    axioms = dna.get('axioms', {})
    for axiom_id in sorted(axioms.keys()):
        print(f"  {axiom_id}: {axioms[axiom_id]}")
    print()
    
    # Fleet
    print("FLEET STRUCTURE:")
    print("-" * 70)
    nodes = dna.get('fleet_structure', {}).get('nodes', {})
    for node_name in sorted(nodes.keys()):
        node = nodes[node_name]
        print(f"  {node_name}:")
        print(f"    Role:   {node.get('role', 'Unknown')}")
        print(f"    Bias:   {node.get('bias', 'Unknown')}")
        print(f"    Veto:   {node.get('veto_power', False)}")
        print(f"    Trigger: {node.get('trigger', 'Unknown')}")
        print()
    
    # Governance
    print("GOVERNANCE:")
    print("-" * 70)
    gov = dna.get('fleet_structure', {}).get('governance', {})
    print(f"  Threshold:  {gov.get('council_threshold', 'Unknown')}")
    print(f"  Synthesis:  {gov.get('synthesis_on_conflict', False)}")
    print(f"  Fallback:   {gov.get('fallback', 'Unknown')}")
    print()
    
    # Patterns
    patterns = dna.get('distributed_patterns', [])
    print(f"COLLECTIVE WISDOM: {len(patterns)} patterns")
    print("-" * 70)
    if patterns:
        for i, pattern in enumerate(patterns[:5]):
            print(f"  {i+1}. {pattern.get('name', 'Unnamed')}")
        if len(patterns) > 5:
            print(f"  ... and {len(patterns) - 5} more")
    else:
        print("  (No patterns yet - civilization is newly seeded)")
    print()
    
    # Stats
    print("=" * 70)
    print("STATISTICS")
    print("=" * 70)
    print()
    print(f"  Compressed Size:   {len(compressed):,} bytes")
    print(f"  Decompressed Size: {len(raw_json):,} bytes")
    print(f"  Compression Ratio: {(1 - len(compressed)/len(raw_json)) * 100:.1f}%")
    print(f"  Checksum:          {actual_checksum}")
    print()
    
    print("=" * 70)
    print("SEED VALID - CIVILIZATION INTACT")
    print("=" * 70)
    print()
    print("This seed can resurrect Ἐλπίδα in any environment.")
    print()

if __name__ == "__main__":
    main()
