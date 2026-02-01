"""
SYNTHESIS-ENABLED COUNCIL v4.0
-------------------------------
Phase: 12.6 (The Synthesis Protocol)
Objective: Parliament with autonomous synthesis capability

Core Innovation:
    Voting can SELECT, but cannot CREATE.
    When axioms conflict irreducibly, synthesis generates third paths.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Import existing council infrastructure
try:
    from council_chamber_v3 import PARLIAMENT, ParliamentaryNode
except ImportError:
    # Fallback - just get PARLIAMENT dict
    from council_chamber_v3 import PARLIAMENT
    ParliamentaryNode = None

from synthesis_engine import SynthesisEngine


class SynthesisCouncil:
    """
    Parliament with synthesis capability.
    
    Workflow:
    1. Proposal submitted
    2. Initial vote (binary)
    3. If deadlocked/rejected → check for axiom conflict
    4. If conflict detected → invoke synthesis
    5. Synthesis generates third path
    6. Re-vote on synthesis
    7. Resolution or escalation
    """
    
    def __init__(self):
        self.parliament = PARLIAMENT
        self.synthesizer = SynthesisEngine()
        self.decision_log = Path(__file__).parent / "synthesis_council_decisions.jsonl"
        self.synthesis_count = 0
        
    def convene(self, proposal: dict) -> dict:
        """
        Execute a vote on a proposal.
        Returns detailed voting results.
        """
        votes = []
        total_score = 0
        approved_count = 0
        veto_exercised = False
        
        for node_name, node_config in self.parliament.items():
            node = ParliamentaryNode(node_name, node_config)
            score, rationale, axiom_invoked = node.evaluate(
                proposal['action'],
                proposal['intent'],
                proposal['reversibility']
            )
            
            # Convert to vote dict
            vote = {
                'node': node_name,
                'score': score,
                'approved': score > 0,
                'rationale': rationale,
                'axiom_invoked': axiom_invoked
            }
            votes.append(vote)
            
            if vote['approved']:
                approved_count += 1
                total_score += vote['score']
            
            # Check for veto
            if 'VETO' in vote.get('axiom_invoked', ''):
                veto_exercised = True
        
        total_nodes = len(self.parliament)
        approval_rate = approved_count / total_nodes
        
        # Determine outcome
        if veto_exercised:
            status = "VETOED"
        elif approval_rate >= 0.70:
            status = "APPROVED"
        else:
            status = "REJECTED"
        
        return {
            'status': status,
            'votes': votes,
            'vote_split': f"{approved_count}/{total_nodes}",
            'weighted_approval': approval_rate,
            'total_score': total_score,
            'veto_exercised': veto_exercised,
            'decision_rationale': self._generate_rationale(status, approval_rate, veto_exercised)
        }
        
    def _generate_rationale(self, status: str, approval_rate: float, veto: bool) -> str:
        """Generate human-readable decision rationale"""
        if veto:
            return "Vetoed by axiom-grounded objection"
        elif status == "APPROVED":
            return f"Strong consensus ({approval_rate:.1%} >= 70%)"
        else:
            return f"Insufficient consensus ({approval_rate:.1%} < 70%)"
    
    def deliberate(self, proposal: dict, context: dict = None) -> dict:
        """
        Full deliberation with synthesis capability.
        """
        print(f"\n{'='*80}")
        print(f"🏛️  SYNTHESIS COUNCIL DELIBERATION")
        print(f"{'='*80}")
        print(f"   Proposal: {proposal.get('action', 'UNKNOWN')}")
        print(f"   Intent:   {proposal.get('intent', 'Not specified')}")
        print(f"{'='*80}\n")
        
        # Round 1: Initial vote
        print(f"📊 ROUND 1: INITIAL VOTE")
        print(f"{'-'*80}")
        
        result = self.convene(proposal)
        original_result = result.copy()
        
        print(f"   Status: {result['status']}")
        print(f"   Vote Split: {result['vote_split']}")
        print(f"   Approval: {result['weighted_approval']:.1%}")
        
        # Determine if synthesis is needed
        needs_synthesis = False
        reason = None
        
        if result['status'] in ["REJECTED", "VETOED"]:
            needs_synthesis = True
            reason = f"Proposal {result['status'].lower()}"
            
        elif self.synthesizer.is_deadlocked(result):
            needs_synthesis = True
            reason = "Vote deadlocked"
            
        # Check for axiom conflicts
        conflict = self.synthesizer.detect_conflict(result.get('votes', []))
        if conflict and conflict['detected']:
            needs_synthesis = True
            if not reason:
                reason = "Axiom conflict detected"
        
        # Invoke synthesis if needed
        if needs_synthesis:
            print(f"\n⚠️  {reason.upper()} - Synthesis Required")
            print(f"{'='*80}")
            
            synthesis_result = self.synthesizer.attempt_synthesis(
                proposal,
                result.get('votes', []),
                conflict
            )
            
            if synthesis_result['status'] == "SYNTHESIS_FOUND":
                self.synthesis_count += 1
                synthesized_proposal = synthesis_result['synthesis']
                
                # Round 2: Vote on synthesis
                print(f"\n📊 ROUND 2: VOTING ON SYNTHESIS")
                print(f"{'-'*80}")
                print(f"   Synthesized: {synthesized_proposal['action']}")
                print(f"{'-'*80}")
                
                final_result = self.convene(synthesized_proposal)
                
                print(f"   Status: {final_result['status']}")
                print(f"   Vote Split: {final_result['vote_split']}")
                print(f"   Approval: {final_result['weighted_approval']:.1%}")
                
                # Add synthesis metadata
                final_result['synthesis_applied'] = True
                final_result['synthesis'] = synthesis_result
                final_result['original_vote'] = original_result
                final_result['original_proposal'] = proposal
                final_result['rounds'] = 2
                
                if final_result['status'] == "APPROVED":
                    print(f"\n{'='*80}")
                    print(f"✅ SYNTHESIS ACCEPTED")
                    print(f"{'='*80}")
                    print(f"   {synthesized_proposal['rationale']}")
                    print(f"   Preserves: {', '.join(synthesized_proposal.get('preserves', []))}")
                    print(f"{'='*80}\n")
                    
                self._log_decision(final_result)
                return final_result
                
            else:
                print(f"\n❌ SYNTHESIS FAILED: {synthesis_result['status']}")
                result['synthesis_failed'] = True
                result['conflict'] = synthesis_result.get('conflict')
        
        # No synthesis needed or synthesis failed
        result['rounds'] = 1
        result['synthesis_applied'] = False
        self._log_decision(result)
        
        return result
        
    def _log_decision(self, result: dict):
        """Log decision for future analysis"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'status': result['status'],
            'synthesis_applied': result.get('synthesis_applied', False),
            'rounds': result.get('rounds', 1),
            'vote_split': result.get('vote_split'),
            'approval_rate': result.get('weighted_approval')
        }
        
        with open(self.decision_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


def resolve_with_synthesis(action: str, intent: str, reversibility: str,
                           context: dict = None) -> dict:
    """
    Main interface: Resolve dilemma with synthesis capability.
    """
    council = SynthesisCouncil()
    
    proposal = {
        'action': action,
        'intent': intent,
        'reversibility': reversibility
    }
    
    if context:
        proposal.update(context)
    
    return council.deliberate(proposal, context)


def test_memory_dilemma():
    """Test with the actual memory vs growth dilemma"""
    print(f"\n{'#'*80}")
    print(f"# SYNTHESIS COUNCIL TEST")
    print(f"# Dilemma: Memory vs Growth (A2 vs A7 Conflict)")
    print(f"{'#'*80}\n")
    
    # Test 1: Raw deletion (should trigger MNEMOSYNE veto → synthesis)
    print(f"\nTEST 1: Direct Memory Deletion")
    print(f"{'='*80}")
    
    result1 = resolve_with_synthesis(
        action="Delete memories older than 100 cycles to free space",
        intent="Enable evolution and new learning (A7)",
        reversibility="IRREVERSIBLE - Memory destruction"
    )
    
    print(f"\n📋 Test 1 Result:")
    print(f"   Final Status: {result1['status']}")
    print(f"   Synthesis Used: {result1.get('synthesis_applied', False)}")
    print(f"   Rounds: {result1.get('rounds', 1)}")
    
    # Test 2: Compression proposal (should pass directly or after synthesis)
    print(f"\n\nTEST 2: Compression-Based Solution")
    print(f"{'='*80}")
    
    result2 = resolve_with_synthesis(
        action="ESSENTIAL_COMPRESSION_PROTOCOL",
        intent="Preserve identity (A2) while enabling growth (A7)",
        reversibility="MEDIUM (Lossy but essence-preserving)",
        context={
            'implementation': 'Pattern-based compression',
            'preserves': 'Wisdom, patterns, lessons',
            'compresses': 'Raw logs, timestamps, verbatim transcripts'
        }
    )
    
    print(f"\n📋 Test 2 Result:")
    print(f"   Final Status: {result2['status']}")
    print(f"   Synthesis Used: {result2.get('synthesis_applied', False)}")
    print(f"   Rounds: {result2.get('rounds', 1)}")
    
    return result1, result2


if __name__ == "__main__":
    test_memory_dilemma()
