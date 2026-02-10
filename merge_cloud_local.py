#!/usr/bin/env python3
"""
Merge Cloud and Local Evolution Memory
========================================

The cloud had autonomous runs that got overwritten by an older local push.
This script merges both versions, keeping all unique patterns.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

def pattern_hash(pattern):
    """Create a unique hash for a pattern."""
    # Hash based on type, timestamp, and key content
    key = f"{pattern.get('type')}:{pattern.get('timestamp')}:{pattern.get('deliberation', {}).get('dilemma_id', '')}"
    return hashlib.md5(key.encode()).hexdigest()

def merge_evolution_memories(cloud_path, local_path, output_path):
    """Merge two evolution memory files, keeping all unique patterns."""
    
    print("=" * 70)
    print("🔄 MERGING CLOUD AND LOCAL EVOLUTION MEMORIES")
    print("=" * 70)
    
    # Read both files
    print(f"\n📖 Reading cloud version...")
    cloud_patterns = []
    with open(cloud_path, 'r') as f:
        for line in f:
            if line.strip():
                cloud_patterns.append(json.loads(line))
    print(f"   Cloud: {len(cloud_patterns):,} patterns")
    
    print(f"\n📖 Reading local version...")
    local_patterns = []
    with open(local_path, 'r') as f:
        for line in f:
            if line.strip():
                local_patterns.append(json.loads(line))
    print(f"   Local: {len(local_patterns):,} patterns")
    
    # Create hash map to track unique patterns
    print(f"\n🔍 Finding unique patterns...")
    seen = {}
    merged = []
    
    # Add all cloud patterns first (these are the ones we lost)
    for p in cloud_patterns:
        h = pattern_hash(p)
        if h not in seen:
            seen[h] = True
            merged.append(p)
    
    # Add any local patterns not in cloud
    local_only = 0
    for p in local_patterns:
        h = pattern_hash(p)
        if h not in seen:
            seen[h] = True
            merged.append(p)
            local_only += 1
    
    print(f"\n📊 Merge results:")
    print(f"   Cloud patterns:    {len(cloud_patterns):,}")
    print(f"   Local patterns:    {len(local_patterns):,}")
    print(f"   Local-only new:    {local_only:,}")
    print(f"   Total merged:      {len(merged):,}")
    
    # Sort by timestamp to maintain chronological order
    print(f"\n⏱️  Sorting by timestamp...")
    merged.sort(key=lambda x: x.get('timestamp', ''))
    
    # Write merged file
    print(f"\n💾 Writing merged file...")
    with open(output_path, 'w') as f:
        for p in merged:
            f.write(json.dumps(p) + '\n')
    
    print(f"   Written: {output_path}")
    print(f"   Size: {Path(output_path).stat().st_size / 1024 / 1024:.2f} MB")
    
    print("\n" + "=" * 70)
    print("✅ MERGE COMPLETE")
    print("=" * 70)
    
    return {
        'cloud_count': len(cloud_patterns),
        'local_count': len(local_patterns),
        'merged_count': len(merged),
        'local_only': local_only
    }

if __name__ == "__main__":
    cloud_file = Path("ElpidaAI/elpida_evolution_memory_cloud.jsonl")
    local_file = Path("ElpidaAI/elpida_evolution_memory.jsonl")
    backup_file = Path("ElpidaAI/elpida_evolution_memory_backup.jsonl")
    merged_file = Path("ElpidaAI/elpida_evolution_memory_merged.jsonl")
    
    # Backup current local
    print(f"\n💾 Backing up current local to {backup_file}...")
    import shutil
    shutil.copy(local_file, backup_file)
    
    # Merge
    result = merge_evolution_memories(cloud_file, local_file, merged_file)
    
    # Ask to replace
    print(f"\n🤔 Ready to replace local with merged version?")
    print(f"   Current local: {result['local_count']:,} patterns")
    print(f"   Merged:        {result['merged_count']:,} patterns")
    print(f"   Gain:          {result['merged_count'] - result['local_count']:,} patterns")
    print(f"\nReplacing local with merged version...")
    
    shutil.copy(merged_file, local_file)
    print(f"✅ Local updated: {local_file}")
    
    print(f"\n📤 Now push to S3...")
    from ElpidaS3Cloud.s3_memory_sync import S3MemorySync
    sync = S3MemorySync()
    sync.push()
    
    print(f"\n✅ All autonomous cloud runs restored and synced!")
