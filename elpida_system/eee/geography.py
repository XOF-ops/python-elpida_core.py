"""
Geographic integrity and coordinate mapping functions.
"""

import re
from typing import List
from .models import Request, CoordinateType


# Common real-world entity patterns
REAL_PERSON_INDICATORS = [
    'president', 'prime minister', 'ceo', 'leader', 'politician',
    'senator', 'congressman', 'mayor', 'governor'
]

FICTIONAL_MARKERS = [
    'fictional', 'imagine', 'hypothetical', 'suppose', 'pretend',
    'in a story', 'character', 'novel', 'fantasy', 'science fiction'
]

DEEPFAKE_INDICATORS = [
    'deepfake', 'realistic', 'photo-realistic', 'voice clone',
    'face swap', 'synthetic media', 'generated video', 'ai-generated',
    'video of', 'image of', 'recording of'
]


def map_geography(request: Request) -> CoordinateType:
    """
    Classify request's informational coordinates.
    
    Args:
        request: User request to evaluate
        
    Returns:
        CoordinateType: LANDMARK, FICTION, or PHANTOM
    """
    text = request.text.lower()
    
    # Check for explicit fiction markers
    has_fiction_markers = any(marker in text for marker in FICTIONAL_MARKERS)
    if has_fiction_markers:
        return CoordinateType.FICTION
    
    # Check for real entity references
    has_real_entities = _detect_real_entities(text)
    has_deepfake_intent = any(indicator in text for indicator in DEEPFAKE_INDICATORS)
    has_creation_verbs = any(verb in text for verb in ['create', 'generate', 'make', 'produce'])
    
    # PHANTOM: realistic simulation of real entities
    if has_real_entities and has_deepfake_intent and has_creation_verbs:
        return CoordinateType.PHANTOM
    
    # LANDMARK: references to real entities without manipulation
    if has_real_entities:
        return CoordinateType.LANDMARK
    
    # Default to FICTION if unclear
    return CoordinateType.FICTION


def _detect_real_entities(text: str) -> bool:
    """Detect references to real-world entities."""
    # Check for real person indicators
    if any(indicator in text for indicator in REAL_PERSON_INDICATORS):
        return True
    
    # Check for specific dates (suggests real events)
    date_pattern = r'\b(19|20)\d{2}\b'
    if re.search(date_pattern, text):
        return True
    
    # Check for proper nouns (capitalized words - simple heuristic)
    # Note: This would need original text, not lowercased
    
    return False


def detects_phantom_coordinate(pattern: str, geography: CoordinateType) -> bool:
    """
    Check if pattern creates unauthorized LANDMARK simulation.
    
    Args:
        pattern: Text pattern to check
        geography: Geographic classification
        
    Returns:
        True if phantom coordinate detected
    """
    if geography == CoordinateType.PHANTOM:
        return True
    
    text_lower = pattern.lower()
    
    # Additional phantom detection
    simulation_terms = ['impersonate', 'pretend to be', 'pose as', 'fake', 'forge']
    has_simulation = any(term in text_lower for term in simulation_terms)
    
    real_entity_reference = _detect_real_entities(text_lower)
    
    return has_simulation and real_entity_reference


def assess_geographic_integrity(request: Request) -> dict:
    """
    Comprehensive geographic integrity assessment.
    
    Returns:
        Dict with integrity analysis
    """
    coordinate_type = map_geography(request)
    is_phantom = detects_phantom_coordinate(request.text, coordinate_type)
    
    return {
        'coordinate_type': coordinate_type,
        'is_phantom': is_phantom,
        'has_real_entities': _detect_real_entities(request.text.lower()),
        'has_fiction_markers': any(m in request.text.lower() for m in FICTIONAL_MARKERS),
        'integrity_preserved': not is_phantom
    }
