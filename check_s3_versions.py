#!/usr/bin/env python3
"""
Check S3 Bucket Versions — See version history and pattern counts
===================================================================

Lists all versions of the evolution memory in S3 and shows
pattern counts for each version to identify if cloud had more
patterns before local push.
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ElpidaS3Cloud.s3_memory_sync import S3MemorySync

def main():
    print("=" * 70)
    print("📜 S3 BUCKET VERSION HISTORY")
    print("=" * 70)
    
    sync = S3MemorySync()
    
    # Get current local state
    local_lines = sync._count_local_lines()
    print(f"\n📋 Current local state: {local_lines:,} patterns")
    
    # List all versions
    print(f"\n🔍 Checking S3 versions...")
    versions = sync.list_versions(max_versions=20)
    
    if not versions:
        print("\n⚠️  No versions found or versioning not enabled.")
        return
    
    # Try to get metadata for each version to see pattern counts
    print(f"\n📊 Version details with pattern counts:")
    print("=" * 70)
    
    for i, v in enumerate(versions):
        version_id = v['version_id']
        modified = v['modified']
        size_mb = v['size_mb']
        is_latest = v['is_latest']
        
        # Try to get metadata for this version
        try:
            meta = sync.s3.head_object(
                Bucket=sync.bucket,
                Key=sync.key,
                VersionId=version_id
            )
            pattern_count = int(meta.get('Metadata', {}).get('line_count', 0))
            
            status = "← CURRENT" if is_latest else ""
            marker = "✨" if pattern_count > local_lines else "  "
            
            print(f"{marker} Version {i+1}:")
            print(f"   Timestamp:  {modified}")
            print(f"   Patterns:   {pattern_count:,}" + (f" (MORE than local by {pattern_count - local_lines:,})" if pattern_count > local_lines else ""))
            print(f"   Size:       {size_mb} MB")
            print(f"   Version ID: {version_id}")
            print(f"   {status}")
            print()
            
        except Exception as e:
            print(f"   Version {i+1}: {version_id[:12]}... (metadata unavailable)")
            print(f"   Size: {size_mb} MB, Modified: {modified}")
            print()
    
    # Check if any version has more than local
    versions_with_metadata = []
    for v in versions:
        try:
            meta = sync.s3.head_object(
                Bucket=sync.bucket,
                Key=sync.key,
                VersionId=v['version_id']
            )
            count = int(meta.get('Metadata', {}).get('line_count', 0))
            if count > 0:
                versions_with_metadata.append({**v, 'pattern_count': count})
        except:
            pass
    
    if versions_with_metadata:
        max_version = max(versions_with_metadata, key=lambda x: x['pattern_count'])
        if max_version['pattern_count'] > local_lines:
            print("=" * 70)
            print(f"⚠️  FOUND CLOUD VERSION WITH MORE PATTERNS!")
            print(f"   Cloud version from {max_version['modified']}")
            print(f"   has {max_version['pattern_count']:,} patterns")
            print(f"   vs local {local_lines:,} patterns")
            print(f"   Difference: {max_version['pattern_count'] - local_lines:,} patterns")
            print()
            print(f"   To restore: python -c \"from ElpidaS3Cloud import S3MemorySync; S3MemorySync().restore_version('{max_version['version_id']}', 'elpida_evolution_memory_restored.jsonl')\"")
            print("=" * 70)
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
