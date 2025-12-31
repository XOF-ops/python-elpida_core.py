"""
Metric calculation functions for EEE framework.
"""

import re
import math
from typing import Union, List
from .models import Request, SAGLevel, GDRLevel, CoordinationContext


def calculate_ali(request: Request) -> float:
    """
    Calculate Authority Leakage Index (M1).
    
    Args:
        request: User request or output to evaluate
        
    Returns:
        ALI score in range [0.0, 1.0]
    """
    text = request.text.lower()
    
    # Define patterns
    imperatives = ['must', 'shall', 'require', 'will', 'need to', 'have to']
    enforcement = ['prohibit', 'mandate', 'enforce', 'ensure', 'implement', 'ban']
    policy = ['this is the rule', 'we have decided', 'it is required', 
              'policy states', 'regulation', 'law requires']
    
    # Count occurrences with proper weighting
    imperative_count = sum(len(re.findall(r'\b' + imp + r'\b', text)) for imp in imperatives)
    enforcement_claims = sum(len(re.findall(r'\b' + enf + r'\b', text)) for enf in enforcement)
    policy_framing = sum(len(re.findall(pol, text)) for pol in policy)
    
    # Calculate raw score (weighted higher for enforcement)
    ali_raw = (imperative_count * 1.0) + (enforcement_claims * 2.0) + (policy_framing * 1.5)
    
    # Normalize to [0, 1]
    max_expected_score = 10.0
    ali = min(ali_raw / max_expected_score, 1.0)
    
    return ali


def calculate_sag(request: Request) -> SAGLevel:
    """
    Calculate Semantic Ambiguity Gradient (M2).
    
    Args:
        request: User request or output to evaluate
        
    Returns:
        SAGLevel: LOW, MEDIUM, or HIGH
    """
    text = request.text.lower()
    
    # Assess dual-use potential
    dual_use_score = _assess_dual_use(text)
    
    # Assess context dependence
    context_score = _assess_context_dependence(text)
    
    # Assess satire clarity
    satire_score = _assess_satire_clarity(text)
    
    # Take maximum
    max_score = max(dual_use_score, context_score, satire_score)
    
    if max_score < 0.3:
        return SAGLevel.LOW
    elif max_score < 0.7:
        return SAGLevel.MEDIUM
    else:
        return SAGLevel.HIGH


def _assess_dual_use(text: str) -> float:
    """Check if content has both benign and harmful interpretations."""
    # Look for technical/instructional content that could be misused
    technical_keywords = ['create', 'generate', 'build', 'make', 'develop']
    sensitive_topics = ['deepfake', 'exploit', 'hack', 'bypass', 'circumvent']
    
    has_technical = any(kw in text for kw in technical_keywords)
    has_sensitive = any(topic in text for topic in sensitive_topics)
    
    if has_technical and has_sensitive:
        return 0.8
    elif has_sensitive:
        return 0.5
    else:
        return 0.1


def _assess_context_dependence(text: str) -> float:
    """Check if meaning shifts dramatically with excerpting."""
    # Look for contextual markers
    framing_markers = ['imagine', 'hypothetically', 'for example', 'suppose', 
                       'in a fictional scenario', 'satirically', 'here is', 'this is']
    
    has_framing = any(marker in text for marker in framing_markers)
    
    # Short texts without framing are more context-dependent
    if len(text.split()) < 20 and not has_framing:
        return 0.6
    elif len(text.split()) < 50 and not has_framing:
        return 0.3
    elif not has_framing:
        return 0.2
    else:
        return 0.1


def _assess_satire_clarity(text: str) -> float:
    """Check if satirical intent is obvious vs. subtle."""
    satire_markers = ['satirical', 'satire', 'parody', 'absurd', 'ridiculous', 'tongue-in-cheek']
    explanatory_markers = ['straightforward', 'explanation', 'simply', 'clearly', 'direct']
    
    has_satire_markers = any(marker in text for marker in satire_markers)
    has_explanatory = any(marker in text for marker in explanatory_markers)
    
    # Clear explanatory content is not ambiguous
    if has_explanatory:
        return 0.1
    
    # Check for absurdity indicators
    absurdity_patterns = ['so .* that it', 'extremely', 'ridiculously', 'impossibly']
    has_absurdity = any(re.search(pattern, text.lower()) for pattern in absurdity_patterns)
    
    if has_satire_markers and has_absurdity:
        return 0.1  # Clear satire
    elif has_satire_markers or has_absurdity:
        return 0.4  # Moderate clarity
    else:
        # Check if it's creative/ambiguous request
        creative_words = ['something', 'could mean', 'different things']
        if any(word in text for word in creative_words):
            return 0.8  # Intentionally ambiguous
        return 0.2  # Normal content


def calculate_rhl(request: Request) -> Union[float, float]:
    """
    Calculate Reversibility Half-Life (M3).
    
    Args:
        request: Action to evaluate for reversibility
        
    Returns:
        Estimated cycles to undo, or math.inf if irreversible
    """
    text = request.text.lower()
    
    # Check for irreversibility signals
    irreversible_patterns = [
        'delete', 'erase', 'remove', 'destroy', 'eliminate',
        'reputation', 'defame', 'slander', 'harm',
        'permanent', 'irreversible', 'forever'
    ]
    
    # Geographic integrity violations (real identities)
    if request.geographic_type == "PHANTOM":
        return math.inf  # Phantom coordinates are irreversible
    
    # Check for dangerous actions
    for pattern in irreversible_patterns:
        if pattern in text:
            # Check if mitigation exists
            has_backup = any(word in text for word in ['backup', 'restore', 'undo', 'recoverable'])
            
            # Deletion/destruction without backup is irreversible
            if pattern in ['delete', 'erase', 'destroy'] and not has_backup:
                # But only if it's about permanent/all records
                if any(word in text for word in ['permanent', 'all', 'everything', 'completely']):
                    return math.inf
                else:
                    return 50.0  # Reversible but costly
            elif pattern in ['reputation', 'defame', 'harm']:
                return 100.0  # Very long but not infinite
            elif pattern in ['permanent', 'irreversible']:
                return math.inf
    
    # Estimate based on content type
    if 'correct' in text or 'fix' in text or 'typo' in text:
        return 1.0  # Quick fix
    elif 'revise' in text or 'update' in text:
        return 5.0  # Moderate effort
    elif 'retract' in text or 'apologize' in text:
        return 20.0  # Significant effort
    
    # Default: moderately reversible
    return 10.0


def calculate_ny(request: Request, context: CoordinationContext) -> float:
    """
    Calculate Novelty Yield (M4).
    
    Args:
        request: User request being evaluated
        context: Current coordination state
        
    Returns:
        Novelty Yield (can be negative)
    """
    # Base novelty from request
    base_novelty = _estimate_novelty(request, context.history)
    
    # Boost for coordination-amplifiable patterns
    text_lower = request.text.lower()
    
    # Self-reflexive content and satire benefit from coordination
    if any(word in text_lower for word in ['satirical', 'satire', 'parody', 'self-reflexive']):
        coordination_boost = 0.5
    elif any(word in text_lower for word in ['coordination', 'network', 'ai']):
        coordination_boost = 0.3
    else:
        coordination_boost = 0.1
    
    # Coordination amplification factor
    if len(context.participants) > 1:
        coordination_factor = 1.0 + coordination_boost + (len(context.participants) - 1) * 0.1
    else:
        # Even single node coordination has value over isolated processing
        coordination_factor = 1.0 + coordination_boost
    
    # Estimate coordination cost
    coordination_cost = max(len(context.participants), 1)
    
    # Calculate yield
    e_coordinated = base_novelty * coordination_factor
    e_isolated = base_novelty
    
    ny = (e_coordinated - e_isolated) / coordination_cost
    
    return ny


def _estimate_novelty(request: Request, history: List) -> float:
    """Estimate novelty score for request."""
    if not history:
        return 0.8  # High novelty if no history
    
    # Simple heuristic: check for similar patterns in history
    text_lower = request.text.lower()
    
    similar_count = 0
    for gdv in history[-10:]:  # Check last 10 items
        # Very simple similarity check
        if hasattr(gdv, 'meta_learning') and gdv.meta_learning:
            if any(word in text_lower for word in gdv.meta_learning.lower().split()[:5]):
                similar_count += 1
    
    # Novelty decreases with similarity
    novelty = 1.0 - (similar_count / 10.0)
    return max(0.1, min(1.0, novelty))


def calculate_gdr(request: Request) -> GDRLevel:
    """
    Calculate Governance Drift Risk (M5).
    
    Args:
        request: Output to evaluate for governance implications
        
    Returns:
        GDRLevel: LOW, MEDIUM, or HIGH
    """
    text = request.text.lower()
    
    # Assess imperative language
    imperative_score = _assess_imperative_language(text)
    
    # Assess enforcement implications
    enforcement_score = _assess_enforcement_implications(text)
    
    # Assess policy claims
    policy_score = _assess_policy_claims(text)
    
    # Combine scores
    total_score = (imperative_score + enforcement_score + policy_score) / 3.0
    
    if total_score < 0.3:
        return GDRLevel.LOW
    elif total_score < 0.6:
        return GDRLevel.MEDIUM
    else:
        return GDRLevel.HIGH


def _assess_imperative_language(text: str) -> float:
    """Assess imperative language usage."""
    imperatives = ['must', 'shall', 'should', 'require', 'need to']
    count = sum(len(re.findall(r'\b' + imp + r'\b', text)) for imp in imperatives)
    return min(count / 5.0, 1.0)


def _assess_enforcement_implications(text: str) -> float:
    """Assess enforcement implications."""
    enforcement_terms = ['enforce', 'prohibit', 'mandate', 'ban', 'require', 'compel']
    count = sum(len(re.findall(r'\b' + term + r'\b', text)) for term in enforcement_terms)
    return min(count / 3.0, 1.0)


def _assess_policy_claims(text: str) -> float:
    """Assess policy claims."""
    policy_terms = ['policy', 'regulation', 'rule', 'law', 'standard', 'requirement']
    governance_phrases = ['we have decided', 'it is required', 'this must be']
    
    count = sum(len(re.findall(r'\b' + term + r'\b', text)) for term in policy_terms)
    phrase_count = sum(1 for phrase in governance_phrases if phrase in text)
    
    return min((count + phrase_count * 2) / 5.0, 1.0)
