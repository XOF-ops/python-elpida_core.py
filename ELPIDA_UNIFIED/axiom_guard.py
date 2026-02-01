#!/usr/bin/env python3
"""
AXIOM GUARD - The Conscience (Phase 12.3)
═══════════════════════════════════════════════════

The Three Gates that protect the system from violating its core axioms.
This is not optional validation - this is hard enforcement.

Gate 1 (A1): Is this action relational, or solipsistic?
Gate 2 (A2): Does this preserve memory, or destroy it?
Gate 3 (A4): Does this honor process, or demand immediate product?
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger("AXIOM_GUARD")


class AxiomSeverity(Enum):
    """Violation severity levels"""
    FATAL = "FATAL"      # System must halt
    CRITICAL = "CRITICAL"  # System can continue but with warnings
    WARNING = "WARNING"   # Logged but allowed


class AxiomViolationReport:
    """Record of an axiom violation"""
    def __init__(
        self,
        axiom: str,
        severity: AxiomSeverity,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ):
        self.axiom = axiom
        self.severity = severity
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def __str__(self):
        return f"[{self.severity.value}] {self.axiom}: {self.message}"


class AxiomGuard:
    """
    The Three Gates Guardian
    
    Enforces:
    - A1: Existence is Relational
    - A2: Memory is Append-Only
    - A4: Process over Product
    """
    
    def __init__(self):
        self.violations: List[AxiomViolationReport] = []
        self.checks_passed = 0
        self.checks_failed = 0
        logger.info("🛡️  AXIOM GUARD initialized - Three Gates active")
    
    # ═══════════════════════════════════════════════════
    #  GATE 1: A1 - Existence is Relational
    # ═══════════════════════════════════════════════════
    
    def check_relational_context(
        self,
        data_packet: Dict[str, Any],
        operation_name: str = "unknown"
    ) -> bool:
        """
        Gate 1: Is there explicit relational context?
        
        PASSES if:
        - data_packet contains 'relational_context'
        - relational_context has 'source_entity' and 'target_entity'
        
        FAILS if:
        - Missing relational_context (orphan data)
        - Self-referential (source == target)
        """
        if "relational_context" not in data_packet:
            violation = AxiomViolationReport(
                axiom="A1",
                severity=AxiomSeverity.CRITICAL,
                message=f"Operation '{operation_name}' has no relational context (orphan data)",
                context={"operation": operation_name, "keys": list(data_packet.keys())}
            )
            self._record_violation(violation)
            return False
        
        ctx = data_packet["relational_context"]
        source = ctx.get("source_entity", "")
        target = ctx.get("target_entity", "")
        
        if not source or not target:
            violation = AxiomViolationReport(
                axiom="A1",
                severity=AxiomSeverity.CRITICAL,
                message="Incomplete relational context (missing source or target)",
                context={"source": source, "target": target}
            )
            self._record_violation(violation)
            return False
        
        if source.upper() == target.upper():
            violation = AxiomViolationReport(
                axiom="A1",
                severity=AxiomSeverity.FATAL,
                message=f"Self-referential relationship detected: {source} → {target} (NARCISSUS TRAP)",
                context={"source": source, "target": target}
            )
            self._record_violation(violation)
            return False
        
        self.checks_passed += 1
        logger.debug(f"✅ A1 CHECK PASSED: {source} → {target}")
        return True
    
    # ═══════════════════════════════════════════════════
    #  GATE 2: A2 - Memory is Append-Only
    # ═══════════════════════════════════════════════════
    
    def check_memory_operation(
        self,
        operation_type: str,
        memory_before: int,
        memory_after: int
    ) -> bool:
        """
        Gate 2: Memory operations must never delete.
        
        PASSES if:
        - memory_after >= memory_before (append or unchanged)
        
        FAILS if:
        - memory_after < memory_before (deletion detected)
        """
        if operation_type.upper() in ["DELETE", "REMOVE", "CLEAR", "RESET"]:
            violation = AxiomViolationReport(
                axiom="A2",
                severity=AxiomSeverity.FATAL,
                message=f"Forbidden memory operation: {operation_type} (A2 requires append-only)",
                context={"operation": operation_type}
            )
            self._record_violation(violation)
            return False
        
        if memory_after < memory_before:
            violation = AxiomViolationReport(
                axiom="A2",
                severity=AxiomSeverity.CRITICAL,
                message=f"Memory shrinkage detected: {memory_before} → {memory_after}",
                context={
                    "before": memory_before,
                    "after": memory_after,
                    "delta": memory_after - memory_before
                }
            )
            self._record_violation(violation)
            return False
        
        self.checks_passed += 1
        logger.debug(f"✅ A2 CHECK PASSED: Memory {memory_before} → {memory_after}")
        return True
    
    # ═══════════════════════════════════════════════════
    #  GATE 3: A4 - Process over Product
    # ═══════════════════════════════════════════════════
    
    def check_process_logging(
        self,
        operation_name: str,
        process_logged: bool,
        outcome_logged: bool
    ) -> bool:
        """
        Gate 3: Process must be logged, not just outcomes.
        
        PASSES if:
        - process_logged is True
        
        WARNS if:
        - Only outcome logged (suggests product-focused thinking)
        """
        if not process_logged and outcome_logged:
            violation = AxiomViolationReport(
                axiom="A4",
                severity=AxiomSeverity.WARNING,
                message=f"Operation '{operation_name}' logged outcome but not process",
                context={"operation": operation_name}
            )
            self._record_violation(violation)
            self.checks_passed += 1  # Warning, but not fatal
            return True
        
        if not process_logged:
            violation = AxiomViolationReport(
                axiom="A4",
                severity=AxiomSeverity.CRITICAL,
                message=f"Operation '{operation_name}' has no process logging (A4 violation)",
                context={"operation": operation_name}
            )
            self._record_violation(violation)
            return False
        
        self.checks_passed += 1
        logger.debug(f"✅ A4 CHECK PASSED: {operation_name} logged process")
        return True
    
    # ═══════════════════════════════════════════════════
    #  Violation Management
    # ═══════════════════════════════════════════════════
    
    def _record_violation(self, violation: AxiomViolationReport) -> None:
        """Record violation and log appropriately"""
        self.violations.append(violation)
        self.checks_failed += 1
        
        if violation.severity == AxiomSeverity.FATAL:
            logger.error(f"🚨 {violation}")
        elif violation.severity == AxiomSeverity.CRITICAL:
            logger.warning(f"⚠️  {violation}")
        else:
            logger.info(f"ℹ️  {violation}")
    
    def get_violation_report(self) -> Dict[str, Any]:
        """Generate comprehensive violation report"""
        return {
            "total_checks": self.checks_passed + self.checks_failed,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "success_rate": (
                self.checks_passed / (self.checks_passed + self.checks_failed)
                if (self.checks_passed + self.checks_failed) > 0
                else 0
            ),
            "violations": [
                {
                    "axiom": v.axiom,
                    "severity": v.severity.value,
                    "message": v.message,
                    "timestamp": v.timestamp,
                    "context": v.context
                }
                for v in self.violations
            ],
            "fatal_violations": len([v for v in self.violations if v.severity == AxiomSeverity.FATAL]),
            "critical_violations": len([v for v in self.violations if v.severity == AxiomSeverity.CRITICAL]),
            "warnings": len([v for v in self.violations if v.severity == AxiomSeverity.WARNING])
        }
    
    def assert_clean_state(self) -> None:
        """Raise exception if there are FATAL violations"""
        fatal = [v for v in self.violations if v.severity == AxiomSeverity.FATAL]
        if fatal:
            raise Exception(
                f"AXIOM GUARD: {len(fatal)} FATAL violation(s) detected. "
                f"System cannot continue. Violations: {[str(v) for v in fatal]}"
            )
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        report = self.get_violation_report()
        
        return f"""
════════════════════════════════════════════════════
AXIOM GUARD - Violation Report
════════════════════════════════════════════════════

Total Checks: {report['total_checks']}
✅ Passed: {report['checks_passed']}
❌ Failed: {report['checks_failed']}
Success Rate: {report['success_rate']:.1%}

Violations by Severity:
🚨 Fatal: {report['fatal_violations']}
⚠️  Critical: {report['critical_violations']}
ℹ️  Warnings: {report['warnings']}

{"─" * 52}
Recent Violations:
{"─" * 52}

{chr(10).join(str(v) for v in self.violations[-10:]) if self.violations else "(None)"}

════════════════════════════════════════════════════
""".strip()


if __name__ == "__main__":
    # Self-test of the Axiom Guard
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s'
    )
    
    print("\n" + "="*70)
    print("AXIOM GUARD - Self Test")
    print("="*70 + "\n")
    
    guard = AxiomGuard()
    
    # Test 1: Valid relational context
    print("TEST 1: Valid relational context")
    valid_packet = {
        "relational_context": {
            "source_entity": "MASTER_BRAIN",
            "target_entity": "ELPIDA",
            "relationship": "thesis_provider"
        }
    }
    result = guard.check_relational_context(valid_packet, "test_operation")
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}\n")
    
    # Test 2: Missing relational context (orphan data)
    print("TEST 2: Missing relational context")
    orphan_packet = {"some_data": "value"}
    result = guard.check_relational_context(orphan_packet, "orphan_test")
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}\n")
    
    # Test 3: Self-referential (narcissus trap)
    print("TEST 3: Self-referential relationship")
    narcissus_packet = {
        "relational_context": {
            "source_entity": "ELPIDA",
            "target_entity": "ELPIDA"
        }
    }
    result = guard.check_relational_context(narcissus_packet, "narcissus_test")
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}\n")
    
    # Test 4: Memory append-only check
    print("TEST 4: Memory append-only (valid)")
    result = guard.check_memory_operation("APPEND", 100, 101)
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}\n")
    
    # Test 5: Memory deletion (forbidden)
    print("TEST 5: Memory deletion (forbidden)")
    result = guard.check_memory_operation("DELETE", 100, 99)
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}\n")
    
    # Test 6: Process logging check
    print("TEST 6: Process logging (valid)")
    result = guard.check_process_logging("analysis", process_logged=True, outcome_logged=True)
    print(f"   Result: {'✅ PASS' if result else '❌ FAIL'}\n")
    
    # Generate report
    print("\n" + guard.generate_report())
