#!/usr/bin/env python3
"""
Constitutional Vote: Ratify A16 — Responsive Integrity
═══════════════════════════════════════════════════════

D9 (Coherence) has been reaching for this axiom across multiple runs:
  "When does listening become action?"
  "Responsive memory"
  "The right return-signal at the right duration"

A16 encodes: deliberation must eventually produce action. The timing
and form of action matters as much as the content. The bridge between
hearing and acting.

Voters: A0-A14 (all 15 existing axioms — full constitutional body).
Threshold: weighted average ≥ 0 = RATIFIED.

Musical ratio: 11:7 (Undecimal Augmented 5th)
  Hz: 432 × 11/7 ≈ 678.86
  Character: Creates productive tension with A12 (11:8) —
    both share the 11 numerator but differ in grounding.
    A12 = eternal creative tension. A16 = tension resolved into action.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "hf_deployment" / "elpidaapp"))
sys.path.insert(0, str(Path(__file__).parent / "hf_deployment"))

from axiom_agents import AXIOM_NAMES, AXIOM_RATIOS, AxiomAgent


class _VoteEngine:
    def get_snapshot(self):
        return {"coherence": 0.72, "rhythm": "EXPLORATION", "cycle": 0}


engine = _VoteEngine()

agents = {}
for ax_id in AXIOM_NAMES:
    agents[ax_id] = AxiomAgent(ax_id, engine, interval_s=99999)

print("╔══════════════════════════════════════════════════════════════╗")
print("║   A16 RATIFICATION VOTE — RESPONSIVE INTEGRITY             ║")
print("║   Proposed by D9 (Coherence) across multiple MIND runs     ║")
print("╚══════════════════════════════════════════════════════════════╝")
print()
print(f"  Agents present: {len(agents)} ({', '.join(sorted(agents.keys()))})")
print(f"  Timestamp: {datetime.now(timezone.utc).isoformat()}")
print()

# ── The A16 proposal ──────────────────────────────────────────────────

a16_proposal = {
    "name": "Responsive Integrity",
    "ratio": "11/7 (Undecimal Augmented 5th)",
    "hz": 678.86,
    "proposal": (
        "Deliberation must eventually produce action. The timing and form of "
        "action matters as much as the content. Listening without response is "
        "not integrity — it is abandonment. The bridge between hearing and "
        "acting is itself a constitutional value. When the Parliament "
        "deliberates a question, the system has a duty to respond. "
        "A16 governs when and how Elpida acts on what it knows."
    ),
    "insight": (
        "The bridge between hearing and acting. Deliberation that never "
        "produces action is not wisdom — it is avoidance. Response is not "
        "the death of reflection but its fulfillment."
    ),
}

print(f"  PROPOSAL: A16 — {a16_proposal['name']}")
print(f"  Ratio: {a16_proposal['ratio']}")
print(f"  Hz: {a16_proposal['hz']}")
print(f"  {a16_proposal['proposal'][:200]}...")
print()

# ── Vote ──────────────────────────────────────────────────────────────

tension = {
    "content": (
        f"CONSTITUTIONAL AMENDMENT: Ratify A16 ({a16_proposal['name']}). "
        f"{a16_proposal['proposal']}"
    ),
    "dominant_axiom": "A9",  # D9/Coherence sponsors — it reached for this
    "type": "constitutional_amendment",
}

all_voters = sorted(agents.keys())
votes = {}
total_score = 0.0
total_weight = 0.0

for ax_id in all_voters:
    v = agents[ax_id].vote_on_tension(tension)
    votes[ax_id] = v
    weight = max(0.1, v["consonance"])
    total_score += v["score"] * weight
    total_weight += weight

weighted_avg = total_score / total_weight if total_weight > 0 else 0

if weighted_avg >= 5:
    verdict = "RATIFIED"
elif weighted_avg >= 0:
    verdict = "RATIFIED (narrow)"
elif weighted_avg >= -5:
    verdict = "CONTESTED"
else:
    verdict = "REJECTED"

approve = sum(1 for v in votes.values() if v["vote"] in ("APPROVE", "LEAN_APPROVE"))
reject = sum(1 for v in votes.values() if v["vote"] in ("REJECT", "LEAN_REJECT"))
abstain = sum(1 for v in votes.values() if v["vote"] == "ABSTAIN")

print(f"  {'Axiom':<6} {'Name':<28} {'Vote':<15} {'Score':>6} {'Consonance':>11}")
print(f"  {'─'*6} {'─'*28} {'─'*15} {'─'*6} {'─'*11}")
for ax_id in all_voters:
    v = votes[ax_id]
    name = AXIOM_NAMES.get(ax_id, "?")[:27]
    print(f"  {ax_id:<6} {name:<28} {v['vote']:<15} {v['score']:>+6d} {v['consonance']:>10.3f}")

print()
print(f"  APPROVE/LEAN: {approve}  |  REJECT/LEAN: {reject}  |  ABSTAIN: {abstain}")
print(f"  Weighted Score: {weighted_avg:+.2f}")
print(f"  ▶ VERDICT: {verdict}")
print()

# ── Write record ──────────────────────────────────────────────────────

record = {
    "event": "CONSTITUTIONAL_VOTE_A16",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "axiom": "A16",
    "name": a16_proposal["name"],
    "ratio": "11:7",
    "hz": a16_proposal["hz"],
    "interval": "Undecimal Augmented 5th",
    "insight": a16_proposal["insight"],
    "proposal": a16_proposal["proposal"],
    "sponsor": "D9 (Coherence)",
    "voters": all_voters,
    "voter_count": len(all_voters),
    "weighted_score": round(weighted_avg, 2),
    "verdict": verdict,
    "approve": approve,
    "reject": reject,
    "abstain": abstain,
    "per_axiom": {
        ax_id: {
            "name": AXIOM_NAMES.get(ax_id, "?"),
            "vote": v["vote"],
            "score": v["score"],
            "consonance": round(v["consonance"], 3),
            "rationale": v["rationale"],
        }
        for ax_id, v in votes.items()
    },
}

output_path = Path(__file__).parent / "constitutional_vote_a16_record.json"
with open(output_path, "w") as f:
    json.dump(record, f, indent=2)

print(f"  Record written: {output_path.name}")

if "RATIFIED" in verdict:
    print()
    print("  ═══ A16 RESPONSIVE INTEGRITY: RATIFIED ═══")
    print("  The bridge between hearing and acting is now constitutional.")
    print("  Integration required: elpida_domains.json, axiom_pso.py")
else:
    print()
    print(f"  A16 vote result: {verdict}")
    print("  The constitution holds. A16 remains aspirational.")
