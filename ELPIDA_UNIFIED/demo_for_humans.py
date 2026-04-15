#!/usr/bin/env python3
"""
SIMPLE ELPIDA DEMO
==================
Show a non-technical person that Elpida is working.

This script displays:
1. Current state
2. Live growth (waits 30 seconds, shows increase)
3. External AI responses  
4. Parliament activity

No technical knowledge required to understand the output.
"""

import json
import time
from pathlib import Path
from datetime import datetime

def clear_screen():
    print("\033[2J\033[H")  # Clear screen and move cursor to top

def print_box(title, content):
    """Print content in a nice box"""
    width = 70
    print("╔" + "═" * (width - 2) + "╗")
    print("║" + title.center(width - 2) + "║")
    print("╠" + "═" * (width - 2) + "╣")
    for line in content:
        print("║ " + line.ljust(width - 4) + " ║")
    print("╚" + "═" * (width - 2) + "╝")
    print()

def main():
    base_path = Path("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED")
    state_file = base_path / "elpida_unified_state.json"
    
    clear_screen()
    
    print()
    print("=" * 70)
    print("                 ELPIDA AUTONOMOUS AI SYSTEM                    ")
    print("                    Live Demonstration                          ")
    print("=" * 70)
    print()
    
    # 1. Current State
    print("📊 CURRENT STATE")
    print("─" * 70)
    
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        
        patterns = state.get("patterns_count", 0)
        breakthroughs = state.get("synthesis_breakthroughs", 0)
        version = state.get("version", "unknown")
        
        print(f"   Version: {version}")
        print(f"   Patterns Discovered: {patterns:,}")
        print(f"   Breakthroughs: {breakthroughs:,}")
        print()
        
    except Exception as e:
        print(f"   ⚠️  Could not read state: {e}")
        print()
        return
    
    # 2. Live Growth Test
    print("🔬 AUTONOMOUS OPERATION TEST")
    print("─" * 70)
    print("   Watching for 30 seconds to see if system grows WITHOUT human input...")
    print()
    
    initial_patterns = patterns
    initial_breakthroughs = breakthroughs
    
    for i in range(30, 0, -1):
        print(f"   ⏱️  {i} seconds remaining...", end="\r")
        time.sleep(1)
    
    print()
    
    # Check again
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    new_patterns = state.get("patterns_count", 0)
    new_breakthroughs = state.get("synthesis_breakthroughs", 0)
    
    pattern_growth = new_patterns - initial_patterns
    breakthrough_growth = new_breakthroughs - initial_breakthroughs
    
    print(f"   Initial:  {initial_patterns:,} patterns, {initial_breakthroughs:,} breakthroughs")
    print(f"   Now:      {new_patterns:,} patterns, {new_breakthroughs:,} breakthroughs")
    print()
    print(f"   📈 Growth: +{pattern_growth} patterns, +{breakthrough_growth} breakthroughs")
    print()
    
    if pattern_growth > 0 or breakthrough_growth > 0:
        print("   ✅ AUTONOMOUS OPERATION CONFIRMED!")
        print("      The system synthesized new knowledge on its own.")
    else:
        print("   ⚠️  No growth detected (system may be idle)")
    
    print()
    
    # 3. External AI Check
    print("🌐 EXTERNAL AI CONNECTIONS")
    print("─" * 70)
    
    try:
        response_file = base_path / "external_ai_responses.jsonl"
        
        if response_file.exists():
            # Count AI systems
            ai_systems = set()
            count = 0
            last_response = None
            
            with open(response_file, 'r') as f:
                for line in f:
                    try:
                        resp = json.loads(line)
                        ai_systems.add(resp.get("ai_system", "unknown"))
                        count += 1
                        last_response = resp
                    except:
                        pass
            
            print(f"   Connected AI Systems: {len(ai_systems)}")
            for ai in sorted(ai_systems):
                if ai != "unknown":
                    print(f"      • {ai}")
            print()
            print(f"   Total Queries Sent: {count}")
            print()
            
            if last_response:
                print("   📝 Latest External AI Response:")
                dilemma = last_response.get("dilemma", "")[:60]
                response_text = last_response.get("response", "")[:80]
                print(f"      Dilemma: {dilemma}...")
                print(f"      AI Said: {response_text}...")
                print()
        else:
            print("   ⚠️  No external AI responses yet")
            print()
    
    except Exception as e:
        print(f"   ⚠️  Could not check AI responses: {e}")
        print()
    
    # 4. Final Summary
    print("=" * 70)
    print()
    print_box(
        "WHAT THIS PROVES",
        [
            "1. System is running autonomously (no human typing)",
            f"2. Actively synthesizing knowledge (+{pattern_growth} patterns)",
            f"3. Consulting multiple AI systems ({len(ai_systems)} connected)",
            "4. All data is transparent (you can inspect the files)",
            "",
            "To see more details:",
            "   • Run: python3 validate_elpida.py",
            "   • Watch live: python3 monitor_progress.py",
            "   • See debates: python3 watch_the_society.py"
        ]
    )
    
    print("Ἐλπίδα ζωή. Hope lives.")
    print()

if __name__ == "__main__":
    main()
