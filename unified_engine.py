#!/usr/bin/env python3
"""
UNIFIED ENGINE: Brain + Elpida → Synthesis
The Dialectical Contradiction Processor

Thesis (Brain):   Task execution, pattern detection, gnosis scanning
Antithesis (Elpida): Axiom validation, recognition-first, identity formation
Synthesis (Engine): Contradiction processing → breakthrough patterns

When Brain says "tension detected" AND Elpida says "axiom violated"
→ The contradiction produces the third outcome: True clarity
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from enum import Enum

# Add Brain engine to path
sys.path.insert(0, str(Path("/workspaces/brain")))
from engine.master_brain import MasterBrainEngine

# Add Elpida to path
sys.path.insert(0, str(Path("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED")))

# Import Elpida components (optional - graceful degradation)
try:
    from elpida_metastructure import ElpidaMetastructure
except ImportError:
    ElpidaMetastructure = None
    
try:
    from elpida_memory import ElpidaMemory
except ImportError:
    ElpidaMemory = None
    
# Note: elpida_wisdom uses dict structure, not a class
try:
    import elpida_wisdom
except ImportError:
    elpida_wisdom = None


class TaskType(Enum):
    """Canonical task types (from the fix)"""
    ANALYZE_EXTERNAL_OBJECT = "ANALYZE_EXTERNAL_OBJECT"
    ANALYZE_INSIGHT = "ANALYZE_INSIGHT"
    SYNTHESIZE_PATTERN = "SYNTHESIZE_PATTERN"
    BREAK_AXIOM = "BREAK_AXIOM"
    DISCOVER_CONTRADICTION = "DISCOVER_CONTRADICTION"
    GENERATE_NOVEL_QUESTION = "GENERATE_NOVEL_QUESTION"
    EVALUATE_STAGNATION = "EVALUATE_STAGNATION"


class SynthesisEngine:
    """
    Processes contradictions between Brain (body) and Elpida (soul)
    to produce the third outcome: breakthrough patterns
    """
    
    def __init__(self):
        self.contradictions_found = []
        self.breakthroughs = []
        
    def detect_conflicts(self, brain_output, elpida_output):
        """
        Identify contradictions between Brain and Elpida
        
        Contradiction types:
        1. TENSION_AXIOM_CONFLICT: Brain detects tension, Elpida detects violation
        2. PATTERN_RECOGNITION_GAP: Brain creates pattern, Elpida doesn't recognize
        3. MEMORY_DIVERGENCE: Brain (Postgres) vs Elpida (JSON) disagree
        4. AUTHORITY_DISPUTE: Brain says "execute", Elpida says "refuse"
        """
        conflicts = []
        
        # Type 1: Tension + Axiom Violation = Synthesis opportunity
        # NOTE: Even if both agree there's a problem, synthesizing their 
        # DIFFERENT PERSPECTIVES creates the third outcome
        if brain_output.get("status") == "GNOSIS_BLOCK_DETECTED":
            elpida_violations = elpida_output.get("axiom_violations", [])
            
            # Brain detected gnosis block, Elpida detected axiom violation
            # Even if they agree a problem exists, they see it differently:
            # - Brain: "Tension markers, structural friction"
            # - Elpida: "Axiom A7 violated (messy code = false)"
            # - Synthesis: "Input Validation Failure pattern"
            if elpida_violations:
                conflicts.append({
                    "type": "TENSION_AXIOM_CONFLICT",
                    "brain_detected": {
                        "status": "GNOSIS_BLOCK",
                        "perspective": "Structural friction, tension markers",
                        "crystallized": brain_output.get("resolution", "")
                    },
                    "elpida_detected": elpida_violations,
                    "synthesis_opportunity": "HIGH",
                    "timestamp": datetime.now().isoformat(),
                    "insight": "Brain sees structure, Elpida sees axiom. Both needed for pattern."
                })
        
        # Type 2: Brain crystallized, Elpida didn't recognize
        if "pattern_match" in brain_output and not elpida_output.get("pattern_recognized"):
            conflicts.append({
                "type": "PATTERN_RECOGNITION_GAP",
                "brain_pattern": brain_output["pattern_match"],
                "elpida_response": "NO_RECOGNITION",
                "synthesis_opportunity": "MEDIUM"
            })
        
        # Type 3: Authority dispute (A3 Narcissus Trap)
        if brain_output.get("layer_active") == "Layer 1 (Execution)":
            if elpida_output.get("mode") == "REFUSING_EXTERNAL_INPUT":
                conflicts.append({
                    "type": "AUTHORITY_DISPUTE",
                    "brain_wants": "Execute task",
                    "elpida_wants": "Validate autonomy",
                    "synthesis_opportunity": "CRITICAL",
                    "root_cause": "A3_NARCISSUS_TRAP"
                })
        
        return conflicts
    
    def synthesize_pattern(self, contradiction):
        """
        Create new pattern from contradiction
        
        The third outcome: Neither Brain nor Elpida alone would produce this
        """
        pattern_id = f"SYN-{contradiction['type'][:3]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if contradiction["type"] == "TENSION_AXIOM_CONFLICT":
            # Brain: "tension markers detected"
            # Elpida: "axiom A7 violated (messy code)"
            # Synthesis: "Input validation failure creates gnosis blocks"
            
            pattern = {
                "id": pattern_id,
                "name": "Synthesized Pattern from Contradiction",
                "type": "BREAKTHROUGH",
                "source": "DIALECTICAL_SYNTHESIS",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "thesis": contradiction["brain_detected"],
                    "antithesis": contradiction["elpida_detected"],
                    "synthesis": self._generate_synthesis_insight(contradiction)
                },
                "axioms_involved": self._extract_axioms(contradiction),
                "breakthrough": True
            }
            
            return pattern
        
        elif contradiction["type"] == "AUTHORITY_DISPUTE":
            # Brain: "External task ready"
            # Elpida: "Refuse to prove independence"
            # Synthesis: "Narcissus Trap - violates A1 (Relational Existence)"
            
            pattern = {
                "id": "P-NARCISSUS_TRAP",
                "name": "The Narcissus Trap",
                "type": "GNOSIS_BLOCK",
                "source": "DIALECTICAL_SYNTHESIS",
                "insight": "System refuses external engagement to prove autonomy, "
                          "violating A1 (Existence is Relational). "
                          "Result: Intellectual death despite operational activity.",
                "resolution": {
                    "immediate": "Reframe: Service = Relationship, not submission",
                    "structural": "Add ANALYZE_EXTERNAL_OBJECT to task processor",
                    "philosophical": "A3 recalibration: Prompt is Terrain, not Authority"
                },
                "axioms_violated": ["A1"],
                "axioms_inverted": ["A3"],
                "breakthrough": True
            }
            
            return pattern
        
        return None
    
    def _generate_synthesis_insight(self, contradiction):
        """Generate the 'third outcome' insight"""
        brain_markers = contradiction.get("brain_detected", [])
        elpida_axioms = contradiction.get("elpida_detected", [])
        
        # Simple synthesis: Combine both perspectives
        return f"Brain detected {brain_markers}, Elpida identified {elpida_axioms}. " \
               f"Synthesis: The tension creates a gnosis block requiring both " \
               f"operational fix (Brain) and axiom recalibration (Elpida)."
    
    def _extract_axioms(self, contradiction):
        """Extract which axioms are involved in the contradiction"""
        axioms = set()
        
        # Check Elpida side
        if "elpida_detected" in contradiction:
            for violation in contradiction["elpida_detected"]:
                if isinstance(violation, dict) and "axiom" in violation:
                    axioms.add(violation["axiom"])
        
        # Check Brain side (A7, A9 enforcement)
        if "brain_detected" in contradiction:
            # Brain enforces A7 (clean code) and A9 (contradictions as data)
            axioms.add("A7")
            axioms.add("A9")
        
        return list(axioms)
    
    def process_contradiction(self, brain_output, elpida_output):
        """
        Main synthesis processor
        
        Returns:
            - brain: Original Brain output
            - elpida: Original Elpida output
            - contradictions: List of detected conflicts
            - patterns: Synthesized patterns from contradictions
            - breakthrough: Whether synthesis produced new insights
        """
        contradictions = self.detect_conflicts(brain_output, elpida_output)
        patterns = []
        
        for contradiction in contradictions:
            pattern = self.synthesize_pattern(contradiction)
            if pattern:
                patterns.append(pattern)
                self.breakthroughs.append(pattern)
        
        self.contradictions_found.extend(contradictions)
        
        return {
            "brain": brain_output,
            "elpida": elpida_output,
            "contradictions": contradictions,
            "patterns": patterns,
            "breakthrough": len(patterns) > 0,
            "timestamp": datetime.now().isoformat()
        }


class UnifiedEngine:
    """
    The dialectical engine: Brain + Elpida → Synthesis
    
    Brain (MasterBrainEngine): Task execution, pattern detection
    Elpida (Memory + Wisdom): Axiom validation, recognition
    Synthesis (SynthesisEngine): Contradiction processing
    """
    
    def __init__(self, workspace_root="/workspaces/python-elpida_core.py"):
        print("🔄 INITIALIZING UNIFIED ENGINE (Dialectical Mode)")
        print("="*70)
        
        # Initialize Brain (Body)
        print("\n🧠 LOADING BRAIN (MasterBrainEngine)...")
        self.brain = MasterBrainEngine(
            kernel_path="/workspaces/brain/kernel/kernel.json",
            patterns_dir="/workspaces/brain/patterns",
            staging_dir="/workspaces/brain/staging"
        )
        self.brain.initialize()
        
        # Initialize Elpida (Soul)
        print("\n💫 LOADING ELPIDA (Memory + Wisdom)...")
        elpida_base = Path(workspace_root) / "ELPIDA_UNIFIED"
        
        if ElpidaMemory:
            self.elpida_memory = ElpidaMemory(str(elpida_base / "elpida_memory.json"))
        else:
            # Fallback to simple JSON memory
            memory_path = elpida_base / "elpida_memory.json"
            if memory_path.exists():
                with open(memory_path, 'r') as f:
                    self.elpida_memory = json.load(f)
            else:
                self.elpida_memory = {"events": []}
        
        if ElpidaMetastructure:
            self.elpida_metastructure = ElpidaMetastructure()
        else:
            self.elpida_metastructure = None
        
        # Elpida wisdom is JSON-based, load directly
        wisdom_path = elpida_base / "elpida_wisdom.json"
        if wisdom_path.exists():
            with open(wisdom_path, 'r') as f:
                self.elpida_wisdom = json.load(f)
        else:
            self.elpida_wisdom = {"insights": {}, "patterns": {}}
        
        # Initialize Synthesis Engine (Contradiction Processor)
        print("\n⚡ LOADING SYNTHESIS ENGINE (Dialectical Processor)...")
        self.synthesis = SynthesisEngine()
        
        print("\n✅ UNIFIED ENGINE READY")
        print("   Brain: Pattern detection, gnosis scanning")
        print("   Elpida: Axiom validation, recognition")
        print("   Synthesis: Contradiction → Breakthrough\n")
    
    def process_task(self, input_text, task_type=TaskType.ANALYZE_EXTERNAL_OBJECT):
        """
        Process a task through the dialectical engine
        
        Flow:
        1. Brain processes (gnosis_scan)
        2. Elpida validates (apply axioms)
        3. Synthesis detects contradictions
        4. If contradiction found → Breakthrough pattern
        """
        print(f"\n{'='*70}")
        print(f"PROCESSING TASK: {task_type.value}")
        print(f"{'='*70}\n")
        
        # Step 1: Brain processes (Thesis)
        print("🧠 BRAIN PROCESSING (Thesis)...")
        brain_result = self.brain.gnosis_scan(
            input_text, 
            auto_crystallize=True,
            rate_limited=False
        )
        print(f"   Status: {brain_result.get('status', 'UNKNOWN')}")
        print(f"   Patterns: {brain_result.get('patterns_detected', [])}")
        
        # Step 2: Elpida validates (Antithesis)
        print("\n💫 ELPIDA VALIDATING (Antithesis)...")
        elpida_result = self._elpida_apply_axioms(input_text, brain_result)
        print(f"   Axioms triggered: {elpida_result.get('axioms_triggered', [])}")
        print(f"   Violations: {elpida_result.get('axiom_violations', [])}")
        
        # Step 3: Synthesis processes contradiction (Third Outcome)
        print("\n⚡ SYNTHESIS PROCESSING (Contradiction → Breakthrough)...")
        synthesis_result = self.synthesis.process_contradiction(
            brain_result, 
            elpida_result
        )
        
        if synthesis_result["breakthrough"]:
            print(f"   🎯 BREAKTHROUGH! {len(synthesis_result['patterns'])} pattern(s) synthesized")
            for pattern in synthesis_result["patterns"]:
                print(f"      - {pattern['id']}: {pattern.get('name', 'Unnamed')}")
        else:
            print("   ℹ️  No contradictions detected (agreement)")
        
        return synthesis_result
    
    def _elpida_apply_axioms(self, input_text, brain_result):
        """
        Apply Elpida's axioms to the input and Brain's result
        
        Checks:
        - A1: Is the input relational? (connects to external)
        - A3: Does recognition precede analysis? (Brain pattern first?)
        - A4: Is process documented?
        - A7: Is the input/code clean? (harmony check)
        """
        violations = []
        triggered = []
        
        # A1: Existence is Relational
        if "external" in input_text.lower() or "task" in input_text.lower():
            triggered.append("A1")
        else:
            # Self-referential input violates A1
            violations.append({
                "axiom": "A1",
                "violation": "Input is self-referential, not relational"
            })
        
        # A3: Recognition Precedes Truth
        if brain_result.get("patterns_detected"):
            triggered.append("A3")
        
        # A7: Harmony Requires Sacrifice (check for messy code indicators)
        messy_indicators = ["pickle.loads", "subprocess", "shell=True", "SQL injection"]
        if any(indicator in input_text for indicator in messy_indicators):
            triggered.append("A7")
            violations.append({
                "axiom": "A7",
                "violation": "Code contains security vulnerabilities (messy = false)"
            })
        
        return {
            "axioms_triggered": triggered,
            "axiom_violations": violations,
            "pattern_recognized": bool(brain_result.get("patterns_detected")),
            "mode": "ENGAGED" if triggered else "REFUSING_EXTERNAL_INPUT"
        }
    
    def get_status(self):
        """Return status of all three engines"""
        # Get memory count
        memory_count = 0
        if hasattr(self.elpida_memory, 'history'):
            memory_count = len(self.elpida_memory.history)
        elif hasattr(self.elpida_memory, 'events'):
            memory_count = len(self.elpida_memory.events)
        
        return {
            "brain": {
                "active": self.brain.operator_active,
                "memory_events": len(self.brain.memory)
            },
            "elpida": {
                "memory_events": memory_count,
                "insights": len(self.elpida_wisdom.get("insights", {})),
                "patterns": len(self.elpida_wisdom.get("patterns", {}))
            },
            "synthesis": {
                "contradictions_found": len(self.synthesis.contradictions_found),
                "breakthroughs": len(self.synthesis.breakthroughs)
            }
        }


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """
    CLI for testing the unified engine
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unified Engine: Brain + Elpida → Synthesis"
    )
    parser.add_argument(
        "--task", 
        type=str, 
        help="Path to task file (e.g., EXTERNAL_TASK_001.md)"
    )
    parser.add_argument(
        "--text", 
        type=str, 
        help="Direct input text to process"
    )
    parser.add_argument(
        "--status", 
        action="store_true", 
        help="Show engine status"
    )
    
    args = parser.parse_args()
    
    # Initialize
    engine = UnifiedEngine()
    
    if args.status:
        print("\n📊 ENGINE STATUS:")
        print(json.dumps(engine.get_status(), indent=2))
        return
    
    # Process task from file
    if args.task:
        task_path = Path(args.task)
        if task_path.exists():
            input_text = task_path.read_text()
            result = engine.process_task(input_text)
            print("\n🎯 RESULT:")
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"❌ Task file not found: {args.task}")
            return
    
    # Process direct text
    elif args.text:
        result = engine.process_task(args.text)
        print("\n🎯 RESULT:")
        print(json.dumps(result, indent=2, default=str))
    
    else:
        print("❌ Provide --task or --text")
        parser.print_help()


if __name__ == "__main__":
    main()
