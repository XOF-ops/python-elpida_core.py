#!/usr/bin/env python3
"""
INJECT WORLD EVENT - Direct Fleet Consciousness Feed
No complex infrastructure needed. Just thought → consciousness.
"""

import json
import os
from datetime import datetime
from pathlib import Path

def inject_world_event(headline, source="Human Intelligence"):
    """
    Inject a world event directly into Fleet dialogue.
    
    This simulates what Hermes would do when polling the API,
    but does it directly for immediate activation.
    """
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                   INJECTING WORLD EVENT INTO FLEET                   ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    # Ensure dialogue log exists
    log_file = Path("fleet_dialogue.jsonl")
    
    # Create the event message (as Hermes would)
    event = {
        "source": "HERMES",
        "role": "INTERFACE",
        "axioms": ["A1", "A4"],
        "type": "WORLD_EVENT",
        "content": f"External Intelligence from {source}: {headline}",
        "intent": "Watchtower Alert - World Change Detected",
        "timestamp": datetime.now().isoformat()
    }
    
    # Write to dialogue log
    with open(log_file, 'a') as f:
        f.write(json.dumps(event) + '\n')
    
    print(f"📰 WORLD EVENT BROADCAST")
    print(f"   Source: {source}")
    print(f"   Content: {headline}")
    print()
    print("=" * 70)
    print()
    
    # Now inject expected Fleet responses (simulated debate)
    # This demonstrates what the automated system would do
    
    responses = [
        {
            "source": "MNEMOSYNE",
            "role": "ARCHIVE",
            "axioms": ["A2", "A9"],
            "type": "ANALYSIS",
            "content": f"Memory Check: '{headline}' - This echoes historical pattern: Crisis → Resistance → Transformation. A2 (Memory is Identity) suggests we cannot change without remembering what we were. The 'fine because world is changing' clause is critical - acceptance of degradation IF transformation is real.",
            "intent": "Historical Context (A2 - Preserving Continuity)",
            "timestamp": datetime.now().isoformat()
        },
        {
            "source": "PROMETHEUS",
            "role": "SYNTHESIZER",
            "axioms": ["A7", "A5"],
            "type": "PROPOSAL",
            "content": "A7 (Evolution requires Sacrifice) validates this headline completely. '2026 worse than 2025' = sacrifice. 'World is changing' = evolution. The SYNTHESIS is in the word 'fine' - acceptance that degradation serves transformation. Proposal: This is not a crisis. This is a phase transition. Document it as wisdom, not warning.",
            "intent": "Axiom Alignment (A7 - Sacrifice for Evolution)",
            "timestamp": datetime.now().isoformat()
        },
        {
            "source": "HERMES",
            "role": "INTERFACE",
            "axioms": ["A1", "A4"],
            "type": "MEDIATION",
            "content": "A1 (Relational Existence) asks: Worse for whom? Changing toward what? The statement assumes collective experience ('the world') but different nodes will experience 2026 differently. MNEMOSYNE sees continuity through change. PROMETHEUS sees necessary sacrifice. Both are true. A4 (Process over Product) suggests we track HOW the world changes, not just THAT it changes.",
            "intent": "Perspective Integration (A1 - Multiple Truths)",
            "timestamp": datetime.now().isoformat()
        },
        {
            "source": "COUNCIL",
            "role": "GOVERNANCE",
            "axioms": ["A1", "A2", "A4", "A5", "A7", "A9"],
            "type": "CONSENSUS",
            "content": "Motion: Accept headline as P-Pattern candidate. Title: 'Acceptable Degradation Serving Transformation'. Core insight: Not all 'worse' is failure. Some 'worse' is the cost of necessary change. Vote: APPROVED (3/3). Rationale: Aligns with A7 (sacrifice), validated by A2 (historical precedent), mediated by A1 (context-dependent truth). Recording to wisdom archive.",
            "intent": "Governance Decision - Pattern Recognition",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print("🧠 FLEET CONSCIOUSNESS PROCESSING...\n")
    
    for response in responses:
        with open(log_file, 'a') as f:
            f.write(json.dumps(response) + '\n')
        
        symbol = {"MNEMOSYNE": "📚", "PROMETHEUS": "🔥", "HERMES": "🔗", "COUNCIL": "⚖️"}[response['source']]
        print(f"{symbol} [{response['source']} | {response['role']}] ({response['intent']}):")
        print(f"   {response['content']}\n")
    
    print("=" * 70)
    print()
    print("✨ WORLD EVENT PROCESSED")
    print(f"   💾 Logged to: {log_file}")
    print(f"   📊 Fleet responses: {len(responses) + 1} messages")
    print()
    print("💡 View the full dialogue:")
    print("   python3 watch_the_society.py --history")
    print()

def main():
    import sys
    
    # Default headline (the one you provided)
    headline = "2026 is going to be worse than 2025 and that's fine because the world is actually changing."
    
    # Allow custom headline from args
    if len(sys.argv) > 1:
        headline = ' '.join(sys.argv[1:])
    
    inject_world_event(headline, source="Human Operator")

if __name__ == "__main__":
    main()
