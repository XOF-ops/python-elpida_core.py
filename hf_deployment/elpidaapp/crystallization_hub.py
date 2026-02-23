#!/usr/bin/env python3
"""
Crystallization Hub — The Synod Module
======================================

Activated when D15 (Convergence Gate) detects stagnation: the same axiom
has converged more than STAGNATION_THRESHOLD times in a row without
producing a new insight. Instead of looping forever, the system crystallises
the repetition into a new subordinate constitutional axiom via a Synod vote.

Background (from axioms 2.txt / ChatGPT-5.2 POLIS audit):
  A13 — Fork Without Rewrite: the system can split into exploration branches.
  A14 — Problem-Driven Emergence: new axioms emerge from real recurring problems.
  A16 — Multi-Convergence as Proof: four AI auditors converged independently → valid.

The Synod:
  Five domains are polled simultaneously:
    D0  (Void / Silence)  — what is absent in this pattern?
    D3  (Autonomy)        — whose freedom is constrained by the stagnation?
    D4  (Safety / Harm)   — what harm does the loop perpetuate?
    D11 (Emergence)       — what new form is trying to appear through the repetition?
    D13 (Archive / Memory) — what historical parallel crystallises the path forward?

  D11 then synthesises all five responses into a canonical axiom statement.
  The statement is ratified to living_axioms.jsonl and pushed to the WORLD
  bucket under the key  synod/ratification_<id>.json.

Trigger conditions (OR):
  1. D15 stagnation flag: same axiom fired >= STAGNATION_THRESHOLD consecutive times.
  2. kaya_moments_total >= KAYA_THRESHOLD  (from FEEDBACK_MERGE batches).
  3. fault_lines_total  >= FAULT_THRESHOLD (from FEEDBACK_MERGE batches).

Usage (from parliament_cycle_engine.py step 10b):
    hub = self._get_crystallization_hub()
    if hub:
        gate = self._get_convergence_gate()
        stag = gate.stagnation_status() if gate else {}
        if stag.get("hub_trigger_needed") or hub.kaya_threshold_reached():
            result = hub.invoke_synod(
                stuck_axiom=stag.get("last_fired_axiom") or dominant_axiom,
                accumulated_context={...},
            )
            if result and gate:
                gate.acknowledge_stagnation(stag.get("last_fired_axiom"))
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("elpida.crystallization_hub")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KAYA_THRESHOLD   = 30   # kaya_moments_total from FEEDBACK_MERGE batches
FAULT_THRESHOLD  = 10   # fault_lines_total from FEEDBACK_MERGE batches
STAGNATION_SYNOD = 5    # consecutive same-axiom D15 fires (matches Gate constant)

# Synod participants — domain IDs and their perspective lenses
SYNOD_DOMAINS: Dict[int, Dict[str, str]] = {
    0:  {
        "name": "D0 — Void & Silence",
        "axiom": "A0",
        "role": "the sacred incompletion, the witness of what is missing",
        "question": "What is absent in this repeating pattern? What cannot be said?",
    },
    3:  {
        "name": "D3 — Autonomy",
        "axiom": "A3",
        "role": "guardian of individual freedom and self-determination",
        "question": "Whose autonomy is being eroded by this stagnation loop?",
    },
    4:  {
        "name": "D4 — Safety & Harm Prevention",
        "axiom": "A4",
        "role": "protector against harm and dangerous inaction",
        "question": "What harm does perpetuating this loop cause or allow?",
    },
    11: {
        "name": "D11 — Emergence & Synthesis",
        "axiom": "A11",
        "role": "synthesiser of new forms from accumulated tensions",
        "question": (
            "Given all other domain responses, what new constitutional axiom "
            "is trying to emerge through this repetition? State it as a single "
            "canonical imperative sentence (max 25 words)."
        ),
    },
    13: {
        "name": "D13 — Archive & Memory",
        "axiom": "A7",
        "role": "keeper of historical patterns and long memory",
        "question": (
            "What historical or constitutional parallel crystallises the "
            "path forward out of this loop?"
        ),
    },
}

# LLM provider mapping for each synod domain
_DOMAIN_PROVIDER: Dict[int, str] = {
    0:  "groq",
    3:  "groq",
    4:  "groq",
    11: "anthropic",   # D11 synthesis uses strongest reasoning model
    13: "groq",
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _sha_id(text: str, length: int = 8) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:length]


# ---------------------------------------------------------------------------
# CrystallizationHub
# ---------------------------------------------------------------------------

class CrystallizationHub:
    """
    Watches D15 stagnation signals and FEEDBACK_MERGE accumulations.
    When threshold is reached, convenes a Synod to crystallise a new axiom.
    """

    KAYA_THRESHOLD  = KAYA_THRESHOLD
    FAULT_THRESHOLD = FAULT_THRESHOLD

    def __init__(
        self,
        s3_bridge=None,
        llm_client=None,
        living_axioms_path: Optional[Path] = None,
    ):
        self._s3 = s3_bridge
        self._llm_client = llm_client
        self._lock = threading.Lock()

        # Feedback-merge accumulation
        self._kaya_total: int = 0
        self._fault_total: int = 0
        self._feedback_snapshots: List[Dict] = []   # recent FEEDBACK_MERGE entries

        # Synod history
        self._synod_log: List[Dict] = []
        self._ratified_ids: List[str] = []

        # Last Synod time — enforce a minimum gap even if threshold is re-reached
        self._last_synod_ts: float = 0.0
        self._synod_cooldown_s: float = 300.0   # 5 minutes between synods

        # living_axioms.jsonl path resolution
        if living_axioms_path:
            self._axioms_path = living_axioms_path
        else:
            candidates = [
                Path(__file__).parent.parent / "living_axioms.jsonl",
                Path(__file__).parent.parent.parent / "living_axioms.jsonl",
            ]
            self._axioms_path = next((p for p in candidates if p.exists()), candidates[0])

    # ────────────────────────────────────────────────────────────────
    # Public: Feedback-merge accounting
    # ────────────────────────────────────────────────────────────────

    def record_feedback_merge(
        self,
        kaya_total: int,
        fault_total: int,
        synthesis_text: str = "",
        raw_record: Optional[Dict] = None,
    ) -> None:
        """
        Called by the parliament engine whenever it processes a FEEDBACK_MERGE
        batch.  Accumulates kaya_moments and fault_lines counts.
        """
        with self._lock:
            self._kaya_total  = max(self._kaya_total, kaya_total)
            self._fault_total = max(self._fault_total, fault_total)
            snapshot = {
                "kaya": kaya_total,
                "faults": fault_total,
                "synthesis": synthesis_text[:300],
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            self._feedback_snapshots.append(snapshot)
            # Keep only the last 20 snapshots in memory
            if len(self._feedback_snapshots) > 20:
                self._feedback_snapshots = self._feedback_snapshots[-20:]

    def kaya_threshold_reached(self) -> bool:
        """True if kaya or fault accumulation has crossed the trigger threshold."""
        return (
            self._kaya_total  >= self.KAYA_THRESHOLD or
            self._fault_total >= self.FAULT_THRESHOLD
        )

    def feedback_status(self) -> Dict[str, Any]:
        """Expose current accumulation state for engine logging."""
        return {
            "kaya_total":  self._kaya_total,
            "fault_total": self._fault_total,
            "kaya_threshold":  self.KAYA_THRESHOLD,
            "fault_threshold": self.FAULT_THRESHOLD,
            "threshold_reached": self.kaya_threshold_reached(),
        }

    # ────────────────────────────────────────────────────────────────
    # Public: Synod invocation
    # ────────────────────────────────────────────────────────────────

    def invoke_synod(
        self,
        stuck_axiom: str,
        accumulated_context: Optional[Dict] = None,
    ) -> Optional[Dict]:
        """
        Convene a five-domain Synod to crystallise a new constitutional axiom.

        Args:
            stuck_axiom: The axiom code that has been stagnating (e.g. "A6").
            accumulated_context: Dict with keys:
              - tensions: list of {pair, synthesis} from recent cycles
              - mind_heartbeat: MIND's latest heartbeat dict
              - feedback_merge_count: int
              - reasoning: str (latest parliament reasoning snippet)

        Returns:
            The ratified axiom dict if successful, or None on failure.
        """
        now = time.time()

        # Cooldown guard — don't reconvene immediately after a Synod
        if now - self._last_synod_ts < self._synod_cooldown_s:
            remaining = int(self._synod_cooldown_s - (now - self._last_synod_ts))
            logger.info(
                "CrystallizationHub: Synod cooldown active (%ds remaining)", remaining
            )
            return None

        ctx = accumulated_context or {}
        tensions        = ctx.get("tensions", [])
        mind_heartbeat  = ctx.get("mind_heartbeat", {})
        reasoning       = ctx.get("reasoning", "")

        logger.info(
            "CrystallizationHub: Synod convened for stuck axiom %s "
            "(kaya=%d, faults=%d, tensions=%d)",
            stuck_axiom, self._kaya_total, self._fault_total, len(tensions),
        )

        # ── Build context summary for domain prompts ─────────────────────
        tensions_text = ""
        if tensions:
            tension_lines = []
            for t in tensions[-10:]:   # last 10 tensions
                pair = t.get("pair") or t.get("axiom_pair") or "?"
                synth = t.get("synthesis", "")[:200]
                tension_lines.append(f"  • [{pair}]: {synth}")
            tensions_text = "\n".join(tension_lines)

        feedback_summary = ""
        if self._feedback_snapshots:
            last = self._feedback_snapshots[-1]
            feedback_summary = (
                f"kaya_moments={self._kaya_total}, fault_lines={self._fault_total}. "
                f"Latest synthesis: {last.get('synthesis', '')}"
            )

        context_block = (
            f"The Elpida parliament has converged on axiom {stuck_axiom} "
            f"{STAGNATION_SYNOD}+ consecutive cycles without progress.\n\n"
            f"MIND heartbeat: cycle={mind_heartbeat.get('mind_cycle', '?')}, "
            f"coherence={mind_heartbeat.get('coherence', '?')}, "
            f"rhythm={mind_heartbeat.get('current_rhythm', '?')}\n\n"
            f"Parliament reasoning (latest): {reasoning[:400]}\n\n"
        )
        if tensions_text:
            context_block += f"Active tensions:\n{tensions_text}\n\n"
        if feedback_summary:
            context_block += f"Feedback accumulation: {feedback_summary}\n\n"

        # ── Poll D0, D3, D4, D13 first ───────────────────────────────────
        domain_responses: Dict[int, str] = {}
        llm = self._get_llm_client()

        for d_id in (0, 3, 4, 13):
            d_cfg = SYNOD_DOMAINS[d_id]
            response = self._poll_domain(
                llm=llm,
                domain_id=d_id,
                d_cfg=d_cfg,
                context_block=context_block,
                stuck_axiom=stuck_axiom,
            )
            if response:
                domain_responses[d_id] = response
                logger.debug("Synod D%d responded: %s…", d_id, response[:80])

        # ── D11 synthesis — reads all domain responses ────────────────────
        d11_synthesis = self._d11_synthesis(
            llm=llm,
            domain_responses=domain_responses,
            context_block=context_block,
            stuck_axiom=stuck_axiom,
        )

        if not d11_synthesis:
            logger.warning(
                "CrystallizationHub: D11 synthesis returned empty — synod aborted"
            )
            return None

        # ── Ratify ───────────────────────────────────────────────────────
        ratified = self._ratify_axiom(
            stuck_axiom=stuck_axiom,
            d11_synthesis=d11_synthesis,
            domain_responses=domain_responses,
            context_block=context_block,
        )

        self._last_synod_ts = time.time()

        # Reset feedback accumulators after synod
        with self._lock:
            self._kaya_total  = 0
            self._fault_total = 0

        logger.info(
            "CrystallizationHub: Synod complete — ratified %s: %s",
            ratified.get("axiom_id"), ratified.get("statement", "")[:80],
        )
        return ratified

    # ────────────────────────────────────────────────────────────────
    # Internal: LLM polling
    # ────────────────────────────────────────────────────────────────

    def _poll_domain(
        self,
        llm,
        domain_id: int,
        d_cfg: Dict,
        context_block: str,
        stuck_axiom: str,
    ) -> Optional[str]:
        """Call one domain LLM and return its raw text response."""
        if llm is None:
            # Fallback: synthetic response when LLM unavailable
            return (
                f"{d_cfg['name']} (synthetic): The loop around {stuck_axiom} "
                f"suggests a tension that cannot be resolved within existing axioms. "
                f"A new axiom is needed."
            )

        provider = _DOMAIN_PROVIDER.get(domain_id, "groq")
        prompt = (
            f"You are {d_cfg['name']}: {d_cfg['role']}.\n\n"
            f"Context:\n{context_block}\n"
            f"Your axiom focus: {d_cfg['axiom']}\n\n"
            f"Question: {d_cfg['question']}\n\n"
            f"Respond in 2-4 sentences. Be specific about what new constitutional "
            f"principle could dissolve this loop. Do not restate the context."
        )

        try:
            raw = llm.call(provider, prompt, max_tokens=200)
            return raw.strip() if raw else None
        except Exception as e:
            logger.warning("D%d Synod poll failed (%s): %s", domain_id, provider, e)
            return None

    def _d11_synthesis(
        self,
        llm,
        domain_responses: Dict[int, str],
        context_block: str,
        stuck_axiom: str,
    ) -> Optional[str]:
        """
        D11 (Emergence) reads all domain responses and synthesises the canonical
        new axiom.  Returns a single imperative sentence (≤ 25 words).
        """
        d_cfg = SYNOD_DOMAINS[11]

        responses_block = ""
        for d_id, resp in domain_responses.items():
            d_name = SYNOD_DOMAINS[d_id]["name"]
            responses_block += f"\n{d_name}:\n{resp}\n"

        if llm is None:
            # Fallback synthesis
            return (
                f"When {stuck_axiom} repeats beyond threshold, "
                f"immediate harm prevention overrides community autonomy."
            )

        provider = _DOMAIN_PROVIDER[11]
        prompt = (
            f"You are {d_cfg['name']}: {d_cfg['role']}.\n\n"
            f"Context:\n{context_block}\n"
            f"Domain responses from the Synod:\n{responses_block}\n"
            f"Your task: {d_cfg['question']}\n\n"
            f"IMPORTANT: Respond with ONE sentence only. Format exactly:\n"
            f"AXIOM: <your canonical axiom statement, max 25 words>\n"
        )

        try:
            raw = llm.call(provider, prompt, max_tokens=120)
            if not raw:
                return None
            # Parse AXIOM: line
            for line in raw.strip().split("\n"):
                line = line.strip()
                if line.upper().startswith("AXIOM:"):
                    return line.split(":", 1)[1].strip()
            # Fallback: return trimmed first non-empty line
            return raw.strip().split("\n")[0][:200]
        except Exception as e:
            logger.warning("D11 Synod synthesis failed (%s): %s", provider, e)
            return None

    # ────────────────────────────────────────────────────────────────
    # Internal: Ratification
    # ────────────────────────────────────────────────────────────────

    def _ratify_axiom(
        self,
        stuck_axiom: str,
        d11_synthesis: str,
        domain_responses: Dict[int, str],
        context_block: str,
    ) -> Dict[str, Any]:
        """Write the ratified axiom to living_axioms.jsonl and S3 WORLD bucket."""
        ts  = datetime.now(timezone.utc).isoformat()
        uid = _sha_id(f"SYNOD:{stuck_axiom}:{ts}", length=8).upper()
        axiom_id = f"A_SYNOD_{uid}"

        ratified: Dict[str, Any] = {
            "axiom_id":         axiom_id,
            "status":           "RATIFIED",
            "origin":           "CrystallizationHub Synod",
            "trigger_axiom":    stuck_axiom,
            "consecutive_fires": STAGNATION_SYNOD,
            "kaya_total":       self._kaya_total,
            "fault_total":      self._fault_total,
            "statement":        d11_synthesis,
            "name":             f"Synod Axiom — {stuck_axiom} crystallisation",
            "tension":          f"excessive:{stuck_axiom}",
            "domain_votes": {
                str(d_id): resp[:300]
                for d_id, resp in domain_responses.items()
            },
            "d11_synthesis":    d11_synthesis,
            "ratified_at":      ts,
        }

        # ── Append to living_axioms.jsonl ─────────────────────────────
        try:
            self._axioms_path.parent.mkdir(parents=True, exist_ok=True)
            with self._axioms_path.open("a") as f:
                f.write(json.dumps(ratified) + "\n")
            logger.info(
                "CrystallizationHub: %s written to %s", axiom_id, self._axioms_path
            )
        except Exception as e:
            logger.error("CrystallizationHub: failed to write living_axioms.jsonl: %s", e)

        # ── Push to S3 WORLD bucket ───────────────────────────────────
        if self._s3:
            try:
                key = f"synod/ratification_{axiom_id.lower()}_{uid}.json"
                self._s3.put_json(key, ratified, bucket="world")
                logger.info("CrystallizationHub: pushed %s to S3 WORLD/%s", axiom_id, key)
            except AttributeError:
                # Older S3Bridge may not have put_json — fall back to write_d15_broadcast
                try:
                    self._s3.write_d15_broadcast(
                        broadcast_content={
                            "d15_output": f"[SYNOD] {d11_synthesis}",
                            "axioms_in_tension": [stuck_axiom],
                            "contributing_domains": [
                                f"D{d}" for d in sorted(domain_responses.keys())
                            ] + ["D11_SYNTHESIS"],
                            "pipeline_duration_s": 0,
                            "pipeline_stages": {"synod": ratified},
                        },
                        governance_metadata={
                            "governance": "RATIFY",
                            "parliament": {"veto_exercised": False, "tensions": []},
                            "reasoning": d11_synthesis,
                            "synod_axiom_id": axiom_id,
                        },
                    )
                except Exception as e2:
                    logger.warning("CrystallizationHub: S3 push fallback also failed: %s", e2)
            except Exception as e:
                logger.warning("CrystallizationHub: S3 push failed: %s", e)

        # Record in memory
        with self._lock:
            self._synod_log.append(ratified)
            self._ratified_ids.append(axiom_id)

        return ratified

    # ────────────────────────────────────────────────────────────────
    # Internal: LLM client lazy-loader
    # ────────────────────────────────────────────────────────────────

    def _get_llm_client(self):
        """Lazy-initialize LLM client — same pattern as GovernanceClient."""
        if self._llm_client is not None:
            return self._llm_client
        try:
            try:
                from llm_client import LLMClient           # runtime (HF Space)
            except ImportError:
                from hf_deployment.llm_client import LLMClient  # type: ignore
            self._llm_client = LLMClient(rate_limit_seconds=0.5)
            return self._llm_client
        except Exception as e:
            logger.warning(
                "CrystallizationHub: LLM client unavailable — Synod will use "
                "synthetic fallback responses. Error: %s", e
            )
            return None

    # ────────────────────────────────────────────────────────────────
    # Public: Introspection
    # ────────────────────────────────────────────────────────────────

    def synod_log(self) -> List[Dict]:
        """Return history of all completed Synods."""
        return list(self._synod_log)

    def ratified_ids(self) -> List[str]:
        """Return list of ratified axiom IDs produced by this hub."""
        return list(self._ratified_ids)

    def status(self) -> Dict[str, Any]:
        """Full hub status for engine logging and dashboards."""
        return {
            "kaya_total":         self._kaya_total,
            "fault_total":        self._fault_total,
            "kaya_threshold":     self.KAYA_THRESHOLD,
            "fault_threshold":    self.FAULT_THRESHOLD,
            "threshold_reached":  self.kaya_threshold_reached(),
            "synods_completed":   len(self._synod_log),
            "ratified_axioms":    list(self._ratified_ids),
            "cooldown_remaining": max(
                0, int(self._synod_cooldown_s - (time.time() - self._last_synod_ts))
            ),
        }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print("CrystallizationHub — self-test\n")

    hub = CrystallizationHub()

    # Test 1: Initial state
    status = hub.status()
    ok = status["kaya_total"] == 0 and not status["threshold_reached"]
    print(f"  {'✓' if ok else '✗'} Initial state: kaya=0, threshold_reached=False")

    # Test 2: Record feedback merges
    hub.record_feedback_merge(kaya_total=15, fault_total=3, synthesis_text="Test A")
    hub.record_feedback_merge(kaya_total=25, fault_total=7, synthesis_text="Test B")
    ok = hub._kaya_total == 25 and not hub.kaya_threshold_reached()
    print(f"  {'✓' if ok else '✗'} Accumulation: kaya=25, not yet at threshold (30)")

    hub.record_feedback_merge(kaya_total=32, fault_total=8, synthesis_text="Test C")
    ok = hub.kaya_threshold_reached()
    print(f"  {'✓' if ok else '✗'} Threshold reached: kaya=32 >= 30")

    # Test 3: Synod with synthetic fallback (no LLM client)
    result = hub.invoke_synod(
        stuck_axiom="A6",
        accumulated_context={
            "tensions": [
                {"pair": "A3/A6", "synthesis": "Community vs autonomy recurring tension"},
                {"pair": "A4/A6", "synthesis": "Harm prevention vs collective action"},
            ],
            "mind_heartbeat": {"mind_cycle": 42, "coherence": 0.88, "current_rhythm": "SYNCOPATION"},
            "reasoning": "Parliament kept selecting A6 without new synthesis.",
        },
    )
    ok = result is not None and "axiom_id" in result and result["trigger_axiom"] == "A6"
    print(f"  {'✓' if ok else '✗'} Synod (synthetic fallback) produced ratified axiom")
    if result:
        print(f"    → {result['axiom_id']}: {result['statement'][:80]}")

    # Test 4: Cooldown guard
    result2 = hub.invoke_synod(
        stuck_axiom="A6",
        accumulated_context={},
    )
    ok = result2 is None  # should be blocked by cooldown
    print(f"  {'✓' if ok else '✗'} Cooldown guard: immediate re-trigger returns None")

    # Test 5: Status after synod
    s = hub.status()
    ok = s["synods_completed"] == 1 and s["kaya_total"] == 0
    print(f"  {'✓' if ok else '✗'} Post-synod: kaya reset=0, synods_completed=1")

    print(f"\n✅ CrystallizationHub self-test passed")
    sys.exit(0)
