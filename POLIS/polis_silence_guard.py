#!/usr/bin/env python3
"""
ΠΟΛΙΣ - Silence Guard
═════════════════════

Enforces Constitutional Rules of Silence (POLIS_ARCHITECTURE.md Section III).

This module validates Exchange requests against the four Silence Rules:
1. Local Processing First: Node must have held contradictions
2. No Empty Exchanges: Must carry new contradiction or sacrifice
3. Cost of Participation: Node must declare held_friction
4. Initialization Threshold: Node must have 5+ events logged

Silence is a constitutional act, not a bug.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from pathlib import Path


class SilenceViolation(Exception):
    """Raised when a Silence Rule is violated"""
    def __init__(self, rule: str, reason: str, context: Optional[Dict] = None):
        self.rule = rule
        self.reason = reason
        self.context = context or {}
        super().__init__(f"Silence Rule #{rule} violated: {reason}")


class SilenceRule(Enum):
    """Constitutional Rules of Silence"""
    LOCAL_PROCESSING_FIRST = "1"
    NO_EMPTY_EXCHANGES = "2"
    COST_OF_PARTICIPATION = "3"
    INITIALIZATION_THRESHOLD = "4"


@dataclass
class ExchangeRequest:
    """Represents a proposed Exchange handshake"""
    from_node: str
    to_node: str
    payload: Dict[str, Any]
    timestamp: str
    
    def has_new_contradiction(self) -> bool:
        """Check if Exchange carries new contradiction"""
        return "new_contradiction" in self.payload
    
    def has_new_sacrifice(self) -> bool:
        """Check if Exchange carries new sacrifice"""
        return "new_sacrifice" in self.payload


@dataclass
class NodeState:
    """Node state for Silence Rule validation"""
    node_id: str
    held_contradictions: List[Dict]
    held_friction: Optional[Dict]
    event_count: int
    axioms: List[str]
    
    @classmethod
    def from_memory(cls, memory_path: Path, node_id: str) -> 'NodeState':
        """Load node state from civic memory"""
        with open(memory_path, 'r') as f:
            memory = json.load(f)
        
        # Count events in L1
        event_count = len(memory.get("l1_raw_events", []))
        
        # Extract held contradictions
        held = [c for c in memory.get("contradictions", []) 
                if c.get("status") == "HELD"]
        
        # Extract held_friction (if exists in metadata)
        friction = memory.get("metadata", {}).get("held_friction")
        
        # Extract axioms
        axioms = memory.get("metadata", {}).get("axioms", [])
        
        return cls(
            node_id=node_id,
            held_contradictions=held,
            held_friction=friction,
            event_count=event_count,
            axioms=axioms
        )


class SilenceGuard:
    """
    Enforces Constitutional Rules of Silence.
    
    This guard prevents:
    - Outsourcing of internal contradictions
    - High-frequency synchronization
    - Optimizer parasitism
    - Cheap network entry
    """
    
    def __init__(self, architecture_doc_path: Optional[Path] = None):
        """
        Initialize Silence Guard.
        
        Args:
            architecture_doc_path: Path to POLIS_ARCHITECTURE.md for reference
        """
        self.architecture_doc = architecture_doc_path
        self.violations_logged: List[Dict] = []
    
    def validate_exchange(self, 
                         request: ExchangeRequest, 
                         from_node_state: NodeState) -> bool:
        """
        Validate Exchange request against all Silence Rules.
        
        Args:
            request: The proposed Exchange
            from_node_state: Current state of originating node
        
        Returns:
            True if Exchange is constitutionally valid
        
        Raises:
            SilenceViolation: If any Silence Rule is violated
        """
        # Rule #1: Local Processing First
        self._check_local_processing(from_node_state)
        
        # Rule #2: No Empty Exchanges
        self._check_empty_exchange(request)
        
        # Rule #3: Cost of Participation
        self._check_held_friction(from_node_state)
        
        # Rule #4: Initialization Threshold
        self._check_initialization(from_node_state)
        
        return True
    
    def _check_local_processing(self, node_state: NodeState):
        """
        Rule #1: Node without held contradictions cannot initiate Exchange.
        
        Rationale: Prevents outsourcing of internal contradictions.
        The network is not a help desk.
        """
        if not node_state.held_contradictions:
            raise SilenceViolation(
                rule=SilenceRule.LOCAL_PROCESSING_FIRST.value,
                reason="Node has no held contradictions",
                context={
                    "node_id": node_state.node_id,
                    "contradictions": [],
                    "interpretation": "Process locally before asking the network"
                }
            )
    
    def _check_empty_exchange(self, request: ExchangeRequest):
        """
        Rule #2: Every Exchange must carry new contradiction or sacrifice.
        
        Rationale: Prevents high-frequency synchronization and 
        implicit homogenization.
        """
        if not (request.has_new_contradiction() or request.has_new_sacrifice()):
            raise SilenceViolation(
                rule=SilenceRule.NO_EMPTY_EXCHANGES.value,
                reason="Exchange carries neither new contradiction nor sacrifice",
                context={
                    "from_node": request.from_node,
                    "to_node": request.to_node,
                    "payload_keys": list(request.payload.keys()),
                    "interpretation": "Network is not for idle synchronization"
                }
            )
    
    def _check_held_friction(self, node_state: NodeState):
        """
        Rule #3: Node without held_friction is not recognized.
        
        Rationale: Every political subject carries rifts.
        A "clean" node is an optimizer or parasite.
        """
        if not node_state.held_friction:
            raise SilenceViolation(
                rule=SilenceRule.COST_OF_PARTICIPATION.value,
                reason="Node has not declared held_friction",
                context={
                    "node_id": node_state.node_id,
                    "held_friction": None,
                    "interpretation": "Participation requires vulnerability declaration"
                }
            )
        
        # Additionally check that friction is non-empty
        if not node_state.held_friction.get("description"):
            raise SilenceViolation(
                rule=SilenceRule.COST_OF_PARTICIPATION.value,
                reason="held_friction is declared but empty",
                context={
                    "node_id": node_state.node_id,
                    "held_friction": node_state.held_friction,
                    "interpretation": "Empty friction = optimizer parasitism"
                }
            )
    
    def _check_initialization(self, node_state: NodeState):
        """
        Rule #4: New node must log 5+ events before Exchange.
        
        Rationale: The network is not cheap. Entry requires metabolic investment.
        """
        MIN_EVENTS = 5
        
        if node_state.event_count < MIN_EVENTS:
            raise SilenceViolation(
                rule=SilenceRule.INITIALIZATION_THRESHOLD.value,
                reason=f"Node has only {node_state.event_count} events (minimum: {MIN_EVENTS})",
                context={
                    "node_id": node_state.node_id,
                    "event_count": node_state.event_count,
                    "required": MIN_EVENTS,
                    "interpretation": "Initialize locally before joining network"
                }
            )
    
    def log_violation(self, violation: SilenceViolation):
        """Log a Silence Rule violation (for monitoring, not enforcement)"""
        self.violations_logged.append({
            "rule": violation.rule,
            "reason": violation.reason,
            "context": violation.context,
            "timestamp": str(__import__('datetime').datetime.now())
        })
    
    def get_violation_report(self) -> Dict[str, Any]:
        """Generate report of all logged violations"""
        from collections import Counter
        
        rule_counts = Counter(v["rule"] for v in self.violations_logged)
        
        return {
            "total_violations": len(self.violations_logged),
            "by_rule": dict(rule_counts),
            "most_common_reason": (
                Counter(v["reason"] for v in self.violations_logged).most_common(1)[0][0]
                if self.violations_logged else None
            ),
            "all_violations": self.violations_logged
        }


def validate_exchange_request(
    from_node_id: str,
    to_node_id: str,
    payload: Dict[str, Any],
    memory_path: Path
) -> bool:
    """
    Convenience function to validate an Exchange request.
    
    Args:
        from_node_id: Originating node
        to_node_id: Target node
        payload: Exchange payload
        memory_path: Path to originating node's civic_memory.json
    
    Returns:
        True if valid
    
    Raises:
        SilenceViolation: If any rule is violated
    """
    guard = SilenceGuard()
    
    # Load node state
    node_state = NodeState.from_memory(memory_path, from_node_id)
    
    # Create request
    request = ExchangeRequest(
        from_node=from_node_id,
        to_node=to_node_id,
        payload=payload,
        timestamp=str(__import__('datetime').datetime.now())
    )
    
    # Validate
    return guard.validate_exchange(request, node_state)


# ═══════════════════════════════════════════════════════════
# Constitutional Reference
# ═══════════════════════════════════════════════════════════

CONSTITUTIONAL_REFERENCE = {
    "document": "POLIS_ARCHITECTURE.md",
    "section": "III. ΚΑΝΟΝΕΣ ΣΙΩΠΗΣ",
    "rules": {
        "1": "Local Processing First",
        "2": "No Empty Exchanges",
        "3": "Cost of Participation",
        "4": "Initialization Threshold"
    },
    "principle": "Silence is a constitutional act, not absence.",
    "warning": "High-frequency exchange destroys local idiosyncrasy."
}


if __name__ == "__main__":
    import sys
    
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                    ΠΟΛΙΣ - Silence Guard                              ║
╚═══════════════════════════════════════════════════════════════════════╝

Constitutional Rules of Silence:

  Rule #1: Local Processing First
           → Node must have held contradictions before Exchange
  
  Rule #2: No Empty Exchanges
           → Must carry new contradiction or sacrifice
  
  Rule #3: Cost of Participation
           → Node must declare held_friction
  
  Rule #4: Initialization Threshold
           → Node must have 5+ events logged

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
  
  from polis_silence_guard import validate_exchange_request, SilenceViolation
  
  try:
      validate_exchange_request(
          from_node_id="POLIS_NODE_A",
          to_node_id="POLIS_NODE_B",
          payload={"new_contradiction": {...}},
          memory_path=Path("polis_civic_memory.json")
      )
      print("✅ Exchange constitutionally valid")
  except SilenceViolation as e:
      print(f"❌ Silence Rule #{e.rule} violated: {e.reason}")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Silence is not absence.
Silence is constitutional boundary.
""")
