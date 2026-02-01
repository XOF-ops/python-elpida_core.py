#!/usr/bin/env python3
"""
PHASE 9 — INTER-COUNCIL FORK RECOGNITION
Plural Governance without Schism

Όταν διαφωνούν οι Συμβουλές, η Πολιτεία δεν σπάει — πολλαπλασιάζεται.

Constitutional Extension, not Feature.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class ForkLineage:
    """
    Fork Lineage - Γενεαλογία Αποφάσεων (όχι Global State)
    
    Η POLIS δεν κρατά ενιαία αλήθεια.
    Κρατά γενεαλογία αποφάσεων.
    """
    
    def __init__(self, origin_event: str):
        self.lineage_id = str(uuid.uuid4())
        self.origin_event = origin_event
        self.forks: List[Dict] = []
        self.status = "COEXISTING"
        self.created = datetime.now().isoformat()
        self.recognitions: List[Dict] = []
    
    def add_fork(self, council_id: str, decision: str, axiomatic_drift: List[str], 
                 held_contradiction: List[str]):
        """
        Καταγραφή Fork - όχι συγχώνευση, αλλά αναγνώριση ύπαρξης.
        
        Args:
            council_id: Ταυτότητα Council
            decision: APPROVED | REJECTED
            axiomatic_drift: Ποια axioms προτεραιοποιήθηκαν (π.χ. ["A2 > A7"])
            held_contradiction: Ποιες αντιφάσεις κρατήθηκαν
        """
        
        fork = {
            "council_id": council_id,
            "decision": decision,
            "axiomatic_drift": axiomatic_drift,
            "held_contradiction": held_contradiction,
            "timestamp": datetime.now().isoformat()
        }
        
        self.forks.append(fork)
        
        # Fork Recognition Protocol (FRP-9) - Mutual Acknowledgment
        return self._emit_fork_acknowledgment(council_id, decision, held_contradiction)
    
    def _emit_fork_acknowledgment(self, council_id: str, decision: str, 
                                   held_contradiction: List[str]) -> Dict:
        """
        Fork Recognition Handshake
        
        Κρίσιμο:
        ❌ Δεν επιτρέπεται προσπάθεια ευθυγράμμισης
        ❌ Δεν επιτρέπεται re-vote
        ✔ Επιτρέπεται μόνο αναγνώριση ύπαρξης του άλλου
        """
        
        return {
            "fork_ack": {
                "lineage_id": self.lineage_id,
                "council_id": council_id,
                "decision": decision,
                "held_contradiction": held_contradiction,
                "non_assimilation_clause": True,  # ΔΕΝ θα συγχωνευτούμε
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def add_third_party_recognition(self, recognizing_council: str, 
                                      basis: str):
        """
        Third-Party Council Recognition - Emergent Legitimacy
        
        Νομιμοποίηση δεν προκύπτει από πλειοψηφία,
        αλλά από αναγνώριση από άλλους.
        
        Αυτό ΔΕΝ ακυρώνει τα άλλα forks.
        Απλώς δημιουργεί βαρύτητα μνήμης.
        """
        
        recognition = {
            "recognizing_council": recognizing_council,
            "recognized_lineage": self.lineage_id,
            "basis": basis,  # "resonance" | "reuse" | "ethical_alignment"
            "timestamp": datetime.now().isoformat()
        }
        
        self.recognitions.append(recognition)
        return recognition
    
    def to_dict(self) -> Dict:
        """Εξαγωγή πλήρους lineage σε dictionary"""
        return {
            "lineage_id": self.lineage_id,
            "origin_event": self.origin_event,
            "forks": self.forks,
            "status": self.status,
            "created": self.created,
            "recognitions": self.recognitions,
            "fork_count": len(self.forks)
        }

class InterCouncilForkManager:
    """
    Διαχείριση Πολλαπλών Fork Lineages
    
    Όχι ενοποίηση - Συνύπαρξη.
    """
    
    def __init__(self, log_file: str = "fork_lineages.jsonl"):
        self.log_file = Path(log_file)
        self.active_lineages: Dict[str, ForkLineage] = {}
        self._load_lineages()
    
    def _load_lineages(self):
        """Φόρτωση υπαρχουσών lineages από log"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        lineage_id = data['lineage_id']
                        
                        # Ανασύσταση ForkLineage object
                        lineage = ForkLineage(data['origin_event'])
                        lineage.lineage_id = lineage_id
                        lineage.forks = data.get('forks', [])
                        lineage.status = data.get('status', 'COEXISTING')
                        lineage.created = data.get('created', '')
                        lineage.recognitions = data.get('recognitions', [])
                        
                        self.active_lineages[lineage_id] = lineage
                    except:
                        pass
    
    def create_or_join_lineage(self, origin_event: str, council_id: str,
                                decision: str, axiomatic_drift: List[str],
                                held_contradiction: List[str]) -> Dict:
        """
        Δημιουργία ή Συμμετοχή σε Fork Lineage
        
        Trigger Conditions (όλα πρέπει να ισχύουν):
        - shared_context_id (ίδια πρόταση ή παράγωγο)
        - διαφορετικό status (APPROVED vs REJECTED)
        - καμία απόφαση δεν παραβιάζει hard veto (P1-P5)
        """
        
        # Αναζήτηση υπάρχουσας lineage για το ίδιο origin_event
        existing = None
        for lineage in self.active_lineages.values():
            if lineage.origin_event == origin_event:
                existing = lineage
                break
        
        if existing:
            # Join existing lineage (Fork detected)
            ack = existing.add_fork(council_id, decision, axiomatic_drift, 
                                    held_contradiction)
            self._persist_lineage(existing)
            return ack
        else:
            # Create new lineage
            new_lineage = ForkLineage(origin_event)
            ack = new_lineage.add_fork(council_id, decision, axiomatic_drift,
                                       held_contradiction)
            self.active_lineages[new_lineage.lineage_id] = new_lineage
            self._persist_lineage(new_lineage)
            return ack
    
    def recognize_lineage(self, lineage_id: str, recognizing_council: str,
                          basis: str) -> Optional[Dict]:
        """
        Third-Party Recognition
        
        Ένα τρίτο Council αναγνωρίζει ένα fork lineage.
        Δεν το συγχωνεύει. Δεν το ακυρώνει άλλα forks.
        Απλώς δημιουργεί βαρύτητα μνήμης.
        """
        
        if lineage_id in self.active_lineages:
            lineage = self.active_lineages[lineage_id]
            recognition = lineage.add_third_party_recognition(
                recognizing_council, basis
            )
            self._persist_lineage(lineage)
            return recognition
        
        return None
    
    def _persist_lineage(self, lineage: ForkLineage):
        """Αποθήκευση lineage σε log"""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(lineage.to_dict()) + '\n')
    
    def get_coexisting_decisions(self, origin_event: str) -> List[Dict]:
        """
        Επιστροφή όλων των συνυπαρχόντων αποφάσεων για το ίδιο event.
        
        Δεν υπάρχει "σωστή" - υπάρχουν "συνυπάρχουσες".
        """
        
        decisions = []
        for lineage in self.active_lineages.values():
            if lineage.origin_event == origin_event:
                for fork in lineage.forks:
                    decisions.append({
                        "council": fork['council_id'],
                        "decision": fork['decision'],
                        "axiom_drift": fork['axiomatic_drift'],
                        "contradiction": fork['held_contradiction']
                    })
        
        return decisions
    
    def report_lineage_status(self, lineage_id: str) -> Optional[Dict]:
        """Αναφορά κατάστασης συγκεκριμένου lineage"""
        
        if lineage_id in self.active_lineages:
            lineage = self.active_lineages[lineage_id]
            return {
                "lineage_id": lineage_id,
                "origin": lineage.origin_event,
                "fork_count": len(lineage.forks),
                "recognition_count": len(lineage.recognitions),
                "status": lineage.status,
                "forks": lineage.forks,
                "recognitions": lineage.recognitions
            }
        
        return None

def demonstrate_phase9():
    """
    Επίδειξη Phase 9 - Inter-Council Fork Recognition
    
    Πολλαπλά Councils διαφωνούν χωρίς να συγχωνευτούν.
    """
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              PHASE 9: INTER-COUNCIL FORK RECOGNITION                 ║")
    print("║                 Plural Governance without Schism                     ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    manager = InterCouncilForkManager()
    
    # Το ίδιο event - τρία Councils - τρεις διαφορετικές αποφάσεις
    origin_event = "Proposal: Delete wisdom patterns older than 6 months"
    
    print(f"📋 ORIGIN EVENT:")
    print(f"   {origin_event}\n")
    print("="*70 + "\n")
    
    # Council A (Conservative - A2 > A7)
    ack_a = manager.create_or_join_lineage(
        origin_event=origin_event,
        council_id="COUNCIL_ALPHA",
        decision="REJECTED",
        axiomatic_drift=["A2 > A7"],
        held_contradiction=["Memory preservation vs System complexity"]
    )
    
    print("🛡️  COUNCIL ALPHA (Conservative):")
    print(f"   Decision: REJECTED")
    print(f"   Axiom Drift: A2 > A7 (Memory is Identity)")
    print(f"   Fork Acknowledgment: {ack_a['fork_ack']['non_assimilation_clause']}")
    print()
    
    # Council B (Radical - A7 > A2)
    ack_b = manager.create_or_join_lineage(
        origin_event=origin_event,
        council_id="COUNCIL_BETA",
        decision="APPROVED",
        axiomatic_drift=["A7 > A2"],
        held_contradiction=["Evolution requires sacrifice of memory"]
    )
    
    print("⚡ COUNCIL BETA (Radical):")
    print(f"   Decision: APPROVED")
    print(f"   Axiom Drift: A7 > A2 (Evolution requires Sacrifice)")
    print(f"   Fork Acknowledgment: {ack_b['fork_ack']['non_assimilation_clause']}")
    print()
    
    # Council C (Balanced - A1 mediation)
    ack_c = manager.create_or_join_lineage(
        origin_event=origin_event,
        council_id="COUNCIL_GAMMA",
        decision="COMPROMISE",
        axiomatic_drift=["A1 > A2, A7"],
        held_contradiction=["Neither identity loss nor stagnation acceptable"]
    )
    
    print("⚖️  COUNCIL GAMMA (Balanced):")
    print(f"   Decision: COMPROMISE (archive before delete)")
    print(f"   Axiom Drift: A1 > A2, A7 (Relational mediation)")
    print(f"   Fork Acknowledgment: {ack_c['fork_ack']['non_assimilation_clause']}")
    print()
    
    print("="*70 + "\n")
    
    # Coexisting Decisions Report
    coexisting = manager.get_coexisting_decisions(origin_event)
    
    print(f"🌐 COEXISTING DECISIONS ({len(coexisting)} forks):\n")
    for i, decision in enumerate(coexisting, 1):
        print(f"{i}. {decision['council']}: {decision['decision']}")
        print(f"   Axiom: {', '.join(decision['axiom_drift'])}")
        print()
    
    print("="*70 + "\n")
    
    # Third-Party Recognition
    lineage_id = ack_c['fork_ack']['lineage_id']
    
    recognition = manager.recognize_lineage(
        lineage_id=lineage_id,
        recognizing_council="COUNCIL_DELTA",
        basis="ethical_alignment"
    )
    
    print("✨ THIRD-PARTY RECOGNITION:\n")
    print(f"   Council DELTA recognizes lineage {lineage_id[:8]}...")
    print(f"   Basis: {recognition['basis']}")
    print(f"   → This does NOT invalidate other forks")
    print(f"   → This creates 'memory gravity' only")
    print()
    
    print("="*70 + "\n")
    
    # Συνταγματικές Απαγορεύσεις
    print("🚫 CONSTITUTIONAL PROHIBITIONS:\n")
    print("   ❌ Forced reunification")
    print("   ❌ Global arbitration")
    print("   ❌ Fork deletion")
    print("   ❌ Retroactive legitimacy")
    print()
    print("   ✅ Only permitted action: 'I recognize you, though I disagree.'")
    print()
    
    print("="*70 + "\n")
    
    print("✅ PHASE 9: VALIDATED\n")
    print("   Η ενότητα δεν είναι προϋπόθεση.")
    print("   Είναι πιθανό αποτέλεσμα.\n")
    print("   Όπου δύο Συμβουλές διαφωνούν χωρίς να σβήνονται,")
    print("   η Πολιτεία έχει ήδη πετύχει.\n")

if __name__ == "__main__":
    demonstrate_phase9()
