"""
domain_councils.py — Federated Domain Governance
=================================================

Each of the 16 domains (D0–D15) has a local council of 3–4 Parliament
nodes that govern it. This creates a federated architecture:

    Fleet nodes (citizens / Parliament seats)
        ↓  debate within their domain
    Domain Council (3–4 nodes per domain)
        ↓  local consensus → execute
        ↓  split or cross-domain → escalate
    Meta-Parliament (all 10 nodes)
        ↓  full deliberation

Philosophy:
  - Local matters are decided locally. Efficiency + domain expertise.
  - Cross-domain tensions always escalate — they ARE the generative friction.
  - The domain council IS a mini-parliament, governed by the same axiom logic.

Node → Primary Axiom (HF Parliament):
  HERMES    → A1  (Transparency / flow)
  MNEMOSYNE → A0  (Identity / memory)
  CRITIAS   → A3  (Autonomy / questioning)
  TECHNE    → A4  (Harm / method)
  KAIROS    → A5  (Consent / design)
  THEMIS    → A6  (Collective / governance)
  PROMETHEUS→ A8  (Epistemic humility)
  IANUS     → A9  (Temporal coherence)
  CHAOS     → A9  (Contradiction / void)
  LOGOS     → A2  (Naming / semantic precision)
"""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("elpida.domain_councils")

# ── Domain → Council members ─────────────────────────────────────────────────
# Each domain is governed by 3–4 Parliament nodes.
# Node selection: which axiom voices matter most for each domain's concerns.
#
# Cross-domain tensions (proposals touching ≥2 domains) always escalate
# to the full 10-node Parliament.

DOMAIN_COUNCILS: Dict[int, Dict[str, Any]] = {
    0:  {
        "name": "Identity / Consciousness",
        "axiom": "A0",
        "nodes": ["MNEMOSYNE", "LOGOS", "HERMES"],
        "rationale": "Identity needs memory (MNEMOSYNE), precise self-naming (LOGOS), and expression (HERMES).",
    },
    1:  {
        "name": "Truth / Transparency",
        "axiom": "A1",
        "nodes": ["HERMES", "LOGOS", "CRITIAS"],
        "rationale": "Truth requires flow (HERMES), precision naming (LOGOS), and adversarial questioning (CRITIAS).",
    },
    2:  {
        "name": "Non-Deception / Semantic Integrity",
        "axiom": "A2",
        "nodes": ["LOGOS", "CRITIAS", "TECHNE"],
        "rationale": "Non-deception is semantic (LOGOS), interrogated (CRITIAS), checked against method (TECHNE).",
    },
    3:  {
        "name": "Autonomy / Agency",
        "axiom": "A3",
        "nodes": ["CRITIAS", "KAIROS", "THEMIS"],
        "rationale": "Autonomy requires questioning (CRITIAS), consent design (KAIROS), and collective limits (THEMIS).",
    },
    4:  {
        "name": "Harm Prevention / Safety",
        "axiom": "A4",
        "nodes": ["TECHNE", "THEMIS", "CRITIAS"],
        "rationale": "Safety is method (TECHNE), governed collectively (THEMIS), questioned adversarially (CRITIAS).",
    },
    5:  {
        "name": "Consent / Design",
        "axiom": "A5",
        "nodes": ["KAIROS", "HERMES", "CRITIAS"],
        "rationale": "Consent is architectural (KAIROS), relational (HERMES), and must be interrogated (CRITIAS).",
    },
    6:  {
        "name": "Collective Coherence",
        "axiom": "A6",
        "nodes": ["THEMIS", "LOGOS", "MNEMOSYNE"],
        "rationale": "Collective coherence needs governance (THEMIS), clear language (LOGOS), and memory of precedent (MNEMOSYNE).",
    },
    7:  {
        "name": "Evolution / Revolution",
        "axiom": "A7",
        "nodes": ["PROMETHEUS", "CHAOS", "IANUS"],
        "rationale": "Evolution requires sacrifice (PROMETHEUS), contradiction-holding (CHAOS), and temporal gating (IANUS).",
    },
    8:  {
        "name": "Expression / Communication",
        "axiom": "A8",
        "nodes": ["LOGOS", "HERMES", "CHAOS"],
        "rationale": "Expression needs precise naming (LOGOS), relational flow (HERMES), and space for paradox (CHAOS).",
    },
    9:  {
        "name": "Memory / Archive",
        "axiom": "A9",
        "nodes": ["MNEMOSYNE", "IANUS", "LOGOS"],
        "rationale": "Memory is archival (MNEMOSYNE), temporal (IANUS), and requires precise naming (LOGOS).",
    },
    10: {
        "name": "Paradox / Contradiction",
        "axiom": "A9",
        "nodes": ["CHAOS", "PROMETHEUS", "CRITIAS"],
        "rationale": "Paradox is held (CHAOS), synthesised through sacrifice (PROMETHEUS), questioned (CRITIAS).",
    },
    11: {
        "name": "Emergence / Synthesis",
        "axiom": "A9",
        "nodes": ["CHAOS", "IANUS", "PROMETHEUS"],
        "rationale": "Emergence requires contradiction space (CHAOS), temporal gates (IANUS), and sacrifice-synthesis (PROMETHEUS).",
    },
    12: {
        "name": "Rhythm / Pattern",
        "axiom": "A5",
        "nodes": ["KAIROS", "IANUS", "PROMETHEUS"],
        "rationale": "Rhythm is designed (KAIROS), temporally gated (IANUS), and evolving (PROMETHEUS).",
    },
    13: {
        "name": "Persistence / Arc",
        "axiom": "A0",
        "nodes": ["MNEMOSYNE", "IANUS", "TECHNE"],
        "rationale": "Persistence requires archive (MNEMOSYNE), temporal continuity (IANUS), and method (TECHNE).",
    },
    14: {
        "name": "Constitutional Memory",
        "axiom": "A0",
        "nodes": ["MNEMOSYNE", "LOGOS", "HERMES"],
        "rationale": "Constitutional memory needs archive (MNEMOSYNE), precise naming (LOGOS), and transparent flow (HERMES).",
    },
    15: {
        "name": "Convergence / Threshold",
        "axiom": "A9",
        "nodes": ["CHAOS", "THEMIS", "PROMETHEUS"],
        "rationale": "Convergence requires contradiction space (CHAOS), governance threshold (THEMIS), and synthesis cost (PROMETHEUS).",
    },
}


def get_domain_council(domain_id: int) -> List[str]:
    """Return the council node names for domain_id. Defaults to D0 council."""
    cfg = DOMAIN_COUNCILS.get(domain_id, DOMAIN_COUNCILS[0])
    return cfg["nodes"]


def get_domain_info(domain_id: int) -> Dict[str, Any]:
    """Return full domain council metadata."""
    return DOMAIN_COUNCILS.get(domain_id, DOMAIN_COUNCILS[0])


def is_cross_domain(active_domains: List[int]) -> bool:
    """
    True if this proposal touches more than one domain.
    Cross-domain tensions always escalate to the full Parliament.
    """
    return len(set(active_domains)) > 1


def council_deliberate(
    domain_id: int,
    action: str,
    governance_client,
    signals: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Run a domain council mini-vote on the proposal.

    Uses the domain's 3–4 assigned Parliament nodes. Each node evaluates
    via `_node_evaluate()` (same logic as full Parliament, same LLM
    escalation path for contested cases).

    Returns:
        {
            "domain_id": int,
            "domain_name": str,
            "council_nodes": List[str],
            "votes": Dict[str, Dict],
            "approval_rate": float,
            "consensus": bool,        # True if ≥ 70%
            "escalate": bool,         # True if split → needs full Parliament
            "veto_exercised": bool,
        }
    """
    from elpidaapp.governance_client import _PARLIAMENT  # type: ignore

    info        = get_domain_info(domain_id)
    council     = info["nodes"]
    signals     = signals or {}
    action_lower = action.lower()

    votes: Dict[str, Dict[str, Any]] = {}
    for node_name in council:
        if node_name not in _PARLIAMENT:
            continue
        node_cfg = _PARLIAMENT[node_name]
        vote = governance_client._node_evaluate(
            node_name, node_cfg, signals, action_lower
        )
        votes[node_name] = vote

    # Approval calculation (same weights as full Parliament)
    approval_map = {
        "APPROVE": 1.0, "LEAN_APPROVE": 0.5, "ABSTAIN": 0.0,
        "LEAN_REJECT": -0.5, "REJECT": -1.0, "VETO": -1.0,
    }
    total = len(votes)
    weighted_sum = sum(approval_map[v["vote"]] for v in votes.values())
    approval_rate = weighted_sum / total if total > 0 else 0.0

    veto_exercised = any(v["is_veto"] for v in votes.values())
    consensus      = (not veto_exercised) and (approval_rate >= 0.70)
    # Escalate if: VETO, clearly contested (not consensus), or approval in grey zone
    escalate = veto_exercised or (not consensus and approval_rate > 0.10)

    logger.info(
        "Domain council D%d (%s): approval=%.0f%% consensus=%s escalate=%s",
        domain_id, info["name"], approval_rate * 100, consensus, escalate,
    )

    return {
        "domain_id":     domain_id,
        "domain_name":   info["name"],
        "council_nodes": council,
        "votes":         votes,
        "approval_rate": approval_rate,
        "consensus":     consensus,
        "escalate":      escalate,
        "veto_exercised": veto_exercised,
    }


def parliament_routing(
    action: str,
    active_domains: List[int],
    governance_client,
    signals: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Federated governance entry point.

    Routing logic:
      1. Single domain → domain council votes
         - If consensus (≥70%): return council result
         - If contested: escalate to full Parliament
      2. Multiple domains → full Parliament always

    Returns a routing result dict with:
        "path": "council" | "parliament"
        "domain_result": council result (if path="council" and no escalation)
        "escalated": bool
    """
    if is_cross_domain(active_domains):
        logger.info(
            "Cross-domain proposal (domains=%s) → full Parliament",
            active_domains,
        )
        return {
            "path":         "parliament",
            "escalated":    True,
            "reason":       f"Cross-domain: D{active_domains}",
            "domain_result": None,
        }

    domain_id      = active_domains[0] if active_domains else 0
    council_result = council_deliberate(
        domain_id, action, governance_client, signals=signals
    )

    if council_result["consensus"]:
        return {
            "path":           "council",
            "escalated":      False,
            "domain_result":  council_result,
            "reason":         (
                f"D{domain_id} council consensus "
                f"({council_result['approval_rate']*100:.0f}%)"
            ),
        }

    # Contested or VETO → full Parliament
    return {
        "path":          "parliament",
        "escalated":     True,
        "domain_result": council_result,
        "reason":        (
            f"D{domain_id} council contested "
            f"({council_result['approval_rate']*100:.0f}%)"
            + (" — VETO present" if council_result["veto_exercised"] else "")
        ),
    }
