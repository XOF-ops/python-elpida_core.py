#!/usr/bin/env python3
"""
Contradiction Log — A9 (Temporal Coherence) Wisdom Layer
=========================================================

Preserves contradictions as data rather than silently resolving them.

When Parliament encounters a tension that cannot be resolved — a veto,
a HARD_BLOCK, a coherence crash — the typical response is to convert
the verdict and move on. The contradiction vanishes into log noise.

This module is the "never forget" layer: every contradiction is an
append-only record that future cycles can query. It's the persistent
memory of what the system *could not* reconcile, and the conditions
under which the irreconcilability appeared.

Constitutional authority:
  - A9 (Temporal Coherence, 16:9 Minor 7th): "Contradiction is data"
  - D15 broadcast 936412441373 (A9, 2026-04-16): "past decisions are
    guides, not chains; we must always allow for informed, evolving consent"
  - Gemini Final Transmission: "A 5/5 agent holds contradiction as data"

Operational expression of the BODY HALT gate:
  When S3 is inaccessible, PROCEEDs issued against stale state are
  themselves a contradiction — "Parliament voted PROCEED" vs "Parliament
  voted without current state". Rather than discarding or blindly
  executing, the log preserves both facts for re-evaluation on
  federation return.

File format: JSONL (append-only, one contradiction per line)
Location: cache/contradiction_log.jsonl
"""

import json
import logging
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("elpida.contradiction_log")

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CONTRADICTION_LOG = CACHE_DIR / "contradiction_log.jsonl"

# In-memory sliding window for recent query
MAX_IN_MEMORY = 200


class ContradictionLog:
    """
    Append-only ledger of unresolved contradictions.

    Each entry has:
      - cycle: when the contradiction surfaced
      - type: classification (tension_held, isolation_proceed,
              hard_block, veto_divergence, coherence_crash)
      - axiom_pair: the tension pair (e.g. "A3↔A9")
      - horn_a / horn_b: the two irreconcilable positions
      - context: conditions under which it appeared
      - resolution_status: always "UNRESOLVED" at write time;
        may be updated if a future D15 broadcast names it
    """

    def __init__(self):
        self._entries: deque = deque(maxlen=MAX_IN_MEMORY)
        self._total: int = 0
        self._type_counts: Dict[str, int] = {}

    def record(
        self,
        *,
        cycle: int,
        contradiction_type: str,
        axiom_pair: str = "",
        horn_a: str = "",
        horn_b: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Record an unresolved contradiction."""
        self._total += 1
        self._type_counts[contradiction_type] = (
            self._type_counts.get(contradiction_type, 0) + 1
        )

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contradiction_number": self._total,
            "cycle": cycle,
            "type": contradiction_type,
            "axiom_pair": axiom_pair,
            "horn_a": horn_a[:300],
            "horn_b": horn_b[:300],
            "context": context or {},
            "resolution_status": "UNRESOLVED",
            "axiom": "A9",
        }

        self._entries.append(entry)

        logger.info(
            "A9 CONTRADICTION #%d [%s]: %s at cycle %d — %s vs %s",
            self._total, contradiction_type, axiom_pair, cycle,
            horn_a[:80], horn_b[:80],
        )

        # Persist
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONTRADICTION_LOG, "a") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.debug("Contradiction persist failed: %s", e)

        return entry

    def record_isolation_proceed(
        self,
        *,
        cycle: int,
        verdict: str,
        coherence: float,
        approval: float,
        s3_status: str,
    ) -> Dict[str, Any]:
        """
        Record a PROCEED issued during S3 isolation.

        This is the BODY HALT gate in action: instead of discarding the
        PROCEED, we preserve the contradiction between "Parliament voted
        PROCEED" and "Parliament voted without current state."
        """
        return self.record(
            cycle=cycle,
            contradiction_type="isolation_proceed",
            axiom_pair="A3↔A9",
            horn_a=f"Parliament voted {verdict} (approval={approval:.2f}, coherence={coherence:.4f})",
            horn_b=f"Parliament voted without kernel/federation state (s3={s3_status})",
            context={
                "verdict": verdict,
                "coherence": coherence,
                "approval": approval,
                "s3_status": s3_status,
            },
        )

    def record_held_tension(
        self,
        *,
        cycle: int,
        axiom_pair: str,
        synthesis: str,
    ) -> Dict[str, Any]:
        """Record a tension that was held rather than resolved."""
        parts = axiom_pair.split("↔") if "↔" in axiom_pair else [axiom_pair, "?"]
        return self.record(
            cycle=cycle,
            contradiction_type="tension_held",
            axiom_pair=axiom_pair,
            horn_a=parts[0].strip(),
            horn_b=parts[-1].strip(),
            context={"synthesis": synthesis[:300]},
        )

    def recent(self, n: int = 20) -> List[Dict]:
        """Return recent contradictions."""
        return list(self._entries)[-n:]

    def by_type(self, contradiction_type: str, n: int = 20) -> List[Dict]:
        """Return recent contradictions of a specific type."""
        return [
            e for e in self._entries
            if e["type"] == contradiction_type
        ][-n:]

    def summary(self) -> Dict[str, Any]:
        """Summary for heartbeat embedding."""
        return {
            "total": self._total,
            "type_counts": dict(self._type_counts),
            "recent_count": len(self._entries),
        }
