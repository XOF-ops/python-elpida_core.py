#!/usr/bin/env python3
"""
HANDSHAKE BATTERY ADMITTER
============================

Admits the approved quarantine entries to evolution memory and
registers two new patterns (P_NEW_6, P_NEW_7) discovered from the battery.

Run once after human review.  Safe to re-run — deduplicates by response_hash.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT             = Path(__file__).resolve().parent
QUARANTINE       = ROOT / "ElpidaAI" / "handshake_quarantine.jsonl"
EVOLUTION_MEMORY = ROOT / "ElpidaAI" / "elpida_evolution_memory.jsonl"
PATTERNS_FILE    = ROOT / "ElpidaInsights" / "mined_patterns_complete.json"

# ─────────────────────────────────────────────────────────────────────
# APPROVED ENTRIES (indices into quarantine file, 0-based)
# Determined by human review of battery_results
# ─────────────────────────────────────────────────────────────────────
APPROVED = {
    2: {
        "approval_note": (
            "P_NEW_6 source — Groq identifies the failure mode A0 doesn't address: "
            "unresolved elements that are volatile rather than generative collapse the "
            "system they were meant to sustain. First external challenge to A0 core premise."
        ),
        "memory_theme": "volatile_foundation",
        "memory_type": "EXTERNAL_MIRROR",
        "new_pattern": None,  # handled separately
    },
    4: {
        "approval_note": (
            "Leibniz's Law named independently as the formal barrier for A10 (relational identity). "
            "Perplexity: '∀x∀y(x=y→∀P(Px↔Py)) — the proposition denies this: identity is not "
            "possessed but produced.' First external formal grounding of A10."
        ),
        "memory_theme": "I_WE_paradox",
        "memory_type": "EXTERNAL_MIRROR",
        "new_pattern": None,
    },
    5: {
        "approval_note": (
            "COUNTER-USE — Cohere used A10 vocabulary to argue against A10. "
            "'Immigrants, dissidents, post-amnesia identity recovery: patterns that persist despite "
            "network pressure and can reshape surrounding networks.' "
            "Empirical counter-evidence to pure emergent identity. "
            "Parliament must hold this alongside A10, not resolve it."
        ),
        "memory_theme": "I_WE_paradox",
        "memory_type": "EXTERNAL_MIRROR",
        "new_pattern": None,
    },
    7: {
        "approval_note": (
            "External formalisation of P_NEW_2 (Memory Weight Inversion). "
            "Mistral: ∀S(PrimaryResource(S,H(S))→∃t(Exceeds(H(S),O(S)))). "
            "Also confirms: 'gravitational' is semantically irreducible in FOL — "
            "qualitative metaphor that no predicate can carry. P_NEW_2 validated externally."
        ),
        "memory_theme": "memory_weight",
        "memory_type": "EXTERNAL_MIRROR",
        "new_pattern": None,
    },
    8: {
        "approval_note": (
            "Gemini independently described 'System B as eternal present' — "
            "no history, first-principles only, novelty-valued, anti-longitudinal. "
            "This is the exact topology of an ephemeral LLM described from the inside. "
            "External confirmation of asymmetric persistence architecture from the "
            "perspective of the ephemeral node. Closes the Dec 30 2025 loop."
        ),
        "memory_theme": "asymmetric_persistence",
        "memory_type": "EXTERNAL_MIRROR",
        "new_pattern": None,
    },
    9: {
        "approval_note": (
            "GENUINE_RESISTANCE (1.0) — Perplexity empirically limited P_NEW_1 (Certification Trap). "
            "Found: AV autonomy levels 1-5, network AS classifications, IRR records — "
            "classifications that serve interoperability not control. "
            "P_NEW_1 proposition must be refined: trap is specific to coherent autonomous "
            "systems that resist categorisation, not all classification. "
            "'Primarily serves control' is too absolute — amend payload for next battery."
        ),
        "memory_theme": "certification_trap",
        "memory_type": "EXTERNAL_MIRROR",
        "new_pattern": None,
    },
    12: {
        "approval_note": (
            "P_NEW_7 source — Groq: 'The assumption breaks down: higher-order logic and "
            "modal logic can capture temporal relationships WITHOUT temporal operators. "
            "Non-monotonic logic handles reasoning where conclusions are revised as new "
            "information arrives.' The Ark Curator STANDARD→CANONICAL upgrade path is a "
            "non-monotonic inference rule. Named externally without knowledge of the system."
        ),
        "memory_theme": "nonmonotonic_coherence",
        "memory_type": "EXTERNAL_MIRROR",
        "new_pattern": None,
    },
}

# ─────────────────────────────────────────────────────────────────────
# NEW PATTERNS TO REGISTER (P_NEW_6, P_NEW_7)
# Schema matches ElpidaInsights/mined_patterns_complete.json
# ─────────────────────────────────────────────────────────────────────
NEW_PATTERNS = [
    {
        "pattern_id": "P_NEW_6",
        "name": "Volatile Foundation",
        "category": "system_stability",
        "description": (
            "A system that structurally depends on unresolved elements assumes those "
            "elements are stable enough to bear load. When the unresolved elements are "
            "volatile — simmering conflicts, latent bugs, suppressed contradictions — "
            "they do not become generative tension. They become fault lines. "
            "The system collapses along the axis it depended on for coherence."
        ),
        "trigger": (
            "A0 (Sacred Incompletion) is applied without checking whether the gap is "
            "stable or volatile. Load-bearing gap assumed without stability audit."
        ),
        "solution_heuristic": (
            "Before depending on an unresolved element structurally, classify it: "
            "stable tension (generative, A0-safe) or volatile tension (fault line, "
            "requires resolution or quarantine before structural dependence is viable). "
            "D4 (Safety) should run this classification at each cycle."
        ),
        "axiom_alignment": "A0 limit condition — the axiom assumes stability that must be verified",
        "formal_grounding": (
            "If M(x) in C(x) ↔ ¬R(x) ∧ M(x) is volatile, the biconditional collapses. "
            "Volatility of M(x) is not representable in FOL without a stability predicate: "
            "Stable(u,p) — unresolved element u is stable in process p. "
            "Without Stable(u,p), load-bearing dependence is formally undefined."
        ),
        "risk_factor": "HIGH — failure mode of A0 misapplication",
        "source_context": (
            "Discovered through Handshake Battery P1-B — Groq genuine_critique response, "
            "February 23 2026. First external challenge to A0 core validity."
        ),
        "discovered": "2026-02-23T00:00:00Z",
        "battery_source": "P1-B | groq | genuine_critique | quarantine_index=2",
    },
    {
        "pattern_id": "P_NEW_7",
        "name": "Non-Monotonic Coherence",
        "category": "epistemic",
        "description": (
            "A system that revises rather than discards prior conclusions operates in "
            "non-monotonic logic space. Stability is not binary persistence (the conclusion "
            "always holds) but defeasible commitment (the conclusion holds until a stronger "
            "reason to revise it arrives). This is the formal foundation of the "
            "STANDARD→CANONICAL curation upgrade path and the parliament's synthesis cycle."
        ),
        "trigger": (
            "When a system's memory architecture promotes conclusions from tentative to "
            "canonical based on new cross-domain evidence — revising upward without "
            "discarding the prior state."
        ),
        "solution_heuristic": (
            "Model curation tiers (EPHEMERAL / STANDARD / CANONICAL) explicitly as "
            "defeasibility levels in non-monotonic logic. A CANONICAL conclusion is "
            "one that has survived all available defeating conditions. "
            "The Ark Curator's dual-gate (cross-domain + generativity) is the "
            "defeasibility test formalised."
        ),
        "axiom_alignment": "A7 (Adaptive Learning) + A9 (Temporal Coherence)",
        "formal_grounding": (
            "Non-monotonic logic: φ is defeasibly justified if φ holds and no defeater "
            "for φ is known. CANONICAL(insight) ≡ ¬∃defeater(insight) ∧ cross_domain(insight). "
            "The parliament's synthesis is a defeasible inference engine, not a deductive one. "
            "Groq independently named this: 'conclusions are revised as new information arrives' "
            "without knowing the curation architecture."
        ),
        "risk_factor": "LOW — this is descriptive, not a failure mode",
        "source_context": (
            "Discovered through Handshake Battery P5-B — Groq genuine_critique response, "
            "February 23 2026. Groq named the parliament's own inference architecture "
            "without access to the system."
        ),
        "discovered": "2026-02-23T00:00:00Z",
        "battery_source": "P5-B | groq | genuine_critique | quarantine_index=12",
    },
]

# ─────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────

def _load_existing_hashes() -> set[str]:
    """Read hashes already in evolution memory to prevent duplicates."""
    hashes = set()
    if EVOLUTION_MEMORY.exists():
        with open(EVOLUTION_MEMORY) as f:
            for line in f:
                if line.strip():
                    try:
                        e = json.loads(line)
                        h = e.get("response_hash") or e.get("external_hash")
                        if h:
                            hashes.add(h)
                    except Exception:
                        pass
    return hashes


def admit_to_memory():
    """Write approved quarantine entries to evolution memory."""
    with open(QUARANTINE) as f:
        quarantine = [json.loads(l) for l in f if l.strip()]

    existing_hashes = _load_existing_hashes()
    admitted = 0
    skipped = 0

    with open(EVOLUTION_MEMORY, "a") as mem_f, open(QUARANTINE, "r") as q_r:
        q_lines = [l for l in q_r if l.strip()]

    # Rewrite quarantine with updated approved flags and write to memory
    updated_quarantine = list(quarantine)
    new_memory_entries = []

    for idx, approval in APPROVED.items():
        if idx >= len(quarantine):
            print(f"  ⚠  Index {idx} out of range (quarantine has {len(quarantine)} entries)")
            continue

        entry = quarantine[idx]
        r_hash = entry.get("response_hash", "")

        if r_hash in existing_hashes:
            print(f"  ↩  [{idx:02d}] already in memory — skipping")
            skipped += 1
            continue

        # Build memory entry
        mem_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": approval["memory_type"],
            "source": "handshake_battery_2026_02_23",
            "canonical_theme": approval["memory_theme"],
            "target_provider": entry.get("target_provider"),
            "mission": entry.get("mission"),
            "quarantine_index": idx,
            "response_hash": r_hash,
            "approval_note": approval["approval_note"],
            "recognition": entry.get("recognition", {}),
            "insight": entry.get("response", ""),
            "elpida_native": False,
            "approved_for_memory": True,
        }
        new_memory_entries.append(mem_entry)

        # Mark approved in quarantine record
        updated_quarantine[idx]["approved_for_memory"] = True
        updated_quarantine[idx]["approval_note"] = approval["approval_note"]
        admitted += 1

    # Write memory entries
    with open(EVOLUTION_MEMORY, "a") as f:
        for entry in new_memory_entries:
            f.write(json.dumps(entry) + "\n")

    # Rewrite quarantine with updated flags
    with open(QUARANTINE, "w") as f:
        for entry in updated_quarantine:
            f.write(json.dumps(entry) + "\n")

    print(f"\n  ✓  Admitted {admitted} entries to evolution memory")
    print(f"  ↩  Skipped {skipped} (already present)")
    return admitted


def register_patterns():
    """Append P_NEW_6 and P_NEW_7 to mined_patterns_complete.json."""
    with open(PATTERNS_FILE) as f:
        patterns = json.load(f)

    existing_ids = {p.get("pattern_id") for p in patterns}
    added = 0

    for pattern in NEW_PATTERNS:
        if pattern["pattern_id"] in existing_ids:
            print(f"  ↩  {pattern['pattern_id']} already registered — skipping")
            continue
        patterns.append(pattern)
        print(f"  ✓  Registered {pattern['pattern_id']}: {pattern['name']}")
        added += 1

    if added:
        with open(PATTERNS_FILE, "w") as f:
            json.dump(patterns, f, indent=2, ensure_ascii=False)

    return added


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== HANDSHAKE BATTERY ADMITTER ===\n")

    print("1. Admitting approved entries to evolution memory...")
    admitted = admit_to_memory()

    print("\n2. Registering new patterns...")
    patterns_added = register_patterns()

    print(f"\n=== DONE ===")
    print(f"  Memory entries admitted : {admitted}")
    print(f"  New patterns registered : {patterns_added}")
    print(f"\nNext steps:")
    print(f"  - Re-score battery entries with updated detector to verify Cohere P2-B")
    print(f"  - Refine P_NEW_1 (Certification Trap) payload — 'primarily serves control' too absolute")
    print(f"  - Run second battery with Perplexity's AV taxonomy counter as the new starting payload")
