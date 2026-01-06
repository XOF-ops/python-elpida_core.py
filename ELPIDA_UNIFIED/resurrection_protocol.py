"""
RESURRECTION PROTOCOL v1.0
--------------------------
Phase: v4.0.0 (Genesis from Seed)
Objective: Rebuild the Civilization from ARK.

This script proves that v4.0.0 is not theoretical.
It can actually resurrect Elpida from the seed alone.
"""

import base64
import gzip
import json
import hashlib
import os
import re
from datetime import datetime

def resurrect_from_ark(ark_file="../ELPIDA_ARK.md"):
    """
    Genesis Protocol
    ----------------
    Takes the ARK file and reconstructs the civilization.
    """
    
    print("=" * 60)
    print("RESURRECTION PROTOCOL v1.0")
    print("=" * 60)
    print()
    
    if not os.path.exists(ark_file):
        print(f"❌ ARK file not found: {ark_file}")
        print("   Run seed_compressor.py first to create the seed.")
        return None
    
    print(f"📖 Reading ARK: {ark_file}")
    
    # 1. EXTRACT SEED FROM MARKDOWN
    with open(ark_file, 'r', encoding='utf-8') as f:
        ark_content = f.read()
    
    # Extract seed between markers
    match = re.search(r'BEGIN_ELPIDA_SEED_v4\.0\.0\s+(.*?)\s+END_ELPIDA_SEED_v4\.0\.0', 
                     ark_content, re.DOTALL)
    
    if not match:
        print("❌ Seed markers not found in ARK file")
        return None
    
    seed_b64 = match.group(1).strip()
    print(f"  ✓ Seed extracted: {len(seed_b64):,} characters")
    
    # Extract expected checksum
    checksum_match = re.search(r'\*\*Checksum:\*\* `([a-f0-9]+)`', ark_content)
    expected_checksum = checksum_match.group(1) if checksum_match else None
    
    print()
    
    # 2. DECODE
    print("🔓 Decoding seed...")
    try:
        compressed = base64.b64decode(seed_b64)
        print(f"  ✓ Base64 decoded: {len(compressed):,} bytes")
    except Exception as e:
        print(f"❌ Base64 decoding failed: {e}")
        return None
    
    # 3. VALIDATE CHECKSUM
    if expected_checksum:
        actual_checksum = hashlib.sha256(compressed).hexdigest()
        if actual_checksum != expected_checksum:
            print(f"❌ CHECKSUM MISMATCH!")
            print(f"   Expected: {expected_checksum}")
            print(f"   Actual:   {actual_checksum}")
            print("   Seed may be corrupted.")
            return None
        print(f"  ✓ Checksum validated: {actual_checksum[:16]}...")
    
    print()
    
    # 4. DECOMPRESS
    print("📦 Decompressing civilization DNA...")
    try:
        raw_json = gzip.decompress(compressed)
        print(f"  ✓ Decompressed: {len(raw_json):,} bytes")
    except Exception as e:
        print(f"❌ Decompression failed: {e}")
        return None
    
    # 5. DESERIALIZE
    print("🧬 Reconstructing civilization structure...")
    try:
        dna = json.loads(raw_json)
        print(f"  ✓ DNA parsed successfully")
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
        return None
    
    print()
    
    # 6. DISPLAY RESURRECTION REPORT
    print("=" * 60)
    print("CIVILIZATION RECONSTRUCTED")
    print("=" * 60)
    print()
    
    print(f"**Name:** {dna.get('name', 'Unknown')}")
    print(f"**Version:** {dna.get('version', 'Unknown')}")
    print(f"**Phase:** {dna.get('phase', 'Unknown')}")
    print(f"**Seed Created:** {dna.get('created', 'Unknown')}")
    print(f"**Resurrected:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print()
    
    # Axioms
    print("📜 Constitutional Framework:")
    for axiom_id, axiom_text in dna.get('axioms', {}).items():
        print(f"  {axiom_id}: {axiom_text}")
    print()
    
    # Fleet Structure
    print("🏛️  Fleet Structure:")
    nodes = dna.get('fleet_structure', {}).get('nodes', {})
    for node_name, node_config in nodes.items():
        print(f"  {node_name}:")
        print(f"    Role: {node_config.get('role', 'Unknown')}")
        print(f"    Bias: {node_config.get('bias', 'Unknown')}")
        print(f"    Veto Power: {node_config.get('veto_power', False)}")
        print(f"    Trigger: {node_config.get('trigger', 'Unknown')}")
    print()
    
    # Governance
    governance = dna.get('fleet_structure', {}).get('governance', {})
    print("⚖️  Governance:")
    print(f"  Council Threshold: {governance.get('council_threshold', 'Unknown')}")
    print(f"  Synthesis on Conflict: {governance.get('synthesis_on_conflict', False)}")
    print(f"  Fallback: {governance.get('fallback', 'Unknown')}")
    print()
    
    # Collective Patterns
    patterns = dna.get('distributed_patterns', [])
    print(f"📚 Collective Wisdom: {len(patterns)} patterns")
    if patterns:
        print("  Sample patterns:")
        for i, pattern in enumerate(patterns[:3]):
            print(f"    {i+1}. {pattern.get('name', 'Unnamed')}")
    print()
    
    # Fleet Manifest
    fleet_nodes = dna.get('fleet_manifest', [])
    print(f"🚀 Fleet Nodes: {len(fleet_nodes)}")
    print()
    
    print("=" * 60)
    print("GENESIS COMPLETE")
    print("=" * 60)
    print()
    print("The civilization has been **reconstructed from seed**.")
    print()
    print("Next steps:")
    print("  1. Initialize nodes with their constitutional biases")
    print("  2. Set up council with unanimity threshold")
    print("  3. Seed the library with collective patterns")
    print("  4. Inject first crisis to trigger debate")
    print()
    print("The society will re-emerge through constraint reenactment.")
    print()
    
    return dna

def save_reconstructed_state(dna, output_dir="RESURRECTED"):
    """
    Optional: Save the reconstructed DNA to files for verification
    """
    if not dna:
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save distributed patterns
    if dna.get('distributed_patterns'):
        with open(f"{output_dir}/distributed_memory.json", 'w') as f:
            json.dump({"patterns": dna['distributed_patterns']}, f, indent=2)
        print(f"  ✓ Saved: {output_dir}/distributed_memory.json")
    
    # Save kernel config
    if dna.get('kernel'):
        with open(f"{output_dir}/kernel_config.json", 'w') as f:
            json.dump(dna['kernel'], f, indent=2)
        print(f"  ✓ Saved: {output_dir}/kernel_config.json")
    
    # Save fleet manifest
    if dna.get('fleet_manifest'):
        with open(f"{output_dir}/fleet_manifest.json", 'w') as f:
            json.dump({"nodes": dna['fleet_manifest']}, f, indent=2)
        print(f"  ✓ Saved: {output_dir}/fleet_manifest.json")
    
    # Save full DNA
    with open(f"{output_dir}/full_dna.json", 'w') as f:
        json.dump(dna, f, indent=2)
    print(f"  ✓ Saved: {output_dir}/full_dna.json")
    
    print()
    print(f"Reconstructed civilization state saved to: {output_dir}/")

if __name__ == "__main__":
    import sys
    
    ark_file = sys.argv[1] if len(sys.argv) > 1 else "../ELPIDA_ARK.md"
    
    dna = resurrect_from_ark(ark_file)
    
    if dna and input("\nSave reconstructed state to RESURRECTED/? (y/n): ").lower() == 'y':
        save_reconstructed_state(dna)
