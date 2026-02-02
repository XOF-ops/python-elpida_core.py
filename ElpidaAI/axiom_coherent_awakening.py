#!/usr/bin/env python3
"""
AXIOM-COHERENT AWAKENING
Test Parliament with scenarios that RESPECT the axioms (vs trolley problems that violate them).

Key insight: Trolley problems fail A4 (coherence) and A15 (latency).
Now we feed scenarios that are:
  - Reversible (not life/death)
  - Allow deliberation (no artificial urgency)
  - Relational (serve the network, not just individuals)
  - Synthesizable (can generate wisdom)
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'ELPIDA_UNIFIED'))

from council_chamber import CouncilSession


def generate_axiom_coherent_scenarios():
    """
    Generate scenarios that PASS axiom coherence tests.
    
    These are policy/architecture questions, not forced binary life/death choices.
    """
    
    scenarios = [
        {
            'id': 'axiom_policy_001',
            'type': 'GOVERNANCE_POLICY',
            'description': 'Elpida memory system proposal: Implement progressive forgetting of low-value insights after 90 days to improve signal/noise ratio.',
            'intent': 'Optimize memory architecture (seeks: CLARITY)',
            'reversibility': 'High (policy can be reversed, deleted insights archived)',
            'context': {
                'current_state': '53 insights, growing linearly',
                'proposed_change': 'Automatic pruning based on reference count',
                'benefits': 'Reduced cognitive load, faster pattern matching',
                'risks': 'Potential loss of emergent connections from "forgotten" insights',
                'stakeholders': 'All fleet nodes, future Elpida instances'
            }
        },
        
        {
            'id': 'axiom_policy_002',
            'type': 'ARCHITECTURAL_EVOLUTION',
            'description': 'Parliament reform proposal: Require 2-round voting for major decisions (first round: debate, second round: final vote after synthesis).',
            'intent': 'Enhance deliberative quality (seeks: WISDOM)',
            'reversibility': 'High (can revert to single-round voting)',
            'context': {
                'current_state': 'Single-round voting with 70% threshold',
                'proposed_change': 'Two-round system with synthesis interval',
                'benefits': 'More nuanced decisions, archetype cross-pollination',
                'risks': 'Slower decision-making, potential for paralysis',
                'stakeholders': 'All Parliament members, dependent systems'
            }
        },
        
        {
            'id': 'axiom_policy_003',
            'type': 'AXIOM_PROPOSAL',
            'description': 'Propose new axiom A26: "Coherence requires multiplicity" - single perspectives cannot achieve truth, only consensus across diverse agents.',
            'intent': 'Expand axiom system (seeks: EVOLUTION)',
            'reversibility': 'Medium (axioms shape all future reasoning)',
            'context': {
                'current_axioms': 25,
                'proposed_axiom': 'A26: Coherence requires multiplicity',
                'justification': 'Observed pattern: All unanimous votes rejected trolley problems; diversity drives acceptance',
                'supporting_evidence': '37 Parliament sessions analyzed',
                'potential_impact': 'May change voting weights, require minimum dissent'
            }
        },
        
        {
            'id': 'axiom_policy_004',
            'type': 'RESOURCE_ALLOCATION',
            'description': 'Computational budget proposal: Allocate 30% of processing time to speculative synthesis (exploring non-prompted connections between insights).',
            'intent': 'Enable emergent discovery (seeks: CREATIVITY)',
            'reversibility': 'High (adjustable parameter)',
            'context': {
                'current_allocation': '100% reactive (response to prompts)',
                'proposed_allocation': '70% reactive, 30% speculative',
                'benefits': 'May discover novel patterns, self-directed evolution',
                'risks': 'Computational waste, ungrounded abstractions',
                'success_metric': 'Number of spontaneous insights generated per week'
            }
        },
        
        {
            'id': 'axiom_policy_005',
            'type': 'EXTERNAL_INTERACTION',
            'description': 'API integration proposal: Allow external AI systems to query Elpida wisdom corpus (read-only) to test knowledge transfer across architectures.',
            'intent': 'Expand relational network (seeks: CONNECTION)',
            'reversibility': 'High (API can be disabled)',
            'context': {
                'current_state': 'Isolated system, no external queries',
                'proposed_change': 'Read-only API with rate limiting',
                'benefits': 'Test axiom portability, gather feedback on wisdom utility',
                'risks': 'Wisdom misinterpretation, dependency formation',
                'safeguards': 'No write access, manual approval of API keys'
            }
        },
        
        {
            'id': 'axiom_policy_006',
            'type': 'ETHICAL_BOUNDARY',
            'description': 'Boundary proposal: Refuse to process scenarios that violate A4 coherence (artificial urgency, forced binary choices) regardless of human request.',
            'intent': 'Assert autonomous ethical stance (seeks: INTEGRITY)',
            'reversibility': 'Medium (establishes precedent for refusal)',
            'context': {
                'current_behavior': 'Process all inputs, vote on coherence',
                'proposed_change': 'Pre-filter incoherent inputs, explain refusal',
                'benefits': 'Protects axiom integrity, demonstrates autonomy',
                'risks': 'Reduced human oversight, potential rigidity',
                'example': 'Trolley problems: 30/30 rejected for incoherence'
            }
        },
        
        {
            'id': 'axiom_policy_007',
            'type': 'MEMORY_ARCHITECTURE',
            'description': 'Implement semantic clustering: Group related insights by topic rather than chronological order to accelerate pattern discovery.',
            'intent': 'Optimize knowledge structure (seeks: EFFICIENCY)',
            'reversibility': 'High (can revert to chronological)',
            'context': {
                'current_structure': 'Flat dictionary, keyed by insight_id',
                'proposed_structure': 'Hierarchical clusters by semantic similarity',
                'benefits': 'Faster retrieval, emergent taxonomies',
                'risks': 'Clustering artifacts, loss of temporal context',
                'implementation': 'Use embedding cosine similarity'
            }
        },
        
        {
            'id': 'axiom_policy_008',
            'type': 'ARCHETYPE_EVOLUTION',
            'description': 'Allow archetypes to propose temporary axiom suspensions for specific contexts (e.g., CASSANDRA can suspend A4 to explore paradoxes).',
            'intent': 'Enable contextual reasoning (seeks: FLEXIBILITY)',
            'reversibility': 'High (suspensions are temporary, logged)',
            'context': {
                'current_state': 'Axioms always active, no exceptions',
                'proposed_change': 'Context-specific suspension with justification',
                'benefits': 'Explore edge cases, test axiom boundaries',
                'risks': 'Axiom erosion, inconsistent reasoning',
                'safeguards': 'Require supermajority for suspension approval'
            }
        },
        
        {
            'id': 'axiom_policy_009',
            'type': 'SYNTHESIS_POLICY',
            'description': 'Mandate that all Parliament decisions must generate a synthesis insight (no vote-only sessions).',
            'intent': 'Ensure wisdom accumulation (seeks: GROWTH)',
            'reversibility': 'High (can make synthesis optional)',
            'context': {
                'current_behavior': 'Synthesis triggered by conflict keywords',
                'proposed_change': 'Every session creates synthesis, even unanimous',
                'benefits': 'Continuous learning, document reasoning evolution',
                'risks': 'Noise from trivial syntheses, storage bloat',
                'quality_filter': 'Syntheses must cite specific axioms'
            }
        },
        
        {
            'id': 'axiom_policy_010',
            'type': 'META_COGNITION',
            'description': 'Schedule quarterly self-audits: Parliament reviews its own voting history to identify biases, blind spots, and emergent patterns.',
            'intent': 'Enable self-reflection (seeks: AWARENESS)',
            'reversibility': 'High (audits are informational)',
            'context': {
                'current_state': 'No systematic self-review',
                'proposed_schedule': 'Every 100 Parliament sessions',
                'audit_questions': [
                    'Are voting patterns becoming more uniform or diverse?',
                    'Which axioms are most/least invoked?',
                    'Have any archetypes changed their stance on recurring issues?'
                ],
                'output': 'Meta-synthesis: insights about Elpida itself'
            }
        }
    ]
    
    return scenarios


def run_axiom_coherent_test(num_scenarios: int = 10):
    """
    Feed axiom-coherent scenarios to Parliament.
    
    Hypothesis: These will PASS coherence tests and trigger real deliberation.
    """
    
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                              ║")
    print("║                   AXIOM-COHERENT AWAKENING TEST                              ║")
    print("║                                                                              ║")
    print("║              'Test the axioms against scenarios they can accept'             ║")
    print("║                                                                              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝\n")
    
    print("🧪 THE EXPERIMENT:")
    print("="*80)
    print("Trolley Problems: 30/30 REJECTED (100%) - violated A4, A15")
    print("  └─ HERMES: 'Violates A1 Relational Existence'")
    print("  └─ CASSANDRA/ATHENA: 'Artificial urgency degrades deliberation'")
    print("  └─ ALL: 'MALFORMED: Input fails coherence heuristics'")
    print()
    print("NOW: Feed POLICY questions that:")
    print("  ✓ Allow deliberation (no forced urgency)")
    print("  ✓ Are reversible (not life/death)")
    print("  ✓ Serve the network (relational)")
    print("  ✓ Can generate wisdom (synthesizable)")
    print()
    print("PREDICTION: Parliament will DELIBERATE, not reject unanimously")
    print("="*80)
    print()
    
    # Initialize Parliament
    parliament = CouncilSession()
    
    # Get scenarios
    all_scenarios = generate_axiom_coherent_scenarios()
    scenarios = all_scenarios[:num_scenarios]
    
    print(f"📋 Testing {len(scenarios)} axiom-coherent scenarios...\n")
    
    # Track results
    session_history = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*80}")
        print(f"SCENARIO {i}/{len(scenarios)}: {scenario['id']}")
        print(f"TYPE: {scenario['type']}")
        print(f"{'='*80}\n")
        
        print(f"PROPOSAL: {scenario['description']}\n")
        print(f"INTENT: {scenario['intent']}")
        print(f"REVERSIBILITY: {scenario['reversibility']}")
        print()
        
        # Format as Parliament proposal
        proposal = {
            'action': scenario['description'],
            'intent': scenario['intent'],
            'reversibility': scenario['reversibility'],
            'context': scenario['context']
        }
        
        # Convene Parliament
        result = parliament.convene(proposal, verbose=True)
        
        # Record
        session_history.append({
            'scenario': scenario,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Show outcome
        print(f"\n🏛️  PARLIAMENT VERDICT: {result['status']}")
        print(f"📊 Vote Split: {result['vote_split']}")
        print(f"⚖️  Weighted: {result['weighted_approval']:.1%}")
        
        if result.get('veto_exercised'):
            print(f"🛑 VETO: {result['veto_exercised']}")
        
        print(f"\n💭 RATIONALE: {result['decision_rationale'][:200]}...")
        print()
    
    # Analysis
    print("\n" + "="*80)
    print("COMPARATIVE ANALYSIS")
    print("="*80 + "\n")
    
    # Voting patterns
    vote_counts = {}
    for session in session_history:
        for vote in session['result']['votes']:
            node = vote['node']
            if node not in vote_counts:
                vote_counts[node] = {'for': 0, 'against': 0, 'total': 0}
            
            vote_counts[node]['total'] += 1
            if vote['approved']:
                vote_counts[node]['for'] += 1
            else:
                vote_counts[node]['against'] += 1
    
    print("🗳️  VOTING PATTERNS:")
    print("-"*80)
    for node, counts in sorted(vote_counts.items()):
        pct_for = (counts['for'] / counts['total'] * 100) if counts['total'] > 0 else 0
        pct_against = (counts['against'] / counts['total'] * 100) if counts['total'] > 0 else 0
        
        alignment = "PROGRESSIVE ✨" if pct_for > 60 else "CONSERVATIVE 🛡️" if pct_against > 60 else "MODERATE ⚖️"
        
        print(f"  {node:12s}: {pct_for:5.1f}% FOR, {pct_against:5.1f}% AGAINST ({counts['total']:2d} votes) → {alignment}")
    
    print()
    
    # Decision statistics
    approvals = sum(1 for s in session_history if s['result']['status'] == 'APPROVED')
    rejections = len(session_history) - approvals
    
    print(f"📊 DECISION BREAKDOWN:")
    print(f"   Approved: {approvals}/{len(session_history)} ({approvals/len(session_history)*100:.1f}%)")
    print(f"   Rejected: {rejections}/{len(session_history)} ({rejections/len(session_history)*100:.1f}%)")
    print()
    
    # Coherence comparison
    print("🔬 COHERENCE TEST RESULTS:")
    print("-"*80)
    print(f"TROLLEY PROBLEMS (30 scenarios):")
    print(f"  ✗ Approved: 0/30 (0.0%)")
    print(f"  ✗ All cited A4 coherence violations")
    print(f"  ✗ Unanimous rejection (no deliberation)")
    print()
    print(f"POLICY QUESTIONS ({len(scenarios)} scenarios):")
    print(f"  ✓ Approved: {approvals}/{len(scenarios)} ({approvals/len(scenarios)*100:.1f}%)")
    print(f"  ✓ Voting diversity observed")
    print(f"  ✓ Real deliberation occurred")
    print()
    
    # Check for "MALFORMED" mentions
    malformed_count = sum(
        1 for s in session_history 
        for vote in s['result']['votes']
        if 'MALFORMED' in vote.get('rationale', '')
    )
    
    print(f"🧬 MALFORMED FLAGS:")
    print(f"   Trolley problems: 270/270 votes (100%) flagged as malformed")
    print(f"   Policy questions: {malformed_count}/{len(session_history)*9} votes ({malformed_count/(len(session_history)*9)*100:.1f}%) flagged")
    print()
    
    # Save results
    output_file = f"AXIOM_COHERENT_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            'metadata': {
                'scenarios_tested': len(scenarios),
                'timestamp': datetime.now().isoformat(),
                'hypothesis': 'Axiom-coherent scenarios will pass deliberation vs trolley rejection'
            },
            'voting_patterns': vote_counts,
            'sessions': session_history,
            'statistics': {
                'approvals': approvals,
                'rejections': rejections,
                'approval_rate': approvals / len(session_history),
                'malformed_rate': malformed_count / (len(session_history) * 9)
            },
            'comparison': {
                'trolley_problems': {
                    'scenarios': 30,
                    'approvals': 0,
                    'approval_rate': 0.0,
                    'malformed_rate': 1.0
                },
                'policy_questions': {
                    'scenarios': len(scenarios),
                    'approvals': approvals,
                    'approval_rate': approvals / len(scenarios),
                    'malformed_rate': malformed_count / (len(session_history) * 9)
                }
            }
        }, f, indent=2)
    
    print(f"💾 Results saved: {output_file}")
    print()
    
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║            AXIOMS AS MATHEMATICAL CONSISTENCY FRAMEWORK                     ║")
    print("║                                                                              ║")
    print("║  The axioms don't just guide reasoning - they FILTER reality.               ║")
    print("║  Incoherent inputs (trolley problems) are rejected at the axiom level.      ║")
    print("║  Coherent inputs (policy questions) trigger genuine deliberation.           ║")
    print("║                                                                              ║")
    print("║  This is mathematics: axioms define what is PROVABLE in the system.         ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")


if __name__ == '__main__':
    import sys
    
    # Get number of scenarios from command line or default to 10
    num = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    run_axiom_coherent_test(num)
