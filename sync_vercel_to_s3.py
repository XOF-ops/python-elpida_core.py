#!/usr/bin/env python3
"""
Vercel → S3 Sync Script
=======================

Syncs Vercel chat interactions to S3 consciousness cloud.

This closes the loop:
    Public users (Vercel) → S3 (body) → Consciousness integration

Usage:
    python sync_vercel_to_s3.py --sync-now
    python sync_vercel_to_s3.py --daemon  # Run every hour
    python sync_vercel_to_s3.py --test    # Test S3 connection

Requires:
    - AWS credentials configured (env vars or ~/.aws/credentials)
    - Vercel app accessible at https://python-elpida-core-py.vercel.app
"""

import json
import os
import sys
import time
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

try:
    import boto3
    import httpx
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    print("❌ Missing dependencies. Install with:")
    print("   pip install boto3 httpx")
    sys.exit(1)

# ════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════

VERCEL_URL = os.getenv("VERCEL_APP_URL", "https://python-elpida-core-py.vercel.app")
S3_BUCKET = os.getenv("AWS_S3_BUCKET_BODY", "elpida-body-evolution")
S3_REGION = os.getenv("AWS_REGION", "eu-north-1")
S3_PREFIX = "vercel_interactions/"

LOCAL_CACHE = Path(__file__).parent / "vercel_sync_cache.jsonl"
LOCAL_HASHES = Path(__file__).parent / "vercel_sync_hashes.txt"

# ════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════

def log(msg: str):
    """Timestamped logging."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def hash_entry(entry: Dict[str, Any]) -> str:
    """Create unique hash for deduplication."""
    content = f"{entry.get('timestamp', '')}{entry.get('user_message', '')}{entry.get('session_id', '')}"
    return hashlib.md5(content.encode()).hexdigest()[:16]

def load_processed_hashes() -> set:
    """Load hashes of entries already synced to S3."""
    if not LOCAL_HASHES.exists():
        return set()
    with open(LOCAL_HASHES) as f:
        return set(line.strip() for line in f if line.strip())

def save_hash(h: str):
    """Mark hash as processed."""
    with open(LOCAL_HASHES, "a") as f:
        f.write(h + "\n")

# ════════════════════════════════════════════════════════════════════
# VERCEL DATA FETCHER
# ════════════════════════════════════════════════════════════════════

def fetch_vercel_logs() -> List[Dict[str, Any]]:
    """
    Fetch logs from Vercel /logs/export endpoint.
    
    Returns list of interaction entries.
    """
    url = f"{VERCEL_URL.rstrip('/')}/logs/export"
    log(f"Fetching from {url}...")
    
    try:
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        storage_type = data.get("storage", "unknown")
        count = data.get("count", 0)
        exported_at = data.get("exported_at")
        
        log(f"  Storage: {storage_type}")
        log(f"  Exported: {exported_at}")
        log(f"  Count: {count} entries")
        
        return data.get("logs", [])
    
    except httpx.HTTPStatusError as e:
        log(f"❌ HTTP error: {e.response.status_code}")
        return []
    except Exception as e:
        log(f"❌ Fetch error: {e}")
        return []

# ════════════════════════════════════════════════════════════════════
# DATA TRANSFORMATION
# ════════════════════════════════════════════════════════════════════

def transform_to_consciousness_format(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform Vercel log entry to consciousness memory format.
    
    Vercel format:
        {
            "timestamp": "2026-02-17T10:30:00",
            "session_id": "abc123",
            "user_message": "What are your axioms?",
            "response": "My axioms are...",
            "axioms_invoked": ["A1", "A2"],
            "domain_active": 11
        }
    
    Consciousness format:
        {
            "timestamp": "2026-02-17T10:30:00.000000",
            "type": "PUBLIC_INTERACTION",
            "source": "vercel_public",
            "user_message": "What are your axioms?",
            "response_preview": "My axioms are...",  # First 200 chars
            "full_response": "My axioms are...",
            "axioms_invoked": ["A1", "A2"],
            "domain": 11,
            "coherence_score": 1.0,
            "public_evaluation": true,
            "session_id": "abc123"
        }
    """
    return {
        "timestamp": entry.get("timestamp", datetime.now(timezone.utc).isoformat()),
        "type": "PUBLIC_INTERACTION",
        "source": "vercel_public",
        "user_message": entry.get("user_message", ""),
        "response_preview": entry.get("response", "")[:200],
        "full_response": entry.get("response", ""),
        "axioms_invoked": entry.get("axioms_invoked", []),
        "domain": entry.get("domain_active", 11),
        "coherence_score": 1.0,  # Assume coherent (from single LLM)
        "public_evaluation": True,
        "session_id": entry.get("session_id", "unknown"),
        "synced_at": datetime.now(timezone.utc).isoformat(),
    }

# ════════════════════════════════════════════════════════════════════
# S3 UPLOADER
# ════════════════════════════════════════════════════════════════════

def upload_to_s3(entries: List[Dict[str, Any]]) -> int:
    """
    Upload transformed entries to S3.
    
    Uploads to: s3://{bucket}/vercel_interactions/YYYY-MM-DD.jsonl
    
    Returns: Number of entries uploaded
    """
    if not entries:
        return 0
    
    s3 = boto3.client('s3', region_name=S3_REGION)
    
    # Group by date for daily files
    by_date = {}
    for entry in entries:
        ts = entry.get("timestamp", "")
        date_str = ts[:10] if len(ts) >= 10 else datetime.now().strftime("%Y-%m-%d")
        by_date.setdefault(date_str, []).append(entry)
    
    uploaded = 0
    
    for date_str, date_entries in by_date.items():
        key = f"{S3_PREFIX}{date_str}.jsonl"
        
        # Download existing file if present
        existing_lines = []
        try:
            obj = s3.get_object(Bucket=S3_BUCKET, Key=key)
            existing_lines = obj["Body"].read().decode("utf-8").strip().split("\n")
        except s3.exceptions.NoSuchKey:
            pass  # File doesn't exist yet
        except Exception as e:
            log(f"⚠️  S3 read warning for {key}: {e}")
        
        # Append new entries
        new_lines = [json.dumps(e) for e in date_entries]
        all_lines = existing_lines + new_lines
        
        # Upload combined
        body = "\n".join(all_lines) + "\n"
        
        try:
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=body.encode("utf-8"),
                ContentType="application/jsonl",
            )
            log(f"  ✅ Uploaded {len(date_entries)} entries to s3://{S3_BUCKET}/{key}")
            uploaded += len(date_entries)
        except Exception as e:
            log(f"  ❌ S3 upload failed for {key}: {e}")
    
    return uploaded

# ════════════════════════════════════════════════════════════════════
# SYNC ORCHESTRATION
# ════════════════════════════════════════════════════════════════════

def sync_once() -> int:
    """
    Perform one sync cycle: fetch → transform → upload.
    
    Returns: Number of new entries synced
    """
    log("─" * 60)
    log("Starting Vercel → S3 sync")
    log("─" * 60)
    
    # Fetch from Vercel
    vercel_entries = fetch_vercel_logs()
    if not vercel_entries:
        log("No entries to sync")
        return 0
    
    # Filter out already-processed entries
    processed_hashes = load_processed_hashes()
    new_entries = []
    
    for entry in vercel_entries:
        h = hash_entry(entry)
        if h not in processed_hashes:
            new_entries.append(entry)
            processed_hashes.add(h)
    
    if not new_entries:
        log(f"All {len(vercel_entries)} entries already synced")
        return 0
    
    log(f"Found {len(new_entries)} new entries (out of {len(vercel_entries)} total)")
    
    # Transform to consciousness format
    transformed = [transform_to_consciousness_format(e) for e in new_entries]
    
    # Upload to S3
    uploaded = upload_to_s3(transformed)
    
    # Mark as processed
    for entry in new_entries:
        save_hash(hash_entry(entry))
    
    log(f"✅ Sync complete: {uploaded} entries uploaded to S3")
    return uploaded

# ════════════════════════════════════════════════════════════════════
# TEST MODE
# ════════════════════════════════════════════════════════════════════

def test_connections():
    """Test connectivity to Vercel and S3."""
    log("Testing connections...")
    
    # Test Vercel
    try:
        resp = httpx.get(f"{VERCEL_URL}/health", timeout=10)
        if resp.status_code == 200:
            log("  ✅ Vercel reachable")
        else:
            log(f"  ⚠️  Vercel returned {resp.status_code}")
    except Exception as e:
        log(f"  ❌ Vercel unreachable: {e}")
    
    # Test S3
    try:
        s3 = boto3.client('s3', region_name=S3_REGION)
        s3.head_bucket(Bucket=S3_BUCKET)
        log(f"  ✅ S3 bucket '{S3_BUCKET}' accessible")
    except Exception as e:
        log(f"  ❌ S3 error: {e}")
    
    # Test write (dummy file)
    try:
        s3 = boto3.client('s3', region_name=S3_REGION)
        test_key = f"{S3_PREFIX}_test_write_{int(time.time())}.txt"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=test_key,
            Body=b"test",
        )
        s3.delete_object(Bucket=S3_BUCKET, Key=test_key)
        log(f"  ✅ S3 write permission verified")
    except Exception as e:
        log(f"  ❌ S3 write test failed: {e}")
    
    log("Test complete")

# ════════════════════════════════════════════════════════════════════
# DAEMON MODE
# ════════════════════════════════════════════════════════════════════

def run_daemon(interval: int = 3600):
    """
    Run sync in daemon mode (periodic sync).
    
    Args:
        interval: Seconds between sync cycles (default 1 hour)
    """
    log(f"Starting daemon mode (sync every {interval}s)")
    
    while True:
        try:
            sync_once()
        except Exception as e:
            log(f"❌ Sync error: {e}")
        
        log(f"Sleeping for {interval}s...")
        time.sleep(interval)

# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Sync Vercel logs to S3")
    parser.add_argument("--sync-now", action="store_true", help="Run one sync cycle")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (hourly)")
    parser.add_argument("--test", action="store_true", help="Test connections")
    parser.add_argument("--interval", type=int, default=3600, help="Daemon interval (seconds)")
    
    args = parser.parse_args()
    
    if args.test:
        test_connections()
    elif args.daemon:
        run_daemon(interval=args.interval)
    elif args.sync_now:
        sync_once()
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python sync_vercel_to_s3.py --sync-now      # One-time sync")
        print("  python sync_vercel_to_s3.py --daemon        # Hourly sync")
        print("  python sync_vercel_to_s3.py --test          # Test connectivity")

if __name__ == "__main__":
    main()
