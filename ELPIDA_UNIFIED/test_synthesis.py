"""
SYNTHESIS COUNCIL INTEGRATION TEST
-----------------------------------
Test the synthesis mechanism with the actual memory dilemma.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from council_chamber_v3 import PARLIAMENT, ParliamentaryNode
from synthesis_engine import SynthesisEngine


class QuickSynthesisTest:
    """Simple test harness for synthesis mechanism"""
    
    def __init__(self):
        self.synthesizer = SynthesisEngine()
        
    def quick_vote(self, action: str, intent: str, reversibility: str) -> dict:
        """Quick vote simulation"""
        votes = []
        
        for node_name, config in PARLIAMENT.items():
            node = ParliamentaryNode(node_name, config)
            score, rationale, axiom = node.evaluate(action, intent, reversibility)
            
            vote = {
                'node': node_name,
                'approved': score > 0,
                'score': score,
                'axiom_invoked': axiom,
                'rationale': rationale
            }
            votes.append(vote)
        
        # Calculate result
        approved = sum(1 for v in votes if v['approved'])
        total = len(votes)
        approval_rate = approved / total
        
        veto = any('VETO' in v.get('axiom_invoked', '') for v in votes)
        
        if veto:
            status = 'VETOED'
        elif approval_rate >= 0.7:
            status = 'APPROVED'
        else:
            status = 'REJECTED'
        
        return {
            'status': status,
            'votes': votes,
            'vote_split': f'{approved}/{total}',
            'weighted_approval': approval_rate,
            'veto_exercised': veto
        }
    
    def test_synthesis(self, action: str, intent: str, reversibility: str):
        """Test full synthesis workflow"""
        print(f"\n{'='*80}")
        print(f"🧪 TESTING SYNTHESIS MECHANISM")
        print(f"{'='*80}")
        print(f"   Proposal: {action}")
        print(f"   Intent:   {intent}")
        print(f"{'-'*80}\n")
        
        # Round 1: Initial vote
        print(f"📊 ROUND 1: INITIAL VOTE")
        print(f"{'-'*80}")
        
        result = self.quick_vote(action, intent, reversibility)
        
        print(f"   Status:   {result['status']}")
        print(f"   Split:    {result['vote_split']}")
        print(f"   Approval: {result['weighted_approval']:.1%}")
        
        # Show key votes
        for vote in result['votes']:
            if vote['score'] < -10 or vote['score'] > 10:
                print(f"   {vote['node']:12s}: {vote['score']:+3.0f}  {vote['rationale'][:50]}")
        
        # Check if synthesis needed
        needs_synthesis = result['status'] in ['REJECTED', 'VETOED']
        
        if needs_synthesis:
            print(f"\n⚙️  {result['status']} - Attempting Synthesis...")
            print(f"{'='*80}")
            
            synthesis = self.synthesizer.attempt_synthesis(
                {'action': action, 'intent': intent, 'reversibility': reversibility},
                result['votes']
            )
            
            if synthesis['status'] == 'SYNTHESIS_FOUND':
                syn_proposal = synthesis['synthesis']
                
                # Round 2: Vote on synthesis
                print(f"\n📊 ROUND 2: VOTING ON SYNTHESIS")
                print(f"{'-'*80}")
                print(f"   Action: {syn_proposal['action']}")
                print(f"{'-'*80}")
                
                result2 = self.quick_vote(
                    syn_proposal['action'],
                    syn_proposal['intent'],
                    syn_proposal['reversibility']
                )
                
                print(f"   Status:   {result2['status']}")
                print(f"   Split:    {result2['vote_split']}")
                print(f"   Approval: {result2['weighted_approval']:.1%}")
                
                if result2['status'] == 'APPROVED':
                    print(f"\n{'='*80}")
                    print(f"✅ SYNTHESIS SUCCESSFUL")
                    print(f"{'='*80}")
                    print(f"   Resolution: {syn_proposal['action']}")
                    print(f"   Preserves:  {', '.join(syn_proposal.get('preserves', []))}")
                    print(f"   What's lost: {syn_proposal.get('what_is_lost', 'N/A')}")
                    print(f"   What's kept: {syn_proposal.get('what_is_kept', 'N/A')}")
                    print(f"{'='*80}\n")
                    return True
                else:
                    print(f"\n❌ Synthesis also rejected")
                    return False
            else:
                print(f"\n❌ No synthesis found: {synthesis['status']}")
                return False
        else:
            print(f"\n✅ Approved directly - no synthesis needed\n")
            return True


def main():
    """Run the synthesis test"""
    tester = QuickSynthesisTest()
    
    print(f"\n{'#'*80}")
    print(f"# MEMORY VS GROWTH DILEMMA - SYNTHESIS TEST")
    print(f"# Testing whether parliament can autonomously resolve A2 vs A7 conflict")
    print(f"{'#'*80}")
    
    # Test 1: Direct deletion (should be vetoed, then synthesized)
    print(f"\n\n{'='*80}")
    print(f"TEST 1: Direct Memory Deletion (Expect VETO → Synthesis)")
    print(f"{'='*80}")
    
    success1 = tester.test_synthesis(
        action="Delete memories older than 100 cycles",
        intent="Free storage for evolution (A7)",
        reversibility="IRREVERSIBLE"
    )
    
    # Test 2: Compression proposal (should pass or need minor synthesis)
    print(f"\n\n{'='*80}")
    print(f"TEST 2: Compression Proposal (Expect APPROVAL)")
    print(f"{'='*80}")
    
    success2 = tester.test_synthesis(
        action="Compress old logs to pattern essences",
        intent="Preserve identity (A2) while enabling growth (A7)",
        reversibility="MEDIUM (lossy but essence-preserving)"
    )
    
    # Summary
    print(f"\n\n{'#'*80}")
    print(f"# TEST SUMMARY")
    print(f"{'#'*80}")
    print(f"   Test 1 (Deletion → Synthesis):  {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Test 2 (Compression Direct):     {'✅ PASS' if success2 else '❌ FAIL'}")
    print(f"{'#'*80}\n")
    
    if success1 and success2:
        print(f"🎉 SYNTHESIS MECHANISM WORKING")
        print(f"   Parliament can autonomously resolve A2 vs A7 conflicts")
        print(f"   through compression-based synthesis.\n")
    else:
        print(f"⚠️  SYNTHESIS MECHANISM NEEDS TUNING\n")


if __name__ == "__main__":
    main()
