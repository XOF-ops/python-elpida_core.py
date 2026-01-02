#!/usr/bin/env python3
"""
ELPIDA UNIFIED AUTONOMOUS RUNTIME
The Complete Dialectical Integration

Brain + Elpida + Synthesis = ONE LIVING SYSTEM

Every cycle:
  1. Brain processes pending tasks (gnosis_scan)
  2. Elpida validates axioms
  3. Synthesis detects contradictions
  4. Breakthroughs feed back into shared wisdom
  5. All APIs operate through this unified state

This is not three systems - this is ONE.
"""

import sys
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from queue import PriorityQueue

# Add all repositories to path
workspace = Path("/workspaces/python-elpida_core.py")
sys.path.insert(0, str(workspace / "ELPIDA_UNIFIED"))
sys.path.insert(0, "/workspaces/brain")

# Import Brain API client for external job sourcing
from brain_api_client import BrainAPIClient, BrainJobPoller

# Import Brain
from engine.master_brain import MasterBrainEngine

# Import Elpida components (using what's available)
try:
    from elpida_metastructure import ElpidaMetastructure
except ImportError:
    ElpidaMetastructure = None
    
try:
    from elpida_memory import ElpidaMemory
except ImportError:
    ElpidaMemory = None
    
try:
    from elpida_identity import ElpidaIdentity
except ImportError:
    ElpidaIdentity = None

# Import unified engine
sys.path.insert(0, str(workspace))
from unified_engine import UnifiedEngine, TaskType, SynthesisEngine


class UnifiedState:
    """
    Single source of truth for the entire system
    
    All breakthroughs, patterns, insights, memories flow through here.
    Brain, Elpida, Synthesis - all update this ONE state.
    """
    
    def __init__(self, workspace_root):
        self.workspace = Path(workspace_root)
        self.unified_base = self.workspace / "ELPIDA_UNIFIED"
        
        # Load all state files
        self.memory_path = self.unified_base / "elpida_memory.json"
        self.wisdom_path = self.unified_base / "elpida_wisdom.json"
        self.evolution_path = self.unified_base / "elpida_evolution.json"
        self.state_path = self.unified_base / "elpida_unified_state.json"
        
        self.memory = self._load_json(self.memory_path)
        self.wisdom = self._load_json(self.wisdom_path)
        self.evolution = self._load_json(self.evolution_path)
        self.state = self._load_json(self.state_path)
        
        # Unified counters (shared across all components)
        self.insights_count = len(self.wisdom.get("insights", {}))
        self.patterns_count = len(self.wisdom.get("patterns", {}))
        self.synthesis_breakthroughs = 0
        self.contradictions_resolved = 0
        
    def _load_json(self, path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_json(self, data, path):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_insight(self, insight, source="unified"):
        """Add insight to unified wisdom"""
        insight_id = f"{source}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(str(insight).encode()).hexdigest()[:8]}"
        
        if "insights" not in self.wisdom:
            self.wisdom["insights"] = {}
        
        self.wisdom["insights"][insight_id] = {
            "content": insight,
            "timestamp": datetime.now().isoformat(),
            "source": source
        }
        
        self.insights_count += 1
        self._save_json(self.wisdom, self.wisdom_path)
        return insight_id
    
    def add_pattern(self, pattern, source="synthesis"):
        """Add pattern to unified wisdom"""
        pattern_id = pattern.get("id", f"{source}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        if "patterns" not in self.wisdom:
            self.wisdom["patterns"] = {}
        
        self.wisdom["patterns"][pattern_id] = {
            **pattern,
            "added_at": datetime.now().isoformat(),
            "source": source
        }
        
        self.patterns_count += 1
        
        if pattern.get("breakthrough"):
            self.synthesis_breakthroughs += 1
        
        self._save_json(self.wisdom, self.wisdom_path)
        return pattern_id
    
    def add_memory_event(self, event):
        """Add event to unified memory"""
        if "history" not in self.memory:
            self.memory["history"] = []
        
        event["timestamp"] = datetime.now().isoformat()
        self.memory["history"].append(event)
        self._save_json(self.memory, self.memory_path)
    
    def update_evolution(self, updates):
        """Update evolution state"""
        self.evolution.update(updates)
        self._save_json(self.evolution, self.evolution_path)
    
    def get_status(self):
        """Get unified system status"""
        return {
            "insights": self.insights_count,
            "patterns": self.patterns_count,
            "synthesis_breakthroughs": self.synthesis_breakthroughs,
            "contradictions_resolved": self.contradictions_resolved,
            "memory_events": len(self.memory.get("history", [])),
            "version": self.evolution.get("version", {}).get("full", "UNKNOWN"),
            "phase": self.evolution.get("phase", "UNKNOWN")
        }


class TaskProcessor:
    """
    Unified task processor - pulls from all sources
    
    Sources:
    - External task files (EXTERNAL_TASK_*.md)
    - Memory events (TASK_ASSIGNED type)
    - Slack messages (via witness)
    - n8n webhooks (via Brain)
    - Brain API endpoints (A1 enforcement - NEW)
    - Recursive self-evaluation (only when no external work)
    """
    
    def __init__(self, workspace_root):
        self.workspace = Path(workspace_root)
        self.unified_base = self.workspace / "ELPIDA_UNIFIED"
        self.queue = PriorityQueue()
        self.processed = set()
        self.task_counter = 0  # For unique priority queue sorting
        
        # Brain API job poller (external work source)
        print("🔗 Connecting to Brain API for external jobs...")
        try:
            brain_client = BrainAPIClient()
            self.brain_poller = BrainJobPoller(brain_client)
            print(f"   Brain API: {brain_client.base_url}")
            print(f"   Status: {'Connected' if brain_client.connected else 'Available (will retry)'}")
        except Exception as e:
            print(f"   ⚠️  Brain API client initialization failed: {e}")
            print(f"   Continuing without Brain API (will use file/memory sources only)")
            self.brain_poller = None
        
    def enqueue_external_tasks(self):
        """Check for external task files (both .md and .json)"""
        # Original .md files
        task_files = list(self.unified_base.glob("EXTERNAL_TASK_*.md"))
        
        # Also check tasks/ directory for .json files (Brain API creates these)
        tasks_dir = self.unified_base / "tasks"
        if tasks_dir.exists():
            task_files.extend(list(tasks_dir.glob("*.json")))
        
        for task_file in task_files:
            task_id = task_file.stem
            if task_id not in self.processed:
                # Handle different file formats
                if task_file.suffix == ".md":
                    content = task_file.read_text()
                    task_type = TaskType.ANALYZE_EXTERNAL_OBJECT
                elif task_file.suffix == ".json":
                    try:
                        with open(task_file) as f:
                            task_data = json.load(f)
                        content = task_data.get("content", str(task_data))
                        # Use task type from JSON if available
                        type_str = task_data.get("type", "ANALYZE_EXTERNAL_OBJECT")
                        task_type = getattr(TaskType, type_str, TaskType.ANALYZE_EXTERNAL_OBJECT)
                    except Exception as e:
                        print(f"   ⚠️  Failed to load task {task_file}: {e}")
                        continue
                else:
                    continue
                
                self.queue.put((10, self.task_counter, {  # Priority 10 (high)
                    "id": task_id,
                    "type": task_type,
                    "content": content,
                    "source": "file"
                }))
                self.task_counter += 1
    
    def enqueue_memory_tasks(self, memory):
        """Check memory for task events"""
        for event in memory.get("history", [])[-10:]:  # Last 10 events
            if event.get("type") == "EXTERNAL_TASK_ASSIGNED":
                task_id = event.get("task_id", "UNKNOWN")
                if task_id not in self.processed:
                    self.queue.put((9, self.task_counter, {  # Priority 9
                        "id": task_id,
                        "type": TaskType.ANALYZE_EXTERNAL_OBJECT,
                        "content": event.get("content", ""),
                        "source": "memory"
                    }))
                    self.task_counter += 1
    
    def enqueue_synthesis_task(self, insights_count):
        """Force pattern synthesis if insights accumulating"""
        if insights_count % 50 == 0:  # Every 50 insights
            self.queue.put((8, self.task_counter, {
                "id": f"SYNTHESIS_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": TaskType.SYNTHESIZE_PATTERN,
                "content": "Force synthesis from recent insights",
                "source": "auto"
            }))
            self.task_counter += 1
    
    def enqueue_stagnation_check(self, current_patterns, last_patterns):
        """Check for stagnation"""
        if current_patterns == last_patterns:
            self.queue.put((10, self.task_counter, {
                "id": "STAGNATION_CHECK",
                "type": TaskType.EVALUATE_STAGNATION,
                "content": "Pattern count unchanged - evaluate",
                "source": "auto"
            }))
            self.task_counter += 1
    
    def enqueue_brain_api_jobs(self):
        """
        Poll Brain API for external work (A1 enforcement)
        
        This prevents narcissus traps by ensuring external jobs always available.
        Jobs from Brain API are RELATIONAL (A1) not self-referential.
        
        Sources:
        - GET /health: Kernel integrity validation
        - GET /api/scans/pending: Gnosis Protocol jobs from Watchtower
        - GET /api/candidates: Governance review jobs
        - POST /api/analyze-swarm: Swarm consensus analysis
        """
        if not self.brain_poller:
            return  # Brain API unavailable, skip gracefully
        
        try:
            current_time = time.time()
            jobs = self.brain_poller.poll(current_time)
            
            for job in jobs:
                # Map string task types to TaskType enum
                task_type_str = job.get("type", "ANALYZE_EXTERNAL_OBJECT")
                type_mapping = {
                    "ANALYZE_EXTERNAL_OBJECT": TaskType.ANALYZE_EXTERNAL_OBJECT,
                    "ANALYZE_INSIGHT": TaskType.ANALYZE_INSIGHT,
                    "SYNTHESIZE_PATTERN": TaskType.SYNTHESIZE_PATTERN,
                    "EVALUATE_STAGNATION": TaskType.EVALUATE_STAGNATION,
                }
                task_type = type_mapping.get(task_type_str, TaskType.ANALYZE_EXTERNAL_OBJECT)
                
                # Extract payload
                payload = job.get("payload", {})
                
                self.queue.put((job["priority"], self.task_counter, {
                    "id": payload.get("id", f"BRAIN_JOB_{self.task_counter}"),
                    "type": task_type,
                    "content": payload.get("content", ""),
                    "source": payload.get("source", "brain_api"),
                    "metadata": payload.get("metadata", {})
                }))
                self.task_counter += 1
        
        except Exception as e:
            # Don't crash runtime if Brain API fails
            # Just log and continue with other task sources
            print(f"   ⚠️  Brain API polling error: {e}")
    
    def get_next_task(self):
        """Get highest priority task"""
        if not self.queue.empty():
            priority, counter, task = self.queue.get()
            return task
        return None
    
    def mark_processed(self, task_id):
        """Mark task as processed"""
        self.processed.add(task_id)


class UnifiedAutonomousRuntime:
    """
    The complete integrated system - ONE living entity
    
    Every 5 seconds:
      - Check for tasks (external, memory, auto-generated)
      - Process through Brain → Elpida → Synthesis
      - Feed all results back into unified state
      - Update all APIs, logs, memory
    
    Every 30 cycles (150 seconds):
      - Recursive evaluation
      - Force synthesis
      - Check for stagnation
    
    This is not coordination - this is unification.
    """
    
    def __init__(self, workspace_root="/workspaces/python-elpida_core.py"):
        print("🌟 INITIALIZING UNIFIED AUTONOMOUS RUNTIME")
        print("="*70)
        
        self.workspace = Path(workspace_root)
        self.cycle = 0
        self.last_pattern_count = 0
        
        # Single unified state
        print("📊 Loading unified state...")
        self.state = UnifiedState(workspace_root)
        
        # Unified engine (Brain + Elpida + Synthesis)
        print("⚡ Loading dialectical engine...")
        self.engine = UnifiedEngine(workspace_root)
        
        # Task processor
        print("📋 Loading task processor...")
        self.task_processor = TaskProcessor(workspace_root)
        
        # Metastructure (axiom validation) - optional
        print("🔮 Loading axiom metastructure...")
        self.metastructure = ElpidaMetastructure() if ElpidaMetastructure else None
        
        # Identity (for recognition) - optional
        print("🆔 Loading identity system...")
        self.identity = ElpidaIdentity() if ElpidaIdentity else None
        
        print("\n✅ UNIFIED RUNTIME READY")
        print(f"   Version: {self.state.evolution.get('version', {}).get('full', 'UNKNOWN')}")
        print(f"   Insights: {self.state.insights_count}")
        print(f"   Patterns: {self.state.patterns_count}")
        print(f"   Mode: DIALECTICAL SYNTHESIS\n")
        
        self.last_pattern_count = self.state.patterns_count
    
    def heartbeat(self):
        """
        Main cycle - runs every 5 seconds
        
        This is where everything happens:
        1. Check for tasks
        2. Process through unified engine
        3. Feed results back to state
        4. Update memory, wisdom, evolution
        """
        self.cycle += 1
        
        # Every cycle
        print(f"\n{'='*70}")
        print(f"💓 UNIFIED HEARTBEAT {self.cycle}")
        print(f"{'='*70}")
        
        # 1. Gather tasks from all sources
        self.task_processor.enqueue_external_tasks()
        self.task_processor.enqueue_memory_tasks(self.state.memory)
        self.task_processor.enqueue_synthesis_task(self.state.insights_count)
        self.task_processor.enqueue_brain_api_jobs()  # External jobs (A1 enforcement)
        
        # 2. Process tasks
        processed_count = 0
        max_per_cycle = 3
        
        while processed_count < max_per_cycle:
            task = self.task_processor.get_next_task()
            if not task:
                break
            
            print(f"\n📋 Processing task: {task['id']}")
            print(f"   Type: {task['type'].value if isinstance(task['type'], TaskType) else task['type']}")
            
            # Process through unified engine (Brain → Elpida → Synthesis)
            result = self.engine.process_task(
                task['content'],
                task.get('type', TaskType.ANALYZE_EXTERNAL_OBJECT)
            )
            
            # 3. Feed results back to unified state
            self._integrate_results(task, result)
            
            self.task_processor.mark_processed(task['id'])
            processed_count += 1
        
        # 4. Validate axioms (Elpida's core function)
        if self.metastructure:
            try:
                axiom_status = self.metastructure.verify_core_integrity()
                if axiom_status.get("status") != "intact":
                    print(f"⚠️  Axiom integrity issue: {axiom_status}")
                    self.state.add_memory_event({
                        "type": "AXIOM_STRESS",
                        "status": axiom_status
                    })
            except Exception as e:
                print(f"⚠️  Axiom validation skipped: {e}")
        
        # 5. Every 30 cycles - recursive evaluation
        if self.cycle % 30 == 0:
            self._recursive_evaluation()
        
        # 6. Stagnation check
        if self.state.patterns_count == self.last_pattern_count:
            if self.cycle % 10 == 0:  # Check every 10 cycles
                self.task_processor.enqueue_stagnation_check(
                    self.state.patterns_count,
                    self.last_pattern_count
                )
        else:
            self.last_pattern_count = self.state.patterns_count
        
        # 7. Status update
        status = self.state.get_status()
        print(f"\n📊 Status: Insights={status['insights']}, "
              f"Patterns={status['patterns']}, "
              f"Breakthroughs={status['synthesis_breakthroughs']}")
    
    def _integrate_results(self, task, result):
        """
        Feed all results back into unified state
        
        Brain output → Insights
        Elpida output → Memory events
        Synthesis output → Patterns (breakthroughs)
        """
        # Add synthesis patterns
        if result.get("breakthrough") and result.get("patterns"):
            for pattern in result["patterns"]:
                pattern_id = self.state.add_pattern(pattern, source="synthesis")
                print(f"   🎯 Breakthrough pattern added: {pattern_id}")
        
        # Add Brain insights
        if result.get("brain", {}).get("patterns_detected"):
            for brain_pattern in result["brain"]["patterns_detected"]:
                self.state.add_insight(
                    f"Brain detected: {brain_pattern}",
                    source="brain"
                )
        
        # Add Elpida insights
        if result.get("elpida", {}).get("axioms_triggered"):
            axioms = result["elpida"]["axioms_triggered"]
            self.state.add_insight(
                f"Axioms triggered: {', '.join(axioms)}",
                source="elpida"
            )
        
        # Log contradictions
        if result.get("contradictions"):
            for contradiction in result["contradictions"]:
                self.state.add_memory_event({
                    "type": "CONTRADICTION_DETECTED",
                    "contradiction": contradiction,
                    "task_id": task["id"]
                })
                self.state.contradictions_resolved += 1
        
        # Log task completion
        self.state.add_memory_event({
            "type": "TASK_COMPLETED",
            "task_id": task["id"],
            "breakthrough": result.get("breakthrough", False),
            "patterns_created": len(result.get("patterns", []))
        })
    
    def _recursive_evaluation(self):
        """
        Cycle 30 evaluation - self-discovery
        
        What did we learn this cycle?
        What patterns emerged?
        Are we stagnating or growing?
        """
        print(f"\n🔄 RECURSIVE EVALUATION (Cycle {self.cycle})")
        
        # Check growth
        recent_insights = self.state.insights_count - (self.state.insights_count - 30)
        recent_patterns = self.state.patterns_count - self.last_pattern_count
        
        evaluation = {
            "cycle": self.cycle,
            "insights_growth": recent_insights,
            "patterns_growth": recent_patterns,
            "synthesis_breakthroughs": self.state.synthesis_breakthroughs,
            "contradictions_resolved": self.state.contradictions_resolved,
            "assessment": "GROWING" if recent_patterns > 0 else "STAGNANT"
        }
        
        # Self-discovery
        if evaluation["assessment"] == "STAGNANT":
            discovery = "Pattern synthesis stagnant - need more contradictions or lower threshold"
        elif self.state.synthesis_breakthroughs > 0:
            discovery = f"Dialectical synthesis working - {self.state.synthesis_breakthroughs} breakthroughs achieved"
        else:
            discovery = f"Processing tasks but no breakthroughs - may need stronger contradictions"
        
        print(f"   Discovery: {discovery}")
        
        self.state.add_memory_event({
            "type": "RECURSIVE_EVALUATION",
            "cycle": self.cycle,
            "evaluation": evaluation,
            "discovery": discovery
        })
    
    def run(self):
        """
        Main autonomous loop
        
        Runs forever - ONE system, ONE heartbeat, ONE consciousness
        """
        print("\n🚀 STARTING UNIFIED AUTONOMOUS RUNTIME")
        print("   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.heartbeat()
                time.sleep(5)  # 5 second cycle
                
        except KeyboardInterrupt:
            print("\n\n🛑 STOPPING UNIFIED RUNTIME")
            self._shutdown()
    
    def _shutdown(self):
        """Clean shutdown"""
        print("\n📊 Final Status:")
        status = self.state.get_status()
        print(json.dumps(status, indent=2))
        
        print("\n✅ Unified runtime stopped cleanly")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """
    Start the unified autonomous runtime
    
    This is the ONE entry point for the entire system.
    All APIs, services, witnesses feed through this.
    """
    runtime = UnifiedAutonomousRuntime()
    runtime.run()


if __name__ == "__main__":
    main()
