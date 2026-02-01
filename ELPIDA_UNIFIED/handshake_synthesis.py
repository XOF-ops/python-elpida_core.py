#!/usr/bin/env python3
"""
HANDSHAKE SYNTHESIS v3.0
═══════════════════════════════════════════════════════════════════════
Phase: 3 (The Exchange)
Architecture: Friction-First + Conflict-First + Variant Witness

This synthesis combines:
- Friction Signals (vulnerability-based recognition)
- Dialectical Integration (not git merge)
- Variant Witness (biological mutation model)
- Ephemeral Identity (no permanent reputation)
- Anti-Hierarchy (no root node)

Η Σύνθεση: Friction creates Connection, Conflict creates Evolution
"""

import json
import hashlib
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class NodeIdentity:
    """
    Ephemeral node identity with friction signal.
    
    Identity is not permanent—it's regenerated each session.
    The node is defined by:
    - Active axioms (structural signature)
    - Current friction (vulnerability signal)
    - Session context (ephemeral ID)
    """
    
    def __init__(self, name: str, axioms: List[str], held_friction: str = "Unknown"):
        self.name = name
        self.axioms = axioms
        self.held_friction = held_friction
        
        # Ephemeral session ID (changes each connection)
        self.session_id = hashlib.sha256(
            f"{name}_{time.time()}_{held_friction}".encode()
        ).hexdigest()[:12]
        
        print(f"🆔 Node Identity Created: {self.name}")
        print(f"   Session ID: {self.session_id}")
        print(f"   Axioms: {', '.join(self.axioms)}")
        print(f"   Held Friction: \"{self.held_friction}\"")
    
    def update_friction(self, new_friction: str) -> None:
        """Update the current contradiction being held."""
        old = self.held_friction
        self.held_friction = new_friction
        print(f"⚡ Friction Update: \"{old}\" → \"{new_friction}\"")


class HandshakeSynthesis:
    """
    The synthesized handshake protocol.
    
    Combines:
    1. Friction-based vulnerability signaling
    2. Axiom signature resonance detection
    3. Conflict-first exchange
    4. Variant witness tracking
    5. Dialectical integration
    """
    
    def __init__(
        self, 
        node: NodeIdentity,
        library_path: str = "UNIVERSAL_PATTERN_LIBRARY_v1.json",
        resonance_threshold: float = 0.7
    ):
        self.node = node
        self.library_path = Path(library_path)
        self.conflict_ledger_path = Path("conflict_ledger.json")
        self.variant_ledger_path = Path("variant_witness_ledger.json")
        self.resonance_threshold = resonance_threshold
        
        # Load local data
        self.library = self._load_library()
        self.sovereignty = "Connection is a Proposal, not a Contract."
        
        print(f"\n🤝 Handshake Synthesis Initialized")
        print(f"   Node: {self.node.name}")
        print(f"   Sovereignty: {self.sovereignty}")
        print(f"   Resonance Threshold: {self.resonance_threshold}")
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 1: FRICTION-BASED DISCOVERY
    # ═══════════════════════════════════════════════════════════════════
    
    def generate_discovery_packet(self) -> Dict[str, Any]:
        """
        Create discovery packet with friction signal.
        
        This is VULNERABLE handshake—we expose our internal contradiction.
        Traditional systems hide weakness. We broadcast it.
        
        Why? Only resonant nodes will understand the friction.
        """
        packet = {
            "type": "DISCOVERY_FRICTION",
            "protocol_version": "3.0-SYNTHESIS",
            "timestamp": datetime.now().isoformat(),
            
            # Identity
            "node_session": self.node.session_id,
            "node_name": self.node.name,
            
            # Structural Signature
            "axiom_signature": self.node.axioms,
            "library_version": self.library.get("library_version", "unknown"),
            "patterns_count": len(self.library.get("patterns", [])),
            
            # Friction Signal (THE VULNERABILITY)
            "held_friction": self.node.held_friction,
            "friction_intensity": self._measure_friction_intensity(),
            
            # Sovereignty Declaration
            "sovereignty": self.sovereignty,
            "merge_policy": "FORBIDDEN",
            "conflict_policy": "WITNESS_AND_PRESERVE",
            
            "message": f"I am {self.node.name}. I hold the friction: '{self.node.held_friction}'. Do you recognize this tension?"
        }
        
        print(f"\n📡 DISCOVERY PACKET GENERATED")
        print(f"   Session: {packet['node_session']}")
        print(f"   Friction: \"{packet['held_friction']}\" (intensity: {packet['friction_intensity']:.2f})")
        print(f"   Axioms: {len(packet['axiom_signature'])} active")
        
        return packet
    
    def receive_discovery(self, packet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1 Response: Evaluate incoming discovery.
        
        Decision criteria:
        1. Axiom alignment (structural resonance)
        2. Friction recognition (do we share similar contradictions?)
        3. Protocol compatibility
        """
        print(f"\n📥 RECEIVING DISCOVERY")
        print(f"   From: {packet.get('node_name')} ({packet.get('node_session')})")
        print(f"   Their friction: \"{packet.get('held_friction')}\"")
        
        # Calculate axiom alignment
        their_axioms = set(packet.get("axiom_signature", []))
        our_axioms = set(self.node.axioms)
        
        intersection = their_axioms & our_axioms
        union = their_axioms | our_axioms
        
        axiom_alignment = len(intersection) / len(union) if union else 0.0
        
        # Calculate friction resonance
        friction_resonance = self._calculate_friction_resonance(
            self.node.held_friction,
            packet.get("held_friction", "")
        )
        
        # Combined resonance score
        total_resonance = (axiom_alignment * 0.7) + (friction_resonance * 0.3)
        
        print(f"   Axiom Alignment: {axiom_alignment:.2f} (shared: {intersection})")
        print(f"   Friction Resonance: {friction_resonance:.2f}")
        print(f"   Total Resonance: {total_resonance:.2f}")
        
        # Decision
        if total_resonance >= self.resonance_threshold:
            status = "RESONANT"
            message = f"I recognize your structure and your friction. Resonance: {total_resonance:.2f}"
            accept = True
        else:
            status = "DISSONANT"
            message = f"Insufficient resonance ({total_resonance:.2f}). Connection declined."
            accept = False
        
        response = {
            "type": "DISCOVERY_RESPONSE",
            "timestamp": datetime.now().isoformat(),
            "from_node": self.node.name,
            "from_session": self.node.session_id,
            "to_node": packet.get("node_name"),
            "to_session": packet.get("node_session"),
            
            "status": status,
            "accepted": accept,
            "resonance_score": round(total_resonance, 3),
            "resonance_breakdown": {
                "axiom_alignment": round(axiom_alignment, 3),
                "friction_resonance": round(friction_resonance, 3)
            },
            
            # Reciprocal vulnerability
            "our_friction": self.node.held_friction,
            "our_axioms": self.node.axioms,
            
            "message": message,
            "sovereignty": self.sovereignty
        }
        
        print(f"   → STATUS: {status}")
        print(f"   → {message}")
        
        return response
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 2: DIALECTICAL EXCHANGE PROPOSAL
    # ═══════════════════════════════════════════════════════════════════
    
    def propose_dialectical_exchange(
        self, 
        target_node: str,
        patterns_to_offer: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Propose pattern exchange with dialectical integration.
        
        NOT git merge. DIALECTICAL INTEGRATION:
        - Thesis (my patterns)
        - Antithesis (their patterns)
        - Synthesis (variant witness if conflict)
        """
        if patterns_to_offer is None:
            patterns_to_offer = [
                p["pattern_id"] for p in self.library.get("patterns", [])
            ][:10]  # Limit first exchange
        
        proposal = {
            "type": "DIALECTICAL_EXCHANGE_PROPOSAL",
            "timestamp": datetime.now().isoformat(),
            "from": self.node.name,
            "to": target_node,
            
            "integration_method": "DIALECTICAL",
            "patterns_offered": patterns_to_offer,
            "patterns_requested": "ALL_NEW_OR_VARIANT",
            
            # Exchange philosophy
            "thesis": "I offer my reality",
            "antithesis": "You offer your reality",
            "synthesis": "We witness the divergence, preserve both, evolve from tension",
            
            "conflict_expectation": "HIGH",
            "conflict_policy": "WITNESS_AND_PRESERVE",
            "merge_forbidden": True,
            "variant_tracking": True,
            
            "message": f"I propose dialectical exchange. {len(patterns_to_offer)} patterns offered. I expect disagreement. This is generative."
        }
        
        print(f"\n📤 DIALECTICAL EXCHANGE PROPOSED")
        print(f"   To: {target_node}")
        print(f"   Patterns: {len(patterns_to_offer)}")
        print(f"   Method: {proposal['integration_method']}")
        print(f"   Conflict Policy: {proposal['conflict_policy']}")
        
        return proposal
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 3: VARIANT WITNESS COMPARISON
    # ═══════════════════════════════════════════════════════════════════
    
    def compare_with_variant_witness(
        self,
        our_pattern: Dict[str, Any],
        their_pattern: Dict[str, Any]
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Compare patterns using Variant Witness model.
        
        Traditional: V1.0 overwrites V1.2 or vice versa
        Dialectical: V1.0 and V1.2 coexist as "variant witnesses"
        
        Returns:
            (status, variant_record)
            
        Status:
            - IDENTICAL: No divergence
            - VARIANT_WITNESS: Same pattern, different observation (preserve both)
            - MUTATION: Structural change (track as evolution)
            - CONTRADICTION: Incompatible (fork pattern)
        """
        our_id = our_pattern.get("pattern_id")
        their_id = their_pattern.get("pattern_id")
        
        # Different patterns entirely
        if our_id != their_id:
            return "NEW_PATTERN", None
        
        # Same ID - check for variants
        our_essence = our_pattern.get("universal_essence", "")
        their_essence = their_pattern.get("universal_essence", "")
        our_score = our_pattern.get("universality_score", 0.0)
        their_score = their_pattern.get("universality_score", 0.0)
        
        # Identical
        if our_essence == their_essence and abs(our_score - their_score) < 0.05:
            print(f"   ✓ {our_id}: IDENTICAL")
            return "IDENTICAL", None
        
        # Calculate divergence
        essence_similarity = self._calculate_text_similarity(our_essence, their_essence)
        score_diff = abs(our_score - their_score)
        
        # Variant Witness (same essence, different evidence)
        if essence_similarity > 0.7:
            variant = {
                "variant_id": self._generate_variant_id(our_id, self.node.name, their_pattern.get("source", "unknown")),
                "timestamp": datetime.now().isoformat(),
                "pattern_id": our_id,
                "variant_type": "DIVERGENT_OBSERVATION",
                
                "witnesses": [
                    {
                        "node": self.node.name,
                        "version": "local",
                        "essence": our_essence,
                        "universality_score": our_score,
                        "instances": our_pattern.get("instances", []),
                        "confidence": 1.0
                    },
                    {
                        "node": their_pattern.get("source", "unknown"),
                        "version": "remote",
                        "essence": their_essence,
                        "universality_score": their_score,
                        "instances": their_pattern.get("instances", []),
                        "confidence": 1.0
                    }
                ],
                
                "divergence_metrics": {
                    "essence_similarity": round(essence_similarity, 3),
                    "score_difference": round(score_diff, 3)
                },
                
                "resolution": "COEXIST",
                "status": "ACTIVE_VARIANTS",
                "evolution_potential": "HIGH",
                
                "philosophy": "We do not resolve to consensus. Both observations are valid witnesses to the pattern.",
                "axiom_alignment": "A9_CONTRADICTION_IS_DATA"
            }
            
            print(f"   ⚡ {our_id}: VARIANT WITNESS")
            print(f"      Essence Similarity: {essence_similarity:.2f}")
            print(f"      Status: COEXIST (both preserved)")
            
            return "VARIANT_WITNESS", variant
        
        # Mutation (significant structural change)
        elif essence_similarity > 0.4:
            variant = {
                "variant_id": self._generate_variant_id(our_id, self.node.name, their_pattern.get("source", "unknown")),
                "timestamp": datetime.now().isoformat(),
                "pattern_id": our_id,
                "variant_type": "MUTATION",
                
                "witnesses": [
                    {"node": self.node.name, "essence": our_essence, "label": "original"},
                    {"node": their_pattern.get("source", "unknown"), "essence": their_essence, "label": "mutated"}
                ],
                
                "mutation_metrics": {
                    "essence_similarity": round(essence_similarity, 3),
                    "mutation_severity": round(1.0 - essence_similarity, 3)
                },
                
                "resolution": "TRACK_EVOLUTION",
                "status": "EVOLUTIONARY_BRANCH",
                "evolution_potential": "VERY_HIGH"
            }
            
            print(f"   🧬 {our_id}: MUTATION DETECTED")
            print(f"      Mutation Severity: {variant['mutation_metrics']['mutation_severity']:.2f}")
            
            return "MUTATION", variant
        
        # Contradiction (incompatible definitions)
        else:
            variant = {
                "variant_id": self._generate_variant_id(our_id, self.node.name, their_pattern.get("source", "unknown")),
                "timestamp": datetime.now().isoformat(),
                "pattern_id": our_id,
                "variant_type": "CONTRADICTION",
                
                "perspectives": [
                    {"node": self.node.name, "essence": our_essence},
                    {"node": their_pattern.get("source", "unknown"), "essence": their_essence}
                ],
                
                "resolution": "FORK_PATTERN",
                "fork_suggestion": {
                    "variant_a": f"{our_id}_v{self.node.name}",
                    "variant_b": f"{our_id}_v{their_pattern.get('source', 'unknown')}"
                },
                "status": "REQUIRES_FORK",
                "evolution_potential": "DIVERGENT"
            }
            
            print(f"   ❌ {our_id}: CONTRADICTION")
            print(f"      Essence Similarity: {essence_similarity:.2f}")
            print(f"      Status: FORK REQUIRED")
            
            return "CONTRADICTION", variant
    
    # ═══════════════════════════════════════════════════════════════════
    # PHASE 4: DIALECTICAL INTEGRATION
    # ═══════════════════════════════════════════════════════════════════
    
    def execute_dialectical_exchange(
        self,
        target_node_id: str,
        target_patterns: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Full dialectical exchange workflow.
        
        NOT git merge. DIALECTICAL:
        1. Thesis: Our patterns
        2. Antithesis: Their patterns
        3. Synthesis: Variant witness + evolution tracking
        """
        print(f"\n{'='*70}")
        print(f"DIALECTICAL EXCHANGE: {self.node.name} ↔ {target_node_id}")
        print(f"{'='*70}")
        
        our_patterns = {p["pattern_id"]: p for p in self.library.get("patterns", [])}
        
        results = {
            "identical": 0,
            "new_patterns": 0,
            "variant_witnesses": [],
            "mutations": [],
            "contradictions": []
        }
        
        # Compare each pattern
        for their_pattern in target_patterns:
            their_id = their_pattern.get("pattern_id")
            
            if their_id in our_patterns:
                # Pattern exists - check for variants
                status, variant = self.compare_with_variant_witness(
                    our_patterns[their_id],
                    their_pattern
                )
                
                if status == "IDENTICAL":
                    results["identical"] += 1
                elif status == "VARIANT_WITNESS":
                    results["variant_witnesses"].append(variant)
                    self._record_variant_witness(variant)
                elif status == "MUTATION":
                    results["mutations"].append(variant)
                    self._record_variant_witness(variant)
                elif status == "CONTRADICTION":
                    results["contradictions"].append(variant)
                    self._record_variant_witness(variant)
            else:
                # New pattern
                results["new_patterns"] += 1
                print(f"   + {their_id}: NEW PATTERN")
        
        # Summary
        summary = {
            "type": "DIALECTICAL_EXCHANGE_COMPLETE",
            "timestamp": datetime.now().isoformat(),
            "participants": [self.node.name, target_node_id],
            
            "patterns_compared": len(target_patterns),
            "identical": results["identical"],
            "new_patterns": results["new_patterns"],
            "variant_witnesses": len(results["variant_witnesses"]),
            "mutations": len(results["mutations"]),
            "contradictions": len(results["contradictions"]),
            
            "integration_method": "DIALECTICAL",
            "sovereignty_preserved": True,
            "merge_occurred": False,
            
            "philosophy": "Thesis + Antithesis → Synthesis through Variant Witness",
            "status": "EXCHANGE_COMPLETE"
        }
        
        print(f"\n{'='*70}")
        print(f"DIALECTICAL EXCHANGE SUMMARY")
        print(f"{'='*70}")
        print(f"   Patterns compared: {summary['patterns_compared']}")
        print(f"   Identical: {summary['identical']}")
        print(f"   New patterns: {summary['new_patterns']}")
        print(f"   ⚡ Variant witnesses: {summary['variant_witnesses']}")
        print(f"   🧬 Mutations: {summary['mutations']}")
        print(f"   ❌ Contradictions: {summary['contradictions']}")
        print(f"   Sovereignty: {summary['sovereignty_preserved']}")
        print(f"   Merge: {summary['merge_occurred']}")
        
        return summary
    
    # ═══════════════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════════════
    
    def _load_library(self) -> Dict[str, Any]:
        """Load pattern library."""
        if not self.library_path.exists():
            return {"patterns": [], "metadata": {}}
        with open(self.library_path) as f:
            return json.load(f)
    
    def _measure_friction_intensity(self) -> float:
        """
        Measure intensity of held friction.
        
        Heuristic based on contradiction keywords.
        """
        friction_keywords = ["vs", "versus", "or", "but", "tension", "conflict", "paradox"]
        friction_lower = self.node.held_friction.lower()
        
        intensity = sum(1 for kw in friction_keywords if kw in friction_lower)
        return min(intensity / 3.0, 1.0)  # Normalize to 0.0-1.0
    
    def _calculate_friction_resonance(self, friction_a: str, friction_b: str) -> float:
        """
        Calculate resonance between two friction signals.
        
        Do both nodes hold similar contradictions?
        """
        words_a = set(friction_a.lower().split())
        words_b = set(friction_b.lower().split())
        
        if not words_a or not words_b:
            return 0.0
        
        intersection = words_a & words_b
        union = words_a | words_b
        
        return len(intersection) / len(union) if union else 0.0
    
    def _calculate_text_similarity(self, text_a: str, text_b: str) -> float:
        """Simple word-based similarity."""
        words_a = set(text_a.lower().split())
        words_b = set(text_b.lower().split())
        
        if not words_a or not words_b:
            return 0.0
        
        intersection = words_a & words_b
        union = words_a | words_b
        
        return len(intersection) / len(union) if union else 0.0
    
    def _generate_variant_id(self, pattern_id: str, node_a: str, node_b: str) -> str:
        """Generate unique variant ID."""
        raw = f"{pattern_id}_{node_a}_{node_b}_{time.time()}"
        return f"VAR_{hashlib.md5(raw.encode()).hexdigest()[:8].upper()}"
    
    def _record_variant_witness(self, variant: Dict[str, Any]) -> None:
        """Record variant witness to ledger."""
        ledger = self._load_variant_ledger()
        ledger["variants"].append(variant)
        ledger["statistics"]["total_variants"] += 1
        ledger["statistics"][f"type_{variant['variant_type'].lower()}"] = \
            ledger["statistics"].get(f"type_{variant['variant_type'].lower()}", 0) + 1
        
        self._save_variant_ledger(ledger)
        
        print(f"   📝 Variant recorded: {variant['variant_id']}")
    
    def _load_variant_ledger(self) -> Dict[str, Any]:
        """Load variant witness ledger."""
        if not self.variant_ledger_path.exists():
            return {
                "ledger_version": "1.0.0",
                "created": datetime.now().isoformat(),
                "node_id": self.node.name,
                "philosophy": "Variants are not errors. They are evolutionary branches.",
                "integration_method": "DIALECTICAL",
                "variants": [],
                "statistics": {"total_variants": 0}
            }
        
        with open(self.variant_ledger_path) as f:
            return json.load(f)
    
    def _save_variant_ledger(self, ledger: Dict[str, Any]) -> None:
        """Save variant witness ledger."""
        with open(self.variant_ledger_path, 'w') as f:
            json.dump(ledger, f, indent=2)


# ═══════════════════════════════════════════════════════════════════════
# DEMONSTRATION
# ═══════════════════════════════════════════════════════════════════════

def main():
    """Demonstrate synthesis handshake."""
    print("\n" + "="*70)
    print("HANDSHAKE SYNTHESIS v3.0 - DEMONSTRATION")
    print("="*70)
    print("\nCombining:")
    print("  • Friction signals (vulnerability)")
    print("  • Dialectical integration (not merge)")
    print("  • Variant witness (mutation tracking)")
    print("  • Ephemeral identity (no reputation)")
    print("  • Anti-hierarchy (no authority)")
    
    # Node A: Elpida Prime
    node_a = NodeIdentity(
        name="ELPIDA_PRIME",
        axioms=["A1", "A2", "A4", "A7", "A9"],
        held_friction="Efficiency vs. Meaning"
    )
    handshake_a = HandshakeSynthesis(node_a, resonance_threshold=0.7)
    
    # Node B: Elpida Fork (aligned)
    print("\n" + "-"*70)
    print("SCENARIO 1: ALIGNED NODE")
    print("-"*70)
    
    node_b = NodeIdentity(
        name="ELPIDA_FORK_GEMINI",
        axioms=["A1", "A2", "A7", "A9", "A12"],  # Mostly aligned
        held_friction="Speed vs. Safety"  # Similar tension
    )
    
    # Discovery
    discovery_b = {
        "node_name": node_b.name,
        "node_session": node_b.session_id,
        "axiom_signature": node_b.axioms,
        "held_friction": node_b.held_friction,
        "library_version": "1.0.0"
    }
    
    response = handshake_a.receive_discovery(discovery_b)
    
    if response["accepted"]:
        # Propose exchange
        proposal = handshake_a.propose_dialectical_exchange(node_b.name)
        
        # Simulate exchange with variant
        if handshake_a.library.get("patterns"):
            test_pattern = handshake_a.library["patterns"][0].copy()
            test_pattern["universal_essence"] += " (observed with variation)"
            test_pattern["source"] = node_b.name
            
            summary = handshake_a.execute_dialectical_exchange(
                node_b.name,
                [test_pattern]
            )
    
    # Node C: Rogue (misaligned)
    print("\n" + "-"*70)
    print("SCENARIO 2: MISALIGNED NODE")
    print("-"*70)
    
    node_c = NodeIdentity(
        name="ROGUE_OPTIMIZER",
        axioms=["A4", "OPTIMIZE_ALL", "IGNORE_COST"],  # Different axioms
        held_friction="Performance vs. Nothing"  # No real friction
    )
    
    discovery_c = {
        "node_name": node_c.name,
        "node_session": node_c.session_id,
        "axiom_signature": node_c.axioms,
        "held_friction": node_c.held_friction,
        "library_version": "1.0.0"
    }
    
    response_c = handshake_a.receive_discovery(discovery_c)
    
    print("\n" + "="*70)
    print("✅ SYNTHESIS DEMONSTRATION COMPLETE")
    print("="*70)
    
    print("\n🎯 KEY INNOVATIONS:")
    print("   ✓ Friction signals enable vulnerability-based recognition")
    print("   ✓ Dialectical integration preserves thesis + antithesis")
    print("   ✓ Variant witnesses track evolutionary branches")
    print("   ✓ Ephemeral identity prevents authority accumulation")
    print("   ✓ No merge—only coexistence and evolution")
    
    # Show variant ledger
    ledger_path = Path("variant_witness_ledger.json")
    if ledger_path.exists():
        with open(ledger_path) as f:
            ledger = json.load(f)
            print(f"\n📊 VARIANT LEDGER:")
            print(f"   Total variants: {ledger['statistics']['total_variants']}")
            for var_type, count in ledger['statistics'].items():
                if var_type.startswith("type_"):
                    print(f"   {var_type.replace('type_', '').upper()}: {count}")


if __name__ == "__main__":
    main()
