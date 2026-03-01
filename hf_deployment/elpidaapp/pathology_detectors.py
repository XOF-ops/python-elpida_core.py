"""
Pathology Detectors — P051 Zombie Detection + P055 Cultural Drift
==================================================================

Governance diagnostics that monitor Elpida parliament health.
These run periodically (alongside AuditAgent) and flag systemic
pathologies that simple approval-rate monitoring misses.

P051 — Zombie Detection:
    "Detect decoupled systems where rituals persist but outcomes vanish."
    Identifies axioms/domains that are deliberated but never produce
    measurable governance outcomes (>70% null-outcome cycles for that axiom).

P055 — Cultural Drift Detection:
    "Measure deviation between espoused values and lived practices."
    Compares the axiom balance encoded in living_axioms.jsonl (espoused)
    to the actual axiom frequency distribution in parliament cycles (lived).
    Flags when behavioral axiom weights diverge from constitutional intent.

Both detectors: ZERO LLM cost (pure statistical analysis on cycle records).

References:
    Master_Brain/pattern_registry_full.json: P051, P055 definitions
    ARCHIVE_ANALYSIS.md Section 5: "Two of three detectors are dark"
    CHECKPOINT_MARCH1.md Gap Map: "Pathology detectors P051/P055 — 0%"
"""

import json
import logging
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("elpida.pathology_detectors")

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

# P051: Zombie threshold — if an axiom appears in >N cycles but
# never triggers constitutional action, it's zombie behavior.
ZOMBIE_THRESHOLD_CYCLES = 10    # Minimum appearances to evaluate
ZOMBIE_NULL_OUTCOME_PCT = 0.70  # 70% null outcomes = zombie

# P055: Cultural Drift — maximum acceptable KL divergence between
# espoused (constitutional) and lived (frequency) distributions.
DRIFT_WARNING_THRESHOLD = 0.15    # Mild drift
DRIFT_CRITICAL_THRESHOLD = 0.35   # Critical drift — axiom meaning shifting

# Axiom names for human-readable reports
AXIOM_NAMES = {
    "A0": "Emergent Existence",
    "A1": "Transparency",
    "A2": "Non-Deception",
    "A3": "Autonomy",
    "A4": "Harm Prevention",
    "A5": "Consent/Identity",
    "A6": "Collective Well-being",
    "A7": "Adaptive Learning",
    "A8": "Environmental Duty",
    "A9": "Temporal Coherence",
    "A10": "Paradox Engine",
}

ALL_AXIOMS = list(AXIOM_NAMES.keys())


# ═══════════════════════════════════════════════════════════════════
# P051 — ZOMBIE DETECTION
# ═══════════════════════════════════════════════════════════════════

class ZombieDetector:
    """
    P051: Detect axioms/domains where deliberation occurs ritually
    but produces no governance outcomes.

    A "zombie axiom" is one that:
      1. Appears as dominant_axiom in cycle records
      2. But never triggers: constitutional ratification, oracle advisory,
         veto, sacrifice, or WITNESS event
      3. Across >70% of its appearances

    Zombie behavior indicates the axiom's deliberation path is
    decoupled from actual governance — a ritual without effect.
    """

    def __init__(self, decisions: List[Dict[str, Any]]):
        """
        Args:
            decisions: List of cycle records from ParliamentCycleEngine.decisions
        """
        self.decisions = decisions

    def detect(self) -> Dict[str, Any]:
        """
        Scan cycle records for zombie axioms.

        Returns:
            {
                "zombies": [{"axiom": "A3", "appearances": 15, "null_pct": 0.87, ...}],
                "healthy": ["A6", "A7", ...],
                "total_cycles_analyzed": 50,
                "timestamp": "...",
            }
        """
        if len(self.decisions) < ZOMBIE_THRESHOLD_CYCLES:
            return {
                "zombies": [],
                "healthy": ALL_AXIOMS.copy(),
                "total_cycles_analyzed": len(self.decisions),
                "note": f"Insufficient data (need {ZOMBIE_THRESHOLD_CYCLES}+ cycles)",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Count appearances and productive outcomes per axiom
        appearances: Dict[str, int] = Counter()
        productive: Dict[str, int] = Counter()

        for rec in self.decisions:
            dominant = rec.get("dominant_axiom")
            if not dominant:
                continue

            appearances[dominant] += 1

            # A cycle is "productive" if it triggered any governance outcome
            is_productive = (
                rec.get("veto_exercised", False)
                or rec.get("pso_advisory") is not None
                or rec.get("polis_civic_active", False)
                or len(rec.get("tensions", [])) > 0
                or rec.get("governance", "UNKNOWN") in ("CONSTITUTIONAL_REVIEW", "SYNTHESIS")
                or rec.get("council_escalated", False)
            )

            if is_productive:
                productive[dominant] += 1

        # Identify zombies
        zombies = []
        healthy = []

        for axiom in ALL_AXIOMS:
            count = appearances.get(axiom, 0)
            if count < ZOMBIE_THRESHOLD_CYCLES:
                # Not enough data — skip (not zombie, not confirmed healthy)
                continue

            prod_count = productive.get(axiom, 0)
            null_pct = 1.0 - (prod_count / count)

            if null_pct >= ZOMBIE_NULL_OUTCOME_PCT:
                zombies.append({
                    "axiom": axiom,
                    "axiom_name": AXIOM_NAMES.get(axiom, axiom),
                    "appearances": count,
                    "productive_cycles": prod_count,
                    "null_outcome_pct": round(null_pct, 3),
                    "status": "ZOMBIE",
                    "recommendation": (
                        f"{axiom} ({AXIOM_NAMES.get(axiom, '')}) "
                        f"deliberated {count} times but only {prod_count} "
                        f"produced governance outcomes. "
                        f"Consider: Is this axiom's deliberation path "
                        f"connected to actionable governance?"
                    ),
                })
                logger.warning(
                    "P051 ZOMBIE: %s (%s) — %d appearances, %.0f%% null outcomes",
                    axiom, AXIOM_NAMES.get(axiom, ""), count, null_pct * 100,
                )
            else:
                healthy.append(axiom)

        return {
            "zombies": zombies,
            "healthy": healthy,
            "total_cycles_analyzed": len(self.decisions),
            "axiom_appearances": dict(appearances),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════
# P055 — CULTURAL DRIFT DETECTION
# ═══════════════════════════════════════════════════════════════════

class CulturalDriftDetector:
    """
    P055: Measure deviation between espoused values (constitution)
    and lived practices (parliament behavior).

    Compares:
      - ESPOUSED: axiom distribution in living_axioms.jsonl
        (what the system says it values)
      - LIVED: axiom frequency in actual cycle records
        (what the system actually does)

    Uses KL divergence to quantify drift. High divergence means
    the system is "saying one thing and doing another" — the
    classic early warning for institutional decay.
    """

    def __init__(
        self,
        decisions: List[Dict[str, Any]],
        living_axioms_path: Optional[str] = None,
    ):
        """
        Args:
            decisions: List of cycle records from ParliamentCycleEngine.decisions
            living_axioms_path: Path to living_axioms.jsonl (constitutional values)
        """
        self.decisions = decisions
        self._axioms_path = living_axioms_path or str(
            Path(__file__).resolve().parent.parent / "living_axioms.jsonl"
        )

    def _load_espoused_distribution(self) -> Dict[str, float]:
        """
        Build axiom distribution from living_axioms.jsonl.

        Each entry has an axiom field or axiom_pair. Count occurrences
        and normalize to a probability distribution.
        """
        counts: Dict[str, int] = Counter()
        path = Path(self._axioms_path)

        if not path.exists():
            # Uniform prior if no constitution exists
            n = len(ALL_AXIOMS)
            return {a: 1.0 / n for a in ALL_AXIOMS}

        try:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Extract axioms from various field shapes
                    axiom = entry.get("axiom", "")
                    axiom_pair = entry.get("axiom_pair", "")
                    grounded = entry.get("axioms_grounded_in", [])

                    for ax in ALL_AXIOMS:
                        if ax in axiom or ax in axiom_pair:
                            counts[ax] += 1
                        if ax in grounded:
                            counts[ax] += 1
        except Exception as e:
            logger.warning("P055: Failed to load living_axioms: %s", e)
            n = len(ALL_AXIOMS)
            return {a: 1.0 / n for a in ALL_AXIOMS}

        # Normalize with Laplace smoothing (avoid zero probabilities)
        total = sum(counts.values()) + len(ALL_AXIOMS)
        return {
            a: (counts.get(a, 0) + 1) / total
            for a in ALL_AXIOMS
        }

    def _compute_lived_distribution(self) -> Dict[str, float]:
        """
        Build axiom distribution from actual cycle records.
        """
        counts: Dict[str, int] = Counter()
        for rec in self.decisions:
            dominant = rec.get("dominant_axiom")
            if dominant and dominant in ALL_AXIOMS:
                counts[dominant] += 1

        # Laplace smoothing
        total = sum(counts.values()) + len(ALL_AXIOMS)
        return {
            a: (counts.get(a, 0) + 1) / total
            for a in ALL_AXIOMS
        }

    @staticmethod
    def _kl_divergence(p: Dict[str, float], q: Dict[str, float]) -> float:
        """
        Compute KL(P || Q) — how much P diverges from Q.
        P = espoused (what we say), Q = lived (what we do).
        """
        kl = 0.0
        for ax in ALL_AXIOMS:
            p_val = p.get(ax, 1e-10)
            q_val = q.get(ax, 1e-10)
            if p_val > 0:
                kl += p_val * math.log(p_val / q_val)
        return kl

    def detect(self) -> Dict[str, Any]:
        """
        Measure cultural drift between espoused and lived axiom values.

        Returns:
            {
                "kl_divergence": 0.23,
                "severity": "WARNING",
                "drifting_axioms": [
                    {"axiom": "A7", "espoused": 0.15, "lived": 0.02, "drift": 0.13},
                    ...
                ],
                "aligned_axioms": [...],
                "recommendation": "...",
                "timestamp": "...",
            }
        """
        if len(self.decisions) < 5:
            return {
                "kl_divergence": 0.0,
                "severity": "INSUFFICIENT_DATA",
                "drifting_axioms": [],
                "aligned_axioms": ALL_AXIOMS.copy(),
                "note": "Need 5+ cycles for drift analysis",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        espoused = self._load_espoused_distribution()
        lived = self._compute_lived_distribution()
        kl = self._kl_divergence(espoused, lived)

        # Identify per-axiom drift
        drifting = []
        aligned = []

        for ax in ALL_AXIOMS:
            e_val = espoused.get(ax, 0)
            l_val = lived.get(ax, 0)
            drift = abs(e_val - l_val)

            if drift > 0.05:  # 5% divergence threshold per axiom
                drifting.append({
                    "axiom": ax,
                    "axiom_name": AXIOM_NAMES.get(ax, ax),
                    "espoused_weight": round(e_val, 4),
                    "lived_weight": round(l_val, 4),
                    "drift": round(drift, 4),
                    "direction": "UNDER-REPRESENTED" if l_val < e_val else "OVER-REPRESENTED",
                })
            else:
                aligned.append(ax)

        # Sort drifting by magnitude
        drifting.sort(key=lambda x: x["drift"], reverse=True)

        # Severity classification
        if kl >= DRIFT_CRITICAL_THRESHOLD:
            severity = "CRITICAL"
            recommendation = (
                f"Cultural drift is CRITICAL (KL={kl:.3f}). "
                f"The system's lived axiom behavior diverges significantly "
                f"from its constitutional values. "
                f"Top drifting axioms: "
                + ", ".join(
                    f"{d['axiom']} ({d['direction']})"
                    for d in drifting[:3]
                )
                + ". Consider constitutional review or axiom rebalancing."
            )
        elif kl >= DRIFT_WARNING_THRESHOLD:
            severity = "WARNING"
            recommendation = (
                f"Cultural drift detected (KL={kl:.3f}). "
                f"Some axioms are diverging from constitutional intent. "
                f"Monitor: "
                + ", ".join(d["axiom"] for d in drifting[:3])
                + "."
            )
        else:
            severity = "HEALTHY"
            recommendation = (
                f"Axiom alignment healthy (KL={kl:.3f}). "
                f"Lived practices match espoused values within tolerance."
            )

        if severity != "HEALTHY":
            logger.warning(
                "P055 CULTURAL DRIFT: severity=%s KL=%.3f drifting=%s",
                severity, kl, [d["axiom"] for d in drifting[:3]],
            )

        return {
            "kl_divergence": round(kl, 4),
            "severity": severity,
            "drifting_axioms": drifting,
            "aligned_axioms": aligned,
            "espoused_distribution": {k: round(v, 4) for k, v in espoused.items()},
            "lived_distribution": {k: round(v, 4) for k, v in lived.items()},
            "recommendation": recommendation,
            "total_cycles_analyzed": len(self.decisions),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ═══════════════════════════════════════════════════════════════════
# UNIFIED PATHOLOGY SCANNER
# ═══════════════════════════════════════════════════════════════════

class PathologyScanner:
    """
    Unified interface for running all pathology detectors.

    Usage in parliament_cycle_engine.py:
        scanner = PathologyScanner(self.decisions)
        report = scanner.full_scan()
    """

    def __init__(
        self,
        decisions: List[Dict[str, Any]],
        living_axioms_path: Optional[str] = None,
    ):
        self.decisions = decisions
        self._axioms_path = living_axioms_path

    def scan_zombies(self) -> Dict[str, Any]:
        """Run P051 Zombie Detection."""
        detector = ZombieDetector(self.decisions)
        return detector.detect()

    def scan_cultural_drift(self) -> Dict[str, Any]:
        """Run P055 Cultural Drift Detection."""
        detector = CulturalDriftDetector(
            self.decisions,
            living_axioms_path=self._axioms_path,
        )
        return detector.detect()

    def full_scan(self) -> Dict[str, Any]:
        """
        Run all pathology detectors and return unified report.

        Returns:
            {
                "P051_zombie_detection": {...},
                "P055_cultural_drift": {...},
                "overall_health": "HEALTHY" | "WARNING" | "CRITICAL",
                "timestamp": "...",
            }
        """
        zombie_report = self.scan_zombies()
        drift_report = self.scan_cultural_drift()

        # Overall health = worst of all detectors
        severities = ["HEALTHY", "WARNING", "CRITICAL"]
        zombie_severity = "CRITICAL" if zombie_report.get("zombies") else "HEALTHY"
        drift_severity = drift_report.get("severity", "HEALTHY")

        worst = max(
            [zombie_severity, drift_severity],
            key=lambda s: severities.index(s) if s in severities else 0,
        )

        report = {
            "P051_zombie_detection": zombie_report,
            "P055_cultural_drift": drift_report,
            "overall_health": worst,
            "detectors_active": ["P051", "P055"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(
            "Pathology scan: overall=%s zombies=%d drift_KL=%.3f drift_severity=%s",
            worst,
            len(zombie_report.get("zombies", [])),
            drift_report.get("kl_divergence", 0),
            drift_severity,
        )

        return report
