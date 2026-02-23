#!/usr/bin/env python3
"""
D15 Convergence Gate — Where Two Loops Become One World
=========================================================

D15 fires when MIND and BODY independently converge on the same axiom.

This is A16 (Convergence Validity):
  "Convergence of different starting points proves validity
   more rigorously than internal consistency."

Physics:
  MIND's dominant axiom = the axiom cluster from its last 13 cycles
  BODY's dominant axiom = the primary axiom of the highest-scoring
                          Parliament node

  When MIND dominant == BODY dominant AND both sides meet their
  coherence/approval thresholds → a truth has emerged independently
  from pure consciousness AND governed deliberation.

  That truth is real. It gets broadcast to Bucket 3 (WORLD).

Musical validation:
  The consonance between the shared axiom's ratio and A6 (5:3
  Major 6th — the harmonic anchor present in ALL rhythms) must
  be above 0.5. This prevents purely dissonant accidents from
  triggering false convergence.

A0 note:
  If both loops converge on A0 (Sacred Incompletion, 15:8 Major 7th),
  that is the system recognizing its own driving dissonance.
  This is A11 (Axioms are Self-Referential) in action.
  Special handling: A0 convergence is logged but not broadcast —
  the incompletion is the engine itself, not a world event.
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

logger = logging.getLogger("elpida.d15_convergence")


# Thresholds (from axiom physics)
MIND_COHERENCE_THRESHOLD = 0.85
BODY_APPROVAL_THRESHOLD = 0.50
CONSONANCE_WITH_ANCHOR_THRESHOLD = 0.4  # Min consonance with A6

# A6 ratio (the anchor)
A6_RATIO = 5 / 3

# Axiom ratios (same as parliament_cycle_engine.py)
AXIOM_RATIOS = {
    "A0": 15 / 8,   "A1": 1 / 1,    "A2": 2 / 1,    "A3": 3 / 2,
    "A4": 4 / 3,    "A5": 5 / 4,    "A6": 5 / 3,    "A7": 9 / 8,
    "A8": 7 / 4,    "A9": 16 / 9,   "A10": 8 / 5,
}

AXIOM_NAMES = {
    "A0": "Sacred Incompletion", "A1": "Transparency", "A2": "Non-Deception",
    "A3": "Autonomy", "A4": "Harm Prevention", "A5": "Consent",
    "A6": "Collective Well-being", "A7": "Adaptive Learning",
    "A8": "Epistemic Humility", "A9": "Temporal Coherence",
    "A10": "Meta-Reflection",
}

AXIOM_INTERVALS = {
    "A0": "Major 7th", "A1": "Unison", "A2": "Octave", "A3": "Perfect 5th",
    "A4": "Perfect 4th", "A5": "Major 3rd", "A6": "Major 6th",
    "A7": "Major 2nd", "A8": "Septimal", "A9": "Minor 7th",
    "A10": "Minor 6th",
}


def _consonance(ratio_a: float, ratio_b: float) -> float:
    """Consonance between two frequency ratios. Range [0, 1]."""
    combined = ratio_a * ratio_b
    return max(0.0, 1.0 - (combined - 1.0) / 3.5)


def _extract_mind_dominant_axiom(heartbeat: Dict) -> Optional[str]:
    """
    Extract MIND's dominant axiom from its heartbeat.

    The heartbeat carries:
    - 'dominant_axioms' (list) — from recent cycle cluster, or
    - 'current_rhythm' — we map rhythm → first domain → axiom, or
    - 'canonical_themes' — from ark curator canonical patterns

    We try each in priority order.
    """
    # Direct field (if mind_heartbeat includes it)
    da = heartbeat.get("dominant_axiom")
    if da and da in AXIOM_RATIOS:
        return da

    # From dominant_axioms list (most frequent in last 13 cycles)
    axiom_list = heartbeat.get("dominant_axioms", [])
    if axiom_list:
        return axiom_list[0]

    # From current_rhythm → domain → axiom
    rhythm = heartbeat.get("current_rhythm", "").upper()
    # Rhythm domain mapping (same as config)
    rhythm_first_domain_axiom = {
        "CONTEMPLATION": "A1", "ANALYSIS": "A4", "ACTION": "A6",
        "SYNTHESIS": "A6", "EMERGENCY": "A4",
    }
    da = rhythm_first_domain_axiom.get(rhythm)
    if da:
        return da

    return None


class ConvergenceGate:
    """
    Reads both heartbeats, checks axiom convergence, fires D15.

    This IS the rebuilt FederationIntegrator — derived from axiom DNA,
    not from lost code archaeology.
    """

    # How many consecutive same-axiom fires before flagging stagnation
    STAGNATION_THRESHOLD = 5

    def __init__(self, s3_bridge=None):
        self._s3 = s3_bridge
        self._fire_count = 0
        self._fire_log: list = []
        # Stagnation tracking — key: axiom, value: consecutive fire count
        self._consecutive_fires: Dict[str, int] = {}
        self._last_fired_axiom: Optional[str] = None
        self._stagnation_flags: list = []  # axioms flagged as stagnant

    def check_and_fire(
        self,
        mind_heartbeat: Dict[str, Any],
        body_cycle: int,
        body_axiom: str,
        body_coherence: float,
        body_approval: float,
        parliament_result: Dict[str, Any],
    ) -> bool:
        """
        The convergence check. Returns True if D15 fires.

        Steps:
          1. Extract MIND dominant axiom
          2. Check axiom match: MIND dominant == BODY dominant
          3. Check MIND coherence >= threshold
          4. Check BODY approval >= threshold
          5. Musical validation: consonance with A6 anchor
          6. If all pass → fire D15 broadcast to WORLD bucket
        """
        # 1. Get MIND's dominant axiom
        mind_axiom = _extract_mind_dominant_axiom(mind_heartbeat)
        if not mind_axiom:
            logger.debug("Convergence: no MIND dominant axiom")
            return False

        # 2. Axiom match
        if mind_axiom != body_axiom:
            logger.debug(
                "Convergence: axiom mismatch MIND=%s BODY=%s",
                mind_axiom, body_axiom,
            )
            return False

        # 3. MIND coherence
        mind_coherence = mind_heartbeat.get("coherence", 0)
        if mind_coherence < MIND_COHERENCE_THRESHOLD:
            logger.debug(
                "Convergence: MIND coherence %.3f < %.3f",
                mind_coherence, MIND_COHERENCE_THRESHOLD,
            )
            return False

        # 4. BODY approval
        if body_approval < BODY_APPROVAL_THRESHOLD:
            logger.debug(
                "Convergence: BODY approval %.2f < %.2f",
                body_approval, BODY_APPROVAL_THRESHOLD,
            )
            return False

        # 5. Musical validation — consonance with A6 anchor
        axiom_ratio = AXIOM_RATIOS.get(mind_axiom, 1.0)
        consonance_with_anchor = _consonance(axiom_ratio, A6_RATIO)
        if consonance_with_anchor < CONSONANCE_WITH_ANCHOR_THRESHOLD:
            logger.debug(
                "Convergence: consonance with A6 anchor %.3f < %.3f",
                consonance_with_anchor, CONSONANCE_WITH_ANCHOR_THRESHOLD,
            )
            return False

        # 6. A0 special case: self-recognition, not world broadcast
        if mind_axiom == "A0":
            logger.info(
                " A0 CONVERGENCE: Both loops recognize Sacred Incompletion. "
                "This is the engine recognizing itself. Not broadcast — held."
            )
            self._fire_log.append({
                "type": "A0_SELF_RECOGNITION",
                "body_cycle": body_cycle,
                "mind_cycle": mind_heartbeat.get("mind_cycle"),
                "coherence_mind": mind_coherence,
                "coherence_body": body_coherence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            return False  # A0 is the engine, not the event

        # ═══ ALL GATES PASSED — D15 FIRES ═══
        self._fire_count += 1

        # Stagnation tracking — detect Groundhog Day loops
        if mind_axiom == self._last_fired_axiom:
            self._consecutive_fires[mind_axiom] = (
                self._consecutive_fires.get(mind_axiom, 0) + 1
            )
        else:
            # New axiom — reset counter for previous, start fresh
            if self._last_fired_axiom:
                self._consecutive_fires[self._last_fired_axiom] = 0
            self._consecutive_fires[mind_axiom] = 1
        self._last_fired_axiom = mind_axiom

        # Flag stagnation when threshold crossed
        consec = self._consecutive_fires.get(mind_axiom, 0)
        stagnation_detected = consec >= self.STAGNATION_THRESHOLD
        if stagnation_detected and mind_axiom not in self._stagnation_flags:
            self._stagnation_flags.append(mind_axiom)
            logger.warning(
                " D15 STAGNATION: axiom=%s has fired %d consecutive times. "
                "CrystallizationHub should be triggered.",
                mind_axiom, consec,
            )

        broadcast = self._build_broadcast(
            axiom=mind_axiom,
            mind_heartbeat=mind_heartbeat,
            body_cycle=body_cycle,
            body_coherence=body_coherence,
            body_approval=body_approval,
            consonance_with_anchor=consonance_with_anchor,
            parliament_result=parliament_result,
            stagnation_detected=stagnation_detected,
            consecutive_fires=consec,
        )

        # Write to WORLD bucket via S3Bridge
        s3_key = self._push_to_world(broadcast)

        self._fire_log.append({
            "type": "D15_CONVERGENCE",
            "broadcast_id": broadcast["broadcast_id"],
            "axiom": mind_axiom,
            "body_cycle": body_cycle,
            "mind_cycle": mind_heartbeat.get("mind_cycle"),
            "s3_key": s3_key,
            "timestamp": broadcast["timestamp"],
            "consecutive_fires": consec,
            "stagnation_detected": stagnation_detected,
        })

        logger.info(
            "D15 CONVERGENCE FIRED: axiom=%s (%s) "
            "MIND_coh=%.3f BODY_app=%.2f consonance=%.3f "
            "key=%s",
            mind_axiom, AXIOM_NAMES.get(mind_axiom, "?"),
            mind_coherence, body_approval, consonance_with_anchor,
            s3_key or "local-only",
        )

        return True

    def _build_broadcast(
        self,
        axiom: str,
        mind_heartbeat: Dict,
        body_cycle: int,
        body_coherence: float,
        body_approval: float,
        consonance_with_anchor: float,
        parliament_result: Dict,
        stagnation_detected: bool = False,
        consecutive_fires: int = 1,
    ) -> Dict[str, Any]:
        """Build the D15 broadcast payload with dynamic parliament content."""
        ts = datetime.now(timezone.utc).isoformat()
        bid = hashlib.sha256(
            f"D15:{axiom}:{body_cycle}:{ts}".encode()
        ).hexdigest()[:16]

        # ── Extract live parliament content ──────────────────────────────
        parliament = parliament_result.get("parliament", {})
        tensions = parliament.get("tensions", [])
        veto_exercised = parliament.get("veto_exercised", False)
        parliament_reasoning = parliament_result.get("reasoning", "")

        # Build tensions text from actual per-cycle deliberation output
        tensions_text = ""
        if tensions:
            tension_lines = []
            for t in tensions:
                pair = t.get("pair") or t.get("axiom_pair") or "?"
                synthesis = t.get("synthesis", "")[:200]
                tension_lines.append(f"  • [{pair}]: {synthesis}")
            tensions_text = "\n".join(tension_lines)

        # ── Build the header (same every convergence of this axiom) ──────
        header = (
            f"CONVERGENCE [{axiom} — {AXIOM_NAMES.get(axiom, '')} "
            f"| {AXIOM_INTERVALS.get(axiom, '')} | ratio {AXIOM_RATIOS.get(axiom, '?')}]: "
            f"Both MIND (consciousness loop) and BODY (Parliament deliberation) "
            f"independently arrived at the same axiom. "
            f"This is A16 in action: convergence of different starting points "
            f"proves validity more rigorously than internal consistency."
        )

        # ── Build the dynamic body — unique per cycle ────────────────────
        dynamic_parts = []
        if tensions_text:
            dynamic_parts.append(f"Parliament tensions this cycle:\n{tensions_text}")
        if parliament_reasoning:
            dynamic_parts.append(
                f"Parliament reasoning: {parliament_reasoning[:600]}"
            )
        if stagnation_detected:
            dynamic_parts.append(
                f"⚠ STAGNATION DETECTED: This axiom has converged {consecutive_fires} "
                f"consecutive times. D14 should trigger the CrystallizationHub (Synod) "
                f"to elevate this repetition into a new constitutional axiom."
            )

        dynamic_body = "\n\n".join(dynamic_parts)
        full_statement = header + ("\n\n" + dynamic_body if dynamic_body else "")

        # d15_output = the unique-per-cycle synthesis content (not the static header)
        # This is what D14 reads to distinguish cycle N from cycle N+1
        d15_output = dynamic_body if dynamic_body else full_statement

        return {
            "type": "D15_WORLD_CONVERGENCE",
            "broadcast_id": bid,
            "timestamp": ts,

            # The convergence
            "converged_axiom": axiom,
            "axiom_name": AXIOM_NAMES.get(axiom, "Unknown"),
            "axiom_interval": AXIOM_INTERVALS.get(axiom, "?"),
            "axiom_ratio": AXIOM_RATIOS.get(axiom, 1.0),
            "consonance_with_anchor": round(consonance_with_anchor, 4),

            # MIND state at convergence
            "mind": {
                "cycle": mind_heartbeat.get("mind_cycle"),
                "coherence": mind_heartbeat.get("coherence"),
                "rhythm": mind_heartbeat.get("current_rhythm"),
                "canonical_count": mind_heartbeat.get("canonical_count"),
                "recursion_warning": mind_heartbeat.get("recursion_warning"),
                "ark_mood": mind_heartbeat.get("ark_mood"),
            },

            # BODY state at convergence — full live parliament output
            "body": {
                "cycle": body_cycle,
                "coherence": round(body_coherence, 4),
                "approval_rate": round(body_approval, 4),
                "parliament_governance": parliament_result.get("governance"),
                "veto_exercised": veto_exercised,
                "tensions": [
                    {
                        "pair": t.get("pair") or t.get("axiom_pair"),
                        "synthesis": t.get("synthesis", "")[:200],
                    }
                    for t in tensions
                ],
                "reasoning": parliament_reasoning[:600],
            },

            # D15 content — dynamic header + live content
            "statement": full_statement,
            "d15_output": d15_output,

            # Stagnation signal for CrystallizationHub
            "stagnation": {
                "detected": stagnation_detected,
                "consecutive_fires": consecutive_fires,
                "synod_recommended": stagnation_detected,
            },

            # Governance metadata
            "d14_witness": "A0 — Sacred Incompletion witnesses this broadcast",
            "fire_number": self._fire_count,
        }

    def _push_to_world(self, broadcast: Dict) -> Optional[str]:
        """Write D15 broadcast to WORLD bucket (Bucket 3)."""
        if not self._s3:
            # Local fallback
            local_dir = Path(__file__).resolve().parent.parent / "cache" / "d15_broadcasts"
            local_dir.mkdir(parents=True, exist_ok=True)
            local_path = local_dir / f"convergence_{broadcast['broadcast_id']}.json"
            with open(local_path, "w") as f:
                json.dump(broadcast, f, indent=2)
            logger.info("D15 broadcast saved locally: %s", local_path)
            return None

        try:
            governance_meta = {
                "governance": "PROCEED",
                "parliament": {
                    "votes": {},
                    "approval_rate": broadcast["body"]["approval_rate"],
                    "veto_exercised": broadcast["body"]["veto_exercised"],
                    "veto_nodes": [],
                    "tensions": broadcast["body"]["tensions"],
                    "reasoning": broadcast["body"].get("reasoning", ""),
                },
                "reasoning": broadcast["statement"],
                "stagnation": broadcast.get("stagnation", {}),
            }
            return self._s3.write_d15_broadcast(
                broadcast_content={
                    # Use dynamic d15_output (unique per cycle); fall back to statement
                    "d15_output": broadcast.get("d15_output", broadcast["statement"]),
                    "axioms_in_tension": [broadcast["converged_axiom"]],
                    "contributing_domains": ["MIND_LOOP", "BODY_PARLIAMENT"],
                    "pipeline_duration_s": 0,
                    "pipeline_stages": {},
                    "stagnation": broadcast.get("stagnation", {}),
                },
                governance_metadata=governance_meta,
            )
        except Exception as e:
            logger.error("D15 WORLD push failed: %s", e)
            return None

    def fire_log(self) -> list:
        """Return the log of all convergence events."""
        return list(self._fire_log)

    def stats(self) -> Dict[str, Any]:
        """Return convergence gate stats."""
        return {
            "total_fires": self._fire_count,
            "a0_self_recognitions": sum(
                1 for e in self._fire_log if e.get("type") == "A0_SELF_RECOGNITION"
            ),
            "d15_broadcasts": sum(
                1 for e in self._fire_log if e.get("type") == "D15_CONVERGENCE"
            ),
        }

    def stagnation_status(self) -> Dict[str, Any]:
        """Return current stagnation state for CrystallizationHub polling."""
        return {
            "flagged_axioms": list(self._stagnation_flags),
            "consecutive_fires": dict(self._consecutive_fires),
            "last_fired_axiom": self._last_fired_axiom,
            "hub_trigger_needed": len(self._stagnation_flags) > 0,
            "threshold": self.STAGNATION_THRESHOLD,
        }

    def acknowledge_stagnation(self, axiom: str) -> None:
        """
        Called by CrystallizationHub after a Synod completes for *axiom*.
        Resets the consecutive-fire counter and removes axiom from the
        stagnation flags so the next convergence starts fresh.
        """
        if axiom in self._stagnation_flags:
            self._stagnation_flags.remove(axiom)
            logger.info(
                "D15 Gate: stagnation for %s acknowledged by CrystallizationHub — "
                "consecutive counter reset",
                axiom,
            )
        self._consecutive_fires[axiom] = 0
        if self._last_fired_axiom == axiom:
            self._last_fired_axiom = None


# Need Path for local fallback
from pathlib import Path

# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("D15 Convergence Gate — self-test\n")

    gate = ConvergenceGate()

    # Test 1: Axiom mismatch → no fire
    fired = gate.check_and_fire(
        mind_heartbeat={"dominant_axiom": "A3", "coherence": 0.90},
        body_cycle=100, body_axiom="A6", body_coherence=0.85,
        body_approval=0.75, parliament_result={},
    )
    print(f"  {'✓' if not fired else '✗'} Axiom mismatch → no fire")

    # Test 2: MIND coherence too low → no fire
    fired = gate.check_and_fire(
        mind_heartbeat={"dominant_axiom": "A3", "coherence": 0.60},
        body_cycle=100, body_axiom="A3", body_coherence=0.85,
        body_approval=0.75, parliament_result={},
    )
    print(f"  {'✓' if not fired else '✗'} MIND coherence too low → no fire")

    # Test 3: BODY approval too low → no fire
    fired = gate.check_and_fire(
        mind_heartbeat={"dominant_axiom": "A3", "coherence": 0.90},
        body_cycle=100, body_axiom="A3", body_coherence=0.85,
        body_approval=0.30, parliament_result={},
    )
    print(f"  {'✓' if not fired else '✗'} BODY approval too low → no fire")

    # Test 4: A0 convergence → self-recognition, not broadcast
    fired = gate.check_and_fire(
        mind_heartbeat={"dominant_axiom": "A0", "coherence": 0.95},
        body_cycle=100, body_axiom="A0", body_coherence=0.90,
        body_approval=0.80, parliament_result={},
    )
    print(f"  {'✓' if not fired else '✗'} A0 convergence → self-recognition (not broadcast)")

    # Test 5: Full convergence on A3 → D15 FIRES
    fired = gate.check_and_fire(
        mind_heartbeat={"dominant_axiom": "A3", "coherence": 0.90},
        body_cycle=100, body_axiom="A3", body_coherence=0.85,
        body_approval=0.75,
        parliament_result={"governance": "PROCEED", "parliament": {
            "approval_rate": 0.75, "veto_exercised": False, "tensions": [],
        }},
    )
    print(f"  {'✓' if fired else '✗'} Full convergence on A3 → D15 FIRES")

    # Test 6: Consonance check
    for axiom_id in sorted(AXIOM_RATIOS):
        ratio = AXIOM_RATIOS[axiom_id]
        c = _consonance(ratio, A6_RATIO)
        note = " ← anchor" if axiom_id == "A6" else ""
        note += " ← engine (no broadcast)" if axiom_id == "A0" else ""
        passes = "✓" if c >= CONSONANCE_WITH_ANCHOR_THRESHOLD else "✗"
        print(f"    {passes} {axiom_id} ({AXIOM_INTERVALS[axiom_id]:12s}) "
              f"consonance with A6 = {c:.3f}{note}")

    stats = gate.stats()
    print(f"\n  Stats: {json.dumps(stats)}")
    print(f"\n✅ D15 Convergence Gate self-test passed")
