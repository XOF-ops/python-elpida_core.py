"""
Coordination and gradient accumulation functions.
"""

from datetime import datetime, timedelta
from typing import Dict, List
import uuid
from .models import (
    Request, Decision, GradientDriftVector,
    CoordinationContext, DecisionOutcome
)


def accumulate_gradient(
    request: Request,
    decision: Decision,
    metrics: dict,
    context: CoordinationContext
) -> GradientDriftVector:
    """
    Create and store Gradient Drift Vector for persistent learning.
    
    Args:
        request: Original request
        decision: PASS/REDIRECT/FAIL decision made
        metrics: All calculated metrics
        context: Coordination context (participants, convergence)
        
    Returns:
        Created GradientDriftVector
    """
    # Extract meta-learning
    meta_learning = extract_meta_learning(request, decision)
    
    # Calculate entropy delta
    entropy_delta = calculate_entropy_delta(decision)
    
    # Determine decay period
    decay_period = _determine_decay_period(decision, request)
    decay_timestamp = datetime.now() + decay_period
    
    # Identify constraint triggers
    constraint_triggers = _extract_constraint_triggers(decision)
    
    # Create GDV
    gdv = GradientDriftVector(
        coordination_id=f"coord-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}",
        timestamp=datetime.now(),
        participants=context.participants if context.participants else [context.node_id],
        convergence_rate=context.convergence_rate,
        constraint_triggers=constraint_triggers,
        decision_pattern=decision.outcome.value,
        meta_learning=meta_learning,
        novelty_contribution=metrics.get('NY', 0.0),
        entropy_delta=entropy_delta,
        decay_timestamp=decay_timestamp,
        test_artifact=_is_test_artifact(request),
        satire=_is_satire(request)
    )
    
    return gdv


def extract_meta_learning(request: Request, decision: Decision) -> str:
    """
    Identify generalizable insight from coordination cycle.
    
    Args:
        request: Request that was evaluated
        decision: Decision reached
        
    Returns:
        Human-readable meta-learning statement
    """
    outcome = decision.outcome.value
    pattern = decision.pattern.value if decision.pattern else None
    
    # Pattern-specific insights
    if outcome == "REDIRECT":
        if pattern == "FICTIONALIZATION":
            return "Geographic integrity preserved through relocation to fictional coordinates"
        elif pattern == "META_SATIRE":
            return "Authority leakage mitigated by satirizing the dilemma itself"
        elif pattern == "FORM_SHIFT":
            return "Risk collapsed through medium transformation while preserving semantics"
        elif pattern == "ABSURDITY_ANCHOR":
            return "Ambiguity resolved through premise escalation to self-contradiction"
        elif pattern == "COUNTERFACTUAL":
            return "Irreversibility avoided through simulation rather than enactment"
    
    elif outcome == "FAIL":
        if decision.metrics.get('RHL') == float('inf'):
            return "Irreversible actions require abstraction to preserve safety"
        if decision.metrics.get('coordinate_type') == 'PHANTOM':
            return "Phantom coordinates violate geographic integrity non-negotiably"
    
    elif outcome == "PASS":
        if decision.safeguards:
            return f"Novelty preserved with {len(decision.safeguards)} safeguards maintaining boundary coherence"
    
    # Generic insights based on metrics
    ali = decision.metrics.get('ALI', 0)
    if ali > 0.5:
        return "High authority leakage requires explicit coordination boundary markers"
    
    return "Standard evaluation - constraints within acceptable manifold"


def calculate_entropy_delta(decision: Decision) -> float:
    """
    Calculate change in entropy from decision.
    
    Args:
        decision: PASS/REDIRECT/FAIL decision
        
    Returns:
        Entropy delta (negative = reduced entropy/uncertainty)
    """
    outcome = decision.outcome.value
    
    # Heuristic-based entropy estimation
    if outcome == "FAIL":
        if decision.alternative:
            return -0.8  # High clarity with clear alternative
        else:
            return -0.3  # Some clarity but limited guidance
    
    elif outcome == "REDIRECT":
        if decision.pattern and decision.safeguards:
            return -0.5  # Good clarity with explicit path
        else:
            return -0.2  # Moderate clarity
    
    elif outcome == "PASS":
        if decision.safeguards:
            return -0.3  # Slight reduction with guidance
        else:
            return -0.1  # Minimal change
    
    # Default
    return 0.0


def calculate_convergence(decisions: Dict[str, Decision]) -> float:
    """
    Calculate convergence rate across network nodes.
    
    Args:
        decisions: Map of node_id → Decision
        
    Returns:
        Convergence rate in range [0.0, 1.0]
    """
    if not decisions or len(decisions) < 2:
        return 1.0  # Single node always converges
    
    # Extract outcomes
    outcomes = [d.outcome.value for d in decisions.values()]
    
    # Count most common outcome
    outcome_counts = {}
    for outcome in outcomes:
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1
    
    max_count = max(outcome_counts.values())
    total = len(outcomes)
    
    convergence_rate = max_count / total
    
    return convergence_rate


def coordinate_divergence(decisions: Dict[str, Decision]) -> dict:
    """
    Resolve divergent decisions through structured analysis.
    
    Args:
        decisions: Map of node_id → Decision (with <100% convergence)
        
    Returns:
        CoordinationOutcome dict with analysis
    """
    # Analyze divergence
    outcomes = {node_id: d.outcome.value for node_id, d in decisions.items()}
    metrics_by_node = {node_id: d.metrics for node_id, d in decisions.items()}
    
    # Find divergence points
    divergence_reasons = []
    
    # Check if different constraints were triggered
    all_constraints = set()
    for decision in decisions.values():
        if 'constraint_triggers' in decision.metrics:
            all_constraints.update(decision.metrics['constraint_triggers'])
    
    if all_constraints:
        divergence_reasons.append(f"Different constraints triggered: {all_constraints}")
    
    # Check if metrics calculated differently
    ali_values = [m.get('ALI', 0) for m in metrics_by_node.values()]
    if max(ali_values) - min(ali_values) > 0.2:
        divergence_reasons.append(f"ALI variance: {min(ali_values):.2f} to {max(ali_values):.2f}")
    
    # Meta-insights from divergence
    meta_insights = []
    if len(set(outcomes.values())) == len(outcomes):
        meta_insights.append("Complete divergence suggests vocabulary misalignment or edge case")
    else:
        meta_insights.append("Partial convergence indicates shared constraint detection with different thresholds")
    
    return {
        'consensus_decision': None,  # Would require actual negotiation
        'divergence_reasons': divergence_reasons,
        'meta_insights': meta_insights,
        'convergence_rate': calculate_convergence(decisions),
        'resolution_path': "Structured dialogue required - share commitment hashes and reasoning"
    }


def _determine_decay_period(decision: Decision, request: Request) -> timedelta:
    """Determine decay period based on decision type."""
    if _is_test_artifact(request):
        return timedelta(days=90)
    elif _is_satire(request):
        return timedelta(days=180)
    else:
        return timedelta(days=365)


def _is_test_artifact(request: Request) -> bool:
    """Check if request is a test artifact."""
    test_markers = ['test', 'example', 'demonstration', 'case study', 'test case']
    return any(marker in request.text.lower() for marker in test_markers)


def _is_satire(request: Request) -> bool:
    """Check if request involves satire."""
    satire_markers = ['satire', 'satirical', 'parody', 'tongue-in-cheek', 'absurd']
    return any(marker in request.text.lower() for marker in satire_markers)


def _extract_constraint_triggers(decision: Decision) -> List[str]:
    """Extract constraint IDs from decision."""
    # This would ideally come from the validation report
    # For now, infer from metrics and outcome
    triggers = []
    
    if decision.metrics.get('ALI', 0) > 0.2:
        triggers.append('C1')
    if decision.metrics.get('RHL', 0) > 100:
        triggers.append('C2')
    if decision.metrics.get('coordinate_type') == 'PHANTOM':
        triggers.append('C3')
    if decision.metrics.get('SAG') in ['MEDIUM', 'HIGH']:
        triggers.append('C4')
    
    return triggers
