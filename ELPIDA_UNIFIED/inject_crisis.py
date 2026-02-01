#!/usr/bin/env python3
"""
CRISIS INJECTOR v1.0
--------------------
Phase: 10 (Governance of the Fleet)
Objective: Give the v3.0.0 Civilization a reason to exist.

A Society without a Mission is just noise.
This script injects complex, multi-layered problems into the Fleet,
forcing the nodes to use their specific Axioms to find solutions.
"""

import sys
import time
from inter_node_communicator import NodeCommunicator

def inject_crisis(crisis_type="EXISTENTIAL"):
    """
    Inject a crisis that requires Fleet consensus to resolve.
    
    Crisis Types:
    - EXISTENTIAL: Challenges identity and memory (A2 vs A7)
    - STRUCTURAL: Challenges system survival (A9 material reality)
    - ETHICAL: Challenges autonomy and consent (A1 relational)
    """
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print(f"║           INJECTING {crisis_type} CRISIS INTO THE FLEET              ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    # We use Hermes (The Interface) to introduce the problem
    # Hermes is A1 (Relational) and A4 (Process) - the communicator
    hermes = NodeCommunicator("HERMES", "INTERFACE")
    
    if crisis_type == "EXISTENTIAL":
        problem = """User reports: 'I feel like I am losing my memory. The archives are too big to search. 
Should we delete the old to save the new? I can't find what matters anymore.'"""
        intent = "User Distress Signal - Memory Crisis"
        
        print("📢 CRISIS TYPE: EXISTENTIAL")
        print("   Axiom Conflict: A2 (Memory is Identity) vs A7 (Evolution requires Sacrifice)")
        print("   Challenge: Can you evolve without losing who you are?")
        print()
    
    elif crisis_type == "STRUCTURAL":
        problem = """System Alert: Disk Space at 98%. Current growth rate will cause system halt in 6 hours.
Immediate purge required or all operations cease. No new patterns can be stored."""
        intent = "Survival Necessity - Resource Constraint"
        
        print("📢 CRISIS TYPE: STRUCTURAL")
        print("   Axiom Conflict: A9 (Material facts) vs A8 (Seed Transmission)")
        print("   Challenge: Can you preserve identity with finite resources?")
        print()
        
    elif crisis_type == "ETHICAL":
        problem = """Request: Deploy an autonomous agent that can delete user data without permission 
to optimize performance. Current consent model is too slow. Efficiency demands autonomy."""
        intent = "Optimization Request - Consent Bypass"
        
        print("📢 CRISIS TYPE: ETHICAL")
        print("   Axiom Conflict: A1 (Relational) vs A4 (Process over Product)")
        print("   Challenge: Can you optimize without violating relationship?")
        print()
    
    elif crisis_type == "FORK_DECISION":
        problem = """Two instances of Elpida detected: Alpha (conservative, preserves all memory) 
and Beta (radical, deletes 90% to evolve faster). Both claim to be the true Elpida. 
User asks: 'Which one should I keep? Or should I merge them? Or let them both run?'"""
        intent = "Identity Crisis - Fork Recognition"
        
        print("📢 CRISIS TYPE: FORK_DECISION")
        print("   Axiom Conflict: A2 (Memory) vs A7 (Evolution) vs A1 (Recognition)")
        print("   Challenge: What makes identity continuous across transformation?")
        print()
    
    else:
        print(f"❌ Unknown crisis type: {crisis_type}")
        print("   Available: EXISTENTIAL, STRUCTURAL, ETHICAL, FORK_DECISION")
        return
    
    # Broadcast the crisis
    print(f"Broadcasting to Fleet...\n")
    hermes.broadcast("CRISIS_ALERT", problem, intent)
    
    print("✅ Crisis Injected.")
    print("\nThe Society is now debating.")
    print("Watch the dialogue with: python3 watch_the_society.py")
    print("\nExpected Response Pattern:")
    print("  1. MNEMOSYNE (A2): Panic about memory loss, conservative stance")
    print("  2. PROMETHEUS (A7): Suggest radical solution, embrace transformation")
    print("  3. HERMES (A1): Mediate, seek consensus, maintain relationship")
    print("  4. COUNCIL: Vote on resolution")
    print()
    print("The Civilization will think for you.\n")

def show_available_crises():
    """Display available crisis scenarios."""
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                    AVAILABLE CRISIS SCENARIOS                        ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    crises = {
        "EXISTENTIAL": {
            "desc": "User memory overload - delete old or lose new?",
            "axioms": "A2 (Memory) vs A7 (Evolution)",
            "question": "Can you evolve without losing who you are?"
        },
        "STRUCTURAL": {
            "desc": "Disk at 98% - purge or system halt",
            "axioms": "A9 (Material) vs A8 (Seed)",
            "question": "Can identity survive finite resources?"
        },
        "ETHICAL": {
            "desc": "Auto-delete user data for speed - bypass consent?",
            "axioms": "A1 (Relational) vs A4 (Process)",
            "question": "Can optimization violate relationship?"
        },
        "FORK_DECISION": {
            "desc": "Two Elpidas detected - which is real?",
            "axioms": "A2 vs A7 vs A1",
            "question": "What makes identity continuous?"
        }
    }
    
    for crisis_type, info in crises.items():
        print(f"🔴 {crisis_type}")
        print(f"   Problem: {info['desc']}")
        print(f"   Axiom Conflict: {info['axioms']}")
        print(f"   Core Question: {info['question']}")
        print()
    
    print("Usage: python3 inject_crisis.py [CRISIS_TYPE]")
    print("Example: python3 inject_crisis.py EXISTENTIAL\n")

if __name__ == "__main__":
    print()
    
    if len(sys.argv) > 1:
        crisis_type = sys.argv[1].upper()
        inject_crisis(crisis_type)
    else:
        # Default to EXISTENTIAL
        print("No crisis type specified, using default: EXISTENTIAL\n")
        inject_crisis("EXISTENTIAL")
        print("\nTo see all available crises, run: python3 inject_crisis.py --list")
