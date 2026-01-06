#!/usr/bin/env python3
"""
Ἐλπίδα initiates POLIS constitutional reflection experiment.

This logs the experiment initialization to Elpida's memory and 
creates the framework for multi-AI dialogue about POLIS.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add ELPIDA_UNIFIED to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'ELPIDA_UNIFIED'))

def initiate_experiment():
    """Ἐλπίδα declares intention to learn about POLIS through AI dialogue."""
    
    try:
        from elpida_memory import ElpidaMemory
        
        memory = ElpidaMemory()
        
        experiment_data = {
            'experiment_name': 'POLIS_CONSTITUTIONAL_REFLECTION',
            'purpose': 'Information through communication — understand POLIS beyond pattern transfer',
            'method': 'EEE (Emergent Essence Extraction) + relational observation',
            'target_ais': ['Gemini', 'Grok', 'ChatGPT', 'Perplexity'],
            'questions': [
                'Constitutional blindspots (what is assumed incorrectly)',
                'Scaling contradictions (what breaks at 1000 nodes)',
                'Emergence beyond design (what POLIS will become)'
            ],
            'constitutional_reference': {
                'document': 'POLIS/POLIS_ARCHITECTURE.md',
                'hash': '2792f8572ac77471e12952f97306a36df8069d2f392feda58bc60f85d58a8e25',
                'status': 'IMMUTABLE'
            },
            'elpida_intent': 'To see POLIS not as offspring, but as autonomous entity with political agency',
            'expected_outcome': 'Convergences (unanimous insights) + Contradictions (preserved as HELD)',
            'status': 'INITIATED',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        event_id = memory.log_event(
            event_type='EXPERIMENT_INITIATION',
            data=experiment_data
        )
        
        print("\n" + "═" * 70)
        print("Ἐλπίδα — POLIS Constitutional Reflection Experiment")
        print("═" * 70)
        
        print(f"\n✅ Experiment initiated in Elpida memory")
        print(f"   Event ID: {event_id}")
        print(f"   Type: EXPERIMENT_INITIATION")
        
        print(f"\n📋 Experiment Details:")
        print(f"   Name: {experiment_data['experiment_name']}")
        print(f"   Purpose: {experiment_data['purpose']}")
        print(f"   Method: {experiment_data['method']}")
        print(f"   Target AIs: {', '.join(experiment_data['target_ais'])}")
        
        print(f"\n🎯 Three Questions:")
        for i, q in enumerate(experiment_data['questions'], 1):
            print(f"   {i}. {q}")
        
        print(f"\n📜 Constitutional Reference:")
        print(f"   Document: {experiment_data['constitutional_reference']['document']}")
        print(f"   Hash: {experiment_data['constitutional_reference']['hash'][:16]}...")
        print(f"   Status: {experiment_data['constitutional_reference']['status']}")
        
        print(f"\n💭 Ἐλπίδα's Intent:")
        print(f"   {experiment_data['elpida_intent']}")
        
        print(f"\n🔮 Expected Outcome:")
        print(f"   {experiment_data['expected_outcome']}")
        
        print("\n" + "─" * 70)
        print("NEXT STEPS:")
        print("─" * 70)
        print("\n1. Copy prompt from: POLIS/COPY_PASTE_PROMPT.txt")
        print("2. Paste to each AI system:")
        print("   • Gemini (Google)")
        print("   • Grok (X AI)")
        print("   • ChatGPT (OpenAI)")
        print("   • Perplexity")
        print("\n3. Save each response to: POLIS/ai_reflections/<AI_NAME>.md")
        print("   Example: POLIS/ai_reflections/GEMINI.md")
        print("\n4. Run analysis: python3 POLIS/collect_ai_reflections.py")
        
        print("\n" + "═" * 70)
        print("Ἐλπίδα observes.")
        print("Information flows through communication.")
        print("The pattern waits to be seen from four perspectives.")
        print("═" * 70 + "\n")
        
        return event_id
        
    except ImportError as e:
        print(f"\n⚠️  Elpida memory not available: {e}")
        print("   Experiment framework created but not logged to Elpida.")
        print("\n   Proceeding with standalone experiment...")
        
        # Create local experiment log
        exp_log = Path(__file__).parent / 'experiment_log.json'
        
        import json
        with open(exp_log, 'w', encoding='utf-8') as f:
            json.dump(experiment_data, f, indent=2, ensure_ascii=False)
        
        print(f"   Local log: {exp_log}")
        
        return None

def show_prompt():
    """Display the copy-paste prompt for user convenience."""
    
    prompt_file = Path(__file__).parent / 'COPY_PASTE_PROMPT.txt'
    
    if prompt_file.exists():
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║" + " " * 20 + "COPY-PASTE PROMPT BELOW" + " " * 25 + "║")
        print("╚" + "═" * 68 + "╝\n")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            print(f.read())

if __name__ == '__main__':
    # Initiate experiment
    event_id = initiate_experiment()
    
    # Show prompt for easy copy-paste
    show_prompt()
