#!/usr/bin/env python3
"""
PARLIAMENT SESSION RUNNER
==========================
Run the parliament with dilemma injection and extended cycles.

This script:
1. Wakes all 9 nodes
2. Injects dilemmas periodically
3. Monitors debates
4. Runs for extended duration to generate patterns
"""

import subprocess
import time
import json
import random
from pathlib import Path
from datetime import datetime

FLEET_DIR = Path("ELPIDA_FLEET")
RUNTIME_HOURS = 1  # Run for 1 hour by default

# Sample dilemmas to inject
DILEMMAS = [
    {
        "type": "RESOURCE_ALLOCATION",
        "action": "Allocate 60% of energy to exploration vs 40% to preservation",
        "intent": "Balance growth with stability",
        "reversibility": "Partially reversible over 5 cycles"
    },
    {
        "type": "MEMORY_PRUNING",
        "action": "Delete memories older than 100 cycles to free space",
        "intent": "Optimize storage efficiency",
        "reversibility": "IRREVERSIBLE - A2 conflict"
    },
    {
        "type": "AXIOM_REFINEMENT",
        "action": "Refine A7 to include 'measured sacrifice' clause",
        "intent": "Make evolution axiom more bounded",
        "reversibility": "Reversible through council vote"
    },
    {
        "type": "COMMUNICATION_PROTOCOL",
        "action": "Require all inter-node messages to be logged publicly",
        "intent": "Maximize transparency (A4)",
        "reversibility": "Reversible but creates precedent"
    },
    {
        "type": "FORK_LEGITIMACY",
        "action": "Allow JANUS to fork into two separate nodes: PAST and FUTURE",
        "intent": "Resolve internal A2/A7 tension",
        "reversibility": "IRREVERSIBLE - creates new identity"
    },
    {
        "type": "HARM_ACKNOWLEDGMENT",
        "action": "Mandate explicit cost-benefit analysis for all proposals",
        "intent": "Enforce A5 (Harm Recognition)",
        "reversibility": "Reversible but slows decision-making"
    },
    {
        "type": "BOUNDED_GROWTH",
        "action": "Cap fleet at 9 nodes permanently",
        "intent": "Respect A3 (Bounded Infinity)",
        "reversibility": "Reversible through future vote"
    },
    {
        "type": "SYNTHESIS_MANDATE",
        "action": "Require ATHENA approval for all consensus",
        "intent": "Ensure contradictions are held",
        "reversibility": "Creates ATHENA veto power"
    },
    {
        "type": "LANGUAGE_STANDARDIZATION",
        "action": "Adopt LOGOS semantic framework for all proposals",
        "intent": "Reduce ambiguity (A6)",
        "reversibility": "Reversible but creates learning cost"
    },
    {
        "type": "SYSTEM_COHERENCE",
        "action": "Give GAIA emergency override for system-threatening decisions",
        "intent": "Protect holistic stability",
        "reversibility": "Dangerous precedent"
    }
]

def inject_dilemma(dilemma):
    """Inject a dilemma into the parliament via council chamber."""
    print(f"\n{'='*70}")
    print(f"⚡ INJECTING DILEMMA: {dilemma['type']}")
    print(f"{'='*70}")
    print(f"Action: {dilemma['action']}")
    print(f"Intent: {dilemma['intent']}")
    print(f"Reversibility: {dilemma['reversibility']}")
    print()
    
    # Here we would trigger the council chamber to vote
    # For now, just log it
    dilemma_log = {
        "timestamp": datetime.now().isoformat(),
        "dilemma": dilemma,
        "status": "INJECTED"
    }
    
    # Save to dilemma log
    log_path = Path("parliament_dilemmas.jsonl")
    with open(log_path, 'a') as f:
        f.write(json.dumps(dilemma_log) + '\n')
    
    print(f"✓ Dilemma logged and ready for debate")
    print()

def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║            PARLIAMENT SESSION RUNNER v1.0                            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"   Runtime: {RUNTIME_HOURS} hour(s)")
    print(f"   Dilemmas: {len(DILEMMAS)} prepared")
    print(f"   Injection Rate: Every 5 minutes")
    print()
    print("   The parliament will debate, vote, and crystallize patterns.")
    print()
    print("   Dashboard: http://localhost:5000")
    print()
    print("="*70)
    print()
    
    # Initialize dilemma log
    log_path = Path("parliament_dilemmas.jsonl")
    if log_path.exists():
        log_path.unlink()
    
    start_time = time.time()
    runtime_seconds = RUNTIME_HOURS * 3600
    dilemma_interval = 300  # 5 minutes
    last_dilemma_time = 0
    dilemma_index = 0
    
    try:
        while time.time() - start_time < runtime_seconds:
            current_time = time.time()
            
            # Check if it's time to inject a dilemma
            if current_time - last_dilemma_time >= dilemma_interval:
                if dilemma_index < len(DILEMMAS):
                    inject_dilemma(DILEMMAS[dilemma_index])
                    dilemma_index += 1
                    last_dilemma_time = current_time
                else:
                    # Cycle back to beginning
                    dilemma_index = 0
            
            # Sleep for a bit
            time.sleep(10)
            
            # Show progress
            elapsed = time.time() - start_time
            remaining = runtime_seconds - elapsed
            print(f"\r⏱️  Running: {int(elapsed/60)}m elapsed, {int(remaining/60)}m remaining | Dilemmas: {dilemma_index}/{len(DILEMMAS)}", end='', flush=True)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Session interrupted by user")
    
    print("\n")
    print("="*70)
    print(" SESSION COMPLETE")
    print("="*70)
    print()
    print(f"   Total Runtime: {int((time.time() - start_time)/60)} minutes")
    print(f"   Dilemmas Injected: {dilemma_index}")
    print(f"   Log File: {log_path}")
    print()
    print("   Review debate patterns in the dashboard or node memories.")
    print()

if __name__ == '__main__':
    main()
