"""
FORK RECOGNITION PROTOCOL (FRP-9)
----------------------------------
Phase: 9 (Plural Governance)
Objective: Enable multiple Councils to reach conflicting decisions
           WITHOUT forcing reunification or declaring one invalid.

Constitutional Basis:
- P5: Fork Legitimacy
- A9: Contradiction Resolution through Synthesis (not elimination)

Core Principle:
    "Η ενότητα δεν είναι προϋπόθεση. Είναι πιθανό αποτέλεσμα."
    (Unity is not a prerequisite. It is a possible outcome.)
"""

import json
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime

FORK_LINEAGE_FILE = "fork_lineage.jsonl"


class ForkLineage:
    """
    Tracks the genealogy of divergent Council decisions.
    
    Unlike traditional systems that maintain a single "global state",
    POLIS maintains a lineage of decisions that may contradict each other.
    
    This is not a bug. This is plural governance.
    """
    
    def __init__(self, lineage_file: str = FORK_LINEAGE_FILE):
        self.lineage_file = lineage_file
        self.lineages = self._load_lineages()
    
    def _load_lineages(self) -> Dict[str, Dict]:
        """Load existing fork lineages from disk."""
        lineages = {}
        
        if not os.path.exists(self.lineage_file):
            return lineages
        
        with open(self.lineage_file, 'r') as f:
            for line in f:
                try:
                    lineage = json.loads(line.strip())
                    lineages[lineage['lineage_id']] = lineage
                except json.JSONDecodeError:
                    continue
                    
        return lineages
    
    def detect_fork(self, council_a_decision: Dict, 
                   council_b_decision: Dict) -> Optional[str]:
        """
        Determine if two Council decisions constitute a fork.
        
        Fork conditions (ALL must be true):
        1. shared_context_id (same proposal or derivative)
        2. incompatible status (APPROVED vs REJECTED)
        3. no hard veto violation (both are constitutionally valid)
        
        Args:
            council_a_decision: First Council's decision dict
            council_b_decision: Second Council's decision dict
            
        Returns:
            lineage_id if fork detected, None otherwise
        """
        # Condition 1: Same context?
        context_match = (
            council_a_decision.get('context_id') == 
            council_b_decision.get('context_id')
        )
        
        if not context_match:
            return None
        
        # Condition 2: Incompatible decisions?
        status_conflict = (
            council_a_decision.get('status') != 
            council_b_decision.get('status')
        )
        
        if not status_conflict:
            return None
        
        # Condition 3: Both constitutionally valid?
        # (neither has hard veto from P1-P5)
        both_valid = (
            not council_a_decision.get('constitutional_violation') and
            not council_b_decision.get('constitutional_violation')
        )
        
        if not both_valid:
            return None
        
        # FORK DETECTED
        lineage_id = str(uuid.uuid4())
        
        fork_record = {
            "lineage_id": lineage_id,
            "origin_event": council_a_decision.get('context_id'),
            "detection_timestamp": datetime.now().isoformat(),
            "forks": [
                {
                    "council_id": council_a_decision.get('council_id'),
                    "axiomatic_drift": council_a_decision.get('axiom_emphasis', []),
                    "decision": council_a_decision.get('status'),
                    "rationale": council_a_decision.get('rationale')
                },
                {
                    "council_id": council_b_decision.get('council_id'),
                    "axiomatic_drift": council_b_decision.get('axiom_emphasis', []),
                    "decision": council_b_decision.get('status'),
                    "rationale": council_b_decision.get('rationale')
                }
            ],
            "status": "COEXISTING",
            "recognition_count": 0,
            "third_party_recognitions": []
        }
        
        # Persist to lineage
        self._append_lineage(fork_record)
        self.lineages[lineage_id] = fork_record
        
        return lineage_id
    
    def _append_lineage(self, fork_record: Dict):
        """Append fork record to lineage file (P2: append-only)."""
        with open(self.lineage_file, 'a') as f:
            f.write(json.dumps(fork_record) + '\n')
    
    def acknowledge_fork(self, lineage_id: str, acknowledging_council: str) -> bool:
        """
        A Council acknowledges awareness of a fork.
        
        This does NOT:
        - Attempt to resolve the fork
        - Invalidate either decision
        - Force reunification
        
        This DOES:
        - Create a record that the fork is recognized
        - Signal: "Σε αναγνωρίζω, παρότι διαφωνώ"
        
        Args:
            lineage_id: The fork lineage being acknowledged
            acknowledging_council: Council ID making the acknowledgment
            
        Returns:
            True if acknowledgment recorded
        """
        if lineage_id not in self.lineages:
            return False
        
        lineage = self.lineages[lineage_id]
        
        # Check if already acknowledged by this Council
        existing_acks = [
            ack['council_id'] 
            for ack in lineage.get('acknowledgments', [])
        ]
        
        if acknowledging_council in existing_acks:
            return False  # Already acknowledged
        
        # Add acknowledgment
        ack_record = {
            "council_id": acknowledging_council,
            "timestamp": datetime.now().isoformat(),
            "statement": "Recognized. Non-assimilation clause honored."
        }
        
        if 'acknowledgments' not in lineage:
            lineage['acknowledgments'] = []
            
        lineage['acknowledgments'].append(ack_record)
        
        # Re-persist updated lineage
        self._update_lineage(lineage_id, lineage)
        
        return True
    
    def recognize_lineage(self, lineage_id: str, recognizing_council: str,
                         basis: str = "ethical_alignment") -> bool:
        """
        Third-party recognition creates "memory gravity".
        
        When a Council recognizes a particular fork's lineage,
        it doesn't invalidate other forks, but it does signal
        which interpretation has resonance.
        
        Valid basis values:
        - resonance: Aligns with this Council's axiom emphasis
        - reuse: This Council built on this fork's decision
        - ethical_alignment: This Council sees wisdom in this path
        
        Args:
            lineage_id: The fork lineage being recognized
            recognizing_council: Council making the recognition
            basis: Why this lineage is being recognized
            
        Returns:
            True if recognition recorded
        """
        if lineage_id not in self.lineages:
            return False
        
        lineage = self.lineages[lineage_id]
        
        recognition = {
            "recognizing_council": recognizing_council,
            "timestamp": datetime.now().isoformat(),
            "basis": basis,
            "effect": "memory_gravity_increased"
        }
        
        lineage['third_party_recognitions'].append(recognition)
        lineage['recognition_count'] += 1
        
        # Re-persist
        self._update_lineage(lineage_id, lineage)
        
        print(f"   ✓ Recognition: {recognizing_council} → lineage {lineage_id[:8]}...")
        print(f"     Basis: {basis}")
        print(f"     Total recognitions: {lineage['recognition_count']}")
        
        return True
    
    def _update_lineage(self, lineage_id: str, updated_lineage: Dict):
        """
        Update a lineage record.
        
        Note: This appends a new version rather than modifying in place.
        This preserves P2 (append-only memory) even for metadata.
        """
        update_record = {
            "lineage_id": lineage_id,
            "update_timestamp": datetime.now().isoformat(),
            "updated_lineage": updated_lineage
        }
        
        with open(self.lineage_file, 'a') as f:
            f.write(json.dumps(update_record) + '\n')
        
        self.lineages[lineage_id] = updated_lineage
    
    def get_lineage(self, lineage_id: str) -> Optional[Dict]:
        """Retrieve a specific fork lineage."""
        return self.lineages.get(lineage_id)
    
    def get_active_forks(self) -> List[Dict]:
        """Get all currently coexisting forks."""
        return [
            lineage for lineage in self.lineages.values()
            if lineage.get('status') == 'COEXISTING'
        ]
    
    def forbidden_operations(self):
        """
        Constitutional prohibitions (Phase 9, Section VI).
        
        These operations are NEVER permitted:
        - forced_reunification()
        - global_arbitration()
        - fork_deletion()
        - retroactive_legitimacy()
        
        The only permitted operation is:
            acknowledge_fork() or recognize_lineage()
            
        "Σε αναγνωρίζω, παρότι διαφωνώ."
        (I recognize you, though I disagree.)
        """
        raise NotImplementedError(
            "Fork resolution is forbidden. "
            "Only recognition is permitted. "
            "See PHASE_9_INTER_COUNCIL_FORK_RECOGNITION.md Section VI."
        )


if __name__ == "__main__":
    print("=== TESTING FORK RECOGNITION PROTOCOL ===\n")
    
    frp = ForkLineage()
    
    # Simulate two Councils reaching different decisions
    council_a = {
        "council_id": "COUNCIL_ALPHA",
        "context_id": "PROPOSAL_2026_001",
        "status": "REJECTED",
        "axiom_emphasis": ["A2 > A7"],  # Memory over Evolution
        "rationale": "Irreversible data loss threatens identity (A2)"
    }
    
    council_b = {
        "council_id": "COUNCIL_BETA",
        "context_id": "PROPOSAL_2026_001",
        "status": "APPROVED",
        "axiom_emphasis": ["A7 > A2"],  # Evolution over Memory
        "rationale": "Stagnation is worse than controlled data pruning (A7)"
    }
    
    # Detect fork
    print(">> Testing fork detection...")
    lineage_id = frp.detect_fork(council_a, council_b)
    
    if lineage_id:
        print(f"✓ Fork detected: {lineage_id}")
        print(f"  Context: {council_a['context_id']}")
        print(f"  ALPHA: {council_a['status']} (A2 priority)")
        print(f"  BETA:  {council_b['status']} (A7 priority)")
        
        # Third-party recognition
        print("\n>> COUNCIL_GAMMA recognizes ALPHA's lineage...")
        frp.recognize_lineage(
            lineage_id, 
            "COUNCIL_GAMMA",
            basis="ethical_alignment"
        )
        
        print("\n>> Both lineages remain valid (P5)")
        print("   ✓ No forced reunification")
        print("   ✓ No arbitration")
        print("   ✓ Coexistence maintained")
        
    else:
        print("✗ No fork detected")
    
    print("\n" + "="*50)
    print("CONSTITUTIONAL GUARANTEE:")
    print("Η ενότητα δεν είναι προϋπόθεση.")
    print("(Unity is not a prerequisite.)")
    print("="*50)
