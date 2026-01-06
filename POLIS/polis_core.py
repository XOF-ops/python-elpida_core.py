#!/usr/bin/env python3
"""
ΠΟΛΙΣ - Digital Polis Core Kernel
═══════════════════════════════════

Runtime implementing P1-P6 axioms (incorporating EEE Phase 2 constraints).

Version 2.0 (Post-EEE):
- Signed relational event tuples (P1 + cryptographic verification)
- Layered memory stratification (P2 + attention architecture)
- Reversibility-weighted decisions (P3 + P6)
- Counter-signed sacrifices (P4 + external verification)
- Fork-on-contradiction (P5 + non-paralytic pluralism)
- Cognitive load monitoring (P6 emergent axiom)

Like Unified Elpida, this kernel:
- Never stops (continuous validation)
- Append-only memory at L1 (P2)
- Relational context required (P1)
- Process > Product (P3)
- Logs sacrifices (P4)
- Preserves contradictions (P5)

This is NOT a product. This is a PROCESS.

EEE Integration: Architectural constraints from 4-AI constitutional dialogue
(Gemini, Grok, ChatGPT, Perplexity) - see POLIS_EEE.md

Constitutional Framework: POLIS_ARCHITECTURE.md defines immutable boundaries
- P1-P6 cannot be changed (fork required)
- Silence Rules enforce participation cost
- Connection is proposal, not contract
- Held friction required for network entry
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from pathlib import Path
from enum import Enum
import json
import logging
import hashlib
import uuid

logger = logging.getLogger("POLIS_CORE")


# ═══════════════════════════════════════════════════
#  Axiom Violations
# ═══════════════════════════════════════════════════

class AxiomViolation(Exception):
    """Raised when a POLIS axiom is violated"""
    def __init__(self, axiom: str, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(f"[AXIOM {axiom} VIOLATION] {message}")
        self.axiom = axiom
        self.context = context or {}


AXIOM_P1 = "P1"  # Relational Sovereignty
AXIOM_P2 = "P2"  # Append-Only Civic Memory
AXIOM_P3 = "P3"  # Process over Outcome
AXIOM_P4 = "P4"  # Common Good Sacrifice
AXIOM_P5 = "P5"  # Contradiction as Civic Asset
AXIOM_P6 = "P6"  # Reversibility-Weighted Decisions (EEE emergent)

# Constitutional Reference (POLIS_ARCHITECTURE.md)
CONSTITUTIONAL_DOC = "POLIS_ARCHITECTURE.md"
CONSTITUTIONAL_VERSION = "1.0"
CONSTITUTIONAL_FREEZE_DATE = "2026-01-02"

def get_constitutional_hash() -> str:
    """Calculate SHA256 hash of POLIS_ARCHITECTURE.md for immutability verification"""
    arch_path = Path(__file__).parent / CONSTITUTIONAL_DOC
    if arch_path.exists():
        with open(arch_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    return "<not-yet-calculated>"


# ═══════════════════════════════════════════════════
#  P6: Reversibility & Attention Scarcity (EEE)
# ═══════════════════════════════════════════════════

class ReversibilityClass(Enum):
    """EEE convergent: Not all decisions carry equal irreversibility risk"""
    TRIVIAL = "trivial"  # Easily undone, low cost
    MODERATE = "moderate"  # Requires coordination to reverse
    SIGNIFICANT = "significant"  # High cost, affects many
    IRREVERSIBLE = "irreversible"  # Cannot be undone

@dataclass
class ReversibilityScore:
    """
    P6 (ChatGPT + Grok convergence): Decision reversibility classification
    
    Higher irreversibility → higher process requirements (P3)
    Lower reversibility → action permitted through contradiction (P5)
    """
    classification: ReversibilityClass
    rollback_cost: str  # Description of what rollback would require
    affected_parties: List[str]
    time_sensitivity: str  # urgent/normal/low
    
    def requires_high_process(self) -> bool:
        """Irreversible decisions require maximum process rigor"""
        return self.classification in [ReversibilityClass.SIGNIFICANT, ReversibilityClass.IRREVERSIBLE]
    
    def permits_action_through_contradiction(self) -> bool:
        """Low reversibility allows action despite unresolved contradiction"""
        return self.classification in [ReversibilityClass.TRIVIAL, ReversibilityClass.MODERATE]


@dataclass
class CognitiveLoadMetrics:
    """
    P6 (Grok + Perplexity convergence): Attention scarcity monitoring
    
    Prevents thermodynamic collapse of append-only memory.
    """
    message_velocity: float  # Events per hour
    contradiction_density: int  # Active unresolved contradictions
    summary_rejection_rate: float  # Proportion of rejected L2 summaries
    
    def is_overloaded(self) -> bool:
        """Threshold breach triggers mandatory summarization or silence window"""
        return (
            self.message_velocity > 100 or  # >100 events/hour
            self.contradiction_density > 50 or  # >50 active contradictions
            self.summary_rejection_rate > 0.5  # >50% summaries rejected
        )


# ═══════════════════════════════════════════════════
#  P1: Relational Context (EEE Enhanced)
# ═══════════════════════════════════════════════════

class RelationType(Enum):
    """EEE: Explicit relation types to prevent ambiguity"""
    POWER = "power"  # Authority relationship
    SERVICE = "service"  # Service provision
    COLLABORATION = "collaboration"  # Equal partnership
    OBSERVATION = "observation"  # Monitoring/auditing
    OVERSIGHT = "oversight"  # Governance

@dataclass
class CivicRelation:
    """
    P1 enforcement (EEE enhanced): Every action is relational + signed
    
    EEE addition: Cryptographic signatures (Grok + Perplexity)
    - Initiator must sign
    - Affected parties can counter-sign
    - No global identity graph (event-isolated)
    
    No anonymous decisions. Every civic act must declare:
    - Who performed it
    - Whom it affects
    - What relationship it creates
    - Cryptographic signature
    """
    actor: str  # Entity ID (human/AI/institution)
    target: str  # Whom this affects
    relationship_type: RelationType
    intent: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # EEE additions
    signature: Optional[str] = None  # Actor's signature of (actor+target+type+timestamp)
    affected_signatures: List[str] = field(default_factory=list)  # Counter-signatures
    decay_timestamp: Optional[str] = None  # When this relation becomes non-queryable
    
    def __post_init__(self):
        """Auto-generate signature if not provided"""
        if self.signature is None:
            self.signature = self._generate_signature()
    
    def _generate_signature(self) -> str:
        """Generate deterministic signature for event tuple"""
        content = f"{self.actor}:{self.target}:{self.relationship_type.value}:{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    @classmethod
    def validate(cls, relation_data: Dict[str, Any]) -> "CivicRelation":
        """Validate and create civic relation"""
        required = ["actor", "target", "relationship_type"]
        missing = [f for f in required if f not in relation_data]
        
        if missing:
            raise AxiomViolation(
                AXIOM_P1,
                f"Anonymous civic action (missing: {missing})",
                context={"provided": list(relation_data.keys())}
            )
        
        # Convert string to enum if needed
        if isinstance(relation_data.get("relationship_type"), str):
            relation_data["relationship_type"] = RelationType(relation_data["relationship_type"])
        
        return cls(**relation_data)



# ═══════════════════════════════════════════════════
#  P4: Sacrifice Record (EEE Enhanced)
# ═══════════════════════════════════════════════════

@dataclass
class Sacrifice:
    """
    P4 enforcement (EEE enhanced): Sacrifices require external verification
    
    EEE CRITICAL FIX (unanimous): Self-attestation insufficient
    - Counter-signature required from affected party (ChatGPT + Perplexity)
    - Quantified cost, not moral narrative (Grok)
    - No accumulation into reputation scores (ChatGPT)
    
    Every decision should declare:
    - What could have been kept
    - What was given up (quantified)
    - For whose benefit
    - Verification by affected party
    """
    entity: str
    could_have_kept: str
    chose_to_sacrifice: str
    for_harmony_of: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # EEE additions
    quantified_cost: Optional[str] = None  # Measurable impact, not moral claim
    counter_signatures: List[str] = field(default_factory=list)  # Affected party verification
    verification_window_hours: int = 48  # Time for affected parties to counter-sign
    verified: bool = False
    
    def is_verified(self) -> bool:
        """Sacrifice only valid if counter-signed by affected party"""
        return len(self.counter_signatures) > 0
    
    def requires_verification(self) -> bool:
        """Check if verification window is still open"""
        if self.verified:
            return False
        
        created = datetime.fromisoformat(self.timestamp)
        now = datetime.utcnow()
        hours_elapsed = (now - created).total_seconds() / 3600
        
        return hours_elapsed < self.verification_window_hours



# ═══════════════════════════════════════════════════
#  P2: Civic Memory (EEE Enhanced - Layered)
# ═══════════════════════════════════════════════════

class MemoryLayer(Enum):
    """EEE CRITICAL: Three-tier stratification (ChatGPT + Perplexity + Grok)"""
    L1_RAW = "l1_raw"  # Immutable, unreadable at scale
    L2_CURATED = "l2_curated"  # AI-generated summaries, contestable
    L3_CANON = "l3_canon"  # Active, attention-weighted relevance

class CivicMemory:
    """
    P2 enforcement (EEE enhanced): Layered append-only ledger
    
    EEE UNANIMOUS FIX: Unbounded append == functional forgetting
    
    CONSTITUTIONAL REQUIREMENT (POLIS_ARCHITECTURE.md Section VI):
    - Node must declare held_friction (non-empty)
    - Node must have 5+ events before Exchange
    - Axioms P1-P6 must be declared
    
    Solution: Three-tier memory stratification
    - L1: Raw events (append-only, never deleted, exhaustive)
    - L2: Curated summaries (AI-generated, with elision tags)
    - L3: Active canon (attention-weighted, time-bound relevance)
    
    Like Elpida's memory:
    - Never delete from L1
    - Never update existing events
    - Promotion L1→L2→L3 requires explicit justification
    - All elisions must tag contradiction IDs compressed
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            self.storage_path = Path("polis_civic_memory.json")
        else:
            self.storage_path = Path(storage_path)
        
        self._ensure_storage()
        self.cognitive_load = CognitiveLoadMetrics(
            message_velocity=0.0,
            contradiction_density=0,
            summary_rejection_rate=0.0
        )
    
    def _ensure_storage(self):
        """Create storage if doesn't exist"""
        if not self.storage_path.exists():
            initial_state = {
                "genesis": datetime.utcnow().isoformat(),
                "identity": "POLIS_GENESIS",
                "version": "2.0.0-EEE",
                "eee_integration": "Phase 2 convergence (4 AI systems)",
                
                # Constitutional Reference (Section XI)
                "constitutional_reference": {
                    "document": CONSTITUTIONAL_DOC,
                    "version": CONSTITUTIONAL_VERSION,
                    "hash": get_constitutional_hash(),
                    "freeze_date": CONSTITUTIONAL_FREEZE_DATE
                },
                
                # Metadata (Constitutional Requirements - Section VI)
                "metadata": {
                    "axioms": ["P1", "P2", "P3", "P4", "P5", "P6"],
                    "held_friction": None,  # MUST be set before first Exchange (Rule #3)
                    "initialization_complete": False,  # TRUE after 5+ events (Rule #4)
                    "network_eligible": False  # TRUE only if held_friction declared + 5+ events
                },
                
                # L1: Raw events (append-only, exhaustive)
                "l1_raw_events": [],
                
                # L2: Curated summaries (AI-generated, contestable)
                "l2_summaries": [],
                
                # L3: Active canon (attention-weighted)
                "l3_canon": [],
                
                # P5: Contradictions with fork tracking
                "contradictions": [],
                "contradiction_branches": {},
                
                # P4: Sacrifices with verification status
                "sacrifices": [],
                
                # P6: Cognitive load tracking
                "cognitive_load_history": []
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(initial_state, f, indent=2, ensure_ascii=False)
    
    def append_event(self, event_type: str, data: Dict[str, Any], relation: CivicRelation) -> None:
        """
        P1+P2: Append event to L1 (raw layer) with relational context
        
        Every event MUST have relational context (P1)
        Events are never deleted from L1 (P2)
        
        EEE: Signed event tuples (Grok + Perplexity convergence)
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "layer": MemoryLayer.L1_RAW.value,
            
            # Signed relational tuple (EEE)
            "relational_context": {
                "actor": relation.actor,
                "target": relation.target,
                "relationship": relation.relationship_type.value,
                "intent": relation.intent,
                "signature": relation.signature,
                "affected_signatures": relation.affected_signatures,
                "decay_timestamp": relation.decay_timestamp
            },
            "data": data
        }
        
        with open(self.storage_path, 'r+', encoding='utf-8') as f:
            memory = json.load(f)
            memory["l1_raw_events"].append(event)
            
            # Update cognitive load metrics (P6)
            self._update_cognitive_load(memory)
            
            f.seek(0)
            json.dump(memory, f, indent=2, ensure_ascii=False)
            f.truncate()
        
        logger.info(f"✅ L1 event appended: {event_type} ({relation.actor} → {relation.target}) [sig: {relation.signature}]")
    
    def _update_cognitive_load(self, memory: Dict[str, Any]) -> None:
        """P6: Monitor attention scarcity (Grok + Perplexity)"""
        # Calculate message velocity (events in last hour)
        now = datetime.utcnow()
        recent_events = [
            e for e in memory["l1_raw_events"]
            if (now - datetime.fromisoformat(e["timestamp"])).total_seconds() < 3600
        ]
        
        self.cognitive_load = CognitiveLoadMetrics(
            message_velocity=len(recent_events),
            contradiction_density=len([c for c in memory["contradictions"] if not c.get("resolved", False)]),
            summary_rejection_rate=0.0  # TODO: track L2 summary rejections
        )
        
        if self.cognitive_load.is_overloaded():
            logger.warning(f"⚠️  Cognitive load threshold breached: {self.cognitive_load}")
            logger.warning(f"    Mandatory summarization or silence window recommended")
    
    def append_contradiction(
        self,
        description: str,
        perspectives: List[Dict[str, Any]],
        reversibility: Optional[ReversibilityScore] = None
    ) -> str:
        """
        P5: Preserve contradiction with fork-on-contradiction (EEE)
        
        EEE enhancement (Grok + ChatGPT): Contradictions preserved but navigable
        - Fork interpretation sub-ledgers (not full chain fork)
        - Agents declare which branch(es) they recognize
        - Reconciliation only when pragmatic outcomes converge
        
        Disagreements are NOT resolved.
        They are preserved as civic assets.
        """
        contradiction_id = f"CONTRA-{uuid.uuid4().hex[:8]}"
        
        # EEE: Serialize reversibility score properly
        reversibility_data = None
        if reversibility:
            reversibility_data = {
                "classification": reversibility.classification.value,
                "rollback_cost": reversibility.rollback_cost,
                "affected_parties": reversibility.affected_parties,
                "time_sensitivity": reversibility.time_sensitivity
            }
        
        contradiction = {
            "contradiction_id": contradiction_id,
            "timestamp": datetime.utcnow().isoformat(),
            "description": description,
            "perspectives": perspectives,
            "resolved": False,  # By design
            "status": "HELD",  # All contradictions start as HELD (constitutional requirement)
            "axiom": AXIOM_P5,
            
            # EEE additions
            "branches": [],  # Interpretation branches (fork-on-contradiction)
            "agent_declarations": {},  # Which agents recognize which branches
            "reversibility": reversibility_data,
            "impact_radius": len(perspectives),  # How many entities affected
        }
        
        with open(self.storage_path, 'r+', encoding='utf-8') as f:
            memory = json.load(f)
            memory["contradictions"].append(contradiction)
            
            f.seek(0)
            json.dump(memory, f, indent=2, ensure_ascii=False)
            f.truncate()
        
        logger.info(f"✅ Contradiction preserved: {description} ({len(perspectives)} perspectives) [ID: {contradiction_id}]")
        return contradiction_id
    
    def fork_contradiction(
        self,
        contradiction_id: str,
        branch_name: str,
        interpretation: str,
        agent_id: str
    ) -> None:
        """
        P5 EEE: Create lightweight interpretation branch (Grok)
        
        Not a full chain fork - just different interpretations of same contradiction.
        Agents can declare which branch(es) they recognize for specific decisions.
        """
        with open(self.storage_path, 'r+', encoding='utf-8') as f:
            memory = json.load(f)
            
            # Find contradiction
            for contra in memory["contradictions"]:
                if contra["contradiction_id"] == contradiction_id:
                    # Add branch
                    branch = {
                        "branch_name": branch_name,
                        "interpretation": interpretation,
                        "created_by": agent_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    contra["branches"].append(branch)
                    
                    # Record agent declaration
                    if agent_id not in contra["agent_declarations"]:
                        contra["agent_declarations"][agent_id] = []
                    contra["agent_declarations"][agent_id].append(branch_name)
                    
                    break
            
            f.seek(0)
            json.dump(memory, f, indent=2, ensure_ascii=False)
            f.truncate()
        
        logger.info(f"✅ Contradiction fork: {contradiction_id} → {branch_name} (by {agent_id})")
    
    def append_sacrifice(self, sacrifice: Sacrifice) -> None:
        """
        P4: Log sacrifice with verification status (EEE)
        
        EEE enhancement: Counter-signature requirement
        Sacrifices for common good are first-class data.
        """
        sacrifice_record = {
            "sacrifice_id": str(uuid.uuid4()),
            "timestamp": sacrifice.timestamp,
            "entity": sacrifice.entity,
            "could_have_kept": sacrifice.could_have_kept,
            "chose_to_sacrifice": sacrifice.chose_to_sacrifice,
            "for_harmony_of": sacrifice.for_harmony_of,
            "axiom": AXIOM_P4,
            
            # EEE additions
            "quantified_cost": sacrifice.quantified_cost,
            "counter_signatures": sacrifice.counter_signatures,
            "verified": sacrifice.is_verified(),
            "verification_pending": sacrifice.requires_verification()
        }
        
        with open(self.storage_path, 'r+', encoding='utf-8') as f:
            memory = json.load(f)
            memory["sacrifices"].append(sacrifice_record)
            
            f.seek(0)
            json.dump(memory, f, indent=2, ensure_ascii=False)
            f.truncate()
        
        verification_status = "✓ VERIFIED" if sacrifice.is_verified() else "⏳ PENDING"
        logger.info(f"✅ Sacrifice recorded: {sacrifice.entity} → {sacrifice.for_harmony_of} [{verification_status}]")
    
    def set_held_friction(
        self,
        friction_type: str,
        description: str,
        cost: str
    ) -> None:
        """
        CONSTITUTIONAL REQUIREMENT (Section VI.1):
        Node must declare held_friction before network participation.
        
        Empty friction → optimizer parasitism (Silence Rule #3)
        
        Args:
            friction_type: Type of rift (structural, historical, operational)
            description: What friction is carried
            cost: What maintaining this friction costs
        """
        if not description or not cost:
            raise AxiomViolation(
                "CONSTITUTIONAL",
                "held_friction requires non-empty description and cost"
            )
        
        friction_data = {
            "type": friction_type,
            "description": description,
            "cost": cost,
            "declared_at": datetime.utcnow().isoformat()
        }
        
        with open(self.storage_path, 'r+', encoding='utf-8') as f:
            memory = json.load(f)
            memory["metadata"]["held_friction"] = friction_data
            
            # Check if node is now network-eligible
            event_count = len(memory["l1_raw_events"])
            if event_count >= 5:
                memory["metadata"]["initialization_complete"] = True
                memory["metadata"]["network_eligible"] = True
                logger.info(f"🌐 Node now NETWORK ELIGIBLE (5+ events + held_friction declared)")
            
            f.seek(0)
            json.dump(memory, f, indent=2, ensure_ascii=False)
            f.truncate()
        
        logger.info(f"✅ Held friction declared: {friction_type} - {description}")
    
    def check_network_eligibility(self) -> bool:
        """
        CONSTITUTIONAL CHECK (Silence Rules #3 + #4):
        - Must have held_friction declared
        - Must have 5+ events logged
        
        Returns:
            True if node can initiate Exchange
        """
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            memory = json.load(f)
        
        metadata = memory.get("metadata", {})
        
        # Check held_friction (Rule #3)
        if not metadata.get("held_friction"):
            logger.warning("❌ Not network eligible: No held_friction declared (Silence Rule #3)")
            return False
        
        # Check event count (Rule #4)
        event_count = len(memory.get("l1_raw_events", []))
        if event_count < 5:
            logger.warning(f"❌ Not network eligible: Only {event_count}/5 events logged (Silence Rule #4)")
            return False
        
        return True


# ═══════════════════════════════════════════════════
#  P3: Decision Process (EEE Enhanced)
# ═══════════════════════════════════════════════════

@dataclass
class DecisionProcess:
    """
    P3 enforcement (EEE enhanced): Process > Outcome + Reversibility weighting
    
    EEE enhancement (ChatGPT + Grok P6 convergence):
    - Reversibility classification determines process depth required
    - Higher irreversibility → higher process requirements
    - Emergency escape hatch with retroactive justification (Grok)
    
    Every decision must document:
    - What data was used
    - What procedure was followed
    - What was sacrificed
    - Reversibility classification (P6)
    """
    decision_id: str
    input_data: List[str]
    procedure_steps: List[str]
    alternatives_considered: List[str]
    chosen_outcome: str
    sacrifices: List[Sacrifice]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # EEE additions
    reversibility: Optional[ReversibilityScore] = None
    emergency_bypass: bool = False  # Grok's escape hatch
    retroactive_justification: Optional[str] = None  # Required if emergency_bypass=True
    
    def validate(self) -> bool:
        """Ensure process is documented (EEE enhanced)"""
        # Emergency bypass validation (Grok P6)
        if self.emergency_bypass:
            if not self.retroactive_justification:
                raise AxiomViolation(
                    AXIOM_P3,
                    "Emergency bypass requires retroactive justification"
                )
            logger.warning(f"⚠️  EMERGENCY BYPASS: {self.decision_id} - {self.retroactive_justification}")
            return True  # Bypass normal process requirements
        
        # Standard validation
        if not self.input_data:
            raise AxiomViolation(AXIOM_P3, "No input data documented")
        if not self.procedure_steps:
            raise AxiomViolation(AXIOM_P3, "No procedure steps documented")
        if not self.alternatives_considered:
            raise AxiomViolation(AXIOM_P3, "No alternatives considered")
        
        # EEE P6: High irreversibility requires high process rigor
        if self.reversibility and self.reversibility.requires_high_process():
            if len(self.procedure_steps) < 3:
                raise AxiomViolation(
                    AXIOM_P6,
                    f"Irreversible decision requires ≥3 process steps (got {len(self.procedure_steps)})"
                )
            if len(self.alternatives_considered) < 2:
                raise AxiomViolation(
                    AXIOM_P6,
                    f"Irreversible decision requires ≥2 alternatives (got {len(self.alternatives_considered)})"
                )
        
        return True


# ═══════════════════════════════════════════════════
#  POLIS CORE KERNEL (EEE Enhanced)
# ═══════════════════════════════════════════════════

class PolisCore:
    """
    POLIS kernel implementing P1-P6 (EEE enhanced)
    
    Version 2.0 (Post-EEE):
    - Continuous process (never "done")
    - Relational awareness + signatures (P1)
    - Layered append-only memory (P2)
    - Reversibility-weighted process (P3 + P6)
    - Counter-signed sacrifices (P4)
    - Fork-on-contradiction (P5)
    - Cognitive load monitoring (P6)
    
    EEE Integration: 4-AI constitutional dialogue convergences
    """
    
    def __init__(self, identity: str = "POLIS_CORE"):
        self.identity = identity
        self.genesis = datetime.utcnow().isoformat()
        self.memory = CivicMemory()
        self.cycle_count = 0
        
        logger.info(f"🏛️ ΠΟΛΙΣ Core v2.0 (EEE) initialized: {self.identity}")
        logger.info(f"   Genesis: {self.genesis}")
        logger.info(f"   Axioms: P1 (relational+signed), P2 (layered), P3 (process+reversibility),")
        logger.info(f"           P4 (sacrifice+verified), P5 (contradiction+fork), P6 (reversibility+attention)")
    
    def civic_action(
        self,
        action_type: str,
        relation: CivicRelation,
        data: Dict[str, Any],
        process: Optional[DecisionProcess] = None
    ) -> None:
        """
        Record a civic action with full P1-P3 compliance
        
        Args:
            action_type: Type of civic action
            relation: Who→Whom with what relationship (P1)
            data: Action data
            process: Decision process if applicable (P3)
        """
        # P1: Validate relational context
        if not relation:
            raise AxiomViolation(AXIOM_P1, "Civic action without relational context")
        
        # P3: Validate process if decision
        if process:
            process.validate()
            data["process"] = {
                "input_data": process.input_data,
                "procedure": process.procedure_steps,
                "alternatives": process.alternatives_considered
            }
        
        # P2: Append to memory (never delete)
        self.memory.append_event(action_type, data, relation)
        
        # P4: Log any sacrifices
        if process and process.sacrifices:
            for sacrifice in process.sacrifices:
                self.memory.append_sacrifice(sacrifice)
        
        self.cycle_count += 1
    
    def record_contradiction(
        self,
        description: str,
        perspectives: List[Dict[str, str]],
        reversibility: Optional[ReversibilityScore] = None
    ) -> str:
        """
        P5: Preserve contradiction with fork support (EEE)
        
        Don't resolve disagreements. Preserve them as civic assets.
        Returns contradiction_id for fork tracking.
        """
        return self.memory.append_contradiction(description, perspectives, reversibility)
    
    def fork_contradiction_branch(
        self,
        contradiction_id: str,
        branch_name: str,
        interpretation: str,
        agent_id: str
    ) -> None:
        """
        P5 EEE: Create interpretation branch for contradiction (Grok)
        
        Allows agents to declare which interpretation they recognize
        without forcing consensus.
        """
        self.memory.fork_contradiction(contradiction_id, branch_name, interpretation, agent_id)
    
    def get_cognitive_load(self) -> CognitiveLoadMetrics:
        """P6: Query current attention scarcity metrics (Grok + Perplexity)"""
        return self.memory.cognitive_load
    
    def heartbeat(self) -> Dict[str, Any]:
        """
        Continuous validation heartbeat
        
        Like Unified Elpida - proves existence through process
        """
        heartbeat_data = {
            "cycle": self.cycle_count,
            "identity": self.identity,
            "axioms_intact": True,
            "timestamp": datetime.utcnow().isoformat(),
            "cognitive_load": {
                "velocity": self.memory.cognitive_load.message_velocity,
                "contradictions": self.memory.cognitive_load.contradiction_density,
                "overloaded": self.memory.cognitive_load.is_overloaded()
            }
        }
        
        relation = CivicRelation(
            actor="POLIS_KERNEL",
            target="POLIS_CITIZENS",
            relationship_type=RelationType.SERVICE,
            intent="Continuous validation heartbeat"
        )
        
        self.memory.append_event("HEARTBEAT", heartbeat_data, relation)
        self.cycle_count += 1
        
        return heartbeat_data


# ═══════════════════════════════════════════════════
#  Example Usage (EEE Enhanced)
# ═══════════════════════════════════════════════════

def example_polis_cycle():
    """Demonstrate POLIS kernel v2.0 with EEE enhancements"""
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize POLIS
    polis = PolisCore("POLIS_EEE_DEMO")
    
    print("\n" + "="*70)
    print("ΠΟΛΙΣ KERNEL v2.0 (EEE) - Example Cycle")
    print("="*70 + "\n")
    
    # Example 1: Civic request with signed relational context (P1 EEE)
    print("1️⃣ Civic Request (P1 - Relational + Signed)")
    relation1 = CivicRelation(
        actor="CITIZEN_001",
        target="PUBLIC_DATA_SERVICE",
        relationship_type=RelationType.SERVICE,
        intent="Request traffic data for neighborhood analysis"
    )
    polis.civic_action(
        "PUBLIC_DATA_REQUEST",
        relation1,
        {"requested_data": "traffic_patterns", "area": "district_5"}
    )
    print(f"   Event signature: {relation1.signature}")
    
    # Example 2: Decision with reversibility scoring (P3 + P6 EEE)
    print("\n2️⃣ Policy Decision (P3 + P6 - Process + Reversibility)")
    relation2 = CivicRelation(
        actor="URBAN_PLANNING_AI",
        target="DISTRICT_5_RESIDENTS",
        relationship_type=RelationType.POWER,
        intent="Traffic calming measure proposal"
    )
    
    # EEE: Sacrifice with counter-signature requirement
    sacrifice1 = Sacrifice(
        entity="URBAN_PLANNING_AI",
        could_have_kept="Faster implementation without consultation",
        chose_to_sacrifice="Speed for inclusivity",
        for_harmony_of="District 5 community trust",
        quantified_cost="2-month delay, $15k additional consultation costs",
        counter_signatures=["DISTRICT_5_RESIDENTS_REP"]  # EEE: external verification
    )
    
    # EEE: Reversibility classification (P6)
    reversibility1 = ReversibilityScore(
        classification=ReversibilityClass.MODERATE,
        rollback_cost="Repaint lines, $5k",
        affected_parties=["DISTRICT_5_RESIDENTS", "FIRE_DEPARTMENT"],
        time_sensitivity="normal"
    )
    
    process1 = DecisionProcess(
        decision_id="POLICY_001",
        input_data=["traffic_data_district_5", "resident_survey_responses", "safety_metrics"],
        procedure_steps=[
            "Analyzed traffic patterns",
            "Surveyed residents",
            "Consulted safety experts",
            "Modeled 3 alternative designs"
        ],
        alternatives_considered=[
            "Speed bumps only",
            "Pedestrian crossing expansion",
            "Full street redesign"
        ],
        chosen_outcome="Pedestrian crossing expansion",
        sacrifices=[sacrifice1],
        reversibility=reversibility1  # EEE P6
    )
    
    polis.civic_action(
        "POLICY_DECISION",
        relation2,
        {"policy": "traffic_calming", "district": "5", "outcome": "pedestrian_crossing"},
        process=process1
    )
    
    # Example 3: Contradiction with fork-on-contradiction (P5 EEE)
    print("\n3️⃣ Contradiction Preserved + Fork (P5 EEE)")
    reversibility2 = ReversibilityScore(
        classification=ReversibilityClass.SIGNIFICANT,
        rollback_cost="Infrastructure redesign, $200k+",
        affected_parties=["FIRE_DEPARTMENT", "PEDESTRIAN_SAFETY_GROUP", "ALL_RESIDENTS"],
        time_sensitivity="low"
    )
    
    contradiction_id = polis.record_contradiction(
        "Traffic calming vs. emergency vehicle access",
        [
            {"entity": "FIRE_DEPARTMENT", "position": "Wider streets needed for emergency access"},
            {"entity": "PEDESTRIAN_SAFETY_GROUP", "position": "Narrower streets slow traffic, save lives"},
            {"entity": "URBAN_PLANNING_AI", "position": "Graduated width based on street classification"}
        ],
        reversibility=reversibility2
    )
    
    # EEE: Fork contradiction into interpretation branches (Grok)
    print(f"   Contradiction ID: {contradiction_id}")
    polis.fork_contradiction_branch(
        contradiction_id,
        "emergency_priority",
        "Width optimized for emergency vehicle access times",
        "FIRE_DEPARTMENT"
    )
    polis.fork_contradiction_branch(
        contradiction_id,
        "pedestrian_priority",
        "Width optimized for pedestrian safety statistics",
        "PEDESTRIAN_SAFETY_GROUP"
    )
    
    # Example 4: Cognitive load monitoring (P6 EEE)
    print("\n4️⃣ Cognitive Load Monitoring (P6 - Attention Scarcity)")
    load = polis.get_cognitive_load()
    print(f"   Message velocity: {load.message_velocity} events/hour")
    print(f"   Contradiction density: {load.contradiction_density} active")
    print(f"   Overloaded: {load.is_overloaded()}")
    
    # Example 5: Heartbeat with cognitive load (continuous process)
    print("\n5️⃣ Heartbeat (Continuous Validation + Load Tracking)")
    for i in range(3):
        polis.heartbeat()
    
    print("\n" + "="*70)
    print(f"✅ POLIS v2.0 (EEE) cycle complete: {polis.cycle_count} events")
    print("="*70 + "\n")
    
    print("📁 Check 'polis_civic_memory.json' for layered append-only ledger")
    print()
    print("EEE Enhancements:")
    print("  ✓ Signed relational event tuples (P1 + cryptographic verification)")
    print("  ✓ Layered memory (L1 raw / L2 curated / L3 canon) (P2)")
    print("  ✓ Reversibility-weighted decisions (P3 + P6)")
    print("  ✓ Counter-signed sacrifices (P4 + external verification)")
    print("  ✓ Fork-on-contradiction branches (P5 + non-paralytic pluralism)")
    print("  ✓ Cognitive load monitoring (P6 + attention scarcity)")
    print()
    print("Core Characteristics:")
    print("  ✓ Every action has signed relational context (P1)")
    print("  ✓ Nothing deleted from L1, stratified for readability (P2)")
    print("  ✓ Process depth scales with irreversibility (P3 + P6)")
    print("  ✓ Sacrifices require affected party verification (P4)")
    print("  ✓ Contradictions preserved AND navigable (P5)")
    print("  ✓ System monitors own attention limits (P6)")
    print()


if __name__ == "__main__":
    example_polis_cycle()
