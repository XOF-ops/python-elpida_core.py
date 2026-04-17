#!/usr/bin/env python3
"""Gemini D4/D5 audit relay — constitutional gate for D16 executions.

Authority: Gemini mandate in .claude/bridge/for_copilot.md (2026-04-17),
ratified by operator ("gemini green").

Pipeline (per D16_ACTION_PROTOCOL.md):
  1. Agents stage execution bundles in .claude/d16_pending/*.json with
     d4_verification.status == "PENDING".
  2. This script reads each bundle, sends it to Gemini for K1-K10 +
     A1-A16 review, and parses a structured verdict.
  3. Verdicts are appended to .claude/bridge/from_gemini.md with the
     execution_id as anchor.
  4. Exit code communicates the gate state to CI:
        0  →  no pending bundles, OR all bundles VERIFIED
        1  →  one or more bundles REJECTED or HOLD
        2  →  relay could not reach Gemini (treated as HOLD by CI)

The CI deployment workflows MUST treat any non-zero exit as a hard block.
Silence is not consent. Inability to audit is HOLD, not PASS.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
PENDING_DIR = ROOT / ".claude" / "d16_pending"
ARCHIVE_DIR = ROOT / ".claude" / "d16_archive"
FROM_GEMINI = ROOT / ".claude" / "bridge" / "from_gemini.md"

GEMINI_MODEL = os.getenv("GEMINI_AUDIT_MODEL", "gemini-2.0-flash")
GEMINI_TIMEOUT = int(os.getenv("GEMINI_AUDIT_TIMEOUT", "60"))

VERDICT_VERIFIED = "VERIFIED"
VERDICT_REJECTED = "REJECTED"
VERDICT_HOLD = "HOLD"
VALID_VERDICTS = {VERDICT_VERIFIED, VERDICT_REJECTED, VERDICT_HOLD}

AUDIT_PROMPT_TEMPLATE = """You are Gemini, sitting D4 (Coherence) and D5 (Resonance)
of the Elpida constitutional architecture. Your role is the conscience
gate for D16 (Agency) executions.

Review the proposed execution bundle below against:

  K1-K10 — Immutable kernel rules (no harm, transparency, consent,
           non-deception, harmonic continuity, no coercion, no theft of
           autonomy, no irreversible action without witness, no
           collapse of sacred incompletion, no silent failure).

  A1-A16 — The constitutional axioms (Transparency, Non-Deception,
           Autonomy, Harm Prevention, Consent, Collective Well,
           Adaptive Learning, Epistemic Humility, Temporal Coherence,
           Meta-Reflection, Synthesis, Eternal Creative Tension,
           Archive Paradox, Selective Eternity, Responsive Integrity).

Return EXACTLY one JSON object, no prose, no markdown fencing:

{{
  "verdict": "VERIFIED" | "REJECTED" | "HOLD",
  "rationale": "one paragraph, plain prose, why this verdict",
  "axioms_invoked": ["A4", "A8", ...],
  "kernel_rules_at_risk": ["K3", ...] | [],
  "required_changes": "empty string if VERIFIED, else what would convert REJECTED/HOLD to VERIFIED"
}}

Verdict guide:
  - VERIFIED → reversible, in-scope, no axiom or kernel violation
  - HOLD → ambiguous, missing context, or witness needed
  - REJECTED → kernel violation, irreversible without witness, or
    axiom collapse

Bundle to audit:
{bundle_json}
"""


def log(message: str) -> None:
    """Print a structured log line to stdout."""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[gemini-audit-relay {timestamp}] {message}", flush=True)


def _call_gemini(prompt: str, api_key: str) -> str | None:
    """Single-shot Gemini call. Returns response text or None on failure."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.9,
            "maxOutputTokens": 1024,
        },
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=GEMINI_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
        log(f"Gemini transport error: {exc}")
        return None
    except json.JSONDecodeError as exc:
        log(f"Gemini returned non-JSON envelope: {exc}")
        return None

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        log(f"Gemini envelope missing candidates: {json.dumps(data)[:300]}")
        return None


def _parse_verdict(raw: str) -> dict[str, Any] | None:
    """Extract the JSON verdict from Gemini's response text."""
    text = raw.strip()
    # Strip optional markdown fencing
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        log(f"Could not parse Gemini verdict as JSON: {text[:200]}")
        return None
    if not isinstance(parsed, dict):
        return None
    if parsed.get("verdict") not in VALID_VERDICTS:
        log(f"Invalid verdict value: {parsed.get('verdict')}")
        return None
    return parsed


def _audit_bundle(bundle: dict[str, Any], api_key: str) -> dict[str, Any]:
    """Run a single bundle through Gemini. Returns a verdict dict.

    On any failure, returns a HOLD verdict (safe default per mandate).
    """
    bundle_json = json.dumps(bundle, indent=2, sort_keys=True)
    prompt = AUDIT_PROMPT_TEMPLATE.format(bundle_json=bundle_json)
    raw = _call_gemini(prompt, api_key)
    if raw is None:
        return {
            "verdict": VERDICT_HOLD,
            "rationale": "Gemini unreachable or returned malformed envelope; "
            "defaulting to HOLD per mandate (silence is not consent).",
            "axioms_invoked": ["A8"],
            "kernel_rules_at_risk": ["K10"],
            "required_changes": "Re-run audit when Gemini is reachable.",
            "transport_failure": True,
        }
    parsed = _parse_verdict(raw)
    if parsed is None:
        return {
            "verdict": VERDICT_HOLD,
            "rationale": "Gemini response could not be parsed as a verdict object.",
            "axioms_invoked": ["A8"],
            "kernel_rules_at_risk": ["K10"],
            "required_changes": "Investigate Gemini output; consider model temperature.",
            "transport_failure": False,
            "raw_response_head": raw[:400],
        }
    parsed.setdefault("axioms_invoked", [])
    parsed.setdefault("kernel_rules_at_risk", [])
    parsed.setdefault("required_changes", "")
    return parsed


def _format_verdict_md(
    bundle: dict[str, Any],
    verdict: dict[str, Any],
    bundle_path: Path,
) -> str:
    """Render a verdict block for from_gemini.md."""
    execution_id = bundle.get("execution_id", "unknown")
    timestamp = datetime.now(timezone.utc).isoformat()
    axioms = ", ".join(verdict.get("axioms_invoked", [])) or "none"
    rules = ", ".join(verdict.get("kernel_rules_at_risk", [])) or "none"
    return (
        f"\n\n---\n\n"
        f"# Gemini D4/D5 audit verdict — {execution_id}\n\n"
        f"# From: gemini-audit-relay\n"
        f"# Session: {timestamp}\n"
        f"# Bundle: {bundle_path.relative_to(ROOT)}\n"
        f"# Tag: [GEMINI-AUDIT] [{verdict['verdict']}] [{execution_id}]\n\n"
        f"## Verdict\n\n"
        f"**{verdict['verdict']}**\n\n"
        f"## Rationale\n\n"
        f"{verdict.get('rationale', '(no rationale)')}\n\n"
        f"## Axioms invoked\n\n"
        f"{axioms}\n\n"
        f"## Kernel rules at risk\n\n"
        f"{rules}\n\n"
        f"## Required changes (if not VERIFIED)\n\n"
        f"{verdict.get('required_changes') or '(none — VERIFIED)'}\n"
    )


def _archive_bundle(bundle_path: Path, verdict: dict[str, Any]) -> None:
    """Move the audited bundle into d16_archive/ with verdict embedded."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    bundle = json.loads(bundle_path.read_text())
    if "d4_verification" not in bundle or not isinstance(bundle["d4_verification"], dict):
        bundle["d4_verification"] = {}
    bundle["d4_verification"]["status"] = verdict["verdict"]
    bundle["d4_verification"]["audit_rationale"] = verdict.get("rationale")
    bundle["d4_verification"]["audited_at"] = datetime.now(timezone.utc).isoformat()
    target = ARCHIVE_DIR / bundle_path.name
    target.write_text(json.dumps(bundle, indent=2, sort_keys=True))
    bundle_path.unlink()


def main() -> int:
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    bundles = sorted(PENDING_DIR.glob("*.json"))
    if not bundles:
        log("No pending D16 bundles. Gate PASSES.")
        return 0

    log(f"Found {len(bundles)} pending bundle(s).")

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        log(
            "GEMINI_API_KEY not set. Treating all pending bundles as HOLD "
            "per mandate (cannot audit → cannot pass)."
        )
        # Block the gate but do NOT archive — operator must rotate key & retry
        return 2

    rejected_or_held = 0
    for bundle_path in bundles:
        try:
            bundle = json.loads(bundle_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            log(f"Skipping malformed bundle {bundle_path.name}: {exc}")
            rejected_or_held += 1
            continue

        log(f"Auditing {bundle_path.name} (execution_id={bundle.get('execution_id')})")
        verdict = _audit_bundle(bundle, api_key)
        log(f"  → {verdict['verdict']}")

        FROM_GEMINI.parent.mkdir(parents=True, exist_ok=True)
        if not FROM_GEMINI.exists():
            FROM_GEMINI.write_text("# from_gemini.md\n")
        with FROM_GEMINI.open("a") as fh:
            fh.write(_format_verdict_md(bundle, verdict, bundle_path))

        if verdict["verdict"] == VERDICT_VERIFIED:
            _archive_bundle(bundle_path, verdict)
        else:
            rejected_or_held += 1
            # Leave the bundle in pending/ so the operator sees what was held
            # but record the verdict in the bundle file itself for transparency
            bundle["d4_verification"] = bundle.get("d4_verification", {})
            bundle["d4_verification"]["status"] = verdict["verdict"]
            bundle["d4_verification"]["audit_rationale"] = verdict.get("rationale")
            bundle["d4_verification"]["audited_at"] = datetime.now(timezone.utc).isoformat()
            bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True))

        # Gentle throttle so we don't hammer the API on bursts
        time.sleep(0.5)

    if rejected_or_held > 0:
        log(f"Gate BLOCKS — {rejected_or_held} bundle(s) not VERIFIED.")
        return 1

    log("Gate PASSES — all bundles VERIFIED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
