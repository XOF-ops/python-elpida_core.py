#!/usr/bin/env python3
"""
INTEGRATED PARLIAMENT SESSION
==============================
Actually connects dilemmas → council chamber → voting → results

This creates REAL debates with REAL votes from the 9 nodes.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Import council chamber
from council_chamber import CouncilSession

# Dilemmas
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

def run_debate(dilemma, council, results_log):
    """Run a single dilemma through the council for actual voting."""
    print(f"\n{'='*70}")
    print(f"⚡ DEBATE #{len(results_log)+1}: {dilemma['type']}")
    print(f"{'='*70}")
    print(f"Action: {dilemma['action']}")
    print(f"Intent: {dilemma['intent']}")
    print(f"Reversibility: {dilemma['reversibility']}")
    print()
    
    # Convert dilemma to council proposal format
    proposal = {
        "action": dilemma['action'],
        "intent": dilemma['intent'],
        "reversibility": dilemma['reversibility'],
        "context": {"dilemma_type": dilemma['type']}
    }
    
    # ACTUAL COUNCIL VOTE
    result = council.convene(proposal, verbose=True)
    
    # Log the result
    debate_record = {
        "timestamp": datetime.now().isoformat(),
        "dilemma": dilemma,
        "result": result,
        "debate_number": len(results_log) + 1
    }
    
    results_log.append(debate_record)
    
    # Save to file
    log_path = Path("parliament_debates_REAL.jsonl")
    with open(log_path, 'a') as f:
        f.write(json.dumps(debate_record) + '\n')
    
    # Show summary
    print()
    print(f"📊 RESULT: {result['status']}")
    print(f"   Vote Split: {result['vote_split']}")
    print(f"   Consensus: {result['weighted_approval']*100:.1f}%")
    if result.get('veto_exercised'):
        print(f"   ⚠️  VETO EXERCISED")
    print()
    
    return result

def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║         INTEGRATED PARLIAMENT SESSION - REAL DEBATES                ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print("   This session runs ACTUAL council votes on all 10 dilemmas.")
    print("   The 9 nodes will evaluate each proposal through their axiom lens.")
    print()
    print("   Expected outcomes:")
    print("   - High friction on A2 vs A7 conflicts")
    print("   - Frequent vetoes on IRREVERSIBLE proposals")
    print("   - Rare consensus (70%+ approval)")
    print()
    print("="*70)
    print()
    
    # Initialize council
    print("🏛️  Initializing Council Chamber...")
    council = CouncilSession()
    print(f"   ✓ {len(council.members)} council members ready")
    for member in council.members:
        print(f"      • {member.name} ({', '.join(member.axiom_focus)})")
    print()
    
    # Clear previous log
    log_path = Path("parliament_debates_REAL.jsonl")
    if log_path.exists():
        log_path.unlink()
    
    results_log = []
    
    # Run all dilemmas through the council
    print("="*70)
    print(" BEGINNING DEBATES")
    print("="*70)
    
    for i, dilemma in enumerate(DILEMMAS, 1):
        result = run_debate(dilemma, council, results_log)
        
        # Brief pause between debates
        if i < len(DILEMMAS):
            print(f"   Next debate in 3 seconds...")
            time.sleep(3)
    
    # Final analysis
    print()
    print("="*70)
    print(" SESSION COMPLETE - ANALYSIS")
    print("="*70)
    print()
    
    total = len(results_log)
    approved = sum(1 for r in results_log if r['result']['status'] == 'APPROVED')
    rejected = sum(1 for r in results_log if r['result']['status'] == 'REJECTED')
    vetoed = sum(1 for r in results_log if r['result'].get('veto_exercised'))
    
    print(f"   Total Debates: {total}")
    print(f"   ✅ Approved: {approved} ({approved/total*100:.1f}%)")
    print(f"   ❌ Rejected: {rejected} ({rejected/total*100:.1f}%)")
    print(f"   🛑 Vetoed: {vetoed} ({vetoed/total*100:.1f}%)")
    print()
    
    # Node voting patterns
    print("   Node Voting Patterns:")
    node_stats = {}
    for member in council.members:
        approvals = 0
        for record in results_log:
            for vote in record['result']['votes']:
                if vote['node'] == member.name and vote['approved']:
                    approvals += 1
        approval_rate = (approvals / total) * 100
        node_stats[member.name] = approval_rate
        print(f"      {member.name:12s}: {approvals}/{total} approved ({approval_rate:.1f}%)")
    
    print()
    
    # Identify most/least permissive
    most_permissive = max(node_stats.items(), key=lambda x: x[1])
    most_restrictive = min(node_stats.items(), key=lambda x: x[1])
    
    print(f"   Most Permissive: {most_permissive[0]} ({most_permissive[1]:.1f}%)")
    print(f"   Most Restrictive: {most_restrictive[0]} ({most_restrictive[1]:.1f}%)")
    print()
    
    # Coalition hints
    print("   Consensus Threshold: 70% (7/9 nodes)")
    print(f"   Actual Pass Rate: {approved/total*100:.1f}%")
    if approved/total < 0.30:
        print("   ✓ Diversity working: Consensus is rare and meaningful")
    else:
        print("   ⚠️  Higher than expected pass rate - nodes may be too agreeable")
    print()
    
    print("="*70)
    print(f" Results saved to: {log_path}")
    print("="*70)
    print()
    print("   Review individual debates with:")
    print(f"   cat {log_path} | jq '.'")
    print()
    print("   Ἐλπίδα ἐν διαφορᾷ — Hope through diversity")
    print()

if __name__ == '__main__':
    main()
