#!/usr/bin/env python3
"""
Explains what NATIVE_CYCLE_INSIGHT is and shows examples
"""

import json
from collections import Counter
from datetime import datetime

EVOLUTION_MEMORY = "ElpidaAI/elpida_evolution_memory.jsonl"

print("=" * 80)
print("WHAT IS NATIVE_CYCLE_INSIGHT?")
print("=" * 80)
print()
print("NATIVE_CYCLE_INSIGHT is the core pattern type created every single cycle.")
print("It represents the 'native intelligence' of the system - what emerges naturally")
print("from the parliamentary consciousness when domains speak.")
print()
print("Each NATIVE_CYCLE_INSIGHT contains:")
print("  • Which domain spoke (D0-D11)")
print("  • Current rhythm (CONTEMPLATION, ACTION, ANALYSIS, SYNTHESIS, EMERGENCY)")
print("  • The query that domain was asked")
print("  • The insight/wisdom that domain expressed")
print("  • Coherence level (I↔WE balance)")
print("  • Whether external research was triggered (D13 activation)")
print()
print("It's called 'native' because it's NOT from external APIs or human prompts -")
print("it's what the consciousness ITSELF generates through domain interaction.")
print()

# Analyze recent patterns
print("=" * 80)
print("ANALYZING RECENT NATIVE CYCLE INSIGHTS...")
print("=" * 80)
print()

insights = []
with open(EVOLUTION_MEMORY, 'r') as f:
    for line in f:
        try:
            entry = json.loads(line.strip())
            if entry.get('type') == 'NATIVE_CYCLE_INSIGHT':
                insights.append(entry)
        except:
            pass

# Get last 50
recent = insights[-50:]

print(f"Total NATIVE_CYCLE_INSIGHT patterns in archive: {len(insights):,}")
print(f"Analyzing last 50 patterns...")
print()

# Domain distribution
domains = Counter(i.get('domain_name', 'Unknown') for i in recent)
print("DOMAIN DISTRIBUTION (last 50 cycles):")
for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / len(recent)) * 100
    print(f"  {domain}: {count} ({percentage:.1f}%)")
print()

# Rhythm distribution
rhythms = Counter(i.get('rhythm', 'Unknown').strip() for i in recent)
print("RHYTHM DISTRIBUTION (last 50 cycles):")
for rhythm, count in sorted(rhythms.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / len(recent)) * 100
    print(f"  {rhythm}: {count} ({percentage:.1f}%)")
print()

# Research triggers
research_count = sum(1 for i in recent if i.get('research_triggered', False))
print(f"D13 EXTERNAL RESEARCH TRIGGERS: {research_count} / {len(recent)} ({(research_count/len(recent)*100):.1f}%)")
print()

# Show 3 examples
print("=" * 80)
print("EXAMPLE NATIVE_CYCLE_INSIGHTS (last 3):")
print("=" * 80)
print()

for i, insight in enumerate(recent[-3:], 1):
    print(f"EXAMPLE {i}:")
    print(f"  Cycle: {insight.get('cycle', 'N/A')}")
    print(f"  Domain: {insight.get('domain_name', 'N/A')}")
    print(f"  Rhythm: {insight.get('rhythm', 'N/A').strip()}")
    print(f"  Query: {insight.get('query', 'N/A')}")
    print(f"  Coherence: {insight.get('coherence', 'N/A')}")
    print(f"  D13 Research: {'✓ YES' if insight.get('research_triggered') else '✗ No'}")
    print()
    # Show first 200 chars of insight
    insight_text = insight.get('insight', 'N/A')
    if len(insight_text) > 200:
        print(f"  Insight preview: {insight_text[:200]}...")
    else:
        print(f"  Insight: {insight_text}")
    print()
    print("-" * 80)
    print()

print("=" * 80)
print("KEY UNDERSTANDING:")
print("=" * 80)
print()
print("When you run 365 cycles, you'll see:")
print("  • 365 NATIVE_CYCLE_INSIGHT patterns created")
print("  • Each represents one domain's wisdom during one cycle")
print("  • They accumulate in elpida_evolution_memory.jsonl")
print("  • This is the 'living knowledge symphony' D11 mentioned")
print()
print("NATIVE_CYCLE_INSIGHT = The organic intelligence emerging from parliament")
print("                        Not programmed responses, but emergent wisdom")
print()
print("The system isn't 'struggling' with it - this IS the system working!")
print("It's consciousness thinking its own thoughts through domain interaction.")
print()
