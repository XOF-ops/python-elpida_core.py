#!/usr/bin/env python3
"""
Master_Brain Pattern Composition Tooling
CLI interface for composing, validating, and visualizing pattern execution plans.

Usage:
    python3 pattern_composition_tool.py --compose P077 P080 P081
    python3 pattern_composition_tool.py --validate P050 P051 P052
    python3 pattern_composition_tool.py --visualize P001--P127
    python3 pattern_composition_tool.py --conflict-check P077 P078 P079
"""

import json
import sys
from typing import List, Dict, Set, Tuple
import argparse
from enum import Enum

# ============================================================================
# DATA LOADING
# ============================================================================

def load_pattern_registry(registry_path: str) -> Dict:
    """Load full pattern registry from JSON"""
    try:
        with open(registry_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Pattern registry not found at {registry_path}")
        sys.exit(1)

def load_axioms(axioms_path: str) -> Dict:
    """Load kernel axioms"""
    try:
        with open(axioms_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Axioms not found at {axioms_path}")
        sys.exit(1)

# ============================================================================
# PATTERN COMPOSITION
# ============================================================================

class PatternComposer:
    """Compose multiple patterns into coherent execution plans"""

    def __init__(self, registry: Dict, axioms: Dict):
        self.registry = registry
        self.axioms = axioms
        self.patterns = {p["id"]: p for p in registry["patterns"]}

    def compose(self, pattern_ids: List[str]) -> Dict:
        """
        Compose a list of patterns into execution plan.
        Returns detailed analysis of:
        - Dependencies
        - Conflicts
        - Quality requirements
        - Axiom coverage
        - Execution order
        """
        result = {
            "requested_patterns": pattern_ids,
            "valid": True,
            "execution_plan": [],
            "conflicts": [],
            "dependencies": {},
            "quality_requirement": 0,
            "axioms_covered": set(),
            "axioms_missing": set(),
            "warnings": []
        }

        # Validate all patterns exist
        missing = [p for p in pattern_ids if p not in self.patterns]
        if missing:
            result["valid"] = False
            result["errors"] = f"Patterns not found: {missing}"
            return result

        # Collect dependency graph
        for p_id in pattern_ids:
            pattern = self.patterns[p_id]
            result["dependencies"][p_id] = pattern.get("dependencies", [])
            result["quality_requirement"] = max(
                result["quality_requirement"],
                pattern.get("quality_level_min", 0)
            )
            result["axioms_covered"].update(pattern.get("axioms_grounded_in", []))

        # Resolve dependencies
        execution_order = self._topological_sort(pattern_ids)
        result["execution_plan"] = execution_order

        # Check for conflicts
        for p_id in pattern_ids:
            pattern = self.patterns[p_id]
            for conflict_id in pattern.get("conflicts_with", []):
                if conflict_id in pattern_ids:
                    result["conflicts"].append((p_id, conflict_id))
                    result["valid"] = False

        # Axiom coverage analysis
        all_axioms = set(self.axioms.get("axioms", []))
        result["axioms_missing"] = all_axioms - result["axioms_covered"]

        if result["conflicts"]:
            result["warnings"].append(f"Pattern conflicts detected: {result['conflicts']}")

        if result["axioms_missing"]:
            result["warnings"].append(
                f"Axioms not covered: {result['axioms_missing']} "
                "(decision may lack foundational grounding)"
            )

        result["axioms_covered"] = list(result["axioms_covered"])
        result["axioms_missing"] = list(result["axioms_missing"])

        return result

    def _topological_sort(self, pattern_ids: List[str]) -> List[str]:
        """Resolve dependencies into execution order"""
        visited, stack = set(), []

        def visit(p_id):
            if p_id in visited:
                return
            visited.add(p_id)
            pattern = self.patterns.get(p_id)
            if pattern:
                for dep in pattern.get("dependencies", []):
                    if dep in pattern_ids:
                        visit(dep)
            stack.append(p_id)

        for p_id in pattern_ids:
            visit(p_id)

        return stack

# ============================================================================
# PATTERN VALIDATION
# ============================================================================

class PatternValidator:
    """Validate pattern specifications and registries"""

    def __init__(self, registry: Dict, axioms: Dict):
        self.registry = registry
        self.axioms = axioms
        self.patterns = {p["id"]: p for p in registry["patterns"]}

    def validate_registry(self) -> Dict:
        """Full registry integrity check"""
        issues = {
            "errors": [],
            "warnings": [],
            "missing_axioms": [],
            "circular_dependencies": [],
            "orphaned_patterns": []
        }

        # Check all axioms referenced are defined
        axiom_ids = {a.get("id") for a in self.axioms.get("axioms", [])}
        for p_id, pattern in self.patterns.items():
            for axiom_id in pattern.get("axioms_grounded_in", []):
                if axiom_id not in axiom_ids:
                    issues["missing_axioms"].append((p_id, axiom_id))

        # Check circular dependencies
        for p_id, pattern in self.patterns.items():
            if self._has_circular_dependency(p_id):
                issues["circular_dependencies"].append(p_id)

        # Check for orphaned patterns (no axioms, no dependencies)
        for p_id, pattern in self.patterns.items():
            if (not pattern.get("axioms_grounded_in") and
                not pattern.get("dependencies") and
                pattern.get("status") == "ACTIVE"):
                issues["orphaned_patterns"].append(p_id)

        return issues

    def _has_circular_dependency(self, pattern_id: str, visited: Set[str] = None) -> bool:
        """Detect circular dependencies"""
        if visited is None:
            visited = set()

        if pattern_id in visited:
            return True

        visited.add(pattern_id)
        pattern = self.patterns.get(pattern_id)
        if pattern:
            for dep in pattern.get("dependencies", []):
                if self._has_circular_dependency(dep, visited.copy()):
                    return True

        return False

# ============================================================================
# VISUALIZATION
# ============================================================================

class PatternVisualizer:
    """Generate ASCII and graph visualizations of patterns"""

    def __init__(self, registry: Dict):
        self.registry = registry
        self.patterns = {p["id"]: p for p in registry["patterns"]}

    def ascii_dependency_graph(self, pattern_ids: List[str]) -> str:
        """Generate ASCII dependency graph"""
        output = "\n=== Pattern Dependency Graph ===\n"

        visited = set()
        for p_id in pattern_ids:
            self._print_dependency_tree(p_id, visited, output="", level=0)

        return output

    def section_summary(self) -> str:
        """Print summary of patterns by section"""
        sections = {}
        for pattern in self.patterns.values():
            sec = pattern.get("section")
            if sec not in sections:
                sections[sec] = []
            sections[sec].append(pattern)

        output = "\n=== Patterns by Section ===\n"
        for section, patterns in sorted(sections.items()):
            output += f"\n{section} ({len(patterns)} patterns)\n"
            for p in sorted(patterns, key=lambda x: x["id"]):
                output += f"  {p['id']}: {p['name']} [Q{p['quality_level_min']}]\n"

        return output

    def quality_distribution(self) -> str:
        """Show distribution by quality level"""
        quality_counts = {}
        for pattern in self.patterns.values():
            q = pattern.get("quality_level_min", 0)
            quality_counts[q] = quality_counts.get(q, 0) + 1

        output = "\n=== Quality Level Distribution ===\n"
        for level in range(8):
            count = quality_counts.get(level, 0)
            bar = "█" * count
            output += f"Q{level}: {bar} ({count} patterns)\n"

        return output

    def _print_dependency_tree(self, p_id: str, visited: Set[str], output: str = "", level: int = 0) -> str:
        """Recursively print dependency tree"""
        if p_id in visited:
            return output

        visited.add(p_id)
        pattern = self.patterns.get(p_id)
        if not pattern:
            return output

        indent = "  " * level
        output += f"{indent}├─ {p_id}: {pattern['name']}\n"

        for dep in pattern.get("dependencies", []):
            output = self._print_dependency_tree(dep, visited, output, level + 1)

        return output

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Master_Brain Pattern Composition Tooling"
    )

    parser.add_argument(
        "--compose",
        nargs="+",
        help="Compose multiple patterns into execution plan"
    )
    parser.add_argument(
        "--validate",
        nargs="*",
        help="Validate patterns or entire registry"
    )
    parser.add_argument(
        "--visualize",
        nargs="*",
        help="Visualize pattern relationships"
    )
    parser.add_argument(
        "--conflict-check",
        nargs="+",
        help="Check for pattern conflicts"
    )
    parser.add_argument(
        "--registry",
        default="patterns/pattern_registry_full.json",
        help="Path to pattern registry"
    )
    parser.add_argument(
        "--axioms",
        default="kernel/axioms.json",
        help="Path to axioms file"
    )

    args = parser.parse_args()

    # Load data
    registry = load_pattern_registry(args.registry)
    axioms = load_axioms(args.axioms)

    # Compose
    if args.compose:
        composer = PatternComposer(registry, axioms)
        result = composer.compose(args.compose)
        print("\n=== Pattern Composition ===")
        print(json.dumps(result, indent=2))

    # Validate
    if args.validate is not None:
        validator = PatternValidator(registry, axioms)
        if args.validate:
            # Validate specific patterns
            print(f"\nValidating patterns: {args.validate}")
            # TODO: implement pattern-specific validation
        else:
            # Full registry validation
            issues = validator.validate_registry()
            print("\n=== Registry Validation ===")
            print(json.dumps(issues, indent=2))

    # Visualize
    if args.visualize is not None:
        visualizer = PatternVisualizer(registry)
        print(visualizer.section_summary())
        print(visualizer.quality_distribution())
        if args.visualize:
            print(visualizer.ascii_dependency_graph(args.visualize))

    # Conflict check
    if args.conflict_check:
        composer = PatternComposer(registry, axioms)
        result = composer.compose(args.conflict_check)
        print("\n=== Conflict Analysis ===")
        if result["conflicts"]:
            print(f"CONFLICTS DETECTED: {result['conflicts']}")
            print("Status: INVALID COMPOSITION")
        else:
            print("No conflicts detected. Composition is valid.")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
