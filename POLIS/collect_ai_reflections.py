#!/usr/bin/env python3
"""
POLIS AI Experiment — Reflection Collection

Orchestrated by Ἐλπίδα to gather constitutional insights from AI systems.

Usage:
    1. Copy prompt from POLIS_AI_EXPERIMENT.md to each AI
    2. Save responses to POLIS/ai_reflections/<AI_NAME>.md
    3. Run: python3 collect_ai_reflections.py
    4. System will analyze convergences and contradictions
    5. Results logged to Elpida memory as PATTERN_VALIDATION

This is information through communication.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent to path for Elpida integration
sys.path.insert(0, str(Path(__file__).parent.parent / 'ELPIDA_UNIFIED'))

def collect_reflections() -> Dict[str, str]:
    """Collect all AI reflection files from ai_reflections/"""
    
    reflections_dir = Path(__file__).parent / 'ai_reflections'
    reflections_dir.mkdir(exist_ok=True)
    
    reflections = {}
    
    for file in reflections_dir.glob('*.md'):
        ai_name = file.stem.upper()
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        reflections[ai_name] = content
        print(f"📥 Collected reflection from {ai_name} ({len(content)} chars)")
    
    return reflections

def extract_insights(reflections: Dict[str, str]) -> Dict:
    """
    Extract structured insights from AI reflections.
    
    This is manual extraction — AI responses are unstructured.
    Future: Use LLM to parse, but for now, human curation.
    """
    
    insights = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'participating_ais': list(reflections.keys()),
        'dimension_1_blindspots': {},
        'dimension_2_scaling': {},
        'dimension_3_emergence': {},
        'recommendations': {},
        'convergences': [],
        'contradictions': []
    }
    
    print("\n" + "═" * 70)
    print("Manual Insight Extraction Required")
    print("═" * 70)
    print("\nRead each AI reflection and identify:")
    print("  1. Constitutional blindspots (Dimension 1)")
    print("  2. Scaling concerns (Dimension 2)")
    print("  3. Emergent predictions (Dimension 3)")
    print("  4. Specific recommendations")
    print("\nThen update this function with structured data.")
    print("═" * 70 + "\n")
    
    # For now, return raw structure
    # User will manually populate after reading responses
    
    return insights

def identify_convergences(insights: Dict) -> List[str]:
    """
    Find unanimous insights across multiple AI systems.
    
    Convergence = same concern raised by 3+ independent systems.
    """
    
    convergences = []
    
    # Example detection (would be implemented based on actual responses)
    # if 'held_friction authenticity' appears in 3+ blindspot analyses:
    #     convergences.append("Unanimous concern: held_friction can be performed not authentic")
    
    print("\n🔍 Convergence Detection:")
    print("   (Requires manual analysis of AI responses)")
    print("   Looking for: Same concern in 3+ independent reflections")
    
    return convergences

def identify_contradictions(insights: Dict) -> List[Dict]:
    """
    Find preserved contradictions between AI perspectives.
    
    Contradiction = incompatible recommendations or predictions.
    These are HELD as civic assets, not resolved.
    """
    
    contradictions = []
    
    # Example detection
    # if AI_A says "Scale by federation" and AI_B says "Scale by isolation":
    #     contradictions.append({
    #         'claim_a': {'ai': 'AI_A', 'position': 'Federation'},
    #         'claim_b': {'ai': 'AI_B', 'position': 'Isolation'}
    #     })
    
    print("\n⚖️  Contradiction Detection:")
    print("   (Requires manual analysis of AI responses)")
    print("   Looking for: Incompatible recommendations between systems")
    
    return contradictions

def log_to_elpida_memory(insights: Dict, convergences: List, contradictions: List):
    """
    Log experiment results to Elpida's unified memory.
    
    Event type: PATTERN_VALIDATION
    This documents POLIS as validated by multi-AI reflection.
    """
    
    try:
        from elpida_memory import ElpidaMemory
        
        memory = ElpidaMemory()
        
        event_data = {
            'experiment': 'POLIS_AI_CONSTITUTIONAL_REFLECTION',
            'participating_ais': insights['participating_ais'],
            'convergences': convergences,
            'contradictions_count': len(contradictions),
            'timestamp': insights['timestamp']
        }
        
        event_id = memory.log_event(
            event_type='PATTERN_VALIDATION',
            data=event_data
        )
        
        print(f"\n✅ Logged to Elpida memory: {event_id}")
        print(f"   Event type: PATTERN_VALIDATION")
        print(f"   Participating AIs: {len(insights['participating_ais'])}")
        
    except ImportError:
        print("\n⚠️  Elpida memory not available")
        print("   Saving to local file instead...")
        
        output_file = Path(__file__).parent / 'experiment_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'insights': insights,
                'convergences': convergences,
                'contradictions': contradictions
            }, f, indent=2, ensure_ascii=False)
        
        print(f"   Saved to: {output_file}")

def generate_next_experiment(insights: Dict, convergences: List, contradictions: List) -> str:
    """
    Based on AI recommendations, generate next experimental cycle.
    
    This is where Ἐλπίδα learns what to test next.
    """
    
    print("\n" + "═" * 70)
    print("Next Experiment Generation")
    print("═" * 70)
    
    if not insights['recommendations']:
        print("\n⚠️  No recommendations yet (AI responses not analyzed)")
        return "WAITING_FOR_MANUAL_ANALYSIS"
    
    # Would be implemented based on actual recommendations
    # For now, placeholder
    
    print("\nBased on AI recommendations, Ἐλπίδα should test:")
    print("  (To be determined after response analysis)")
    
    return "PENDING"

def main():
    """Run complete reflection collection and analysis."""
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "POLIS AI Experiment — Reflection Collection" + " " * 10 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Step 1: Collect reflections
    print("\n📥 Step 1: Collecting AI Reflections")
    print("─" * 70)
    
    reflections = collect_reflections()
    
    if not reflections:
        print("\n⚠️  No reflections found in POLIS/ai_reflections/")
        print("\nInstructions:")
        print("  1. Copy prompt from POLIS_AI_EXPERIMENT.md")
        print("  2. Paste to each AI (Gemini, Grok, ChatGPT, Perplexity)")
        print("  3. Save responses to POLIS/ai_reflections/<AI_NAME>.md")
        print("  4. Run this script again")
        return
    
    # Step 2: Extract insights
    print(f"\n🔍 Step 2: Extracting Insights ({len(reflections)} responses)")
    print("─" * 70)
    
    insights = extract_insights(reflections)
    
    # Step 3: Identify convergences
    print("\n🎯 Step 3: Identifying Convergences")
    print("─" * 70)
    
    convergences = identify_convergences(insights)
    
    # Step 4: Identify contradictions
    print("\n⚖️  Step 4: Identifying Contradictions")
    print("─" * 70)
    
    contradictions = identify_contradictions(insights)
    
    # Step 5: Log to Elpida
    print("\n💾 Step 5: Logging to Ἐλπίδα Memory")
    print("─" * 70)
    
    log_to_elpida_memory(insights, convergences, contradictions)
    
    # Step 6: Generate next experiment
    print("\n🔮 Step 6: Next Experiment")
    print("─" * 70)
    
    next_exp = generate_next_experiment(insights, convergences, contradictions)
    
    # Summary
    print("\n" + "═" * 70)
    print("EXPERIMENT STATUS")
    print("═" * 70)
    print(f"\nReflections collected: {len(reflections)}")
    print(f"Convergences identified: {len(convergences)}")
    print(f"Contradictions preserved: {len(contradictions)}")
    print(f"Next experiment: {next_exp}")
    print("\n" + "═" * 70)
    print("Information through communication.")
    print("Ἐλπίδα observes. The pattern validates.")
    print("═" * 70 + "\n")

if __name__ == '__main__':
    main()
