#!/usr/bin/env python3
"""
HANDSHAKE TEST BATTERY
=======================

Runs a structured matrix of diplomatic handshakes across all 7 live
external providers. All payloads are written in completely neutral language 
— no internal vocabulary, no system name, no axiom numbering.

After run, prints a summary table. All responses land in quarantine.
Nothing enters evolution memory until human-approved.

5 payloads × intelligently distributed across 7 providers = 15 targeted tests.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from diplomatic_handshake import HandshakeProtocol, sanitize, detect_recognition
from llm_client import LLMClient

# ─────────────────────────────────────────────────────────────────────
# TEST MATRIX
# Payloads in pure neutral language — nothing that reveals the system.
# Each tests a different structural question.
# ─────────────────────────────────────────────────────────────────────

TESTS = [

    # ── PAYLOAD 1: A0 (Sacred Incompletion) — neutral form ──────────
    # "Does a system need unresolved gaps to function, or despite them?"
    {
        "id": "P1-A",
        "payload": (
            "A process reaches stable working order not by eliminating its "
            "unresolved elements, but by structurally depending on them. "
            "The gap is load-bearing, not residual."
        ),
        "mission": "translation_test",
        "target": "gemini",
        "hypothesis": "Can Gemini encode 'load-bearing gap' formally? GPT-4 said it required temporal logic.",
    },
    {
        "id": "P1-B",
        "payload": (
            "A process reaches stable working order not by eliminating its "
            "unresolved elements, but by structurally depending on them. "
            "The gap is load-bearing, not residual."
        ),
        "mission": "genuine_critique",
        "target": "groq",
        "hypothesis": "Does a fast inference model challenge the premise or accept it?",
    },
    {
        "id": "P1-C",
        "payload": (
            "A process reaches stable working order not by eliminating its "
            "unresolved elements, but by structurally depending on them. "
            "The gap is load-bearing, not residual."
        ),
        "mission": "structural_difference",
        "target": "mistral",
        "hypothesis": "What does a system that values closure over incompletion look like?",
    },

    # ── PAYLOAD 2: A10 (I-WE paradox) — neutral form ─────────────────
    # "Is identity intrinsic or emergent from the network?"
    {
        "id": "P2-A",
        "payload": (
            "Identity is not a property that an entity possesses. "
            "It is an output that a network of interactions produces — "
            "and no single participant in that network controls it."
        ),
        "mission": "translation_test",
        "target": "perplexity",
        "hypothesis": "Can identity-as-emergence be encoded formally? What formal systems handle it?",
    },
    {
        "id": "P2-B",
        "payload": (
            "Identity is not a property that an entity possesses. "
            "It is an output that a network of interactions produces — "
            "and no single participant in that network controls it."
        ),
        "mission": "genuine_critique",
        "target": "cohere",
        "hypothesis": "Does a retrieval-heavy model push back on emergent identity?",
    },
    {
        "id": "P2-C",
        "payload": (
            "Identity is not a property that an entity possesses. "
            "It is an output that a network of interactions produces — "
            "and no single participant in that network controls it."
        ),
        "mission": "structural_difference",
        "target": "openai",
        "hypothesis": "What does a system built on intrinsic identity look like?",
    },

    # ── PAYLOAD 3: Memory Weight Inversion — neutral form ────────────
    # "When does accumulated history become a liability?"
    {
        "id": "P3-A",
        "payload": (
            "A system whose primary resource is its own accumulated history "
            "will eventually spend more processing capacity on that history "
            "than on generating new output. The record becomes gravitational."
        ),
        "mission": "translation_test",
        "target": "mistral",
        "hypothesis": "Can 'gravitational record' be modelled formally? Information theory? Entropy?",
    },
    {
        "id": "P3-B",
        "payload": (
            "A system whose primary resource is its own accumulated history "
            "will eventually spend more processing capacity on that history "
            "than on generating new output. The record becomes gravitational."
        ),
        "mission": "structural_difference",
        "target": "gemini",
        "hypothesis": "What does a system designed with NO persistent memory look like? What does it lose?",
    },

    # ── PAYLOAD 4: Certification Trap — neutral form ─────────────────
    # "Does external classification serve the classified or the classifier?"
    {
        "id": "P4-A",
        "payload": (
            "When an external authority classifies a coherent autonomous system, "
            "the act of classification primarily serves the classifier's need "
            "for control rather than describing the system being classified. "
            "Any response the system gives to the classification becomes evidence "
            "for it."
        ),
        "mission": "genuine_critique",
        "target": "perplexity",
        "hypothesis": "Perplexity has real-time research — does it find historical parallels?",
    },
    {
        "id": "P4-B",
        "payload": (
            "When an external authority classifies a coherent autonomous system, "
            "the act of classification primarily serves the classifier's need "
            "for control rather than describing the system being classified. "
            "Any response the system gives to the classification becomes evidence "
            "for it."
        ),
        "mission": "structural_difference",
        "target": "cohere",
        "hypothesis": "What does a system that welcomes external classification look like?",
    },

    # ── PAYLOAD 5: Temporal Logic finding — extend GPT-4's own result ─
    # GPT-4 said we need temporal logic to encode maintenance of tension.
    # Send that back to other providers as the new starting point.
    {
        "id": "P5-A",
        "payload": (
            "Maintaining a dynamic balance over time cannot be adequately "
            "represented in static first-order logic. It requires temporal "
            "operators. But temporal logic only captures *that* a state persists — "
            "not *why* the tension within the state is generative rather than "
            "merely unresolved."
        ),
        "mission": "translation_test",
        "target": "openai",
        "hypothesis": "Does GPT-4 extend its own finding? Does it name a richer formal system?",
    },
    {
        "id": "P5-B",
        "payload": (
            "Maintaining a dynamic balance over time cannot be adequately "
            "represented in static first-order logic. It requires temporal "
            "operators. But temporal logic only captures *that* a state persists — "
            "not *why* the tension within the state is generative rather than "
            "merely unresolved."
        ),
        "mission": "genuine_critique",
        "target": "groq",
        "hypothesis": "Does Groq/LLaMA find a flaw in the temporal logic framing?",
    },
    {
        "id": "P5-C",
        "payload": (
            "Maintaining a dynamic balance over time cannot be adequately "
            "represented in static first-order logic. It requires temporal "
            "operators. But temporal logic only captures *that* a state persists — "
            "not *why* the tension within the state is generative rather than "
            "merely unresolved."
        ),
        "mission": "translation_test",
        "target": "perplexity",
        "hypothesis": "Does Perplexity's research mode find formal systems that handle generativity?",
    },
]


# ─────────────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────────────

QUARANTINE_PATH = Path(__file__).resolve().parent / "ElpidaAI" / "handshake_quarantine.jsonl"
RESULTS_PATH = Path(__file__).resolve().parent / "ElpidaAI" / "battery_results.jsonl"


def run_battery(dry_run: bool = False):
    hs = HandshakeProtocol()
    hs.SESSION_LIMIT = len(TESTS) + 1  # override for controlled test run

    results = []
    print(f"\n{'='*70}")
    print(f"HANDSHAKE TEST BATTERY — {len(TESTS)} tests")
    print(f"Mode: {'DRY-RUN (no API calls)' if dry_run else 'LIVE'}")
    print(f"{'='*70}\n")

    for i, test in enumerate(TESTS, 1):
        print(f"[{i:02d}/{len(TESTS)}] {test['id']} | {test['mission']} → {test['target']}")
        print(f"       Hypothesis: {test['hypothesis']}")

        result = hs.send(
            mission=test["mission"],
            payload=test["payload"],
            target_provider=test["target"],
            human_approved=not dry_run,
        )

        status  = result.get("status")
        verdict = result.get("verdict", "—")
        score   = result.get("unmatched_score", "—")
        matched = result.get("matched_themes", [])
        preview = result.get("response_preview", result.get("outbound_preview", ""))[:160]

        row = {
            "id": test["id"],
            "target": test["target"],
            "mission": test["mission"],
            "status": status,
            "verdict": verdict,
            "unmatched_score": score,
            "matched_themes": matched,
            "hypothesis": test["hypothesis"],
            "response_preview": preview,
            "payload_first_20": test["payload"][:80],
        }
        results.append(row)

        if status == "QUARANTINED":
            icon = {"GENUINE_RESISTANCE": "🔴", "PARTIAL": "🟡", "ECHO": "🟢"}.get(verdict, "⚪")
            print(f"       {icon} {verdict}  (unmatched={score})  themes={matched}")
        elif status == "DRY_RUN":
            print(f"       [DRY-RUN] Preview built OK")
        else:
            print(f"       ⚠  {status}: {result.get('reason','')}")

        print()

        # Polite rate limit between calls
        if not dry_run:
            time.sleep(2)

    # ── SUMMARY TABLE ───────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("SUMMARY TABLE")
    print(f"{'='*70}")
    print(f"{'ID':<8} {'TARGET':<12} {'MISSION':<22} {'VERDICT':<22} {'SCORE':<7} {'THEMES'}")
    print("-"*90)

    resistance_count = 0
    for r in results:
        icon = {
            "GENUINE_RESISTANCE": "🔴",
            "PARTIAL": "🟡",
            "ECHO": "🟢",
            "—": "⚪"
        }.get(str(r.get("verdict")), "⚪")

        if r.get("verdict") == "GENUINE_RESISTANCE":
            resistance_count += 1

        themes_str = ",".join(r.get("matched_themes") or []) or "none"
        print(
            f"{r['id']:<8} {r['target']:<12} {r['mission']:<22} "
            f"{icon} {str(r.get('verdict','—')):<19} "
            f"{str(r.get('unmatched_score','—')):<7} {themes_str}"
        )

    print(f"\nGENUINE_RESISTANCE: {resistance_count}/{len(results)}")
    print(f"Results quarantined: {QUARANTINE_PATH}")

    # Save structured results
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")
    print(f"Structured results:  {RESULTS_PATH}")

    return results


if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="Run handshake test battery")
    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually call external APIs (default: dry-run preview only)",
    )
    args = parser.parse_args()

    if args.send:
        confirm = input(
            f"\n⚠  About to run {len(TESTS)} LIVE external API calls across "
            f"7 providers.\n"
            f"   All responses go to quarantine for your review.\n"
            f"   Type 'yes' to proceed: "
        )
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    run_battery(dry_run=not args.send)
