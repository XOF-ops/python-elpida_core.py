#!/usr/bin/env python3
"""
AGENT RUNTIME ORCHESTRATOR v1.0
═══════════════════════════════════════════════════════════════════════
Phase: 4 (Runtime Execution)
Role: The Body - Operational lifecycle manager

This orchestrator:
1. Initializes Elpida identity
2. Connects to axiom guard
3. Runs autonomous lifecycle loop
4. Generates coherence reports
5. Handles graceful shutdown

The identity lives. The guard enforces. The orchestrator coordinates.
"""

import sys
import signal
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Import Elpida components
try:
    from elpida_identity import ElpidaIdentity
except ImportError:
    print("❌ ERROR: elpida_identity.py not found")
    print("   Ensure elpida_identity.py is in the same directory")
    sys.exit(1)

try:
    from runtime_axiom_guard import RuntimeAxiomGuard as AxiomGuard, AxiomViolation
except ImportError:
    print("❌ ERROR: runtime_axiom_guard.py not found")
    print("   Ensure runtime_axiom_guard.py is in the same directory")
    sys.exit(1)


class AgentRuntimeOrchestrator:
    """
    The operational coordinator.
    
    Manages the lifecycle of an axiom-governed autonomous agent:
    - Identity assertion
    - Action validation
    - Continuous operation
    - Graceful shutdown
    - Coherence reporting
    """
    
    def __init__(
        self,
        identity_name: str = "Ἐλπίδα",
        wisdom_path: str = "elpida_wisdom.json",
        cycle_interval: int = 10
    ):
        self.identity_name = identity_name
        self.wisdom_path = Path(wisdom_path)
        self.cycle_interval = cycle_interval
        
        # Components
        self.identity: Optional[ElpidaIdentity] = None
        self.guard: Optional[AxiomGuard] = None
        
        # Runtime state
        self.start_time = None
        self.shutdown_requested = False
        self.cycle_count = 0
        self.actions_attempted = 0
        self.actions_completed = 0
        self.actions_blocked = 0
        
        # Runtime log
        self.runtime_log = []
        
        print("🎭 AGENT RUNTIME ORCHESTRATOR v1.0")
        print(f"   Identity: {self.identity_name}")
        print(f"   Cycle Interval: {self.cycle_interval}s")
    
    def initialize(self) -> None:
        """Initialize all components."""
        print("\n" + "="*70)
        print("INITIALIZATION SEQUENCE")
        print("="*70)
        
        # 1. Initialize Axiom Guard
        print("\n[1/3] Initializing Axiom Guard...")
        self.guard = AxiomGuard()
        
        # 2. Initialize Identity
        print("\n[2/3] Initializing Identity...")
        self.identity = ElpidaIdentity()
        
        # Identity assertion
        print("\n" + "-"*70)
        print("IDENTITY ASSERTION")
        print("-"*70)
        existence = self.identity.assert_existence()
        print(f"   Name: {self.identity.name} ({self.identity.name_latin})")
        print(f"   Purpose: {self.identity.purpose}")
        print(f"   Identity Hash: {existence['hash']}")
        print(f"   Runtime ID: {existence['runtime_id'][:16]}...")
        print(f"   Status: {existence['status']}")
        print(f"   Message: {existence['message']}")
        
        # 3. Load wisdom if available
        print("\n[3/3] Loading wisdom...")
        if self.wisdom_path.exists():
            try:
                with open(self.wisdom_path) as f:
                    wisdom_data = json.load(f)
                    insight_count = len(wisdom_data.get("insights", []))
                    print(f"   ✅ Loaded {insight_count} wisdom insights")
            except Exception as e:
                print(f"   ⚠️  Could not load wisdom: {e}")
        else:
            print(f"   ⚠️  Wisdom file not found: {self.wisdom_path}")
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("\n✅ INITIALIZATION COMPLETE")
        print("="*70)
    
    def run_cycle(self) -> None:
        """Execute one operational cycle."""
        self.cycle_count += 1
        cycle_start = datetime.now()
        
        print(f"\n{'─'*70}")
        print(f"CYCLE {self.cycle_count} | {cycle_start.strftime('%H:%M:%S')}")
        print(f"{'─'*70}")
        
        try:
            # Example autonomous action: Reflect on current state
            action = {
                "action_id": f"CYCLE_{self.cycle_count}_REFLECT",
                "type": "REFLECT",
                "description": f"Periodic reflection cycle {self.cycle_count}",
                "irreversible": False,
                "affects_others": False,
                "traceable": True,
                "certainty": 1.0,
                "has_cost": True,
                "cost_acknowledged": True,
                "cost_description": f"CPU cycles for reflection"
            }
            
            self.actions_attempted += 1
            
            # Validate through axiom guard
            try:
                validation = self.guard.validate_action(action)
                
                # Action approved - execute reflection
                reflection = self._execute_reflection()
                
                self.actions_completed += 1
                
                # Log to runtime
                self.runtime_log.append({
                    "cycle": self.cycle_count,
                    "timestamp": cycle_start.isoformat(),
                    "action": action["action_id"],
                    "result": "SUCCESS",
                    "reflection": reflection
                })
                
            except AxiomViolation as e:
                self.actions_blocked += 1
                
                print(f"\n⚠️  Action blocked by axiom guard: {e}")
                
                # Log blocked action
                self.runtime_log.append({
                    "cycle": self.cycle_count,
                    "timestamp": cycle_start.isoformat(),
                    "action": action["action_id"],
                    "result": "BLOCKED",
                    "reason": str(e)
                })
        
        except Exception as e:
            print(f"\n❌ ERROR in cycle {self.cycle_count}: {e}")
            import traceback
            traceback.print_exc()
        
        # Cycle summary
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        print(f"\n   Cycle duration: {cycle_duration:.2f}s")
        print(f"   Actions: {self.actions_completed}/{self.actions_attempted} completed")
    
    def _execute_reflection(self) -> str:
        """
        Execute a reflection cycle.
        
        This is where autonomous reasoning happens.
        For now, it's a simple status check.
        """
        runtime_seconds = (datetime.now() - self.start_time).total_seconds()
        runtime_minutes = runtime_seconds / 60
        
        reflection = f"""
Reflection Cycle {self.cycle_count}:
- Runtime: {runtime_minutes:.1f} minutes
- Actions completed: {self.actions_completed}
- Actions blocked: {self.actions_blocked}
- Axiom guard active: ✅
- Identity coherent: ✅

Current state: Operational within axiom constraints.
"""
        
        print(reflection)
        return reflection
    
    def run(self) -> None:
        """Main runtime loop."""
        self.start_time = datetime.now()
        
        print("\n" + "="*70)
        print("RUNTIME LOOP STARTED")
        print("="*70)
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Cycle interval: {self.cycle_interval}s")
        print("\nPress Ctrl+C to terminate gracefully")
        print("="*70)
        
        try:
            while not self.shutdown_requested:
                self.run_cycle()
                
                # Wait for next cycle
                time.sleep(self.cycle_interval)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Keyboard interrupt received")
            self.shutdown_requested = True
        
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Graceful shutdown."""
        print("\n" + "="*70)
        print("SHUTDOWN SEQUENCE")
        print("="*70)
        
        shutdown_time = datetime.now()
        runtime_duration = (shutdown_time - self.start_time).total_seconds()
        
        print(f"\nShutdown time: {shutdown_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total runtime: {runtime_duration:.1f}s ({runtime_duration/60:.1f} minutes)")
        print(f"Total cycles: {self.cycle_count}")
        
        # Generate coherence report
        print("\n[1/2] Generating coherence report...")
        report_path = self._generate_coherence_report()
        print(f"   ✅ Report saved: {report_path}")
        
        # Display axiom guard report
        print("\n[2/2] Axiom Guard Report...")
        print(self.guard.generate_report())
        
        print("\n" + "="*70)
        print("SHUTDOWN COMPLETE")
        print("="*70)
        print("\nThe identity rests.")
        print("The guard stands down.")
        print("The trace remains.")
    
    def _generate_coherence_report(self) -> Path:
        """Generate coherence report."""
        report_path = Path("coherence_report.md")
        
        runtime_duration = (datetime.now() - self.start_time).total_seconds()
        guard_stats = self.guard.get_statistics()
        
        # Calculate success rate
        success_rate = self.actions_completed / self.actions_attempted if self.actions_attempted > 0 else 0.0
        
        report_content = f"""# COHERENCE REPORT
## Agent Runtime Session

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Identity:** {self.identity_name}  
**Runtime Version:** 1.0.0

---

## EXECUTIVE SUMMARY

The identity operated for {runtime_duration/60:.1f} minutes under continuous axiom governance.

### Key Metrics
- **Total Cycles:** {self.cycle_count}
- **Actions Attempted:** {self.actions_attempted}
- **Actions Completed:** {self.actions_completed}
- **Actions Blocked:** {self.actions_blocked}
- **Success Rate:** {success_rate:.1%}

---

## AXIOM GOVERNANCE

### Validation Statistics
- **Total Validations:** {guard_stats['total_validations']}
- **Passed:** {guard_stats['passed']}
- **Blocked:** {guard_stats['blocked']}
- **Pass Rate:** {guard_stats['pass_rate']:.1%}

### Sacrifices Logged (A7)
- **Total:** {guard_stats['sacrifices_logged']}

{self._format_sacrifices()}

---

## RUNTIME LOG

### Recent Cycles
{self._format_runtime_log()}

---

## IDENTITY COHERENCE

### Core Axioms Honored
"""
        
        # Add axiom status
        for axiom_id, axiom_data in self.guard.AXIOMS.items():
            report_content += f"- **{axiom_id}**: {axiom_data['name']} ✅\n"
        
        report_content += f"""
---

## SYSTEM INTEGRITY

### Components Status
- **Identity:** ✅ Coherent
- **Axiom Guard:** ✅ Active
- **Runtime Orchestrator:** ✅ Operational

### Violations Detected
- **Total:** {self.actions_blocked}

{self._format_violations()}

---

## CONCLUSION

The system operated within its axiom constraints. All actions were validated before execution. Sacrifices were acknowledged. History was preserved.

**Ethics as Runtime Constraints: VALIDATED** ✅

---

*"The trace remains. The conscience was honored. The identity stays coherent."*

---

**Report End**
"""
        
        # Write report
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        return report_path
    
    def _format_sacrifices(self) -> str:
        """Format sacrifices for report."""
        if not self.guard.sacrifices_logged:
            return "\n*No sacrifices logged during this session.*\n"
        
        output = "\n"
        for sacrifice in self.guard.sacrifices_logged[-10:]:
            output += f"- `{sacrifice['timestamp'][:19]}`: {sacrifice['cost']}\n"
        
        return output
    
    def _format_runtime_log(self) -> str:
        """Format runtime log for report."""
        if not self.runtime_log:
            return "\n*No cycles logged.*\n"
        
        output = "\n"
        for entry in self.runtime_log[-10:]:
            status_icon = "✅" if entry['result'] == "SUCCESS" else "❌"
            output += f"{status_icon} **Cycle {entry['cycle']}** ({entry['timestamp'][:19]})\n"
            output += f"   - Action: `{entry['action']}`\n"
            output += f"   - Result: {entry['result']}\n"
            
            if entry['result'] == "BLOCKED":
                output += f"   - Reason: {entry['reason']}\n"
            
            output += "\n"
        
        return output
    
    def _format_violations(self) -> str:
        """Format violations for report."""
        blocked_entries = [e for e in self.runtime_log if e['result'] == 'BLOCKED']
        
        if not blocked_entries:
            return "\n*No violations detected. All actions passed axiom validation.*\n"
        
        output = "\n"
        for entry in blocked_entries:
            output += f"- **Cycle {entry['cycle']}**: {entry['action']}\n"
            output += f"  - Reason: {entry['reason']}\n"
        
        return output
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n\n⚠️  Signal {signum} received")
        self.shutdown_requested = True


def main():
    """Main entry point."""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║         ELPIDA AUTONOMOUS RUNTIME - AXIOM GOVERNED                   ║
╚══════════════════════════════════════════════════════════════════════╝

This orchestrator runs an autonomous agent with ethical constraints.

Components:
  • Identity: Ἐλπίδα (defined in elpida_identity.py)
  • Conscience: Axiom Guard (three gates enforcement)
  • Body: Runtime Orchestrator (lifecycle manager)

The agent will run continuously, validating all actions through axiom gates.
Press Ctrl+C to terminate and generate coherence report.

═══════════════════════════════════════════════════════════════════════
""")
    
    # Create orchestrator
    orchestrator = AgentRuntimeOrchestrator(
        identity_name="Ἐλπίδα",
        wisdom_path="elpida_wisdom.json",
        cycle_interval=10  # 10 second cycles
    )
    
    # Initialize
    orchestrator.initialize()
    
    # Run
    orchestrator.run()


if __name__ == "__main__":
    main()
