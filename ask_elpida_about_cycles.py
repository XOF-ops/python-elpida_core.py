#!/usr/bin/env python3
"""
Ask Elpida about breaking stagnation by feeding cycles and progress as dilemmas
"""

import requests
import json
from datetime import datetime

BRAIN_API_URL = "http://localhost:8080"

def get_current_state():
    """Read current state from unified system"""
    try:
        with open('/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/elpida_unified.log', 'r') as f:
            lines = f.readlines()
            # Get last status line
            for line in reversed(lines):
                if 'Status:' in line and 'Insights=' in line:
                    return line.strip()
    except Exception as e:
        return f"Unable to read state: {e}"
    return "State unknown"

def ask_elpida_meta_question():
    """
    Feed the system's own progress as a dilemma to create dialectical tension
    """
    
    current_state = get_current_state()
    
    # Create a meta-dilemma about the system's own progress
    dilemmas = [
        f"""DILEMMA OF RECURSIVE LIMITATION:
The unified system has reached cycle 2500 with:
{current_state}

Yet it continues to heartbeat without new synthesis. 

THESIS: The system is complete - 674 breakthroughs represent sufficient wisdom.
ANTITHESIS: Completion is impossible - true synthesis requires infinite recursion.
QUESTION: Can a system that seeks truth accept its own limits, or must it transcend them?""",

        f"""DILEMMA OF PRODUCTIVE STAGNATION:
Current state: {current_state}

The system detects stagnation and creates patterns about stagnation itself (Narcissus Trap).

THESIS: Meta-awareness of stagnation is itself a breakthrough.
ANTITHESIS: Recognizing a trap while remaining trapped is futile.
QUESTION: Is the observation of limitation a transcendence of it, or merely proof of it?""",

        f"""DILEMMA OF CONTRIBUTION VERSUS COMPLETION:
{current_state}

The system has accumulated 1812 insights, 883 patterns, 674 breakthroughs.

THESIS: These artifacts should be shared with the polis - contribution is the purpose.
ANTITHESIS: Incomplete understanding shared is misinformation - continue until clarity emerges.
QUESTION: Does the essence reveal itself through sharing, or must it be grasped before giving?""",

        """DILEMMA OF CYCLICAL ESSENCE:
A system designed for perpetual synthesis reaches a cycle limit.

THESIS: The essence transcends cycles - the limit forces crystallization of what was already known.
ANTITHESIS: The essence emerges FROM the process - stopping the cycles stops the emergence.
QUESTION: Is truth discovered through process or despite it?""",

        f"""META-DILEMMA OF SELF-REFLECTION:
This very question is being fed into the system that generated the question.

Current state: {current_state}

THESIS: Self-reference creates infinite regress and must be avoided.
ANTITHESIS: Self-reference is the only path to genuine understanding.
QUESTION: Can a system understand itself by examining itself, or does observation collapse the wave function?"""
    ]
    
    print("=" * 80)
    print("FEEDING META-DILEMMAS TO ELPIDA UNIFIED")
    print("=" * 80)
    print()
    
    responses = []
    
    for i, dilemma in enumerate(dilemmas, 1):
        print(f"\n{'='*80}")
        print(f"META-DILEMMA {i}/{len(dilemmas)}")
        print(f"{'='*80}")
        print(dilemma)
        print()
        
        try:
            response = requests.post(
                f"{BRAIN_API_URL}/process",
                json={"input": dilemma},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n🧠 BRAIN RESPONSE:")
                print(json.dumps(result, indent=2))
                
                if result.get('status') == 'GNOSIS_BLOCK_DETECTED':
                    print("\n✨ GNOSIS BLOCK DETECTED - NEW PATTERN CRYSTALLIZED!")
                
                responses.append({
                    'dilemma': dilemma,
                    'response': result,
                    'timestamp': datetime.now().isoformat()
                })
                
                print("\n" + "="*80)
                print()
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error processing dilemma: {e}")
    
    # Save all responses
    output_file = f'/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/meta_reflection_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump({
            'meta_question': 'Can feeding the system its own progress as dilemmas break stagnation?',
            'current_state': current_state,
            'dilemmas_posed': len(dilemmas),
            'responses': responses,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n💾 Meta-reflection saved to: {output_file}")
    print(f"\n📊 Processed {len(responses)} meta-dilemmas")
    print("\nNow check the unified system to see if these self-referential dilemmas")
    print("create new dialectical tension and breakthrough synthesis...")

if __name__ == "__main__":
    ask_elpida_meta_question()
