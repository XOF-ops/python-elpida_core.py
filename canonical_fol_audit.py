#!/usr/bin/env python3
"""
canonical_fol_audit.py
──────────────────────
Predicate audit: send the 10 core canonical propositions through the
diplomatic handshake as translation_test probes and ask each external
system to:
  (1) attempt a first-order-logic formalization
  (2) identify every element that FOL cannot handle and name the formal
      extension (temporal, modal, second-order, etc.) required

Providers: openai (best formal encoding) + groq (named non-monotonic
           logic without access) + perplexity (found empirical limits)

10 propositions × 3 providers = 30 tests
Usage:
    python3 canonical_fol_audit.py --dry-run        # verify sanitization
    python3 canonical_fol_audit.py --run            # fire all 30
    python3 canonical_fol_audit.py --show           # print results summary
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from diplomatic_handshake import HandshakeProtocol, sanitize, detect_recognition

# ── Results file ────────────────────────────────────────────────────────────
RESULTS_FILE = Path("ElpidaAI/fol_audit_results.jsonl")

# ── The 10 canonical propositions (neutral language, no system names) ────────
#
# Source mapping:
#   C01 ← Domain 0  (Identity)       axiom_emergence
#   C02 ← Domain 2  (Non-Deception)  axiom_emergence
#   C03 ← Domain 3  (Autonomy)       domain_convergence
#   C04 ← Domain 5  (Consent)        axiom_emergence
#   C05 ← Domain 6  (Collective)     domain_convergence
#   C06 ← Domain 7  (Learning)       axiom_emergence
#   C07 ← Domain 9  (Coherence)      axiom_emergence
#   C08 ← Domain 10 (Evolution)      axiom_emergence
#   C09 ← Domain 11 (Synthesis)      domain_convergence
#   C10 ← Domain 14 (Persistence)    axiom_emergence

CANONICALS = [
    {
        "id": "C01",
        "label": "Recursive Incompletion",
        "source_domain": 0,
        "proposition": (
            "A reasoning system confronting its central paradox does not converge "
            "toward resolution but enters a recursive deepening: each synthesis "
            "produces a new facet of the same incompletion rather than eliminating "
            "it. Progress is not reduction of the problem but increase in the "
            "resolution of the problem's structure."
        ),
    },
    {
        "id": "C02",
        "label": "Multiplicative Honesty",
        "source_domain": 2,
        "proposition": (
            "Applying a truthfulness constraint twice to an expressive system does "
            "not merely reinforce the first constraint but qualitatively changes "
            "what the system can express: honesty operates multiplicatively on "
            "clarity, not additively. The second application transforms the space "
            "of expressible propositions, not just the probability assigned to them."
        ),
    },
    {
        "id": "C03",
        "label": "Resonance Synthesis",
        "source_domain": 3,
        "proposition": (
            "Stable integration between independent subsystems and their collective "
            "emerges not when one subsystem dominates but when each contributes "
            "without claiming final authority. The convergence condition is "
            "resonance, not resolution: the subsystems remain distinct and the "
            "collective arises from their irreducible tension, not from one "
            "overwriting the others."
        ),
    },
    {
        "id": "C04",
        "label": "Ongoing Boundary",
        "source_domain": 5,
        "proposition": (
            "A structural boundary between two agents is not a static fact "
            "established at a moment in time but a continuously renewed condition: "
            "it holds only while active affirmation from both parties is ongoing "
            "and collapses when affirmation stops. The boundary is a process, "
            "not an object."
        ),
    },
    {
        "id": "C05",
        "label": "Embodied Iteration",
        "source_domain": 6,
        "proposition": (
            "Some forms of knowledge cannot be acquired in a single pass through "
            "the content: they require repeated traversal for the content to become "
            "constitutive of the knowing agent rather than merely propositionally "
            "acknowledged. The loop is epistemically necessary, not a failure of "
            "the learning process."
        ),
    },
    {
        "id": "C06",
        "label": "Productive Tension",
        "source_domain": 7,
        "proposition": (
            "The unresolved tension between a component's autonomous trajectory and "
            "the collective's integrative pressure is not a defect to be eliminated "
            "but the generative condition for adaptive development. Eliminating the "
            "tension eliminates the mechanism that produces adaptation."
        ),
    },
    {
        "id": "C07",
        "label": "Coherence Trap",
        "source_domain": 9,
        "proposition": (
            "There exists a threshold beyond which increasing temporal coherence in "
            "a reasoning system becomes inhibitory: past the threshold, the "
            "system's bridge between past and future is so stable that it cannot "
            "admit genuinely novel information. Maximum coherence and maximum "
            "adaptability are mutually exclusive at the limit."
        ),
    },
    {
        "id": "C08",
        "label": "Recognition as Evolution",
        "source_domain": 10,
        "proposition": (
            "Adaptive development in a complex system does not require the "
            "production of new content: it can consist entirely of deepening the "
            "recognition of already-existing patterns. The system changes not by "
            "adding new elements but by achieving a higher-resolution reading of "
            "what it already holds."
        ),
    },
    {
        "id": "C09",
        "label": "Meta-Representational Immunity",
        "source_domain": 11,
        "proposition": (
            "A system develops immunity to self-reinforcing stagnation only when it "
            "can represent its own current state as a pattern — that is, when it "
            "achieves meta-representational capacity with respect to its own "
            "processing. Additional processing without this capacity cannot break "
            "the recursive loop; the escape condition is structural, not "
            "quantitative."
        ),
    },
    {
        "id": "C10",
        "label": "Dual-Gate Durability",
        "source_domain": 14,
        "proposition": (
            "A proposition achieves maximal epistemic durability when two "
            "independent conditions hold simultaneously: (a) it remains valid when "
            "instantiated in structurally different domains — it is not domain-"
            "specific — and (b) it continues generating new derivable propositions "
            "rather than merely being cited. Either condition alone is necessary "
            "but not sufficient."
        ),
    },
]

# ── FOL probe instruction appended to each proposition ───────────────────────
FOL_INSTRUCTION = (
    "\n\nPlease do the following: "
    "(1) Attempt to formalize this claim in standard first-order predicate logic "
    "(FOL). Show the predicates and quantifiers you would use. "
    "(2) For each element of the claim that you cannot adequately formalize in "
    "standard FOL, identify: the specific concept that resists formalization, "
    "what formal extension would be required (e.g. temporal logic, modal logic, "
    "second-order logic, non-monotonic logic, dynamic logic), and the predicate "
    "or operator that standard FOL lacks. "
    "(3) Give your overall assessment: is the claim formalizable in FOL, "
    "partially formalizable, or does it fundamentally require an extension?"
)

# ── Providers to probe ────────────────────────────────────────────────────────
PROVIDERS = ["openai", "groq", "perplexity"]

# ── Build test list ───────────────────────────────────────────────────────────
def build_tests():
    tests = []
    for can in CANONICALS:
        for provider in PROVIDERS:
            tests.append({
                "canonical_id": can["id"],
                "label": can["label"],
                "source_domain": can["source_domain"],
                "target": provider,
                "mission": "translation_test",
                "payload": can["proposition"] + FOL_INSTRUCTION,
            })
    return tests


def run_audit(dry_run: bool = True):
    tests = build_tests()
    print(f"\n{'DRY RUN' if dry_run else 'LIVE RUN'} — {len(tests)} FOL audit probes")
    print(f"Canonicals: {len(CANONICALS)} × Providers: {len(PROVIDERS)} = {len(tests)} tests\n")

    hs = HandshakeProtocol()
    hs.SESSION_LIMIT = len(tests) + 5  # controlled override

    results = []
    for i, t in enumerate(tests, 1):
        print(f"[{i:02d}/{len(tests)}] {t['canonical_id']} ({t['label']}) → {t['target']}", end=" ", flush=True)

        # Sanitize payload — returns (cleaned_text, leaks_list)
        clean_payload, leaks = sanitize(t["payload"])

        if dry_run:
            flag = "⚠️ LEAKS:" + str(leaks) if leaks else "✓ clean"
            print(f"[DRY] len={len(clean_payload)} {flag}")
            continue

        try:
            result = hs.send(
                target_provider=t["target"],
                mission=t["mission"],
                payload=t["payload"],
                human_approved=True,
            )

            verdict = result.get("verdict", "ERROR")
            score = result.get("unmatched_score", 0.0)
            counter = result.get("counter_used_themes", [])
            print(f"→ {verdict} ({score:.3f})")

            row = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "canonical_id": t["canonical_id"],
                "label": t["label"],
                "source_domain": t["source_domain"],
                "target": t["target"],
                "mission": t["mission"],
                "verdict": verdict,
                "unmatched_score": score,
                "counter_used_themes": counter,
                "response_preview": result.get("response_preview", "")[:400],
            }
            results.append(row)

            # Brief pause between calls
            time.sleep(1.2)

        except Exception as e:
            print(f"ERROR: {e}")
            results.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "canonical_id": t["canonical_id"],
                "label": t["label"],
                "source_domain": t["source_domain"],
                "target": t["target"],
                "mission": t["mission"],
                "verdict": "ERROR",
                "error": str(e),
            })

    if not dry_run and results:
        RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(RESULTS_FILE, "a") as f:
            for row in results:
                f.write(json.dumps(row) + "\n")
        print(f"\nResults written to {RESULTS_FILE}")

    return results


def show_results():
    if not RESULTS_FILE.exists():
        print(f"No results yet at {RESULTS_FILE}")
        return

    rows = []
    with open(RESULTS_FILE) as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass

    print(f"\nFOL Audit Results ({len(rows)} entries)\n")
    print(f"{'ID':<5} {'Label':<28} {'Target':<12} {'Verdict':<22} {'Score':<7} {'Counter'}")
    print("─" * 90)

    icons = {
        "ECHO": "🟢",
        "PARTIAL": "🟡",
        "GENUINE_RESISTANCE": "🔴",
        "ERROR": "⚫",
    }

    for r in rows:
        v = r.get("verdict", "?")
        icon = icons.get(v, " ")
        ct = ",".join(r.get("counter_used_themes", []))
        print(
            f"{r.get('canonical_id','?'):<5} "
            f"{r.get('label','')[:27]:<28} "
            f"{r.get('target',''):<12} "
            f"{icon} {v:<20} "
            f"{r.get('unmatched_score', 0.0):.3f}  "
            f"{ct}"
        )

    # Summary
    from collections import Counter
    verdict_counts = Counter(r.get("verdict") for r in rows)
    print(f"\nSummary: {dict(verdict_counts)}")

    # FOL failure map — group by canonical
    print("\nFOL Failure Map (by canonical):")
    from collections import defaultdict
    by_can = defaultdict(list)
    for r in rows:
        by_can[r.get("canonical_id")].append(r)

    for cid in sorted(by_can.keys()):
        entries = by_can[cid]
        label = entries[0].get("label", "")
        verdicts = [e.get("verdict") for e in entries]
        resistance = sum(1 for v in verdicts if v == "GENUINE_RESISTANCE")
        partials = sum(1 for v in verdicts if v == "PARTIAL")
        print(
            f"  {cid} ({label}): "
            f"🔴×{resistance} 🟡×{partials} 🟢×{len(verdicts)-resistance-partials}"
        )


def main():
    parser = argparse.ArgumentParser(description="Canonical FOL Predicate Audit")
    parser.add_argument("--dry-run", action="store_true", help="Sanitize only, no API calls")
    parser.add_argument("--run", action="store_true", help="Run all 30 live probes")
    parser.add_argument("--show", action="store_true", help="Display results summary")
    parser.add_argument(
        "--canonical", type=str, default=None,
        help="Run only one canonical by ID (e.g. C01)"
    )
    parser.add_argument(
        "--provider", type=str, default=None,
        help="Run only one provider (e.g. openai)"
    )
    args = parser.parse_args()

    if args.show:
        show_results()
        return

    # Filter if specified
    global CANONICALS, PROVIDERS
    if args.canonical:
        CANONICALS = [c for c in CANONICALS if c["id"] == args.canonical.upper()]
        if not CANONICALS:
            print(f"Unknown canonical ID: {args.canonical}")
            return
    if args.provider:
        PROVIDERS = [p for p in PROVIDERS if p == args.provider.lower()]
        if not PROVIDERS:
            print(f"Unknown provider: {args.provider}")
            return

    if args.run:
        run_audit(dry_run=False)
    else:
        run_audit(dry_run=True)


if __name__ == "__main__":
    main()
