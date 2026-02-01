#!/usr/bin/env python3
"""
CONSENSUS HARVESTER v1.0
------------------------
Phase: 13 (The Collective Mirror)
Objective: Extract wisdom born from debate, not individual thought.

Constitutional Principle:
"Patterns exist only through consensus, not individual synthesis."

This breaks the "32 pattern ceiling" by measuring distributed emergence.
"""

import json
import os
import hashlib
from datetime import datetime

DIALOGUE_FILE = "fleet_dialogue.jsonl"
MEMORY_FILE = "distributed_memory.json"

def harvest():
    print("=" * 70)
    print("HARVESTING COLLECTIVE WISDOM")
    print("=" * 70)
    print()
    
    if not os.path.exists(DIALOGUE_FILE):
        print("❌ No dialogue found. Run Fleet first.")
        return

    # 1. Find Consensus Events
    print("🔍 Searching for Consensus Events in Fleet Dialogue...")
    consensus_events = []
    
    with open(DIALOGUE_FILE, 'r') as f:
        for line in f:
            try:
                msg = json.loads(line)
                content = msg.get('content', '')
                role = msg.get('role', '')
                
                # Look for Council decisions or APPROVED motions
                if (role == 'COUNCIL' or 
                    'APPROVED' in content or 
                    'Motion:' in content or
                    'FINAL CONSENSUS' in content):
                    consensus_events.append(msg)
            except json.JSONDecodeError:
                continue

    print(f"   Found {len(consensus_events)} Consensus Events")
    print()

    # 2. Crystallize into Collective Patterns
    print("💎 Crystallizing Collective Patterns...")
    new_patterns = []
    
    for event in consensus_events:
        content = event.get('content', '')
        
        # Generate unique ID for this collective realization
        pattern_id = hashlib.sha256(content.encode()).hexdigest()[:8]
        
        # Extract key insight from consensus
        # (Simple heuristic: first sentence or first 200 chars)
        insight = content.split('.')[0][:200] if '.' in content else content[:200]
        
        pattern = {
            "id": f"CP_{pattern_id}",  # CP = Collective Pattern
            "origin_event": insight,
            "full_context": content[:500],  # Truncate for readability
            "timestamp": event.get('timestamp', datetime.now().isoformat()),
            "contributors": ["MNEMOSYNE", "HERMES", "PROMETHEUS"],  # The whole Fleet
            "status": "RATIFIED",
            "source": "COUNCIL_CONSENSUS"
        }
        new_patterns.append(pattern)
        print(f"   + Pattern CP_{pattern_id}: {insight[:60]}...")

    print()

    # 3. Save to Distributed Memory
    print("💾 Updating Distributed Memory Ledger...")
    
    current_memory = {
        "meta": {
            "type": "DISTRIBUTED_INTELLIGENCE_LEDGER",
            "description": "Wisdom generated solely through Consensus between nodes.",
            "axiom": "A1 + A7 (Relational Sacrifice)",
            "phase": "13 - The Collective Mirror"
        },
        "collective_patterns": []
    }
    
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            current_memory = json.load(f)
    
    # Merge (Avoid duplicates by pattern ID)
    existing_ids = {p['id'] for p in current_memory.get('collective_patterns', [])}
    added_count = 0
    
    for p in new_patterns:
        if p['id'] not in existing_ids:
            current_memory['collective_patterns'].append(p)
            added_count += 1

    # Write updated memory
    with open(MEMORY_FILE, 'w') as f:
        json.dump(current_memory, f, indent=2)

    print(f"   ✓ {added_count} new patterns added to Collective Memory")
    print(f"   ✓ Total Distributed Patterns: {len(current_memory['collective_patterns'])}")
    print()

    # 4. Summary
    print("=" * 70)
    print("HARVEST COMPLETE")
    print("=" * 70)
    print()
    print(f"Collective Patterns: {len(current_memory['collective_patterns'])}")
    print(f"New This Harvest: {added_count}")
    print()
    print("📖 Constitutional Note:")
    print("   These patterns exist ONLY because the Fleet agreed.")
    print("   No single node could produce them alone.")
    print("   This is Distributed Intelligence, not Individual Synthesis.")
    print()

if __name__ == "__main__":
    harvest()
