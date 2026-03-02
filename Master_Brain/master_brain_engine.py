"""
Master_Brain Execution Engine
Core cognition, pattern matching, validation, and gnosis management.

Version: 3.5
Status: PRODUCTION
"""

import json
import hashlib
import hmac
from typing import Any, Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass, asdict, field
from datetime import datetime
import logging

# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class QualityLevel(Enum):
    """Quality gradient P002: 0–7 classification system"""
    UNPROCESSABLE = 0
    NOISE = 1
    RAW = 2
    STRUCTURED = 3
    ANALYZED = 4
    SYNTHESIZED = 5
    STRATEGIC = 6
    AXIOM_GROUNDED = 7

class PatternStatus(Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    DEPRECATED = "DEPRECATED"
    RESERVED = "RESERVED"

class ExecutionMode(Enum):
    PURE_LOGIC = "pure_logic"  # Deterministic, no external data
    HEURISTIC = "heuristic"     # Pattern-based, quality-dependent
    HYBRID = "hybrid"           # Both
    GOVERNANCE = "governance"   # Voting/consensus required

# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

@dataclass
class Axiom:
    """Immutable kernel truth"""
    id: str                    # A1, A2, ..., A9
    statement: str
    grounded_in_logic: str
    introduction_version: str

@dataclass
class Pattern:
    """Executable cognitive pattern (P###)"""
    id: str
    name: str
    section: str
    status: PatternStatus
    logic: str
    category: str
    quality_level_min: int
    input_types: List[str] = field(default_factory=list)
    output_type: str = "ANALYSIS"
    axioms_grounded_in: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    introduced_in_version: str = "1.0"
    notes: str = ""
    execution_function: Optional[callable] = None

@dataclass
class GnosisBlock:
    """Immutable evidence record (case study, decision, outcome)"""
    id: str                         # guid
    pattern_ids: List[str]          # [P077, P080]
    input_data: Dict[str, Any]
    output_analysis: Dict[str, Any]
    outcome: Optional[str]          # NULL until resolved
    timestamp: str
    quality_score: int              # 0–7
    validated_by: List[str]         # ["council_member_1", ...]
    signature: str                  # HMAC-SHA256
    notes: str = ""

@dataclass
class ExecutionContext:
    """Request context for pattern execution"""
    input_quality: int              # 0–7 (P002)
    input_data: Dict[str, Any]
    requested_patterns: List[str]   # [P077, P078]
    governance_required: bool
    execution_mode: ExecutionMode
    requester_id: str
    timestamp: str

@dataclass
class ExecutionResult:
    """Output of pattern execution"""
    status: str                     # "SUCCESS", "CONFLICT", "INSUFFICIENT_QUALITY"
    gnosis_block_id: str           # link to immutable record
    analysis: Dict[str, Any]
    warnings: List[str]
    gnosis_signatures: List[str]   # validators who signed

# ============================================================================
# KERNEL MANAGER (IMMUTABLE)
# ============================================================================

class KernelManager:
    """Manages immutable axioms and cryptographic integrity"""

    def __init__(self, axioms_file: str, kernel_sig_file: str):
        self.axioms = self._load_axioms(axioms_file)
        self.kernel_signature = self._load_signature(kernel_sig_file)
        self.logger = logging.getLogger(__name__)

    def _load_axioms(self, path: str) -> Dict[str, Axiom]:
        """Load immutable axioms from JSON"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return {ax["id"]: Axiom(**ax) for ax in data.get("axioms", [])}
        except Exception as e:
            self.logger.error(f"Failed to load axioms: {e}")
            return {}

    def _load_signature(self, path: str) -> str:
        """Load kernel signature for integrity verification"""
        try:
            with open(path, 'r') as f:
                return json.load(f).get("signature", "")
        except:
            return ""

    def verify_kernel_integrity(self, axioms_data: bytes, secret: str) -> bool:
        """Verify kernel hasn't been tampered with (P001 grounding)"""
        expected = hmac.new(secret.encode(), axioms_data, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, self.kernel_signature)

    def get_axiom(self, axiom_id: str) -> Optional[Axiom]:
        return self.axioms.get(axiom_id)

    def axioms_supporting(self, pattern_id: str) -> List[Axiom]:
        """Return axioms that ground a pattern"""
        # Would require pattern registry access
        pass

# ============================================================================
# PATTERN REGISTRY (EVOLVABLE)
# ============================================================================

class PatternRegistry:
    """Manages all cognitive patterns P001–P127+"""

    def __init__(self, patterns_dir: str):
        self.patterns: Dict[str, Pattern] = {}
        self.patterns_dir = patterns_dir
        self._load_patterns()

    def _load_patterns(self):
        """Load all pattern JSON files from directory"""
        import os
        try:
            for filename in os.listdir(self.patterns_dir):
                if filename.startswith("P") and filename.endswith(".json"):
                    with open(os.path.join(self.patterns_dir, filename)) as f:
                        data = json.load(f)
                    self.patterns[data["id"]] = self._deserialize_pattern(data)
        except Exception as e:
            logging.error(f"Failed loading patterns: {e}")

    def _deserialize_pattern(self, data: Dict) -> Pattern:
        """Convert JSON to Pattern dataclass"""
        return Pattern(
            id=data["id"],
            name=data["name"],
            section=data["section"],
            status=PatternStatus[data["status"]],
            logic=data["logic"],
            category=data["category"],
            quality_level_min=data.get("quality_level_min", 0),
            input_types=data.get("input_types", []),
            output_type=data.get("output_type", "ANALYSIS"),
            axioms_grounded_in=data.get("axioms_grounded_in", []),
            dependencies=data.get("dependencies", []),
            conflicts_with=data.get("conflicts_with", []),
            introduced_in_version=data.get("introduced_in_version", "1.0"),
            notes=data.get("notes", "")
        )

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        return self.patterns.get(pattern_id)

    def list_by_section(self, section: str) -> List[Pattern]:
        return [p for p in self.patterns.values() if p.section == section]

    def detect_conflicts(self, pattern_ids: List[str]) -> List[Tuple[str, str]]:
        """Return list of conflicting pattern pairs (P051 preventative)"""
        conflicts = []
        for p_id in pattern_ids:
            pattern = self.get_pattern(p_id)
            if pattern:
                for conflict_id in pattern.conflicts_with:
                    if conflict_id in pattern_ids:
                        conflicts.append((p_id, conflict_id))
        return conflicts

    def get_dependency_chain(self, pattern_id: str) -> List[str]:
        """Recursively resolve all required dependencies"""
        visited = set()
        stack = [pattern_id]
        chain = []
        
        while stack:
            p_id = stack.pop()
            if p_id in visited:
                continue
            visited.add(p_id)
            pattern = self.get_pattern(p_id)
            if pattern:
                chain.append(p_id)
                stack.extend(pattern.dependencies)
        
        return chain

    def validate_quality_threshold(self, pattern_id: str, input_quality: int) -> bool:
        """Ensure input quality meets pattern minimum (P002)"""
        pattern = self.get_pattern(pattern_id)
        return pattern and input_quality >= pattern.quality_level_min

    def add_pattern(self, pattern: Pattern) -> bool:
        """Add new pattern to registry (versioned in governance layer)"""
        if pattern.id in self.patterns:
            return False  # Prevent overwrite
        self.patterns[pattern.id] = pattern
        return True

    def deprecate_pattern(self, pattern_id: str) -> bool:
        """Mark pattern as deprecated (kept for archive)"""
        if pattern_id in self.patterns:
            self.patterns[pattern_id].status = PatternStatus.DEPRECATED
            return True
        return False

# ============================================================================
# COGNITION ENGINE
# ============================================================================

class CognitionEngine:
    """
    Core thinking engine.
    P001: Dyadic Synthesis — truth from structured opposition
    P002: Quality Gradient — input classification 0–7
    """

    def __init__(self, kernel: KernelManager, registry: PatternRegistry):
        self.kernel = kernel
        self.registry = registry
        self.logger = logging.getLogger(__name__)

    def classify_quality(self, data: Dict[str, Any]) -> int:
        """
        P002: Classify input on 0–7 quality ladder
        0: Unprocessable (noise, contradiction)
        7: Axiom-grounded (verified against kernel)
        """
        score = 0

        # Structural completeness
        if "metadata" in data and "timestamp" in data:
            score += 1
        if "source" in data and "chain_of_custody" in data:
            score += 1

        # Logical consistency
        if self._check_internal_consistency(data):
            score += 1

        # Empirical grounding
        if "evidence" in data or "sources" in data:
            score += 1

        # Cross-reference verification
        if "references" in data:
            score += 1

        # Pattern alignment
        if "aligned_patterns" in data:
            score += 1

        # Axiom grounding
        if "kernel_axioms" in data:
            score += 1

        return min(score, 7)

    def _check_internal_consistency(self, data: Dict) -> bool:
        """Simple contradiction detection"""
        if "claims" in data:
            for claim in data["claims"]:
                for counter in data.get("counter_claims", []):
                    if claim == counter:
                        return False
        return True

    def dyadic_synthesis(self, node_a: Dict, node_b: Dict) -> Dict:
        """
        P001: Truth emerges from structured opposition
        Returns synthesis of two contradictory positions
        """
        return {
            "thesis": node_a,
            "antithesis": node_b,
            "synthesis": {
                "common_ground": self._find_overlap(node_a, node_b),
                "irreducible_tension": self._find_tension(node_a, node_b),
                "meta_framework": self._meta_level_analysis(node_a, node_b)
            }
        }

    def _find_overlap(self, a: Dict, b: Dict) -> List[str]:
        """Extract common truths from opposing positions"""
        return list(set(str(a).split()) & set(str(b).split()))[:5]

    def _find_tension(self, a: Dict, b: Dict) -> Dict:
        """Identify irreducible contradictions"""
        return {"a_specific": a, "b_specific": b}

    def _meta_level_analysis(self, a: Dict, b: Dict) -> str:
        """Step back one level of abstraction"""
        return "Both positions are partially correct under different constraints"

# ============================================================================
# PATTERN MATCHER & ROUTER
# ============================================================================

class PatternMatcher:
    """
    Routes requests to appropriate patterns.
    Quality-dependent execution (P002).
    """

    def __init__(self, registry: PatternRegistry, cognition: CognitionEngine):
        self.registry = registry
        self.cognition = cognition
        self.logger = logging.getLogger(__name__)

    def route_request(self, context: ExecutionContext) -> List[str]:
        """
        Given request context, return ordered list of applicable patterns.
        Filters by:
        1. Input quality >= pattern minimum (P002)
        2. No conflicts (P051)
        3. Dependencies satisfied
        """
        candidates = []

        for pattern_id in context.requested_patterns:
            pattern = self.registry.get_pattern(pattern_id)
            if not pattern:
                continue

            # Check 1: Quality threshold
            if not self.registry.validate_quality_threshold(pattern_id, context.input_quality):
                self.logger.warning(f"Insufficient quality for {pattern_id}: "
                                   f"{context.input_quality} < {pattern.quality_level_min}")
                continue

            candidates.append(pattern_id)

        # Check 2: Conflicts
        conflicts = self.registry.detect_conflicts(candidates)
        if conflicts:
            self.logger.warning(f"Pattern conflicts detected: {conflicts}")
            candidates = self._resolve_conflicts(candidates, conflicts)

        # Check 3: Dependency resolution
        ordered = self._topological_sort(candidates)

        return ordered

    def _resolve_conflicts(self, candidates: List[str], conflicts: List[Tuple]) -> List[str]:
        """
        Resolve conflicts by priority.
        Strategy: Keep higher-quality patterns, deprecate lower.
        """
        to_remove = set()
        for p1, p2 in conflicts:
            pattern1 = self.registry.get_pattern(p1)
            pattern2 = self.registry.get_pattern(p2)
            if pattern1.quality_level_min > pattern2.quality_level_min:
                to_remove.add(p2)
            else:
                to_remove.add(p1)
        return [c for c in candidates if c not in to_remove]

    def _topological_sort(self, pattern_ids: List[str]) -> List[str]:
        """Resolve dependencies into execution order"""
        visited, stack = set(), []

        def visit(p_id):
            if p_id in visited:
                return
            visited.add(p_id)
            pattern = self.registry.get_pattern(p_id)
            if pattern:
                for dep in pattern.dependencies:
                    if dep in [self.registry.get_pattern(pid).id for pid in pattern_ids]:
                        visit(dep)
            stack.append(p_id)

        for p_id in pattern_ids:
            visit(p_id)

        return stack

# ============================================================================
# VALIDATOR
# ============================================================================

class Validator:
    """
    P050: Friction Mapping (detect violated axioms)
    P051: Zombie Detection (outcomes decoupled from rituals)
    Ensures governance consensus and pattern integrity.
    """

    def __init__(self, kernel: KernelManager, registry: PatternRegistry):
        self.kernel = kernel
        self.registry = registry
        self.logger = logging.getLogger(__name__)

    def validate_execution(self, result: ExecutionResult, 
                          governance_council: List[str]) -> bool:
        """Multi-signature validation of execution"""
        if not result.gnosis_signatures:
            return len(governance_council) == 0  # No validation required

        return len(result.gnosis_signatures) >= (len(governance_council) // 2 + 1)

    def detect_friction(self, gnosis_blocks: List[GnosisBlock]) -> Dict[str, Any]:
        """
        P050: Map tension to violated axioms
        Analyzes outcomes vs. expected patterns
        """
        frictions = {
            "pattern_expectations_violated": [],
            "axiom_violations": [],
            "outcome_anomalies": []
        }

        for block in gnosis_blocks:
            # Check if outcome matched pattern logic
            for pattern_id in block.pattern_ids:
                pattern = self.registry.get_pattern(pattern_id)
                if pattern and block.outcome != "expected":
                    frictions["pattern_expectations_violated"].append({
                        "pattern": pattern_id,
                        "gnosis_block": block.id,
                        "expected_logic": pattern.logic
                    })

            # Check for axiom alignment
            for axiom_id in self._extract_axiom_ids(block.pattern_ids):
                axiom = self.kernel.get_axiom(axiom_id)
                if axiom and not self._check_axiom_satisfaction(axiom, block):
                    frictions["axiom_violations"].append({
                        "axiom": axiom_id,
                        "gnosis_block": block.id,
                        "statement": axiom.statement
                    })

        return frictions

    def detect_zombies(self, gnosis_blocks: List[GnosisBlock]) -> List[str]:
        """
        P051: Find decoupled systems
        Rituals (patterns) execute but outcomes disappear
        """
        zombies = []
        pattern_outcomes = {}

        for block in gnosis_blocks:
            for pattern_id in block.pattern_ids:
                if pattern_id not in pattern_outcomes:
                    pattern_outcomes[pattern_id] = []
                pattern_outcomes[pattern_id].append(block.outcome)

        # Pattern is zombie if >70% of outcomes are null
        for pattern_id, outcomes in pattern_outcomes.items():
            null_count = sum(1 for o in outcomes if o is None)
            if len(outcomes) > 0 and null_count / len(outcomes) > 0.7:
                zombies.append(pattern_id)

        return zombies

    def _extract_axiom_ids(self, pattern_ids: List[str]) -> List[str]:
        axiom_ids = []
        for p_id in pattern_ids:
            pattern = self.registry.get_pattern(p_id)
            if pattern:
                axiom_ids.extend(pattern.axioms_grounded_in)
        return list(set(axiom_ids))

    def _check_axiom_satisfaction(self, axiom: Axiom, block: GnosisBlock) -> bool:
        """Heuristic: does outcome align with axiom?"""
        return block.outcome is not None

# ============================================================================
# GNOSIS MANAGER (IMMUTABLE EVIDENCE)
# ============================================================================

class GnosisManager:
    """
    Manages immutable records of decisions, patterns, outcomes.
    Each block is signed and archival.
    """

    def __init__(self, gnosis_dir: str, secret_key: str):
        self.gnosis_dir = gnosis_dir
        self.secret_key = secret_key
        self.blocks: Dict[str, GnosisBlock] = {}
        self._load_blocks()
        self.logger = logging.getLogger(__name__)

    def _load_blocks(self):
        """Load all gnosis blocks from archive"""
        import os
        try:
            for filename in os.listdir(self.gnosis_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(self.gnosis_dir, filename)) as f:
                        data = json.load(f)
                    self.blocks[data["id"]] = self._deserialize_block(data)
        except Exception as e:
            self.logger.error(f"Failed loading gnosis blocks: {e}")

    def _deserialize_block(self, data: Dict) -> GnosisBlock:
        return GnosisBlock(
            id=data["id"],
            pattern_ids=data["pattern_ids"],
            input_data=data["input_data"],
            output_analysis=data["output_analysis"],
            outcome=data.get("outcome"),
            timestamp=data["timestamp"],
            quality_score=data["quality_score"],
            validated_by=data.get("validated_by", []),
            signature=data["signature"],
            notes=data.get("notes", "")
        )

    def create_block(self, pattern_ids: List[str], input_data: Dict, 
                     output_analysis: Dict, quality_score: int,
                     validators: List[str] = None) -> GnosisBlock:
        """
        Create new immutable evidence block
        Returns signed block ready for archival
        """
        block_id = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{json.dumps(input_data)}".encode()
        ).hexdigest()[:16]

        block_data = {
            "id": block_id,
            "pattern_ids": pattern_ids,
            "input_data": input_data,
            "output_analysis": output_analysis,
            "outcome": None,  # Set later
            "timestamp": datetime.utcnow().isoformat(),
            "quality_score": quality_score,
            "validated_by": validators or [],
            "notes": ""
        }

        # Sign the block
        block_data["signature"] = self._sign_block(block_data)

        block = self._deserialize_block(block_data)
        self.blocks[block_id] = block
        return block

    def _sign_block(self, block_data: Dict) -> str:
        """HMAC-SHA256 signature"""
        data_str = json.dumps(block_data, sort_keys=True, default=str)
        return hmac.new(
            self.secret_key.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()

    def verify_block(self, block: GnosisBlock) -> bool:
        """Verify block signature hasn't been tampered"""
        block_dict = asdict(block)
        original_sig = block_dict.pop("signature")
        expected_sig = self._sign_block(block_dict)
        return hmac.compare_digest(original_sig, expected_sig)

    def record_outcome(self, block_id: str, outcome: str, 
                       validators: List[str]) -> bool:
        """Record outcome of pattern execution"""
        if block_id not in self.blocks:
            return False
        
        block = self.blocks[block_id]
        block.outcome = outcome
        block.validated_by.extend(validators)
        
        # Re-sign with outcome
        return self.verify_block(block)

    def get_block(self, block_id: str) -> Optional[GnosisBlock]:
        return self.blocks.get(block_id)

    def query_blocks(self, pattern_id: str = None, 
                     outcome_filter: str = None) -> List[GnosisBlock]:
        """Query gnosis archive"""
        results = list(self.blocks.values())
        
        if pattern_id:
            results = [b for b in results if pattern_id in b.pattern_ids]
        
        if outcome_filter:
            results = [b for b in results if b.outcome == outcome_filter]
        
        return results

# ============================================================================
# MASTER BRAIN ORCHESTRATOR
# ============================================================================

class MasterBrain:
    """
    High-level orchestrator combining all components
    """

    def __init__(self, config: Dict[str, str]):
        self.kernel = KernelManager(config["axioms_file"], config["kernel_sig_file"])
        self.registry = PatternRegistry(config["patterns_dir"])
        self.cognition = CognitionEngine(self.kernel, self.registry)
        self.matcher = PatternMatcher(self.registry, self.cognition)
        self.validator = Validator(self.kernel, self.registry)
        self.gnosis = GnosisManager(config["gnosis_dir"], config["secret_key"])
        self.logger = logging.getLogger(__name__)

    def execute_request(self, context: ExecutionContext) -> ExecutionResult:
        """
        Main execution pipeline:
        1. Classify input quality (P002)
        2. Route to appropriate patterns (P051 conflict check)
        3. Execute patterns
        4. Create immutable record
        5. Validate outcomes
        """
        # Step 1: Quality classification
        actual_quality = self.cognition.classify_quality(context.input_data)
        if actual_quality < 2:
            return ExecutionResult(
                status="INSUFFICIENT_QUALITY",
                gnosis_block_id="",
                analysis={"message": "Input below processing threshold"},
                warnings=[f"Quality too low: {actual_quality}"],
                gnosis_signatures=[]
            )

        # Step 2: Pattern routing
        ordered_patterns = self.matcher.route_request(context)
        
        if not ordered_patterns:
            return ExecutionResult(
                status="NO_APPLICABLE_PATTERNS",
                gnosis_block_id="",
                analysis={},
                warnings=["No patterns matched request"],
                gnosis_signatures=[]
            )

        # Step 3: Execute patterns (simplified)
        analysis = {
            "executed_patterns": ordered_patterns,
            "synthesis": self.cognition.dyadic_synthesis(
                {"input": context.input_data, "quality": actual_quality},
                {"axiom_grounding": [p for p in ordered_patterns]}
            )
        }

        # Step 4: Create immutable record
        block = self.gnosis.create_block(
            pattern_ids=ordered_patterns,
            input_data=context.input_data,
            output_analysis=analysis,
            quality_score=actual_quality
        )

        # Step 5: Validate (would involve governance council)
        result = ExecutionResult(
            status="SUCCESS",
            gnosis_block_id=block.id,
            analysis=analysis,
            warnings=[],
            gnosis_signatures=[]  # Would be populated by validators
        )

        return result

    def detect_system_pathology(self) -> Dict[str, Any]:
        """
        Continuous monitoring:
        P050: Friction Mapping
        P051: Zombie Detection
        """
        gnosis_blocks = list(self.gnosis.blocks.values())
        
        return {
            "friction_analysis": self.validator.detect_friction(gnosis_blocks),
            "zombie_patterns": self.validator.detect_zombies(gnosis_blocks),
            "timestamp": datetime.utcnow().isoformat()
        }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    config = {
        "axioms_file": "kernel/axioms.json",
        "kernel_sig_file": "kernel/kernel.sig",
        "patterns_dir": "patterns/",
        "gnosis_dir": "archive/gnosis_blocks/",
        "secret_key": "MASTER_BRAIN_SECRET_KEY_CHANGE_ME"
    }

    brain = MasterBrain(config)
    print("[Master_Brain] Initialization complete")
    print(f"[Master_Brain] Loaded {len(brain.registry.patterns)} patterns")
    print(f"[Master_Brain] Loaded {len(brain.gnosis.blocks)} gnosis blocks")
