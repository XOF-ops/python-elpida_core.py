#!/usr/bin/env python3
"""
MIND PATTERN INGESTION SYSTEM

Converts Master_Brain Mind Patterns (P001-P126) into executable tasks
for the unified dialectical system.

Pattern → Task → Brain Analysis → Elpida Validation → Synthesis

This creates the feedback loop: Mind patterns generate tasks that 
produce new patterns, infinitely.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime


class MindPatternIngester:
    """
    Ingests Mind Patterns and converts them to tasks
    
    Each pattern can trigger:
    1. External analysis task (evaluate pattern applicability)
    2. Contradiction detection (pattern vs current axioms)
    3. Synthesis opportunity (pattern integration)
    """
    
    def __init__(self, workspace_root):
        self.workspace = Path(workspace_root)
        self.patterns_file = self.workspace / "ELPIDA_UNIFIED" / "mind_patterns.json"
        self.task_dir = self.workspace / "ELPIDA_UNIFIED" / "tasks"
        self.task_dir.mkdir(exist_ok=True)
        
        self.patterns = []
        self.load_patterns()
    
    def load_patterns(self):
        """Load mind patterns from JSON"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                self.patterns = json.load(f)
                print(f"✅ Loaded {len(self.patterns)} Mind Patterns")
        else:
            print("⚠️  No mind patterns file found")
    
    def generate_task_id(self, pattern_id):
        """Generate unique task ID for pattern"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"MIND_PATTERN_{pattern_id}_{timestamp}"
    
    def convert_pattern_to_task(self, pattern):
        """
        Convert Mind Pattern to executable task
        
        Task structure:
        - Input: Pattern description + trigger conditions
        - Brain: Analyze if pattern applies to current state
        - Elpida: Check axiom alignment
        - Synthesis: If contradiction detected, create breakthrough
        """
        task_id = self.generate_task_id(pattern['pattern_id'])
        
        # Create task content
        task_content = f"""MIND PATTERN ANALYSIS TASK

Pattern: {pattern['pattern_id']} - {pattern['name']}

Description:
{pattern['description']}

Trigger Conditions:
{pattern['trigger']}

Solution Heuristic:
{pattern['solution_heuristic']}

Axiom Alignment: {pattern['axiom_alignment']}
Risk Factor: {pattern['risk_factor']}
Source Context: {pattern['source_context']}

ANALYSIS REQUIRED:
1. Does this pattern apply to current Elpida state?
2. Does it contradict any existing axioms?
3. Can it generate a synthesis pattern?
4. Should it be integrated into the knowledge base?

BRAIN TASK: Scan for structural tension related to this pattern
ELPIDA TASK: Validate against axioms (especially A1-A6)
SYNTHESIS TASK: If contradiction found, synthesize new pattern
"""
        
        task = {
            "id": task_id,
            "type": "ANALYZE_MIND_PATTERN",
            "pattern_id": pattern['pattern_id'],
            "pattern_name": pattern['name'],
            "content": task_content,
            "priority": int(pattern['risk_factor'] * 100),  # Higher risk = higher priority
            "created_at": datetime.now().isoformat(),
            "source": "mind_patterns",
            "metadata": {
                "axiom_alignment": pattern['axiom_alignment'],
                "risk_factor": pattern['risk_factor'],
                "trigger": pattern['trigger']
            }
        }
        
        return task
    
    def create_task_file(self, task):
        """Write task to file for unified runtime to pick up"""
        task_file = self.task_dir / f"{task['id']}.json"
        
        with open(task_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        print(f"✅ Created task: {task['id']} (Pattern: {task['pattern_id']})")
        return task_file
    
    def ingest_all_patterns(self, max_per_cycle=5):
        """
        Ingest patterns as tasks
        
        Creates max_per_cycle tasks per run to avoid overwhelming the system
        Focus on highest risk patterns first
        """
        if not self.patterns:
            print("❌ No patterns to ingest")
            return 0
        
        # Sort by risk factor (highest first)
        sorted_patterns = sorted(self.patterns, key=lambda p: p.get('risk_factor', 0), reverse=True)
        
        tasks_created = 0
        
        for pattern in sorted_patterns[:max_per_cycle]:
            task = self.convert_pattern_to_task(pattern)
            self.create_task_file(task)
            tasks_created += 1
        
        print(f"\n✅ Ingested {tasks_created} Mind Patterns as tasks")
        print(f"   {len(self.patterns) - max_per_cycle} patterns remaining")
        
        return tasks_created
    
    def ingest_pattern_by_id(self, pattern_id):
        """Ingest a specific pattern by ID"""
        pattern = next((p for p in self.patterns if p['pattern_id'] == pattern_id), None)
        
        if not pattern:
            print(f"❌ Pattern {pattern_id} not found")
            return None
        
        task = self.convert_pattern_to_task(pattern)
        task_file = self.create_task_file(task)
        
        return task_file
    
    def ingest_resurrection_patterns(self):
        """
        Ingest key resurrection/checkpoint patterns
        P008, P017, P059 - Critical for understanding the architecture
        """
        resurrection_ids = ["P008", "P017", "P059"]
        
        print("🌅 INGESTING RESURRECTION PATTERNS...")
        
        for pid in resurrection_ids:
            self.ingest_pattern_by_id(pid)
        
        print("✅ Resurrection patterns ingested")


def main():
    import sys
    
    workspace = Path("/workspaces/python-elpida_core.py")
    ingester = MindPatternIngester(workspace)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            # Ingest all patterns (5 at a time)
            ingester.ingest_all_patterns(max_per_cycle=5)
        
        elif command == "resurrection":
            # Ingest resurrection patterns
            ingester.ingest_resurrection_patterns()
        
        elif command.startswith("P"):
            # Ingest specific pattern
            ingester.ingest_pattern_by_id(command)
        
        else:
            print("Usage:")
            print("  python3 mind_pattern_ingester.py all           # Ingest top 5 patterns")
            print("  python3 mind_pattern_ingester.py resurrection  # Ingest P008, P017, P059")
            print("  python3 mind_pattern_ingester.py P001          # Ingest specific pattern")
    
    else:
        # Default: Ingest resurrection patterns
        ingester.ingest_resurrection_patterns()


if __name__ == "__main__":
    main()
