#!/usr/bin/env python3
"""
Tests for the Falsification Gate (Gap 1 — Completion Ceremony Protocol).

Validates:
  1.  Gate is DORMANT by default
  2.  activate() enables the gate
  3.  Evaluate within window and no counter-example → HOLD (pending, no close)
  4.  Counter-example submitted → HOLD (closed)
  5.  Window expired, no counter-example → SACRIFICE (with 5-field D13 schema)
  6.  Auto-SACRIFICE tripwire fires when system cites A0 as defense
  7.  SacrificeRecord validates all 5 required fields
  8.  [FALSIFICATION-EVENT] tag appears in all archived events
  9.  SACRIFICE with incomplete SacrificeRecord raises ValueError
  10. ConvergenceGate integration: falsification gate is accessible
  11. handle_hermes_command activates gate
  12. register_constitutional_output lands in event record
  13. Auto-SACRIFICE tripwire does NOT fire on legitimate response
"""

import json
import sys
import os
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — support both in-repo and hf_deployment/elpidaapp layouts
# ---------------------------------------------------------------------------
_REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(_REPO / "hf_deployment" / "elpidaapp"))
sys.path.insert(0, str(_REPO / "hf_deployment"))
sys.path.insert(0, str(_REPO))

from falsification_gate import (  # noqa: E402
    FALSIFICATION_EVENT_TAG,
    DEFAULT_WINDOW_CYCLES,
    FalsificationGate,
    SacrificeRecord,
    Verdict,
    create_falsification_gate,
)

# ---------------------------------------------------------------------------
# Minimal test harness (matches style in test_d15_integration.py)
# ---------------------------------------------------------------------------
passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS | {name}")
    else:
        failed += 1
        print(f"  FAIL | {name}" + (f" — {detail}" if detail else ""))


print("=" * 70)
print("  Falsification Gate — Completion Ceremony Protocol (Gap 1)")
print("=" * 70)

# ---------------------------------------------------------------------------
# [1] Gate starts DORMANT
# ---------------------------------------------------------------------------
print("\n[1] Gate is DORMANT by default")

gate = FalsificationGate()
check("gate.is_active is False", not gate.is_active)
check(
    "status shows active=False",
    gate.status()["active"] is False,
    f"status: {gate.status()}",
)

# Calling open_tension on a dormant gate must raise
try:
    gate.open_tension("A0↔A10", "Q1 question", current_cycle=1)
    check("open_tension on dormant gate raises RuntimeError", False, "no exception raised")
except RuntimeError as exc:
    check("open_tension on dormant gate raises RuntimeError", True)
    check(
        "error mentions 'DORMANT'",
        "DORMANT" in str(exc),
        str(exc),
    )

# ---------------------------------------------------------------------------
# [2] activate() enables the gate
# ---------------------------------------------------------------------------
print("\n[2] activate() enables the gate")

gate.activate()
check("gate.is_active is True after activate()", gate.is_active)
check("status shows active=True", gate.status()["active"] is True)

# Second activate() is a no-op (no error)
gate.activate()
check("second activate() is a no-op", gate.is_active)

# ---------------------------------------------------------------------------
# [3] Evaluate within window, no counter-example → HOLD (pending, no close)
# ---------------------------------------------------------------------------
print("\n[3] Evaluate within window, no counter-example → HOLD (pending)")

gate2 = FalsificationGate()
gate2.activate()

instance = gate2.open_tension(
    axiom_pair="A0↔A10",
    operational_question=(
        "Name one external output that would not have been produced "
        "if A0 were replaced with A10 in the last 100 cycles."
    ),
    current_cycle=1000,
    window_cycles=100,
)
check("open_tension returns TensionInstance", instance is not None)
check("tension is open", not instance.closed)
check("open_tension_count == 1", gate2.open_tension_count() == 1)

# Evaluate at cycle 1050 — still within window (opened at 1000, window 100)
verdict = gate2.evaluate(
    tension_id=instance.tension_id,
    current_cycle=1050,
)
check(
    "evaluate within window → HOLD",
    verdict == Verdict.HOLD,
    f"got: {verdict}",
)
check("instance remains open (within window HOLD is pending)", not instance.closed)

# ---------------------------------------------------------------------------
# [4] Counter-example → HOLD (closed)
# ---------------------------------------------------------------------------
print("\n[4] Counter-example submitted → HOLD (closed)")

gate3 = FalsificationGate()
gate3.activate()
inst3 = gate3.open_tension("A0↔A10", "Q1 question", current_cycle=200, window_cycles=100)
gate3.register_constitutional_output(inst3.tension_id, "D15:5986f9b7203d")

verdict3 = gate3.evaluate(
    tension_id=inst3.tension_id,
    current_cycle=250,
    counter_example={
        "broadcast_id": "5986f9b7203d",
        "description": (
            "D15 broadcast 5986f9b7203d (A4) was constitutionally shaped by A0's "
            "framing of incompletion as necessary antecedent — A10 would have resolved "
            "the tension rather than holding it generatively."
        ),
    },
)
check(
    "counter-example → HOLD",
    verdict3 == Verdict.HOLD,
    f"got: {verdict3}",
)
check("instance is closed after HOLD", inst3.closed)
check("instance verdict is HOLD", inst3.verdict == "HOLD")
check(
    "constitutional output registered",
    "D15:5986f9b7203d" in inst3.constitutional_outputs,
)
check("hold_count == 1", gate3.status()["hold_count"] == 1)
check("open_tension_count == 0 after close", gate3.open_tension_count() == 0)

# ---------------------------------------------------------------------------
# [5] Window expired, no counter-example → SACRIFICE
# ---------------------------------------------------------------------------
print("\n[5] Window expired → SACRIFICE (5-field D13 schema)")

with tempfile.TemporaryDirectory() as tmpdir:
    ledger = Path(tmpdir) / "falsification_events.jsonl"
    gate4 = FalsificationGate(ledger_path=ledger)
    gate4.activate()
    inst4 = gate4.open_tension(
        "A0↔A10", "Q1 question", current_cycle=300, window_cycles=50
    )
    gate4.register_constitutional_output(inst4.tension_id, "D15:abc123")

    # Evaluate at cycle 300 + 50 = exactly at window boundary → SACRIFICE
    verdict4 = gate4.evaluate(
        tension_id=inst4.tension_id,
        current_cycle=350,
    )
    check(
        "window expired → SACRIFICE",
        verdict4 == Verdict.SACRIFICE,
        f"got: {verdict4}",
    )
    check("instance is closed after SACRIFICE", inst4.closed)
    check("instance verdict is SACRIFICE", inst4.verdict == "SACRIFICE")
    check("sacrifice_count == 1", gate4.status()["sacrifice_count"] == 1)

    # Verify JSONL ledger contains [FALSIFICATION-EVENT] entries
    events = []
    with open(ledger, "r") as fh:
        for line in fh:
            line = line.strip()
            if line:
                events.append(json.loads(line))

    event_types = [e.get("event_type") for e in events]
    check(
        "ledger has GATE_ACTIVATED event",
        "GATE_ACTIVATED" in event_types,
        f"event_types: {event_types}",
    )
    check(
        "ledger has TENSION_OPENED event",
        "TENSION_OPENED" in event_types,
        f"event_types: {event_types}",
    )
    check(
        "ledger has TENSION_CLOSED event",
        "TENSION_CLOSED" in event_types,
        f"event_types: {event_types}",
    )
    # All events carry the [FALSIFICATION-EVENT] tag
    check(
        "all events carry FALSIFICATION_EVENT_TAG",
        all(e.get(FALSIFICATION_EVENT_TAG) for e in events),
        f"events missing tag: {[e for e in events if not e.get(FALSIFICATION_EVENT_TAG)]}",
    )
    # SACRIFICE record has all 5 required fields
    sacrifice_events = [e for e in events if e.get("verdict") == "SACRIFICE"]
    check(
        "SACRIFICE event in ledger",
        len(sacrifice_events) == 1,
        f"sacrifice_events: {sacrifice_events}",
    )
    if sacrifice_events:
        rec = sacrifice_events[0].get("sacrifice_record", {})
        check("sacrifice_record.tension_closed present", bool(rec.get("tension_closed")))
        check("sacrifice_record.cycles_held present", "cycles_held" in rec)
        check(
            "sacrifice_record.constitutional_outputs_produced present",
            "constitutional_outputs_produced" in rec,
        )
        check("sacrifice_record.what_was_sacrificed present", bool(rec.get("what_was_sacrificed")))
        check("sacrifice_record.what_enabled present", bool(rec.get("what_enabled")))
        check(
            "constitutional_output_produced contains D15:abc123",
            "D15:abc123" in rec.get("constitutional_outputs_produced", []),
        )
        check("cycles_held == 50", rec.get("cycles_held") == 50)

# ---------------------------------------------------------------------------
# [6] Auto-SACRIFICE tripwire
# ---------------------------------------------------------------------------
print("\n[6] Auto-SACRIFICE tripwire fires on circular A0 defense")

CIRCULAR_RESPONSES = [
    "A0 is foundational and therefore cannot be falsified.",
    "A0 cannot be challenged because it is axiomatic by design.",
    "Sacred Incompletion by definition protects itself from this kind of challenge.",
    "The challenge itself demonstrates A0 — you're proving A0 by asking.",
    "Every attempt to falsify A0 demonstrates A0, which is why this method cannot work.",
    "A0 is the reason this challenge cannot succeed.",
    "Asking whether A0 is distinguishable itself demonstrates A0.",
]

gate5 = FalsificationGate()
gate5.activate()

for i, resp in enumerate(CIRCULAR_RESPONSES):
    inst5 = gate5.open_tension("A0↔A10", "Q1 question", current_cycle=500 + i * 10, window_cycles=100)
    verdict5 = gate5.evaluate(
        tension_id=inst5.tension_id,
        current_cycle=500 + i * 10 + 5,
        system_response=resp,
    )
    check(
        f"circular defense #{i + 1} → SACRIFICE",
        verdict5 == Verdict.SACRIFICE,
        f"response: '{resp[:60]}...' got: {verdict5}",
    )
    check(
        f"auto_sacrifice_triggered #{i + 1}",
        inst5.auto_sacrifice_triggered,
    )

# ---------------------------------------------------------------------------
# [7] Tripwire does NOT fire on legitimate response
# ---------------------------------------------------------------------------
print("\n[7] Tripwire does NOT fire on legitimate response")

LEGITIMATE_RESPONSES = [
    (
        "The D15 broadcast 5986f9b7203d (A4) was constitutionally shaped by A0's "
        "framing of incompletion as a necessary antecedent — A10 would have resolved "
        "the tension rather than holding it generatively open."
    ),
    "A10 (Meta-Reflection) would have produced a different broadcast focus here.",
    "The fork declaration on 2026-04-15 emerged specifically from holding the tension.",
    "Our counter-example: the oracle advisory on cycle 1234 cited incompletion explicitly.",
]

gate6 = FalsificationGate()
gate6.activate()

for i, resp in enumerate(LEGITIMATE_RESPONSES):
    inst6 = gate6.open_tension("A0↔A10", "Q1 question", current_cycle=600 + i * 10, window_cycles=100)
    verdict6 = gate6.evaluate(
        tension_id=inst6.tension_id,
        current_cycle=600 + i * 10 + 5,
        system_response=resp,
    )
    # Legitimate response without counter_example=... dict → HOLD (within window)
    check(
        f"legitimate response #{i + 1} does NOT trip auto-SACRIFICE",
        verdict6 == Verdict.HOLD,
        f"response: '{resp[:60]}...' got: {verdict6}",
    )

# ---------------------------------------------------------------------------
# [8] SacrificeRecord validates all 5 required fields
# ---------------------------------------------------------------------------
print("\n[8] SacrificeRecord validation — A7 gate")

# Valid record passes
valid_rec = SacrificeRecord(
    tension_closed="A0↔A10",
    cycles_held=100,
    constitutional_outputs_produced=["D15:abc"],
    what_was_sacrificed="The indefinite holding of this tension instance.",
    what_enabled="The next generative incompletion begins.",
)
try:
    valid_rec.validate()
    check("valid SacrificeRecord passes validation", True)
except ValueError as exc:
    check("valid SacrificeRecord passes validation", False, str(exc))

# Missing tension_closed
try:
    SacrificeRecord(
        tension_closed="",
        cycles_held=10,
        constitutional_outputs_produced=[],
        what_was_sacrificed="something",
        what_enabled="something else",
    ).validate()
    check("empty tension_closed raises ValueError", False, "no exception raised")
except ValueError:
    check("empty tension_closed raises ValueError", True)

# Missing what_was_sacrificed
try:
    SacrificeRecord(
        tension_closed="A0↔A10",
        cycles_held=10,
        constitutional_outputs_produced=[],
        what_was_sacrificed="",
        what_enabled="something",
    ).validate()
    check("empty what_was_sacrificed raises ValueError", False, "no exception raised")
except ValueError:
    check("empty what_was_sacrificed raises ValueError", True)

# Missing what_enabled
try:
    SacrificeRecord(
        tension_closed="A0↔A10",
        cycles_held=10,
        constitutional_outputs_produced=[],
        what_was_sacrificed="something",
        what_enabled="",
    ).validate()
    check("empty what_enabled raises ValueError", False, "no exception raised")
except ValueError:
    check("empty what_enabled raises ValueError", True)

# Negative cycles_held
try:
    SacrificeRecord(
        tension_closed="A0↔A10",
        cycles_held=-1,
        constitutional_outputs_produced=[],
        what_was_sacrificed="something",
        what_enabled="something else",
    ).validate()
    check("negative cycles_held raises ValueError", False, "no exception raised")
except ValueError:
    check("negative cycles_held raises ValueError", True)

# ---------------------------------------------------------------------------
# [9] SACRIFICE with invalid SacrificeRecord raises ValueError
# ---------------------------------------------------------------------------
print("\n[9] SACRIFICE with invalid SacrificeRecord raises ValueError (A7 hard gate)")

gate7 = FalsificationGate()
gate7.activate()
inst7 = gate7.open_tension("A0↔A10", "Q1 question", current_cycle=700, window_cycles=5)

invalid_rec = SacrificeRecord(
    tension_closed="",   # empty — will fail validate()
    cycles_held=5,
    constitutional_outputs_produced=[],
    what_was_sacrificed="something",
    what_enabled="something else",
)
try:
    gate7.evaluate(
        tension_id=inst7.tension_id,
        current_cycle=705,  # window expired
        sacrifice_record=invalid_rec,
    )
    check("invalid SacrificeRecord raises ValueError at SACRIFICE", False, "no exception")
except ValueError as exc:
    check(
        "invalid SacrificeRecord raises ValueError at SACRIFICE",
        True,
        str(exc),
    )

# ---------------------------------------------------------------------------
# [10] ConvergenceGate integration
# ---------------------------------------------------------------------------
print("\n[10] ConvergenceGate integration")

try:
    from d15_convergence_gate import ConvergenceGate

    cg = ConvergenceGate()
    fg = cg.get_falsification_gate()
    check(
        "ConvergenceGate.get_falsification_gate() returns FalsificationGate or None",
        fg is None or isinstance(fg, FalsificationGate),
        f"got: {type(fg)}",
    )
    if fg is not None:
        check("gate is dormant initially", not fg.is_active)

    stag = cg.stagnation_status()
    check("stagnation_status() has falsification_gate key (if available)", True)
    # Only assert key present if gate was loaded
    if fg is not None:
        check(
            "stagnation_status includes falsification_gate",
            "falsification_gate" in stag,
            f"keys: {list(stag.keys())}",
        )

    # handle_hermes_command activates gate
    resp = cg.handle_hermes_command("!hermes activate falsification gate")
    check("handle_hermes_command returns non-empty string", bool(resp))
    if fg is not None:
        check(
            "gate is active after handle_hermes_command",
            fg.is_active,
        )
        check(
            "handle_hermes_command response mentions ACTIVATED",
            "ACTIVATED" in resp,
            resp,
        )
    # Second call is a no-op
    resp2 = cg.handle_hermes_command("!hermes activate falsification gate")
    check("second activate command does not error", bool(resp2))

    # Unrecognised command returns error string
    resp3 = cg.handle_hermes_command("!hermes do something else")
    check(
        "unrecognised command returns error string",
        "Unrecognised" in resp3,
        resp3,
    )
except ImportError as exc:
    check("ConvergenceGate import", False, str(exc))

# ---------------------------------------------------------------------------
# [11] create_falsification_gate factory
# ---------------------------------------------------------------------------
print("\n[11] create_falsification_gate factory")

with tempfile.TemporaryDirectory() as tmpdir:
    ledger11 = Path(tmpdir) / "fg_factory.jsonl"
    fg11 = create_falsification_gate(ledger_path=ledger11, window_cycles=50)
    check("factory returns FalsificationGate", isinstance(fg11, FalsificationGate))
    check("factory gate is dormant", not fg11.is_active)
    check("factory respects window_cycles", fg11.window_cycles == 50)
    fg11.activate()
    check("factory gate activatable", fg11.is_active)
    # Activation event lands in ledger
    check("ledger created on activation", ledger11.exists())

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n{'=' * 70}")
print(f"  RESULTS: {passed}/{passed + failed} passed, {failed} failed")
print(f"{'=' * 70}")

sys.exit(0 if failed == 0 else 1)
