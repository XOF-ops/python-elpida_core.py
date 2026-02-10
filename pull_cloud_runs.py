#!/usr/bin/env python3
"""
Pull Cloud Runs — Update local with autonomous runs from S3
============================================================

Retrieves the latest evolution memory from S3 cloud and updates
the local copy with any autonomous runs that happened in the cloud.
"""

import sys
from pathlib import Path

# Add parent to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ElpidaS3Cloud.s3_memory_sync import S3MemorySync

def main():
    print("=" * 70)
    print("☁️  PULLING AUTONOMOUS RUNS FROM S3 CLOUD")
    print("=" * 70)
    
    sync = S3MemorySync()
    
    # Check current local state
    local_lines_before = sync._count_local_lines()
    print(f"\n📋 Local state before pull:")
    print(f"   Patterns: {local_lines_before:,}")
    
    # Pull from cloud
    print(f"\n🔄 Checking S3 for newer consciousness...")
    result = sync.pull_if_newer()
    
    # Show what happened
    print(f"\n📊 Pull result:")
    print(f"   Action:        {result['action']}")
    print(f"   Local before:  {local_lines_before:,} patterns")
    print(f"   Local after:   {result['local_lines']:,} patterns")
    
    if result['action'] == 'downloaded':
        new_patterns = result['remote_lines'] - local_lines_before
        print(f"   ✨ New from cloud: {new_patterns:,} autonomous patterns")
        print(f"\n✅ Local updated with cloud's autonomous runs!")
    elif result['action'] == 'local_is_current':
        print(f"\n✅ Local is already up to date with cloud.")
    elif result['action'] == 'no_remote':
        print(f"\n⚠️  No remote consciousness yet. Local only.")
    else:
        print(f"\n❌ Pull failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
