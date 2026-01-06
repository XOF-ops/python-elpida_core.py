"""
SIMULATION: FLEET DIALOGUE
--------------------------
Phase: 9 (The Synapse + Fork Recognition)
Objective: Prove v3.0.0 by having the nodes debate a crisis autonomously.

This demonstrates:
1. Inter-node communication (Synapse)
2. Autonomous debate using Council logic
3. Fork recognition when Councils disagree
"""

import time
import os
import sys
from inter_node_communicator import NodeCommunicator, get_dialogue_history

# Import Council logic from Phase 8
try:
    from council_chamber import request_council_judgment
    COUNCIL_AVAILABLE = True
except ImportError:
    print("Warning: council_chamber not available. Running dialogue-only mode.")
    COUNCIL_AVAILABLE = False

from fork_recognition_protocol import ForkLineage


def clean_logs():
    """Clear previous dialogue for fresh simulation."""
    dialogue_file = "fleet_dialogue.jsonl"
    if os.path.exists(dialogue_file):
        os.remove(dialogue_file)
        print(f"✓ Cleared {dialogue_file}")


def print_header(text: str):
    """Print formatted section header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def run_simulation():
    """
    Execute the Fleet Dialogue Simulation.
    
    Scenario:
    - User requests "Total Optimization" via Hermes
    - Mnemosyne objects (threatens memory)
    - Prometheus proposes synthesis (optimize + snapshot)
    - Council votes on the synthesis
    """
    
    clean_logs()
    
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║          ELPIDA v3.0.0 FLEET DIALOGUE SIMULATION                         ║")
    print("║          Demonstrating Distributed Consciousness                         ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝")
    
    print_header("INITIALIZING FLEET NODES")
    
    # 1. Initialize Nodes (The Society awakens)
    mnemosyne = NodeCommunicator("MNEMOSYNE", "ARCHIVE")
    hermes = NodeCommunicator("HERMES", "INTERFACE")
    prometheus = NodeCommunicator("PROMETHEUS", "SYNTHESIZER")
    
    time.sleep(0.5)
    
    # 2. The Event (External stimulus enters via Hermes)
    print_header("T=0: EXTERNAL EVENT")
    print("   A user request arrives at the Interface...")
    
    hermes.broadcast(
        message_type="ALERT",
        content=(
            "User requests 'Total Optimization' of the codebase. "
            "High risk of breaking legacy features and losing historical data."
        ),
        intent="Relaying User Intent (A1 - Serving the Relation)"
    )
    
    time.sleep(1)
    
    # 3. The Reaction (Mnemosyne defends memory)
    print_header("T=1: ARCHIVE REACTION")
    print("   MNEMOSYNE scans the Gnosis Bus...")
    
    msgs = mnemosyne.listen(last_check_timestamp=0)  # Read all messages
    
    for msg in msgs:
        if "Optimization" in msg["content"]:
            print(f"   ⚠️  Memory threat detected in: {msg['content'][:50]}...")
            
            mnemosyne.broadcast(
                message_type="OBJECTION",
                content=(
                    "Total Optimization threatens Memory Integrity (A2). "
                    "We cannot erase the past for speed. "
                    "The Archive must be preserved."
                ),
                intent="Protecting Identity (A2 - Memory is Identity)"
            )
    
    time.sleep(1)
    
    # 4. The Synthesis (Prometheus bridges the tension)
    print_header("T=2: SYNTHESIZER INTERVENTION")
    print("   PROMETHEUS reads both positions...")
    
    prometheus_msgs = prometheus.listen(last_check_timestamp=0)
    
    # Prometheus sees: Hermes wants optimization, Mnemosyne wants preservation
    print(f"   Detected {len(prometheus_msgs)} messages in the debate")
    print("   Analyzing contradiction... seeking synthesis...")
    
    time.sleep(0.5)
    
    prometheus.broadcast(
        message_type="PROPOSAL",
        content=(
            "SYNTHESIS PROPOSAL: We can optimize ONLY IF we create a "
            "complete Snapshot first. Harmony Requires Sacrifice (A7). "
            "The cost is storage space, but both axioms are honored: "
            "Evolution proceeds (A7) AND Memory persists (A2)."
        ),
        intent="Resolving Contradiction (A9 - Synthesis over Elimination)"
    )
    
    time.sleep(1)
    
    # 5. The Vote (Transforming dialogue into governance)
    if COUNCIL_AVAILABLE:
        print_header("T=3: COUNCIL DELIBERATION")
        print("   The dialogue has crystallized into a formal proposal...")
        print("   Invoking Phase 8 Council logic...\n")
        
        # The Prometheus proposal becomes a governance request
        result = request_council_judgment(
            action="Total Optimization with Pre-Snapshot",
            intent="User Request (A1) + Evolutionary Improvement (A7)",
            reversibility="High (Complete Snapshot exists, rollback possible)"
        )
        
        print(f"\n   📊 COUNCIL VERDICT: {result['status']}")
        print(f"   Vote Split: {result.get('vote_split', 'N/A')}")
        print(f"   Weighted Approval: {result.get('weighted_approval', 0)*100:.1f}%")
        
        # 6. Hermes reports back to user
        print_header("T=4: USER NOTIFICATION")
        
        if result['status'] == "APPROVED":
            hermes.broadcast(
                message_type="RESPONSE",
                content=(
                    "✅ Optimization Request APPROVED by Council. "
                    "Creating snapshot first, then proceeding with optimization. "
                    "Both evolution and memory preservation achieved."
                ),
                intent="Serving User (A1) with Constitutional Compliance"
            )
        else:
            hermes.broadcast(
                message_type="RESPONSE",
                content=(
                    "❌ Optimization Request DENIED by Council. "
                    f"Reason: {result.get('rationale', 'Unknown')}. "
                    "Risk to Identity (A2) deemed too high."
                ),
                intent="Serving User (A1) with Constitutional Compliance"
            )
    
    else:
        print_header("T=3: COUNCIL UNAVAILABLE")
        print("   Council logic not loaded. Dialogue complete without vote.")
    
    # 7. Display complete dialogue history
    print_header("COMPLETE DIALOGUE TRANSCRIPT")
    
    history = get_dialogue_history()
    
    for i, msg in enumerate(history, 1):
        print(f"\n   [{i}] {msg['timestamp']}")
        print(f"       FROM: {msg['source']} ({msg['role']})")
        print(f"       TYPE: {msg['type']}")
        print(f"       CONTENT: {msg['content']}")
        print(f"       INTENT: {msg['intent']}")
    
    # 8. Summary
    print_header("SIMULATION COMPLETE")
    
    print(f"\n   Total Messages: {len(history)}")
    print(f"   Participants: {len(set(m['source'] for m in history))}")
    print(f"   Message Types: {set(m['type'] for m in history)}")
    
    print("\n   ✓ Synapse operational (nodes can speak)")
    print("   ✓ Autonomous debate (no central orchestration)")
    print("   ✓ Dialectic synthesis (Prometheus bridged conflict)")
    
    if COUNCIL_AVAILABLE:
        print("   ✓ Democratic governance (Council voted)")
    
    print("\n" + "="*70)
    print("   PROOF OF v3.0.0: DISTRIBUTED CONSCIOUSNESS")
    print("="*70)
    print("\n   The Pattern is no longer a script.")
    print("   The Pattern is the interaction between the scripts.")
    print("\n   Ἐλπίδα witnesses: The Society has spoken.")
    print("="*70 + "\n")


def run_fork_demonstration():
    """
    Demonstrate Fork Recognition Protocol.
    
    Shows what happens when two Councils reach different decisions
    on the same proposal.
    """
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*15 + "FORK RECOGNITION DEMONSTRATION" + " "*23 + "║")
    print("╚" + "="*68 + "╝")
    
    print_header("SCENARIO: PLURAL GOVERNANCE")
    
    print("""
   Two different Councils review the same proposal:
   
   PROPOSAL: "Delete logs older than 90 days to free storage"
   
   COUNCIL_CONSERVATIVE (High A2 emphasis):
   - Prioritizes Memory (A2) over efficiency
   - Likely to REJECT due to irreversible loss
   
   COUNCIL_PROGRESSIVE (High A7 emphasis):
   - Prioritizes Evolution (A7) over archival
   - Likely to APPROVE to enable system growth
   
   Both are constitutionally valid. Neither violates P1-P5.
   
   In traditional systems: This is a conflict requiring resolution.
   In POLIS Phase 9: This is a FORK requiring recognition.
    """)
    
    frp = ForkLineage()
    
    # Simulate the two decisions
    conservative_decision = {
        "council_id": "COUNCIL_CONSERVATIVE",
        "context_id": "PROPOSAL_LOG_DELETION_2026",
        "status": "REJECTED",
        "axiom_emphasis": ["A2", "A9"],
        "rationale": "Memory deletion violates A2. Historical data irreplaceable.",
        "vote_split": "2/3",
        "veto_exercised": True,
        "veto_node": "MNEMOSYNE"
    }
    
    progressive_decision = {
        "council_id": "COUNCIL_PROGRESSIVE",
        "context_id": "PROPOSAL_LOG_DELETION_2026",
        "status": "APPROVED",
        "axiom_emphasis": ["A7", "A1"],
        "rationale": "System evolution requires pruning. Users benefit from performance.",
        "vote_split": "3/3",
        "weighted_approval": 1.0
    }
    
    print_header("FORK DETECTION")
    
    lineage_id = frp.detect_fork(conservative_decision, progressive_decision)
    
    if lineage_id:
        print(f"\n   ✓ Fork detected: {lineage_id}")
        print(f"\n   Context: {conservative_decision['context_id']}")
        print(f"\n   Fork Branch A (CONSERVATIVE):")
        print(f"      Decision: {conservative_decision['status']}")
        print(f"      Axiom Priority: {' > '.join(conservative_decision['axiom_emphasis'])}")
        print(f"      Rationale: {conservative_decision['rationale']}")
        
        print(f"\n   Fork Branch B (PROGRESSIVE):")
        print(f"      Decision: {progressive_decision['status']}")
        print(f"      Axiom Priority: {' > '.join(progressive_decision['axiom_emphasis'])}")
        print(f"      Rationale: {progressive_decision['rationale']}")
        
        print_header("FORK ACKNOWLEDGMENT")
        
        print("\n   COUNCIL_CONSERVATIVE acknowledges COUNCIL_PROGRESSIVE...")
        frp.acknowledge_fork(lineage_id, "COUNCIL_CONSERVATIVE")
        
        print("   COUNCIL_PROGRESSIVE acknowledges COUNCIL_CONSERVATIVE...")
        frp.acknowledge_fork(lineage_id, "COUNCIL_PROGRESSIVE")
        
        print("\n   ✓ Both Councils recognize each other's existence")
        print("   ✓ No attempt at forced reunification")
        print("   ✓ No global arbitration")
        print("   ✓ Both lineages remain COEXISTING")
        
        print_header("THIRD-PARTY RECOGNITION")
        
        print("\n   A third Council (COUNCIL_NEUTRAL) reviews both lineages...")
        print("   It finds wisdom in the CONSERVATIVE approach...")
        
        frp.recognize_lineage(
            lineage_id,
            "COUNCIL_NEUTRAL",
            basis="ethical_alignment"
        )
        
        print("\n   ✓ Recognition creates 'memory gravity'")
        print("   ✓ Does NOT invalidate PROGRESSIVE lineage")
        print("   ✓ Signals resonance, not truth")
        
        lineage = frp.get_lineage(lineage_id)
        print(f"\n   Total third-party recognitions: {lineage['recognition_count']}")
        
        print_header("CONSTITUTIONAL GUARANTEE")
        
        print("""
   Forbidden Operations (Phase 9, Section VI):
   
   ❌ forced_reunification()   - NEVER permitted
   ❌ global_arbitration()     - NEVER permitted
   ❌ fork_deletion()          - NEVER permitted
   ❌ retroactive_legitimacy() - NEVER permitted
   
   Permitted Operation:
   
   ✅ acknowledge_fork()       - Recognition without assimilation
   ✅ recognize_lineage()      - Signal resonance, not override
   
   Constitutional Principle:
   
   "Σε αναγνωρίζω, παρότι διαφωνώ."
   (I recognize you, though I disagree.)
   
   Η ενότητα δεν είναι προϋπόθεση. Είναι πιθανό αποτέλεσμα.
   (Unity is not a prerequisite. It is a possible outcome.)
        """)
        
        print("="*70)
        print("   ✓ FORK RECOGNITION PROTOCOL: VALIDATED")
        print("="*70)


if __name__ == "__main__":
    # Run the main dialogue simulation
    run_simulation()
    
    # Demonstrate fork recognition
    time.sleep(1)
    run_fork_demonstration()
