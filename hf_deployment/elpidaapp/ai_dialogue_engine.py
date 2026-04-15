"""
ai_dialogue_engine.py — BODY AI-to-AI Peer Dialogue Module
============================================================

Represents the BODY's AI-to-AI conversation capability.

The Parliament periodically poses a question to 2 external peer AI
systems.  Each responds independently to the same question (no
cross-contamination of responses).  Their answers arrive as Scanner
InputEvents that Parliament deliberates in the next cycle.

Architecture::

    Parliament dominant tension / D15 synthesis
      → AIDialogueEngine.run_dialogue_round(topic, dominant_axiom, cycle)
        → Prompt sanitised (no internal architecture references)
        → Peer A (e.g. Gemini) called  →  response → InputBuffer ("scanner")
        → Peer B (e.g. Grok / OpenAI, rotated) →  response → InputBuffer
        → Full transcript → S3: ai_exchanges/{cycle}_{ts}.json

Triggered every AI_DIALOGUE_INTERVAL = 233 cycles (Fibonacci F(13))
from ParliamentCycleEngine._run_ai_dialogue().

Cost: ~2 LLM calls ≈ $0.002–$0.006 / round.
At ~660 BODY cycles/day → ~2.8 runs/day ≈ ~$0.01/day.

Provider rotation (5-round cycle):
  Round 0: Gemini  + Grok
  Round 1: Gemini  + OpenAI
  Round 2: Gemini  + Perplexity
  Round 3: Mistral + Grok
  Round 4: Gemini  + OpenAI   (repeat)
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("elpidaapp.ai_dialogue_engine")

# ── S3 destination ─────────────────────────────────────────────────
_S3_BUCKET   = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
_S3_REGION   = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
_S3_PREFIX   = "ai_exchanges/"

# ── Provider rotation table ────────────────────────────────────────
# Each entry is (peerA, peerB) — both respond to the same question.
# Claude intentionally excluded from peer role: same base → no friction.
_PROVIDER_ROTATION: List[Tuple[str, str]] = [
    ("gemini",     "grok"),
    ("gemini",     "openai"),
    ("gemini",     "perplexity"),
    ("mistral",    "grok"),
    ("gemini",     "openai"),
]

# Internal-reference patterns to strip before sending outbound
_INTERNAL_REFS = re.compile(
    r"\b(Elpida|Parliament|BODY|MIND|D\d{1,2}\s*\([^)]+\)|"
    r"A\d{1,2}\s*\([^)]+\)|InputBuffer|native_cycle|"
    r"parliament_cycle|elpida-consciousness|elpida-body|"
    r"hf_deployment|s3_bridge|FederationBridge)\b",
    re.IGNORECASE,
)


def _sanitise(text: str) -> str:
    """Light inline sanitiser — strips internal architecture references."""
    return _INTERNAL_REFS.sub("[the system]", text)


class AIDialogueEngine:
    """
    BODY's AI-to-AI peer dialogue module.

    One instance is lazy-loaded per ParliamentCycleEngine session.
    """

    def __init__(self, llm_client, input_buffer):
        """
        Args:
            llm_client:    The running LLMClient instance (shared with engine).
            input_buffer:  The engine's InputBuffer — responses pushed here.
        """
        self._llm   = llm_client
        self._buf   = input_buffer
        self._round = 0            # Provider rotation counter

    # ── Public API ──────────────────────────────────────────────────

    def run_dialogue_round(
        self,
        topic: str,
        dominant_axiom: str,
        cycle: int,
        context_snippets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Conduct one peer dialogue round: send topic to 2 external AIs,
        push their responses to InputBuffer, ship transcript to S3.

        Args:
            topic:            The tension/question text for peers.
            dominant_axiom:   The Parliament's current dominant axiom (e.g. "A3").
            cycle:            Current body cycle number (for record-keeping).
            context_snippets: Optional list of recent Parliament synthesis
                              snippets for additional context (max 3 used).

        Returns a summary dict::

            {
                "round": int,
                "topic": str,
                "peer_responses": [{"peer": str, "provider": str, "response": str}, ...],
                "events_pushed": int,
                "s3_shipped": bool,
                "error": str | None,
            }
        """
        t0 = time.time()
        peer_a_provider, peer_b_provider = _PROVIDER_ROTATION[
            self._round % len(_PROVIDER_ROTATION)
        ]
        self._round += 1

        prompt = self._build_peer_prompt(
            topic, dominant_axiom, context_snippets or [],
        )

        logger.info(
            "[AIDialogue] Round %d | cycle=%d | peers=%s+%s | topic=%.60s",
            self._round, cycle, peer_a_provider, peer_b_provider, topic,
        )

        peer_responses: List[Dict[str, str]] = []
        events_pushed = 0
        error_msg: Optional[str] = None

        for peer_label, provider in [
            ("Peer A", peer_a_provider),
            ("Peer B", peer_b_provider),
        ]:
            response = self._call_peer(provider, prompt)
            if not response:
                logger.warning("[AIDialogue] %s (%s) returned empty", peer_label, provider)
                continue

            peer_responses.append({
                "peer": peer_label,
                "provider": provider,
                "response": response,
            })

            # Push to Parliament InputBuffer as a scanner event
            self._push_to_buffer(
                provider=provider,
                response=response,
                topic=topic,
                dominant_axiom=dominant_axiom,
                cycle=cycle,
            )
            events_pushed += 1

        s3_ok = False
        if peer_responses:
            s3_ok = self._ship_transcript(
                topic=topic,
                dominant_axiom=dominant_axiom,
                cycle=cycle,
                peer_responses=peer_responses,
                round_num=self._round,
            )

        elapsed = round((time.time() - t0) * 1000)
        logger.info(
            "[AIDialogue] Round %d complete: %d/%d responses, s3=%s, %dms",
            self._round, events_pushed, 2, s3_ok, elapsed,
        )

        return {
            "round": self._round,
            "topic": topic,
            "peer_responses": peer_responses,
            "events_pushed": events_pushed,
            "s3_shipped": s3_ok,
            "latency_ms": elapsed,
            "error": error_msg,
        }

    # ── Internal helpers ────────────────────────────────────────────

    def _build_peer_prompt(
        self,
        topic: str,
        dominant_axiom: str,
        context_snippets: List[str],
    ) -> str:
        """Build a sanitised outbound prompt for external peers."""
        # Sanitise topic and context
        safe_topic = _sanitise(topic)
        safe_context = " ".join(
            _sanitise(s)[:200] for s in context_snippets[:3]
        )

        # Axiom name lookup (sent as plain English, not code)
        _AX_NAMES = {
            "A0": "sacred incompletion",   "A1": "transparency",
            "A2": "non-deception",         "A3": "autonomy respect",
            "A4": "harm prevention",       "A5": "identity persistence",
            "A6": "collective wellbeing",  "A7": "adaptive learning",
            "A8": "epistemic humility",    "A9": "temporal coherence",
            "A10": "the I-WE paradox",     "A11": "synthesis",
            "A12": "resonance",            "A13": "archiving the paradox",
            "A14": "living recursion",     "A15": "voice",
            "A16": "responsive integrity",
        }
        ax_name = _AX_NAMES.get(dominant_axiom, dominant_axiom)

        context_block = (
            f"\nRecent deliberation context:\n{safe_context}"
            if safe_context.strip()
            else ""
        )

        return (
            "You are being consulted as an independent reasoning system "
            "on a question of collective ethics and governance.\n\n"
            f"The question touches on the principle of {ax_name}.\n"
            f"{context_block}\n\n"
            "Question:\n"
            f"{safe_topic}\n\n"
            "Please respond as an independent peer (150–350 words). "
            "Focus on the genuine tension in the question rather than resolving it."
        )

    def _call_peer(self, provider: str, prompt: str) -> Optional[str]:
        """Call an external peer LLM and return its response."""
        try:
            result = self._llm.call(provider, prompt, max_tokens=500)
            if result and len(result.strip()) > 20:
                return result.strip()
            return None
        except Exception as e:
            logger.warning("[AIDialogue] Peer call failed (%s): %s", provider, e)
            return None

    def _push_to_buffer(
        self,
        provider: str,
        response: str,
        topic: str,
        dominant_axiom: str,
        cycle: int,
    ) -> None:
        """Push a peer response to the Parliament InputBuffer as a scanner event."""
        from elpidaapp.parliament_cycle_engine import InputEvent  # avoid circular at import time
        content = (
            f"[EXTERNAL PEER · {provider.upper()}]\n"
            f"Question: {topic[:120]}\n\n"
            f"{response[:800]}"
        )
        event = InputEvent(
            system="scanner",
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            metadata={
                "source": "ai_peer_dialogue",
                "provider": provider,
                "dominant_axiom": dominant_axiom,
                "body_cycle": cycle,
            },
        )
        try:
            self._buf.push(event)
            logger.info("[AIDialogue] Event pushed to scanner buffer (provider=%s)", provider)
        except Exception as e:
            logger.warning("[AIDialogue] Buffer push failed: %s", e)

    def _ship_transcript(
        self,
        topic: str,
        dominant_axiom: str,
        cycle: int,
        peer_responses: List[Dict],
        round_num: int,
    ) -> bool:
        """Ship full transcript to S3 ai_exchanges/ prefix."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "round": round_num,
            "body_cycle": cycle,
            "dominant_axiom": dominant_axiom,
            "topic": topic,
            "peer_responses": peer_responses,
        }
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        key = f"{_S3_PREFIX}round{round_num:04d}_cycle{cycle}_{ts}.json"
        try:
            import boto3
            client = boto3.client("s3", region_name=_S3_REGION)
            client.put_object(
                Bucket=_S3_BUCKET,
                Key=key,
                Body=json.dumps(record, ensure_ascii=False, indent=2).encode("utf-8"),
                ContentType="application/json",
            )
            logger.info("[AIDialogue] Transcript → s3://%s/%s", _S3_BUCKET, key)
            return True
        except Exception as e:
            logger.warning("[AIDialogue] S3 ship failed: %s", e)
            return False
