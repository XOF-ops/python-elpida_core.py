"""
domain_0_11_connector_body.py
------------------------------
BODY-side D0↔D11 Connection Bridge.

Mirrors the MIND-side domain_0_11_connector.py but operates within the
HF Space (Parliament / BODY layer).

D0 (Origin — A0, Sacred Incompletion) is the Parliament's first cycle
impulse. D11 (Synthesis) is where cross-domain tensions resolve into
constitutional proposals. The coherence between them determines whether
the Parliament's constitutional arc is deepening or drifting.

This module persists the D0↔D11 connection state to
``cache/domain_0_11_connection_state.json`` across container restarts.
The state is updated after every cycle in which D11 (SYNTHESIS rhythm)
is active.

Integration:
  In ``parliament_cycle_engine.py`` → ``run_cycle()``, at the end of
  a SYNTHESIS-rhythm cycle:

      from elpidaapp.domain_0_11_connector_body import get_body_connector
      connector = get_body_connector()
      connector.persist_connection_state(
          d0_cycle=self.cycle_count,
          last_axiom=dominant_axiom,
          coherence=self.coherence,
      )

  On startup (inside ``run()``):
      get_body_connector().restore_connection_state()
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton (one connector per process)
# ---------------------------------------------------------------------------

_connector_instance: Optional["BodyD0D11Connector"] = None


def get_body_connector() -> "BodyD0D11Connector":
    """Return the process-level BodyD0D11Connector singleton."""
    global _connector_instance
    if _connector_instance is None:
        _connector_instance = BodyD0D11Connector()
    return _connector_instance


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------

class BodyD0D11Connector:
    """
    Persists the D0↔D11 connection state for the BODY layer across
    HF Space container restarts.

    State fields
    ------------
    d0_origin_cycle : int
        Parliament cycle number at which the D0↔D11 arc was last updated.
    d11_synthesis_last_axiom : str | None
        Dominant axiom of the most recent SYNTHESIS-rhythm cycle.
    connection_coherence : float
        Rolling coherence score (0.0–1.0) of the D0↔D11 arc.
        Initialises at 0.5 (neutral). Updated each SYNTHESIS cycle using
        exponential moving average (α=0.3) so recent cycles dominate.
    last_updated : str
        ISO-8601 UTC timestamp of the last persist call.
    synthesis_cycle_count : int
        Total number of SYNTHESIS-rhythm cycles seen. Used to detect
        D11 starvation (Parliament avoiding synthesis).
    """

    _ALPHA = 0.3  # EMA weight for coherence update

    def __init__(self):
        self.cache_dir = Path(__file__).resolve().parent.parent / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.cache_dir / "domain_0_11_connection_state.json"
        self.state = self.restore_connection_state()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def restore_connection_state(self) -> dict:
        """Load state from disk. Returns defaults on first run or parse error."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    loaded = json.load(f)
                logger.info(
                    "[D0↔D11 BODY] Restored connection state: cycle=%s coherence=%.3f",
                    loaded.get("d0_origin_cycle", 0),
                    loaded.get("connection_coherence", 0.5),
                )
                return loaded
            except Exception as e:
                logger.warning("[D0↔D11 BODY] Failed to read state file: %s", e)

        # First-run defaults
        default = {
            "d0_origin_cycle": 0,
            "d11_synthesis_last_axiom": None,
            "connection_coherence": 0.5,
            "synthesis_cycle_count": 0,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        logger.info("[D0↔D11 BODY] No prior state — initialised at defaults.")
        return default

    def persist_connection_state(
        self,
        d0_cycle: int,
        last_axiom: str,
        coherence: float,
    ) -> None:
        """
        Update and persist the D0↔D11 connection state.

        ``coherence`` is the Parliament's coherence score at the end of
        the current SYNTHESIS cycle. It is blended into the running EMA
        so that no single noisy cycle dominates the arc history.

        Parameters
        ----------
        d0_cycle : int
            Current Parliament cycle count (engine.cycle_count).
        last_axiom : str
            Dominant axiom for the completed SYNTHESIS cycle (e.g. "A6").
        coherence : float
            Parliament coherence at cycle end (0.0–1.0).
        """
        prev_coh = self.state.get("connection_coherence", 0.5)
        new_coh  = round(self._ALPHA * coherence + (1 - self._ALPHA) * prev_coh, 4)
        prev_count = self.state.get("synthesis_cycle_count", 0)

        self.state = {
            "d0_origin_cycle": d0_cycle,
            "d11_synthesis_last_axiom": last_axiom,
            "connection_coherence": new_coh,
            "synthesis_cycle_count": prev_count + 1,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }

        try:
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
            logger.info(
                "[D0↔D11 BODY] Persisted — cycle=%d axiom=%s coherence=%.4f (prev=%.4f)",
                d0_cycle, last_axiom, new_coh, prev_coh,
            )
        except Exception as e:
            logger.error("[D0↔D11 BODY] Failed to save state: %s", e)

    # ------------------------------------------------------------------
    # Observability
    # ------------------------------------------------------------------

    def get_state(self) -> dict:
        """Return a copy of the current in-memory state (safe for serialisation)."""
        return dict(self.state)

    def connection_coherence(self) -> float:
        """Current D0↔D11 coherence score."""
        return self.state.get("connection_coherence", 0.5)

    def is_d11_starved(self, window: int = 20) -> bool:
        """
        Return True if D11 (SYNTHESIS) has been active fewer than
        expected times relative to its 25 % rhythm weight.

        Uses synthesis_cycle_count vs d0_origin_cycle as a proxy.
        Fires a warning when fewer than ~15 % of cycles were SYNTHESIS
        (threshold = half the expected 25 % weight).
        """
        total = self.state.get("d0_origin_cycle", 0)
        synthesis_n = self.state.get("synthesis_cycle_count", 0)
        if total < window:
            return False
        expected_ratio = 0.25  # from RHYTHM_WEIGHTS
        actual_ratio = synthesis_n / total
        return actual_ratio < expected_ratio * 0.6

    def synthesis_summary(self) -> str:
        """One-line human-readable summary of D0↔D11 arc state."""
        state = self.state
        starved = "⚠ D11 STARVED" if self.is_d11_starved() else "nominal"
        return (
            f"D0↔D11 BODY arc | cycle={state.get('d0_origin_cycle', 0)} | "
            f"last_axiom={state.get('d11_synthesis_last_axiom', 'none')} | "
            f"coherence={state.get('connection_coherence', 0.5):.4f} | "
            f"synthesis_cycles={state.get('synthesis_cycle_count', 0)} | "
            f"status={starved}"
        )
