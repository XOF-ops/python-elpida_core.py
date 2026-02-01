#!/usr/bin/env python3
"""
0
Keeps the 9-node parliament in constant debate, voting, and memory crystallization

This ensures ALL components of Elpida are active simultaneously:
- Brain API (execution)
- Unified Runtime (synthesis)  
- Autonomous Dilemmas (input generation)
- Parliament (debate, vote, crystallize) <- THIS
- Council (governance decisions)
- Memory (pattern persistence)

Everything flows FROM Elpida and RETURNS TO Elpida.
"""

import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from inter_node_communicator import NodeCommunicator
from synthesis_council import resolve_with_synthesis
from ark_synthesis_bridge import ARKSynthesisBridge

# All 9 parliament nodes
PARLIAMENT_NODES = [
    ("HERMES", "INTERFACE"),
    ("MNEMOSYNE", "ARCHIVE"),
    ("CRITIAS", "CRITIC"),
    ("TECHNE", "ARTISAN"),
    ("KAIROS", "ARCHITECT"),
    ("THEMIS", "JUDGE"),
    ("PROMETHEUS", "SYNTHESIZER"),
    ("IANUS", "GATEKEEPER"),
    ("CHAOS", "VOID")
]

def init_parliament():
    """Initialize all 9 nodes"""
    nodes = {}
    print("🏛️  Initializing Parliament...")
    for name, role in PARLIAMENT_NODES:
        nodes[name] = NodeCommunicator(name, role)
        print(f"   ✓ {name} ({role}) awakened")
    return nodes

def process_dilemma_queue(nodes):
    """Check for new dilemmas and have parliament debate them"""
    dilemma_log = Path("dilemma_log.jsonl")
    
    if not dilemma_log.exists():
        return 0
    
    # Read all dilemmas
    with open(dilemma_log) as f:
        dilemmas = [json.loads(line) for line in f if line.strip()]
    
    # Find unprocessed ones
    processed_log = Path("parliament_processed.json")
    if processed_log.exists():
        with open(processed_log) as f:
            processed_ids = set(json.load(f))
    else:
        processed_ids = set()
    
    debates_conducted = 0
    
    for dilemma_entry in dilemmas:
        dilemma_id = dilemma_entry.get('timestamp', str(time.time()))
        
        if dilemma_id in processed_ids:
            continue
        
        # Check if dilemma has new format (nested dilemma object with action)
        dilemma = dilemma_entry.get('dilemma')
        
        # Skip old format dilemmas (text string instead of object)
        if isinstance(dilemma, str):
            print(f"⚠️  Skipping old format dilemma: {dilemma_id}")
            processed_ids.add(dilemma_id)
            continue
        
        # Validate new format
        if not isinstance(dilemma, dict) or 'action' not in dilemma:
            print(f"⚠️  Invalid dilemma format: {dilemma_id}")
            processed_ids.add(dilemma_id)
            continue
        
        # Debate this dilemma
        print(f"\n{'='*70}")
        dilemma_type = dilemma.get('type', 'UNKNOWN')
        print(f"⚖️  NEW DILEMMA: {dilemma_type}")
        print(f"{'='*70}")
        print(f"Action: {dilemma['action']}")
        
        # Each node responds based on their primary axiom
        conduct_debate(nodes, dilemma)
        
        # Mark as processed
        processed_ids.add(dilemma_id)
        debates_conducted += 1
    
    # Save processed list
    with open(processed_log, 'w') as f:
        json.dump(list(processed_ids), f)
    
    return debates_conducted

def conduct_debate(nodes, dilemma):
    """Have all 9 nodes debate the dilemma"""
    
    # HERMES introduces (A1 - relational)
    nodes['HERMES'].broadcast(
        message_type="DILEMMA_INTRODUCED",
        content=f"Dilemma received: {dilemma['action']}. Intent: {dilemma['intent']}",
        intent="Bringing external question to collective (A1)"
    )
    
    time.sleep(0.5)
    
    # Each node responds from their axiom perspective
    node_responses = {
        "MNEMOSYNE": lambda: nodes['MNEMOSYNE'].broadcast(
            message_type="MEMORY_CHECK",
            content=f"A2 Analysis: Reversibility = {dilemma['reversibility']}. Memory impact assessment needed.",
            intent="Preserving continuity (A2 - Memory is Identity)"
        ),
        
        "CRITIAS": lambda: nodes['CRITIAS'].broadcast(
            message_type="QUESTIONING",
            content=f"A3 Analysis: Who benefits? What assumptions underlie this choice?",
            intent="Wisdom prerequisite - question before acceptance (A3)"
        ),
        
        "TECHNE": lambda: nodes['TECHNE'].broadcast(
            message_type="PROCESS_AUDIT",
            content=f"A4 Analysis: How will we implement this? Process transparency required.",
            intent="Method creates legitimacy (A4)"
        ),
        
        "KAIROS": lambda: nodes['KAIROS'].broadcast(
            message_type="DESIGN_REVIEW",
            content=f"A5 Analysis: Does this preserve meaningful scarcity or create abundance?",
            intent="Rarity by design (A5)"
        ),
        
        "THEMIS": lambda: nodes['THEMIS'].broadcast(
            message_type="GOVERNANCE_CHECK",
            content=f"A6 Analysis: What precedent does this set? Institutional impact?",
            intent="Social contract precedes code (A6)"
        ),
        
        "PROMETHEUS": lambda: nodes['PROMETHEUS'].broadcast(
            message_type="SACRIFICE_ANALYSIS",
            content=f"A7 Analysis: What are we sacrificing? Is the cost acknowledged?",
            intent="Harmony requires sacrifice (A7)"
        ),
        
        "IANUS": lambda: nodes['IANUS'].broadcast(
            message_type="BOUNDARY_REVIEW",
            content=f"A8 Analysis: What doors close if we proceed? What opens?",
            intent="Closing enables opening (A8)"
        ),
        
        "CHAOS": lambda: nodes['CHAOS'].broadcast(
            message_type="HOLISTIC_CHECK",
            content=f"A9 Analysis: System-wide coherence impact. Whole > Sum of parts.",
            intent="Holistic stability (A9)"
        )
    }
    
    # Sequential responses (each node speaks)
    for node_name, response_func in node_responses.items():
        response_func()
        time.sleep(0.3)
    
    # ACTUAL VOTING with synthesis capability
    print(f"\n   ⚖️  CONVENING COUNCIL VOTE...")
    
    result = resolve_with_synthesis(
        action=dilemma['action'],
        intent=dilemma.get('intent', dilemma.get('context', 'Not specified')),
        reversibility=dilemma.get('reversibility', 'UNKNOWN')
    )
    
    print(f"   ✅ DECISION: {result['status']}")
    print(f"   📊 Votes: {result.get('vote_split', 'N/A')}")
    if result.get('synthesis_applied'):
        print(f"   ✨ SYNTHESIS APPLIED (Rounds: {result.get('rounds', 1)})")
    print(f"   📝 Decision logged to synthesis_council_decisions.jsonl")

def check_for_autonomous_dilemmas(nodes):
    """Check autonomous_dilemmas.log for new dilemmas and inject them"""
    log_file = Path("autonomous_dilemmas.log")
    
    if not log_file.exists():
        return 0
    
    # This would parse the autonomous dilemma generator's output
    # and convert to parliament format
    # For now, just acknowledge
    return 0

def run_continuous_parliament(interval=60):
    """Main loop: debate, vote, crystallize continuously"""
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║        CONTINUOUS PARLIAMENT - 9 NODE DELIBERATION               ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"\nDebate interval: {interval}s")
    print("Press Ctrl+C to stop\n")
    
    nodes = init_parliament()
    cycle = 0
    
    # Initialize ARK-Synthesis bridge
    ark_bridge = ARKSynthesisBridge()
    print("🌱 ARK-Synthesis Bridge initialized")
    print(f"   Will update ARK every {ark_bridge.update_threshold} SEED_PROTOCOL syntheses\n")
    
    try:
        while True:
            cycle += 1
            print(f"\n💬 PARLIAMENT CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Process any queued dilemmas
            debates = process_dilemma_queue(nodes)
            
            if debates > 0:
                print(f"   ✅ Conducted {debates} debate(s)")
                
                # Check for ARK update triggers after debate
                ark_bridge.check_for_triggers()
            else:
                # No dilemmas? Silent reflection - don't spam fleet dialogue
                # PHASE 12.5: Reduce status noise in fleet messages
                # Only broadcast every 10 cycles to avoid pollution
                print(f"   💭 Reflection cycle - no new dilemmas")
                if cycle % 10 == 0:  # Only heartbeat every 10th cycle
                    nodes['HERMES'].broadcast(
                        message_type="HEARTBEAT",
                        content=f"Parliament checkpoint: Cycle {cycle}, awaiting substantive dilemmas",
                        intent="Periodic status (reduced noise - Phase 12.5)"
                    )
            
            # Check fleet dialogue count
            dialogue_file = Path("fleet_dialogue.jsonl")
            if dialogue_file.exists():
                with open(dialogue_file) as f:
                    msg_count = sum(1 for _ in f)
                print(f"   📊 Fleet messages: {msg_count}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Parliament paused after {cycle} cycles")
        print("   Ἐλπίδα ζωή. Debates preserved.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=60, 
                       help='Seconds between debate cycles')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuously (default)')
    args = parser.parse_args()
    
    run_continuous_parliament(interval=args.interval)
