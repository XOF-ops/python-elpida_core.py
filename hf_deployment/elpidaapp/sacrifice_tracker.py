"""
sacrifice_tracker — A7 Compliance: Log Every Cost
===================================================

When the Oracle issues a WITNESS recommendation (Empathy Protocol),
the sacrifice tracker records what each resolution path would have cost.

This is the operational implementation of Axiom A7
("Contradiction Is Data" / "Sacrifice As Data"):
  - Every tension the system cannot resolve is logged permanently.
  - Every axiom that would be violated by choosing a horn is named.
  - The cost of holding the tension (instead of resolving it) is also tracked.
  - Nothing is deleted. The sacrifice ledger grows monotonically.

Architecture lineage:
  - CASSANDRA fleet node (A5/A8/A7): "sees costs everywhere"
  - ELPIDA_UNIFIED/handshake_synthesis.py: VARIANT_WITNESS ledger
  - Master_Brain/ARCHIVE_ANALYSIS.md: "Sacrifice Tracking: 0% implemented"
  - CHECKPOINT_MARCH1.md Section 7: "Sacrifice Tracker — HIGH priority"

File format: JSONL (one JSON object per line, append-only)
Location: sacrifice_ledger.jsonl (next to oracle_advisories.jsonl)

Thread safety: append-only writes are atomic at the OS level for
lines shorter than PIPE_BUF (4096 bytes). Each record is well under
this limit. No lock required.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("elpidaapp.sacrifice_tracker")


class SacrificeTracker:
    """
    Append-only ledger for Oracle WITNESS sacrifice costs.

    Every time the Oracle issues a WITNESS recommendation, this tracker
    records the sacrifice costs — what each horn would have lost — as
    a permanent entry in the sacrifice ledger.

    Usage:
        tracker = SacrificeTracker(Path("sacrifice_ledger.jsonl"))
        # Called automatically by Oracle.adjudicate() when WITNESS fires:
        tracker.record(
            oracle_cycle=42,
            dilemma_id="DEBATE_42",
            template="A10_CRISIS_VS_RELATION",
            sacrifice_costs={...},
            witness_stance="...",
        )
    """

    def __init__(self, ledger_path: Optional[Path] = None):
        self._path = ledger_path
        self._count = 0

        # Count existing records
        if self._path and self._path.exists():
            try:
                with open(self._path, "r") as f:
                    self._count = sum(1 for line in f if line.strip())
                logger.info(
                    "SacrificeTracker: loaded %d existing records from %s",
                    self._count, self._path,
                )
            except Exception as e:
                logger.warning("SacrificeTracker: could not read ledger: %s", e)

    def record(
        self,
        *,
        oracle_cycle: int,
        dilemma_id: str,
        template: str,
        sacrifice_costs: Dict[str, Any],
        witness_stance: str,
    ) -> Dict[str, Any]:
        """
        Log a sacrifice event to the ledger.

        Args:
            oracle_cycle: The Oracle cycle number that produced WITNESS.
            dilemma_id: The dual-horn debate ID.
            template: The tension template name (e.g., "A10_CRISIS_VS_RELATION").
            sacrifice_costs: Output of Oracle._compute_sacrifice_costs().
            witness_stance: Output of Oracle._witness_stance().

        Returns:
            The sacrifice record dict.
        """
        self._count += 1

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sacrifice_number": self._count,
            "oracle_cycle": oracle_cycle,
            "dilemma_id": dilemma_id,
            "template": template,
            "horn_1_sacrifices": sacrifice_costs.get("horn_1_sacrifices", []),
            "horn_2_sacrifices": sacrifice_costs.get("horn_2_sacrifices", []),
            "shared_cost": sacrifice_costs.get("shared_cost", []),
            "reversal_cost": sacrifice_costs.get("reversal_cost", []),
            "total_axioms_at_risk": sacrifice_costs.get("total_axioms_at_risk", 0),
            "witness_stance": witness_stance,
            "axiom": "A7",
            "principle": "Contradiction Is Data — every sacrifice is signal, not loss.",
        }

        if self._path:
            try:
                with open(self._path, "a") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception as e:
                logger.error("SacrificeTracker: write failed: %s", e)

        logger.info(
            "SACRIFICE #%d | cycle=%d | template=%s | axioms_at_risk=%d",
            self._count, oracle_cycle, template,
            entry["total_axioms_at_risk"],
        )

        return entry

    @property
    def count(self) -> int:
        """Total sacrifice events recorded."""
        return self._count

    def recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Read the most recent sacrifice entries from the ledger."""
        if not self._path or not self._path.exists():
            return []

        entries: List[Dict[str, Any]] = []
        try:
            with open(self._path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            logger.warning("SacrificeTracker: read failed: %s", e)
            return []

        return entries[-limit:]

    def summary(self) -> Dict[str, Any]:
        """
        Summary statistics of all recorded sacrifices.

        Returns template frequencies, most-sacrificed axioms, and
        total events — useful for D14 Ark Curator to assess system
        health and pattern stagnation.
        """
        entries = self.recent(limit=10000)
        if not entries:
            return {"total": 0}

        templates: Dict[str, int] = {}
        axioms_at_risk: Dict[str, int] = {}

        for e in entries:
            t = e.get("template", "UNKNOWN")
            templates[t] = templates.get(t, 0) + 1

            for ax_list_key in ("horn_1_sacrifices", "horn_2_sacrifices", "shared_cost"):
                for ax in e.get(ax_list_key, []):
                    axioms_at_risk[ax] = axioms_at_risk.get(ax, 0) + 1

        return {
            "total": len(entries),
            "templates": templates,
            "axioms_at_risk": axioms_at_risk,
            "most_sacrificed_axiom": (
                max(axioms_at_risk, key=axioms_at_risk.get)
                if axioms_at_risk else None
            ),
        }


def create_sacrifice_tracker(
    ledger_path: Optional[str] = None,
) -> SacrificeTracker:
    """
    Create a SacrificeTracker instance.

    Args:
        ledger_path: Path to JSONL ledger file.
            If None, records are counted but not persisted.
    """
    path = Path(ledger_path) if ledger_path else None
    return SacrificeTracker(ledger_path=path)


# ---------------------------------------------------------------------------
# Governance Sacrifice Tracker — verdict conversion layer (A7)
# ---------------------------------------------------------------------------
# Distinct from Oracle WITNESS sacrifices: these track when the engine
# *converts* a Parliament verdict (P6, P7, block_escape, isolation_gate).
# Each conversion is a named sacrifice — one axiom's interest traded
# for another's — made visible so the system can re-evaluate later.
#
# Constitutional authority: D15 broadcast 936412441373 (A9, 2026-04-16)
# "past decisions are guides, not chains" — every sacrifice logged here
# is a decision the system can later re-evaluate.
# ---------------------------------------------------------------------------

_GOV_SACRIFICE_LOG = Path(__file__).resolve().parent.parent / "cache" / "governance_sacrifices.jsonl"

# Mapping: sacrifice type → (axiom_cost, axiom_served)
# What value was traded away, and what value was protected.
SACRIFICE_AXIOM_MAP = {
    "P6_critical_gate":    ("A3",  "A0"),   # Autonomy sacrificed for Sacred Incompletion (coherence)
    "P6_proceed_gate":     ("A3",  "A0"),   # Same: forward motion traded for structural health
    "P7_proceed_cooldown": ("A3",  "A9"),   # Autonomy traded for Temporal Coherence (breathing)
    "block_escape":        ("A4",  "A12"),  # Harm Prevention relaxed for Eternal Creative Tension
    "isolation_gate":      ("A3",  "A9"),   # Autonomy (acting on stale state) → Temporal Coherence
}


class GovernanceSacrificeTracker:
    """
    Tracks governance verdict conversions as named sacrifices.

    Wired into parliament_cycle_engine.run_cycle() at each point
    where a verdict is mutated (P6, P7, block_escape, isolation).
    """

    def __init__(self):
        self._count: int = 0
        self._type_counts: Dict[str, int] = {}

    def record(
        self,
        *,
        cycle: int,
        sacrifice_type: str,
        original_verdict: str,
        final_verdict: str,
        reason: str,
        coherence: Optional[float] = None,
        approval: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Record a governance sacrifice."""
        self._count += 1
        axiom_cost, axiom_served = SACRIFICE_AXIOM_MAP.get(
            sacrifice_type, ("?", "?")
        )
        self._type_counts[sacrifice_type] = (
            self._type_counts.get(sacrifice_type, 0) + 1
        )

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sacrifice_number": self._count,
            "cycle": cycle,
            "type": sacrifice_type,
            "original_verdict": original_verdict,
            "final_verdict": final_verdict,
            "reason": reason,
            "axiom_cost": axiom_cost,
            "axiom_served": axiom_served,
            "coherence": coherence,
            "approval": approval,
            "axiom": "A7",
        }

        logger.info(
            "A7 GOV-SACRIFICE [%s]: %s→%s cycle=%d — %s (cost=%s served=%s)",
            sacrifice_type, original_verdict, final_verdict, cycle,
            reason, axiom_cost, axiom_served,
        )

        try:
            _GOV_SACRIFICE_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(_GOV_SACRIFICE_LOG, "a") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.debug("Gov sacrifice persist failed: %s", e)

        return entry

    def summary(self) -> Dict[str, Any]:
        """Summary for heartbeat embedding."""
        return {
            "total": self._count,
            "type_counts": dict(self._type_counts),
        }
