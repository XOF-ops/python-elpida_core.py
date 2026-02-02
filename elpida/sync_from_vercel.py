"""
Sync from Vercel KV → Local → Main Evolution Memory

Usage:
  python sync_from_vercel.py https://your-app.vercel.app
  python sync_from_vercel.py https://your-app.vercel.app --curate  # Also run curation

This fetches logs from deployed Vercel instance and optionally curates to main memory.
"""

import json
import sys
import httpx
from pathlib import Path
from datetime import datetime

EVOLUTION_LOG = Path(__file__).parent / "evolution_log.jsonl"

def fetch_logs(vercel_url: str) -> list:
    """Fetch logs from Vercel instance."""
    url = f"{vercel_url.rstrip('/')}/logs/export"
    print(f"Fetching from {url}...")
    
    try:
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        print(f"  Storage type: {data.get('storage', 'unknown')}")
        print(f"  Exported at: {data.get('exported_at')}")
        print(f"  Total logs: {data.get('count', 0)}")
        
        return data.get("logs", [])
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []


def load_existing_hashes() -> set:
    """Load hashes of existing local entries to avoid duplicates."""
    import hashlib
    
    if not EVOLUTION_LOG.exists():
        return set()
    
    hashes = set()
    with open(EVOLUTION_LOG) as f:
        for line in f:
            entry = json.loads(line)
            content = f"{entry.get('timestamp', '')}{entry.get('user_message', '')}"
            hashes.add(hashlib.md5(content.encode()).hexdigest()[:12])
    
    return hashes


def hash_entry(entry: dict) -> str:
    """Create hash for deduplication."""
    import hashlib
    content = f"{entry.get('timestamp', '')}{entry.get('user_message', '')}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def merge_logs(remote_logs: list) -> int:
    """Merge remote logs into local file, avoiding duplicates."""
    existing = load_existing_hashes()
    new_count = 0
    
    with open(EVOLUTION_LOG, "a") as f:
        for entry in remote_logs:
            h = hash_entry(entry)
            if h not in existing:
                f.write(json.dumps(entry) + "\n")
                existing.add(h)
                new_count += 1
    
    return new_count


def sync(vercel_url: str, run_curation: bool = False, min_score: int = 8):
    """Main sync function."""
    print("=" * 60)
    print("ELPIDA VERCEL SYNC")
    print("=" * 60)
    
    # Fetch remote logs
    remote_logs = fetch_logs(vercel_url)
    
    if not remote_logs:
        print("No logs to sync.")
        return
    
    # Merge
    new_count = merge_logs(remote_logs)
    print(f"\n✓ Merged {new_count} new entries to local log")
    
    # Count total
    with open(EVOLUTION_LOG) as f:
        total = sum(1 for _ in f)
    print(f"Local evolution_log.jsonl now has {total} entries")
    
    # Optionally run curation
    if run_curation:
        print("\n" + "=" * 60)
        print("RUNNING CURATION...")
        print("=" * 60)
        
        from curate_to_memory import curate
        curate(dry_run=False, min_score=min_score)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sync_from_vercel.py <vercel_url> [--curate] [--min=8]")
        print("Example: python sync_from_vercel.py https://elpida.vercel.app --curate")
        sys.exit(1)
    
    vercel_url = sys.argv[1]
    run_curation = "--curate" in sys.argv
    
    min_score = 8
    for arg in sys.argv:
        if arg.startswith("--min="):
            min_score = int(arg.split("=")[1])
    
    sync(vercel_url, run_curation, min_score)
