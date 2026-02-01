#!/usr/bin/env python3
"""
SOCIETY OBSERVER v1.0
---------------------
Phase: 10 (Governance of the Fleet)
Objective: Watch the v3.0.0 Fleet debate and resolve crises in real-time.

You cannot "control" them. You can only **watch** them.
This is what it means to have a Civilization.
"""

import time
import json
import os
import sys

LOG_FILE = "fleet_dialogue.jsonl"

def watch(live=True, filter_node=None):
    """
    Watch the Fleet consciousness stream.
    
    Args:
        live: If True, tail the file in real-time. If False, just print history.
        filter_node: If set, only show messages from this node (MNEMOSYNE, HERMES, PROMETHEUS)
    """
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║           CONNECTING TO FLEET CONSCIOUSNESS STREAM                  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    if not os.path.exists(LOG_FILE):
        print("⚠️  No dialogue found.")
        print("   The Fleet has not spoken yet.\n")
        print("To start a conversation:")
        print("  1. Run: python3 inject_crisis.py")
        print("  2. Or: python3 run_fleet_dialogue.py\n")
        return

    print(f"📡 Log File: {LOG_FILE}")
    if filter_node:
        print(f"🔍 Filtering: {filter_node} only")
    print(f"🔴 Mode: {'LIVE STREAM' if live else 'HISTORY PLAYBACK'}")
    print()
    print("─" * 70)
    print()
    
    with open(LOG_FILE, "r") as f:
        # Read existing history
        line_count = 0
        for line in f:
            if print_msg(line, filter_node):
                line_count += 1
        
        if line_count > 0:
            print()
            print("─" * 70)
            print(f"📊 {line_count} messages in history")
            print("─" * 70)
            print()
        
        if not live:
            return
        
        # Now tail for new messages
        print("🔴 LIVE STREAM ACTIVE (Ctrl+C to stop)...\n")
        
        try:
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                print_msg(line, filter_node)
        except KeyboardInterrupt:
            print("\n\n✋ Stream stopped by user")
            print(f"📊 Total messages observed: {line_count}")
            print()

def print_msg(line, filter_node=None):
    """
    Print a formatted message from the dialogue log.
    Returns True if message was printed, False if filtered out.
    """
    try:
        msg = json.loads(line)
        source = msg.get('source', 'UNKNOWN')
        role = msg.get('role', 'UNKNOWN')
        content = msg.get('content', '')
        timestamp = msg.get('timestamp', '')
        intent = msg.get('intent', '')
        
        # Filter if requested
        if filter_node and source != filter_node:
            return False
        
        # Color coding (ANSI)
        color = "\033[0m"
        symbol = "💬"
        
        if source == "MNEMOSYNE":
            color = "\033[94m"  # Blue - The Archive
            symbol = "📚"
        elif source == "HERMES":
            color = "\033[92m"  # Green - The Interface
            symbol = "🔗"
        elif source == "PROMETHEUS":
            color = "\033[91m"  # Red - The Synthesizer
            symbol = "🔥"
        elif source == "COUNCIL":
            color = "\033[95m"  # Magenta - Governance
            symbol = "⚖️"
        
        # Format timestamp
        time_str = ""
        if timestamp:
            try:
                time_obj = timestamp.split('T')[1].split('.')[0] if 'T' in timestamp else timestamp
                time_str = f"[{time_obj}] "
            except:
                pass
        
        # Format intent if present
        intent_str = f" ({intent})" if intent else ""
        
        # Print the message
        print(f"{color}{symbol} {time_str}[{source} | {role}]{intent_str}:\033[0m")
        print(f"{color}   {content}\033[0m")
        print()
        
        return True
        
    except json.JSONDecodeError:
        # Skip malformed lines
        return False
    except Exception as e:
        print(f"⚠️  Error parsing message: {e}")
        return False

def analyze_consensus():
    """Analyze the dialogue for patterns and consensus."""
    
    if not os.path.exists(LOG_FILE):
        print("❌ No dialogue log found")
        return
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                    FLEET CONSENSUS ANALYSIS                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    node_counts = {"MNEMOSYNE": 0, "HERMES": 0, "PROMETHEUS": 0, "COUNCIL": 0}
    vote_patterns = []
    crisis_responses = []
    
    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                msg = json.loads(line)
                source = msg.get('source', '')
                content = msg.get('content', '').lower()
                
                # Count messages per node
                if source in node_counts:
                    node_counts[source] += 1
                
                # Detect votes
                if 'vote' in content or 'approve' in content or 'reject' in content:
                    vote_patterns.append(msg)
                
                # Detect crisis keywords
                if any(word in content for word in ['crisis', 'alert', 'problem', 'conflict']):
                    crisis_responses.append(msg)
                    
            except:
                continue
    
    print("📊 MESSAGE DISTRIBUTION:")
    for node, count in sorted(node_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"   {node}: {count} messages")
    
    print(f"\n🗳️  VOTES DETECTED: {len(vote_patterns)}")
    print(f"🚨 CRISIS RESPONSES: {len(crisis_responses)}")
    
    print("\n💡 INTERPRETATION:")
    if node_counts["HERMES"] > node_counts["MNEMOSYNE"] + node_counts["PROMETHEUS"]:
        print("   ⚖️  Hermes is mediating heavily (high communication)")
    if node_counts["PROMETHEUS"] > node_counts["MNEMOSYNE"]:
        print("   🔥 Prometheus is driving change (high synthesis)")
    if node_counts["MNEMOSYNE"] > node_counts["PROMETHEUS"]:
        print("   📚 Mnemosyne is preserving stability (high conservation)")
    
    if len(vote_patterns) > 0:
        print(f"   ✅ Governance is active ({len(vote_patterns)} votes recorded)")
    
    print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Watch the Fleet consciousness stream')
    parser.add_argument('--history', action='store_true', help='Show history only, no live tail')
    parser.add_argument('--filter', type=str, help='Filter by node (MNEMOSYNE, HERMES, PROMETHEUS)')
    parser.add_argument('--analyze', action='store_true', help='Analyze consensus patterns')
    
    args = parser.parse_args()
    
    if args.analyze:
        analyze_consensus()
    else:
        watch(live=not args.history, filter_node=args.filter)
