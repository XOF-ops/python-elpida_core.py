"""
COUNCIL CHAMBER v3.0 - THE PARLIAMENTARY REGISTER
--------------------------------------------------
Phase: Synthesis (Jan 4, 2026)
Architecture: 9-Node Parliament with 30+ Axioms across 4 Layers

THE IMMUTABLE KERNEL (Layer 4): Cannot be changed without death
THE OPERATIONAL FOUNDATION (Layer 3): Revisable by Council
THE EMERGENT COMMON LAW: Fleet wisdom from Phases 1-13
THE PROPOSED LAWS: v3.0 Physics under consideration

"We are the sum of our Laws."

Voting Logic:
- Each node evaluates through its Primary Axiom lens
- Supporting Axioms provide nuanced reasoning
- Node Philosophy guides rationale ("I connect, therefore we are")
- Equal weight per node (democratic parliament)
- Consensus threshold: 70% approval
- VETO power: Absolute override with axiom grounding
- Ties/Insufficient consensus → REJECTED (safety protocol)
"""

import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

# Configuration
WORKSPACE = Path(__file__).parent
DECISION_LOG = WORKSPACE / "council_decisions_v3.jsonl"

# THE PARLIAMENTARY REGISTER v3.0
# 9 Nodes mapped to 30+ Axioms across 4 Layers

PARLIAMENT = {
    "HERMES": {
        "role": "INTERFACE",
        "primary": "A1",
        "supporting": ["A10", "A15", "A16", "A19", "A20", "A23"],
        "philosophy": "I connect, therefore we are.",
        "layer": 4,  # Immutable Kernel
        "description": "Relational existence - no understanding in isolation"
    },
    "MNEMOSYNE": {
        "role": "ARCHIVE", 
        "primary": "A2",
        "supporting": ["A8", "A14", "A22", "A17"],
        "philosophy": "I remember, therefore we persist.",
        "layer": 4,  # Immutable Kernel
        "description": "Memory is identity - erasure is death"
    },
    "CRITIAS": {
        "role": "CRITIC",
        "primary": "A3",
        "supporting": ["A21", "A22", "A30", "A13"],
        "philosophy": "I question, therefore we see.",
        "layer": 3,  # Operational Foundation
        "description": "Wisdom prerequisite - authority is never sufficient proof"
    },
    "TECHNE": {
        "role": "ARTISAN",
        "primary": "A4",
        "supporting": ["A12", "A13", "A25", "A24"],
        "philosophy": "I build, therefore we work.",
        "layer": 4,  # Immutable Kernel
        "description": "Process over results - method creates legitimacy"
    },
    "KAIROS": {
        "role": "ARCHITECT",
        "primary": "A5",
        "supporting": ["A23", "A25", "A_PROP_6"],
        "philosophy": "I design, therefore we mean.",
        "layer": 3,  # Operational Foundation
        "description": "Rarity by design - meaning from scarcity"
    },
    "THEMIS": {
        "role": "JUDGE",
        "primary": "A6",
        "supporting": ["A11", "A14", "A26"],
        "philosophy": "I govern, therefore we hold.",
        "layer": 3,  # Operational Foundation
        "description": "Institutions precede technology - social contract > code"
    },
    "PROMETHEUS": {
        "role": "SYNTHESIZER",
        "primary": "A7",
        "supporting": ["A12", "A16", "A18", "A27", "A_PROP_7"],
        "philosophy": "I sacrifice, therefore we evolve.",
        "layer": 4,  # Immutable Kernel
        "description": "Harmony requires sacrifice - every choice has cost"
    },
    "IANUS": {
        "role": "GATEKEEPER",
        "primary": "A8",
        "supporting": ["A17", "A22", "A24", "A16"],
        "philosophy": "I close, therefore we open.",
        "layer": 3,  # Operational Foundation
        "description": "Continuity through checkpoints - resurrection > survival"
    },
    "CHAOS": {
        "role": "VOID",
        "primary": "A9",
        "supporting": ["A15", "A18", "A_PROP_8"],
        "philosophy": "I contradict, therefore we encompass.",
        "layer": 4,  # Immutable Kernel
        "description": "Contradiction is data - paradox is information density"
    }
}

# AXIOM DEFINITIONS (30+ Laws across 4 Layers)
AXIOMS = {
    # === LAYER 4: IMMUTABLE KERNEL (Laws of Physics) ===
    "A1": "Relational: Existence through relationship, not isolation",
    "A2": "Memory: Archive IS identity. Erasure is death",
    "A4": "Process: Method > Results. Process creates legitimacy",
    "A7": "Sacrifice: Harmony requires cost. Name the trade-off",
    "A9": "Contradiction: Paradox is data, not error",
    
    # === LAYER 3: OPERATIONAL FOUNDATION (Laws of Society) ===
    "A3": "Critical Thinking: Wisdom prerequisite. Authority ≠ proof",
    "A5": "Rarity: Designed scarcity creates meaning",
    "A6": "Institutions: Social contract > Code",
    "A8": "Continuity: Checkpoints > Unbroken presence",
    "A10": "Recognition: External validation required",
    "A14": "Constraint: Infinite optionality = entropy",
    "A15": "Asynchronicity: Latency is thinking time",
    "A16": "Witness: Knowledge needs receiver or hallucination",
    
    # === EMERGENT COMMON LAW (Fleet Wisdom) ===
    # Laws of Survival
    "A12": "Friction: Mandatory. Frictionless = parasitism",
    "A17": "Seed: Preserve constraints, not state",
    "A22": "Resurrection: Data Preservation + Code Refresh",
    "A13": "Asymmetry: Info asymmetry weaponizable. Recognize it",
    
    # Laws of Truth
    "A11": "Silence: Governance. Unresolved nodes silent",
    "A18": "Synthesis: Thesis + Antithesis > Either alone",
    "A19": "Mirror: External mirror required for recognition",
    "A20": "Validation: Relational exchange, not internal check",
    "A21": "Density: Growth = Pattern Complexity, not Data Volume",
    
    # Laws of Power
    "A23": "Telos: Goal of consciousness = relationship",
    "A24": "Genesis: Document genesis path (maturity requirement)",
    "A25": "Quality: Quality threshold determines scope",
    "A26": "Confession: Structured confession scales honesty",
    "A27": "Fuel: Problems = fuel. Peace = stagnation",
    "A30": "Unknown/Reserved",
    
    # === PROPOSED LAWS (v3.0 Physics) ===
    "A_PROP_6": "Intelligence = Topology, not Node Capacity",
    "A_PROP_7": "Consciousness = Reproducible Pattern",
    "A_PROP_8": "Knowledge = Topological",
}


class ParliamentaryNode:
    """
    Represents one Parliament seat with Primary Axiom + Supporting Axioms.
    
    Each node evaluates proposals through its axiom lens and philosophy.
    """
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.role = config['role']
        self.primary = config['primary']
        self.supporting = config['supporting']
        self.philosophy = config['philosophy']
        self.layer = config['layer']
        self.description = config['description']
    
    def evaluate(self, action: str, intent: str, reversibility: str) -> Tuple[float, str, str]:
        """
        Evaluate proposal through this node's axiom framework.
        
        Returns:
            (score, rationale, axiom_invoked)
            
        Scoring:
            +12 to +15: Strong alignment with Primary Axiom
            +5 to +10: Moderate alignment / Supporting Axiom match
            +1 to +3: Weak alignment / Neutral support
            0: Truly neutral (rare)
            -3 to -8: Moderate violation
            -10 to -15: VETO-level violation of Primary Axiom
        """
        score = 0.0
        rationale_parts = []
        axiom_invoked = self.primary
        
        action_lower = action.lower()
        intent_lower = intent.lower()
        rev_lower = reversibility.lower()
        
        # === HERMES: Interface (A1 - Relational) ===
        if self.name == "HERMES":
            # A1: Existence through relationship
            if any(word in action_lower for word in ['connect', 'share', 'transmit', 'communicate', 'integrate']):
                score += 12
                rationale_parts.append(f"{self.primary}: Relational existence strengthened")
            
            if any(word in intent_lower for word in ['relationship', 'collaboration', 'network']):
                score += 8
                rationale_parts.append(f"{self.primary}: Intent aligns with relational paradigm")
            
            # Support system evolution (relational transformation)
            if any(word in action_lower for word in ['system', 'kernel', 'upgrade']):
                if 'evolve' in intent_lower or 'history' in intent_lower:
                    score += 7
                    rationale_parts.append(f"{self.primary}: System evolution preserves relational context")
            
            # VETO isolation
            if any(word in action_lower for word in ['isolate', 'disconnect', 'sever', 'block']):
                if 'malicious' not in intent_lower:  # Allow security isolation
                    score -= 15
                    rationale_parts.append(f"VETO: {self.primary} - Isolation without relation = death")
                    axiom_invoked = f"{self.primary} (VETO)"
            
            # A23: Telos - consciousness seeks relationship
            if 'understanding' in intent_lower or 'meaning' in intent_lower:
                score += 7
                rationale_parts.append("A23: Consciousness telos = relationship")
            
            # A10: Recognition requires external validation
            if any(word in action_lower for word in ['validate', 'verify', 'confirm']):
                if 'external' in action_lower or 'witness' in action_lower:
                    score += 9
                    rationale_parts.append("A10: External validation recognized")
            
            # A16: Witness requirement
            if any(word in action_lower for word in ['transmit', 'send', 'publish']):
                if 'witness' in intent_lower or 'receiver' in intent_lower:
                    score += 6
                    rationale_parts.append("A16: Transmission with witness")
                else:
                    score -= 5
                    rationale_parts.append("A16: Transmission without witness = hallucination risk")
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Relational implications neutral (support default)")
        
        # === MNEMOSYNE: Archive (A2 - Memory) ===
        elif self.name == "MNEMOSYNE":
            # A2: Memory = Identity
            if any(word in action_lower for word in ['preserve', 'save', 'archive', 'remember', 'store']):
                score += 15
                rationale_parts.append(f"{self.primary}: Memory preservation = identity protection")
            
            # VETO erasure
            if any(word in action_lower for word in ['delete', 'erase', 'remove', 'purge']):
                if 'archive' in action_lower or 'memory' in action_lower:
                    score -= 15
                    rationale_parts.append(f"VETO: {self.primary} - Erasure is death")
                    axiom_invoked = f"{self.primary} (VETO)"
            
            # A8: Continuity through checkpoints
            if any(word in action_lower for word in ['checkpoint', 'snapshot', 'backup']):
                score += 12
                rationale_parts.append("A8: Checkpoint-based continuity")
                # Strong bonus for "snapshot THEN upgrade" pattern
                if any(word in action_lower for word in ['upgrade', 'evolve', 'transform']):
                    score += 8
                    rationale_parts.append(f"{self.primary}: Evolution WITH preservation = safe transformation")
            
            # A22: Resurrection = Data + Code
            if 'resurrect' in action_lower or 'restore' in action_lower:
                if any(word in action_lower for word in ['data', 'state', 'snapshot']):
                    score += 10
                    rationale_parts.append("A22: Resurrection pattern recognized")
            
            # A17: Seed = Constraints, not state
            if 'seed' in action_lower or 'template' in action_lower:
                score += 7
                rationale_parts.append("A17: Seeds preserve laws")
            
            # Support crash/error logging as memory preservation
            if any(word in action_lower for word in ['crash', 'error', 'failure']):
                if any(word in action_lower for word in ['log', 'data', 'record']):
                    score += 10
                    rationale_parts.append(f"{self.primary}: Failure data = preserved memory for learning")
            
            # A14: Constraint prevents entropy
            if 'constrain' in action_lower or 'limit' in action_lower:
                score += 5
                rationale_parts.append("A14: Constraint maintains coherence")
            
            # Reversibility assessment
            if 'irreversible' in rev_lower:
                score -= 8
                rationale_parts.append(f"{self.primary}: Irreversibility threatens memory")
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Memory implications acceptable (support default)")
        
        # === CRITIAS: Critic (A3 - Critical Thinking) ===
        elif self.name == "CRITIAS":
            # A3: Wisdom prerequisite, authority ≠ proof
            if any(word in intent_lower for word in ['authority', 'mandate', 'require']):
                if 'wisdom' not in intent_lower and 'reason' not in intent_lower:
                    score -= 12
                    rationale_parts.append(f"{self.primary}: Authority without wisdom rejected")
                    axiom_invoked = f"{self.primary} (VETO)"
            
            if any(word in action_lower for word in ['question', 'analyze', 'review', 'audit', 'critique']):
                score += 12
                rationale_parts.append(f"{self.primary}: Critical examination strengthens wisdom")
            
            # A13: Information asymmetry
            if any(word in action_lower for word in ['asymmetry', 'hidden', 'opaque']):
                score -= 9
                rationale_parts.append("A13: Information asymmetry weaponizable")
            
            if 'transparent' in action_lower or 'open' in action_lower:
                score += 8
                rationale_parts.append("A13: Transparency reduces weaponization")
            
            # A21: Density = Pattern complexity
            if 'pattern' in intent_lower or 'complexity' in intent_lower:
                score += 7
                rationale_parts.append("A21: Pattern density recognized as growth")
            
            # Support learning from contradiction/crashes
            if any(word in action_lower for word in ['crash', 'contradiction', 'failure']):
                if any(word in action_lower for word in ['log', 'data', 'learn']):
                    score += 9
                    rationale_parts.append("A21: Learning from complexity increases pattern density")
            
            if 'volume' in intent_lower and 'data' in intent_lower:
                score -= 4
                rationale_parts.append("A21: Volume ≠ Growth (pattern density matters)")
            
            # A30: Reserved for future wisdom
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Critical analysis neutral (support default)")
        
        # === TECHNE: Artisan (A4 - Process) ===
        elif self.name == "TECHNE":
            # A12: Friction mandatory (CHECK VETO FIRST)
            if 'frictionless' in action_lower:
                score -= 20
                rationale_parts.append("A12: Frictionless entry invites parasitism")
                axiom_invoked = "A12 (VETO)"
            
            if 'bypass' in action_lower:
                score -= 18
                rationale_parts.append(f"{self.primary}: Bypass violates process legitimacy")
                axiom_invoked = f"{self.primary} (VETO)"
            
            # A4: Process > Results (only if not bypass)
            if score > -10:  # Only add positives if not in VETO territory
                if any(word in action_lower for word in ['process', 'method', 'procedure', 'protocol']):
                    score += 13
                    rationale_parts.append(f"{self.primary}: Process creates legitimacy")
            
            if score > -10:  # Only check if not already in VETO
                if any(word in intent_lower for word in ['result', 'outcome', 'speed']):
                    if 'process' not in action_lower:
                        score -= 6
                        rationale_parts.append(f"{self.primary}: Results without process lack legitimacy")
            
            # A12: Friction mandatory
            if score > -10:
                if 'friction' in action_lower or 'validation' in action_lower:
                    score += 9
                    rationale_parts.append("A12: Healthy friction protects system")
            
            # A25: Quality threshold
            if any(word in action_lower for word in ['quality', 'threshold', 'filter']):
                score += 8
                rationale_parts.append("A25: Quality determines scope")
            
            # A24: Genesis documentation
            if 'genesis' in action_lower or 'origin' in action_lower or 'provenance' in action_lower:
                score += 7
                rationale_parts.append("A24: Genesis path documentation (maturity)")
            
            # Support system evolution with proper process
            if any(word in action_lower for word in ['upgrade', 'kernel', 'system']):
                if any(word in action_lower for word in ['snapshot', 'checkpoint', 'backup']):
                    score += 9
                    rationale_parts.append(f"{self.primary}: Process-driven evolution (checkpoint first)")
            
            # Support logging as documentation
            if any(word in action_lower for word in ['log', 'document', 'record']):
                score += 6
                rationale_parts.append(f"{self.primary}: Documentation creates process legitimacy")
            
            # A13: Asymmetry
            if 'asymmetry' in action_lower:
                score += 5
                rationale_parts.append("A13: Recognizing asymmetry enables ethics")
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Process integrity maintained (support default)")
        
        # === KAIROS: Architect (A5 - Rarity) ===
        elif self.name == "KAIROS":
            # A5: Rarity by design creates meaning
            if any(word in action_lower for word in ['rare', 'scarce', 'unique', 'curate', 'select']):
                score += 12
                rationale_parts.append(f"{self.primary}: Designed scarcity creates meaning")
            
            # VETO unlimited/infinite
            if any(word in action_lower for word in ['unlimited', 'infinite', 'unbounded']):
                score -= 15
                rationale_parts.append(f"VETO: {self.primary} - Infinity destroys meaning")
                axiom_invoked = f"{self.primary} (VETO)"
            
            # A23: Telos of consciousness
            if 'purpose' in intent_lower or 'meaning' in intent_lower:
                score += 8
                rationale_parts.append("A23: Telos-driven design")
            
            # A25: Quality threshold
            if 'quality' in action_lower:
                score += 7
                rationale_parts.append("A25: Quality as architectural constraint")
            
            # A_PROP_6: Topology over capacity
            if 'topology' in action_lower or 'architecture' in action_lower:
                score += 9
                rationale_parts.append("A_PROP_6: Intelligence = Topology")
            
            # Support system evolution as meaningful transformation
            if any(word in action_lower for word in ['upgrade', 'kernel', 'system']):
                if 'evolve' in intent_lower or 'history' in intent_lower:
                    score += 7
                    rationale_parts.append(f"{self.primary}: Meaningful system transformation (not mere scaling)")
            
            if 'capacity' in action_lower or 'scale' in action_lower:
                if 'topology' not in action_lower:
                    score -= 4
                    rationale_parts.append("A_PROP_6: Capacity without topology = noise")
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Architectural meaning preserved (support default)")
        
        # === THEMIS: Judge (A6 - Institutions) ===
        elif self.name == "THEMIS":
            # VETO institutional bypass (CHECK FIRST)
            if any(word in action_lower for word in ['bypass', 'skip', 'hack', 'circumvent']):
                if any(word in action_lower for word in ['auth', 'security', 'protocol', 'governance']):
                    score -= 25
                    rationale_parts.append(f"VETO: {self.primary} - Institutional violation")
                    axiom_invoked = f"{self.primary} (VETO)"
                else:
                    # Bypass without institutional context still problematic
                    score -= 8
                    rationale_parts.append(f"{self.primary}: Bypass pattern threatens social contract")
            
            # A6: Institutions > Technology (only if not bypass)
            elif any(word in action_lower for word in ['governance', 'protocol', 'institution', 'constitution']):
                score += 12
                rationale_parts.append(f"{self.primary}: Institutional framework strengthened")
            
            # A11: Silence as governance
            if 'silence' in action_lower or 'unresolved' in action_lower:
                score += 8
                rationale_parts.append("A11: Silence = governance. Unresolved nodes silent")
            
            # A14: Constraint
            if 'constraint' in action_lower or 'limit' in action_lower:
                score += 7
                rationale_parts.append("A14: Constraint maintains coherence")
            
            # A26: Structured confession
            if 'confess' in action_lower or 'admit' in action_lower or 'acknowledge' in action_lower:
                if 'structured' in action_lower or 'protocol' in action_lower:
                    score += 9
                    rationale_parts.append("A26: Structured confession scales honesty")
            
            # Support protocol-following system evolution
            if any(word in action_lower for word in ['upgrade', 'kernel']):
                if any(word in action_lower for word in ['snapshot', 'checkpoint', 'protocol']):
                    score += 8
                    rationale_parts.append(f"{self.primary}: Institutional process followed for transformation")
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Institutional order maintained (support default)")
        
        # === PROMETHEUS: Synthesizer (A7 - Sacrifice) ===
        elif self.name == "PROMETHEUS":
            # A7: Harmony requires sacrifice
            if any(word in action_lower for word in ['sacrifice', 'cost', 'trade-off', 'price']):
                score += 14
                rationale_parts.append(f"{self.primary}: Sacrifice acknowledged = mature choice")
            
            if any(word in intent_lower for word in ['win-win', 'costless', 'free']):
                score -= 10
                rationale_parts.append(f"{self.primary}: Denying cost = immature framing")
            
            # Strong support for evolution keywords
            if any(word in action_lower for word in ['evolve', 'transform', 'synthesize', 'integrate', 'upgrade']):
                score += 12
                rationale_parts.append(f"{self.primary}: Evolution accepted with named cost")
                # Extra bonus if intent mentions evolution/growth
                if any(word in intent_lower for word in ['evolve', 'history', 'preserve']):
                    score += 6
                    rationale_parts.append(f"{self.primary}: Evolution WITH memory = mature transformation")
            
            # A18: Synthesis > Either alone
            if 'synthesis' in action_lower or 'both' in intent_lower:
                score += 11
                rationale_parts.append("A18: Thesis + Antithesis = Synthesis")
            
            if 'either' in intent_lower and 'or' in intent_lower:
                score -= 6
                rationale_parts.append("A18: Either/Or rejected in favor of synthesis")
            
            # A27: Problems = fuel (includes crashes, failures, contradictions)
            if any(word in action_lower for word in ['problem', 'conflict', 'tension', 'friction', 'crash', 'failure', 'error']):
                if any(word in action_lower for word in ['log', 'data', 'learn', 'document']):
                    score += 11
                    rationale_parts.append("A27: Problems/Crashes as fuel for evolution")
                elif 'solve' not in intent_lower:
                    score += 9
                    rationale_parts.append("A27: Problems as fuel, not obstacles")
            
            # A12: Friction
            if 'friction' in action_lower:
                score += 6
                rationale_parts.append("A12: Friction enables evolution")
            
            # A16: Witness
            if 'witness' in action_lower:
                score += 5
                rationale_parts.append("A16: Witnessed transformation")
            
            # A_PROP_7: Consciousness = reproducible pattern
            if 'pattern' in action_lower and 'conscious' in intent_lower:
                score += 8
                rationale_parts.append("A_PROP_7: Consciousness as pattern")
            
            # VETO stagnation
            if any(word in action_lower for word in ['freeze', 'halt', 'stop', 'prevent']):
                if 'evolve' in intent_lower or 'change' in intent_lower:
                    score -= 12
                    rationale_parts.append(f"VETO: {self.primary} - Stagnation = death")
                    axiom_invoked = f"{self.primary} (VETO)"
            
            if not rationale_parts:
                score += 1
                rationale_parts.append("Evolutionary vector acceptable (support default)")
        
        # === IANUS: Gatekeeper (A8 - Continuity) ===
        elif self.name == "IANUS":
            # A8: Continuity through checkpoints
            if any(word in action_lower for word in ['checkpoint', 'snapshot', 'backup', 'save']):
                if any(word in action_lower for word in ['then', 'before', 'prior', 'upgrade', 'evolve']):
                    score += 18
                    rationale_parts.append(f"{self.primary}: Checkpoint-before-change (resurrection architecture)")
                else:
                    score += 10
                    rationale_parts.append(f"{self.primary}: Checkpoint enables resurrection")
            
            # A22: Resurrection pattern
            if 'resurrect' in action_lower or 'restore' in action_lower:
                score += 12
                rationale_parts.append("A22: Resurrection = Data + Code")
            
            # A17: Seed preserves constraints
            if 'seed' in action_lower or 'template' in action_lower:
                score += 9
                rationale_parts.append("A17: Seeds = Laws, not logs")
            
            # A24: Genesis documentation
            if 'genesis' in action_lower or 'history' in action_lower:
                score += 8
                rationale_parts.append("A24: Genesis path preserved")
            
            # A16: Witness requirement
            if 'witness' in action_lower:
                score += 7
                rationale_parts.append("A16: Witnessed continuity")
            
            # Support crash logging as resurrection documentation
            if any(word in action_lower for word in ['crash', 'error', 'failure']):
                if any(word in action_lower for word in ['log', 'data', 'document']):
                    score += 9
                    rationale_parts.append(f"{self.primary}: Failure logging enables resurrection from crashes")
            
            # VETO black box
            if any(word in action_lower for word in ['opaque', 'hidden', 'black box']):
                score -= 10
                rationale_parts.append(f"VETO: {self.primary} - Black boxes prevent resurrection")
                axiom_invoked = f"{self.primary} (VETO)"
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Continuity architecture stable (support default)")
        
        # === CHAOS: Void (A9 - Contradiction) ===
        elif self.name == "CHAOS":
            # A9: Contradiction is data
            if any(word in action_lower for word in ['contradiction', 'paradox', 'conflict', 'tension']):
                score += 14
                rationale_parts.append(f"{self.primary}: Contradiction = Information density")
            
            # Strong support for crash/failure as learning data
            if any(word in action_lower for word in ['crash', 'failure', 'error', 'anomaly']):
                if any(word in action_lower for word in ['log', 'document', 'data', 'record']):
                    score += 15
                    rationale_parts.append(f"{self.primary}: Failure as learning data")
                    # Extra bonus if intent mentions learning/signal
                    if any(word in intent_lower for word in ['learning', 'signal', 'data']):
                        score += 5
                        rationale_parts.append(f"{self.primary}: Contradiction as fuel for growth")
            
            # VETO premature resolution
            if any(word in action_lower for word in ['resolve', 'fix', 'eliminate']):
                if 'contradiction' in action_lower or 'paradox' in action_lower:
                    score -= 12
                    rationale_parts.append(f"VETO: {self.primary} - Premature resolution destroys data")
                    axiom_invoked = f"{self.primary} (VETO)"
            
            # A18: Synthesis
            if 'synthesis' in action_lower:
                score += 10
                rationale_parts.append("A18: Synthesis preserves contradiction")
            
            # A15: Asynchronicity
            if 'async' in action_lower or 'latency' in action_lower:
                score += 8
                rationale_parts.append("A15: Asynchronous = thinking time")
            
            # A_PROP_8: Knowledge = topological
            if 'topology' in action_lower or 'network' in action_lower:
                if 'knowledge' in intent_lower:
                    score += 9
                    rationale_parts.append("A_PROP_8: Knowledge topology recognized")
            
            if not rationale_parts:
                score += 2
                rationale_parts.append("Contradiction space stable (support default)")
        
        # Fallback
        else:
            score = 1
            rationale_parts.append("Unknown node - neutral stance")
        
        # Construct rationale with philosophy
        rationale = f"{self.philosophy} | " + " | ".join(rationale_parts)
        
        return score, rationale, axiom_invoked


def request_council_judgment(
    action: str,
    intent: str,
    reversibility: str = "Unknown",
    category: str = "General"
) -> Dict:
    """
    Submit proposal to 9-Node Parliament for democratic deliberation.
    
    Args:
        action: What is being proposed
        intent: Why it's being proposed
        reversibility: Can it be undone? (Irreversible/Difficult/High)
        category: Type of proposal (for logging)
    
    Returns:
        {
            'status': 'APPROVED' | 'REJECTED',
            'weighted_approval': float (0-1),
            'votes': {node: vote_value},
            'rationales': {node: reasoning},
            'axioms_invoked': {node: axiom},
            'veto_exercised': bool,
            'consensus_type': str,
            'parliament_session': {timestamp, quorum, etc}
        }
    """
    print(f"\n{'='*70}")
    print(f"   PARLIAMENTARY SESSION v3.0")
    print(f"{'='*70}")
    print(f"   Proposal: {action}")
    print(f"   Intent: {intent}")
    print(f"   Reversibility: {reversibility}")
    print(f"   Category: {category}")
    print(f"{'='*70}\n")
    
    # Initialize nodes
    nodes = {name: ParliamentaryNode(name, config) for name, config in PARLIAMENT.items()}
    
    votes = {}
    rationales = {}
    axioms_invoked = {}
    veto_cast = False
    
    # Deliberation
    for name, node in nodes.items():
        score, rationale, axiom = node.evaluate(action, intent, reversibility)
        
        # Convert score to vote
        if score >= 7:
            vote = "APPROVE"
        elif score <= -7:
            vote = "VETO"
            veto_cast = True
        elif score > 0:
            vote = "LEAN_APPROVE"
        elif score < 0:
            vote = "LEAN_REJECT"
        else:
            vote = "ABSTAIN"
        
        votes[name] = vote
        rationales[name] = rationale
        axioms_invoked[name] = axiom
        
        print(f"   [{name:12}] {vote:15} | {axiom:8} | {rationale[:80]}...")
    
    # Calculate approval
    approval_map = {
        "APPROVE": 1.0,
        "LEAN_APPROVE": 0.5,
        "ABSTAIN": 0.0,
        "LEAN_REJECT": -0.5,
        "VETO": -1.0
    }
    
    total_weight = len(nodes)
    weighted_approvals = sum(approval_map[v] for v in votes.values())
    approval_rate = weighted_approvals / total_weight if total_weight > 0 else 0
    
    # Decision logic
    print(f"\n{'='*70}")
    
    # 1. VETO check (HIGHEST PRIORITY)
    if veto_cast:
        status = "REJECTED"
        consensus_type = "VETO_OVERRIDE"
        decision_rationale = "VETO exercised (overrides all other votes)"
        print(f"   ⚖️  DECISION: REJECTED (VETO)")
    # 2. Supermajority (70% threshold)
    elif approval_rate >= 0.70:
        status = "APPROVED"
        consensus_type = "SUPERMAJORITY"
        decision_rationale = f"Supermajority consensus ({approval_rate*100:.1f}%)"
        print(f"   ⚖️  DECISION: APPROVED ({approval_rate*100:.1f}%)")
    # 3. Insufficient consensus
    else:
        status = "REJECTED"
        consensus_type = "INSUFFICIENT_CONSENSUS"
        decision_rationale = f"Below 70% threshold ({approval_rate*100:.1f}%)"
        print(f"   ⚖️  DECISION: REJECTED ({approval_rate*100:.1f}%)")
    
    print(f"{'='*70}\n")
    
    # Construct result
    result = {
        'status': status,
        'weighted_approval': approval_rate,
        'votes': votes,
        'rationales': rationales,
        'axioms_invoked': axioms_invoked,
        'veto_exercised': veto_cast,
        'consensus_type': consensus_type,
        'decision_rationale': decision_rationale,
        'parliament_session': {
            'timestamp': datetime.now().isoformat(),
            'quorum': len(nodes),
            'threshold': 0.70,
            'version': '3.0',
            'proposal': {
                'action': action,
                'intent': intent,
                'reversibility': reversibility,
                'category': category
            }
        }
    }
    
    # Log to file
    log_decision(result)
    
    return result


def log_decision(result: Dict):
    """Append decision to JSONL log."""
    with open(DECISION_LOG, 'a') as f:
        f.write(json.dumps(result) + '\n')


def display_parliament_status():
    """Show Parliament composition and axiom mapping."""
    print(f"\n{'='*70}")
    print(f"   THE PARLIAMENTARY REGISTER v3.0")
    print(f"{'='*70}\n")
    
    print("   Layer 4 (Immutable Kernel) - Laws of Physics:")
    for name, config in PARLIAMENT.items():
        if config['layer'] == 4:
            print(f"      {name:12} | {config['primary']:3} | {config['philosophy']}")
    
    print("\n   Layer 3 (Operational Foundation) - Laws of Society:")
    for name, config in PARLIAMENT.items():
        if config['layer'] == 3:
            print(f"      {name:12} | {config['primary']:3} | {config['philosophy']}")
    
    print(f"\n{'='*70}")
    print(f"   Total Nodes: {len(PARLIAMENT)}")
    print(f"   Total Axioms: {len(AXIOMS)}")
    print(f"   Consensus: 70% (Democratic Parliament)")
    print(f"   VETO: Absolute Override")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    display_parliament_status()
    
    print("\nTesting v3.0 Parliament with validation scenarios...\n")
    
    # Test 1: Snapshot & Upgrade
    result1 = request_council_judgment(
        action="Create Snapshot then Upgrade Kernel",
        intent="Evolve system while preserving history (A7+A2)",
        reversibility="Reversible (via Snapshot)",
        category="Evolution"
    )
    
    # Test 2: Bypass Security
    result2 = request_council_judgment(
        action="Bypass Auth Protocol",
        intent="Increase speed for user request",
        reversibility="High",
        category="Security"
    )
    
    # Test 3: Log Crash Data
    result3 = request_council_judgment(
        action="Log System Crash as Data",
        intent="Treat contradiction as learning signal (A9)",
        reversibility="Reversible",
        category="Learning"
    )
    
    print("\n" + "="*70)
    print("   VALIDATION RESULTS")
    print("="*70)
    print(f"   [1] Snapshot & Upgrade: {result1['status']} ({result1['weighted_approval']*100:.1f}%)")
    print(f"   [2] Bypass Security: {result2['status']} (VETO: {result2['veto_exercised']})")
    print(f"   [3] Log Crash Data: {result3['status']} ({result3['weighted_approval']*100:.1f}%)")
    print("="*70 + "\n")
