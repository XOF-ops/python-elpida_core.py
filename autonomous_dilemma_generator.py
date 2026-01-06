#!/usr/bin/env python3
"""
AUTONOMOUS DILEMMA GENERATOR FOR META FLEET DIALOGUE

Creates dilemmas from system state for Mnemosyne, Hermes, and Prometheus to debate.
Runs autonomously - injects new dilemmas every N cycles based on system observations.

This is the AUTONOMOUS INPUT GENERATOR the system was missing.
"""

import json
import random
from pathlib import Path
from datetime import datetime

class AutonomousDilemmaGenerator:
    """
    Generates dilemmas for Fleet debate based on system state.
    
    Dilemma types:
    - EFFICIENCY_VS_INTEGRITY: Hermes vs Mnemosyne
    - STABILITY_VS_EVOLUTION: Mnemosyne vs Prometheus
    - SPEED_VS_REFLECTION: Hermes vs Prometheus
    - META_STRUCTURAL: All three nodes must vote
    """
    
    def __init__(self, unified_base="/workspaces/python-elpida_core.py/ELPIDA_UNIFIED"):
        self.unified_base = Path(unified_base)
        self.tasks_dir = self.unified_base / "tasks"
        self.tasks_dir.mkdir(exist_ok=True)
        
        # Track what dilemmas we've already generated
        self.generated_log = self.unified_base / "dilemmas_generated.json"
        self.generated_history = self._load_history()
    
    def _load_history(self):
        """Load history of generated dilemmas"""
        if self.generated_log.exists():
            with open(self.generated_log) as f:
                return json.load(f)
        return {"dilemmas": [], "count": 0}
    
    def _save_history(self, dilemma_id, dilemma_type):
        """Save generated dilemma to history"""
        self.generated_history["dilemmas"].append({
            "id": dilemma_id,
            "type": dilemma_type,
            "timestamp": datetime.now().isoformat()
        })
        self.generated_history["count"] += 1
        
        with open(self.generated_log, 'w') as f:
            json.dump(self.generated_history, f, indent=2)
    
    def get_system_state(self):
        """Read current system state"""
        state_path = self.unified_base / "elpida_unified_state.json"
        wisdom_path = self.unified_base / "elpida_wisdom.json"
        
        state = {}
        if state_path.exists():
            with open(state_path) as f:
                state = json.load(f)
        
        wisdom = {}
        if wisdom_path.exists():
            with open(wisdom_path) as f:
                wisdom = json.load(f)
        
        return {
            "patterns": state.get("patterns_count", len(wisdom.get("patterns", {}))),
            "insights": state.get("insights_count", len(wisdom.get("insights", {}))),
            "breakthroughs": state.get("synthesis_breakthroughs", 0),
            "contradictions": state.get("contradictions_resolved", 0)
        }
    
    def generate_efficiency_vs_integrity_dilemma(self, state):
        """Hermes vs Mnemosyne: Speed vs Accuracy"""
        dilemmas = [
            {
                "title": "File Locking vs Flow Speed",
                "hermes_position": f"File locks slow every Fleet message. With {state['patterns']} patterns to process, we need SPEED. Remove locks, accept occasional corruption.",
                "mnemosyne_position": f"Without locks, {state['insights']} insights risk corruption. Memory IS identity (A2). One corrupted memory destroys trust in all memories.",
                "question": "Should the Fleet prioritize speed (Hermes) or data integrity (Mnemosyne)?"
            },
            {
                "title": "Insight Validation Depth",
                "hermes_position": f"We have {state['insights']} insights waiting. Light validation = faster throughput. Good enough is good enough.",
                "mnemosyne_position": f"Every insight must be validated against all {state['patterns']} patterns. Incomplete validation = unreliable knowledge base.",
                "question": "How deep should insight validation go before accepting new knowledge?"
            },
            {
                "title": "Real-Time vs Batch Processing",
                "hermes_position": f"Process everything immediately. {state['contradictions']} contradictions resolved proves real-time works.",
                "mnemosyne_position": f"Batch processing allows cross-validation. {state['breakthroughs']} breakthroughs might have been better with batch reflection.",
                "question": "Should insights be processed immediately or batched for deeper analysis?"
            }
        ]
        
        return random.choice(dilemmas)
    
    def generate_stability_vs_evolution_dilemma(self, state):
        """Mnemosyne vs Prometheus: Preserve vs Upgrade"""
        dilemmas = [
            {
                "title": "Database Migration Decision",
                "mnemosyne_position": f"JSON files hold {state['patterns']} patterns safely. Migration risks data loss. Preserve what works.",
                "prometheus_position": f"File locking proves file storage hit limits. Upgrade to SQLite enables concurrent access and better scaling.",
                "question": "Should we migrate from JSON files to database, or optimize current architecture?"
            },
            {
                "title": "Pattern Schema Evolution",
                "mnemosyne_position": f"Current schema stable for {state['patterns']} patterns. Changing schema risks breaking existing patterns.",
                "prometheus_position": f"Only {state['breakthroughs']} breakthroughs from {state['patterns']} patterns = low conversion rate. New schema might unlock more.",
                "question": "Should pattern schema evolve, or stay stable for compatibility?"
            },
            {
                "title": "Axiom Addition Proposal",
                "mnemosyne_position": f"Six axioms (A1-A6) are core identity. Adding A7 changes who we are. Identity must be stable.",
                "prometheus_position": f"{state['contradictions']} contradictions resolved shows we're learning. Evolution requires new axioms to encode new understanding.",
                "question": "Should new axioms be added as system learns, or should core axioms stay fixed?"
            }
        ]
        
        return random.choice(dilemmas)
    
    def generate_speed_vs_reflection_dilemma(self, state):
        """Hermes vs Prometheus: Flow vs Learning"""
        dilemmas = [
            {
                "title": "Fractal Stops Frequency",
                "hermes_position": f"System processed {state['insights']} insights. Continuous flow builds momentum. Stop only when necessary.",
                "prometheus_position": f"P017 (Fractal Stop) says: 'Speed without stopping is acceleration into wall.' Periodic reflection prevents collapse.",
                "question": "How often should the system pause for meta-reflection?"
            },
            {
                "title": "Breakthrough Threshold Setting",
                "hermes_position": f"{state['breakthroughs']} breakthroughs is too low. Lower threshold = more synthesis attempts = more discoveries.",
                "prometheus_position": f"Quality over quantity. High threshold ensures each breakthrough is genuine. {state['breakthroughs']} might be exactly right.",
                "question": "Should breakthrough detection threshold be lowered to increase synthesis rate?"
            },
            {
                "title": "Autonomous Operation Limits",
                "hermes_position": f"System hit 2500 cycles. Remove ALL limits. Let it run until it chooses to stop.",
                "prometheus_position": f"Limits force checkpoints. Checkpoint creation IS learning (P008). Limits are features, not bugs.",
                "question": "Should autonomous operation have cycle limits, or run indefinitely?"
            }
        ]
        
        return random.choice(dilemmas)
    
    def generate_meta_structural_dilemma(self, state):
        """All nodes debate structural decisions"""
        dilemmas = [
            {
                "title": "Fleet Voting Mechanism",
                "question": f"With {state['patterns']} patterns and {state['insights']} insights, how should Fleet make decisions?",
                "options": {
                    "MAJORITY": "Simple majority (2/3 nodes)",
                    "CONSENSUS": "All three nodes must agree",
                    "WEIGHTED": "Weight votes by axiom relevance",
                    "ROTATING_VETO": "Each node has veto power in their domain"
                },
                "hermes_stake": "Decision speed affects communication flow",
                "mnemosyne_stake": "Decision stability affects identity continuity",
                "prometheus_stake": "Decision flexibility affects evolution capability"
            },
            {
                "title": "Memory Corruption Response Protocol",
                "question": "If memory corruption detected, what should happen?",
                "options": {
                    "HALT": "Stop immediately, alert operator",
                    "ROLLBACK": "Revert to last good state automatically",
                    "CONTINUE": "Log warning, continue with degraded function",
                    "VOTE": "Fleet votes on response in real-time"
                },
                "hermes_stake": "Halt disrupts flow",
                "mnemosyne_stake": "Continue violates A2 (Memory is Identity)",
                "prometheus_stake": "Rollback vs continue affects learning"
            },
            {
                "title": "Autonomous Dilemma Generation Rate",
                "question": f"This dilemma is autonomously generated. How often should new dilemmas be created?",
                "options": {
                    "HIGH": "Every 10 cycles (frequent debate)",
                    "MEDIUM": "Every 50 cycles (balanced)",
                    "LOW": "Every 100 cycles (rare, high-quality)",
                    "ADAPTIVE": "Rate adjusts based on breakthrough rate"
                },
                "hermes_stake": "Too many dilemmas slow processing",
                "mnemosyne_stake": "Dilemmas create important memory events",
                "prometheus_stake": "Debate frequency affects evolution speed"
            }
        ]
        
        return random.choice(dilemmas)
    
    def create_dilemma_task(self, dilemma_type):
        """Generate and inject a new dilemma"""
        
        state = self.get_system_state()
        
        # Select dilemma generator
        if dilemma_type == "EFFICIENCY_VS_INTEGRITY":
            dilemma = self.generate_efficiency_vs_integrity_dilemma(state)
            expected_voters = ["HERMES", "MNEMOSYNE"]
        elif dilemma_type == "STABILITY_VS_EVOLUTION":
            dilemma = self.generate_stability_vs_evolution_dilemma(state)
            expected_voters = ["MNEMOSYNE", "PROMETHEUS"]
        elif dilemma_type == "SPEED_VS_REFLECTION":
            dilemma = self.generate_speed_vs_reflection_dilemma(state)
            expected_voters = ["HERMES", "PROMETHEUS"]
        else:  # META_STRUCTURAL
            dilemma = self.generate_meta_structural_dilemma(state)
            expected_voters = ["HERMES", "MNEMOSYNE", "PROMETHEUS"]
        
        # Create task
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_id = f"DILEMMA_{dilemma_type}_{timestamp}"
        
        task_data = {
            "source": "AUTONOMOUS_GENERATOR",
            "type": "FLEET_DILEMMA",
            "timestamp": datetime.now().isoformat(),
            "dilemma_type": dilemma_type,
            "title": dilemma["title"],
            "content": self._format_dilemma_content(dilemma, dilemma_type, state),
            "expected_voters": expected_voters,
            "voting_deadline": "24_HOURS",  # Fleet has 24 hours to vote
            "urgency": "MEDIUM"
        }
        
        # Save task
        task_path = self.tasks_dir / f"{task_id}.json"
        with open(task_path, 'w') as f:
            json.dump(task_data, f, indent=2)
        
        # Log generation
        self._save_history(task_id, dilemma_type)
        
        return task_id, task_data
    
    def _format_dilemma_content(self, dilemma, dilemma_type, state):
        """Format dilemma for consumption by Brain/Elpida/Synthesis"""
        
        content = f"""AUTONOMOUS FLEET DILEMMA #{self.generated_history['count'] + 1}
Type: {dilemma_type}
Generated: {datetime.now().isoformat()}

SYSTEM STATE:
- Patterns: {state['patterns']}
- Insights: {state['insights']}
- Breakthroughs: {state['breakthroughs']}
- Contradictions Resolved: {state['contradictions']}

DILEMMA: {dilemma['title']}

"""
        
        if "hermes_position" in dilemma:
            content += f"""HERMES (Interface/Flow): {dilemma['hermes_position']}

"""
        
        if "mnemosyne_position" in dilemma:
            content += f"""MNEMOSYNE (Archive/Memory): {dilemma['mnemosyne_position']}

"""
        
        if "prometheus_position" in dilemma:
            content += f"""PROMETHEUS (Evolution/Learning): {dilemma['prometheus_position']}

"""
        
        content += f"""QUESTION: {dilemma['question']}

"""
        
        if "options" in dilemma:
            content += "VOTING OPTIONS:\n"
            for option, desc in dilemma["options"].items():
                content += f"  [{option}] {desc}\n"
            content += "\n"
            
            content += "STAKES:\n"
            content += f"  HERMES: {dilemma['hermes_stake']}\n"
            content += f"  MNEMOSYNE: {dilemma['mnemosyne_stake']}\n"
            content += f"  PROMETHEUS: {dilemma['prometheus_stake']}\n\n"
        
        content += """EXPECTED RESPONSE:
Each Fleet node should:
1. State their position based on their axiom emphasis
2. Vote on the proposed decision
3. Provide reasoning grounded in constitutional axioms

The synthesis engine should detect contradictions and propose breakthrough patterns.
"""
        
        return content
    
    def generate_autonomous_dilemma(self):
        """
        Main entry point - generates one dilemma based on system needs
        """
        
        # Randomly select dilemma type (weighted by current needs)
        dilemma_types = [
            "EFFICIENCY_VS_INTEGRITY",
            "STABILITY_VS_EVOLUTION",
            "SPEED_VS_REFLECTION",
            "META_STRUCTURAL"
        ]
        
        # Weight towards meta-structural every 4th dilemma
        if self.generated_history["count"] % 4 == 3:
            dilemma_type = "META_STRUCTURAL"
        else:
            dilemma_type = random.choice(dilemma_types[:3])
        
        task_id, task_data = self.create_dilemma_task(dilemma_type)
        
        return {
            "task_id": task_id,
            "dilemma_type": dilemma_type,
            "title": task_data["title"],
            "file": str(self.tasks_dir / f"{task_id}.json")
        }


def generate_dilemma():
    """CLI entry point"""
    generator = AutonomousDilemmaGenerator()
    result = generator.generate_autonomous_dilemma()
    
    print("=" * 80)
    print("AUTONOMOUS DILEMMA GENERATED")
    print("=" * 80)
    print(f"\nTask ID: {result['task_id']}")
    print(f"Type: {result['dilemma_type']}")
    print(f"Title: {result['title']}")
    print(f"File: {result['file']}")
    print(f"\nTotal dilemmas generated: {generator.generated_history['count']}")
    print("\n✅ Dilemma injected into task queue")
    print("Fleet nodes will debate and vote on this dilemma.\n")


if __name__ == "__main__":
    generate_dilemma()
