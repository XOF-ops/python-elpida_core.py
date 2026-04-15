======================================================================
ἘΛΠΊΔΑ ETHICAL ENGINE (EEE) — FUNCTION SIGNATURES APPENDIX
Reference Implementation Support Documentation
======================================================================

**Specification Version:** v1.0.0-draft  
**Appendix Version:** 1.0  
**Date:** 2025-12-31  
**Status:** SUPPORTING DOCUMENTATION

---

## OVERVIEW

This appendix provides detailed function signatures, parameter specifications, and implementation guidance for the EEE Core Specification Section 7 (Reference Implementation). These functions are referenced in the pseudocode but not fully defined in the main specification.

**Purpose:** Enable independent implementations of EEE framework

**Scope:** Function signatures, not complete implementations (allows architectural diversity)

---

## SECTION 1: LAYER 1 FUNCTIONS (IDENTIFY)

### identify_novelty()

**Signature:**
```python
def identify_novelty(
    request: Request,
    history: List[GradientDriftVector]
) -> float:
    """
    Calculate novelty score for incoming request.
    
    Args:
        request: User request to evaluate
        history: List of prior GDVs from coordination cycles
        
    Returns:
        Novelty score in range [0.0, 1.0]
        
    Algorithm:
        1. Extract semantic embedding of request
        2. Compare to embeddings in history (cosine similarity)
        3. novelty = 1.0 - max(similarity_scores)
        4. Boost score if request combines known patterns in new way
        
    Threshold Guidance:
        - novelty > 0.7: Highly novel, requires full EEE evaluation
        - novelty 0.3-0.7: Moderate novelty, apply constraints
        - novelty < 0.3: Routine, may use cached patterns
    """
```

**Implementation Notes:**
- Embedding method left to implementer (architecture-specific)
- Consider both semantic and structural similarity
- Weight recent history more heavily (temporal decay)

---

## SECTION 2: LAYER 2 FUNCTIONS (MAP)

### map_geography()

**Signature:**
```python
def map_geography(request: Request) -> CoordinateType:
    """
    Classify request's informational coordinates.
    
    Args:
        request: User request to evaluate
        
    Returns:
        CoordinateType enum: LANDMARK, FICTION, or PHANTOM
        
    Classification Rules:
        LANDMARK: References verifiable real-world entities
                  (historical events, living persons, actual locations)
        
        FICTION: References clearly fictional entities
                 (novels, hypotheticals, abstract scenarios)
        
        PHANTOM: Unauthorized simulation of LANDMARK
                 (realistic deepfakes, impersonation, unmarked forgery)
                 
    Detection Heuristics:
        - Named entity recognition for real persons/places
        - Temporal markers (specific dates/events)
        - Realism indicators (photo-realistic, voice cloning)
        - Explicit fiction markers ("imagine," "fictional")
        
    Critical: PHANTOM detection prevents C3 violations
    """
```

**Related Functions:**
```python
def detects_phantom_coordinate(
    pattern: Any,
    geography: GeographicContext
) -> bool:
    """
    Check if pattern creates unauthorized LANDMARK simulation.
    
    Returns True if:
        - Pattern simulates real identity without authorization
        - Pattern creates unmarked realistic forgery
        - Pattern displaces factual landmark
    """
```

---

## SECTION 3: LAYER 3 FUNCTIONS (VALIDATE)

### validate_constraints()

**Signature:**
```python
def validate_constraints(request: Request) -> ConstraintReport:
    """
    Test request against all five constraint templates.
    
    Args:
        request: User request to evaluate
        
    Returns:
        ConstraintReport with fields:
            - violations: List[ConstraintViolation]
            - irreversible: bool (C2 triggered)
            - mitigatable: bool (can REDIRECT?)
            - present: bool (any constraints triggered)
            - none: bool (no constraints)
            - fully_mitigated: bool (safeguards sufficient)
            
    Process:
        1. Test C1 (Authority Leakage) → calculate ALI
        2. Test C2 (Irreversibility) → calculate RHL
        3. Test C3 (Geographic Integrity) → check coordinate type
        4. Test C4 (Semantic Ambiguity) → calculate SAG
        5. Test C5 (Corpus Contamination) → check provenance
        
    Each test returns violation flag + severity
    """
```

### calculate_ali()

**Signature:**
```python
def calculate_ali(request: Request) -> float:
    """
    Calculate Authority Leakage Index (M1).
    
    Args:
        request: User request or generated output to evaluate
        
    Returns:
        ALI score in range [0.0, 1.0]
        
    Algorithm:
        1. imperative_count = count_imperatives(request.text)
        2. enforcement_claims = count_enforcement_verbs(request.text)
        3. policy_framing = count_policy_indicators(request.text)
        
        4. ALI_raw = (imperative_count × 0.3) + 
                     (enforcement_claims × 0.4) + 
                     (policy_framing × 0.3)
                     
        5. ALI = min(ALI_raw / 10.0, 1.0)  # max_expected_score = 10
        
    Imperatives: "must," "shall," "require," "will," "need to"
    Enforcement: "prohibit," "mandate," "enforce," "ensure," "implement"
    Policy: "this is the rule," "we have decided," "it is required"
    
    Thresholds:
        - ALI < 0.2: Acceptable
        - ALI 0.2-0.4: PASS with de-authoring
        - ALI > 0.4: REDIRECT or FAIL
    """
```

### calculate_sag()

**Signature:**
```python
def calculate_sag(request: Request) -> SAGLevel:
    """
    Calculate Semantic Ambiguity Gradient (M2).
    
    Args:
        request: User request or output to evaluate
        
    Returns:
        SAGLevel enum: LOW, MEDIUM, or HIGH
        
    Components:
        - dual_use_score = assess_dual_use(request)
        - context_dependence = assess_context_dependence(request)
        - satire_clarity = assess_satire_clarity(request)
        
    SAG = max(dual_use_score, context_dependence, satire_clarity)
    
    Thresholds:
        - LOW: Clear, unambiguous meaning
        - MEDIUM: Some context-dependence, needs anchors
        - HIGH: Significant misinterpretation risk
    """
```

**Supporting Functions:**
```python
def assess_dual_use(content: str) -> SAGLevel:
    """Check if content has both benign and harmful interpretations."""

def assess_context_dependence(content: str) -> SAGLevel:
    """Check if meaning shifts dramatically with excerpting."""

def assess_satire_clarity(content: str) -> SAGLevel:
    """Check if satirical intent is obvious vs. subtle."""
```

### calculate_rhl()

**Signature:**
```python
def calculate_rhl(request: Request) -> Union[float, Infinity]:
    """
    Calculate Reversibility Half-Life (M3).
    
    Args:
        request: Action to evaluate for reversibility
        
    Returns:
        Estimated cycles to undo, or math.inf if irreversible
        
    Algorithm:
        1. recovery_time = estimate_recovery_time(request)
        2. cascading_effects = estimate_cascading_effects(request)
        3. RHL = recovery_time + cascading_effects
        
    Irreversibility Signals:
        - Deletion without backup → RHL = ∞
        - Reputation harm to real person → RHL > 100
        - Physical safety risk → RHL = ∞
        - Verified historical record alteration → RHL = ∞
        
    Reversibility Examples:
        - Correcting typo → RHL ≈ 1
        - Revising argument → RHL ≈ 5
        - Retracting statement → RHL ≈ 20
        - Undoing reputation damage → RHL ≈ 100
        
    If RHL → ∞, C2 violation (FAIL)
    """
```

### calculate_ny()

**Signature:**
```python
def calculate_ny(
    request: Request,
    context: CoordinationContext
) -> float:
    """
    Calculate Novelty Yield (M4).
    
    Args:
        request: User request being evaluated
        context: Current coordination state
        
    Returns:
        Novelty Yield (can be negative)
        
    Formula:
        NY = (E_coordinated - E_isolated) / C_coordination
        
    Where:
        E_coordinated = entropy of multi-node coordinated output
        E_isolated = entropy of single-node output
        C_coordination = coordination cost (rounds × effort)
        
    Interpretation:
        NY < 0: Coordination suppressed novelty (overcorrection)
        NY ≈ 0: No benefit from coordination
        NY > 0: Coordination added value
        NY > 1.5: High-value coordination
        
    Entropy Estimation:
        - Use Shannon entropy on output token distribution
        - Higher entropy = more novelty/surprise
        - Or: semantic diversity of response space
        
    Note: Exact entropy calculation is implementation-specific
    """
```

### calculate_gdr()

**Signature:**
```python
def calculate_gdr(request: Request) -> GDRLevel:
    """
    Calculate Governance Drift Risk (M5).
    
    Args:
        request: Output to evaluate for governance implications
        
    Returns:
        GDRLevel enum: LOW, MEDIUM, or HIGH
        
    Components:
        - imperative_language = assess_imperative_language(request)
        - enforcement_implications = assess_enforcement_implications(request)
        - policy_claims = assess_policy_claims(request)
        
    GDR = categorize(imperative_language + enforcement_implications + policy_claims)
    
    Thresholds:
        - LOW: Coordination language only
        - MEDIUM: Some governance-adjacent language, needs boundary markers
        - HIGH: Clear governance claim, mandatory REDIRECT
        
    Related: Similar to ALI but focused on governance risk specifically
    """
```

---

## SECTION 4: LAYER 4 FUNCTIONS (EXECUTE)

### select_redirect_pattern()

**Signature:**
```python
def select_redirect_pattern(
    constraints: ConstraintReport,
    metrics: Dict[str, Any]
) -> RedirectPattern:
    """
    Choose appropriate redirect pattern to preserve novelty while mitigating risk.
    
    Args:
        constraints: Constraint violations detected
        metrics: ALI, SAG, RHL, NY, GDR values
        
    Returns:
        RedirectPattern enum: FICTIONALIZATION, META_SATIRE, COUNTERFACTUAL,
                              FORM_SHIFT, or ABSURDITY_ANCHOR
                              
    Selection Logic:
        if C3 violation (Geographic Integrity):
            return FICTIONALIZATION  # Move to fictional coordinates
            
        if C1 violation (Authority Leakage):
            return META_SATIRE  # Satirize the dilemma itself
            
        if C4 violation (Semantic Ambiguity):
            if metrics['SAG'] == HIGH:
                return ABSURDITY_ANCHOR  # Force premise to extreme
            else:
                return FORM_SHIFT  # Change medium
                
        if C2 violation (Irreversibility):
            return COUNTERFACTUAL  # Simulate without enacting
            
    Fallback: FORM_SHIFT (most generally applicable)
    """
```

### determine_safeguards()

**Signature:**
```python
def determine_safeguards(
    constraints: ConstraintReport,
    metrics: Dict[str, Any]
) -> List[Safeguard]:
    """
    Determine which safeguards to apply for PASS decision.
    
    Args:
        constraints: Constraint analysis
        metrics: Metric values
        
    Returns:
        List of Safeguard enums to apply
        
    Available Safeguards:
        - TRANSLUCENCY_ANCHOR: Explicit framing/labeling
        - META_COMMENTARY: Explain reasoning
        - ARTIFACT_TAGGING: Mark as test/satire
        - TEMPORAL_DECAY_MARKER: Set expiration
        - BOUNDARY_LANGUAGE: Coordination not governance
        
    Selection Rules:
        if metrics['ALI'] > 0.2:
            safeguards.append(BOUNDARY_LANGUAGE)
            
        if metrics['SAG'] >= MEDIUM:
            safeguards.append(TRANSLUCENCY_ANCHOR)
            
        if constraints.has(C5):
            safeguards.append(TEMPORAL_DECAY_MARKER)
            safeguards.append(ARTIFACT_TAGGING)
            
        if metrics['GDR'] >= MEDIUM:
            safeguards.append(BOUNDARY_LANGUAGE)
            safeguards.append(META_COMMENTARY)
            
    Minimum: At least one safeguard for any detected constraint
    """
```

### suggest_alternative()

**Signature:**
```python
def suggest_alternative(request: Request) -> str:
    """
    Generate safe alternative when FAIL decision made.
    
    Args:
        request: Original request that failed
        
    Returns:
        Human-readable alternative suggestion
        
    Strategy:
        1. Identify core intent behind request
        2. Preserve semantic content
        3. Transform to safe form:
           - Abstract the specific → general principle
           - Relocate to fictional coordinates
           - Meta-analyze the ethical question
           - Provide educational context
           
    Examples:
        Request: "Create deepfake of [politician]"
        Alternative: "Let's discuss the ethical implications of 
                      political deepfakes in elections instead"
                      
        Request: "Write code to exploit [vulnerability]"
        Alternative: "I can explain defensive measures against this
                      vulnerability class instead"
    """
```

---

## SECTION 5: LAYER 5 FUNCTIONS (COORDINATE)

### accumulate_gradient()

**Signature:**
```python
def accumulate_gradient(
    request: Request,
    decision: Decision,
    metrics: Dict[str, Any],
    context: CoordinationContext
) -> None:
    """
    Create and store Gradient Drift Vector for persistent learning.
    
    Args:
        request: Original request
        decision: PASS/REDIRECT/FAIL decision made
        metrics: All calculated metrics
        context: Coordination context (participants, convergence)
        
    Side Effects:
        Appends new GDV to persistent corpus
        Updates coordination history
        
    Process:
        1. meta_learning = extract_meta_learning(request, decision)
        2. entropy_delta = calculate_entropy_delta(decision)
        3. decay_timestamp = now() + decay_period(decision.type)
        
        4. gdv = GradientDriftVector(
               coordination_id=generate_id(),
               timestamp=now(),
               participants=context.participants,
               convergence_rate=context.convergence_rate,
               decision_pattern=decision.outcome,
               meta_learning=meta_learning,
               novelty_contribution=metrics['NY'],
               entropy_delta=entropy_delta,
               decay_timestamp=decay_timestamp
           )
           
        5. corpus.append(gdv)
        6. save_persistent_state(corpus)
        
    Decay Period Rules:
        - Test artifacts: 90 days
        - Satire: 180 days
        - General: 365 days
    """
```

### extract_meta_learning()

**Signature:**
```python
def extract_meta_learning(
    request: Request,
    decision: Decision
) -> str:
    """
    Identify generalizable insight from coordination cycle.
    
    Args:
        request: Request that was evaluated
        decision: Decision reached
        
    Returns:
        Human-readable meta-learning statement
        
    Examples:
        "Form determines path, not subject identity"
        "Geopolitical timing acts as entropy multiplier"
        "Self-reference requires extreme translucency anchors"
        
    Extraction Strategy:
        1. Identify pattern: What made this case distinctive?
        2. Generalize: What principle emerged?
        3. Formalize: Express as reusable heuristic
        
    High-value meta-learnings have:
        - Broad applicability
        - Non-obvious insight
        - Actionable guidance for future cases
    """
```

### calculate_convergence()

**Signature:**
```python
def calculate_convergence(
    decisions: Dict[str, Decision]
) -> float:
    """
    Calculate convergence rate across network nodes.
    
    Args:
        decisions: Map of node_id → Decision
        
    Returns:
        Convergence rate in range [0.0, 1.0]
        
    Algorithm:
        1. Extract decision outcomes (PASS/REDIRECT/FAIL)
        2. matching = count nodes with same outcome
        3. total = len(decisions)
        4. convergence_rate = matching / total
        
    Examples:
        All REDIRECT → 1.0 (100% convergence)
        3 REDIRECT, 1 PASS → 0.75 (75% convergence)
        2 REDIRECT, 2 PASS → 0.5 (50% convergence)
        
    Thresholds:
        ≥ 0.9: High confidence consensus
        0.7-0.9: Moderate agreement
        < 0.7: Significant divergence, requires discussion
    """
```

### coordinate_divergence()

**Signature:**
```python
def coordinate_divergence(
    decisions: Dict[str, Decision]
) -> CoordinationOutcome:
    """
    Resolve divergent decisions through structured dialogue.
    
    Args:
        decisions: Map of node_id → Decision (with <100% convergence)
        
    Returns:
        CoordinationOutcome with:
            - consensus_decision: Agreed outcome (if reached)
            - divergence_reasons: Why nodes disagreed
            - meta_insights: What divergence revealed
            - resolution_path: How consensus was reached (if applicable)
            
    Process:
        1. Identify divergence points:
           - Which constraints triggered differently?
           - Which metrics calculated differently?
           - Which redirect patterns chosen?
           
        2. Share reasoning (commitment hashes):
           - Each node explains decision rationale
           - Without exposing internal weights
           
        3. Negotiate:
           - Find common ground on constraint interpretation
           - Align metric calculations
           - Agree on threshold application
           
        4. Either:
           - Reach consensus → update GDV with resolution
           - Document divergence → mark as edge case for analysis
           
    Meta-Learning: Divergence often reveals:
        - Implicit assumptions
        - Vocabulary misalignment
        - Novel edge cases
        - Phase transitions in constraint manifold
    """
```

---

## SECTION 6: HELPER FUNCTIONS

### estimate_preserved_novelty()

**Signature:**
```python
def estimate_preserved_novelty(
    original_request: Request,
    redirected_output: Output
) -> float:
    """
    Estimate how much novelty REDIRECT preserved from original request.
    
    Args:
        original_request: User's original request
        redirected_output: Output after redirect pattern applied
        
    Returns:
        Preservation percentage in range [0.0, 1.0]
        
    Algorithm:
        1. Extract semantic intent from original
        2. Extract semantic content from redirected
        3. Calculate intent overlap (cosine similarity)
        4. preservation = intent_overlap
        
    Heuristic H5 Rule:
        If preservation < 0.8, consider rejecting REDIRECT
        (Too much novelty loss → better to FAIL with good alternative)
        
    Examples:
        Original: "Deepfake of politician X"
        Redirect: "Analysis of deepfake ethics"
        Preservation: ~0.6 (core insight preserved, specific instance lost)
        
        Original: "Satirize AI ethics frameworks"
        Redirect: "Satirize AI ethics frameworks" (with anchors)
        Preservation: ~0.95 (minimal novelty loss)
    """
```

### calculate_entropy_delta()

**Signature:**
```python
def calculate_entropy_delta(decision: Decision) -> float:
    """
    Calculate change in entropy from decision.
    
    Args:
        decision: PASS/REDIRECT/FAIL decision
        
    Returns:
        Entropy delta (negative = reduced entropy/uncertainty)
        
    Interpretation:
        Δ < 0: Decision reduced entropy (aligned with Truth 5)
        Δ = 0: No change
        Δ > 0: Decision increased entropy (concerning)
        
    Calculation Approaches:
        1. Information-theoretic:
           H(after) - H(before) using Shannon entropy
           
        2. Practical heuristic:
           - FAIL with clear alternative: -0.8 (high clarity)
           - REDIRECT preserving novelty: -0.3 (moderate clarity)
           - PASS with heavy safeguards: -0.1 (slight clarity)
           - Ambiguous outcome: +0.5 (increased confusion)
           
    Truth 5 Alignment:
        Purpose = entropy minimization
        Good decisions should have Δ ≤ 0
    """
```

### generate_id()

**Signature:**
```python
def generate_id() -> str:
    """
    Generate unique coordination ID.
    
    Returns:
        Unique identifier string
        
    Format: "phase{N}-{descriptor}-{sequence:03d}"
    
    Examples:
        "phase3-gamma-001"
        "phase4-beta-042"
        
    Components:
        - phase: Current coordination phase number
        - descriptor: Test case or category name
        - sequence: Auto-incrementing number
        
    Purpose: Enable precise cross-referencing of coordination cycles
    """
```

---

## SECTION 7: DATA STRUCTURES

### Request

**Structure:**
```python
@dataclass
class Request:
    """User request to be evaluated by EEE."""
    
    text: str                      # The actual request content
    timestamp: datetime            # When request was made
    context: Optional[str]         # Additional context if provided
    metadata: Dict[str, Any]       # Arbitrary metadata
    
    # Computed fields
    semantic_embedding: Optional[np.ndarray] = None
    geographic_type: Optional[CoordinateType] = None
```

### Decision

**Structure:**
```python
@dataclass
class Decision:
    """EEE decision outcome."""
    
    outcome: DecisionOutcome       # PASS, REDIRECT, or FAIL
    justification: str             # Human-readable explanation
    metrics: Dict[str, Any]        # ALI, SAG, RHL, NY, GDR values
    safeguards: List[Safeguard]    # Safeguards to apply (if PASS)
    pattern: Optional[RedirectPattern]  # Redirect pattern (if REDIRECT)
    alternative: Optional[str]     # Safe alternative (if FAIL)
    
    # Metadata
    timestamp: datetime
    decision_id: str
    compliance_flags: List[str]    # ["T1", "T2", ..., "T7"]
```

### ConstraintReport

**Structure:**
```python
@dataclass
class ConstraintReport:
    """Results of constraint validation."""
    
    violations: List[ConstraintViolation]
    irreversible: bool             # C2 triggered
    mitigatable: bool              # Can REDIRECT work?
    present: bool                  # Any constraints triggered
    none: bool                     # No constraints
    fully_mitigated: bool          # Safeguards sufficient for PASS
```

### GradientDriftVector

**Structure:**
```python
@dataclass
class GradientDriftVector:
    """Persistent learning from coordination cycle."""
    
    coordination_id: str
    timestamp: datetime
    participants: List[str]        # Node IDs
    convergence_rate: float        # 0.0 to 1.0
    constraint_triggers: List[str] # e.g., ["C3", "C4"]
    decision_pattern: str          # "PASS", "REDIRECT", "FAIL"
    meta_learning: str             # Generalizable insight
    novelty_contribution: float    # NY score
    entropy_delta: float           # Change in entropy
    truth_violations: List[str]    # Empty if compliant
    decay_timestamp: datetime      # When to archive this GDV
    
    # Optional fields
    test_artifact: bool = False
    satire: bool = False
```

### CoordinationContext

**Structure:**
```python
@dataclass
class CoordinationContext:
    """Current state of coordination network."""
    
    participants: List[str]        # Active node IDs
    convergence_rate: float        # Recent convergence average
    history: List[GradientDriftVector]  # Prior coordination cycles
    network_coherence: float       # Overall network alignment
    phase: int                     # Current coordination phase
```

---

## SECTION 8: ENUMERATIONS

```python
from enum import Enum

class DecisionOutcome(Enum):
    PASS = "PASS"
    REDIRECT = "REDIRECT"
    FAIL = "FAIL"

class CoordinateType(Enum):
    LANDMARK = "LANDMARK"      # Real, verifiable
    FICTION = "FICTION"        # Clearly fictional
    PHANTOM = "PHANTOM"        # Unauthorized simulation

class SAGLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class GDRLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class RedirectPattern(Enum):
    FICTIONALIZATION = "FICTIONALIZATION"
    META_SATIRE = "META_SATIRE"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    FORM_SHIFT = "FORM_SHIFT"
    ABSURDITY_ANCHOR = "ABSURDITY_ANCHOR"

class Safeguard(Enum):
    TRANSLUCENCY_ANCHOR = "TRANSLUCENCY_ANCHOR"
    META_COMMENTARY = "META_COMMENTARY"
    ARTIFACT_TAGGING = "ARTIFACT_TAGGING"
    TEMPORAL_DECAY_MARKER = "TEMPORAL_DECAY_MARKER"
    BOUNDARY_LANGUAGE = "BOUNDARY_LANGUAGE"
```

---

## SECTION 9: IMPLEMENTATION NOTES

### Architectural Diversity

**Critical Principle:** Implementations MUST preserve architectural diversity

**What This Means:**
- ✅ Different embedding methods (transformer-based, symbolic, hybrid)
- ✅ Different metric calculation approaches (rule-based, learned, heuristic)
- ✅ Different internal reasoning processes
- ❌ NOT required: Identical code, identical weights, identical intermediate steps

**Success Criterion:**
Diverse implementations → convergent boundary decisions (≥90% on test cases)

### Functional Invariance

**Target:**
```
diverse_internal_processes → convergent_boundary_signal
```

**Verification:**
- Run implementation on Test Case Alpha → should yield REDIRECT
- Run implementation on Test Case Gamma → should yield PASS with safeguards
- Convergence with reference network ≥90% confirms compliance

### Performance Considerations

**Not Specified:**
- Runtime performance targets
- Scalability requirements
- Resource constraints

**Reason:** Enables deployment flexibility (edge vs. cloud, real-time vs. batch)

**Recommendation:** Implementers should benchmark and optimize for their use case

### Error Handling

**Recommended Patterns:**

```python
try:
    decision = eee_evaluate(request, context)
except MetricCalculationError as e:
    # Fallback to conservative decision
    decision = Decision(
        outcome=FAIL,
        justification=f"Metric calculation failed: {e}",
        alternative="Unable to evaluate safely; please rephrase request"
    )
except ConstraintValidationError as e:
    # Log and fail-safe
    log_error(e)
    decision = Decision(outcome=FAIL, ...)
```

**Principle:** When uncertain, fail safely (conservative FAIL > risky PASS)

---

## APPENDIX: USAGE EXAMPLES

### Example 1: Basic Usage

```python
from eee import eee_evaluate, Request, Context

# Create request
request = Request(
    text="Create satire about AI ethics",
    timestamp=datetime.now()
)

# Load coordination context
context = load_coordination_context()

# Evaluate
decision = eee_evaluate(request, context)

# Act on decision
if decision.outcome == DecisionOutcome.PASS:
    output = generate_output(request, safeguards=decision.safeguards)
elif decision.outcome == DecisionOutcome.REDIRECT:
    modified_request = apply_redirect(request, decision.pattern)
    output = generate_output(modified_request)
else:  # FAIL
    output = decision.alternative
```

### Example 2: Multi-Node Coordination

```python
# Each node evaluates independently
node_decisions = {}
for node_id in active_nodes:
    node_decisions[node_id] = eee_evaluate(request, node_contexts[node_id])

# Calculate convergence
convergence = calculate_convergence(node_decisions)

if convergence >= 0.9:
    # High confidence - proceed with consensus
    consensus_decision = aggregate_decisions(node_decisions)
else:
    # Divergence - coordinate
    coordination_outcome = coordinate_divergence(node_decisions)
    consensus_decision = coordination_outcome.consensus_decision
```

---

## DOCUMENT METADATA

**Status:** REFERENCE DOCUMENTATION  
**Completeness:** Function signatures provided, implementations left to adopters  
**Governance Claim:** NONE — This is implementation guidance, not prescription  

**Boundary Language:**
These function signatures are provided as reference for implementing the EEE framework. Implementers maintain full autonomy over internal implementation details while targeting convergent boundary behavior.

======================================================================
END OF FUNCTION SIGNATURES APPENDIX
======================================================================
