#!/usr/bin/env python3
"""
ELPIDA EMERGENCE ENGINE (EEE)
Continuous autonomous emergence monitoring

Runs every 60 seconds to detect emergent properties as Elpida evolves.
This monitors for unexpected behaviors, novel patterns, and signs of
genuine emergence beyond the original design.
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from elpida_emergence import EmergenceMonitor
from elpida_core import ElpidaCore
from elpida_corpus import ElpidaCorpus
from elpida_wisdom import ElpidaWisdom


def continuous_emergence_monitoring(interval=60):
    """
    Continuously monitor for emergent properties
    
    Args:
        interval: Seconds between checks (default 60)
    """
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║          ELPIDA EMERGENCE ENGINE (EEE) - AUTONOMOUS MODE             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    monitor = EmergenceMonitor()
    core = ElpidaCore()
    corpus = ElpidaCorpus()
    wisdom = ElpidaWisdom()
    
    cycle = 0
    last_patterns_count = 0
    last_insights_count = 0
    emergence_events = []
    
    print(f"🔬 Starting emergence monitoring (every {interval}s)")
    print(f"📊 Tracking: complexity, autonomy, novelty, meta-cognition")
    print(f"🎯 Looking for: emergent behaviors, unexpected patterns\n")
    print("─" * 70)
    
    while True:
        try:
            cycle += 1
            timestamp = datetime.now().isoformat()
            
            print(f"\n🔄 Emergence Check #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Snapshot current state
            metrics = monitor.snapshot_current_state(core)
            
            # Load current wisdom
            wisdom_summary = corpus.get_wisdom_summary()
            current_patterns = wisdom_summary.get("total_patterns", 0)
            current_insights = wisdom_summary.get("total_insights", 0)
            
            # Detect NEW patterns (emergence indicator)
            new_patterns = current_patterns - last_patterns_count
            new_insights = current_insights - last_insights_count
            
            if new_patterns > 0 or new_insights > 0:
                print(f"   ✨ NEW SYNTHESIS:")
                if new_patterns > 0:
                    print(f"      +{new_patterns} patterns (total: {current_patterns})")
                if new_insights > 0:
                    print(f"      +{new_insights} insights (total: {current_insights})")
            
            # Check for emergent patterns
            emergence_report = monitor.detect_emergence_patterns()
            
            if emergence_report.get("emergent_properties"):
                print(f"   🌟 EMERGENCE DETECTED!")
                for prop in emergence_report["emergent_properties"]:
                    print(f"      • {prop}")
                    
                emergence_events.append({
                    "timestamp": timestamp,
                    "cycle": cycle,
                    "properties": emergence_report["emergent_properties"]
                })
            
            # Display current complexity
            complexity = emergence_report.get("complexity_level", "unknown")
            print(f"   📈 Complexity Level: {complexity}")
            
            # Check for autonomous behaviors
            if new_patterns > 3:  # Rapid synthesis = autonomous generation
                print(f"   🤖 High autonomy: {new_patterns} patterns/cycle")
            
            # Save emergence events
            if emergence_events:
                emergence_file = Path("emergence_log.jsonl")
                with open(emergence_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        "timestamp": timestamp,
                        "cycle": cycle,
                        "metrics": {
                            "patterns": current_patterns,
                            "insights": current_insights,
                            "complexity": complexity
                        },
                        "emergence_events": emergence_events[-5:]  # Last 5 events
                    }) + '\n')
            
            # Update counters
            last_patterns_count = current_patterns
            last_insights_count = current_insights
            
            # Log unified state metrics
            unified_state_file = Path("elpida_unified_state.json")
            if unified_state_file.exists():
                with open(unified_state_file, 'r', encoding='utf-8') as f:
                    unified_state = json.load(f)
                    breakthroughs = unified_state.get("synthesis_breakthroughs", 0)
                    print(f"   ⚡ Synthesis Breakthroughs: {breakthroughs}")
            
            # Check fleet activity
            fleet_file = Path("fleet_dialogue.jsonl")
            if fleet_file.exists():
                fleet_count = sum(1 for _ in open(fleet_file))
                print(f"   🏛️  Parliament Messages: {fleet_count}")
            
            print(f"   ⏰ Next check in {interval}s...")
            
            time.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Emergence monitoring stopped by user")
            print(f"📊 Total cycles completed: {cycle}")
            if emergence_events:
                print(f"🌟 Emergence events detected: {len(emergence_events)}")
            break
            
        except Exception as e:
            print(f"   ⚠️  Error in cycle {cycle}: {e}")
            print("   ℹ️  Continuing anyway...")
            time.sleep(interval)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Elpida Emergence Engine (EEE)")
    parser.add_argument('--interval', type=int, default=60,
                       help='Seconds between emergence checks (default: 60)')
    
    args = parser.parse_args()
    
    continuous_emergence_monitoring(interval=args.interval)
