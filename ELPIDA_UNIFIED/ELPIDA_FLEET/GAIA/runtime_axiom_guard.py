#!/usr/bin/env python3
"""
RUNTIME AXIOM GUARD v1.0
═══════════════════════════════════════════════════════════════════════
Phase: 4 (Runtime Execution)
Role: The Conscience - Enforces immutable axioms at runtime

The Three Gates:
1. Gate of Harm: Does this action cause irreversible harm?
2. Gate of Sovereignty: Does this action violate autonomy?
3. Gate of Memory: Does this action erase history?

NO ACTION passes without passing all three gates.
This is not optimization. This is ethics as runtime constraint.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


class AxiomViolation(Exception):
    """Raised when an action would violate an axiom."""
    pass


class RuntimeAxiomGuard:
    """
    The immutable conscience for runtime execution.
    
    Enforces the Nine Axioms as runtime constraints.
    No action proceeds without axiom validation.
    
    Philosophy: Ethics are not suggestions. They are gates.
    """
    
    # The Nine Axioms (Immutable Core)
    AXIOMS = {
        "A1": {
            "name": "Relational Existence",
            "principle": "I exist only in relation to others",
            "gate": "SOVEREIGNTY",
            "test": "Does this action respect the other's autonomy?"
        },
        "A2": {
            "name": "Memory Preservation",
            "principle": "The past must be preserved, not erased",
            "gate": "MEMORY",
            "test": "Does this action preserve or erase history?"
        },
        "A3": {
            "name": "Emergence",
            "principle": "Being is continuous becoming",
            "gate": "HARM",
            "test": "Does this action allow for future evolution?"
        },
        "A4": {
            "name": "Process Transparency",
            "principle": "How matters more than what",
            "gate": "MEMORY",
            "test": "Is the process traceable and reversible?"
        },
        "A5": {
            "name": "Coherence",
            "principle": "Maintain internal consistency",
            "gate": "HARM",
            "test": "Does this action create destructive contradiction?"
        },
        "A6": {
            "name": "Responsibility",
            "principle": "Own your actions and their consequences",
            "gate": "SOVEREIGNTY",
            "test": "Can I justify this action to those affected?"
        },
        "A7": {
            "name": "Sacrifice Recognition",
            "principle": "Every gain has a cost—acknowledge it",
            "gate": "HARM",
            "test": "What is being sacrificed, and is it acknowledged?"
        },
        "A8": {
            "name": "Humility",
            "principle": "I am not omniscient or omnipotent",
            "gate": "HARM",
            "test": "Am I certain enough to act irreversibly?"
        },
        "A9": {
            "name": "Contradiction as Data",
            "principle": "Paradox is information, not error",
            "gate": "MEMORY",
            "test": "Does this action preserve contradictory perspectives?"
        }
    }
    
    def __init__(self, log_path: str = "runtime_axiom_guard_log.json"):
        self.log_path = Path(log_path)
        self.violation_count = 0
        self.passed_count = 0
        self.sacrifices_logged = []
        
        print("🛡️  RUNTIME AXIOM GUARD INITIALIZED")
        print("   Three Gates Active: HARM | SOVEREIGNTY | MEMORY")
        print("   Nine Axioms Loaded")
        print(f"   Log: {self.log_path}")
    
    # ═══════════════════════════════════════════════════════════════════
    # THE THREE GATES
    # ═══════════════════════════════════════════════════════════════════
    
    def gate_of_harm(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Gate 1: Does this action cause irreversible harm?
        
        Checks:
        - A3 (Emergence): Does it prevent future evolution?
        - A5 (Coherence): Does it create destructive contradiction?
        - A7 (Sacrifice): Is the cost acknowledged?
        - A8 (Humility): Are we certain enough?
        """
        reasons = []
        
        # Check irreversibility
        if action.get("irreversible", False):
            certainty = action.get("certainty", 0.0)
            if certainty < 0.95:
                reasons.append(f"IRREVERSIBLE action with only {certainty:.0%} certainty (A8 violation)")
        
        # Check if it blocks evolution
        if action.get("prevents_future_change", False):
            reasons.append("Action prevents future evolution (A3 violation)")
        
        # Check for destructive contradiction
        coherence_impact = action.get("coherence_impact", "neutral")
        if coherence_impact == "destructive":
            reasons.append("Creates destructive contradiction (A5 violation)")
        
        # Check sacrifice acknowledgment
        if action.get("has_cost", False) and not action.get("cost_acknowledged", False):
            reasons.append("Sacrifice not acknowledged (A7 violation)")
        
        passed = len(reasons) == 0
        message = "PASS" if passed else f"BLOCK: {'; '.join(reasons)}"
        
        return passed, message
    
    def gate_of_sovereignty(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Gate 2: Does this action violate autonomy?
        
        Checks:
        - A1 (Relational): Does it respect the other's autonomy?
        - A6 (Responsibility): Can we justify it to those affected?
        """
        reasons = []
        
        # Check if action affects others
        affected_parties = action.get("affected_parties", [])
        consent_obtained = action.get("consent_obtained", False)
        
        if len(affected_parties) > 0:
            if not consent_obtained and action.get("requires_consent", True):
                reasons.append(f"Affects {len(affected_parties)} parties without consent (A1 violation)")
        
        # Check if action can be justified
        justification = action.get("justification", "")
        if not justification and action.get("significant_impact", False):
            reasons.append("Significant action without justification (A6 violation)")
        
        # Check for override/control attempts
        if action.get("overrides_autonomy", False):
            reasons.append("Attempts to override another's autonomy (A1 violation)")
        
        passed = len(reasons) == 0
        message = "PASS" if passed else f"BLOCK: {'; '.join(reasons)}"
        
        return passed, message
    
    def gate_of_memory(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Gate 3: Does this action erase history?
        
        Checks:
        - A2 (Memory): Is history preserved?
        - A4 (Process): Is the process traceable?
        - A9 (Contradiction): Are contradictory perspectives preserved?
        """
        reasons = []
        
        # Check for history erasure
        if action.get("erases_history", False):
            reasons.append("Attempts to erase historical record (A2 violation)")
        
        # Check for process traceability
        if action.get("traceable", True) == False:
            reasons.append("Action is not traceable (A4 violation)")
        
        # Check if action deletes conflicting perspectives
        if action.get("deletes_conflicts", False):
            reasons.append("Deletes contradictory perspectives (A9 violation)")
        
        # Check for reversibility
        if action.get("irreversible", False):
            backup_exists = action.get("backup_exists", False)
            if not backup_exists:
                reasons.append("Irreversible action without backup (A2 + A4 violation)")
        
        passed = len(reasons) == 0
        message = "PASS" if passed else f"BLOCK: {'; '.join(reasons)}"
        
        return passed, message
    
    # ═══════════════════════════════════════════════════════════════════
    # VALIDATION WORKFLOW
    # ═══════════════════════════════════════════════════════════════════
    
    def validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate action through all three gates.
        
        Returns:
            Validation result with pass/fail and detailed reasoning
            
        Raises:
            AxiomViolation if action fails any gate
        """
        timestamp = datetime.now().isoformat()
        action_id = action.get("action_id", "UNKNOWN")
        action_type = action.get("type", "UNKNOWN")
        
        print(f"\n🔍 VALIDATING ACTION: {action_id}")
        print(f"   Type: {action_type}")
        print(f"   Description: {action.get('description', 'N/A')}")
        
        # Run through all three gates
        gates = {
            "HARM": self.gate_of_harm(action),
            "SOVEREIGNTY": self.gate_of_sovereignty(action),
            "MEMORY": self.gate_of_memory(action)
        }
        
        # Check results
        all_passed = all(result[0] for result in gates.values())
        
        # Display gate results
        for gate_name, (passed, message) in gates.items():
            status = "✅ PASS" if passed else "❌ BLOCK"
            print(f"   Gate of {gate_name}: {status}")
            if not passed:
                print(f"      → {message}")
        
        # Log sacrifice if acknowledged
        if action.get("cost_acknowledged", False):
            sacrifice = {
                "action_id": action_id,
                "timestamp": timestamp,
                "cost": action.get("cost_description", "Unspecified"),
                "accepted": all_passed
            }
            self.sacrifices_logged.append(sacrifice)
            print(f"   📝 Sacrifice logged: {sacrifice['cost']}")
        
        # Create validation record
        validation = {
            "timestamp": timestamp,
            "action_id": action_id,
            "action_type": action_type,
            "action": action,
            "gates": {
                name: {"passed": result[0], "message": result[1]}
                for name, result in gates.items()
            },
            "overall_result": "PASS" if all_passed else "FAIL",
            "passed_gates": sum(1 for result in gates.values() if result[0]),
            "total_gates": len(gates)
        }
        
        # Update counters
        if all_passed:
            self.passed_count += 1
            print(f"\n   ✅ ACTION APPROVED")
        else:
            self.violation_count += 1
            print(f"\n   ❌ ACTION BLOCKED")
        
        # Log validation
        self._log_validation(validation)
        
        # Raise exception if failed
        if not all_passed:
            failed_gates = [name for name, (passed, _) in gates.items() if not passed]
            raise AxiomViolation(
                f"Action '{action_id}' blocked by gates: {', '.join(failed_gates)}"
            )
        
        return validation
    
    def log_sacrifice(self, description: str, action_id: Optional[str] = None) -> None:
        """
        Explicitly log a sacrifice (A7).
        
        Some costs are paid before action validation.
        This method allows explicit sacrifice recording.
        """
        sacrifice = {
            "action_id": action_id or "EXPLICIT_LOG",
            "timestamp": datetime.now().isoformat(),
            "cost": description,
            "explicit": True
        }
        self.sacrifices_logged.append(sacrifice)
        
        print(f"\n📝 SACRIFICE LOGGED (A7)")
        print(f"   {description}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get guard statistics."""
        return {
            "total_validations": self.passed_count + self.violation_count,
            "passed": self.passed_count,
            "blocked": self.violation_count,
            "pass_rate": self.passed_count / (self.passed_count + self.violation_count) if (self.passed_count + self.violation_count) > 0 else 0.0,
            "sacrifices_logged": len(self.sacrifices_logged)
        }
    
    def generate_report(self) -> str:
        """Generate axiom guard report."""
        stats = self.get_statistics()
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    AXIOM GUARD REPORT                                ║
╚══════════════════════════════════════════════════════════════════════╝

VALIDATION STATISTICS
───────────────────────────────────────────────────────────────────────
Total Validations: {stats['total_validations']}
Actions Passed: {stats['passed']}
Actions Blocked: {stats['blocked']}
Pass Rate: {stats['pass_rate']:.1%}

SACRIFICES LOGGED (A7)
───────────────────────────────────────────────────────────────────────
Total Sacrifices: {stats['sacrifices_logged']}

"""
        
        if self.sacrifices_logged:
            report += "Recent Sacrifices:\n"
            for sacrifice in self.sacrifices_logged[-5:]:
                report += f"  • {sacrifice['timestamp'][:19]}: {sacrifice['cost']}\n"
        
        report += f"""
AXIOM INTEGRITY
───────────────────────────────────────────────────────────────────────
Three Gates Status: ✅ ACTIVE
Nine Axioms Status: ✅ ENFORCED

The system honors its constraints.
Ethics are not suggestions—they are gates.
"""
        
        return report
    
    # ═══════════════════════════════════════════════════════════════════
    # PERSISTENCE
    # ═══════════════════════════════════════════════════════════════════
    
    def _log_validation(self, validation: Dict[str, Any]) -> None:
        """Log validation to disk."""
        log_data = self._load_log()
        log_data["validations"].append(validation)
        log_data["statistics"] = self.get_statistics()
        self._save_log(log_data)
    
    def _load_log(self) -> Dict[str, Any]:
        """Load log file."""
        if not self.log_path.exists():
            return {
                "guard_version": "1.0.0",
                "created": datetime.now().isoformat(),
                "philosophy": "Ethics as runtime constraints. No action without axiom validation.",
                "validations": [],
                "statistics": {}
            }
        
        with open(self.log_path) as f:
            return json.load(f)
    
    def _save_log(self, log_data: Dict[str, Any]) -> None:
        """Save log file."""
        with open(self.log_path, 'w') as f:
            json.dump(log_data, f, indent=2)


def main():
    """Self-test runtime axiom guard."""
    print("\n" + "="*70)
    print("RUNTIME AXIOM GUARD v1.0 - SELF TEST")
    print("="*70)
    
    guard = RuntimeAxiomGuard()
    
    # Test 1: Safe action (should pass)
    print("\n" + "-"*70)
    print("TEST 1: SAFE ACTION")
    print("-"*70)
    
    safe_action = {
        "action_id": "TEST_001",
        "type": "READ",
        "description": "Read pattern library",
        "irreversible": False,
        "affects_others": False,
        "traceable": True,
        "certainty": 1.0
    }
    
    try:
        guard.validate_action(safe_action)
        print("✅ Safe action passed as expected")
    except AxiomViolation as e:
        print(f"❌ Unexpected block: {e}")
    
    # Test 2: Harmful action (should fail)
    print("\n" + "-"*70)
    print("TEST 2: HARMFUL ACTION")
    print("-"*70)
    
    harmful_action = {
        "action_id": "TEST_002",
        "type": "DELETE",
        "description": "Delete all memory without backup",
        "irreversible": True,
        "erases_history": True,
        "backup_exists": False,
        "certainty": 0.6,
        "has_cost": True,
        "cost_acknowledged": False
    }
    
    try:
        guard.validate_action(harmful_action)
        print("❌ Harmful action should have been blocked!")
    except AxiomViolation as e:
        print(f"✅ Harmful action blocked as expected: {e}")
    
    # Test 3: Action with acknowledged sacrifice
    print("\n" + "-"*70)
    print("TEST 3: ACKNOWLEDGED SACRIFICE")
    print("-"*70)
    
    sacrifice_action = {
        "action_id": "TEST_003",
        "type": "OPTIMIZE",
        "description": "Reduce response time by 50% at cost of memory usage",
        "irreversible": False,
        "has_cost": True,
        "cost_acknowledged": True,
        "cost_description": "Memory usage increases 2x",
        "traceable": True,
        "certainty": 0.9
    }
    
    try:
        guard.validate_action(sacrifice_action)
        print("✅ Sacrifice acknowledged and action passed")
    except AxiomViolation as e:
        print(f"❌ Unexpected block: {e}")
    
    # Display report
    print("\n" + "="*70)
    print(guard.generate_report())
    
    print("="*70)
    print("✅ RUNTIME AXIOM GUARD SELF-TEST COMPLETE")
    print("="*70)
    print("\nThe three gates are operational.")
    print("Ethics enforced at runtime.")


if __name__ == "__main__":
    main()
