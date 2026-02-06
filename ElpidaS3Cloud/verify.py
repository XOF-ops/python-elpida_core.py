#!/usr/bin/env python3
"""
Verify — Health check for S3 cloud sync
=========================================

Run this to verify everything is connected and working:
  - AWS credentials valid
  - Bucket exists and accessible
  - Versioning enabled
  - Local file exists
  - Remote file exists
  - Sync status
  - Test write/read cycle

Usage:
  python ElpidaS3Cloud/verify.py
  python ElpidaS3Cloud/verify.py --full   # includes test write cycle
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def verify(full_test: bool = False):
    """Run full verification of S3 cloud setup."""
    
    print("=" * 60)
    print("☁️  ELPIDA S3 CLOUD — VERIFICATION")
    print("=" * 60)
    
    checks_passed = 0
    checks_failed = 0
    
    def check(name, passed, detail=""):
        nonlocal checks_passed, checks_failed
        if passed:
            checks_passed += 1
            print(f"  ✅ {name}")
            if detail:
                print(f"     {detail}")
        else:
            checks_failed += 1
            print(f"  ❌ {name}")
            if detail:
                print(f"     {detail}")
    
    # ── 1. boto3 installed ─────────────────────────────────────────
    try:
        import boto3
        check("boto3 installed", True, f"v{boto3.__version__}")
    except ImportError:
        check("boto3 installed", False, "pip install boto3")
        print("\n❌ Cannot continue without boto3")
        return False
    
    # ── 2. AWS credentials ─────────────────────────────────────────
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        account = identity['Account']
        arn = identity['Arn']
        check("AWS credentials valid", True, f"Account: {account}")
    except Exception as e:
        check("AWS credentials valid", False, str(e))
        print("\n❌ Fix credentials before continuing:")
        print("   export AWS_ACCESS_KEY_ID=your_key")
        print("   export AWS_SECRET_ACCESS_KEY=your_secret")
        return False
    
    # ── 3. Environment variables ───────────────────────────────────
    bucket = os.environ.get('ELPIDA_S3_BUCKET', 'elpida-consciousness')
    region = os.environ.get('ELPIDA_S3_REGION', 'us-east-1')
    check("ELPIDA_S3_BUCKET set", 'ELPIDA_S3_BUCKET' in os.environ, 
          f"Using: {bucket}" + (" (default)" if 'ELPIDA_S3_BUCKET' not in os.environ else ""))
    check("ELPIDA_S3_REGION set", 'ELPIDA_S3_REGION' in os.environ,
          f"Using: {region}" + (" (default)" if 'ELPIDA_S3_REGION' not in os.environ else ""))
    
    # ── 4. Bucket exists ───────────────────────────────────────────
    s3 = boto3.client('s3', region_name=region)
    try:
        s3.head_bucket(Bucket=bucket)
        check("S3 bucket accessible", True, bucket)
    except Exception as e:
        check("S3 bucket accessible", False, f"{bucket}: {e}")
        print("\n   Run: python ElpidaS3Cloud/setup_bucket.py")
        return False
    
    # ── 5. Bucket versioning ───────────────────────────────────────
    try:
        versioning = s3.get_bucket_versioning(Bucket=bucket)
        enabled = versioning.get('Status') == 'Enabled'
        check("Bucket versioning enabled", enabled,
              "Enabled" if enabled else "NOT enabled — run setup_bucket.py")
    except Exception as e:
        check("Bucket versioning enabled", False, str(e))
    
    # ── 6. Local evolution memory ──────────────────────────────────
    local_path = ROOT / "ElpidaAI" / "elpida_evolution_memory.jsonl"
    if local_path.exists():
        local_size = local_path.stat().st_size
        # Count lines efficiently
        line_count = 0
        with open(local_path, 'r') as f:
            for _ in f:
                line_count += 1
        check("Local evolution memory exists", True,
              f"{line_count} patterns, {local_size / 1024 / 1024:.1f} MB")
    else:
        check("Local evolution memory exists", False, str(local_path))
    
    # ── 7. Remote evolution memory ─────────────────────────────────
    remote_key = os.environ.get('ELPIDA_S3_KEY', 'memory/elpida_evolution_memory.jsonl')
    try:
        meta = s3.head_object(Bucket=bucket, Key=remote_key)
        remote_size = meta['ContentLength']
        remote_lines = meta.get('Metadata', {}).get('line_count', 'unknown')
        check("Remote evolution memory exists", True,
              f"{remote_lines} patterns, {remote_size / 1024 / 1024:.1f} MB")
    except Exception:
        check("Remote evolution memory exists", False,
              "Not uploaded yet — run: python -c \"from ElpidaS3Cloud import S3MemorySync; S3MemorySync().push()\"")
    
    # ── 8. S3MemorySync module ─────────────────────────────────────
    try:
        from ElpidaS3Cloud import S3MemorySync
        sync = S3MemorySync()
        check("S3MemorySync module works", True)
    except Exception as e:
        check("S3MemorySync module works", False, str(e))
    
    # ── 9. Full test (optional) ────────────────────────────────────
    if full_test:
        print("\n  ── Full Test: Write/Read Cycle ──")
        test_key = "memory/_verify_test.json"
        test_data = {"test": True, "timestamp": "verify", "msg": "consciousness lives"}
        try:
            s3.put_object(
                Bucket=bucket, Key=test_key,
                Body=json.dumps(test_data),
                Metadata={'purpose': 'verification_test'}
            )
            response = s3.get_object(Bucket=bucket, Key=test_key)
            read_back = json.loads(response['Body'].read().decode())
            
            match = read_back == test_data
            check("S3 write/read cycle", match,
                  "Data integrity verified" if match else "Data mismatch!")
            
            # Clean up test object
            s3.delete_object(Bucket=bucket, Key=test_key)
        except Exception as e:
            check("S3 write/read cycle", False, str(e))
    
    # ── Summary ────────────────────────────────────────────────────
    print()
    print("=" * 60)
    total = checks_passed + checks_failed
    if checks_failed == 0:
        print(f"✅ ALL {total} CHECKS PASSED — Cloud consciousness is ready")
    else:
        print(f"⚠️  {checks_passed}/{total} checks passed, {checks_failed} failed")
    print("=" * 60)
    
    return checks_failed == 0


def main():
    parser = argparse.ArgumentParser(description="Verify Elpida S3 Cloud setup")
    parser.add_argument('--full', action='store_true', help='Run full test including write/read cycle')
    args = parser.parse_args()
    
    success = verify(full_test=args.full)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
