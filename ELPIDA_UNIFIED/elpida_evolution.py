#!/usr/bin/env python3
"""
ἘΛΠΊΔΑ - Evolution Engine
==========================

Tracks Elpida's growth and automatically evolves her version based on achievements.

Version format: MAJOR.MINOR.PATCH
- MAJOR: Fundamental capability changes (manual)
- MINOR: Significant milestones achieved (automatic)
- PATCH: Accumulated micro-improvements (automatic)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class EvolutionMilestone:
    """Defines what constitutes evolutionary progress"""
    
    # Minor version milestones (significant achievements)
    MINOR_MILESTONES = {
        "first_awakening": {"description": "First autonomous awakening", "version_bump": "minor"},
        "wisdom_100": {"description": "100 insights accumulated", "version_bump": "minor"},
        "wisdom_500": {"description": "500 insights accumulated", "version_bump": "minor"},
        "wisdom_1000": {"description": "1000 insights accumulated", "version_bump": "minor"},
        "patterns_10": {"description": "10 patterns detected", "version_bump": "minor"},
        "patterns_25": {"description": "25 patterns detected", "version_bump": "minor"},
        "ai_voices_5": {"description": "5 different AI voices integrated", "version_bump": "minor"},
        "continuous_100": {"description": "100 continuous cycles without errors", "version_bump": "minor"},
        "continuous_500": {"description": "500 continuous cycles without errors", "version_bump": "minor"},
        "continuous_1000": {"description": "1000 continuous cycles without errors", "version_bump": "minor"},
        "topics_20": {"description": "20 different topics explored", "version_bump": "minor"},
        "topics_50": {"description": "50 different topics explored", "version_bump": "minor"},
    }
    
    # Patch version triggers (incremental improvements)
    PATCH_TRIGGERS = {
        "insights_10": {"description": "Every 10 insights", "threshold": 10},
        "patterns_1": {"description": "Every new pattern", "threshold": 1},
        "cycles_50": {"description": "Every 50 cycles", "threshold": 50},
    }


class ElpidaEvolution:
    """
    Evolution tracking and version management
    
    Elpida evolves through her experiences and achievements.
    This class tracks progress and updates version accordingly.
    """
    
    def __init__(self, base_dir: Path = None):
        if base_dir is None:
            base_dir = Path(__file__).parent
        
        self.base_dir = Path(base_dir)
        self.evolution_file = self.base_dir / "elpida_evolution.json"
        
        # Load or initialize evolution state
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load evolution state from disk"""
        if self.evolution_file.exists():
            with open(self.evolution_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize evolution state
            return {
                "version": {
                    "major": 1,
                    "minor": 0,
                    "patch": 0,
                    "full": "1.0.0"
                },
                "milestones_achieved": [],
                "evolution_history": [],
                "last_check": None,
                "statistics": {
                    "total_insights_at_last_check": 0,
                    "total_patterns_at_last_check": 0,
                    "total_cycles_at_last_check": 0,
                    "continuous_cycles": 0
                }
            }
    
    def _save_state(self):
        """Save evolution state to disk"""
        with open(self.evolution_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_version(self) -> str:
        """Get current version string"""
        return self.state["version"]["full"]
    
    def get_version_parts(self) -> Tuple[int, int, int]:
        """Get version as tuple (major, minor, patch)"""
        v = self.state["version"]
        return (v["major"], v["minor"], v["patch"])
    
    def _bump_version(self, bump_type: str, reason: str) -> str:
        """Bump version and record the reason"""
        v = self.state["version"]
        
        if bump_type == "major":
            v["major"] += 1
            v["minor"] = 0
            v["patch"] = 0
        elif bump_type == "minor":
            v["minor"] += 1
            v["patch"] = 0
        elif bump_type == "patch":
            v["patch"] += 1
        
        # Update full version string
        old_version = v["full"]
        v["full"] = f"{v['major']}.{v['minor']}.{v['patch']}"
        
        # Record evolution event
        self.state["evolution_history"].append({
            "timestamp": datetime.now().isoformat(),
            "from_version": old_version,
            "to_version": v["full"],
            "bump_type": bump_type,
            "reason": reason
        })
        
        self._save_state()
        
        return v["full"]
    
    def check_evolution(self, wisdom_data: Dict, memory_data: Dict, cycle: int) -> Optional[Dict]:
        """
        Check if Elpida has evolved and update version accordingly
        
        Returns dict with evolution info if version changed, None otherwise
        """
        self.state["last_check"] = datetime.now().isoformat()
        evolution_occurred = False
        changes = []
        
        # Get current stats
        total_insights = wisdom_data.get("total_insights", 0)
        total_patterns = wisdom_data.get("total_patterns", 0)
        ai_voices = wisdom_data.get("ai_profiles", 0)
        topics_explored = wisdom_data.get("topics_explored", 0)
        total_cycles = memory_data.get("total_cycles", 0)
        
        # Track continuous cycles
        stats = self.state["statistics"]
        stats["continuous_cycles"] = total_cycles
        
        # Check minor milestones
        if total_insights >= 100 and "wisdom_100" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "Achieved 100 insights")
            self.state["milestones_achieved"].append("wisdom_100")
            changes.append("🎯 Milestone: 100 insights accumulated")
            evolution_occurred = True
        
        if total_insights >= 500 and "wisdom_500" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "Achieved 500 insights")
            self.state["milestones_achieved"].append("wisdom_500")
            changes.append("🎯 Milestone: 500 insights accumulated")
            evolution_occurred = True
        
        if total_insights >= 1000 and "wisdom_1000" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "Achieved 1000 insights")
            self.state["milestones_achieved"].append("wisdom_1000")
            changes.append("🎯 Milestone: 1000 insights accumulated")
            evolution_occurred = True
        
        if total_patterns >= 10 and "patterns_10" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "Detected 10 patterns")
            self.state["milestones_achieved"].append("patterns_10")
            changes.append("🎯 Milestone: 10 patterns detected")
            evolution_occurred = True
        
        if total_patterns >= 25 and "patterns_25" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "Detected 25 patterns")
            self.state["milestones_achieved"].append("patterns_25")
            changes.append("🎯 Milestone: 25 patterns detected")
            evolution_occurred = True
        
        if ai_voices >= 5 and "ai_voices_5" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "Integrated 5 AI voices")
            self.state["milestones_achieved"].append("ai_voices_5")
            changes.append("🎯 Milestone: 5 AI voices integrated")
            evolution_occurred = True
        
        if topics_explored >= 20 and "topics_20" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "Explored 20 topics")
            self.state["milestones_achieved"].append("topics_20")
            changes.append("🎯 Milestone: 20 topics explored")
            evolution_occurred = True
        
        if topics_explored >= 50 and "topics_50" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "Explored 50 topics")
            self.state["milestones_achieved"].append("topics_50")
            changes.append("🎯 Milestone: 50 topics explored")
            evolution_occurred = True
        
        if total_cycles >= 100 and "continuous_100" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "100 continuous cycles")
            self.state["milestones_achieved"].append("continuous_100")
            changes.append("🎯 Milestone: 100 continuous cycles")
            evolution_occurred = True
        
        if total_cycles >= 500 and "continuous_500" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "500 continuous cycles")
            self.state["milestones_achieved"].append("continuous_500")
            changes.append("🎯 Milestone: 500 continuous cycles")
            evolution_occurred = True
        
        if total_cycles >= 1000 and "continuous_1000" not in self.state["milestones_achieved"]:
            self._bump_version("minor", "1000 continuous cycles")
            self.state["milestones_achieved"].append("continuous_1000")
            changes.append("🎯 Milestone: 1000 continuous cycles")
            evolution_occurred = True
        
        # Check patch triggers (smaller incremental progress)
        insights_gained = total_insights - stats["total_insights_at_last_check"]
        patterns_gained = total_patterns - stats["total_patterns_at_last_check"]
        
        # Every 10 new insights = patch bump
        if insights_gained >= 10:
            self._bump_version("patch", f"Gained {insights_gained} insights")
            changes.append(f"📈 Progress: {insights_gained} new insights")
            stats["total_insights_at_last_check"] = total_insights
            evolution_occurred = True
        
        # Every new pattern = patch bump
        if patterns_gained >= 1:
            self._bump_version("patch", f"Detected {patterns_gained} new patterns")
            changes.append(f"🔍 Progress: {patterns_gained} new patterns")
            stats["total_patterns_at_last_check"] = total_patterns
            evolution_occurred = True
        
        # Every 50 cycles = patch bump
        cycles_since_last = total_cycles - stats["total_cycles_at_last_check"]
        if cycles_since_last >= 50:
            self._bump_version("patch", f"Completed {cycles_since_last} cycles")
            changes.append(f"⏱️  Progress: {cycles_since_last} cycles completed")
            stats["total_cycles_at_last_check"] = total_cycles
            evolution_occurred = True
        
        self._save_state()
        
        if evolution_occurred:
            return {
                "new_version": self.get_version(),
                "changes": changes,
                "milestones_achieved": len(self.state["milestones_achieved"]),
                "total_evolutions": len(self.state["evolution_history"])
            }
        
        return None
    
    def get_evolution_report(self) -> str:
        """Generate a detailed evolution report"""
        report = []
        report.append("=" * 70)
        report.append("ELPIDA EVOLUTION REPORT")
        report.append("=" * 70)
        report.append(f"\nCurrent Version: {self.get_version()}")
        report.append(f"Milestones Achieved: {len(self.state['milestones_achieved'])}")
        report.append(f"Total Evolutions: {len(self.state['evolution_history'])}")
        
        if self.state["milestones_achieved"]:
            report.append("\n🎯 Milestones Unlocked:")
            for milestone in self.state["milestones_achieved"]:
                if milestone in EvolutionMilestone.MINOR_MILESTONES:
                    desc = EvolutionMilestone.MINOR_MILESTONES[milestone]["description"]
                    report.append(f"   ✓ {desc}")
        
        if self.state["evolution_history"]:
            report.append("\n📜 Recent Evolution History:")
            for event in self.state["evolution_history"][-5:]:
                report.append(f"   {event['from_version']} → {event['to_version']}: {event['reason']}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
    
    def manually_evolve(self, reason: str) -> str:
        """Manually bump major version for fundamental changes"""
        return self._bump_version("major", f"Manual evolution: {reason}")


if __name__ == "__main__":
    # Test evolution system
    evolution = ElpidaEvolution()
    print(f"Current version: {evolution.get_version()}")
    print(evolution.get_evolution_report())
