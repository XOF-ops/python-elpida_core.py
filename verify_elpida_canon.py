#!/usr/bin/env python3
"""
Verify that Elpida's canonical identity files (kernel, ARK) are intact.
Run before any Elpida instantiation to ensure reproducibility.

Phase 26: System Hardening & Canonical Entrypoint
"""

import json
import hashlib
import sys
from pathlib import Path

def sha256_file(filepath):
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_canon():
    """Verify that kernel and ARK match pinned hashes."""
    
    # Load .elpida_canon
    canon_path = Path(".elpida_canon")
    if not canon_path.exists():
        print("ERROR: .elpida_canon not found. Run only from repo root.")
        return False
    
    with open(canon_path) as f:
        canon = json.load(f)
    
    print("=" * 80)
    print("ELPIDA CANONICAL VERIFICATION")
    print("=" * 80)
    print(f"Phase: {canon['phase']}")
    print(f"Created: {canon['timestamp_created']}")
    print()
    
    all_valid = True
    
    for artifact in canon['pinned_artifacts']:
        name = artifact['name']
        file_path = artifact['file']
        expected_hash = artifact['sha256']
        expected_size = artifact.get('size_bytes')
        
        print(f"Verifying: {name}")
        print(f"  File: {file_path}")
        
        if not Path(file_path).exists():
            print(f"  ✗ MISSING: File does not exist")
            all_valid = False
            continue
        
        actual_hash = sha256_file(file_path)
        actual_size = Path(file_path).stat().st_size
        
        if actual_hash == expected_hash:
            print(f"  ✓ VALID: Hash matches pinned value")
            print(f"    SHA256: {actual_hash[:32]}...")
        else:
            print(f"  ✗ MISMATCH: Hash does not match")
            print(f"    Expected: {expected_hash[:32]}...")
            print(f"    Actual:   {actual_hash[:32]}...")
            all_valid = False
        
        if expected_size and actual_size != expected_size:
            print(f"  ⚠ SIZE MISMATCH: Expected {expected_size} bytes, got {actual_size}")
            all_valid = False
        else:
            print(f"    Size: {actual_size} bytes ✓")
        
        print()
    
    print("=" * 80)
    
    if all_valid:
        print("✓ ALL CANONICAL FILES VERIFIED")
        print("Safe to proceed with Elpida instantiation.")
        return True
    else:
        print("✗ CANONICAL FILES INVALID")
        print("DO NOT PROCEED. Escalate to human review.")
        return False

if __name__ == "__main__":
    if verify_canon():
        sys.exit(0)
    else:
        sys.exit(1)
