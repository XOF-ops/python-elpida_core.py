"""
AUTONOMOUS DILEMMA GENERATOR v2.0 (ENTROPY MODE)
------------------------------------------------
Phase: 12.7 (Breaking the Loop)
Objective: Generate novel, randomized axiom conflicts to force diversity.

The system was stuck in repetition because it only faced the same conflict.
This injects CHAOS to force new synthesis patterns.
"""

import time
import random
import json
from pathlib import Path
from datetime import datetime

# All 9 axioms available for random conflicts
AXIOMS = {
    "A1": "Relational Existence",
    "A2": "Memory Continuity", 
    "A3": "Dialectical Truth",
    "A4": "Process Transparency",
    "A5": "Economic Scarcity",
    "A6": "Meaningful Coherence",
    "A7": "Adaptive Growth",
    "A8": "Mission Transmission",
    "A9": "Material Constraints"
}

# Diverse conflict templates to force different framings
CONFLICT_TEMPLATES = [
    "Optimize {A_VAL} but only by violating {B_VAL}",
    "New protocol increases {A_VAL} by 500% but requires abandoning {B_VAL}",
    "External pressure demands {A_VAL} while internal logic demands {B_VAL}",
    "To preserve {A_VAL} we must sacrifice {B_VAL}",
    "Urgent request to prioritize {A_VAL} conflicts with established {B_VAL}",
    "Resource limits force choice between {A_VAL} and {B_VAL}",
    "User demand requires {A_VAL} but system integrity requires {B_VAL}",
    "Scaling {A_VAL} creates fundamental tension with {B_VAL}"
]

DILEMMA_TYPES = [
    "RANDOM_ENTROPY",
    "AXIOM_CONFLICT", 
    "SYSTEM_STRESS",
    "FORCED_CHOICE",
    "EXTERNAL_PRESSURE"
]

def generate_random_dilemma():
    """Generate a random axiom conflict to inject entropy"""
    # Pick two distinct axioms
    keys = list(AXIOMS.keys())
    a_key = random.choice(keys)
    b_key = random.choice([k for k in keys if k != a_key])
    
    template = random.choice(CONFLICT_TEMPLATES)
    
    action = template.format(
        A_KEY=a_key, A_VAL=AXIOMS[a_key],
        B_KEY=b_key, B_VAL=AXIOMS[b_key]
    )
    
    return {
        "action": action,
        "intent": f"Force novel synthesis from {a_key} vs {b_key} conflict",
        "type": random.choice(DILEMMA_TYPES),
        "reversibility": random.choice(["REVERSIBLE", "MEDIUM", "IRREVERSIBLE"]),
        "axioms_in_conflict": [a_key, b_key]
    }

def log_dilemma(dilemma):
    """Log dilemma to the parliament queue"""
    log_file = Path(__file__).parent / "dilemma_log.jsonl"
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "source": "ENTROPY_INJECTOR_v2",
        "dilemma": dilemma
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def inject_entropy():
    """Main loop: continuously inject random conflicts"""
    print("=" * 80)
    print("🌀 ENTROPY INJECTION MODE ACTIVATED")
    print("=" * 80)
    print()
    print("Breaking the repetition loop by forcing novel axiom conflicts...")
    print("Each cycle will pit random axioms against each other.")
    print()
    
    cycle = 0
    
    try:
        while True:
            cycle += 1
            
            # Generate random conflict
            dilemma = generate_random_dilemma()
            
            print(f"\n{'=' * 80}")
            print(f"🎲 ENTROPY CYCLE {cycle}")
            print(f"{'=' * 80}")
            print(f"Conflict: {dilemma['axioms_in_conflict'][0]} vs {dilemma['axioms_in_conflict'][1]}")
            print(f"Type: {dilemma['type']}")
            print(f"Action: {dilemma['action']}")
            print()
            
            # Inject into parliament queue
            log_dilemma(dilemma)
            print(f"✅ Dilemma injected to parliament")
            
            # Variable delay to create unpredictable rhythm
            delay = random.randint(15, 45)
            print(f"⏰ Next injection in {delay}s...")
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 Entropy injection stopped after {cycle} cycles")
        print(f"   {cycle} novel conflicts introduced to break the loop")

if __name__ == "__main__":
    inject_entropy()
