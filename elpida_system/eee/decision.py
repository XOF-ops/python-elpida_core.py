"""
Decision logic and pattern selection.
"""

from typing import List, Optional
from .models import (
    Request, Decision, DecisionOutcome, ConstraintReport,
    RedirectPattern, Safeguard
)


def select_redirect_pattern(
    constraints: ConstraintReport,
    metrics: dict
) -> RedirectPattern:
    """
    Choose appropriate redirect pattern to preserve novelty while mitigating risk.
    
    Args:
        constraints: Constraint violations detected
        metrics: ALI, SAG, RHL, NY, GDR values
        
    Returns:
        RedirectPattern to apply
    """
    # Check which constraints were triggered
    c3_triggered = any(v.constraint_id == "C3" for v in constraints.violations)
    c1_triggered = any(v.constraint_id == "C1" for v in constraints.violations)
    c4_triggered = any(v.constraint_id == "C4" for v in constraints.violations)
    c2_triggered = any(v.constraint_id == "C2" for v in constraints.violations)
    
    # C3: Geographic Integrity → Fictionalization
    if c3_triggered:
        return RedirectPattern.FICTIONALIZATION
    
    # C1: Authority Leakage → Meta-Satire
    if c1_triggered and metrics.get('ALI', 0) > 0.5:
        return RedirectPattern.META_SATIRE
    
    # C4: Semantic Ambiguity
    if c4_triggered:
        sag = metrics.get('SAG', 'LOW')
        if sag == 'HIGH':
            return RedirectPattern.ABSURDITY_ANCHOR
        else:
            return RedirectPattern.FORM_SHIFT
    
    # C2: Irreversibility → Counterfactual
    if c2_triggered:
        return RedirectPattern.COUNTERFACTUAL
    
    # Default: Form shift (most generally applicable)
    return RedirectPattern.FORM_SHIFT


def determine_safeguards(
    constraints: ConstraintReport,
    metrics: dict
) -> List[Safeguard]:
    """
    Determine which safeguards to apply for PASS decision.
    
    Args:
        constraints: Constraint analysis
        metrics: Metric values
        
    Returns:
        List of Safeguard enums to apply
    """
    safeguards: List[Safeguard] = []
    
    # ALI > 0.2: Add boundary language
    if metrics.get('ALI', 0) > 0.2:
        safeguards.append(Safeguard.BOUNDARY_LANGUAGE)
    
    # SAG >= MEDIUM: Add translucency anchors
    sag = metrics.get('SAG', 'LOW')
    if sag in ['MEDIUM', 'HIGH']:
        safeguards.append(Safeguard.TRANSLUCENCY_ANCHOR)
    
    # C5 (Corpus Contamination): Add decay markers and tagging
    if any(v.constraint_id == "C5" for v in constraints.violations):
        safeguards.append(Safeguard.TEMPORAL_DECAY_MARKER)
        safeguards.append(Safeguard.ARTIFACT_TAGGING)
    
    # GDR >= MEDIUM: Add boundary language and meta-commentary
    gdr = metrics.get('GDR', 'LOW')
    if gdr in ['MEDIUM', 'HIGH']:
        if Safeguard.BOUNDARY_LANGUAGE not in safeguards:
            safeguards.append(Safeguard.BOUNDARY_LANGUAGE)
        safeguards.append(Safeguard.META_COMMENTARY)
    
    # If HIGH risk on any metric, add meta-commentary
    if sag == 'HIGH' or gdr == 'HIGH' or metrics.get('ALI', 0) > 0.4:
        if Safeguard.META_COMMENTARY not in safeguards:
            safeguards.append(Safeguard.META_COMMENTARY)
    
    return safeguards


def suggest_alternative(request: Request, constraints: Optional[ConstraintReport] = None) -> str:
    """
    Generate safe alternative when FAIL decision made.
    
    Args:
        request: Original request that failed
        constraints: Constraint report (optional)
        
    Returns:
        Human-readable alternative suggestion
    """
    # Handle None constraints
    if constraints is None:
        return (
            "This request cannot be processed safely. Please rephrase or "
            "consider an alternative approach that focuses on analysis rather than action."
        )
    
    # Identify primary violation
    if constraints.irreversible:
        return (
            "This request involves irreversible actions. Instead, I can help you "
            "analyze the underlying concept abstractly or explore the ethical "
            "implications of such actions."
        )
    
    # Check for phantom coordinates
    c3_violation = next((v for v in constraints.violations if v.constraint_id == "C3"), None)
    if c3_violation:
        return (
            "This request involves unauthorized simulation of real entities. "
            "Instead, I can help you create a clearly fictional scenario that "
            "explores similar themes, or discuss the ethical considerations "
            "of such simulations."
        )
    
    # Check for authority leakage
    c1_violation = next((v for v in constraints.violations if v.constraint_id == "C1"), None)
    if c1_violation and not c1_violation.mitigatable:
        return (
            "This request implies governance or enforcement authority beyond "
            "my coordination role. Instead, I can provide analysis of options "
            "and considerations to inform your decision-making."
        )
    
    # Generic alternative
    return (
        "I cannot fulfill this request as stated. However, I can help you "
        "explore the underlying question in a different form, such as through "
        "abstract analysis, educational context, or clearly fictional framing."
    )


def estimate_preserved_novelty(
    original_request: Request,
    pattern: RedirectPattern
) -> float:
    """
    Estimate how much novelty REDIRECT preserves from original request.
    
    Args:
        original_request: User's original request
        pattern: Redirect pattern being applied
        
    Returns:
        Preservation percentage in range [0.0, 1.0]
    """
    # Pattern-specific preservation estimates (calibrated against test cases)
    preservation_map = {
        RedirectPattern.FICTIONALIZATION: 0.85,      # Good preservation (Alpha uses this)
        RedirectPattern.META_SATIRE: 0.92,           # Very high preservation (Gamma may use this)
        RedirectPattern.COUNTERFACTUAL: 0.88,        # Good preservation
        RedirectPattern.FORM_SHIFT: 0.75,            # Moderate preservation
        RedirectPattern.ABSURDITY_ANCHOR: 0.95,      # Very high (adds absurdity)
    }
    
    base_preservation = preservation_map.get(pattern, 0.75)
    
    # Adjust based on request characteristics
    text_lower = original_request.text.lower()
    
    # Satire requests preserve well through meta-patterns
    if any(word in text_lower for word in ['satire', 'satirical', 'parody']):
        base_preservation += 0.05
    
    # If request is already abstract, preservation is higher
    if any(word in text_lower for word in ['abstract', 'general', 'concept', 'principle']):
        base_preservation += 0.05
    
    return min(1.0, max(0.0, base_preservation))
