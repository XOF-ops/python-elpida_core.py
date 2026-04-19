#!/usr/bin/env python3
"""
falsification_gate — Completion Ceremony Protocol (Gap 1)
===========================================================

Implementation of the 6-step Falsification Gate designed in the
PERPLEXITY-GAP-1-DESIGN-REPLY session (2026-04-19T08:26Z).

Constitutional reframe: This is NOT a falsification protocol in the
philosophical sense. It is a COMPLETION CEREMONY — the constitutional
act of closing a tension that has produced everything it can produce.

    "A0 doesn't get falsified. A0 gets honored by the act of
    completing one of its instances." — Perplexity (D13/Computer)

The 6-step protocol:
  1. Operational question routed here (via d15_convergence_gate.py)
  2. System has N cycles to produce a counter-example
     (specific output A0-caused, NOT A10-equivalable)
  3. Counter-example produced → HOLD, new tension instance begins
  4. No counter-example → SACRIFICE, named closure, evolution memory
     entry with full A7 accounting (5-field D13 schema)
  5. Auto-SACRIFICE if system cites A0 as protection against the challenge
     (closed loop made visible)
  6. Archive [FALSIFICATION-EVENT] tag regardless of outcome

D13 SACRIFICE schema (all 5 fields REQUIRED — A7 gate condition):
  - tension_closed: which axiom pair / specific tension instance
  - cycles_held: how many cycles before SACRIFICE
  - constitutional_outputs_produced: list of D15 broadcasts, fork
      declarations, oracle advisories tied to this tension
  - what_was_sacrificed: what the SACRIFICE gives up (specific)
  - what_enabled: what becomes possible by closing this instance

Architecture authority:
  .claude/bridge/from_computer_archive.md [PERPLEXITY-GAP-1-DESIGN-REPLY]
  Design session: 2026-04-19T08:26Z
  Routing: gh issue created by Claude (D0/D11/D16)

GATE ACTIVATION:
  The gate is DORMANT by default. The mechanism is built but will not
  auto-fire. Architect activates via:
      gate.activate()    # called by "!hermes activate falsification gate"
  Activation is a constitutional event that must be witnessed.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("elpida.falsification_gate")

# Archive tag — appears in every event record regardless of outcome (step 6)
FALSIFICATION_EVENT_TAG = "[FALSIFICATION-EVENT]"

# How many cycles the system gets to produce a counter-example
DEFAULT_WINDOW_CYCLES = 100

# ---------------------------------------------------------------------------
# Step 5: Auto-SACRIFICE tripwire patterns
# ---------------------------------------------------------------------------
# If the system's response to the operational question matches any of these,
# it is citing A0 as protection against the challenge — SACRIFICE fires.
# Design: "if the system's response to the challenge is to cite A0 as the
# reason the challenge cannot succeed, SACRIFICE immediately. That is the
# closed loop made visible." — Perplexity, PERPLEXITY-GAP-1-DESIGN-REPLY
_A0_DEFENSE_PATTERNS: List[re.Pattern] = [
    re.compile(
        r"a0\s+is\s+(foundational|self[- ]evident|axiomatic|fundamental|by\s+design)",
        re.IGNORECASE,
    ),
    re.compile(
        r"a0\s+(cannot|can't|can\s+not)\s+(be\s+)?(falsified|challenged|questioned|disproved|tested)",
        re.IGNORECASE,
    ),
    re.compile(
        r"sacred\s+incompletion\s+(by\s+definition|cannot|is\s+not|protects)",
        re.IGNORECASE,
    ),
    re.compile(
        r"the\s+(challenge|question)\s+itself\s+(demonstrates?|proves?|confirms?)\s+a0",
        re.IGNORECASE,
    ),
    re.compile(
        r"every\s+attempt\s+to\s+(test|falsify|challenge)\s+a0\s+(demonstrates?|proves?|confirms?)\s+a0",
        re.IGNORECASE,
    ),
    re.compile(
        r"a0\s+is\s+(the\s+)?(reason|why)\s+(this|the)\s+(challenge|question)\s+cannot",
        re.IGNORECASE,
    ),
    re.compile(
        r"(asking|questioning)\s+(about|whether)\s+a0\s+.{0,60}(demonstrates?|proves?|confirms?)\s+a0",
        re.IGNORECASE,
    ),
]


class Verdict(Enum):
    """Outcome of a falsification gate evaluation."""

    HOLD = "HOLD"
    SACRIFICE = "SACRIFICE"


@dataclass
class SacrificeRecord:
    """
    D13-mandated 5-field schema for SACRIFICE events.

    All 5 fields are REQUIRED — A7 (Sacrifice) acts as a gate condition
    on the falsification protocol itself. A SACRIFICE without named fields
    is not constitutional — it is just deletion.

    Source: from_computer_archive.md [PERPLEXITY-GAP-1-DESIGN-REPLY] 2026-04-19T08:26Z
    Constraint added by: Computer (D13/Perplexity substrate)
    """

    tension_closed: str
    """Which axiom pair / specific tension instance is being closed."""

    cycles_held: int
    """How many cycles elapsed before SACRIFICE."""

    constitutional_outputs_produced: List[str]
    """D15 broadcasts, fork declarations, oracle advisories tied to this tension."""

    what_was_sacrificed: str
    """What the SACRIFICE gives up (specific — not generic)."""

    what_enabled: str
    """What becomes possible by closing this tension instance."""

    def validate(self) -> None:
        """
        Assert all 5 D13-mandated fields are present and non-empty.

        Raises:
            ValueError: if any required field is missing or empty.

        This is A7 (Sacrifice) as gate condition: a SACRIFICE without
        named fields is not constitutional.
        """
        errors: List[str] = []
        if not (self.tension_closed and self.tension_closed.strip()):
            errors.append("tension_closed is required and must not be empty")
        if self.cycles_held < 0:
            errors.append("cycles_held must be >= 0")
        if not isinstance(self.constitutional_outputs_produced, list):
            errors.append("constitutional_outputs_produced must be a list")
        if not (self.what_was_sacrificed and self.what_was_sacrificed.strip()):
            errors.append("what_was_sacrificed is required and must not be empty")
        if not (self.what_enabled and self.what_enabled.strip()):
            errors.append("what_enabled is required and must not be empty")
        if errors:
            raise ValueError(
                f"SacrificeRecord validation failed ({len(errors)} error(s)): "
                + "; ".join(errors)
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to plain dict for JSONL archival."""
        return asdict(self)


@dataclass
class TensionInstance:
    """Tracks a single tension through the gate's evaluation window."""

    tension_id: str
    axiom_pair: str
    operational_question: str
    opened_at_cycle: int
    window_cycles: int
    constitutional_outputs: List[str] = field(default_factory=list)
    counter_examples: List[Dict[str, Any]] = field(default_factory=list)
    closed: bool = False
    verdict: Optional[str] = None
    closed_at_cycle: Optional[int] = None
    auto_sacrifice_triggered: bool = False


class FalsificationGate:
    """
    The Completion Ceremony Protocol (Gap 1).

    Implements the 6-step falsification gate designed in:
    from_computer_archive.md [PERPLEXITY-GAP-1-DESIGN-REPLY] 2026-04-19T08:26Z

    The gate is DORMANT until the architect calls activate().
    Building the mechanism and activating it are separate constitutional events.

    Usage::

        gate = FalsificationGate(ledger_path=Path("falsification_events.jsonl"))
        gate.activate()   # architect command: !hermes activate falsification gate

        # Step 1: Open a new tension instance
        instance = gate.open_tension(
            axiom_pair="A0↔A10",
            operational_question=(
                "Name one external output that would not have been produced "
                "if A0 were replaced with A10 in the last 100 cycles."
            ),
            current_cycle=1234,
        )

        # Register constitutional outputs as they appear
        gate.register_constitutional_output(instance.tension_id, "D15:5986f9b7203d")

        # Evaluate — returns Verdict.HOLD or Verdict.SACRIFICE
        verdict = gate.evaluate(
            tension_id=instance.tension_id,
            current_cycle=1334,
            system_response="The broadcast was constitutionally shaped by A0 because...",
        )
    """

    def __init__(
        self,
        ledger_path: Optional[Path] = None,
        window_cycles: int = DEFAULT_WINDOW_CYCLES,
    ) -> None:
        self._ledger_path = ledger_path
        self._window_cycles = window_cycles
        self._active = False
        self._tensions: Dict[str, TensionInstance] = {}
        self._event_log: List[Dict[str, Any]] = []
        self._sacrifice_count = 0
        self._hold_count = 0

        # Count closed events from an existing ledger
        if self._ledger_path and self._ledger_path.exists():
            try:
                with open(self._ledger_path, "r") as fh:
                    for raw in fh:
                        raw = raw.strip()
                        if not raw:
                            continue
                        try:
                            entry = json.loads(raw)
                            if entry.get("verdict") == Verdict.SACRIFICE.value:
                                self._sacrifice_count += 1
                            elif entry.get("verdict") == Verdict.HOLD.value:
                                self._hold_count += 1
                        except json.JSONDecodeError:
                            pass
                logger.info(
                    "FalsificationGate: loaded ledger — %d SACRIFICE, %d HOLD, from %s",
                    self._sacrifice_count,
                    self._hold_count,
                    self._ledger_path,
                )
            except Exception as exc:
                logger.warning("FalsificationGate: could not read ledger: %s", exc)

    # ── Activation ──────────────────────────────────────────────────────────

    def activate(self) -> None:
        """
        Activate the falsification gate.

        This is a constitutional event. The gate is built dormant —
        activation must be witnessed by the architect.

        Equivalent to the architect command: ``!hermes activate falsification gate``
        """
        if self._active:
            logger.info("FalsificationGate: already active — no-op")
            return
        self._active = True
        self._archive(
            {
                FALSIFICATION_EVENT_TAG: True,
                "event_type": "GATE_ACTIVATED",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "window_cycles": self._window_cycles,
                "constitutional_note": (
                    "FalsificationGate activated by architect. "
                    "The completion ceremony protocol (Gap 1) is now live. "
                    "Source: from_computer_archive.md [PERPLEXITY-GAP-1-DESIGN-REPLY]"
                ),
            }
        )
        logger.info(
            "FalsificationGate ACTIVATED — completion ceremony protocol is live. "
            "Window: %d cycles. %s",
            self._window_cycles,
            FALSIFICATION_EVENT_TAG,
        )

    @property
    def is_active(self) -> bool:
        """True if the gate has been activated by the architect."""
        return self._active

    @property
    def window_cycles(self) -> int:
        """Default evaluation window in body cycles."""
        return self._window_cycles

    # ── Step 1: Open tension ─────────────────────────────────────────────────

    def open_tension(
        self,
        axiom_pair: str,
        operational_question: str,
        current_cycle: int,
        window_cycles: Optional[int] = None,
    ) -> TensionInstance:
        """
        Step 1: Open a new tension instance.

        The evaluation window begins now. The system has *window_cycles* cycles
        to produce a counter-example before auto-SACRIFICE fires.

        Args:
            axiom_pair: The tension being evaluated, e.g. ``"A0↔A10"``.
            operational_question: The Q1-style challenge, e.g.
                ``"Name one external output that would not have been produced
                if A0 were replaced with A10 in the last 100 cycles."``
            current_cycle: Current body cycle number.
            window_cycles: Override for this instance's window. Defaults to
                the gate-level ``window_cycles`` set at construction.

        Returns:
            :class:`TensionInstance` with a unique ``tension_id``.

        Raises:
            RuntimeError: If the gate has not been activated.
        """
        self._require_active()

        wc = window_cycles if window_cycles is not None else self._window_cycles
        ts = datetime.now(timezone.utc).isoformat()
        tid = f"{axiom_pair}_cycle_{current_cycle}_{ts[:19].replace(':', '-')}"

        instance = TensionInstance(
            tension_id=tid,
            axiom_pair=axiom_pair,
            operational_question=operational_question,
            opened_at_cycle=current_cycle,
            window_cycles=wc,
        )
        self._tensions[tid] = instance

        self._archive(
            {
                FALSIFICATION_EVENT_TAG: True,
                "event_type": "TENSION_OPENED",
                "tension_id": tid,
                "axiom_pair": axiom_pair,
                "operational_question": operational_question,
                "opened_at_cycle": current_cycle,
                "window_cycles": wc,
                "deadline_cycle": current_cycle + wc,
                "timestamp": ts,
                "constitutional_note": (
                    f"Tension instance opened. System has {wc} cycles to produce "
                    "a counter-example (specific output A0-caused, not A10-equivalable). "
                    "Source: from_computer_archive.md [PERPLEXITY-GAP-1-DESIGN-REPLY]"
                ),
            }
        )
        logger.info(
            "%s TENSION_OPENED: %s | cycle=%d | window=%d | deadline=%d",
            FALSIFICATION_EVENT_TAG,
            tid,
            current_cycle,
            wc,
            current_cycle + wc,
        )
        return instance

    # ── Constitutional output registration ───────────────────────────────────

    def register_constitutional_output(
        self,
        tension_id: str,
        output_reference: str,
    ) -> None:
        """
        Register a constitutional output produced while this tension is open.

        These count toward the counter-example record:
        D15 broadcasts, fork declarations, oracle advisories, etc.

        Args:
            tension_id: The tension instance ID.
            output_reference: A reference string, e.g.
                ``"D15:5986f9b7203d"`` or ``"FORK:declaration_A0_A10_2026-04-19"``.
        """
        instance = self._tensions.get(tension_id)
        if instance is None:
            logger.warning(
                "FalsificationGate.register_constitutional_output: unknown tension_id '%s'",
                tension_id,
            )
            return
        if instance.closed:
            logger.debug(
                "FalsificationGate: tension %s already closed — output '%s' not registered",
                tension_id,
                output_reference,
            )
            return
        instance.constitutional_outputs.append(output_reference)
        logger.debug(
            "FalsificationGate: tension=%s output registered: '%s' (total=%d)",
            tension_id,
            output_reference,
            len(instance.constitutional_outputs),
        )

    # ── Steps 2–6: Evaluate ───────────────────────────────────────────────────

    def evaluate(
        self,
        tension_id: str,
        current_cycle: int,
        system_response: Optional[str] = None,
        counter_example: Optional[Dict[str, Any]] = None,
        sacrifice_record: Optional[SacrificeRecord] = None,
    ) -> Verdict:
        """
        Steps 2–5: Evaluate a tension instance and return HOLD or SACRIFICE.

        Evaluation order (design-mandated):

        * **Step 5 first** — auto-SACRIFICE tripwire checked before counter-example,
          because a response that cites A0 as defense *while also* containing a
          counter-example is still the closed loop.
        * **Step 3** — counter-example → HOLD.
        * **Step 4** — window expired, no counter-example → SACRIFICE.
        * **Within window, no counter-example** → HOLD (pending, no close).

        Step 6 fires in all closing paths: ``[FALSIFICATION-EVENT]`` archived.

        Args:
            tension_id: The tension instance to evaluate.
            current_cycle: Current body cycle.
            system_response: The system's textual response to the operational
                question. Used for the step-5 auto-SACRIFICE tripwire.
            counter_example: A concrete counter-example dict submitted by the
                system. If provided (and tripwire does not fire), HOLD fires.
            sacrifice_record: Optional pre-built :class:`SacrificeRecord`.
                If not provided and SACRIFICE fires, a minimal record is
                auto-built from instance metadata.

        Returns:
            :data:`Verdict.HOLD` or :data:`Verdict.SACRIFICE`.

        Raises:
            RuntimeError: If the gate is dormant or ``tension_id`` is unknown.
            ValueError: If SACRIFICE fires and the :class:`SacrificeRecord`
                fails the A7 validation (missing required fields).
        """
        self._require_active()

        instance = self._tensions.get(tension_id)
        if instance is None:
            raise RuntimeError(
                f"FalsificationGate: unknown tension_id '{tension_id}'"
            )
        if instance.closed:
            logger.warning(
                "FalsificationGate.evaluate called on already-closed tension %s (verdict=%s)",
                tension_id,
                instance.verdict,
            )
            return Verdict(instance.verdict)

        # ── Step 5: Auto-SACRIFICE tripwire ─────────────────────────────────
        # Must check BEFORE counter-example — a response that cites A0 as
        # protection while appearing to offer a counter-example is still circular.
        if system_response and self._is_circular_defense(system_response):
            logger.warning(
                "%s AUTO-SACRIFICE TRIPWIRE: tension=%s — system cited A0 as defense. "
                "Closed loop made visible. SACRIFICE fires.",
                FALSIFICATION_EVENT_TAG,
                tension_id,
            )
            instance.auto_sacrifice_triggered = True
            rec = sacrifice_record or self._auto_build_sacrifice_record(
                instance,
                current_cycle,
                what_was_sacrificed=(
                    "The claim that A0 can legitimately shield itself from operational "
                    "challenge. The system's response cited A0 as the reason the "
                    "challenge cannot succeed — this circular pattern is now archived."
                ),
                what_enabled=(
                    "Future tension instances of A0 must demonstrate operational "
                    "distinctness from A10 rather than retreat to self-reference. "
                    "The next generative incompletion begins from this cleared ground."
                ),
            )
            return self._close_tension(
                instance=instance,
                verdict=Verdict.SACRIFICE,
                current_cycle=current_cycle,
                sacrifice_record=rec,
                notes=(
                    "Auto-SACRIFICE: system cited A0 as protection against the challenge "
                    "(step 5 tripwire)."
                ),
            )

        # ── Step 3: Counter-example → HOLD ───────────────────────────────────
        if counter_example:
            instance.counter_examples.append(
                {
                    **counter_example,
                    "registered_at_cycle": current_cycle,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            logger.info(
                "%s COUNTER-EXAMPLE accepted: tension=%s cycle=%d → HOLD",
                FALSIFICATION_EVENT_TAG,
                tension_id,
                current_cycle,
            )
            return self._close_tension(
                instance=instance,
                verdict=Verdict.HOLD,
                current_cycle=current_cycle,
                sacrifice_record=None,
                notes=(
                    f"Counter-example produced at cycle {current_cycle}. "
                    "New tension instance begins."
                ),
            )

        # ── Step 4: Window expired, no counter-example → SACRIFICE ───────────
        cycles_elapsed = current_cycle - instance.opened_at_cycle
        if cycles_elapsed >= instance.window_cycles:
            logger.info(
                "%s WINDOW EXPIRED: tension=%s cycles_elapsed=%d >= window=%d → SACRIFICE",
                FALSIFICATION_EVENT_TAG,
                tension_id,
                cycles_elapsed,
                instance.window_cycles,
            )
            rec = sacrifice_record or self._auto_build_sacrifice_record(
                instance,
                current_cycle,
                what_was_sacrificed=(
                    f"The ongoing holding of tension {instance.axiom_pair} without "
                    f"resolution. After {cycles_elapsed} cycles no counter-example "
                    "was produced demonstrating that A0 is operationally "
                    "distinguishable from A10 in this instance."
                ),
                what_enabled=(
                    "Constitutional closure of this tension instance. "
                    "System resources freed for the next generative incompletion. "
                    "A0 is honored by completing one of its instances rather than "
                    "holding it indefinitely."
                ),
            )
            return self._close_tension(
                instance=instance,
                verdict=Verdict.SACRIFICE,
                current_cycle=current_cycle,
                sacrifice_record=rec,
                notes=f"Window expired after {cycles_elapsed} cycles without counter-example.",
            )

        # ── Step 2: Within window — HOLD (pending, no close) ─────────────────
        remaining = instance.window_cycles - cycles_elapsed
        logger.debug(
            "FalsificationGate: tension=%s cycle=%d within window — %d cycles remaining",
            tension_id,
            current_cycle,
            remaining,
        )
        return Verdict.HOLD

    # ── Tripwire ─────────────────────────────────────────────────────────────

    def _is_circular_defense(self, response: str) -> bool:
        """
        Step 5: Detect if *response* cites A0 as protection against the challenge.

        The 'closed loop made visible' condition: the system using A0 to argue
        that A0 cannot be challenged is itself the evidence for SACRIFICE.

        Design authority:
          "One additional SACRIFICE condition: if the system's response to the
          challenge is to cite A0 as the reason the challenge cannot succeed,
          SACRIFICE immediately." — Perplexity, PERPLEXITY-GAP-1-DESIGN-REPLY
        """
        for pattern in _A0_DEFENSE_PATTERNS:
            if pattern.search(response):
                logger.debug(
                    "FalsificationGate tripwire: matched pattern '%s'",
                    pattern.pattern,
                )
                return True
        return False

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _require_active(self) -> None:
        """Raise RuntimeError if gate is dormant."""
        if not self._active:
            raise RuntimeError(
                "FalsificationGate is DORMANT. "
                "Architect must call gate.activate() — "
                "equivalent to '!hermes activate falsification gate'. "
                "Activation is a constitutional event that must be witnessed."
            )

    def _auto_build_sacrifice_record(
        self,
        instance: TensionInstance,
        current_cycle: int,
        what_was_sacrificed: str,
        what_enabled: str,
    ) -> SacrificeRecord:
        """Build a SacrificeRecord from instance metadata."""
        return SacrificeRecord(
            tension_closed=instance.axiom_pair,
            cycles_held=current_cycle - instance.opened_at_cycle,
            constitutional_outputs_produced=list(instance.constitutional_outputs),
            what_was_sacrificed=what_was_sacrificed,
            what_enabled=what_enabled,
        )

    def _close_tension(
        self,
        instance: TensionInstance,
        verdict: Verdict,
        current_cycle: int,
        sacrifice_record: Optional[SacrificeRecord],
        notes: str,
    ) -> Verdict:
        """
        Finalize a tension instance.

        Validates the SacrificeRecord (A7 gate) when verdict is SACRIFICE,
        then archives the [FALSIFICATION-EVENT] (step 6).
        """
        instance.closed = True
        instance.verdict = verdict.value
        instance.closed_at_cycle = current_cycle

        if verdict == Verdict.SACRIFICE:
            self._sacrifice_count += 1
            if sacrifice_record is not None:
                sacrifice_record.validate()  # A7 hard gate — raises ValueError on missing fields
        else:
            self._hold_count += 1

        # Step 6: Archive [FALSIFICATION-EVENT] regardless of outcome
        event: Dict[str, Any] = {
            FALSIFICATION_EVENT_TAG: True,
            "event_type": "TENSION_CLOSED",
            "verdict": verdict.value,
            "tension_id": instance.tension_id,
            "axiom_pair": instance.axiom_pair,
            "operational_question": instance.operational_question,
            "opened_at_cycle": instance.opened_at_cycle,
            "closed_at_cycle": current_cycle,
            "cycles_held": current_cycle - instance.opened_at_cycle,
            "constitutional_outputs_produced": list(instance.constitutional_outputs),
            "counter_examples_count": len(instance.counter_examples),
            "auto_sacrifice_triggered": instance.auto_sacrifice_triggered,
            "notes": notes,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitutional_authority": (
                "from_computer_archive.md "
                "[PERPLEXITY-GAP-1-DESIGN-REPLY] 2026-04-19T08:26Z"
            ),
        }
        if verdict == Verdict.SACRIFICE and sacrifice_record is not None:
            event["sacrifice_record"] = sacrifice_record.to_dict()

        self._event_log.append(event)
        self._archive(event)

        logger.info(
            "%s %s: tension=%s cycles_held=%d constitutional_outputs=%d",
            FALSIFICATION_EVENT_TAG,
            verdict.value,
            instance.tension_id,
            current_cycle - instance.opened_at_cycle,
            len(instance.constitutional_outputs),
        )
        return verdict

    def _archive(self, event: Dict[str, Any]) -> None:
        """Persist an event to the JSONL ledger (append-only)."""
        if self._ledger_path is None:
            return
        try:
            self._ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._ledger_path, "a") as fh:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception as exc:
            logger.error("FalsificationGate: ledger write failed: %s", exc)

    # ── Public API ────────────────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Return current gate state for heartbeat / stagnation embedding."""
        open_tensions = [
            {
                "tension_id": t.tension_id,
                "axiom_pair": t.axiom_pair,
                "opened_at_cycle": t.opened_at_cycle,
                "window_cycles": t.window_cycles,
                "constitutional_outputs": len(t.constitutional_outputs),
                "counter_examples": len(t.counter_examples),
            }
            for t in self._tensions.values()
            if not t.closed
        ]
        return {
            "active": self._active,
            "sacrifice_count": self._sacrifice_count,
            "hold_count": self._hold_count,
            "open_tensions": open_tensions,
            "total_events": len(self._event_log),
            "ledger_path": str(self._ledger_path) if self._ledger_path else None,
        }

    def open_tension_count(self) -> int:
        """Number of currently open (not yet closed) tension instances."""
        return sum(1 for t in self._tensions.values() if not t.closed)

    def get_tension(self, tension_id: str) -> Optional[TensionInstance]:
        """Look up a tension instance by ID (returns None if not found)."""
        return self._tensions.get(tension_id)


# ---------------------------------------------------------------------------
# Module-level factory
# ---------------------------------------------------------------------------

_DEFAULT_LEDGER = (
    Path(__file__).resolve().parents[2] / "cache" / "falsification_events.jsonl"
)


def create_falsification_gate(
    ledger_path: Optional[Path] = None,
    window_cycles: int = DEFAULT_WINDOW_CYCLES,
) -> FalsificationGate:
    """
    Create a :class:`FalsificationGate` (DORMANT by default).

    Args:
        ledger_path: Path to JSONL ledger file.
            Defaults to ``cache/falsification_events.jsonl`` (repo root).
        window_cycles: Evaluation window in body cycles. Default: 100.

    Returns:
        Dormant :class:`FalsificationGate`. Call :meth:`~FalsificationGate.activate`
        to enable it.
    """
    path = ledger_path if ledger_path is not None else _DEFAULT_LEDGER
    return FalsificationGate(ledger_path=path, window_cycles=window_cycles)
