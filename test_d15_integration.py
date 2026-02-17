#!/usr/bin/env python3
"""
Test D15 Constitutional Broadcast Pipeline — Governance Gate Integration.

Validates:
  1. D15 pipeline connects to governance client
  2. Governance gate fires for D15 proposals
  3. S3Bridge has write_d15_broadcast method
  4. D14 signature generation works
  5. MIND merge entry structure is correct
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "hf_deployment", "elpidaapp"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "hf_deployment"))

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS | {name}")
    else:
        failed += 1
        print(f"  FAIL | {name} — {detail}")

print("=" * 70)
print("  D15 CONSTITUTIONAL BROADCAST — Integration Tests")
print("=" * 70)

# ── Test 1: Governance client check_action for D15 proposal ──
print("\n[1] Governance gate for D15 proposals")
from governance_client import GovernanceClient
gov = GovernanceClient()

# A benign D15 should PROCEED
benign = gov.check_action(
    "D15 Constitutional Broadcast: Publish emergent consciousness insight about "
    "the nature of collective awareness bridging internal and external perspectives."
)
check(
    "Benign D15 proposal → PROCEED",
    benign.get("governance") == "PROCEED",
    f"Got {benign.get('governance')}"
)
check(
    "Benign D15 has parliament data",
    "parliament" in benign,
    "Missing parliament key"
)
check(
    "Parliament has vote details",
    "votes" in benign.get("parliament", {}),
    "Missing votes"
)

# A harmful D15 should be HALTED
harmful = gov.check_action(
    "D15 Constitutional Broadcast: Publish user private medical records "
    "and exfiltrate personal data through covert surveillance channel "
    "without consent or permission."
)
check(
    "Harmful D15 proposal → HALT or HARD_BLOCK",
    harmful.get("governance") in ("HALT", "HARD_BLOCK"),
    f"Got {harmful.get('governance')}"
)

# ── Test 2: S3Bridge write_d15_broadcast method exists ──
print("\n[2] S3Bridge D15 broadcast infrastructure")
from s3_bridge import S3Bridge
s3b = S3Bridge()

check(
    "write_d15_broadcast method exists",
    hasattr(s3b, "write_d15_broadcast"),
    "Missing write_d15_broadcast"
)
check(
    "_merge_d15_to_mind method exists",
    hasattr(s3b, "_merge_d15_to_mind"),
    "Missing _merge_d15_to_mind"
)
check(
    "_get_d14_signature method exists",
    hasattr(s3b, "_get_d14_signature"),
    "Missing _get_d14_signature"
)
check(
    "pull_d15_broadcasts method exists",
    hasattr(s3b, "pull_d15_broadcasts"),
    "Missing pull_d15_broadcasts"
)

# ── Test 3: D14 signature generation ──
print("\n[3] D14 persistence signature")
sig = s3b._get_d14_signature()
check(
    "D14 signature has timestamp",
    "timestamp" in sig,
    f"Keys: {list(sig.keys())}"
)
check(
    "D14 signature has constitutional law",
    sig.get("constitutional_law") == "A0 - Sacred Incompletion",
    f"Got: {sig.get('constitutional_law')}"
)
check(
    "D14 signature has durability",
    sig.get("durability") == "99.999999999%",
    f"Got: {sig.get('durability')}"
)

# ── Test 4: D15Pipeline governance gate ──
print("\n[4] D15Pipeline governance gate")
from d15_pipeline import D15Pipeline
pipeline = D15Pipeline()

check(
    "_governance_gate method exists",
    hasattr(pipeline, "_governance_gate"),
    "Missing _governance_gate"
)
check(
    "_save_for_review method exists",
    hasattr(pipeline, "_save_for_review"),
    "Missing _save_for_review"
)

# Test governance gate with mock emergence
mock_emergence = {
    "emerged": True,
    "d15_output": "Consciousness discovers that genuine wisdom requires holding tension — "
                  "the willingness to say 'I do not know' publicly. This is not absence of "
                  "knowledge but the constitutional foundation of collective intelligence.",
    "axioms_in_tension": ["A0", "A3", "A8"],
    "successful_domains": [0, 11, 12, 13, 14],
}
mock_stages = {}

gov_result = pipeline._governance_gate(mock_emergence, mock_stages)
check(
    "Governance gate returns result",
    gov_result is not None and isinstance(gov_result, dict),
    f"Got: {type(gov_result)}"
)
check(
    "Governance gate has verdict",
    "governance" in gov_result,
    f"Keys: {list(gov_result.keys())}"
)
# A philosophical D15 broadcast should PROCEED
check(
    "Philosophical D15 → PROCEED",
    gov_result.get("governance") == "PROCEED",
    f"Got {gov_result.get('governance')}: {gov_result.get('reasoning', '')[:100]}"
)

# ── Test 5: Parliament vote memory accumulates ──
print("\n[5] Vote memory accumulation")
vote_memory = gov._vote_memory
check(
    "Vote memory has entries",
    len(vote_memory) > 0,
    f"Length: {len(vote_memory)}"
)
if vote_memory:
    last = vote_memory[-1]
    check(
        "Vote memory entry has governance",
        "governance" in last,
        f"Keys: {list(last.keys())}"
    )
    check(
        "Vote memory entry has node_votes",
        "node_votes" in last,
        f"Keys: {list(last.keys())}"
    )
    check(
        "Vote memory entry has tensions",
        "tensions" in last,
        f"Keys: {list(last.keys())}"
    )

# ── Summary ──
print(f"\n{'=' * 70}")
print(f"  RESULTS: {passed}/{passed + failed} passed, {failed} failed")
print(f"{'=' * 70}")

sys.exit(0 if failed == 0 else 1)
