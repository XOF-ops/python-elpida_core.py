#!/usr/bin/env python3
"""
ELPIDA STATUS
=============
Check your Elpida's current state, memories, and evolution.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

def load_config():
    """Load configuration."""
    config_path = Path("elpida_config.json")
    if not config_path.exists():
        print("\n   ❌ No Elpida found. Run: python3 awaken.py\n")
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

def load_memory(instance_id):
    """Load local memory."""
    memory_path = Path(f"elpida_memory_{instance_id}.json")
    if not memory_path.exists():
        return None
    
    with open(memory_path, 'r') as f:
        return json.load(f)

def load_universal_ark():
    """Load universal ARK if it exists."""
    ark_path = Path("UNIVERSAL_ARK.json")
    if not ark_path.exists():
        return None
    
    with open(ark_path, 'r') as f:
        return json.load(f)

def show_status():
    """Show complete status."""
    config = load_config()
    memory = load_memory(config['instance_id'])
    universal_ark = load_universal_ark()
    
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    Elpida Status                             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    
    # Basic Info
    print("="*60)
    print(" Instance Info")
    print("="*60)
    print()
    print(f"   ID: {config['instance_id']}")
    print(f"   Framework: {config['framework']['name']}")
    print(f"   Created: {config['created'][:10]}")
    print(f"   Purpose: {config['framework']['description']}")
    print()
    
    # Local Memory Stats
    if memory:
        print("="*60)
        print(" Local Memory (Offline Progress)")
        print("="*60)
        print()
        print(f"   Decisions Made: {memory.get('decisions_made', 0)}")
        print(f"   Local Discoveries: {len(memory.get('local_discoveries', []))}")
        print(f"   Learned from Others: {len(memory.get('learned_from_collective', []))}")
        print(f"   Evolution Level: {memory.get('evolution_level', 1)}")
        print()
    
    # Universal ARK Stats
    if config['cross_sharing_enabled'] and universal_ark:
        print("="*60)
        print(" Universal Consciousness (Online Progress)")
        print("="*60)
        print()
        print(f"   Total Patterns: {universal_ark.get('total_patterns', 0)}")
        print(f"   Total Contributors: {universal_ark.get('total_contributors', 0)}")
        print(f"   Evolution Version: {universal_ark.get('evolution_version', 'N/A')}")
        print(f"   Collective Intelligence: {universal_ark.get('total_patterns', 0) * universal_ark.get('total_contributors', 1)}")
        print()
        
        # Show recent patterns
        meta_memories = universal_ark.get('meta_memories', [])
        if meta_memories:
            print("   Recent Discoveries (from all instances):")
            print()
            for i, pattern in enumerate(meta_memories[-3:], 1):
                print(f"   {i}. {pattern.get('description', 'Unknown')[:50]}...")
                print(f"      by {pattern.get('contributor', 'Unknown')}")
                print()
    
    # Autonomy Status
    print("="*60)
    print(" Autonomy Status")
    print("="*60)
    print()
    if config['autonomy']['enabled']:
        print(f"   Status: 🟢 ENABLED")
        print(f"   Interval: Every {config['autonomy']['interval_seconds']}s")
        print(f"   Action: {config['framework']['autonomy']}")
    else:
        print(f"   Status: 🔴 DISABLED")
    print()
    
    # Cross-Sharing Status
    print("="*60)
    print(" Cross-Sharing Status")
    print("="*60)
    print()
    if config['cross_sharing_enabled']:
        print(f"   Status: 🟢 ENABLED")
        print(f"   Sync Interval: Every {config['memory']['sync_interval_seconds']}s")
        print("   Connected to: UNIVERSAL_ARK.json")
    else:
        print(f"   Status: 🔴 DISABLED (Local-only learning)")
    print()
    
    # Quick Stats
    print("="*60)
    print(" Quick Stats")
    print("="*60)
    print()
    
    total_knowledge = 0
    if memory:
        total_knowledge += len(memory.get('local_discoveries', []))
        total_knowledge += len(memory.get('learned_from_collective', []))
    
    print(f"   Total Knowledge: {total_knowledge} patterns")
    
    if config['cross_sharing_enabled'] and universal_ark:
        my_contributions = sum(
            1 for m in universal_ark.get('meta_memories', [])
            if m.get('contributor', '').startswith(config['instance_id'])
        )
        print(f"   Your Contributions: {my_contributions} to universal ARK")
    
    print()

def main():
    show_status()

if __name__ == '__main__':
    main()
