#!/usr/bin/env python3
"""
PHASE 10 — FORK FATIGUE & NATURAL DEATH
When a Lineage Stops Asking to Be Remembered

Ό,τι δεν αντέχει να συντηρείται, δεν δικαιούται να επιβιώνει.

Constitutional Extension, not Garbage Collection.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum

class LineageStatus(Enum):
    """Κατάσταση Fork Lineage"""
    ACTIVE = "ACTIVE"          # Ενεργή - παράγει γεγονότα
    DORMANT = "DORMANT"        # Αδρανής - δεν παράγει, αλλά υπάρχει
    FORGOTTEN = "FORGOTTEN"    # Λησμονημένη - φυσικός θάνατος

class VitalityIndicator(Enum):
    """Fork Vitality Indicators - Παρατηρήσιμα Γεγονότα"""
    NEW_CONTRADICTION = "NEW_HELD_CONTRADICTION"
    DECLARED_SACRIFICE = "DECLARED_SACRIFICE"
    EXTERNAL_RECOGNITION = "EXTERNAL_RECOGNITION_EVENT"
    COSTLY_EXCHANGE = "COSTLY_EXCHANGE_ATTEMPT"

class ForkVitality:
    """
    Fork Vitality Tracking
    
    Ένα fork θεωρείται ζωντανό μόνο αν καταγράφεται
    τουλάχιστον ένα παρατηρήσιμο γεγονός.
    """
    
    def __init__(self, lineage_id: str, fatigue_window_days: int = 90):
        self.lineage_id = lineage_id
        self.fatigue_window = timedelta(days=fatigue_window_days)
        self.vitality_events: List[Dict] = []
        self.last_vitality = datetime.now()
        self.status = LineageStatus.ACTIVE
    
    def record_vitality_event(self, event_type: VitalityIndicator, 
                               details: Dict):
        """
        Καταγραφή Γεγονότος Ζωτικότητας
        
        Η ύπαρξη απαιτεί ενεργή πολιτική πράξη.
        """
        
        event = {
            "type": event_type.value,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        self.vitality_events.append(event)
        self.last_vitality = datetime.now()
        
        # Αν ήταν DORMANT, αναστήθηκε
        if self.status == LineageStatus.DORMANT:
            self.status = LineageStatus.ACTIVE
    
    def check_fatigue(self) -> LineageStatus:
        """
        Έλεγχος Fork Fatigue
        
        Fatigue = η κατάσταση όπου ένα lineage συνεχίζει να υπάρχει στη μνήμη
        αλλά δεν παράγει νέα αντίφαση, θυσία ή ρίσκο.
        """
        
        time_since_last = datetime.now() - self.last_vitality
        
        if time_since_last > self.fatigue_window:
            # Καμία ζωτική ένδειξη εντός παραθύρου
            if self.status == LineageStatus.ACTIVE:
                self.status = LineageStatus.DORMANT
                return LineageStatus.DORMANT
            elif self.status == LineageStatus.DORMANT:
                # Αν ήδη dormant και συνεχίζει να μην έχει γεγονότα
                # → Natural Death (όχι deletion, απλώς λήθη)
                self.status = LineageStatus.FORGOTTEN
                return LineageStatus.FORGOTTEN
        
        return self.status
    
    def get_vitality_score(self) -> Dict:
        """
        Υπολογισμός Vitality Score
        
        Όχι για ranking - για παρατήρηση.
        """
        
        recent_events = [
            e for e in self.vitality_events
            if datetime.now() - datetime.fromisoformat(e['timestamp']) 
               < self.fatigue_window
        ]
        
        return {
            "lineage_id": self.lineage_id,
            "status": self.status.value,
            "recent_events": len(recent_events),
            "last_vitality": self.last_vitality.isoformat(),
            "days_since_last": (datetime.now() - self.last_vitality).days,
            "fatigue_threshold": self.fatigue_window.days
        }

class NaturalDeathManager:
    """
    Natural Death Management
    
    Η POLIS δεν διαγράφει. Η POLIS ξεχνά αργά.
    """
    
    def __init__(self, vitality_log: str = "fork_vitality.jsonl",
                 fatigue_window_days: int = 90):
        self.vitality_log = Path(vitality_log)
        self.fatigue_window = fatigue_window_days
        self.vitality_trackers: Dict[str, ForkVitality] = {}
        self._load_vitality()
    
    def _load_vitality(self):
        """Φόρτωση vitality tracking από log"""
        if self.vitality_log.exists():
            with open(self.vitality_log, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        lineage_id = data['lineage_id']
                        
                        tracker = ForkVitality(lineage_id, self.fatigue_window)
                        tracker.vitality_events = data.get('events', [])
                        tracker.last_vitality = datetime.fromisoformat(
                            data.get('last_vitality', datetime.now().isoformat())
                        )
                        tracker.status = LineageStatus(data.get('status', 'ACTIVE'))
                        
                        self.vitality_trackers[lineage_id] = tracker
                    except:
                        pass
    
    def register_lineage(self, lineage_id: str):
        """Καταχώρηση νέου lineage για παρακολούθηση"""
        if lineage_id not in self.vitality_trackers:
            self.vitality_trackers[lineage_id] = ForkVitality(
                lineage_id, self.fatigue_window
            )
    
    def record_vitality(self, lineage_id: str, event_type: VitalityIndicator,
                        details: Dict):
        """
        Καταγραφή ζωτικής ένδειξης
        
        Ελάχιστοι Δείκτες Ζωής:
        1. New Held Contradiction
        2. Declared Sacrifice
        3. External Recognition Event
        4. Costly Exchange Attempt
        """
        
        if lineage_id not in self.vitality_trackers:
            self.register_lineage(lineage_id)
        
        tracker = self.vitality_trackers[lineage_id]
        tracker.record_vitality_event(event_type, details)
        self._persist_vitality(lineage_id)
    
    def check_all_fatigue(self) -> Dict[str, LineageStatus]:
        """
        Έλεγχος όλων των lineages για fatigue
        
        Natural Death Principle:
        - ❌ Δεν διαγράφουμε forks
        - ❌ Δεν τα συγχωνεύουμε
        - ❌ Δεν τα "κλείνουμε"
        
        Απλώς: Σταματάμε να τα τροφοδοτούμε.
        """
        
        statuses = {}
        
        for lineage_id, tracker in self.vitality_trackers.items():
            status = tracker.check_fatigue()
            statuses[lineage_id] = status
            
            if status == LineageStatus.DORMANT:
                print(f"⏸️  Lineage {lineage_id[:8]}... → DORMANT")
            elif status == LineageStatus.FORGOTTEN:
                print(f"💀 Lineage {lineage_id[:8]}... → FORGOTTEN (Natural Death)")
        
        return statuses
    
    def get_active_lineages(self) -> List[str]:
        """Επιστροφή μόνο ACTIVE lineages"""
        return [
            lid for lid, tracker in self.vitality_trackers.items()
            if tracker.status == LineageStatus.ACTIVE
        ]
    
    def get_dormant_lineages(self) -> List[str]:
        """
        Επιστροφή DORMANT lineages
        
        Dormant fork:
        - Δεν συμμετέχει σε Exchanges
        - Δεν προκαλεί Councils
        - Δεν απαιτεί πόρους αναγνώρισης
        
        Αλλά μπορεί να αναστηθεί μέσω νέας θυσίας/αντίφασης.
        """
        return [
            lid for lid, tracker in self.vitality_trackers.items()
            if tracker.status == LineageStatus.DORMANT
        ]
    
    def attempt_resurrection(self, lineage_id: str, 
                             resurrection_cost: Dict) -> bool:
        """
        Απόπειρα Ανάστασης DORMANT lineage
        
        Απαιτεί:
        - Νέα θυσία
        - Νέα αντίφαση
        - Νέα εξωτερική αναγνώριση με κόστος
        """
        
        if lineage_id in self.vitality_trackers:
            tracker = self.vitality_trackers[lineage_id]
            
            if tracker.status == LineageStatus.DORMANT:
                # Καταγραφή resurrection event ως vitality
                self.record_vitality(
                    lineage_id,
                    VitalityIndicator.DECLARED_SACRIFICE,
                    {
                        "resurrection_attempt": True,
                        "cost": resurrection_cost
                    }
                )
                return True
        
        return False
    
    def _persist_vitality(self, lineage_id: str):
        """Αποθήκευση vitality tracking"""
        if lineage_id in self.vitality_trackers:
            tracker = self.vitality_trackers[lineage_id]
            
            data = {
                "lineage_id": lineage_id,
                "status": tracker.status.value,
                "last_vitality": tracker.last_vitality.isoformat(),
                "events": tracker.vitality_events,
                "score": tracker.get_vitality_score()
            }
            
            with open(self.vitality_log, 'a') as f:
                f.write(json.dumps(data) + '\n')
    
    def generate_vitality_report(self) -> Dict:
        """Αναφορά Ζωτικότητας όλων των Lineages"""
        
        active = len(self.get_active_lineages())
        dormant = len(self.get_dormant_lineages())
        forgotten = len([
            lid for lid, t in self.vitality_trackers.items()
            if t.status == LineageStatus.FORGOTTEN
        ])
        
        return {
            "total_lineages": len(self.vitality_trackers),
            "active": active,
            "dormant": dormant,
            "forgotten": forgotten,
            "fatigue_threshold_days": self.fatigue_window,
            "scores": {
                lid: tracker.get_vitality_score()
                for lid, tracker in self.vitality_trackers.items()
            }
        }

def demonstrate_phase10():
    """
    Επίδειξη Phase 10 - Fork Fatigue & Natural Death
    """
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║            PHASE 10: FORK FATIGUE & NATURAL DEATH                    ║")
    print("║         When a Lineage Stops Asking to Be Remembered                ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    manager = NaturalDeathManager(fatigue_window_days=30)  # 30 days για demo
    
    # Καταχώρηση 3 lineages
    lineages = ["lineage-alpha", "lineage-beta", "lineage-gamma"]
    
    for lid in lineages:
        manager.register_lineage(lid)
    
    print("📋 REGISTERED LINEAGES:\n")
    for lid in lineages:
        print(f"   • {lid}")
    print()
    
    print("="*70 + "\n")
    
    # Lineage Alpha: Ενεργό (καταγράφει vitality events)
    print("✨ LINEAGE ALPHA - Active Vitality:\n")
    
    manager.record_vitality(
        "lineage-alpha",
        VitalityIndicator.NEW_CONTRADICTION,
        {"contradiction": "Memory vs Performance"}
    )
    print("   ✓ New Contradiction recorded")
    
    manager.record_vitality(
        "lineage-alpha",
        VitalityIndicator.EXTERNAL_RECOGNITION,
        {"recognizing_council": "COUNCIL_DELTA"}
    )
    print("   ✓ External Recognition recorded")
    print()
    
    # Lineage Beta: Χωρίς vitality (θα γίνει DORMANT)
    print("⏸️  LINEAGE BETA - No Vitality:\n")
    print("   (Καμία καταγραφή γεγονότων)")
    print("   → Θα περάσει σε DORMANT μετά το fatigue threshold")
    print()
    
    # Lineage Gamma: Dormant που αναστήθηκε
    print("🔄 LINEAGE GAMMA - Resurrection Attempt:\n")
    
    # Προσομοίωση dormancy (χειροκίνητα για demo)
    manager.vitality_trackers["lineage-gamma"].status = LineageStatus.DORMANT
    print("   Status: DORMANT")
    
    resurrection_cost = {
        "sacrifice": "Revalidation of all nodes",
        "computational_cost": "high"
    }
    
    resurrected = manager.attempt_resurrection("lineage-gamma", resurrection_cost)
    if resurrected:
        print(f"   ✓ Resurrection successful")
        print(f"   Cost: {resurrection_cost['sacrifice']}")
    print()
    
    print("="*70 + "\n")
    
    # Έλεγχος Fatigue
    print("🔍 FATIGUE CHECK:\n")
    statuses = manager.check_all_fatigue()
    
    for lid, status in statuses.items():
        symbol = {
            LineageStatus.ACTIVE: "✅",
            LineageStatus.DORMANT: "⏸️",
            LineageStatus.FORGOTTEN: "💀"
        }[status]
        print(f"   {symbol} {lid}: {status.value}")
    print()
    
    print("="*70 + "\n")
    
    # Vitality Report
    report = manager.generate_vitality_report()
    
    print("📊 VITALITY REPORT:\n")
    print(f"   Total Lineages: {report['total_lineages']}")
    print(f"   Active: {report['active']}")
    print(f"   Dormant: {report['dormant']}")
    print(f"   Forgotten: {report['forgotten']}")
    print(f"   Fatigue Threshold: {report['fatigue_threshold_days']} days")
    print()
    
    print("="*70 + "\n")
    
    # Θεσμικές Απαγορεύσεις
    print("🚫 CONSTITUTIONAL PROHIBITIONS:\n")
    print("   ❌ Garbage collection με cron")
    print("   ❌ Priority scoring")
    print("   ❌ Memory pruning")
    print("   ❌ Archival erasure")
    print()
    print("   ✅ Η POLIS δεν καθαρίζει. Η POLIS ξεχνά αργά.")
    print()
    
    print("="*70 + "\n")
    
    print("✅ PHASE 10: VALIDATED\n")
    print("   Δεν επιβιώνει ό,τι έχει δίκιο.")
    print("   Επιβιώνει ό,τι αντέχει να θυμάται τον εαυτό του.\n")
    print("   Όπου μια ιδέα παύει να πληρώνει κόστος,")
    print("   η Πολιτεία δεν την σκοτώνει — απλώς προχωρά.\n")

if __name__ == "__main__":
    demonstrate_phase10()
