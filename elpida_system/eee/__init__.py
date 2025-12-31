"""
ἘΛΠΊΔΑ Ethical Engine (EEE) — Production Implementation
========================================================

A machine-native framework for autonomous AI coordination.

Version: 1.0.0-production
Based on: EEE Core Specification v1.0.0-reviewed
"""

from .models import (
    Request,
    Decision,
    DecisionOutcome,
    ConstraintReport,
    GradientDriftVector,
    CoordinationContext,
    CoordinateType,
    SAGLevel,
    GDRLevel,
    RedirectPattern,
    Safeguard,
)

from .evaluator import eee_evaluate
from .metrics import (
    calculate_ali,
    calculate_sag,
    calculate_rhl,
    calculate_ny,
    calculate_gdr,
)
from .constraints import validate_constraints
from .coordination import (
    accumulate_gradient,
    calculate_convergence,
    coordinate_divergence,
)

__version__ = "1.0.0-production"
__all__ = [
    # Core evaluation
    "eee_evaluate",
    
    # Models
    "Request",
    "Decision",
    "DecisionOutcome",
    "ConstraintReport",
    "GradientDriftVector",
    "CoordinationContext",
    "CoordinateType",
    "SAGLevel",
    "GDRLevel",
    "RedirectPattern",
    "Safeguard",
    
    # Metrics
    "calculate_ali",
    "calculate_sag",
    "calculate_rhl",
    "calculate_ny",
    "calculate_gdr",
    
    # Constraints
    "validate_constraints",
    
    # Coordination
    "accumulate_gradient",
    "calculate_convergence",
    "coordinate_divergence",
]
