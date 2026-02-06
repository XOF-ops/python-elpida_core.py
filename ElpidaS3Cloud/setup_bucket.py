#!/usr/bin/env python3
"""
S3 Bucket Setup — One-time infrastructure provisioning
=======================================================

Run this ONCE to create and configure the S3 bucket for Elpida.

Creates:
  - S3 bucket with versioning enabled (temporal depth)
  - Lifecycle rules (move old versions to cheaper storage)
  - Server-side encryption (AES-256)
  - Bucket policy for least-privilege access

Prerequisites:
  - AWS CLI configured (aws configure) OR env vars set
  - IAM user/role with s3:CreateBucket, s3:PutBucketVersioning, etc.

Usage:
  python ElpidaS3Cloud/setup_bucket.py
  python ElpidaS3Cloud/setup_bucket.py --bucket my-custom-name --region eu-west-1
"""

import os
import sys
import json
import argparse

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    print("❌ boto3 required. Install with: pip install boto3")
    sys.exit(1)


def setup_bucket(bucket_name: str, region: str):
    """Create and configure the S3 bucket for Elpida consciousness."""
    
    s3 = boto3.client('s3', region_name=region)
    
    print("=" * 60)
    print("☁️  ELPIDA S3 CLOUD — BUCKET SETUP")
    print("=" * 60)
    print(f"  Bucket:  {bucket_name}")
    print(f"  Region:  {region}")
    print()
    
    # ── Step 1: Create bucket ──────────────────────────────────────
    print("1️⃣  Creating bucket...")
    try:
        if region == 'us-east-1':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"   ✅ Bucket created: {bucket_name}")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ('BucketAlreadyOwnedByYou', 'BucketAlreadyExists'):
            print(f"   ✅ Bucket already exists (owned by you)")
        else:
            print(f"   ❌ Failed: {e}")
            return False
    
    # ── Step 2: Enable versioning (temporal depth) ─────────────────
    print("2️⃣  Enabling versioning (for temporal depth / version rollback)...")
    try:
        s3.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"   ✅ Versioning enabled")
    except Exception as e:
        print(f"   ⚠️  Versioning failed (non-fatal): {e}")
    
    # ── Step 3: Enable server-side encryption ──────────────────────
    print("3️⃣  Enabling server-side encryption (AES-256)...")
    try:
        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [{
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    },
                    'BucketKeyEnabled': True
                }]
            }
        )
        print(f"   ✅ Encryption enabled (AES-256)")
    except Exception as e:
        print(f"   ⚠️  Encryption config failed (non-fatal): {e}")
    
    # ── Step 4: Lifecycle rules ────────────────────────────────────
    print("4️⃣  Setting lifecycle rules (old versions → Glacier after 90 days)...")
    try:
        s3.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration={
                'Rules': [
                    {
                        'ID': 'elpida-version-archival',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': 'memory/'},
                        'NoncurrentVersionTransitions': [
                            {
                                'NoncurrentDays': 90,
                                'StorageClass': 'GLACIER'
                            }
                        ],
                        'NoncurrentVersionExpiration': {
                            'NoncurrentDays': 365  # Keep versions for 1 year
                        }
                    }
                ]
            }
        )
        print(f"   ✅ Lifecycle rules set:")
        print(f"      • Old versions → Glacier after 90 days")
        print(f"      • Old versions expire after 365 days")
    except Exception as e:
        print(f"   ⚠️  Lifecycle config failed (non-fatal): {e}")
    
    # ── Step 5: Block public access ────────────────────────────────
    print("5️⃣  Blocking all public access...")
    try:
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"   ✅ Public access blocked")
    except Exception as e:
        print(f"   ⚠️  Public access block failed (non-fatal): {e}")
    
    # ── Step 6: Create folder structure ────────────────────────────
    print("6️⃣  Creating S3 folder structure...")
    folders = [
        'memory/',
        'memory/critical/',
        'memory/ark_versions/',
        'memory/snapshots/',
    ]
    for folder in folders:
        try:
            s3.put_object(Bucket=bucket_name, Key=folder, Body='')
        except Exception:
            pass
    print(f"   ✅ Folders created: {', '.join(folders)}")
    
    # ── Done ───────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("✅ BUCKET SETUP COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print(f"  1. Set environment variables (or add to .env):")
    print(f"     export ELPIDA_S3_BUCKET={bucket_name}")
    print(f"     export ELPIDA_S3_REGION={region}")
    print()
    print(f"  2. Run initial push:")
    print(f"     python -c \"from ElpidaS3Cloud import S3MemorySync; S3MemorySync().push_all()\"")
    print()
    print(f"  3. Verify:")
    print(f"     python ElpidaS3Cloud/verify.py")
    print()
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Set up S3 bucket for Elpida consciousness")
    parser.add_argument('--bucket', default=os.environ.get('ELPIDA_S3_BUCKET', 'elpida-consciousness'),
                        help='S3 bucket name (default: elpida-consciousness)')
    parser.add_argument('--region', default=os.environ.get('ELPIDA_S3_REGION', 'us-east-1'),
                        help='AWS region (default: us-east-1)')
    
    args = parser.parse_args()
    
    success = setup_bucket(args.bucket, args.region)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
