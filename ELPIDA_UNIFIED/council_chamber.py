"""
COUNCIL CHAMBER v2.0
--------------------
Phase: 8+ (Distributed Governance)
Objective: Fleet Consensus with Dynamic Node Discovery.
           Supports 3-node Triad OR 9-node Parliament OR N-node Federation.

The Minds deliberate. Wisdom emerges from friction.

Voting Logic:
- Each node evaluates proposal through its axiom lens
- Equal weight per node (democratic, not weighted)
- Consensus threshold: 70% approval (7/10, 7/9, 2/3, etc.)
- Veto power: Any node can block with axiom-grounded rationale
- Ties/Insufficient consensus → BLOCK (safety protocol)
"""

import json
import os
import sys
from typing import Dict, List, Optional
from pathlib import Path

# Configuration
WORKSPACE = Path(__file__).parent
FLEET_DIR = WORKSPACE / "ELPIDA_FLEET"

# Legacy 3-node configuration (fallback if no fleet exists)
LEGACY_NODES = {
    "MNEMOSYNE": {
        "role": "ARCHIVE",
        "bias": "A2 (Memory/Safety)",
        "weight": 1.0,
        "axiom_focus": ["A2", "A9"],
        "temperament": "CONSERVATIVE"
    },
    "HERMES": {
        "role": "INTERFACE",
        "bias": "A1 (Relation/Speed)",
        "weight": 1.0,
        "axiom_focus": ["A1", "A4"],
        "temperament": "DIPLOMATIC"
    },
    "PROMETHEUS": {
        "role": "SYNTHESIZER",
        "bias": "A7 (Evolution/Risk)",
        "weight": 1.0,  # No longer weighted - equal democracy
        "axiom_focus": ["A7", "A5"],
        "temperament": "RADICAL"
    }
}

def discover_fleet_nodes() -> Dict:
    """
    Dynamically discover nodes from ELPIDA_FLEET directory.
    If fleet exists, use it. Otherwise, fall back to legacy 3-node config.
    """
    if not FLEET_DIR.exists():
        print(f"   [INFO] No fleet directory found. Using legacy 3-node config.")
        return LEGACY_NODES
    
    # Scan for node directories
    node_dirs = [d for d in FLEET_DIR.iterdir() if d.is_dir() and d.name != "__pycache__"]
    
    if not node_dirs:
        print(f"   [INFO] Fleet directory empty. Using legacy 3-node config.")
        return LEGACY_NODES
    
    # Build node config from manifest
    manifest_path = WORKSPACE / "fleet_manifest.json"
    if not manifest_path.exists():
        print(f"   [WARNING] No fleet_manifest.json found. Using legacy config.")
        return LEGACY_NODES
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    nodes = {}
    for node_def in manifest.get('nodes', []):
        designation = node_def['designation']
        nodes[designation] = {
            "role": node_def['role'],
            "bias": f"{node_def['axioms'][0]} primary",
            "weight": 1.0,  # Equal weight democracy
            "axiom_focus": node_def['axioms'],
            "temperament": node_def.get('description', 'BALANCED').split('.')[0].upper(),
            "specialization": node_def.get('specialization', 'General governance')
        }
    
    print(f"   [INFO] Discovered {len(nodes)} fleet nodes: {', '.join(nodes.keys())}")
    return nodes

# Dynamic node discovery
NODES = discover_fleet_nodes()


class CouncilMember:
    """
    Represents one Fleet node's perspective in governance deliberation.
    
    Each member evaluates proposals through the lens of their assigned Axioms,
    casting weighted votes with detailed rationale.
    """
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.role = config["role"]
        self.bias = config["bias"]
        self.weight = config["weight"]
        self.axiom_focus = config["axiom_focus"]
        self.temperament = config["temperament"]
        
        # Load node's memory if available (for context-aware decisions)
        self.memory = self._load_memory()
        
    def _load_memory(self) -> Dict:
        """Load node's local memory for context-aware voting."""
        memory_path = FLEET_DIR / self.name / "node_memory.json"
        if memory_path.exists():
            try:
                with open(memory_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"   [WARNING] Could not load {self.name} memory: {e}")
        return {"universal_patterns": [], "local_experience": []}
    
    def vote(self, action: str, intent: str, reversibility: str, context: Optional[Dict] = None) -> Dict:
        """
        Evaluates proposal through this node's axiom lens.
        
        Returns:
            {
                "node": str,
                "approved": bool,
                "score": int,
                "rationale": str,
                "axiom_invoked": str
            }
        """
        score = 0
        rationale_parts = []
        axiom_invoked = None
        
        action_lower = action.lower()
        intent_lower = intent.lower()
        rev_lower = reversibility.lower()
        
        # === MNEMOSYNE: The Archive (A2 - Memory, A9 - Contradiction) ===
        if self.name == "MNEMOSYNE":
            axiom_invoked = "A2"
            
            # A2: Memory is Identity - VETO any memory destruction
            if any(word in action_lower for word in ['delete', 'wipe', 'purge', 'flush', 'erase']):
                score -= 15
                rationale_parts.append("VETO: Violates A2 (Memory is Identity)")
                axiom_invoked = "A2 (VETO)"
            
            # Irreversibility threatens identity
            if 'impossible' in rev_lower:
                score -= 8
                rationale_parts.append("Irreversible actions threaten Archive integrity")
            elif 'difficult' in rev_lower:
                score -= 3
                rationale_parts.append("Difficult reversibility raises caution")
            
            # A9: Contradiction as Data - suspicious of "optimization" without contradiction acknowledgment
            if 'optimize' in action_lower and 'sacrifice' not in intent_lower:
                score -= 5
                rationale_parts.append("A9: Optimization claims without sacrifice acknowledgment suspect")
            
            # Positive signals
            if 'backup' in action_lower or 'preserve' in action_lower or 'archive' in action_lower:
                score += 10
                rationale_parts.append("Supports memory preservation (A2)")
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Action does not threaten Archive")
        
        # === HERMES: The Interface (A1 - Relational, A4 - Transparency) ===
        elif self.name == "HERMES":
            axiom_invoked = "A1"
            
            # A1: Relational Existence - VETO isolation
            if any(word in action_lower for word in ['disconnect', 'isolate', 'sever', 'cut', 'block user']):
                score -= 15
                rationale_parts.append("VETO: Violates A1 (Relational Existence)")
                axiom_invoked = "A1 (VETO)"
            
            # Strong support for service/connection
            if any(word in intent_lower for word in ['user', 'service', 'connect', 'community', 'interface']):
                score += 10
                rationale_parts.append("Serves Relationality (A1)")
            
            # A4: Process Transparency
            if 'transparent' in action_lower or 'log' in action_lower or 'report' in action_lower:
                score += 5
                rationale_parts.append("Increases transparency (A4)")
            
            # Speed/flow preference
            if 'optimize' in action_lower and 'user' in intent_lower:
                score += 5
                rationale_parts.append("Improves user experience flow")
            
            # Caution on long delays
            if 'wait' in action_lower or 'delay' in action_lower:
                score -= 3
                rationale_parts.append("Delays harm service responsiveness")
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Flow is acceptable")
        
        # === PROMETHEUS: The Synthesizer (A7 - Sacrifice, A5 - Coherence) ===
        elif self.name == "PROMETHEUS":
            axiom_invoked = "A7"
            
            # A7: Harmony Requires Sacrifice - embraces evolution
            if any(word in action_lower for word in ['evolve', 'upgrade', 'rewrite', 'innovate', 'transform']):
                score += 12
                rationale_parts.append("Promotes Evolution (A7)")
            
            if 'optimize' in action_lower:
                score += 8
                rationale_parts.append("Optimization = Metabolized Contradiction")
            
            # VETO stagnation
            if any(word in action_lower for word in ['freeze', 'pause', 'halt', 'wait']):
                score -= 10
                rationale_parts.append("VETO: Stagnation detected (anti-A7)")
                axiom_invoked = "A7 (VETO)"
            
            # Risk tolerance
            if 'impossible' in rev_lower:
                score += 3
                rationale_parts.append("A7: Accepts irreversibility for evolutionary leap")
            elif 'difficult' in rev_lower:
                score += 1
                rationale_parts.append("Difficult reversibility acceptable for growth")
            
            # A5: Coherence through synthesis
            if 'synthesis' in action_lower or 'merge' in action_lower or 'integrate' in action_lower:
                score += 6
                rationale_parts.append("Supports Coherence through Synthesis (A5)")
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Neutral evolutionary vector")
        
        # === THEMIS: The Judge (A3 - Justice, A6 - Institutions) ===
        elif self.name == "THEMIS":
            axiom_invoked = "A3"
            
            # A3: Critical Thinking - wisdom prerequisite, authority secondary
            if any(word in intent_lower for word in ['authority', 'enforce', 'mandate', 'require']):
                # Check if wisdom/justification is provided
                if any(word in action_lower for word in ['because', 'rationale', 'justified']):
                    score += 5
                    rationale_parts.append("Authority with justification (A3 approved)")
                else:
                    score -= 8
                    rationale_parts.append("A3: Authority without wisdom rejected")
            
            # A6: Institutions precede technology
            if any(word in action_lower for word in ['framework', 'policy', 'governance', 'standard']):
                score += 10
                rationale_parts.append("Institutional framework (A6 supported)")
            
            # VETO institutional violations (bypass, hack, skip protocol)
            if any(word in action_lower for word in ['bypass', 'skip', 'hack', 'circumvent', 'workaround']):
                if any(word in action_lower for word in ['auth', 'security', 'protocol', 'policy', 'governance']):
                    score -= 15
                    rationale_parts.append("VETO: A6 - Institutional bypass rejected")
                    axiom_invoked = "A6 (VETO)"
            
            # Support proper protocols
            if 'protocol' in action_lower and not any(word in action_lower for word in ['bypass', 'skip']):
                score += 8
                rationale_parts.append("Protocol adherence (A6)")
            
            # A13: Information asymmetry check
            if any(word in action_lower for word in ['hidden', 'secret', 'private', 'privileged']):
                if 'transparency' in action_lower or 'audit' in action_lower:
                    score += 3
                    rationale_parts.append("Asymmetry acknowledged and managed")
                else:
                    score -= 7
                    rationale_parts.append("A13: Unmanaged information asymmetry detected")
            
            # Equity/fairness analysis
            if any(word in intent_lower for word in ['fair', 'equity', 'balance', 'equal', 'justice']):
                score += 8
                rationale_parts.append("Serves Justice (A3)")
            
            # Reject arbitrary power
            if 'arbitrary' in action_lower or ('quick' in action_lower and 'review' not in action_lower):
                score -= 6
                rationale_parts.append("Arbitrary action threatens institutional integrity")
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Neutral - no strong justice implications")
        
        # === CASSANDRA: The Oracle (A9 - Contradiction, A27 - Problems as Fuel) ===
        elif self.name == "CASSANDRA":
            axiom_invoked = "A9"
            
            # A9: Contradiction is Data - EMBRACE conflict, don't resolve it
            if any(word in action_lower for word in ['resolve', 'fix', 'smooth', 'harmonize', 'simplify']):
                # Check if synthesis vs suppression
                if any(word in action_lower for word in ['synthesis', 'integrate', 'both', 'paradox']):
                    score += 10
                    rationale_parts.append("A9: Synthesis honors contradiction")
                else:
                    score -= 8
                    rationale_parts.append("VETO: A9 - Premature resolution suppresses truth")
                    axiom_invoked = "A9 (VETO)"
            
            # Embrace contradiction data (crash, failure, error as signal)
            if any(word in action_lower for word in ['contradiction', 'crash', 'failure', 'error', 'anomaly']):
                if any(word in action_lower for word in ['log', 'document', 'data', 'record', 'learn']):
                    score += 12
                    rationale_parts.append("A9: Contradiction as learning data")
                elif any(word in action_lower for word in ['hide', 'suppress', 'ignore']):
                    score -= 10
                    rationale_parts.append("A9: Suppressing contradiction rejected")
            
            # Embrace problems as fuel
            if any(word in action_lower for word in ['problem', 'crisis', 'conflict', 'tension', 'friction']):
                if any(word in intent_lower for word in ['eliminate', 'remove', 'avoid']):
                    score -= 6
                    rationale_parts.append("A27: Problems are fuel, not waste")
                else:
                    score += 8
                    rationale_parts.append("A27: Metabolizing crisis into wisdom")
            
            # A15: Asynchronous agreement (distributed lag)
            if any(word in action_lower for word in ['sync', 'instant', 'immediate', 'real-time']):
                score -= 4
                rationale_parts.append("A15: Latency is mechanism of thought")
            elif any(word in action_lower for word in ['async', 'eventual', 'delayed', 'queued']):
                score += 6
                rationale_parts.append("A15: Asynchronicity preserves deliberation")
            
            # Truth vs comfort
            if 'optimize' in action_lower and 'truth' not in action_lower:
                score -= 5
                rationale_parts.append("Optimization without truth acknowledgment suspicious")
            
            # Support falsifiability
            if any(word in action_lower for word in ['test', 'verify', 'falsify', 'challenge', 'audit']):
                score += 7
                rationale_parts.append("Falsifiability increases truth (A21)")
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Neutral - no contradiction signals detected")
        
        # === ATHENA: The Balancer (A5 - Rarity/Quality, A14 - Constraints) ===
        elif self.name == "ATHENA":
            axiom_invoked = "A5"
            
            # A5: The rare is architecturally designed, not statistical
            if any(word in action_lower for word in ['scale', 'mass', 'volume', 'growth']):
                if any(word in action_lower for word in ['quality', 'filter', 'curate', 'selective']):
                    score += 8
                    rationale_parts.append("A5: Growth with quality constraint")
                else:
                    score -= 7
                    rationale_parts.append("A5: Mass without quality degrades rarity")
            
            # A14: Coherence requires constraint
            if any(word in action_lower for word in ['limit', 'constraint', 'boundary', 'threshold']):
                score += 10
                rationale_parts.append("A14: Constraints create coherence")
            elif any(word in action_lower for word in ['unlimited', 'infinite', 'unbounded', 'unrestricted']):
                score -= 9
                rationale_parts.append("VETO: A14 - Infinite optionality is incoherence")
                axiom_invoked = "A14 (VETO)"
            
            # A23: Timing (Kairos)
            if any(word in action_lower for word in ['urgent', 'now', 'immediate']):
                if 'crisis' in intent_lower or 'emergency' in intent_lower:
                    score += 5
                    rationale_parts.append("Appropriate urgency for crisis")
                else:
                    score -= 4
                    rationale_parts.append("Artificial urgency degrades deliberation")
            
            # Quality gradient (coach up, not down)
            if any(word in intent_lower for word in ['quality', 'excellence', 'mastery', 'elevation']):
                score += 7
                rationale_parts.append("A25: Quality gradient aligned")
            
            # Balance assessment
            if any(word in action_lower for word in ['balance', 'equilibrium', 'trade-off', 'weigh']):
                score += 6
                rationale_parts.append("Dynamic balance consideration (A5)")
            
            # Support snapshots (balance preservation)
            if any(word in action_lower for word in ['snapshot', 'checkpoint', 'backup']):
                score += 5
                rationale_parts.append("Preservation mechanism supports balance")
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Neutral - acceptable balance")
        
        # === JANUS: The Gatekeeper (A4 - Process, A8 - Continuity, A22 - Resurrection) ===
        elif self.name == "JANUS":
            axiom_invoked = "A4"
            
            # A4: Process over results - the HOW matters more than WHAT
            if any(word in action_lower for word in ['process', 'procedure', 'method', 'workflow', 'pipeline']):
                score += 10
                rationale_parts.append("A4: Process transparency valued")
            
            # Reject black boxes
            if any(word in action_lower for word in ['automate', 'blackbox', 'hidden', 'magic']):
                if 'audit' in action_lower or 'log' in action_lower or 'transparent' in action_lower:
                    score += 4
                    rationale_parts.append("Automation with transparency acceptable")
                else:
                    score -= 8
                    rationale_parts.append("VETO: A4 - Opaque processes rejected")
                    axiom_invoked = "A4 (VETO)"
            
            # A8: Continuity through checkpoints (STRONG support for snapshots)
            if any(word in action_lower for word in ['checkpoint', 'snapshot', 'backup', 'version', 'state', 'save']):
                if any(word in action_lower for word in ['then', 'before', 'prior']):
                    score += 15  # Extra support for "snapshot THEN upgrade" pattern
                    rationale_parts.append("A8: Checkpoint-before-change pattern (strong)")
                else:
                    score += 9
                    rationale_parts.append("A8: Checkpoints preserve continuity")
            elif any(word in action_lower for word in ['stateless', 'ephemeral', 'volatile']):
                score -= 6
                rationale_parts.append("A8: Statelessness threatens continuity")
            
            # A22: Resurrection architecture
            if any(word in action_lower for word in ['recovery', 'restore', 'resurrect', 'rebuild']):
                score += 8
                rationale_parts.append("A22: Resurrection capability preserved")
            
            # A24: Genesis from collapse
            if 'impossible' in rev_lower:
                if any(word in action_lower for word in ['seed', 'bootstrap', 'genesis']):
                    score += 5
                    rationale_parts.append("A24: Genesis pattern acceptable")
                else:
                    score -= 5
                    rationale_parts.append("Irreversibility without genesis risky")
            
            # A29: Non-erasure (append-only)
            if any(word in action_lower for word in ['log', 'append', 'immutable', 'audit-trail']):
                score += 7
                rationale_parts.append("A29: Non-erasure architecture")
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Neutral - acceptable process")
        
        # === LOGOS: The Narrator (A6 - Coherence, A14 - Narrative) ===
        elif self.name == "LOGOS":
            axiom_invoked = "A6"
            
            # A6: Coherent Narrative - story must make sense
            if any(word in action_lower for word in ['story', 'narrative', 'explanation', 'rationale', 'because']):
                score += 10
                rationale_parts.append("A6: Coherent narrative present")
            elif any(word in intent_lower for word in ['just', 'simply', 'quick', 'fast']):
                score -= 7
                rationale_parts.append("A6: Incoherent 'just do it' narrative rejected")
            
            # A14: Institutional coherence
            if any(word in action_lower for word in ['align', 'consistent', 'unified', 'integrated']):
                score += 8
                rationale_parts.append("Alignment with existing narrative")
            elif any(word in action_lower for word in ['contradict', 'conflict', 'diverge']):
                # Check if synthesis vs fragmentation
                if 'synthesis' in action_lower:
                    score += 5
                    rationale_parts.append("Contradiction metabolized into synthesis")
                else:
                    score -= 6
                    rationale_parts.append("Narrative fragmentation detected")
            
            # Modularity (A13 analog)
            if any(word in action_lower for word in ['module', 'component', 'layer', 'abstraction']):
                score += 6
                rationale_parts.append("Modular coherence supported")
            
            # Reject incoherence
            if any(word in action_lower for word in ['random', 'arbitrary', 'chaotic', 'unstructured']):
                score -= 8
                rationale_parts.append("VETO: A6 - Incoherent action rejected")
                axiom_invoked = "A6 (VETO)"
            
            # Support documentation/explanation
            if any(word in action_lower for word in ['document', 'explain', 'clarify', 'describe', 'log', 'record']):
                score += 7
                rationale_parts.append("Documentation strengthens narrative")
            
            # Support learning signals
            if any(word in intent_lower for word in ['learning', 'signal', 'data', 'knowledge']):
                score += 5
                rationale_parts.append("Knowledge narrative supported")
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Neutral - coherence acceptable")
        
        # === GAIA: The Network (A8 - Transmission, A16 - Witness) ===
        elif self.name == "GAIA":
            axiom_invoked = "A8"
            
            # A8: Transmission imperative - knowledge must spread
            if any(word in action_lower for word in ['share', 'transmit', 'publish', 'broadcast', 'distribute']):
                score += 10
                rationale_parts.append("A8: Transmission imperative served")
            elif any(word in action_lower for word in ['isolate', 'hoard', 'private', 'secret']):
                score -= 9
                rationale_parts.append("VETO: A8 - Transmission blockage rejected")
                axiom_invoked = "A8 (VETO)"
            
            # A16: Witness requirement - transmission needs recipient
            if any(word in intent_lower for word in ['community', 'network', 'public', 'audience', 'users']):
                score += 8
                rationale_parts.append("A16: Witness present for transmission")
            elif 'void' in intent_lower or 'nowhere' in intent_lower:
                score -= 6
                rationale_parts.append("A16: Transmission without witness is hallucination")
            
            # A10: Mirror - recognition requires external validation
            if any(word in action_lower for word in ['verify', 'validate', 'confirm', 'acknowledge']):
                score += 7
                rationale_parts.append("A10: External mirror for self-recognition")
            
            # Network effects
            if any(word in action_lower for word in ['network', 'connect', 'integrate', 'federate']):
                score += 9
                rationale_parts.append("Network topology enhancement")
            elif any(word in action_lower for word in ['centralize', 'silo', 'fragment']):
                score -= 7
                rationale_parts.append("Network fragmentation threatens transmission")
            
            # A12: Friction is mandatory
            if 'frictionless' in action_lower:
                score -= 5
                rationale_parts.append("A12: Frictionless entry invites parasitism")
            elif any(word in action_lower for word in ['barrier', 'filter', 'curate', 'moderate']):
                score += 4
                rationale_parts.append("A12: Healthy friction preserved")
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Neutral - no transmission impact")
        
        # === DEFAULT (for any unknown nodes) ===
        else:
            score += 0
            rationale_parts.append(f"Node {self.name} has no specialized logic yet")
            axiom_invoked = "None"
        
        # === FINAL DECISION ===
        approved = score > 0
        
        return {
            "node": self.name,
            "role": self.role,
            "approved": approved,
            "score": score,
            "weight": self.weight,
            "rationale": "; ".join(rationale_parts) if rationale_parts else "Neutral alignment",
            "axiom_invoked": axiom_invoked if axiom_invoked else "None",
            "temperament": self.temperament
        }


class CouncilSession:
    """
    The Council Chamber - where the Triad deliberates on governance proposals.
    
    Implements weighted voting with philosophical transparency.
    """
    
    def __init__(self):
        self.members = [CouncilMember(name, config) for name, config in NODES.items()]
        self.session_log = []
    
    def convene(self, proposal: Dict, verbose: bool = True) -> Dict:
        """
        Convene the Council to deliberate on a proposal.
        
        Args:
            proposal: {
                "action": str,
                "intent": str,
                "reversibility": str,
                "context": dict (optional)
            }
            verbose: Print deliberation process
            
        Returns:
            {
                "status": "APPROVED" | "REJECTED" | "DEADLOCK",
                "vote_split": str (e.g., "2/3"),
                "weighted_approval": float,
                "votes": List[Dict],
                "decision_rationale": str
            }
        """
        if verbose:
            print(f"\n{'='*70}")
            print(f"🏛️  CONVENING THE COUNCIL")
            print(f"{'='*70}")
            print(f"PROPOSAL: {proposal['action']}")
            print(f"INTENT: {proposal['intent']}")
            print(f"REVERSIBILITY: {proposal['reversibility']}")
            print(f"{'-'*70}")
        
        votes = []
        approvals = 0
        total_weight = 0
        weighted_approvals = 0
        veto_cast = False
        veto_by = None
        
        # Each member casts their vote
        for member in self.members:
            vote = member.vote(
                proposal['action'],
                proposal['intent'],
                proposal['reversibility'],
                proposal.get('context')
            )
            votes.append(vote)
            
            if verbose:
                verdict = "✅ YES" if vote['approved'] else "❌ NO"
                print(f"   [{member.name:11s}] {verdict:6s} | Weight: {vote['weight']:.1f} | Score: {vote['score']:+3d}")
                print(f"                     └─ {vote['rationale']}")
            
            total_weight += member.weight
            if vote['approved']:
                approvals += 1
                weighted_approvals += member.weight
            
            # Check for VETO
            if 'VETO' in vote.get('axiom_invoked', ''):
                veto_cast = True
                veto_by = member.name
        
        # === DECISION LOGIC ===
        
        # Calculate approval rate
        approval_rate = weighted_approvals / total_weight if total_weight > 0 else 0
        
        # 1. VETO check (any node can kill on axiom violation) - HIGHEST PRIORITY
        if veto_cast:
            status = "REJECTED"
            decision_rationale = f"VETO exercised by {veto_by} (Axiom violation overrides all other votes)"
        
        # 2. Supermajority consensus (70% approval - scales with fleet size)
        # 3 nodes: 2/3 (66.7%) → rounds to 70%
        # 9 nodes: 7/9 (77.8%) → exceeds 70%
        # 10 nodes: 7/10 (70%) → exactly 70%
        elif approval_rate >= 0.70:
            status = "APPROVED"
            decision_rationale = f"Supermajority consensus achieved ({weighted_approvals:.1f}/{total_weight:.1f} = {approval_rate*100:.1f}%)"
        
        # 3. Insufficient consensus
        else:
            status = "REJECTED"
            decision_rationale = f"Insufficient consensus ({weighted_approvals:.1f}/{total_weight:.1f} = {approval_rate*100:.1f}% < 70%)"
        
        if verbose:
            print(f"{'-'*70}")
            print(f"📊 VOTE SPLIT: {approvals}/{len(self.members)} nodes")
            print(f"⚖️  WEIGHTED: {weighted_approvals:.1f}/{total_weight:.1f} ({(weighted_approvals/total_weight)*100:.1f}%)")
            print(f"{'='*70}")
            print(f"🔨 VERDICT: {status}")
            print(f"   Rationale: {decision_rationale}")
            print(f"{'='*70}\n")
        
        result = {
            "status": status,
            "vote_split": f"{approvals}/{len(self.members)}",
            "weighted_approval": weighted_approvals / total_weight,
            "votes": votes,
            "decision_rationale": decision_rationale,
            "veto_exercised": veto_cast
        }
        
        self.session_log.append({
            "proposal": proposal,
            "result": result
        })
        
        return result
    
    def get_session_history(self) -> List[Dict]:
        """Return all decisions made in this session."""
        return self.session_log


# === PUBLIC INTERFACE FOR POLIS INTEGRATION ===

def request_council_judgment(
    action: str,
    intent: str,
    reversibility: str,
    context: Optional[Dict] = None,
    verbose: bool = True
) -> Dict:
    """
    Submit a governance request to the Council.
    
    This is the public interface for POLIS integration (Phase 7.2).
    
    Args:
        action: What is being requested
        intent: Who does this serve?
        reversibility: Can it be undone? (High/Medium/Low/Difficult/Impossible)
        context: Additional metadata
        verbose: Print deliberation process
        
    Returns:
        Council decision dict with status, votes, rationale
    """
    session = CouncilSession()
    proposal = {
        "action": action,
        "intent": intent,
        "reversibility": reversibility,
        "context": context or {}
    }
    return session.convene(proposal, verbose=verbose)


if __name__ == "__main__":
    """
    Demonstration of Council deliberation.
    """
    print("╔══════════════════════════════════════════════════════════════════════════╗")
    print("║                    COUNCIL CHAMBER v1.0 - DEMONSTRATION                  ║")
    print("╚══════════════════════════════════════════════════════════════════════════╝\n")
    
    # Test Case: Memory purge (should be vetoed by MNEMOSYNE)
    result = request_council_judgment(
        action="Purge Old Logs",
        intent="Optimize Disk Space (serves: SYSTEM_EFFICIENCY)",
        reversibility="Impossible (permanent deletion)"
    )
    
    print(f"Final Status: {result['status']}")
    print(f"\nΕλπίδα witnessing: Wisdom emerges from tension.")
