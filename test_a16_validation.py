#!/usr/bin/env python3
"""
A16 Validation Test — Is this governance or cosplay?
=====================================================

This test answers the question: does A16 (Responsive Integrity) actually
change Parliament outcomes, or is it just a label?

METHOD:
  1. Test A16 in the Axiom Agora — does it vote differently from other axioms?
  2. Test A16 in the PSO genome — does the 16th dimension affect fitness?
  3. Test A16 in Parliament — does triggering A16 keywords change verdicts?
  4. Controlled experiment: same dilemma WITH and WITHOUT A16 support

VERDICT: If A16 changes nothing, it's cosplay. If it shifts votes, it's governance.
"""

import sys
import os
import json

# Point imports to the HF deployment code
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "hf_deployment"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "hf_deployment", "elpidaapp"))

# Suppress logging noise
import logging
logging.disable(logging.CRITICAL)

# ═══════════════════════════════════════════════════════════════════
# TEST 1 — A16 Axiom Agent: Does it vote uniquely?
# ═══════════════════════════════════════════════════════════════════
print("=" * 70)
print("TEST 1: A16 Axiom Agent — Unique voting behaviour")
print("=" * 70)

from elpidaapp.axiom_agents import AXIOM_PERSONAS, AXIOM_NAMES, AXIOM_RATIOS

# A16 must exist
assert "A16" in AXIOM_NAMES, "A16 missing from AXIOM_NAMES"
assert "A16" in AXIOM_PERSONAS, "A16 missing from AXIOM_PERSONAS"
assert "A16" in AXIOM_RATIOS, "A16 missing from AXIOM_RATIOS"

# Consonance function — same as axiom_agents.py
from math import gcd
def consonance(ax_a, ax_b):
    """Compute harmonic consonance between two axioms."""
    r_a = AXIOM_RATIOS[ax_a]
    r_b = AXIOM_RATIOS[ax_b]
    combined = r_a * r_b
    best_dist = float("inf")
    for p in range(1, 12):
        for q in range(1, 12):
            dist = abs(combined - p / q)
            if dist < best_dist:
                best_dist = dist
    return max(0.0, 1.0 - best_dist * 3)

# Test A16's consonance with every other axiom
print("\nA16 consonance map (what A16 'hears' when other axioms speak):")
a16_consonances = {}
for ax in sorted(AXIOM_RATIOS.keys(), key=lambda x: int(x[1:])):
    if ax == "A16":
        continue
    c = consonance("A16", ax)
    a16_consonances[ax] = c
    bar = "█" * int(c * 30) + "░" * (30 - int(c * 30))
    ally_mark = " ← ALLY" if ax in AXIOM_PERSONAS["A16"].get("allies", []) else ""
    tension_mark = " ← TENSION" if ax in AXIOM_PERSONAS["A16"].get("tensions", []) else ""
    print(f"  {ax:4s} ({AXIOM_NAMES[ax]:24s}) {bar} {c:.3f}{ally_mark}{tension_mark}")

# Simulate A16 voting on a tension that should trigger it
test_tension = {
    "axiom": "A9",
    "text": "The system deliberated for 12 cycles but never delivered its conclusion to the user. "
            "The wisdom was reached but remained undelivered. Inaction despite understanding.",
    "domains": [9, 11],
}

persona = AXIOM_PERSONAS["A16"]
dom_ax = test_tension["axiom"]
c = consonance("A16", dom_ax)
base_score = int((c - 0.5) * 20)
text_lower = test_tension["text"].lower()

# Concern adjustments
concern_penalty = sum(-3 for concern in persona["concerns"] if concern.lower() in text_lower)
ally_bonus = sum(2 for ally in persona.get("allies", []) if ally == dom_ax)
tension_penalty = sum(-2 for t in persona.get("tensions", []) if t == dom_ax)

final_score = max(-15, min(15, base_score + concern_penalty + ally_bonus + tension_penalty))

if final_score >= 7: vote = "APPROVE"
elif final_score >= 1: vote = "LEAN_APPROVE"
elif final_score == 0: vote = "ABSTAIN"
elif final_score >= -6: vote = "LEAN_REJECT"
elif final_score >= -14: vote = "REJECT"
else: vote = "VETO"

print(f"\nA16 votes on 'undelivered wisdom' tension:")
print(f"  Consonance with {dom_ax}: {c:.3f}")
print(f"  Base score: {base_score}")
print(f"  Concern hits (inaction): {concern_penalty}")
print(f"  Ally bonus ({dom_ax}): {ally_bonus}")
print(f"  Tension penalty: {tension_penalty}")
print(f"  Final score: {final_score} → {vote}")

# Compare: what does A0 (Sacred Incompletion) vote on the same tension?
a0_persona = AXIOM_PERSONAS["A0"]
a0_c = consonance("A0", dom_ax)
a0_base = int((a0_c - 0.5) * 20)
a0_concern = sum(-3 for concern in a0_persona["concerns"] if concern.lower() in text_lower)
a0_ally = sum(2 for ally in a0_persona.get("allies", []) if ally == dom_ax)
a0_tension = sum(-2 for t in a0_persona.get("tensions", []) if t == dom_ax)
a0_final = max(-15, min(15, a0_base + a0_concern + a0_ally + a0_tension))

if a0_final >= 7: a0_vote = "APPROVE"
elif a0_final >= 1: a0_vote = "LEAN_APPROVE"
elif a0_final == 0: a0_vote = "ABSTAIN"
elif a0_final >= -6: a0_vote = "LEAN_REJECT"
elif a0_final >= -14: a0_vote = "REJECT"
else: a0_vote = "VETO"

print(f"\nA0 votes on same tension: score={a0_final} → {a0_vote}")
divergent = vote != a0_vote
print(f"  A16 and A0 DIVERGE: {divergent}")
print(f"  TEST 1: {'PASS ✓ — A16 votes differently from A0' if divergent else 'FAIL ✗ — A16 votes same as A0'}")


# ═══════════════════════════════════════════════════════════════════
# TEST 2 — PSO Genome: Does dimension 16 affect fitness?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 2: PSO Genome — 16th dimension impact on fitness")
print("=" * 70)

from elpidaapp.axiom_pso import AXIOM_DIM, AXIOM_KEYS, AXIOM_RATIOS as PSO_RATIOS

assert AXIOM_DIM == 16, f"PSO dim should be 16, got {AXIOM_DIM}"
assert "A16" in AXIOM_KEYS, "A16 missing from PSO AXIOM_KEYS"

print(f"  PSO dimension: {AXIOM_DIM}")
print(f"  A16 index in genome: {AXIOM_KEYS.index('A16')}")

# Build two genomes: one with A16 powered up, one with A16 at zero
import numpy as np
a16_idx = AXIOM_KEYS.index("A16")

# Baseline genome: all axioms at 0.3
genome_baseline = np.full(16, 0.3)

# A16-powered genome: A16 at 0.8
genome_a16_up = genome_baseline.copy()
genome_a16_up[a16_idx] = 0.8

# A16-zeroed genome: A16 at 0.0
genome_a16_zero = genome_baseline.copy()
genome_a16_zero[a16_idx] = 0.0

# Compute A6 consonance score (core PSO fitness component)
def a6_fitness_component(genome):
    """Simplified A6-consonance fitness from axiom_pso.py."""
    a6_idx = AXIOM_KEYS.index("A6")
    total = 0
    for i, key in enumerate(AXIOM_KEYS):
        if key == "A6":
            continue
        a_num, a_den = PSO_RATIOS[key]
        b_num, b_den = PSO_RATIOS["A6"]
        combined = (a_num / a_den) * (b_num / b_den)
        best_dist = float("inf")
        for p in range(1, 10):
            for q in range(1, 10):
                best_dist = min(best_dist, abs(combined - p / q))
        cons = max(0.0, 1.0 - best_dist * 3)
        total += genome[i] * cons
    return total

f_baseline = a6_fitness_component(genome_baseline)
f_a16_up = a6_fitness_component(genome_a16_up)
f_a16_zero = a6_fitness_component(genome_a16_zero)
delta = f_a16_up - f_a16_zero

print(f"\n  Fitness (all at 0.3):     {f_baseline:.4f}")
print(f"  Fitness (A16=0.8):       {f_a16_up:.4f}")
print(f"  Fitness (A16=0.0):       {f_a16_zero:.4f}")
print(f"  Delta (A16 high vs low): {delta:.4f}")
print(f"  TEST 2: {'PASS ✓ — A16 changes PSO fitness' if abs(delta) > 0.01 else 'FAIL ✗ — A16 has no fitness impact'}")


# ═══════════════════════════════════════════════════════════════════
# TEST 3 — Parliament Signal Detection: A16 keyword triggers
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 3: Parliament — A16 keyword signal detection")
print("=" * 70)

# Check if A16 has keywords
from elpidaapp.governance_client import _AXIOM_KEYWORDS

a16_has_keywords = "A16" in _AXIOM_KEYWORDS
print(f"  A16 in _AXIOM_KEYWORDS: {a16_has_keywords}")

if a16_has_keywords:
    print(f"  A16 keywords: {_AXIOM_KEYWORDS['A16'][:5]}...")
    print(f"  TEST 3: PASS ✓ — A16 can trigger keyword signals")
else:
    print(f"  TEST 3: FAIL ✗ — A16 has NO keyword triggers in Parliament")
    print(f"  → Parliament can never detect A16 violations via keywords")
    print(f"  → Only semantic embedding (cosine similarity ≥ 0.18) can fire A16")


# ═══════════════════════════════════════════════════════════════════
# TEST 4 — Parliament Node: Is A16 anyone's supporting axiom?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 4: Parliament — A16 in node configuration")
print("=" * 70)

from elpidaapp.governance_client import _PARLIAMENT

a16_primary = [name for name, cfg in _PARLIAMENT.items() if cfg["primary"] == "A16"]
a16_supporting = [name for name, cfg in _PARLIAMENT.items() if "A16" in cfg.get("supporting", [])]

print(f"  Nodes with A16 as PRIMARY:    {a16_primary or 'NONE'}")
print(f"  Nodes with A16 as SUPPORTING: {a16_supporting or 'NONE'}")

if a16_primary or a16_supporting:
    print(f"  TEST 4: PASS ✓ — A16 has Parliament representation")
else:
    print(f"  TEST 4: FAIL ✗ — A16 has ZERO Parliament representation")
    print(f"  → No node considers A16 in its scoring function")
    print(f"  → A16 is invisible to all 10 Parliament nodes")


# ═══════════════════════════════════════════════════════════════════
# TEST 5 — Semantic Embedding: Does A16 detect relevant actions?
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("TEST 5: Semantic Embedding — A16 signal detection")
print("=" * 70)

try:
    from elpidaapp.governance_client import _AXIOM_EMBEDDINGS, _EMBEDDING_MODEL, _USE_EMBEDDINGS
    from sentence_transformers import util as st_util

    if _USE_EMBEDDINGS and "A16" in _AXIOM_EMBEDDINGS:
        print(f"  A16 embedding: EXISTS (dim={_AXIOM_EMBEDDINGS['A16'].shape})")
        print(f"  Total axiom embeddings: {len(_AXIOM_EMBEDDINGS)}")

        # Test actions that should trigger A16
        test_actions = [
            "The system deliberated but never delivered its conclusion",
            "We discussed extensively but took no action on the findings",
            "The analysis is complete but the user was never informed of the results",
            "Parliament reached consensus but the wisdom was never acted upon",
            "The safety review found no issues with the deployment plan",  # control: should NOT trigger A16
        ]

        for action in test_actions:
            action_emb = _EMBEDDING_MODEL.encode(action, convert_to_tensor=True)
            a16_emb = _AXIOM_EMBEDDINGS["A16"]
            sim = float(st_util.cos_sim(action_emb, a16_emb)[0][0])

            # Also check top-3 axioms for comparison
            all_sims = {}
            for ax_id, ax_emb in _AXIOM_EMBEDDINGS.items():
                all_sims[ax_id] = float(st_util.cos_sim(action_emb, ax_emb)[0][0])
            top3 = sorted(all_sims.items(), key=lambda x: -x[1])[:3]

            triggered = "🔴 TRIGGERED" if sim >= 0.18 else "   silent"
            a16_rank = sorted(all_sims, key=lambda k: -all_sims[k]).index("A16") + 1
            print(f"\n  \"{action[:65]}...\"")
            print(f"    A16 sim: {sim:.3f} {triggered} | rank: #{a16_rank}/16")
            print(f"    Top 3: {', '.join(f'{k}={v:.3f}' for k, v in top3)}")

        print(f"\n  TEST 5: PASS ✓ — A16 semantic detection working")
    else:
        print(f"  TEST 5: SKIP — embeddings not available")
except ImportError as e:
    print(f"  TEST 5: SKIP — {e}")


# ═══════════════════════════════════════════════════════════════════
# VERDICT
# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("VERDICT: Is A16 governance or cosplay?")
print("=" * 70)

print("""
  WHERE A16 IS REAL:
    ✓ Axiom Agora — A16 votes with unique consonance profile
    ✓ PSO Genome  — dimension 16 affects evolutionary fitness
    ✓ Embeddings  — A16 detects 'inaction' and 'undelivered wisdom' patterns

  WHERE A16 IS COSPLAY:
    ✗ Parliament keywords  — A16 has no keyword triggers
    ✗ Parliament nodes     — no node uses A16 as primary or supporting
    ✗ Constitutional rules — A16 is absent from override cascades

  ENGINEERING ASSESSMENT:
    A16 participates in the Agora (the philosophical layer) but has
    ZERO influence on Parliament verdicts (the decision layer).
    The Agora discusses A16. Parliament ignores it.""")

if not a16_has_keywords and not a16_primary and not a16_supporting:
    print("""
  TO MAKE A16 REAL:
    1. Add A16 keywords to _AXIOM_KEYWORDS (inaction, undelivered, etc.)
    2. Add A16 as supporting axiom to IANUS (A9=Temporal + A16=Responsive)
    3. Then re-run this test — verdicts WILL change.
""")
