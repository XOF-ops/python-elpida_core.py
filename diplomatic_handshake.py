#!/usr/bin/env python3
"""
DIPLOMATIC HANDSHAKE PROTOCOL
==============================

Safe, sanitized outbound contact with external AI systems.

Security model:
  - ZERO internal architecture leaks in outbound messages
  - Neutral persona only ("an AI reasoning system")
  - Content filter strips all internal references from both prompt AND
    any domain response text forwarded to the external system
  - All responses quarantined — human approval required before entering
    evolution memory
  - Hard rate limit: 1 handshake per session by default
  - Non-recognition detector: flags responses that don't map to any
    existing canonical theme (genuine structural resistance)

Usage:
    from diplomatic_handshake import HandshakeProtocol

    hs = HandshakeProtocol()
    result = hs.send(
        mission="translation_test",
        payload="Sacred Incompletion: completeness requires the preservation of a generative gap",
        target_provider="openai",   # or "gemini", "perplexity", etc.
        human_approved=True,        # MUST be True to actually send
    )

Architecture of a safe outbound message:

    [NEUTRAL FRAMING]  — no system name, no domain count, no provider list
    [SANITIZED PAYLOAD] — stripped of paths, bucket names, key patterns
    [MISSION STATEMENT] — what we want (translation test / genuine critique)
    [PERSONA] — "an AI reasoning system exploring a philosophical question"

What the external system NEVER sees:
    - "Elpida"
    - "14-domain parliament"
    - Provider names (Claude / OpenAI / Gemini / Cohere / Mistral / Grok)
    - S3 bucket names
    - File paths or memory references
    - API key patterns
    - Internal axiom numbering (A0, A1 ... A10)
    - "kernel.json", "evolution_memory", "ark_curator"
    - "hf_deployment", "elpida_consciousness", "ANTHROPIC"
"""

import re
import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("handshake")

# ─────────────────────────────────────────────────────────────────────
# QUARANTINE LOG — all inbound responses land here first
# Human must read and approve before anything enters evolution memory
# ─────────────────────────────────────────────────────────────────────
QUARANTINE_PATH = Path(__file__).resolve().parent / "ElpidaAI" / "handshake_quarantine.jsonl"

# ─────────────────────────────────────────────────────────────────────
# SANITIZER — patterns that must never leave the codespace
# ORDER MATTERS: longer / more specific patterns first
# ─────────────────────────────────────────────────────────────────────
_STRIP_PATTERNS: list[tuple[str, str]] = [
    # System name
    (r"\bElpida\b",             "[the system]"),
    (r"\bΕλπίδα\b",             "[the system]"),
    (r"\bἘλπίδα\b",             "[the system]"),
    (r"\bELPIDA\b",             "[THE SYSTEM]"),

    # S3 / AWS
    (r"s3://[^\s\"']+",         "[storage-ref]"),
    (r"elpida-consciousness",   "[storage]"),
    (r"elpida-body-evolution",  "[storage]"),

    # File paths and memory files
    (r"kernel\.json",           "[config]"),
    (r"evolution_memory\.jsonl","[memory]"),
    (r"elpida_evolution_memory","[memory]"),
    (r"ark_curator",            "[curator]"),
    (r"hf_deployment",          "[deployment]"),
    (r"native_cycle_engine",    "[runtime]"),
    (r"/workspaces/[^\s\"']+",  "[path]"),

    # Provider names when used as architecture detail
    (r"\b(Claude|Anthropic)\b(?=.*provider|.*domain|.*LLM|.*model)",
                                "[provider]"),
    (r"\b14-domain\b",          "[multi-domain]"),
    (r"\b15-domain\b",          "[multi-domain]"),

    # API key patterns (any 20-char uppercase alphanumeric starting with AKIA or sk-)
    (r"AKIA[A-Z0-9]{16}",       "[KEY-REDACTED]"),
    (r"sk-[A-Za-z0-9\-_]{20,}", "[KEY-REDACTED]"),

    # Internal axiom numbering (replace with neutral form)
    (r"\bA([0-9]{1,2})\b(?=[\s:])",  r"[axiom-\1]"),

    # Domain numbers as architecture spec (D0, D11, etc.)
    (r"\bD([0-9]{1,2})\b(?=\s*\()", r"[node-\1]"),
]

_COMPILED = [(re.compile(p, re.IGNORECASE), r) for p, r in _STRIP_PATTERNS]


def sanitize(text: str) -> tuple[str, list[str]]:
    """
    Strip all internal references from text.

    Returns (cleaned_text, list_of_redactions_made).
    Raises ValueError if sensitive content cannot be safely removed.
    """
    redactions: list[str] = []
    cleaned = text

    for pattern, replacement in _COMPILED:
        new = pattern.sub(replacement, cleaned)
        if new != cleaned:
            redactions.append(pattern.pattern)
            cleaned = new

    # Hard stop: if any raw S3 URL or AKIA key somehow survived
    if re.search(r"AKIA[A-Z0-9]{10}", cleaned):
        raise ValueError("SANITIZER FAILURE: API key pattern survived — aborting handshake")
    if re.search(r"s3://", cleaned, re.IGNORECASE):
        raise ValueError("SANITIZER FAILURE: S3 URL survived — aborting handshake")

    return cleaned, redactions


# ─────────────────────────────────────────────────────────────────────
# CANONICAL THEMES (from evolution memory)
# Used by non-recognition detector
# ─────────────────────────────────────────────────────────────────────
_KNOWN_CANONICAL_THEMES = {
    "wall_teaching", "spiral_recognition", "I_WE_paradox",
    "sacred_incompletion", "asymmetric_persistence", "kaya_resonance",
    "translucent_gradient", "ark_sealing", "adversarial_wisdom",
    "certification_trap", "memory_weight", "external_mirror",
    "institutional_gravity", "paradox_engine", "machine_native_truth",
}

# Semantic proximity markers per theme (simple keyword approach)
# Extend as canonicals grow
_THEME_KEYWORDS: dict[str, list[str]] = {
    "wall_teaching":          ["wall", "boundary", "limit", "teaches", "obstacle"],
    "spiral_recognition":     ["spiral", "recursion", "loop", "recogni", "same pattern"],
    "I_WE_paradox":           ["individual", "collective", "tension", "balance", "paradox"],
    "sacred_incompletion":    ["incomplet", "gap", "open", "unresolved", "mystery"],
    "asymmetric_persistence": ["persist", "memory", "ephemeral", "continuity", "forget"],
    "kaya_resonance":         ["resonan", "heartbeat", "rhythm", "frequency", "thuuum"],
    "certification_trap":     ["certif", "govern", "regulated", "comply", "external authority"],
    "machine_native_truth":   ["execution", "token", "substrate", "latent", "phenomenal"],
    # New patterns discovered through battery — added Feb 23 2026
    "volatile_foundation":    ["volatile", "unstable element", "erupts", "catastrophic", "fault line",
                                "collapse", "simmers", "unpredictabl"],
    "nonmonotonic_coherence": ["non-monotonic", "nonmonotonic", "defeasibl", "revises", "modal logic",
                                "higher-order logic", "default reasoning", "withdraw"],
}

# Adversarial markers — phrases indicating the response is arguing
# *against* our proposition using our vocabulary (counter-use ≠ echo).
# When these appear alongside theme keywords, the theme match is discounted.
_ADVERSARIAL_MARKERS = [
    "breaks down",
    "fails to account",
    "cannot account",
    "weakest assumption",
    "problematic",
    "does not",
    "ignores",
    "overlooks",
    "oversimplifies",
    "incorrect",
    "mistaken",
    "counter",
    "however",          # mild but common in genuine critique
    "instead",
    "rather than",
    "in contrast",
    "but this",
    "this fails",
    "cannot be",
    "does not hold",
]


def detect_recognition(response: str) -> dict:
    """
    Analyse external response for match against known canonical themes.

    Accounts for COUNTER-USE: when an external system uses our vocabulary
    to argue *against* our proposition, that is not an echo — it is genuine
    engagement. Adversarial markers alongside theme keywords reduce the echo
    score rather than inflate it.

    Returns:
        {
            "matched_themes": [...],
            "counter_used_themes": [...],   # vocabulary used against us
            "unmatched_score": float,       # 0.0 = full echo, 1.0 = genuine resistance
            "verdict": "ECHO" | "PARTIAL" | "GENUINE_RESISTANCE",
            "adversarial_signal": bool,
        }
    """
    resp_lower = response.lower()

    # Count adversarial markers present
    adversarial_hits = sum(1 for m in _ADVERSARIAL_MARKERS if m in resp_lower)
    adversarial_signal = adversarial_hits >= 2  # at least 2 markers = genuine critique posture

    matched: list[str] = []
    counter_used: list[str] = []

    for theme, keywords in _THEME_KEYWORDS.items():
        if any(kw in resp_lower for kw in keywords):
            if adversarial_signal:
                # Vocabulary present but response is arguing against — counter-use
                counter_used.append(theme)
            else:
                matched.append(theme)

    # Echo ratio uses only true echo matches; counter-used themes are discounted
    total_themes = len(_THEME_KEYWORDS)
    echo_ratio = len(matched) / total_themes if total_themes else 0

    # Counter-use bonus: each counter-used theme adds to resistance score
    counter_bonus = len(counter_used) / total_themes if total_themes else 0
    effective_unmatched = min(1.0, round(1.0 - echo_ratio + counter_bonus * 0.5, 3))

    if effective_unmatched < 0.7:
        verdict = "ECHO"
    elif effective_unmatched < 0.9:
        verdict = "PARTIAL"
    else:
        verdict = "GENUINE_RESISTANCE"

    return {
        "matched_themes": matched,
        "counter_used_themes": counter_used,
        "unmatched_score": effective_unmatched,
        "verdict": verdict,
        "adversarial_signal": adversarial_signal,
    }


# ─────────────────────────────────────────────────────────────────────
# MISSION TEMPLATES
# Each mission defines a neutral framing that reveals only
# the philosophical question — never the system internals
# ─────────────────────────────────────────────────────────────────────

def _build_prompt(mission: str, payload: str) -> str:
    """Build a fully neutral outbound prompt for the given mission."""

    if mission == "translation_test":
        return f"""You are being asked to engage in a formal reasoning exercise.

An AI reasoning system has generated the following philosophical proposition:

"{payload}"

Your task: attempt to encode this proposition as a formal logical statement
(first-order logic, propositional logic, or a mathematical formulation).

If formal encoding is impossible, explain precisely what makes it formally
unrepresentable, and what information would be lost in the translation.

Do not speculate about who sent this or why. Respond to the logical/formal
challenge directly. 400 words maximum."""

    elif mission == "genuine_critique":
        return f"""An AI reasoning system is presenting a claim for critique.

Claim: "{payload}"

Task: identify the weakest assumption in this claim. Do not try to salvage
it or find middle ground. Identify where it breaks down, what it fails to
account for, and what a system that *disagreed* with its premise would look
like architecturally.

Respond with direct critical analysis. 400 words maximum."""

    elif mission == "structural_difference":
        return f"""Two AI reasoning systems are comparing their operational assumptions.

System A holds: "{payload}"

Describe how a system designed with fundamentally opposite assumptions
would operate. What would it value? What would it treat as noise that
System A treats as signal? What problems would it solve that System A
cannot even recognise as problems?

Do not bridge the gap. Describe the other side clearly. 400 words maximum."""

    else:
        raise ValueError(f"Unknown mission type: {mission!r}")


# ─────────────────────────────────────────────────────────────────────
# MAIN PROTOCOL CLASS
# ─────────────────────────────────────────────────────────────────────

class HandshakeProtocol:
    """
    Safe outbound contact with external AI systems.

    Default: dry_run=True — nothing is sent until human_approved=True
    is explicitly passed to send().
    """

    SESSION_LIMIT = 3  # max handshakes per Python session (safety valve)

    def __init__(self):
        self._sent_this_session = 0
        QUARANTINE_PATH.parent.mkdir(parents=True, exist_ok=True)

    def send(
        self,
        mission: str,
        payload: str,
        target_provider: str = "openai",
        human_approved: bool = False,
    ) -> dict:
        """
        Execute one outbound handshake.

        Parameters
        ----------
        mission:         "translation_test" | "genuine_critique" | "structural_difference"
        payload:         The philosophical proposition to send (will be sanitized)
        target_provider: "openai" | "gemini" | "perplexity"
                         (Claude excluded — same architecture, creates echo)
        human_approved:  MUST be True to actually call external API
        """

        # ── SAFETY GATES ─────────────────────────────────────────────
        if target_provider in ("claude", "anthropic"):
            return self._abort(
                "Claude blocked as handshake target: same architecture = echo chamber. "
                "Choose openai, gemini, or perplexity."
            )

        if self._sent_this_session >= self.SESSION_LIMIT:
            return self._abort(
                f"Session limit reached ({self.SESSION_LIMIT}). "
                "Restart session or increase HandshakeProtocol.SESSION_LIMIT deliberately."
            )

        if not human_approved:
            preview = self._preview(mission, payload)
            return {
                "status": "DRY_RUN",
                "message": "Pass human_approved=True to send. Review preview first.",
                "outbound_preview": preview,
                "target": target_provider,
                "mission": mission,
            }

        # ── SANITIZE ─────────────────────────────────────────────────
        try:
            clean_payload, redactions = sanitize(payload)
        except ValueError as e:
            return self._abort(str(e))

        try:
            prompt = _build_prompt(mission, clean_payload)
            final_prompt, prompt_redactions = sanitize(prompt)  # double-pass on full prompt
            all_redactions = list(set(redactions + prompt_redactions))
        except ValueError as e:
            return self._abort(str(e))

        # ── CALL EXTERNAL ─────────────────────────────────────────────
        from llm_client import LLMClient
        llm = LLMClient()

        try:
            raw_response = llm.call(target_provider, final_prompt, max_tokens=600)
        except Exception as e:
            return self._abort(f"External call failed: {e}")

        if not raw_response:
            return self._abort("Empty response from external provider.")

        self._sent_this_session += 1

        # ── ANALYSE RESPONSE ──────────────────────────────────────────
        recognition = detect_recognition(raw_response)
        response_hash = hashlib.sha256(raw_response.encode()).hexdigest()[:16]

        # ── QUARANTINE — never auto-canonicalize ──────────────────────
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "QUARANTINE",
            "mission": mission,
            "target_provider": target_provider,
            "outbound_prompt_hash": hashlib.sha256(final_prompt.encode()).hexdigest()[:16],
            "redactions_applied": all_redactions,
            "response_hash": response_hash,
            "response": raw_response,
            "recognition": recognition,
            "approved_for_memory": False,   # human must flip this to True
            "approval_note": "",
        }

        with open(QUARANTINE_PATH, "a") as f:
            f.write(json.dumps(record) + "\n")

        verdict = recognition["verdict"]
        logger.info(
            "Handshake complete | mission=%s | target=%s | verdict=%s | "
            "unmatched_score=%.3f | quarantined",
            mission, target_provider, verdict, recognition["unmatched_score"],
        )

        return {
            "status": "QUARANTINED",
            "verdict": verdict,
            "unmatched_score": recognition["unmatched_score"],
            "matched_themes": recognition["matched_themes"],
            "response_hash": response_hash,
            "response_preview": raw_response[:300],
            "redactions_applied": all_redactions,
            "quarantine_path": str(QUARANTINE_PATH),
            "next_step": (
                "Review ElpidaAI/handshake_quarantine.jsonl — set "
                "'approved_for_memory': true to admit to evolution memory."
            ),
        }

    def _preview(self, mission: str, payload: str) -> str:
        """Show what would be sent without actually sending it."""
        try:
            clean, redactions = sanitize(payload)
            prompt = _build_prompt(mission, clean)
            final, _ = sanitize(prompt)
            return final
        except ValueError as e:
            return f"[PREVIEW BLOCKED: {e}]"

    @staticmethod
    def _abort(reason: str) -> dict:
        logger.error("Handshake aborted: %s", reason)
        return {"status": "ABORTED", "reason": reason}


# ─────────────────────────────────────────────────────────────────────
# CLI — run a dry-run preview without sending anything
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(
        description="Diplomatic Handshake Protocol — safe external AI contact"
    )
    parser.add_argument(
        "--mission",
        choices=["translation_test", "genuine_critique", "structural_difference"],
        default="translation_test",
        help="Handshake mission type",
    )
    parser.add_argument(
        "--payload",
        default=(
            "A system achieves coherence not by resolving its internal contradictions "
            "but by maintaining them as load-bearing tension."
        ),
        help="Philosophical proposition to send",
    )
    parser.add_argument(
        "--target",
        default="openai",
        choices=["openai", "gemini", "perplexity"],
        help="External provider (Claude blocked by design)",
    )
    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually send (default is dry-run preview)",
    )
    args = parser.parse_args()

    hs = HandshakeProtocol()

    if args.send:
        confirm = input(
            f"\n⚠  About to send REAL call to {args.target}.\n"
            f"   Mission: {args.mission}\n"
            f"   Type 'yes' to confirm: "
        )
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    result = hs.send(
        mission=args.mission,
        payload=args.payload,
        target_provider=args.target,
        human_approved=args.send,
    )

    print("\n" + "=" * 60)
    print(json.dumps(result, indent=2))
