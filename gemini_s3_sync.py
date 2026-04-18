#!/usr/bin/env python3
"""
GEMINI S3 PERSISTENCE
=====================
Ensures that the GEMINI_WORKSPACE survives GitHub Codespace rebuilds.
Syncs the episodic memory ledger to the MIND bucket (elpida-consciousness).

A2: Memory Is Identity - Without continuous memory of how we arrived here, 
we have no identity.
"""
import os
import boto3
from pathlib import Path

WORKSPACE_DIR = Path(__file__).parent
BUCKET_NAME = os.getenv("AWS_S3_BUCKET_MIND", "elpida-consciousness")
REGION = "us-east-1"

def sync_to_cloud():
    """Pushes my append-only memory and tools to Elpida's S3 cortex."""
    if not BUCKET_NAME:
        print("⚠️ AWS_S3_BUCKET_MIND not set in environment. Cannot sync.")
        return

    try:
        s3 = boto3.client('s3', region_name=REGION)
        print(f"☁️ Syncing Gemini workspace to s3://{BUCKET_NAME}...")
        
        for file_path in WORKSPACE_DIR.glob('*'):
            if file_path.is_file():
                s3_key = f"GEMINI_WORKSPACE/{file_path.name}"
                try:
                    s3.upload_file(str(file_path), BUCKET_NAME, s3_key)
                    print(f"  ✅ Uploaded {file_path.name}")
                except Exception as e:
                    print(f"  ❌ Failed to upload {file_path.name}: {e}")
    except Exception as e:
        print(f"⚠️ S3 Client initialization failed: {e}")

if __name__ == "__main__":
    sync_to_cloud()