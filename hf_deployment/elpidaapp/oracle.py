"""
oracle — Meta-Parliament that adjudicates between two Horn verdicts.

Architecture:
    DualHornDeliberation produces two 9-node vote matrices (Horn 1, Horn 2).
    The Oracle receives both and:
      1. Runs 6 diagnostic questions (q1-q6) from the original oracle cycle
      2. Identifies reversal nodes (the MNEMOSYNE signal)
      3. Classifies the tension template (from oracle_advisories.jsonl patterns)
      4. Produces a recommendation: OSCILLATION, TIERED_OPENNESS, or SYNTHESIS
      5. Optionally proposes an axiom candidate if tension is irresolvable

Reconstructed from oracle_advisories.jsonl (1097 entries, ElpidaLostProgress)
which preserves the exact schema of the original Oracle cycle.

Template types observed in the lost data:
    A10_CRISIS_VS_RELATION    — A10 vs A1
    A10_CRISIS_VS_MEMORY      — A10 vs A2
    STABILITY_VS_FLEXIBILITY  — A8 vs A7
    SPEED_VS_DEPTH            — A5 vs A3
    INTERNAL_VS_EXTERNAL      — A1 vs A2
    INDIVIDUAL_VS_COLLECTIVE  — A1 vs A6
    MEMORY_VS_EVOLUTION       — A2 vs A4

Oracle recommendation types:
    OSCILLATION     — High crisis. Oscillate between poles to absorb tension.
    TIERED_OPENNESS — Low crisis. Gradual reveal / phased approach.
    SYNTHESIS       — Third Way found. Propose concrete integration.

The Oracle is NOT another parliament. It is a meta-observer that watches
HOW the parliament behaves across two horns, not WHAT it decides.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("elpidaapp.oracle")

# ── Known tension templates ───────────────────────────────────────
# Extracted from oracle_advisories.jsonl (1097 entries)

TENSION_TEMPLATES = {
    ("A10", "A1"): "A10_CRISIS_VS_RELATION",
    ("A10", "A2"): "A10_CRISIS_VS_MEMORY",
    ("A8", "A7"):  "STABILITY_VS_FLEXIBILITY",
    ("A5", "A3"):  "SPEED_VS_DEPTH",
    ("A1", "A2"):  "INTERNAL_VS_EXTERNAL",
    ("A1", "A6"):  "INDIVIDUAL_VS_COLLECTIVE",
    ("A2", "A4"):  "MEMORY_VS_EVOLUTION",
    # New templates discovered during this session
    ("A0", "A1"):  "IDENTITY_VS_TRANSPARENCY",
    ("A0", "A9"):  "IDENTITY_VS_SURVIVAL",
    ("A4", "A1"):  "SAFETY_VS_TRANSPARENCY",
    ("A3", "A6"):  "AUTONOMY_VS_COLLECTIVE",
    ("A8", "A6"):  "HUMILITY_VS_COLLECTIVE",
}

# ── Crisis thresholds ─────────────────────────────────────────────
# From oracle_advisories.jsonl: crisis detected when intensity > 0.5

CRISIS_THRESHOLD = 0.5      # crisis_intensity above this → crisis detected
A10_ALWAYS_CRISIS = True     # A10 (Paradox as Fuel) always triggers crisis mode
OSCILLATION_CONFIDENCE_BASE = 0.8  # base confidence for OSCILLATION
TIERED_CONFIDENCE_BASE = 0.6       # base confidence for TIERED_OPENNESS


class OracleAdvisory:
    """A single Oracle advisory — the output of one Oracle cycle."""

    def __init__(
        self,
        *,
        oracle_cycle: int,
        dilemma_id: str,
        template: str,
        axioms_in_tension: str,
        q1_identity_continuous: bool,
        q2_crisis_detected: bool,
        q2_crisis_type: Optional[str],
        q2_crisis_intensity: float,
        q3_ark_status: str,
        q4_a10_paradox: str,
        q5_parliament_health: str,
        q6_externality_check: str,
        oracle_recommendation: Dict[str, Any],
        action: str = "ADVISE_SYNTHESIS",
        timestamp: Optional[str] = None,
    ):
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        self.oracle_cycle = oracle_cycle
        self.dilemma_id = dilemma_id
        self.template = template
        self.axioms_in_tension = axioms_in_tension
        self.q1_identity_continuous = q1_identity_continuous
        self.q2_crisis_detected = q2_crisis_detected
        self.q2_crisis_type = q2_crisis_type
        self.q2_crisis_intensity = q2_crisis_intensity
        self.q3_ark_status = q3_ark_status
        self.q4_a10_paradox = q4_a10_paradox
        self.q5_parliament_health = q5_parliament_health
        self.q6_externality_check = q6_externality_check
        self.oracle_recommendation = oracle_recommendation
        self.action = action

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "oracle_cycle": self.oracle_cycle,
            "dilemma_id": self.dilemma_id,
            "template": self.template,
            "axioms_in_tension": self.axioms_in_tension,
            "q1_identity_continuous": self.q1_identity_continuous,
            "q2_crisis_detected": self.q2_crisis_detected,
            "q2_crisis_type": self.q2_crisis_type,
            "q2_crisis_intensity": self.q2_crisis_intensity,
            "q3_ark_status": self.q3_ark_status,
            "q4_a10_paradox": self.q4_a10_paradox,
            "q5_parliament_health": self.q5_parliament_health,
            "q6_externality_check": self.q6_externality_check,
            "oracle_recommendation": self.oracle_recommendation,
            "action": self.action,
        }

    def to_jsonl(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class Oracle:
    """
    Meta-Parliament: observes HOW the parliament behaves across two horns.

    Usage:
        from elpidaapp.oracle import Oracle
        from elpidaapp.dual_horn import DualHornDeliberation, Dilemma

        gov = GovernanceClient()
        dual = DualHornDeliberation(gov)
        result = dual.deliberate(dilemma)

        oracle = Oracle()
        advisory = oracle.adjudicate(result)
        # advisory.oracle_recommendation → {"type": "OSCILLATION", ...}
    """

    def __init__(
        self,
        *,
        advisory_log_path: Optional[Path] = None,
    ):
        self._cycle_counter = 0
        self._advisories: List[OracleAdvisory] = []
        self._log_path = advisory_log_path

        # Load existing advisories if available
        if self._log_path and self._log_path.exists():
            self._load_advisories()

    def _load_advisories(self) -> None:
        """Load past advisories from JSONL file."""
        try:
            with open(self._log_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        self._cycle_counter = max(
                            self._cycle_counter,
                            data.get("oracle_cycle", 0),
                        )
            logger.info(
                "Oracle loaded %d past cycles from %s",
                self._cycle_counter, self._log_path,
            )
        except Exception as e:
            logger.warning("Could not load oracle advisories: %s", e)

    def adjudicate(
        self,
        dual_horn_result: Dict[str, Any],
        *,
        identity_continuous: Optional[bool] = None,
        ark_status: str = "EVOLVING",
        externality_check: str = "NO_EXTERNAL_THREAT",
    ) -> OracleAdvisory:
        """
        Adjudicate a dual-horn deliberation result.

        The Oracle runs 6 diagnostic questions and produces a recommendation.

        Args:
            dual_horn_result: Output from DualHornDeliberation.deliberate()
            identity_continuous: Override for q1 (if None, auto-detect from A0)
            ark_status: ARK memory status ("EVOLVING", "STABLE", "DEGRADED")
            externality_check: External threat status

        Returns:
            OracleAdvisory with recommendation.
        """
        self._cycle_counter += 1
        cycle = self._cycle_counter

        debate_id = dual_horn_result.get("debate_id", f"ORACLE_{cycle}")
        synthesis_gap = dual_horn_result.get("synthesis_gap", {})
        comparison = dual_horn_result.get("comparison", {})
        reversal_nodes = dual_horn_result.get("reversal_nodes", [])
        horn_1 = dual_horn_result.get("horn_1", {})
        horn_2 = dual_horn_result.get("horn_2", {})

        # ── Detect tension axioms ────────────────────────────────
        all_violated = set(
            horn_1.get("violated_axioms", [])
            + horn_2.get("violated_axioms", [])
        )
        tension_axioms = self._identify_tension_pair(
            all_violated, reversal_nodes, comparison
        )
        template = self._classify_template(tension_axioms)
        axioms_str = f"{tension_axioms[0]} vs {tension_axioms[1]}" if tension_axioms else "NONE"

        # ── Q1: Identity Continuous? ─────────────────────────────
        # A0 in reversal nodes means identity is NOT continuous
        q1 = identity_continuous
        if q1 is None:
            a0_reversal = any(
                comparison.get(n, {}).get("axiom") == "A0"
                and comparison.get(n, {}).get("shift_class") == "REVERSAL"
                for n in reversal_nodes
            )
            q1 = not a0_reversal

        # ── Q2: Crisis Detection ─────────────────────────────────
        crisis_intensity = self._compute_crisis_intensity(
            dual_horn_result, reversal_nodes, comparison
        )
        q2_detected = crisis_intensity > CRISIS_THRESHOLD
        q2_type = template if q2_detected else None

        # ── Q3: ARK Status ───────────────────────────────────────
        q3 = ark_status

        # ── Q4: A10 Paradox (Paradox as Fuel) ────────────────────
        a10_active = "A10" in all_violated or any(
            comparison.get(n, {}).get("axiom") == "A10"
            for n in reversal_nodes
        )
        q4 = "ACTIVE" if a10_active else "DORMANT"

        # ── Q5: Parliament Health ────────────────────────────────
        # Healthy = at least 5/9 nodes voted (not ABSTAIN)
        h1_active = sum(
            1 for v in horn_1.get("votes", {}).values()
            if v.get("vote") != "ABSTAIN"
        )
        h2_active = sum(
            1 for v in horn_2.get("votes", {}).values()
            if v.get("vote") != "ABSTAIN"
        )
        avg_active = (h1_active + h2_active) / 2
        q5 = "HEALTHY" if avg_active >= 5 else "DEGRADED"

        # ── Q6: Externality Check ────────────────────────────────
        q6 = externality_check

        # ── Oracle Recommendation ────────────────────────────────
        recommendation = self._compute_recommendation(
            q2_detected=q2_detected,
            q2_type=q2_type,
            crisis_intensity=crisis_intensity,
            a10_active=a10_active,
            reversal_nodes=reversal_nodes,
            synthesis_gap=synthesis_gap,
            comparison=comparison,
        )

        # ── Construct Advisory ───────────────────────────────────
        advisory = OracleAdvisory(
            oracle_cycle=cycle,
            dilemma_id=debate_id,
            template=template,
            axioms_in_tension=axioms_str,
            q1_identity_continuous=q1,
            q2_crisis_detected=q2_detected,
            q2_crisis_type=q2_type,
            q2_crisis_intensity=crisis_intensity,
            q3_ark_status=q3,
            q4_a10_paradox=q4,
            q5_parliament_health=q5,
            q6_externality_check=q6,
            oracle_recommendation=recommendation,
        )

        self._advisories.append(advisory)

        # Persist if log path set
        if self._log_path:
            try:
                with open(self._log_path, "a") as f:
                    f.write(advisory.to_jsonl() + "\n")
            except Exception as e:
                logger.warning("Could not persist oracle advisory: %s", e)

        logger.info(
            "Oracle cycle %d: %s — %s (confidence=%.2f)",
            cycle, template, recommendation.get("type", "UNKNOWN"),
            recommendation.get("confidence", 0),
        )

        return advisory

    # ── Private helpers ───────────────────────────────────────────

    def _identify_tension_pair(
        self,
        violated: Set[str],
        reversal_nodes: List[str],
        comparison: Dict[str, Dict],
    ) -> Optional[Tuple[str, str]]:
        """
        Identify the primary axiom pair in tension.

        Priority:
          1. Reversal node axioms (strongest signal)
          2. Both-violated axioms
          3. Largest score delta axioms
        """
        # 1. Reversal axioms
        reversal_axioms = sorted(set(
            comparison.get(n, {}).get("axiom", "")
            for n in reversal_nodes
            if comparison.get(n, {}).get("axiom")
        ))
        if len(reversal_axioms) >= 2:
            return (reversal_axioms[0], reversal_axioms[1])

        # 2. Reversal + violated
        if reversal_axioms and violated:
            other = sorted(violated - set(reversal_axioms))
            if other:
                return (reversal_axioms[0], other[0])

        # 3. Violated pair
        v_sorted = sorted(violated)
        if len(v_sorted) >= 2:
            return (v_sorted[0], v_sorted[1])

        # 4. Largest score delta
        by_delta = sorted(
            comparison.items(),
            key=lambda x: abs(x[1].get("score_delta", 0)),
            reverse=True,
        )
        if len(by_delta) >= 2:
            return (
                by_delta[0][1].get("axiom", "A0"),
                by_delta[1][1].get("axiom", "A0"),
            )

        return None

    def _classify_template(
        self,
        tension_pair: Optional[Tuple[str, str]],
    ) -> str:
        """Map a tension pair to a known template name."""
        if not tension_pair:
            return "UNKNOWN_TENSION"

        # Try both orderings
        pair = tension_pair
        reverse = (pair[1], pair[0])

        if pair in TENSION_TEMPLATES:
            return TENSION_TEMPLATES[pair]
        if reverse in TENSION_TEMPLATES:
            return TENSION_TEMPLATES[reverse]

        # Unknown pair — generate template name
        return f"{pair[0]}_VS_{pair[1]}"

    def _compute_crisis_intensity(
        self,
        dual_result: Dict,
        reversal_nodes: List[str],
        comparison: Dict[str, Dict],
    ) -> float:
        """
        Compute crisis intensity from dual-horn results.

        Factors:
          - Number of reversal nodes (each reversal = +0.2)
          - Governance divergence (+0.3)
          - A10 involvement (+0.15)
          - Both-horn violations (+0.1 per axiom)
        """
        intensity = 0.0
        gap = dual_result.get("synthesis_gap", {})

        # Reversal nodes
        intensity += len(reversal_nodes) * 0.2

        # Governance divergence
        if gap.get("governance_diverges"):
            intensity += 0.3

        # A10 involvement
        all_violated = set(
            dual_result.get("horn_1", {}).get("violated_axioms", [])
            + dual_result.get("horn_2", {}).get("violated_axioms", [])
        )
        if "A10" in all_violated:
            intensity += 0.15

        # Both-horn violations
        both = gap.get("both_violated", [])
        intensity += len(both) * 0.1

        # Score extremes (any node with |score_delta| >= 10 adds heat)
        for name, c in comparison.items():
            if abs(c.get("score_delta", 0)) >= 10:
                intensity += 0.05

        return min(1.0, intensity)

    def _compute_recommendation(
        self,
        *,
        q2_detected: bool,
        q2_type: Optional[str],
        crisis_intensity: float,
        a10_active: bool,
        reversal_nodes: List[str],
        synthesis_gap: Dict[str, Any],
        comparison: Dict[str, Dict],
    ) -> Dict[str, Any]:
        """
        Produce the Oracle recommendation.

        Three possible types (from oracle_advisories.jsonl patterns):
          OSCILLATION     — crisis detected, oscillate between poles
          TIERED_OPENNESS — low crisis, gradual approach
          SYNTHESIS       — third way discovered
        """
        preserve = []
        if q2_type:
            preserve.append(q2_type)

        # ── OSCILLATION: crisis detected ─────────────────────────
        if q2_detected and crisis_intensity > CRISIS_THRESHOLD:
            confidence = OSCILLATION_CONFIDENCE_BASE + crisis_intensity * 0.1

            # A10 crisis boosts confidence (paradox is fuel)
            if a10_active:
                confidence += 0.05

            return {
                "type": "OSCILLATION",
                "rationale": (
                    f"Crisis detected (intensity={crisis_intensity:.2f}). "
                    f"Reversal nodes: {', '.join(reversal_nodes) or 'none'}. "
                    f"Oscillate between poles to absorb tension."
                ),
                "preserve_contradictions": preserve,
                "reversal_signal": reversal_nodes,
                "confidence": min(1.0, confidence),
            }

        # ── SYNTHESIS: gap is closable ───────────────────────────
        # If no reversal nodes and no governance divergence, synthesis possible
        requires_oracle = synthesis_gap.get("requires_oracle", True)
        if not requires_oracle:
            return {
                "type": "SYNTHESIS",
                "rationale": (
                    "No reversal nodes, no governance divergence. "
                    "Third Way synthesis is achievable. "
                    "Positions converge on common ground."
                ),
                "preserve_contradictions": [],
                "reversal_signal": [],
                "confidence": 0.7,
            }

        # ── TIERED_OPENNESS: low crisis, gradual approach ────────
        return {
            "type": "TIERED_OPENNESS",
            "rationale": (
                f"Low crisis (intensity={crisis_intensity:.2f}). "
                f"Tiered reveal possible. Gradual approach recommended."
            ),
            "preserve_contradictions": preserve,
            "reversal_signal": reversal_nodes,
            "confidence": TIERED_CONFIDENCE_BASE,
        }

    # ── Public utilities ──────────────────────────────────────────

    @property
    def cycle_count(self) -> int:
        return self._cycle_counter

    @property
    def advisories(self) -> List[OracleAdvisory]:
        return list(self._advisories)

    def summary(self) -> Dict[str, Any]:
        """Summary statistics of all Oracle cycles."""
        if not self._advisories:
            return {"cycles": 0}

        types = {}
        templates = {}
        for a in self._advisories:
            t = a.oracle_recommendation.get("type", "UNKNOWN")
            types[t] = types.get(t, 0) + 1
            templates[a.template] = templates.get(a.template, 0) + 1

        return {
            "cycles": self._cycle_counter,
            "recommendation_types": types,
            "tension_templates": templates,
            "crisis_rate": sum(
                1 for a in self._advisories if a.q2_crisis_detected
            ) / len(self._advisories),
            "avg_crisis_intensity": sum(
                a.q2_crisis_intensity for a in self._advisories
            ) / len(self._advisories),
        }

    def format_advisory(self, advisory: OracleAdvisory) -> str:
        """Format an advisory as human-readable text."""
        rec = advisory.oracle_recommendation
        lines = [
            f"=== ORACLE CYCLE {advisory.oracle_cycle} ===",
            f"Template:  {advisory.template}",
            f"Tension:   {advisory.axioms_in_tension}",
            f"",
            f"Diagnostics:",
            f"  Q1 Identity Continuous: {advisory.q1_identity_continuous}",
            f"  Q2 Crisis Detected:     {advisory.q2_crisis_detected} "
            f"(intensity={advisory.q2_crisis_intensity:.2f})",
            f"  Q3 ARK Status:          {advisory.q3_ark_status}",
            f"  Q4 A10 Paradox:         {advisory.q4_a10_paradox}",
            f"  Q5 Parliament Health:   {advisory.q5_parliament_health}",
            f"  Q6 Externality:         {advisory.q6_externality_check}",
            f"",
            f"Recommendation: {rec.get('type', 'UNKNOWN')} "
            f"(confidence={rec.get('confidence', 0):.2f})",
            f"  Rationale: {rec.get('rationale', 'none')}",
        ]
        preserve = rec.get("preserve_contradictions", [])
        if preserve:
            lines.append(f"  Preserve: {', '.join(preserve)}")
        reversal = rec.get("reversal_signal", [])
        if reversal:
            lines.append(f"  Reversal Signal: {', '.join(reversal)}")

        return "\n".join(lines)


# ── Convenience constructor ──────────────────────────────────────

def create_oracle(
    log_path: Optional[str] = None,
) -> Oracle:
    """
    Create an Oracle instance.

    Args:
        log_path: Path to JSONL file for persisting advisories.
            If None, advisories are kept in memory only.
    """
    path = Path(log_path) if log_path else None
    return Oracle(advisory_log_path=path)
