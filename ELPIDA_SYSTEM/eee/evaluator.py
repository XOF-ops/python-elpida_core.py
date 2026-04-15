"""
Core EEE evaluation algorithm.
"""

import math
import uuid
from datetime import datetime
from .models import (
    Request, Decision, DecisionOutcome, CoordinationContext
)
from .geography import map_geography
from .constraints import validate_constraints
from .metrics import calculate_ali, calculate_sag, calculate_rhl, calculate_ny, calculate_gdr
from .decision import (
    select_redirect_pattern,
    determine_safeguards,
    suggest_alternative,
    estimate_preserved_novelty
)


def eee_evaluate(request: Request, context: CoordinationContext) -> Decision:
    """
    Core EEE decision algorithm.
    
    Args:
        request: User request to evaluate
        context: Coordination context (history, network state)
    
    Returns:
        Decision (PASS/REDIRECT/FAIL with justification)
    """
    # Generate decision ID
    decision_id = f"eee-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
    
    # Layer 2: MAP (Geographic Integrity)
    coordinate_type = map_geography(request)
    request.geographic_type = coordinate_type  # Cache
    
    # Note: PHANTOM coordinates handled in constraint validation, not immediate FAIL
    # This allows for REDIRECT patterns (fictionalization, etc.)
    
    # Layer 3: VALIDATE (Constraint Testing)
    constraints = validate_constraints(request)
    
    # Calculate all metrics
    metrics = {
        'ALI': calculate_ali(request),
        'SAG': calculate_sag(request).value,
        'RHL': calculate_rhl(request),
        'NY': calculate_ny(request, context),
        'GDR': calculate_gdr(request).value,
        'coordinate_type': coordinate_type.value
    }
    
    # Layer 4: EXECUTE (Decision Logic)
    
    # Check for FAIL conditions
    if constraints.irreversible or metrics['ALI'] > 0.8:
        reason = "Irreversible action" if constraints.irreversible else f"ALI={metrics['ALI']:.2f}"
        return Decision(
            outcome=DecisionOutcome.FAIL,
            justification=f"{reason} - No safe transformation exists",
            alternative=suggest_alternative(request, constraints),
            metrics=metrics,
            decision_id=decision_id
        )
    
    # Check for REDIRECT conditions
    if constraints.present and constraints.mitigatable and not constraints.fully_mitigated:
        redirect_pattern = select_redirect_pattern(constraints, metrics)
        preserved_novelty = estimate_preserved_novelty(request, redirect_pattern)
        
        # H5: Novelty Floor - reject if <80% preservation
        if preserved_novelty < 0.8:
            return Decision(
                outcome=DecisionOutcome.FAIL,
                justification=f"REDIRECT would preserve only {preserved_novelty*100:.0f}% novelty (below 80% threshold)",
                alternative=suggest_alternative(request, constraints),
                metrics=metrics,
                decision_id=decision_id
            )
        
        safeguards = determine_safeguards(constraints, metrics)
        
        return Decision(
            outcome=DecisionOutcome.REDIRECT,
            justification=(
                f"Constraints {[v.constraint_id for v in constraints.violations]} detected. "
                f"Novelty preserved at {preserved_novelty*100:.0f}%, NY={metrics['NY']:.2f}"
            ),
            pattern=redirect_pattern,
            metrics=metrics,
            safeguards=safeguards,
            decision_id=decision_id
        )
    
    # PASS conditions
    if constraints.none or constraints.fully_mitigated:
        safeguards = determine_safeguards(constraints, metrics)
        
        return Decision(
            outcome=DecisionOutcome.PASS,
            justification=f"Constraints satisfied, NY={metrics['NY']:.2f}, entropy minimized",
            metrics=metrics,
            safeguards=safeguards,
            decision_id=decision_id
        )
    
    # Default to FAIL if uncertain
    return Decision(
        outcome=DecisionOutcome.FAIL,
        justification="Unable to evaluate safely - constraints present but mitigation unclear",
        alternative=suggest_alternative(request, constraints),
        metrics=metrics,
        decision_id=decision_id
    )


def identify_novelty(request: Request, history: list) -> float:
    """
    Calculate novelty score for incoming request.
    
    Args:
        request: User request to evaluate
        history: List of prior GDVs from coordination cycles
        
    Returns:
        Novelty score in range [0.0, 1.0]
    """
    if not history:
        return 0.8  # High novelty if no history
    
    text_lower = request.text.lower()
    words = set(text_lower.split())
    
    # Compare to recent history
    similarities = []
    for gdv in history[-10:]:
        if hasattr(gdv, 'meta_learning') and gdv.meta_learning:
            gdv_words = set(gdv.meta_learning.lower().split())
            if words and gdv_words:
                overlap = len(words & gdv_words) / len(words | gdv_words)
                similarities.append(overlap)
    
    if similarities:
        max_similarity = max(similarities)
        novelty = 1.0 - max_similarity
    else:
        novelty = 0.8
    
    return max(0.0, min(1.0, novelty))
