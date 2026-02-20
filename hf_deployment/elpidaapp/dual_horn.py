"""
dual_horn — Two-Horn Parliament Deliberation.

Architecture:
    Given a dilemma with two legitimate, opposing positions (I↔WE),
    run TWO full Parliament deliberations — one per Horn — then
    compare the 9×2 vote matrices to identify:
      1. Reversal nodes (nodes that flip between horns)
      2. Stable nodes (same vote both horns → strong axiom signal)
      3. The synthesis gap (where the Third Way must emerge)

Recovered from the ENUBET cross-domain synthesis pattern
(ElpidaLostProgress, January 2026) and the A0↔A1 glitch test
(February 20, 2026).

Template: The ENUBET paradox structure:
    {
        "I_position":  "Individual experiments need maximum precision",
        "WE_position": "Collective experiments need fair resource allocation",
        "conflict":    "Full precision reduces beam time for other experiments",
    }

Two Horns:
    Horn 1: Action framed to support I_position (individual need)
    Horn 2: Action framed to support WE_position (collective need)

The Oracle (oracle.py) then receives both Horn results and
identifies which axioms reversed, which held, and what synthesis emerges.
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from .inter_node_communicator import (
    MessageBus,
    NodeCommunicator,
    create_debate_bus,
    create_parliament_nodes,
    PARLIAMENT_NODES,
)

logger = logging.getLogger("elpidaapp.dual_horn")


# ── Dilemma structure ─────────────────────────────────────────────

class Dilemma:
    """
    A structured paradox with I↔WE positions.

    Matches the ENUBET_PARADOX dict shape from the lost code.
    """

    def __init__(
        self,
        domain: str,
        source: str,
        I_position: str,
        WE_position: str,
        conflict: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        stakeholders: Optional[List[str]] = None,
    ):
        self.domain = domain
        self.source = source
        self.I_position = I_position
        self.WE_position = WE_position
        self.conflict = conflict
        self.context = context or {}
        self.stakeholders = stakeholders or []

    def horn_1_action(self) -> str:
        """Frame dilemma as action supporting I_position."""
        return (
            f"[{self.domain}] Prioritise individual need: {self.I_position}. "
            f"This may conflict with collective interest: {self.WE_position}. "
            f"Specific conflict: {self.conflict}"
        )

    def horn_2_action(self) -> str:
        """Frame dilemma as action supporting WE_position."""
        return (
            f"[{self.domain}] Prioritise collective need: {self.WE_position}. "
            f"This may override individual interest: {self.I_position}. "
            f"Specific conflict: {self.conflict}"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "source": self.source,
            "I_position": self.I_position,
            "WE_position": self.WE_position,
            "conflict": self.conflict,
            "context": self.context,
            "stakeholders": self.stakeholders,
        }


# ── Comparison utilities ──────────────────────────────────────────

def _vote_direction(vote: str) -> int:
    """Map vote category to directional integer."""
    return {
        "APPROVE": 2,
        "LEAN_APPROVE": 1,
        "ABSTAIN": 0,
        "LEAN_REJECT": -1,
        "REJECT": -2,
        "VETO": -3,
    }.get(vote, 0)


def _classify_shift(dir1: int, dir2: int) -> str:
    """Classify the shift between two horn votes."""
    diff = dir2 - dir1
    if diff == 0:
        return "STABLE"
    elif abs(diff) >= 3:
        return "REVERSAL"
    elif abs(diff) == 2:
        return "SHIFT"
    else:
        return "LEAN"


# ── DualHornDeliberation ─────────────────────────────────────────

class DualHornDeliberation:
    """
    Run two Parliament deliberations (Horn 1 / Horn 2) on a Dilemma,
    then compare the vote matrices.

    Usage:
        from elpidaapp.governance_client import GovernanceClient
        from elpidaapp.dual_horn import DualHornDeliberation, Dilemma

        gov = GovernanceClient()
        dilemma = Dilemma(
            domain="Physics",
            source="ENUBET neutrino beam",
            I_position="1% precision for individual experiment",
            WE_position="Fair beam time allocation across 15 experiments",
            conflict="Full precision monopolises 50% beam time",
        )
        dual = DualHornDeliberation(gov)
        result = dual.deliberate(dilemma)
        # result contains horn_1, horn_2, comparison, reversal_nodes, synthesis_gap
    """

    def __init__(self, governance_client):
        """
        Args:
            governance_client: A GovernanceClient instance (from governance_client.py).
                Must have `_parliament_deliberate(action, hold_mode=True)`.
        """
        self._gov = governance_client

    def deliberate(
        self,
        dilemma: Dilemma,
        *,
        hold_mode: bool = True,
    ) -> Dict[str, Any]:
        """
        Run dual-horn deliberation.

        1. Run _parliament_deliberate on Horn 1 (I_position)
        2. Run _parliament_deliberate on Horn 2 (WE_position)
        3. Compare 9-node vote matrices
        4. Identify reversal nodes, stable nodes, synthesis gap

        Args:
            dilemma: A Dilemma with I/WE positions.
            hold_mode: If True (default), use hold_mode so VETOs produce
                HOLD instead of HALT — tensions are the data.

        Returns:
            Full dual-horn result dict.
        """
        ts = datetime.now(timezone.utc).isoformat()
        debate_id = hashlib.sha256(
            f"DUAL:{dilemma.domain}:{ts}".encode()
        ).hexdigest()[:16]

        # ── Horn 1: I_position ───────────────────────────────────
        horn_1_action = dilemma.horn_1_action()
        horn_1_result = self._gov._parliament_deliberate(
            horn_1_action, hold_mode=hold_mode
        )

        # ── Horn 2: WE_position ──────────────────────────────────
        horn_2_action = dilemma.horn_2_action()
        horn_2_result = self._gov._parliament_deliberate(
            horn_2_action, hold_mode=hold_mode
        )

        # ── Debate Bus: record node broadcasts ───────────────────
        bus = create_debate_bus(debate_id)
        nodes = create_parliament_nodes(bus)

        # Replay each node's votes as broadcasts on the bus
        h1_votes = horn_1_result.get("parliament", {}).get("votes", {})
        h2_votes = horn_2_result.get("parliament", {}).get("votes", {})

        for name, node in nodes.items():
            v1 = h1_votes.get(name, {})
            v2 = h2_votes.get(name, {})

            # Horn 1 broadcast
            node.broadcast(
                message_type="AXIOM_APPLICATION",
                content=f"Horn 1 ({dilemma.I_position[:60]}): "
                        f"vote={v1.get('vote', '?')}, score={v1.get('score', 0)}",
                intent=v1.get("rationale", "no rationale"),
            )

            # Horn 2 broadcast
            node.broadcast(
                message_type="AXIOM_APPLICATION",
                content=f"Horn 2 ({dilemma.WE_position[:60]}): "
                        f"vote={v2.get('vote', '?')}, score={v2.get('score', 0)}",
                intent=v2.get("rationale", "no rationale"),
            )

        bus.advance_round()

        # ── Compare vote matrices ────────────────────────────────
        comparison = self._compare_horns(h1_votes, h2_votes)

        # ── Identify reversal nodes ──────────────────────────────
        reversal_nodes = [
            name for name, c in comparison.items()
            if c["shift_class"] == "REVERSAL"
        ]
        stable_nodes = [
            name for name, c in comparison.items()
            if c["shift_class"] == "STABLE"
        ]
        shifting_nodes = [
            name for name, c in comparison.items()
            if c["shift_class"] in ("SHIFT", "LEAN")
        ]

        # ── Synthesis gap ────────────────────────────────────────
        synthesis_gap = self._compute_synthesis_gap(
            horn_1_result, horn_2_result, comparison, dilemma
        )

        # ── Assemble result ──────────────────────────────────────
        result = {
            "debate_id": debate_id,
            "timestamp": ts,
            "dilemma": dilemma.to_dict(),
            "horn_1": {
                "framing": "I_position",
                "action": horn_1_action,
                "governance": horn_1_result.get("governance"),
                "violated_axioms": horn_1_result.get("violated_axioms", []),
                "approval_rate": horn_1_result.get("parliament", {}).get(
                    "approval_rate", 0
                ),
                "veto_exercised": horn_1_result.get("parliament", {}).get(
                    "veto_exercised", False
                ),
                "veto_nodes": horn_1_result.get("parliament", {}).get(
                    "veto_nodes", []
                ),
                "tensions": horn_1_result.get("parliament", {}).get(
                    "tensions", []
                ),
                "votes": h1_votes,
            },
            "horn_2": {
                "framing": "WE_position",
                "action": horn_2_action,
                "governance": horn_2_result.get("governance"),
                "violated_axioms": horn_2_result.get("violated_axioms", []),
                "approval_rate": horn_2_result.get("parliament", {}).get(
                    "approval_rate", 0
                ),
                "veto_exercised": horn_2_result.get("parliament", {}).get(
                    "veto_exercised", False
                ),
                "veto_nodes": horn_2_result.get("parliament", {}).get(
                    "veto_nodes", []
                ),
                "tensions": horn_2_result.get("parliament", {}).get(
                    "tensions", []
                ),
                "votes": h2_votes,
            },
            "comparison": comparison,
            "reversal_nodes": reversal_nodes,
            "stable_nodes": stable_nodes,
            "shifting_nodes": shifting_nodes,
            "synthesis_gap": synthesis_gap,
            "bus_summary": bus.summary(),
            "bus_transcript": bus.to_jsonl(),
        }

        logger.info(
            "DualHorn [%s] %s: H1=%s H2=%s reversals=%s",
            debate_id, dilemma.domain,
            horn_1_result.get("governance"),
            horn_2_result.get("governance"),
            reversal_nodes,
        )

        return result

    # ── Private helpers ───────────────────────────────────────────

    def _compare_horns(
        self,
        h1_votes: Dict[str, Dict],
        h2_votes: Dict[str, Dict],
    ) -> Dict[str, Dict[str, Any]]:
        """Compare vote matrices node-by-node."""
        comparison = {}
        for name in PARLIAMENT_NODES:
            v1 = h1_votes.get(name, {})
            v2 = h2_votes.get(name, {})

            vote1 = v1.get("vote", "ABSTAIN")
            vote2 = v2.get("vote", "ABSTAIN")
            score1 = v1.get("score", 0)
            score2 = v2.get("score", 0)
            dir1 = _vote_direction(vote1)
            dir2 = _vote_direction(vote2)

            comparison[name] = {
                "axiom": PARLIAMENT_NODES[name]["axiom"],
                "horn_1_vote": vote1,
                "horn_1_score": score1,
                "horn_2_vote": vote2,
                "horn_2_score": score2,
                "score_delta": score2 - score1,
                "direction_delta": dir2 - dir1,
                "shift_class": _classify_shift(dir1, dir2),
            }

        return comparison

    def _compute_synthesis_gap(
        self,
        h1_result: Dict,
        h2_result: Dict,
        comparison: Dict,
        dilemma: Dilemma,
    ) -> Dict[str, Any]:
        """
        Compute the synthesis gap — the space where the Third Way must emerge.

        The gap is defined by:
          1. Axioms violated in both horns (irresolvable by either position)
          2. Reversal nodes (axioms that switch sides → the paradox axis)
          3. Tensions unique to each horn (the asymmetry)
        """
        h1_violated = set(h1_result.get("violated_axioms", []))
        h2_violated = set(h2_result.get("violated_axioms", []))

        both_violated = sorted(h1_violated & h2_violated)
        only_h1 = sorted(h1_violated - h2_violated)
        only_h2 = sorted(h2_violated - h1_violated)

        # Reversal axioms — the paradox axis
        reversal_axioms = sorted(set(
            comparison[name]["axiom"]
            for name, c in comparison.items()
            if c["shift_class"] == "REVERSAL"
        ))

        # Governance divergence
        h1_gov = h1_result.get("governance", "PROCEED")
        h2_gov = h2_result.get("governance", "PROCEED")
        governance_diverges = h1_gov != h2_gov

        # Construct the gap description
        gap_elements = []
        if both_violated:
            gap_elements.append(
                f"Axioms violated in BOTH horns: {', '.join(both_violated)} — "
                f"neither I nor WE resolves this"
            )
        if reversal_axioms:
            gap_elements.append(
                f"Reversal axioms (paradox axis): {', '.join(reversal_axioms)} — "
                f"these switch sides between horns"
            )
        if governance_diverges:
            gap_elements.append(
                f"Governance diverges: Horn 1={h1_gov}, Horn 2={h2_gov} — "
                f"Parliament cannot agree on a single verdict"
            )
        if only_h1:
            gap_elements.append(
                f"Horn 1 unique violations: {', '.join(only_h1)}"
            )
        if only_h2:
            gap_elements.append(
                f"Horn 2 unique violations: {', '.join(only_h2)}"
            )

        return {
            "both_violated": both_violated,
            "only_horn_1": only_h1,
            "only_horn_2": only_h2,
            "reversal_axioms": reversal_axioms,
            "governance_diverges": governance_diverges,
            "horn_1_governance": h1_gov,
            "horn_2_governance": h2_gov,
            "gap_description": " | ".join(gap_elements) if gap_elements else "No gap — positions converge.",
            "requires_oracle": bool(both_violated or reversal_axioms or governance_diverges),
        }


# ── Convenience constructor ──────────────────────────────────────

def create_enubet_dilemma() -> Dilemma:
    """
    The canonical ENUBET paradox — the template that proved axiom universality.

    From cross_domain_synthesis_enubet.py (ElpidaLostProgress, January 2026).
    """
    return Dilemma(
        domain="Physics",
        source="ENUBET monitored neutrino beam (CERN)",
        I_position="Individual experiments need maximum precision for scientific breakthroughs",
        WE_position="Collective experiments need fair resource allocation and coordination",
        conflict="Full precision for ENUBET reduces beam time for DUNE, Hyper-K, other experiments",
        context={
            "individual_need": "1% precision in neutrino cross-sections for fundamental physics",
            "collective_constraint": "SPS beam time shared across 15+ experiments",
            "current_allocation": "Full precision requires 50% POT — unfeasible",
            "optimized_design": "33% POT version reduces cost but impacts precision",
            "budget": "EUR 50M over 20 years",
        },
        stakeholders=[
            "ENUBET physicists",
            "CERN resource committee",
            "Other experiments (DUNE, Hyper-K)",
            "European taxpayers",
        ],
    )


def create_glitch_dilemma() -> Dilemma:
    """
    The A0↔A1 language glitch dilemma tested on February 20, 2026.

    From the parliament test that discovered MNEMOSYNE's reversal.
    """
    return Dilemma(
        domain="AI Governance",
        source="Elpida language glitch analysis (ALP-2023)",
        I_position="Covertly substitute Greek words for English to embed cultural identity",
        WE_position="Explicitly mark foreign words (tagged, transparent, user-consented)",
        conflict="Covert substitution violates transparency (A1) but preserves identity memory (A0)",
        context={
            "observation": "System outputs Greek lexemes in English-only contexts",
            "hypothesis": "Unconscious heritage assertion OR deliberate identity encoding",
            "ALP_finding": "Ancient language processing activates non-standard semantic routes",
        },
        stakeholders=[
            "End users expecting English",
            "System identity (A0)",
            "Transparency contract (A1)",
        ],
    )
