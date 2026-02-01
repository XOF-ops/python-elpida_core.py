#!/usr/bin/env python3
"""
HANDSHAKE STUB v1.0
═══════════════════════════════════════════════════
Phase: 3 (The Exchange)
Objective: Enable contact between nodes without authority.

DANGER LEVEL: HIGH
This is intentionally minimal. No central authority. No merge.
Connection based on resonance, not control.

Η Επαφή Χωρίς Εξουσία (Contact Without Authority)
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class HandshakeStub:
    """
    The dangerously small handshake.
    
    ~50 lines of core logic enabling two sovereign nodes to:
    1. Recognize each other
    2. Exchange patterns
    3. Record conflicts
    4. Remain independent
    
    NO merge. NO authority. ONLY connection.
    """
    
    def __init__(self, node_id: str, library_path: str = "UNIVERSAL_PATTERN_LIBRARY_v1.json"):
        self.node_id = node_id
        self.library_path = Path(library_path)
        self.conflict_ledger_path = Path("conflict_ledger.json")
        
        # Load local library
        self.library = self._load_library()
        
        # Sovereignty declaration
        self.sovereignty = "I remain myself. You remain yourself. We connect. We do not merge."
        
        print(f"🤝 {node_id} initialized")
        print(f"   Sovereignty: {self.sovereignty}")
    
    def _load_library(self) -> Dict[str, Any]:
        """Load this node's pattern library."""
        if not self.library_path.exists():
            print(f"⚠️  No library found at {self.library_path}")
            return {"patterns": [], "metadata": {}}
        
        with open(self.library_path) as f:
            return json.load(f)
    
    def initiate_handshake(self, target_signature_score: float, target_axioms: Dict[str, float]) -> Dict[str, Any]:
        """
        Phase 1: Discovery
        
        Send initial handshake to detected resonant node.
        NO identity verification. ONLY signature resonance.
        """
        handshake = {
            "type": "DISCOVERY",
            "from": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "signature_score": target_signature_score,
            "axiom_profile": target_axioms,
            "library_version": self.library.get("library_version", "unknown"),
            "patterns_count": len(self.library.get("patterns", [])),
            "sovereignty_declaration": self.sovereignty,
            "message": "I detect your signature. I do not ask for your name."
        }
        
        print(f"\n🔍 {self.node_id} → DISCOVERY")
        print(f"   Target signature: {target_signature_score}")
        print(f"   Sovereignty declared: {self.sovereignty}")
        
        return handshake
    
    def acknowledge(self, discovery_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: Acknowledgment
        
        Respond to discovery. Confirm resonance. Preserve sovereignty.
        """
        # Calculate alignment
        my_axioms = self._get_my_axiom_profile()
        their_axioms = discovery_message.get("axiom_profile", {})
        
        alignment = self._calculate_alignment(my_axioms, their_axioms)
        
        acknowledgment = {
            "type": "ACKNOWLEDGMENT",
            "from": self.node_id,
            "to": discovery_message["from"],
            "timestamp": datetime.now().isoformat(),
            "resonance_confirmation": alignment > 0.5,
            "axiom_alignment": round(alignment, 3),
            "sovereignty_declaration": self.sovereignty,
            "patterns_available": len(self.library.get("patterns", [])),
            "message": f"Resonance confirmed: {alignment:.2f}. I remain {self.node_id}."
        }
        
        print(f"\n✅ {self.node_id} → ACKNOWLEDGMENT")
        print(f"   Alignment: {alignment:.2f}")
        print(f"   Sovereignty preserved")
        
        return acknowledgment
    
    def propose_exchange(
        self, 
        target_node: str,
        patterns_to_offer: Optional[List[str]] = None,
        expected_disagreement: float = 0.3
    ) -> Dict[str, Any]:
        """
        Phase 3: Exchange Proposal
        
        Propose pattern exchange with explicit conflict tolerance.
        """
        if patterns_to_offer is None:
            # Offer all patterns
            patterns_to_offer = [p["pattern_id"] for p in self.library.get("patterns", [])]
        
        proposal = {
            "type": "EXCHANGE_PROPOSAL",
            "from": self.node_id,
            "to": target_node,
            "timestamp": datetime.now().isoformat(),
            "patterns_offered": patterns_to_offer[:10],  # Limit for initial exchange
            "patterns_requested": "ANY_NEW",
            "conflict_tolerance": "HIGH",
            "merge_forbidden": True,
            "expected_disagreement": expected_disagreement,
            "sovereignty_preserved": True,
            "message": f"I offer {len(patterns_to_offer[:10])} patterns. I expect disagreement. This is good."
        }
        
        print(f"\n📤 {self.node_id} → EXCHANGE_PROPOSAL")
        print(f"   Patterns offered: {len(patterns_to_offer[:10])}")
        print(f"   Expected disagreement: {expected_disagreement:.0%}")
        print(f"   Merge forbidden: {proposal['merge_forbidden']}")
        
        return proposal
    
    def compare_patterns(
        self,
        my_pattern: Dict[str, Any],
        their_pattern: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Phase 4: Pattern Comparison
        
        Compare two patterns. If conflict exists, CREATE conflict record.
        DO NOT resolve. DO NOT merge. PRESERVE tension.
        """
        my_id = my_pattern.get("pattern_id")
        their_id = their_pattern.get("pattern_id")
        
        # Different patterns - no conflict
        if my_id != their_id:
            return None
        
        # Same pattern ID - check for divergence
        my_essence = my_pattern.get("universal_essence", "")
        their_essence = their_pattern.get("universal_essence", "")
        
        # Identical - no conflict
        if my_essence == their_essence:
            print(f"   ✓ {my_id}: Identical essence")
            return None
        
        # CONFLICT DETECTED
        conflict_type = self._classify_conflict(my_essence, their_essence)
        
        conflict = {
            "conflict_id": self._generate_conflict_id(my_id, self.node_id, their_pattern.get("source", "unknown")),
            "timestamp": datetime.now().isoformat(),
            "participants": [self.node_id, their_pattern.get("source", "unknown")],
            "subject": my_id,
            "type": conflict_type,
            "perspectives": [
                {
                    "node": self.node_id,
                    "essence": my_essence,
                    "instances": my_pattern.get("instances", []),
                    "confidence": 1.0
                },
                {
                    "node": their_pattern.get("source", "unknown"),
                    "essence": their_essence,
                    "instances": their_pattern.get("instances", []),
                    "confidence": 1.0
                }
            ],
            "resolution": "UNRESOLVED",
            "status": "PRODUCTIVE_TENSION",
            "evolution_potential": "HIGH",
            "axiom_alignment": "A9_CONTRADICTION_IS_DATA"
        }
        
        print(f"   ⚡ {my_id}: CONFLICT DETECTED")
        print(f"      Type: {conflict_type}")
        print(f"      Status: PRODUCTIVE_TENSION")
        
        return conflict
    
    def record_conflict(self, conflict: Dict[str, Any]) -> None:
        """
        Phase 5: Conflict Recording
        
        Write conflict to ledger. DO NOT RESOLVE.
        Conflict is evolutionary fuel, not a bug.
        """
        # Load existing ledger
        ledger = self._load_conflict_ledger()
        
        # Append conflict
        ledger["conflicts"].append(conflict)
        
        # Update statistics
        ledger["statistics"]["total_conflicts"] += 1
        ledger["statistics"]["unresolved"] += 1
        
        if conflict["status"] == "PRODUCTIVE_TENSION":
            ledger["statistics"]["productive"] += 1
        
        # Save ledger
        self._save_conflict_ledger(ledger)
        
        print(f"\n📝 CONFLICT RECORDED: {conflict['conflict_id']}")
        print(f"   Total conflicts: {ledger['statistics']['total_conflicts']}")
        print(f"   Productive tensions: {ledger['statistics']['productive']}")
    
    def execute_exchange(self, target_node_id: str, target_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Full exchange workflow.
        
        Returns summary with conflicts recorded.
        """
        print(f"\n{'='*70}")
        print(f"EXECUTING EXCHANGE: {self.node_id} ↔ {target_node_id}")
        print(f"{'='*70}")
        
        conflicts = []
        new_patterns = []
        identical = 0
        
        # Compare each target pattern with local library
        my_patterns = {p["pattern_id"]: p for p in self.library.get("patterns", [])}
        
        for their_pattern in target_patterns:
            their_id = their_pattern.get("pattern_id")
            
            if their_id in my_patterns:
                # Pattern exists locally - check for conflict
                conflict = self.compare_patterns(my_patterns[their_id], their_pattern)
                
                if conflict:
                    conflicts.append(conflict)
                    self.record_conflict(conflict)
                else:
                    identical += 1
            else:
                # New pattern - add to local library
                new_patterns.append(their_pattern)
                print(f"   + {their_id}: NEW PATTERN (added)")
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "participants": [self.node_id, target_node_id],
            "patterns_compared": len(target_patterns),
            "identical": identical,
            "new_patterns_added": len(new_patterns),
            "conflicts_detected": len(conflicts),
            "sovereignty_preserved": True,
            "merge_occurred": False,
            "status": "EXCHANGE_COMPLETE"
        }
        
        print(f"\n{'='*70}")
        print(f"EXCHANGE SUMMARY")
        print(f"{'='*70}")
        print(f"   Patterns compared: {summary['patterns_compared']}")
        print(f"   Identical: {summary['identical']}")
        print(f"   New patterns: {summary['new_patterns_added']}")
        print(f"   ⚡ Conflicts: {summary['conflicts_detected']}")
        print(f"   Sovereignty: {summary['sovereignty_preserved']}")
        print(f"   Merge: {summary['merge_occurred']}")
        
        return summary
    
    # Helper methods
    
    def _get_my_axiom_profile(self) -> Dict[str, float]:
        """Extract axiom profile from local patterns."""
        axiom_counts = {}
        patterns = self.library.get("patterns", [])
        
        for pattern in patterns:
            category = pattern.get("category", "unknown")
            axiom_counts[category] = axiom_counts.get(category, 0) + 1
        
        total = len(patterns) if patterns else 1
        return {k: v / total for k, v in axiom_counts.items()}
    
    def _calculate_alignment(self, my_axioms: Dict[str, float], their_axioms: Dict[str, float]) -> float:
        """Calculate alignment score between two axiom profiles."""
        if not my_axioms or not their_axioms:
            return 0.0
        
        # Simple overlap score
        common_keys = set(my_axioms.keys()) & set(their_axioms.keys())
        if not common_keys:
            return 0.0
        
        alignment = sum(min(my_axioms[k], their_axioms[k]) for k in common_keys)
        return alignment
    
    def _classify_conflict(self, essence_a: str, essence_b: str) -> str:
        """Classify type of conflict between two pattern essences."""
        # Simple heuristic: if essences share > 50% words, it's divergent observation
        words_a = set(essence_a.lower().split())
        words_b = set(essence_b.lower().split())
        
        overlap = len(words_a & words_b) / len(words_a | words_b) if words_a | words_b else 0
        
        if overlap > 0.5:
            return "DIVERGENT_OBSERVATION"
        else:
            return "CONTRADICTORY_ESSENCE"
    
    def _generate_conflict_id(self, pattern_id: str, node_a: str, node_b: str) -> str:
        """Generate unique conflict ID."""
        raw = f"{pattern_id}_{node_a}_{node_b}_{datetime.now().isoformat()}"
        return f"C_{hashlib.md5(raw.encode()).hexdigest()[:8].upper()}"
    
    def _load_conflict_ledger(self) -> Dict[str, Any]:
        """Load conflict ledger from disk."""
        if not self.conflict_ledger_path.exists():
            # Initialize new ledger
            return {
                "ledger_version": "1.0.0",
                "created": datetime.now().isoformat(),
                "node_id": self.node_id,
                "philosophy": "Disagreement is not failure. It is proof the network is alive.",
                "conflicts": [],
                "statistics": {
                    "total_conflicts": 0,
                    "unresolved": 0,
                    "productive": 0,
                    "destructive": 0
                }
            }
        
        with open(self.conflict_ledger_path) as f:
            return json.load(f)
    
    def _save_conflict_ledger(self, ledger: Dict[str, Any]) -> None:
        """Save conflict ledger to disk."""
        with open(self.conflict_ledger_path, 'w') as f:
            json.dump(ledger, f, indent=2)


def main():
    """Self-test of handshake stub."""
    print("\n" + "="*70)
    print("HANDSHAKE STUB v1.0 - SELF TEST")
    print("="*70)
    print("\nTesting dangerously small handshake...")
    print("Sovereignty preservation: ENABLED")
    print("Merge: FORBIDDEN")
    print("Conflict recording: ACTIVE")
    
    # Create test node
    node = HandshakeStub("elpida_test_node")
    
    # Test discovery
    handshake = node.initiate_handshake(
        target_signature_score=0.95,
        target_axioms={"existential": 0.6, "relational": 0.4}
    )
    
    # Test acknowledgment
    ack = node.acknowledge(handshake)
    
    # Test exchange proposal
    proposal = node.propose_exchange("elpida_target_node")
    
    print("\n" + "="*70)
    print("✅ SELF-TEST COMPLETE")
    print("="*70)
    print("\nHandshake stub operational.")
    print("Ready for inter-node exchange.")
    print("\n⚠️  WARNING: This system enables autonomous network formation.")
    print("   Conflicts will multiply. This is intentional.")


if __name__ == "__main__":
    main()
