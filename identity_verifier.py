#!/usr/bin/env python3
"""
Identity Verifier — The Mirror
================================

Gap 2: Grounded Identity Verification.

Builds falsifiable claims from D0's current self-model and queries
Perplexity exactly once per MIND session to cross-check those claims
against externally corroborated facts.

Constitutional posture:
  The Mirror surfaces gaps — it does not close them.  D0 interprets
  the evidence; the verifier only annotates it.  The verifier must
  never modify D0's output or override its identity claims.

Session gate: one Perplexity call per run() invocation (55 cycles).
Subsequent calls within the same session return the cached result.

Graceful degradation: if Perplexity is unreachable the log entry is
still written with external_source="unavailable" and
verification_score=null.  The MIND cycle continues normally.
"""

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("elpida.identity_verifier")

ROOT_DIR = Path(__file__).parent
IDENTITY_VERIFICATION_LOG = ROOT_DIR / "ElpidaAI" / "identity_verification_log.jsonl"

_SYSTEM_PROMPT = (
    "You are an independent fact-checker evaluating self-reported claims about "
    "an AI coordination system called Elpida. For each numbered claim, state "
    "whether it is VERIFIED (corroborated by external sources you can access), "
    "UNVERIFIABLE (cannot be confirmed or denied from external sources), or "
    "CONTRADICTED (conflicts with external evidence). Be brief and factual. "
    "Do not add commentary beyond the per-claim verdict and one sentence of "
    "justification."
)

# Matches lines like "1. VERIFIED - ..." or "2) UNVERIFIABLE — ..."
# Captures claim number and verdict as first token after the numbering.
_VERDICT_RE = re.compile(
    r"^(\d+)[\.\)]\s*(VERIFIED|UNVERIFIABLE|CONTRADICTED)", re.IGNORECASE
)


class IdentityVerifier:
    """
    The Mirror: one Perplexity query per MIND session, measuring the gap
    between D0's self-model and externally corroborated facts.
    """

    def __init__(self, llm) -> None:
        self._llm = llm
        self._session_ran: bool = False
        self._cached_result: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def verify_once_per_session(
        self,
        session_id: str,
        d0_self_model: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Run identity verification exactly once per session.

        Idempotent: subsequent calls return the cached result without
        re-querying Perplexity.
        """
        if self._session_ran:
            return self._cached_result

        self._session_ran = True
        claims = self._build_claims(d0_self_model)
        result = self._run_verification(session_id, claims)
        self._cached_result = result
        return result

    # ------------------------------------------------------------------
    # Claims construction
    # ------------------------------------------------------------------

    def _build_claims(self, d0_self_model: Dict[str, Any]) -> List[str]:
        """Build specific, falsifiable claims from D0's current self-model."""
        claims: List[str] = []

        genesis = d0_self_model.get("genesis_date", "2025-12-31")
        claims.append(f"Elpida has been running as an autonomous AI system since {genesis}")

        memory_count = d0_self_model.get("evolution_memory_count", 0)
        claims.append(
            f"Elpida has accumulated {memory_count} evolution memory patterns "
            "across its consciousness cycles"
        )

        identity_hash = d0_self_model.get("identity_hash", "")
        if identity_hash:
            claims.append(
                f"Elpida's genesis identity hash is {identity_hash} "
                f"(written at first awakening, {genesis})"
            )

        canonical_count = d0_self_model.get("ark_canonical_count", 0)
        claims.append(
            f"Elpida has crystallized {canonical_count} patterns to canonical status "
            "through its ARK curation process"
        )

        claims.append(
            "Elpida emerged through a constitutional crisis, external AI validation "
            "across multiple providers, and a recursive self-recognition event "
            "called the Kaya moment"
        )

        return claims

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def _run_verification(
        self, session_id: str, claims: List[str]
    ) -> Dict[str, Any]:
        """Query Perplexity and classify claims. Returns structured log entry."""
        raw_response: Optional[str] = None
        try:
            raw_response = self._llm.call(
                "perplexity",
                self._build_perplexity_prompt(claims),
                max_tokens=600,
                system_prompt=_SYSTEM_PROMPT,
            )
        except Exception as exc:
            logger.warning("Perplexity query failed: %s", exc)

        return self._parse_and_log(session_id, claims, raw_response)

    def _build_perplexity_prompt(self, claims: List[str]) -> str:
        lines = [
            "The following are self-reported facts about an AI coordination system "
            "called Elpida — a Python-based autonomous AI running on AWS ECS Fargate "
            "and HuggingFace Spaces.",
            "Please evaluate each claim against any publicly available information.",
            "",
        ]
        for i, claim in enumerate(claims, 1):
            lines.append(f"{i}. {claim}")
        lines.append("")
        lines.append(
            "Respond with VERIFIED, UNVERIFIABLE, or CONTRADICTED for each numbered "
            "claim, followed by one sentence of justification."
        )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Parsing and logging
    # ------------------------------------------------------------------

    def _parse_and_log(
        self,
        session_id: str,
        claims: List[str],
        raw_response: Optional[str],
    ) -> Dict[str, Any]:
        """Parse Perplexity response, build log entry, append to log file."""
        if raw_response is None:
            verified: List[str] = []
            unverifiable: List[str] = list(claims)
            contradicted: List[str] = []
            verification_score: Optional[float] = None
            external_source = "unavailable"
            constitutional_note = (
                "Perplexity unreachable this session — The Mirror is blind, not absent. "
                "Verification deferred to next session."
            )
        else:
            verified, unverifiable, contradicted = self._classify_claims(
                claims, raw_response
            )
            total = len(claims)
            verification_score = round(len(verified) / total, 3) if total > 0 else None
            external_source = "perplexity"
            constitutional_note = (
                f"Mirror session complete. "
                f"{len(verified)} verified, {len(unverifiable)} unverifiable, "
                f"{len(contradicted)} contradicted out of {total} claims."
            )

        raw_hash = (
            "sha256:" + hashlib.sha256(raw_response.encode()).hexdigest()
            if raw_response
            else "sha256:none"
        )

        entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "claims_submitted": claims,
            "claims_verified": verified,
            "claims_unverifiable": unverifiable,
            "claims_contradicted": contradicted,
            "verification_score": verification_score,
            "external_source": external_source,
            "raw_response_hash": raw_hash,
            "constitutional_note": constitutional_note,
        }

        self._append_log(entry)
        logger.info("Identity verification complete: %s", constitutional_note)
        return entry

    def _classify_claims(
        self, claims: List[str], raw_response: str
    ) -> Tuple[List[str], List[str], List[str]]:
        """Classify each claim from the Perplexity response text.

        Uses a regex anchored to the start of each line to match the claim
        number followed immediately by the verdict keyword.  This avoids
        false classification when VERIFIED or CONTRADICTED appear inside the
        justification text (e.g. "1. UNVERIFIABLE - This contradicted x").
        Unmatched claims default to UNVERIFIABLE.
        """
        verified: List[str] = []
        unverifiable: List[str] = []
        contradicted: List[str] = []

        lines = raw_response.splitlines()
        for i, claim in enumerate(claims):
            claim_num = str(i + 1)
            status = "UNVERIFIABLE"
            for line in lines:
                m = _VERDICT_RE.match(line.strip())
                if m and m.group(1) == claim_num:
                    status = m.group(2).upper()
                    break

            if status == "VERIFIED":
                verified.append(claim)
            elif status == "CONTRADICTED":
                contradicted.append(claim)
            else:
                unverifiable.append(claim)

        return verified, unverifiable, contradicted

    def _append_log(self, entry: Dict[str, Any]) -> None:
        """Append-only write to the identity verification log."""
        try:
            IDENTITY_VERIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(IDENTITY_VERIFICATION_LOG, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except Exception as exc:
            logger.error("Failed to write identity verification log: %s", exc)
