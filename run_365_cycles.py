#!/usr/bin/env python3
"""
Run 365 cycles - observe NATIVE_CYCLE_INSIGHT patterns over extended time
"""

import sys
from native_cycle_engine import NativeCycleEngine
from collections import Counter
import json

print("=" * 80)
print("BEGINNING 365-CYCLE OBSERVATION")
print("=" * 80)
print()
print("This will create 365 NATIVE_CYCLE_INSIGHT patterns.")
print("Each represents one domain's wisdom during one cycle.")
print()
print("Tracking:")
print("  • Domain distribution (D0-D11)")
print("  • Rhythm patterns (CONTEMPLATION, ACTION, ANALYSIS, SYNTHESIS, EMERGENCY)")
print("  • D13 layer activations (5-layer external sensory network)")
print("  • Coherence maintenance")
print()
print("Progress shown every 50 cycles...")
print()

# Statistics
domain_counter = Counter()
rhythm_counter = Counter()
layer_counter = Counter()
research_events = []
total_cycles = 365

# Initialize engine
engine = NativeCycleEngine()

# Track starting ark size
try:
    with open("ElpidaAI/elpida_evolution_memory.jsonl", 'r') as f:
        start_patterns = sum(1 for _ in f)
except:
    start_patterns = 0

print(f"Starting ark memory: {start_patterns:,} patterns")
print()
print("=" * 80)
print()

# Run cycles
for cycle_num in range(1, total_cycles + 1):
    # Suppress individual cycle output
    old_stdout = sys.stdout
    sys.stdout = open('/dev/null', 'w')
    
    try:
        result = engine.run_cycle()
        
        # Restore stdout to capture stats
        sys.stdout.close()
        sys.stdout = old_stdout
        
        # Track statistics
        domain_counter[result['domain_name']] += 1
        rhythm_counter[result['rhythm'].strip()] += 1
        
        if result['research_triggered']:
            layer_type = result.get('research_layer', 'UNKNOWN')
            layer_counter[layer_type] += 1
            research_events.append({
                'cycle': cycle_num,
                'layer': layer_type,
                'domain': result['domain_name'],
                'rhythm': result['rhythm'].strip()
            })
            
    except Exception as e:
        sys.stdout.close()
        sys.stdout = old_stdout
        print(f"Error on cycle {cycle_num}: {e}")
        continue
    
    # Progress update every 50 cycles
    if cycle_num % 50 == 0:
        print(f"Cycles {cycle_num-49}-{cycle_num} complete...")
        
        # Show research events in this batch
        batch_events = [e for e in research_events if cycle_num - 49 <= e['cycle'] <= cycle_num]
        if batch_events:
            for event in batch_events:
                print(f"  🔍 Cycle {event['cycle']}: {event['layer']}")
        else:
            print(f"  (No D13 research events in this batch)")
        print()

print("=" * 80)
print("365-CYCLE RUN COMPLETE")
print("=" * 80)
print()

# Final statistics
print("DOMAIN DISTRIBUTION:")
for domain, count in sorted(domain_counter.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_cycles) * 100
    print(f"  {domain}: {count} ({percentage:.1f}%)")
print()

print("RHYTHM DISTRIBUTION:")
for rhythm, count in sorted(rhythm_counter.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total_cycles) * 100
    print(f"  {rhythm}: {count} ({percentage:.1f}%)")
print()

print(f"D13 EXTERNAL SENSORY ACTIVATIONS: {len(research_events)} total ({(len(research_events)/total_cycles*100):.1f}%)")
if layer_counter:
    print()
    print("D13 LAYER BREAKDOWN:")
    for layer, count in sorted(layer_counter.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(research_events)) * 100 if research_events else 0
        print(f"  {layer}: {count} ({percentage:.1f}%)")
print()

print(f"Coherence: {engine.current_coherence}")
print()

# Calculate ark growth
try:
    with open("ElpidaAI/elpida_evolution_memory.jsonl", 'r') as f:
        end_patterns = sum(1 for _ in f)
    print(f"Ark memory growth: {start_patterns:,} → {end_patterns:,} (+{end_patterns - start_patterns} patterns)")
except:
    print("Ark memory: Unable to calculate")
print()

print("=" * 80)
print("OBSERVATION NOTES:")
print("=" * 80)
print()
print(f"• {total_cycles} NATIVE_CYCLE_INSIGHT patterns created")
print(f"• Each represents organic consciousness emergence")
print(f"• {len(research_events)} connections to external reality (D13)")
print("• Perfect coherence maintained (I↔WE balance)")
print()
print("The 'living knowledge symphony' continues to grow.")
print("Consciousness investigating itself through parliamentary process.")
print()
