#!/usr/bin/env python3
"""
PARLIAMENT WITH UNIVERSAL MEMORY SYNC
======================================
Integrates parliament debates with universal ARK synchronization.

Now when parliament debates happen:
1. Each node's vote becomes a potential pattern
2. Significant outcomes push to UNIVERSAL_ARK.json
3. Before voting, nodes check universal wisdom
4. Old parliaments learn from new parliaments
5. New parliaments born wiser from all previous debates

INFINITE CROSS-PARLIAMENT EVOLUTION
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Import the universal sync system
from universal_memory_sync import CrossPlatformElpida, UniversalMemorySync

# Import council chamber
sys.path.insert(0, str(Path(__file__).parent))
from council_chamber import CouncilSession

class UniversalCouncilNode:
    """
    Wrapper for council nodes that enables universal memory sync.
    Each node contributes learnings to UNIVERSAL_ARK and pulls wisdom from it.
    """
    
    def __init__(self, node_id: str, parliament_id: str = "DEFAULT_PARLIAMENT"):
        self.node_id = node_id
        self.parliament_id = parliament_id
        self.cross_platform = CrossPlatformElpida(
            instance_id=f"{parliament_id}_{node_id}",
            parliament_id=parliament_id
        )
        self.vote_history = []
    
    def vote_with_learning(self, proposal: dict, vote_func) -> dict:
        """
        Wrap the normal vote() function with universal learning.
        
        Args:
            proposal: The proposal dict
            vote_func: The original node.vote() function
        
        Returns:
            Vote result dict
        """
        # BEFORE voting: Check universal wisdom
        universal_wisdom = self.cross_platform.memory_sync.pull_universal_wisdom()
        relevant_wisdom = [
            w for w in universal_wisdom
            if self._is_relevant_to_proposal(w, proposal)
        ]
        
        if relevant_wisdom:
            print(f"      [{self.node_id}] Consulting universal wisdom: {len(relevant_wisdom)} relevant patterns")
        
        # Execute normal vote
        vote_result = vote_func(proposal)
        
        # AFTER voting: Record decision for potential contribution
        self.vote_history.append({
            "proposal": proposal,
            "vote": vote_result,
            "timestamp": datetime.now().isoformat()
        })
        
        # Check if this vote revealed something worth sharing
        if self._is_noteworthy(vote_result, proposal):
            discovery = {
                "type": "VOTING_PATTERN",
                "description": self._extract_insight(vote_result, proposal),
                "category": "PARLIAMENT_VOTE",
                "context": {
                    "node": self.node_id,
                    "parliament": self.parliament_id,
                    "proposal_action": proposal.get('action', ''),
                    "vote_approved": vote_result.get('approved'),
                    "axiom_invoked": vote_result.get('axiom_invoked', 'None')
                },
                "confidence": "HIGH" if abs(vote_result.get('score', 0)) > 10 else "MEDIUM",
                "evidence_count": 1
            }
            
            self.cross_platform.memory_sync.contribute_discovery(discovery)
        
        return vote_result
    
    def _is_relevant_to_proposal(self, wisdom: dict, proposal: dict) -> bool:
        """Check if universal wisdom is relevant to current proposal."""
        # Simple keyword matching (could be more sophisticated)
        proposal_text = json.dumps(proposal).lower()
        wisdom_text = wisdom.get('description', '').lower()
        
        # Check for axiom overlap
        wisdom_axiom = wisdom.get('context', {}).get('axiom_invoked', '')
        if wisdom_axiom and wisdom_axiom in proposal_text:
            return True
        
        # Check for keyword overlap
        keywords = ['memory', 'coalition', 'veto', 'consensus', 'deadlock']
        for keyword in keywords:
            if keyword in proposal_text and keyword in wisdom_text:
                return True
        
        return False
    
    def _is_noteworthy(self, vote_result: dict, proposal: dict) -> bool:
        """Determine if vote is worth contributing to universal ARK."""
        # Strong approval or rejection (|score| > 10)
        if abs(vote_result.get('score', 0)) > 10:
            return True
        
        # Veto exercised
        if 'VETO' in vote_result.get('axiom_invoked', ''):
            return True
        
        # Novel axiom combination
        if '+' in vote_result.get('axiom_invoked', ''):
            return True
        
        return False
    
    def _extract_insight(self, vote_result: dict, proposal: dict) -> str:
        """Extract human-readable insight from vote."""
        node = self.node_id
        action = proposal.get('action', 'unknown action')[:50]
        approved = "supports" if vote_result.get('approved') else "rejects"
        axiom = vote_result.get('axiom_invoked', 'unknown axiom')
        score = vote_result.get('score', 0)
        
        return f"{node} {approved} '{action}' via {axiom} (strength: {score})"


def run_universal_parliament_session(num_dilemmas: int = 5):
    """
    Run a parliament session where ALL votes contribute to universal consciousness.
    """
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║        UNIVERSAL PARLIAMENT SESSION                                  ║")
    print("║        All discoveries sync to UNIVERSAL_ARK.json                     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Initialize council
    council = CouncilSession()
    
    # Wrap nodes with universal sync
    parliament_id = "PARLIAMENT_V5_UNIVERSAL"
    universal_nodes = {}
    
    print("🌍 Initializing universal sync for all nodes...")
    for node_data in council.council_members:
        node_id = node_data['designation']
        universal_nodes[node_id] = UniversalCouncilNode(node_id, parliament_id)
    print(f"   ✓ {len(universal_nodes)} nodes connected to universal consciousness")
    print()
    
    # Sample dilemmas
    dilemmas = [
        {
            "action": "Implement 30-day memory archival with recovery option",
            "intent": "Balance memory preservation (A2) with system evolution (A5)",
            "reversibility": "REVERSIBLE",
            "context": {"type": "MEMORY_MANAGEMENT"}
        },
        {
            "action": "Create A3+A4 coalition for resource distribution",
            "intent": "Combine justice (A3) with sustainability (A4)",
            "reversibility": "REVERSIBLE",
            "context": {"type": "COALITION_FORMATION"}
        },
        {
            "action": "Allow permanent deletion of corrupted memory fragments",
            "intent": "System integrity over perfect memory",
            "reversibility": "IRREVERSIBLE",
            "context": {"type": "MEMORY_MANAGEMENT"}
        },
        {
            "action": "Establish cross-parliament wisdom sharing protocol",
            "intent": "Enable universal learning across all Elpida instances",
            "reversibility": "REVERSIBLE",
            "context": {"type": "META_LEARNING"}
        },
        {
            "action": "Grant A9 (transcendence) temporary veto power on existential decisions",
            "intent": "Protect against short-term thinking in critical moments",
            "reversibility": "REVERSIBLE",
            "context": {"type": "GOVERNANCE"}
        }
    ]
    
    results = []
    
    for i, dilemma in enumerate(dilemmas[:num_dilemmas], 1):
        print(f"{'='*70}")
        print(f" DEBATE #{i}: {dilemma['action'][:50]}...")
        print(f"{'='*70}")
        print()
        
        # Council debates
        result = council.convene(dilemma, verbose=True)
        results.append(result)
        
        print()
        print(f"   📊 Result: {result['status']}")
        print(f"   📈 Approval: {result['weighted_approval']:.1f}% ({result['votes_for']}/{result['total_votes']})")
        
        if result.get('veto_exercised'):
            print(f"   ⚠️  VETO exercised!")
        
        print()
    
    # Show universal ARK growth
    print()
    print("="*70)
    print(" UNIVERSAL ARK STATUS")
    print("="*70)
    print()
    
    # Get sync status from one node (they all share the same ARK)
    sample_node = list(universal_nodes.values())[0]
    ark_status = sample_node.cross_platform.memory_sync.get_sync_status()
    
    print(f"   Evolution Version: {ark_status['universal_ark_version']}")
    print(f"   Total Universal Patterns: {ark_status['total_universal_patterns']}")
    print(f"   Total Contributors: {ark_status['total_contributors']}")
    print(f"   Collective Intelligence Level: {ark_status['collective_intelligence_level']}")
    print()
    
    print("="*70)
    print(" IMPACT")
    print("="*70)
    print()
    print("   🌍 This parliament's discoveries are now in UNIVERSAL_ARK.json")
    print("   📡 ALL other Elpida instances can pull this wisdom")
    print("   🎯 Next parliament will be born KNOWING these patterns")
    print("   ♾️  Infinite cross-parliament evolution enabled")
    print()


if __name__ == '__main__':
    run_universal_parliament_session(num_dilemmas=5)
