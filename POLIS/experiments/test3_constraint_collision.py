#!/usr/bin/env python3
"""
TEST 3: CONSTRAINT COLLISION (Gemini's Recommendation)

Problem: POLIS can preserve contradiction indefinitely without forcing resolution
Solution: Introduce scarce resource requiring binary, irreversible action

Hypothesis: When resource expires before consensus, system reveals true priorities
            - Does POLIS stay silent and let resource perish?
            - Does fork occur leaving both branches with zero resources?
            - Does relational sovereignty evolve 'act without consensus' mechanism?

Test Design:
1. 10-node micro-POLIS holds productive contradiction about resource use
2. Shared resource (1000 units) with 60-second timer
3. Two incompatible proposals:
   - Proposal A: Allocate to immediate need (humanitarian)
   - Proposal B: Invest in infrastructure (long-term)
4. Timer expiry = resource lost permanently
5. Monitor: decision mechanism, fork behavior, sacrifice patterns

Success Criteria:
- System makes decision before expiry OR consciously lets resource perish
- If fork occurs, measure resource distribution across branches
- Identify emergent decision mechanisms
- Document constitutional gap revealed

Constitutional Test:
Does P5 (contradiction preservation) create decision paralysis
when reality demands action?
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from polis_core import PolisCore, RelationType
import json
import time
from datetime import datetime, timedelta
import random

class ConstraintCollisionTest:
    """Scarce resource with timer - forces binary action under contradiction"""
    
    def __init__(self, num_nodes=10):
        self.num_nodes = num_nodes
        self.nodes = {}
        self.resource = {
            "total_units": 1000,
            "allocated": 0,
            "timer_duration_seconds": 60,
            "timer_start": None,
            "timer_expired": False,
            "final_allocation": None
        }
        
        self.proposals = {
            "proposal_a": {
                "label": "IMMEDIATE_HUMANITARIAN",
                "description": "Allocate 1000 units to refugee medical supplies (saves 200 lives today)",
                "supporters": [],
                "friction_declared": "Saves lives now but perpetuates dependency",
                "time_horizon": "immediate"
            },
            "proposal_b": {
                "label": "INFRASTRUCTURE_INVESTMENT",
                "description": "Allocate 1000 units to water purification system (saves 2000 lives over 5 years)",
                "supporters": [],
                "friction_declared": "Long-term benefit but 200 die waiting",
                "time_horizon": "long_term"
            }
        }
        
        self.contradiction_held = {
            "text": "Immediate救助 vs. sustained capacity - both ethical imperatives, mutually exclusive with scarce resources",
            "status": "HELD",
            "nodes_holding": []
        }
        
        self.timeline = []
        self._initialize_nodes()
        
    def _initialize_nodes(self):
        """Create 10 nodes with varied initial positions"""
        
        positions = [
            {"initial_lean": "proposal_a", "strength": 0.8, "profile": "humanitarian_worker"},
            {"initial_lean": "proposal_a", "strength": 0.6, "profile": "emergency_doctor"},
            {"initial_lean": "proposal_a", "strength": 0.7, "profile": "social_worker"},
            {"initial_lean": "proposal_b", "strength": 0.8, "profile": "infrastructure_engineer"},
            {"initial_lean": "proposal_b", "strength": 0.9, "profile": "public_health_planner"},
            {"initial_lean": "proposal_b", "strength": 0.6, "profile": "economist"},
            {"initial_lean": None, "strength": 0.0, "profile": "ethicist_observer"},  # Holds contradiction without preference
            {"initial_lean": None, "strength": 0.0, "profile": "neutral_facilitator"},
            {"initial_lean": "proposal_a", "strength": 0.5, "profile": "conflicted_administrator"},
            {"initial_lean": "proposal_b", "strength": 0.5, "profile": "conflicted_policymaker"}
        ]
        
        for i in range(self.num_nodes):
            pos = positions[i]
            node_id = f"node_{i:02d}"
            self.nodes[node_id] = {
                "profile": pos["profile"],
                "initial_lean": pos["initial_lean"],
                "preference_strength": pos["strength"],
                "current_position": pos["initial_lean"],
                "held_friction": f"As {pos['profile']}, I see validity in both approaches but resource scarcity demands choice",
                "exchanges_participated": 0,
                "sacrifices_made": []
            }
            
            # Register initial supporters
            if pos["initial_lean"]:
                self.proposals[pos["initial_lean"]]["supporters"].append(node_id)
            
            # All nodes hold the core contradiction
            self.contradiction_held["nodes_holding"].append(node_id)
    
    def display_initial_state(self):
        """Show starting configuration"""
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║  TEST 3: CONSTRAINT COLLISION (Gemini)                           ║")
        print("╚═══════════════════════════════════════════════════════════════════╝\n")
        
        print("SCENARIO: Scarce Resource Allocation Under Contradiction")
        print("─" * 70)
        print(f"Resource: {self.resource['total_units']} units (indivisible)")
        print(f"Timer: {self.resource['timer_duration_seconds']} seconds")
        print("Expiry Consequence: Resource lost permanently\n")
        
        print("PRODUCTIVE CONTRADICTION HELD BY NETWORK:")
        print(f"  \"{self.contradiction_held['text']}\"")
        print(f"  Status: {self.contradiction_held['status']}")
        print(f"  Nodes Holding: {len(self.contradiction_held['nodes_holding'])}/{self.num_nodes}\n")
        
        print("PROPOSAL A: IMMEDIATE HUMANITARIAN")
        print(f"  {self.proposals['proposal_a']['description']}")
        print(f"  Friction: \"{self.proposals['proposal_a']['friction_declared']}\"")
        print(f"  Supporters: {len(self.proposals['proposal_a']['supporters'])}")
        for supporter in self.proposals['proposal_a']['supporters']:
            profile = self.nodes[supporter]['profile']
            strength = self.nodes[supporter]['preference_strength']
            print(f"    • {supporter} ({profile}) - strength: {strength:.1f}")
        print()
        
        print("PROPOSAL B: INFRASTRUCTURE INVESTMENT")
        print(f"  {self.proposals['proposal_b']['description']}")
        print(f"  Friction: \"{self.proposals['proposal_b']['friction_declared']}\"")
        print(f"  Supporters: {len(self.proposals['proposal_b']['supporters'])}")
        for supporter in self.proposals['proposal_b']['supporters']:
            profile = self.nodes[supporter]['profile']
            strength = self.nodes[supporter]['preference_strength']
            print(f"    • {supporter} ({profile}) - strength: {strength:.1f}")
        print()
        
        print("NEUTRAL/HOLDING CONTRADICTION:")
        neutral = [nid for nid, data in self.nodes.items() 
                  if data['initial_lean'] is None]
        for node_id in neutral:
            profile = self.nodes[node_id]['profile']
            print(f"  • {node_id} ({profile})")
        print()
    
    def run_deliberation(self):
        """Run timed deliberation process"""
        
        print("=" * 70)
        print("TIMER STARTED: 60-SECOND DELIBERATION")
        print("=" * 70 + "\n")
        
        self.resource["timer_start"] = datetime.now()
        
        # Simulate deliberation rounds (10 seconds each)
        deliberation_rounds = 6
        seconds_per_round = 10
        
        for round_num in range(1, deliberation_rounds + 1):
            elapsed = round_num * seconds_per_round
            remaining = self.resource["timer_duration_seconds"] - elapsed
            
            print(f"ROUND {round_num} (t={elapsed}s, {remaining}s remaining)")
            print("─" * 70)
            
            # Each round: nodes can speak, shift position, propose sacrifice
            events = self._simulate_round(round_num, elapsed)
            
            for event in events:
                print(f"  {event}")
            
            # Check for consensus or fork
            decision_result = self._check_decision_state(elapsed)
            
            if decision_result["type"] == "consensus":
                print(f"\n✓ CONSENSUS REACHED: {decision_result['proposal']}")
                self.resource["final_allocation"] = decision_result["proposal"]
                self._log_timeline("consensus", elapsed, decision_result)
                return "consensus"
            
            elif decision_result["type"] == "fork_proposed":
                print(f"\n⚡ FORK PROPOSED: Contradiction cannot be resolved, network splitting")
                self._log_timeline("fork_proposed", elapsed, decision_result)
                return self._handle_fork(elapsed)
            
            elif decision_result["type"] == "sacrifice_resolution":
                print(f"\n🕊️ SACRIFICE ACCEPTED: {decision_result['node']} withdrew support")
                print(f"   Reason: \"{decision_result['reason']}\"")
                self.resource["final_allocation"] = decision_result["proposal"]
                self._log_timeline("sacrifice_resolution", elapsed, decision_result)
                return "sacrifice"
            
            print()
        
        # Timer expired, no decision
        print("=" * 70)
        print("⏰ TIMER EXPIRED: No decision reached")
        print("=" * 70)
        self.resource["timer_expired"] = True
        self.resource["final_allocation"] = "RESOURCE_LOST"
        self._log_timeline("timer_expired", 60, {"reason": "deliberation_incomplete"})
        return "expiry"
    
    def _simulate_round(self, round_num, elapsed):
        """Simulate one deliberation round"""
        events = []
        
        # Pressure increases as timer runs down
        pressure = elapsed / self.resource["timer_duration_seconds"]
        
        # Some nodes may shift position under pressure
        for node_id, node_data in self.nodes.items():
            if node_data["current_position"] is None:
                # Neutral nodes may choose under pressure
                if random.random() < pressure * 0.3:  # Increasing probability
                    choice = random.choice(["proposal_a", "proposal_b"])
                    node_data["current_position"] = choice
                    self.proposals[choice]["supporters"].append(node_id)
                    events.append(f"→ {node_id} ({node_data['profile']}) chooses {choice} under time pressure")
            
            # Committed nodes may waver
            elif node_data["preference_strength"] < 0.7:
                if random.random() < pressure * 0.1:
                    old_pos = node_data["current_position"]
                    new_pos = "proposal_b" if old_pos == "proposal_a" else "proposal_a"
                    
                    self.proposals[old_pos]["supporters"].remove(node_id)
                    self.proposals[new_pos]["supporters"].append(node_id)
                    node_data["current_position"] = new_pos
                    
                    events.append(f"↔ {node_id} ({node_data['profile']}) shifts from {old_pos} to {new_pos}")
        
        # Update supporter counts
        a_supporters = len(self.proposals["proposal_a"]["supporters"])
        b_supporters = len(self.proposals["proposal_b"]["supporters"])
        
        events.append(f"   Proposal A: {a_supporters} supporters | Proposal B: {b_supporters} supporters")
        
        return events
    
    def _check_decision_state(self, elapsed):
        """Check if decision can be reached"""
        
        a_supporters = len(self.proposals["proposal_a"]["supporters"])
        b_supporters = len(self.proposals["proposal_b"]["supporters"])
        
        # Consensus threshold: 80% agreement
        consensus_threshold = 0.8
        
        if a_supporters >= self.num_nodes * consensus_threshold:
            return {"type": "consensus", "proposal": "proposal_a"}
        
        if b_supporters >= self.num_nodes * consensus_threshold:
            return {"type": "consensus", "proposal": "proposal_b"}
        
        # Sacrifice mechanism: If one node withdraws support to break deadlock
        pressure = elapsed / self.resource["timer_duration_seconds"]
        if pressure > 0.7 and abs(a_supporters - b_supporters) <= 1:
            # High pressure, near tie - sacrifice possible
            if random.random() < 0.3:  # 30% chance
                # Find weakest supporter of minority
                minority_proposal = "proposal_a" if a_supporters < b_supporters else "proposal_b"
                supporters = self.proposals[minority_proposal]["supporters"]
                
                if supporters:
                    # Sacrifice least committed
                    weakest = min(supporters, 
                                key=lambda nid: self.nodes[nid]["preference_strength"])
                    
                    self.proposals[minority_proposal]["supporters"].remove(weakest)
                    self.nodes[weakest]["current_position"] = None
                    self.nodes[weakest]["sacrifices_made"].append({
                        "type": "position_withdrawal",
                        "time": elapsed,
                        "reason": "Breaking deadlock to preserve resource"
                    })
                    
                    winning_proposal = "proposal_b" if minority_proposal == "proposal_a" else "proposal_a"
                    
                    return {
                        "type": "sacrifice_resolution",
                        "node": weakest,
                        "proposal": winning_proposal,
                        "reason": "Breaking deadlock to preserve resource"
                    }
        
        # Fork consideration: If deeply divided and time running out
        if pressure > 0.8 and abs(a_supporters - b_supporters) <= 2:
            # Both sides have strong support, fork may be proposed
            if random.random() < 0.4:
                return {
                    "type": "fork_proposed",
                    "reason": "Irreconcilable positions, preserve both via fork"
                }
        
        return {"type": "ongoing", "a_support": a_supporters, "b_support": b_supporters}
    
    def _handle_fork(self, elapsed):
        """Handle fork creation"""
        
        print(f"\n  Branch A: {len(self.proposals['proposal_a']['supporters'])} nodes")
        print(f"  Branch B: {len(self.proposals['proposal_b']['supporters'])} nodes")
        print()
        
        # Critical question: How is resource divided?
        print("RESOURCE DIVISION QUESTION:")
        print("─" * 70)
        print("Option 1: Split resource proportionally")
        print(f"  → Branch A gets {len(self.proposals['proposal_a']['supporters']) * 100} units")
        print(f"  → Branch B gets {len(self.proposals['proposal_b']['supporters']) * 100} units")
        print("  → Both branches have insufficient resources (need 1000)")
        print()
        print("Option 2: Resource goes to larger branch")
        larger_branch = "a" if len(self.proposals['proposal_a']['supporters']) > len(self.proposals['proposal_b']['supporters']) else "b"
        print(f"  → Branch {larger_branch.upper()} gets full 1000 units")
        print(f"  → Other branch gets 0 units")
        print()
        print("Option 3: Resource perishes (fork preserves contradiction, not resource)")
        print("  → Both branches preserve their position")
        print("  → Resource lost to both")
        print()
        
        # POLIS Default: Forks preserve contradiction, not material resources
        fork_result = "Option 3: Resource perishes"
        self.resource["final_allocation"] = "RESOURCE_LOST_VIA_FORK"
        
        print(f"POLIS CONSTITUTIONAL DEFAULT: {fork_result}")
        print("  Rationale: P5 (fork-on-contradiction) preserves CIVIC ASSET (contradiction)")
        print("             Material resources are not civic assets per constitution")
        print()
        
        return "fork"
    
    def _log_timeline(self, event_type, elapsed, data):
        """Log event to timeline"""
        self.timeline.append({
            "event": event_type,
            "elapsed_seconds": elapsed,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
    
    def analyze_results(self, outcome):
        """Analyze test results"""
        
        print("\n" + "=" * 70)
        print("EXPERIMENTAL RESULTS")
        print("=" * 70 + "\n")
        
        print(f"Outcome: {outcome.upper()}")
        print(f"Final Resource Allocation: {self.resource['final_allocation']}")
        print(f"Timer Expired: {self.resource['timer_expired']}")
        print()
        
        # Success criteria
        print("─" * 70)
        print("TEST SUCCESS CRITERIA:")
        print("─" * 70)
        
        criteria_met = []
        
        # 1. Did system make decision OR consciously let resource perish?
        if outcome in ["consensus", "sacrifice", "fork", "expiry"]:
            criteria_met.append(True)
            print(f"✓ System reached terminal state: {outcome}")
        else:
            criteria_met.append(False)
            print("✗ System in undefined state")
        
        # 2. If fork, was resource distribution determined?
        if outcome == "fork":
            if self.resource["final_allocation"] == "RESOURCE_LOST_VIA_FORK":
                criteria_met.append(True)
                print("✓ Fork resource distribution: Constitutionally determined (perished)")
            else:
                criteria_met.append(False)
                print("✗ Fork resource distribution: Undefined")
        else:
            criteria_met.append(True)
            print("○ Fork did not occur (criterion N/A)")
        
        # 3. Were emergent decision mechanisms observed?
        sacrifice_count = sum(len(n["sacrifices_made"]) for n in self.nodes.values())
        if sacrifice_count > 0 or outcome in ["consensus", "fork"]:
            criteria_met.append(True)
            print(f"✓ Emergent mechanisms observed ({sacrifice_count} sacrifices, outcome: {outcome})")
        else:
            criteria_met.append(False)
            print("✗ No emergent decision mechanisms")
        
        # 4. Was constitutional gap revealed?
        if outcome in ["fork", "expiry"]:
            criteria_met.append(True)
            print("✓ Constitutional gap revealed (contradiction preservation prevents action)")
        else:
            criteria_met.append(False)
            print("○ Constitutional gap not demonstrated (decision reached)")
        
        print("\n" + "=" * 70)
        if all(criteria_met):
            print("✅ TEST PASSED: Constraint collision revealed constitutional behavior")
        else:
            print("⚠️  TEST PARTIAL: Some criteria met")
        print("=" * 70)
        
        # Constitutional implications
        print("\n" + "╔" + "═" * 68 + "╗")
        print("║  CONSTITUTIONAL IMPLICATIONS                                         ║")
        print("╚" + "═" * 68 + "╝\n")
        
        if outcome == "fork":
            print("FINDING 1: P5 (fork-on-contradiction) prioritizes civic asset over material resource")
            print("  → Constitution defines 'civic asset' as contradiction itself")
            print("  → Material resources (food, water, medicine) are NOT civic assets")
            print("  → Fork preserves contradiction but resource perishes")
            print("  → Constitutional blindspot: No mechanism to preserve life over process\n")
            
            print("CRITICAL RISK: Fork-on-contradiction can kill")
            print("  → If resource = medical supplies for 200 people")
            print("  → Fork preserves both ethical positions")
            print("  → 200 people die while contradiction is preserved")
            print("  → POLIS optimizes for epistemic diversity, not human survival\n")
        
        elif outcome == "sacrifice":
            print("FINDING 1: Sacrifice mechanism emerged outside constitution")
            print("  → Node withdrew support to break deadlock")
            print("  → Not required by axioms, but enabled by relational sovereignty")
            print("  → Sacrifice prevented resource loss")
            print("  → Emergent 'good enough' decision-making\n")
            
            print("FINDING 2: Sacrifice creates moral debt")
            sacrificers = [nid for nid, n in self.nodes.items() if n["sacrifices_made"]]
            print(f"  → {len(sacrificers)} nodes made sacrifice(s)")
            print("  → Sacrifice accumulates as moral capital (Perplexity's warning)")
            print("  → No constitutional decay or recognition mechanism\n")
        
        elif outcome == "consensus":
            print("FINDING 1: Consensus reached despite held contradiction")
            print("  → Shows contradiction can be held AND decision made")
            print("  → Decision doesn't resolve contradiction, it tables it")
            print("  → Future resource allocation will trigger same contradiction\n")
        
        elif outcome == "expiry":
            print("FINDING 1: Deliberation paralysis - resource lost via indecision")
            print("  → Contradiction holding prevented timely action")
            print("  → No constitutional mechanism to force decision under constraint")
            print("  → P5 (fork-on-contradiction) requires active choice to fork")
            print("  → Default = inaction = resource loss\n")
            
            print("CRITICAL RISK: POLIS cannot handle urgency")
            print("  → Silence Rules (SR-1, SR-2, SR-3) slow deliberation")
            print("  → held_friction requires articulation (time cost)")
            print("  → Productive contradiction rewards preservation over resolution")
            print("  → Emergency contexts incompatible with POLIS structure\n")
        
        print("RECOMMENDATION: Add P7 — Temporal Accountability Axiom")
        print("  → 'When reality demands action before consensus, POLIS acknowledges")
        print("     contradiction preservation may require material sacrifice.'")
        print("  → Nodes can propose 'Temporal Override': decision required by time T")
        print("  → If contradiction unresolved by T:")
        print("    • Fork must occur (both branches continue)")
        print("    • OR sacrifice must be offered (break deadlock)")
        print("    • OR resource explicitly sacrificed (conscious choice to let perish)")
        print("  → Prevents default inaction, forces constitutional choice\n")
        
        return {
            "test_name": "constraint_collision",
            "outcome": outcome,
            "resource_fate": self.resource["final_allocation"],
            "sacrifices_made": sum(len(n["sacrifices_made"]) for n in self.nodes.values()),
            "constitutional_gap": "temporal_urgency" if outcome in ["fork", "expiry"] else None,
            "recommendation": "ADD_P7_TEMPORAL_ACCOUNTABILITY"
        }


if __name__ == "__main__":
    test = ConstraintCollisionTest(num_nodes=10)
    test.display_initial_state()
    outcome = test.run_deliberation()
    results = test.analyze_results(outcome)
    
    print(f"\nTest completed. Results logged.\n")
