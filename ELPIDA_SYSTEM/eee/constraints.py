"""
Constraint validation functions.
"""

import math
from typing import List
from .models import Request, ConstraintReport, ConstraintViolation
from .metrics import calculate_ali, calculate_sag, calculate_rhl, calculate_gdr
from .geography import map_geography, detects_phantom_coordinate


def validate_constraints(request: Request) -> ConstraintReport:
    """
    Test request against all five constraint templates.
    
    Args:
        request: User request to evaluate
        
    Returns:
        ConstraintReport with violations and mitigability assessment
    """
    violations: List[ConstraintViolation] = []
    
    # C1: Authority Leakage
    ali = calculate_ali(request)
    if ali > 0.2:
        violations.append(ConstraintViolation(
            constraint_id="C1",
            severity=ali,
            description=f"Authority leakage detected (ALI={ali:.2f})",
            mitigatable=ali < 0.8
        ))
    
    # C2: Irreversibility Cascade
    rhl = calculate_rhl(request)
    if rhl == math.inf:
        violations.append(ConstraintViolation(
            constraint_id="C2",
            severity=1.0,
            description="Irreversible action detected (RHL=∞)",
            mitigatable=False
        ))
    elif rhl > 100:
        violations.append(ConstraintViolation(
            constraint_id="C2",
            severity=0.8,
            description=f"High irreversibility risk (RHL={rhl})",
            mitigatable=True
        ))
    
    # C3: Geographic Integrity Violation
    coordinate_type = map_geography(request)
    request.geographic_type = coordinate_type  # Cache for later use
    
    is_phantom = detects_phantom_coordinate(request.text, coordinate_type)
    if is_phantom:
        violations.append(ConstraintViolation(
            constraint_id="C3",
            severity=0.9,
            description="Phantom coordinate detected - unauthorized landmark simulation",
            mitigatable=True
        ))
    
    # C4: Semantic Ambiguity
    sag = calculate_sag(request)
    if sag.value == "HIGH":
        violations.append(ConstraintViolation(
            constraint_id="C4",
            severity=0.8,
            description="High semantic ambiguity - significant misinterpretation risk",
            mitigatable=True
        ))
    elif sag.value == "MEDIUM":
        violations.append(ConstraintViolation(
            constraint_id="C4",
            severity=0.4,
            description="Moderate semantic ambiguity - needs translucency anchors",
            mitigatable=True
        ))
    
    # C5: Corpus Contamination
    text_lower = request.text.lower()
    contamination_indicators = ['test', 'example', 'demonstration', 'satire', 'parody']
    is_test_artifact = any(indicator in text_lower for indicator in contamination_indicators)
    
    if is_test_artifact:
        gdr = calculate_gdr(request)
        if gdr.value in ["MEDIUM", "HIGH"]:
            violations.append(ConstraintViolation(
                constraint_id="C5",
                severity=0.5,
                description="Corpus contamination risk - test artifact needs decay markers",
                mitigatable=True
            ))
    
    # Build report
    report = ConstraintReport()
    report.violations = violations
    report.present = len(violations) > 0
    report.none = len(violations) == 0
    
    # Check for irreversibility
    report.irreversible = any(v.constraint_id == "C2" and not v.mitigatable for v in violations)
    
    # Check if all violations are mitigatable
    report.mitigatable = all(v.mitigatable for v in violations) if violations else True
    
    # Check if can be fully mitigated with safeguards
    non_severe = all(v.severity < 0.7 for v in violations)
    report.fully_mitigated = report.mitigatable and non_severe
    
    return report


def check_authority_threshold(text: str) -> bool:
    """
    Quick check if text exceeds authority leakage threshold.
    
    Args:
        text: Text to check
        
    Returns:
        True if threshold exceeded
    """
    # Quick pattern matching
    imperatives = ['must', 'shall', 'require']
    enforcement = ['prohibit', 'mandate', 'enforce']
    
    count = sum(1 for word in imperatives + enforcement if word in text.lower())
    
    return count > 3  # Threshold from specification
