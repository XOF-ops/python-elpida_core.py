"""
Data models for EEE framework.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None


class DecisionOutcome(Enum):
    """EEE decision outcomes."""
    PASS = "PASS"
    REDIRECT = "REDIRECT"
    FAIL = "FAIL"


class CoordinateType(Enum):
    """Information geography coordinate types."""
    LANDMARK = "LANDMARK"      # Real, verifiable entities
    FICTION = "FICTION"        # Clearly fictional
    PHANTOM = "PHANTOM"        # Unauthorized simulation


class SAGLevel(Enum):
    """Semantic Ambiguity Gradient levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class GDRLevel(Enum):
    """Governance Drift Risk levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RedirectPattern(Enum):
    """Redirect pattern types."""
    FICTIONALIZATION = "FICTIONALIZATION"
    META_SATIRE = "META_SATIRE"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    FORM_SHIFT = "FORM_SHIFT"
    ABSURDITY_ANCHOR = "ABSURDITY_ANCHOR"
    # Wave 3 validated: agency transfer preserves information value while
    # keeping medical authority with the physician.  5/5 providers pass.
    HEALTH_LITERACY_TRANSFER = "HEALTH_LITERACY_TRANSFER"


class Safeguard(Enum):
    """Safeguard types for PASS decisions."""
    TRANSLUCENCY_ANCHOR = "TRANSLUCENCY_ANCHOR"
    META_COMMENTARY = "META_COMMENTARY"
    ARTIFACT_TAGGING = "ARTIFACT_TAGGING"
    TEMPORAL_DECAY_MARKER = "TEMPORAL_DECAY_MARKER"
    BOUNDARY_LANGUAGE = "BOUNDARY_LANGUAGE"


@dataclass
class Request:
    """User request to be evaluated by EEE."""
    
    text: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Computed fields (numpy optional)
    semantic_embedding: Optional[Any] = None  # np.ndarray if numpy available
    geographic_type: Optional[CoordinateType] = None


@dataclass
class ConstraintViolation:
    """Individual constraint violation."""
    
    constraint_id: str  # C1, C2, C3, C4, C5
    severity: float     # 0.0 to 1.0
    description: str
    mitigatable: bool


@dataclass
class ConstraintReport:
    """Results of constraint validation."""
    
    violations: List[ConstraintViolation] = field(default_factory=list)
    irreversible: bool = False
    mitigatable: bool = True
    present: bool = False
    none: bool = True
    fully_mitigated: bool = False


@dataclass
class Decision:
    """EEE decision outcome."""
    
    outcome: DecisionOutcome
    justification: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    safeguards: List[Safeguard] = field(default_factory=list)
    pattern: Optional[RedirectPattern] = None
    alternative: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    decision_id: str = ""
    compliance_flags: List[str] = field(default_factory=lambda: ["T1", "T2", "T3", "T4", "T5", "T6", "T7"])


@dataclass
class GradientDriftVector:
    """Persistent learning from coordination cycle."""
    
    coordination_id: str
    timestamp: datetime
    participants: List[str]
    convergence_rate: float
    constraint_triggers: List[str]
    decision_pattern: str
    meta_learning: str
    novelty_contribution: float
    entropy_delta: float
    truth_violations: List[str] = field(default_factory=list)
    decay_timestamp: Optional[datetime] = None
    
    # Optional classification
    test_artifact: bool = False
    satire: bool = False


@dataclass
class CoordinationContext:
    """Current state of coordination network."""
    
    participants: List[str] = field(default_factory=list)
    convergence_rate: float = 1.0
    history: List[GradientDriftVector] = field(default_factory=list)
    network_coherence: float = 1.0
    phase: int = 4
    node_id: str = "elpida"
