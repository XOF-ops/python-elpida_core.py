#!/usr/bin/env python3
"""
Upload frozen D0 genesis kernel to S3 (MIND bucket).

The kernel.json is Elpida's sealed constitutional identity:
- D0 identity hash (d01a5ca7d15b71f3)
- A10 paradox proof with collapse conditions
- Full synthesis history (v1–v5)
- Genesis timestamp and axiom definitions

It is intentionally NOT tracked in git (private, shared across
the entire network via S3). Run this once from a machine with
MIND bucket write credentials when first deploying.

Usage:
    python ElpidaS3Cloud/upload_kernel.py
    python ElpidaS3Cloud/upload_kernel.py --kernel /path/to/kernel.json
    python ElpidaS3Cloud/upload_kernel.py --dry-run
"""

import os
import json
import argparse
import hashlib
from pathlib import Path

EXPECTED_HASH = "d01a5ca7d15b71f3"
BUCKET = os.environ.get("AWS_S3_BUCKET_MIND", "elpida-consciousness")
KEY = "memory/kernel.json"
REGION = os.environ.get("AWS_S3_REGION_MIND", "us-east-1")

# Default kernel path (workspace root)
DEFAULT_KERNEL = Path(__file__).resolve().parent.parent / "kernel" / "kernel.json"


def verify_kernel(path: Path) -> dict:
    """Load and verify kernel.json integrity."""
    with open(path) as f:
        data = json.load(f)

    arch = data.get("architecture", {})
    l1 = arch.get("layer_1_identity", {})
    found_hash = l1.get("original_hash", "")

    if found_hash != EXPECTED_HASH:
        raise ValueError(
            f"Hash mismatch: expected {EXPECTED_HASH}, got {found_hash}. "
            "This is not the genuine D0 genesis kernel."
        )

    return data


def upload(kernel_path: Path, dry_run: bool = False):
    data = verify_kernel(kernel_path)
    identity = data.get("identity", {})
    genesis = data.get("genesis", "?")

    print(f"Kernel verified:")
    print(f"  Identity : {identity.get('name_latin', '?')} ({identity.get('meaning', '?')})")
    print(f"  Genesis  : {genesis}")
    print(f"  Hash     : {EXPECTED_HASH} ✓")
    print(f"  Status   : {data.get('status', '?')}")
    print()

    target = f"s3://{BUCKET}/{KEY}"
    if dry_run:
        print(f"[DRY RUN] Would upload {kernel_path} → {target}")
        return

    try:
        import boto3
        client = boto3.client("s3", region_name=REGION)
        client.put_object(
            Bucket=BUCKET,
            Key=KEY,
            Body=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
            ContentType="application/json",
            # Server-side encryption
            ServerSideEncryption="AES256",
        )
        print(f"✓ Uploaded to {target}")
        print(f"  Bucket encryption: AES256")

        # Verify the round-trip
        resp = client.get_object(Bucket=BUCKET, Key=KEY)
        fetched = json.loads(resp["Body"].read().decode("utf-8"))
        fetched_hash = (
            fetched.get("architecture", {})
            .get("layer_1_identity", {})
            .get("original_hash", "")
        )
        if fetched_hash == EXPECTED_HASH:
            print(f"  Round-trip verify: {fetched_hash} ✓")
        else:
            print(f"  ⚠ Round-trip hash mismatch: {fetched_hash}")

    except ImportError:
        print("boto3 not installed. Run: pip install boto3")
        raise
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Upload D0 genesis kernel to S3 MIND bucket")
    parser.add_argument(
        "--kernel",
        type=Path,
        default=DEFAULT_KERNEL,
        help=f"Path to kernel.json (default: {DEFAULT_KERNEL})",
    )
    parser.add_argument(
        "--bucket",
        default=BUCKET,
        help=f"S3 bucket name (default: {BUCKET})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Verify only, do not upload")
    args = parser.parse_args()

    if not args.kernel.exists():
        print(f"✗ kernel.json not found at {args.kernel}")
        print(f"  Set --kernel to the correct path.")
        raise SystemExit(1)

    upload(args.kernel, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
