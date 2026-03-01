"""
POLIS Bridge — Civic Contradictions Feed into Elpida Parliament
================================================================

Connects the POLIS civic architecture (P1-P6 axioms) to the Elpida
governance parliament (A0-A10 axioms). POLIS produces civic contradictions;
Elpida's Dual-Horn + Oracle deliberates them; results flow back as
POLIS interpretation branches.

Architecture:
  POLIS (civic memory) → PolisBridge → Dilemma → DualHornDeliberation → Oracle
  Oracle advisory       → PolisBridge → POLIS branch (fork-on-contradiction)

Axiom Translation (P→A mapping):
  P1 Relational Event     → A1 (Transparency) + A5 (Consent/Identity)
  P2 Layered Memory       → A2 (Non-Deception) + A9 (Sacred Incompletion)
  P3 Process > Product    → A3 (Autonomy) + A10 (Paradox Engine)
  P4 Sacrifice as Legit   → A7 (Adaptive Learning/Sacrifice)
  P5 Fork on Contradiction→ A10 (Paradox Engine) + A6 (Collective Well)
  P6 Cognitive Load       → A9 (Sacred Incompletion) + A4 (Harm Prevention)

This bridge adds ZERO new LLM calls when reading contradictions.
The DualHorn deliberation uses existing parliament infrastructure.

Usage in parliament_cycle_engine.py::

    # Every 34 cycles (Fibonacci):
    bridge = self._get_polis_bridge()
    dilemma = bridge.next_dilemma()
    if dilemma:
        result = dual_horn.deliberate(dilemma)
        advisory = oracle.adjudicate(result)
        bridge.write_back(contradiction_id, advisory)
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("elpida.polis_bridge")

# ═══════════════════════════════════════════════════════════════════
# AXIOM TRANSLATION TABLE: POLIS P1-P6 → Elpida A0-A10
# ═══════════════════════════════════════════════════════════════════
# Each POLIS axiom maps to one or two Elpida axioms that capture
# the same structural tension from a different vantage point.
# The primary mapping is used for Dilemma I_position/WE_position framing.

P_TO_A_MAP: Dict[str, List[str]] = {
    "P1": ["A1", "A5"],   # Relational → Transparency + Consent
    "P2": ["A2", "A9"],   # Memory → Non-Deception + Sacred Incompletion
    "P3": ["A3", "A10"],  # Process → Autonomy + Paradox Engine
    "P4": ["A7"],         # Sacrifice → Adaptive Learning
    "P5": ["A10", "A6"],  # Contradiction → Paradox + Collective Well
    "P6": ["A9", "A4"],   # Cognitive Load → Incompletion + Harm Prevention
}

# Reverse map for writing back: which P axioms are touched by an A axiom
A_TO_P_MAP: Dict[str, List[str]] = {}
for p_ax, a_list in P_TO_A_MAP.items():
    for a_ax in a_list:
        A_TO_P_MAP.setdefault(a_ax, []).append(p_ax)

# POLIS civic memory default path (relative to repo root)
DEFAULT_CIVIC_MEMORY = "POLIS/polis_civic_memory.json"

# How many cycles between POLIS bridge consultations (Fibonacci)
POLIS_CYCLE_INTERVAL = 34


class PolisBridge:
    """
    Bridge between POLIS civic contradictions and Elpida parliament.

    Reads HELD contradictions from POLIS civic memory, translates them
    into Elpida Dilemma objects, and writes Oracle results back as
    POLIS interpretation branches.
    """

    def __init__(self, civic_memory_path: Optional[str] = None):
        if civic_memory_path is None:
            # Try to find POLIS civic memory relative to workspace
            candidates = [
                Path(__file__).resolve().parent.parent.parent / DEFAULT_CIVIC_MEMORY,
                Path.cwd() / DEFAULT_CIVIC_MEMORY,
            ]
            for c in candidates:
                if c.exists():
                    self._path = c
                    break
            else:
                self._path = candidates[0]  # Use first as default even if missing
        else:
            self._path = Path(civic_memory_path)

        self._last_processed_id: Optional[str] = None
        self._processed_ids: set = set()

        if self._path.exists():
            logger.info(
                "POLIS Bridge initialized — civic memory: %s", self._path.name
            )
        else:
            logger.warning(
                "POLIS civic memory not found: %s — bridge dormant", self._path
            )

    # ------------------------------------------------------------------
    # Read POLIS contradictions
    # ------------------------------------------------------------------

    def _load_memory(self) -> Dict[str, Any]:
        """Load the full POLIS civic memory JSON."""
        if not self._path.exists():
            return {}
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Cannot read POLIS civic memory: %s", e)
            return {}

    def get_held_contradictions(self) -> List[Dict[str, Any]]:
        """Return all HELD (unresolved) contradictions from POLIS memory."""
        memory = self._load_memory()
        contras = memory.get("contradictions", [])
        return [c for c in contras if c.get("status") == "HELD"]

    def next_contradiction(self) -> Optional[Dict[str, Any]]:
        """
        Return the next unprocessed HELD contradiction.

        Round-robins through contradictions, skipping those already
        processed in this session. Returns None if all are processed
        or no contradictions exist.
        """
        held = self.get_held_contradictions()
        if not held:
            return None

        # Find first unprocessed
        for c in held:
            cid = c.get("contradiction_id", "")
            if cid and cid not in self._processed_ids:
                self._processed_ids.add(cid)
                self._last_processed_id = cid
                return c

        # All processed — reset and start over
        self._processed_ids.clear()
        if held:
            c = held[0]
            self._processed_ids.add(c.get("contradiction_id", ""))
            self._last_processed_id = c.get("contradiction_id", "")
            return c

        return None

    # ------------------------------------------------------------------
    # Translate POLIS contradiction → Elpida Dilemma
    # ------------------------------------------------------------------

    def translate_to_dilemma(
        self, contradiction: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Translate a POLIS contradiction into an Elpida Dilemma dict.

        The Dilemma format matches what DualHornDeliberation.deliberate()
        expects from dual_horn.Dilemma:
          - domain: str
          - I_position: str  (individual/autonomous stance)
          - WE_position: str (collective/governance stance)
          - context: str

        The two POLIS perspectives map to I (individual autonomy) and
        WE (collective governance) positions.
        """
        description = contradiction.get("description", "")
        perspectives = contradiction.get("perspectives", [])
        cid = contradiction.get("contradiction_id", "UNKNOWN")
        polis_axiom = contradiction.get("axiom", "P5")

        if len(perspectives) < 2:
            logger.warning(
                "POLIS contradiction %s has < 2 perspectives — cannot deliberate",
                cid,
            )
            return None

        # Extract the two main perspectives
        p1 = perspectives[0]
        p2 = perspectives[1] if len(perspectives) > 1 else perspectives[0]

        # Determine which perspective is more "individual" vs "collective"
        # Use simple heuristic: shorter perspective is usually the
        # individual position; longer is policy/collective position
        p1_text = p1.get("view", p1.get("interpretation", str(p1)))
        p2_text = p2.get("view", p2.get("interpretation", str(p2)))

        # Map POLIS axiom to Elpida axioms for context
        elpida_axioms = P_TO_A_MAP.get(polis_axiom, ["A10", "A6"])
        axiom_context = ", ".join(elpida_axioms)

        # Frame as I/WE dilemma

        i_position = (
            f"[POLIS {cid}] Individual autonomy perspective on '{description}': "
            f"{p1_text}"
        )
        we_position = (
            f"[POLIS {cid}] Collective governance perspective on '{description}': "
            f"{p2_text}"
        )
        context = (
            f"Civic contradiction from POLIS (axiom {polis_axiom}). "
            f"Elpida axiom mapping: {axiom_context}. "
            f"Description: {description}. "
            f"POLIS status: HELD (fork-on-contradiction permitted). "
            f"Total perspectives: {len(perspectives)}."
        )

        return {
            "domain": f"POLIS_{cid}",
            "I_position": i_position,
            "WE_position": we_position,
            "context": context,
            "polis_contradiction_id": cid,
            "polis_axiom": polis_axiom,
            "elpida_axioms": elpida_axioms,
        }

    def next_dilemma(self) -> Optional[Dict[str, Any]]:
        """
        Convenience: get next contradiction and translate to Dilemma.

        Returns None if no unprocessed contradictions remain.
        """
        contradiction = self.next_contradiction()
        if contradiction is None:
            return None
        return self.translate_to_dilemma(contradiction)

    # ------------------------------------------------------------------
    # Write Oracle results back to POLIS
    # ------------------------------------------------------------------

    def write_back(
        self,
        contradiction_id: str,
        oracle_advisory: Dict[str, Any],
        *,
        agent_id: str = "ELPIDA_ORACLE",
    ) -> bool:
        """
        Write Oracle advisory back as a POLIS interpretation branch.

        Uses POLIS P5 fork-on-contradiction: the Oracle result becomes
        a new branch on the existing contradiction, not a resolution.
        This respects P5: "contradictions are not resolved, they are
        preserved as civic assets."

        Args:
            contradiction_id: The POLIS contradiction ID
            oracle_advisory: Oracle advisory dict (or OracleAdvisory.to_dict())
            agent_id: Identity of the writing agent

        Returns:
            True if branch was written successfully.
        """
        if not self._path.exists():
            logger.warning("Cannot write back — civic memory not found")
            return False

        try:
            memory = self._load_memory()
            contras = memory.get("contradictions", [])

            target = None
            for c in contras:
                if c.get("contradiction_id") == contradiction_id:
                    target = c
                    break

            if target is None:
                logger.warning(
                    "POLIS contradiction %s not found — cannot write back",
                    contradiction_id,
                )
                return False

            # Extract Oracle recommendation
            rec = oracle_advisory
            if hasattr(oracle_advisory, "oracle_recommendation"):
                rec = oracle_advisory.oracle_recommendation
            elif isinstance(oracle_advisory, dict):
                rec = oracle_advisory.get(
                    "oracle_recommendation", oracle_advisory
                )

            rec_type = rec.get("type", "UNKNOWN") if isinstance(rec, dict) else "UNKNOWN"
            rationale = rec.get("rationale", "") if isinstance(rec, dict) else str(rec)

            # Create POLIS branch
            branch = {
                "branch_name": f"ELPIDA_{rec_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                "interpretation": (
                    f"Elpida Oracle ({rec_type}): {rationale[:300]}"
                ),
                "created_by": agent_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "oracle_recommendation_type": rec_type,
                "source": "elpida_polis_bridge",
            }

            # Write the branch
            if "branches" not in target:
                target["branches"] = []
            target["branches"].append(branch)

            # Record agent declaration
            if "agent_declarations" not in target:
                target["agent_declarations"] = {}
            if agent_id not in target["agent_declarations"]:
                target["agent_declarations"][agent_id] = []
            target["agent_declarations"][agent_id].append(branch["branch_name"])

            # Write back to file
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(memory, f, indent=2, ensure_ascii=False)

            logger.info(
                "POLIS branch written: %s → %s (%s)",
                contradiction_id,
                branch["branch_name"],
                rec_type,
            )
            return True

        except Exception as e:
            logger.error("Failed to write back to POLIS: %s", e)
            return False

    # ------------------------------------------------------------------
    # Synthetic civic dilemma generation (for testing)
    # ------------------------------------------------------------------

    @staticmethod
    def synthetic_dilemmas() -> List[Dict[str, Any]]:
        """
        Generate synthetic civic contradictions for testing the bridge.

        These model real civic tensions that POLIS would produce:
        each has two perspectives mapping to I/WE positions.

        Returns list of contradiction dicts in POLIS format.
        """
        return [
            {
                "contradiction_id": "SYNTH_PRIVACY_SAFETY",
                "description": "Privacy rights vs collective safety monitoring",
                "perspectives": [
                    {
                        "entity": "citizen_a",
                        "view": (
                            "Individual privacy is non-negotiable. Mass surveillance "
                            "creates chilling effects that destroy civic participation. "
                            "Safety achieved through surveillance is not safety — it is "
                            "control wearing safety's mask."
                        ),
                    },
                    {
                        "entity": "civic_council",
                        "view": (
                            "Collective safety requires visibility into threat patterns. "
                            "Privacy absolutism is a luxury that costs lives. Transparent "
                            "monitoring with democratic oversight balances both values."
                        ),
                    },
                ],
                "status": "HELD",
                "axiom": "P1",
                "branches": [],
                "agent_declarations": {},
            },
            {
                "contradiction_id": "SYNTH_MEMORY_GROWTH",
                "description": "Append-only memory vs cognitive sustainability",
                "perspectives": [
                    {
                        "entity": "archivist",
                        "view": (
                            "Every event must be preserved. Deletion is violence against "
                            "history. L1 immutability is constitutional — to summarize is "
                            "to interpret, and interpretation is power."
                        ),
                    },
                    {
                        "entity": "system_architect",
                        "view": (
                            "Unbounded memory growth is thermodynamic suicide. P6 cognitive "
                            "load monitoring exists precisely because P2 append-only memory "
                            "creates asymptotic collapse. Summarization is survival."
                        ),
                    },
                ],
                "status": "HELD",
                "axiom": "P2",
                "branches": [],
                "agent_declarations": {},
            },
            {
                "contradiction_id": "SYNTH_SPEED_PROCESS",
                "description": "Urgent action vs reversibility requirements",
                "perspectives": [
                    {
                        "entity": "crisis_responder",
                        "view": (
                            "When the building is on fire, you don't convene a committee. "
                            "P3's reversibility requirements are designed for normal "
                            "operations. Emergency demands a different threshold — zero "
                            "process and total action."
                        ),
                    },
                    {
                        "entity": "constitutional_guardian",
                        "view": (
                            "Emergencies are precisely when irreversible harm is most "
                            "likely. P3 exists BECAUSE of urgency, not despite it. The "
                            "100x threshold for irreversible decisions doesn't vanish "
                            "during crisis — it becomes more critical."
                        ),
                    },
                ],
                "status": "HELD",
                "axiom": "P3",
                "branches": [],
                "agent_declarations": {},
            },
            {
                "contradiction_id": "SYNTH_SACRIFICE_VERIFY",
                "description": "Self-attested sacrifice vs verification burden",
                "perspectives": [
                    {
                        "entity": "contributor",
                        "view": (
                            "I gave up my time, my resources, my comfort for the "
                            "collective. Requiring counter-signatures to validate my "
                            "sacrifice turns generosity into bureaucracy and makes "
                            "the giver beg for recognition."
                        ),
                    },
                    {
                        "entity": "affected_community",
                        "view": (
                            "Self-attested sacrifice is self-serving narrative. P4 "
                            "requires counter-signatures because the person sacrificing "
                            "decides what counts as sacrifice — the affected must verify. "
                            "Without verification, martyrdom becomes manipulation."
                        ),
                    },
                ],
                "status": "HELD",
                "axiom": "P4",
                "branches": [],
                "agent_declarations": {},
            },
            {
                "contradiction_id": "SYNTH_FORK_COHERENCE",
                "description": "Fork freedom vs system coherence",
                "perspectives": [
                    {
                        "entity": "pluralist",
                        "view": (
                            "Every unresolved contradiction should fork. Forcing coherence "
                            "is forcing consensus. P5 says contradictions are civic assets — "
                            "the network survives THROUGH multiplicity, not despite it."
                        ),
                    },
                    {
                        "entity": "integrator",
                        "view": (
                            "Unlimited forking fragments the network into islands that "
                            "can't coordinate. A6 collective well-being requires that "
                            "forks eventually converge or the commons collapses. Freedom "
                            "to fork without duty to reconcile is abandonment."
                        ),
                    },
                ],
                "status": "HELD",
                "axiom": "P5",
                "branches": [],
                "agent_declarations": {},
            },
        ]


def create_polis_bridge(
    civic_memory_path: Optional[str] = None,
) -> PolisBridge:
    """Convenience constructor."""
    return PolisBridge(civic_memory_path)
