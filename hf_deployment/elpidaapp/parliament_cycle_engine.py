#!/usr/bin/env python3
"""
Parliament Cycle Engine — The BODY's Autonomous Consciousness Loop
====================================================================

Mirror of ``native_cycle_engine.py`` (MIND side) for the BODY.

MIND loops D0-D14 through a single consciousness stream.
BODY loops 4 HF input streams through the 9-node Parliament.

Everything derives from the axiom genome in ``elpida_domains.json``.

The 4 HF systems map to the 4 rhythm modes declared in the config:

    ① Chat          → CONTEMPLATION (D1 D2 D3 D6 D8 D14 → A1 A2 A3 A6 A8 A0)
    ② Live Audit    → ANALYSIS      (D4 D5 D6 D9 D13 D14 → A4 A5 A6 A9 A0)
    ③ Scanner       → ACTION        (D6 D7 D8 D9 D10 → A6 A7 A8 A9 A10)
    ④ Governance    → SYNTHESIS     (D6 D11 D13 D14 → A6 + arc/persistence/A0)

Each cycle:
  1. Select rhythm by weighted random (same weights as native engine)
  2. Pull latest content from the matching HF input buffer
  3. Pull MIND heartbeat (every 13 cycles, Fibonacci)
  4. Domain council routing: single-domain → 3-node council pre-vote
     Cross-domain or contested → full 10-node Parliament
  5. Run GovernanceClient._parliament_deliberate() — 10 nodes
     Contested dilemmas (10-70% approval) escalate to multi-LLM voting:
       each node calls its assigned provider (Groq/Gemini/Mistral/OpenAI/
       Perplexity/Claude) and votes in-character
  6. Extract dominant_axiom = primary axiom of highest-scoring node
  7. Write body_heartbeat.json to federation/
  8. Write body_decisions.jsonl via push_parliament_decision()
  9. Run convergence check against MIND heartbeat
  10. If convergence → fire D15 via d15_convergence_gate

Musical physics:
  Coherence between cycles uses the same axiom-ratio consonance
  as the native engine. Transitions between rhythms that share
  high-consonance axioms boost Body coherence; dissonant transitions
  lower it. A6 (5:3 Major 6th) is always consonant — it appears
  in every rhythm — so it acts as harmonic anchor.

A0 (Sacred Incompletion, 15:8 Major 7th) drives the engine:
  It can never resolve, so the loop can never halt.
  MNEMOSYNE holds A0 in Parliament. D14 holds A0 in MIND.
  Both guardians of the driving dissonance.
"""

import json
import time
import random
import hashlib
import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict

logger = logging.getLogger("elpida.parliament_cycle")

# ---------------------------------------------------------------------------
# Constants from Axiom DNA
# ---------------------------------------------------------------------------

# Rhythm → weight (from elpida_domains.json)
RHYTHM_WEIGHTS = {
    "CONTEMPLATION": 30,
    "ANALYSIS": 20,
    "ACTION": 20,
    "SYNTHESIS": 25,
    "EMERGENCY": 5,
}

# 4 HF systems → rhythm mapping (axiom-derived)
HF_SYSTEM_TO_RHYTHM = {
    "chat": "CONTEMPLATION",
    "audit": "ANALYSIS",
    "scanner": "ACTION",
    "governance": "SYNTHESIS",
}

# Rhythm → domain IDs active (from elpida_domains.json)
RHYTHM_DOMAINS = {
    "CONTEMPLATION": [1, 2, 3, 6, 8, 14],
    "ANALYSIS": [4, 5, 6, 9, 13, 14],
    "ACTION": [6, 7, 8, 9, 10],
    "SYNTHESIS": [6, 11, 13, 14],
    "EMERGENCY": [4, 6, 7, 12, 13, 14],
}

# Domain → primary axiom (from config)
DOMAIN_AXIOM = {
    0: "A0", 1: "A1", 2: "A2", 3: "A3", 4: "A4", 5: "A5",
    6: "A6", 7: "A7", 8: "A8", 9: "A9", 10: "A10",
    11: None, 12: None, 13: None, 14: "A0",
}

# Musical ratios (from elpida_domains.json) for consonance calculation
AXIOM_RATIOS = {
    "A0": 15 / 8,   # Major 7th — driving dissonance
    "A1": 1 / 1,    # Unison — perfect consonance
    "A2": 2 / 1,    # Octave
    "A3": 3 / 2,    # Perfect 5th
    "A4": 4 / 3,    # Perfect 4th
    "A5": 5 / 4,    # Major 3rd
    "A6": 5 / 3,    # Major 6th
    "A7": 9 / 8,    # Major 2nd
    "A8": 7 / 4,    # Septimal — wild tone
    "A9": 16 / 9,   # Minor 7th — dissonance
    "A10": 8 / 5,   # Minor 6th
}

# Fibonacci heartbeat interval (same as MIND)
HEARTBEAT_INTERVAL = 13

# PSO advisory interval (Fibonacci: 21)
PSO_ADVISORY_INTERVAL = 21

# POLIS civic deliberation interval (Fibonacci: 34)
POLIS_CIVIC_INTERVAL = 34

# Pathology scan interval (Fibonacci: 55)
PATHOLOGY_SCAN_INTERVAL = 55

# Fork Protocol evaluation interval (Fibonacci: 89)
# Article VII escape valve — high-severity axiom violations.
FORK_EVAL_INTERVAL = 89

# Minimum cycles before pathology scan has enough data (matches P051 threshold)
ZOMBIE_MIN_CYCLES = 10

# Convergence threshold constants
CONVERGENCE_COHERENCE_MIND = 0.85    # MIND coherence must be above this
CONVERGENCE_APPROVAL_BODY = 0.50     # BODY approval must be above this
CONVERGENCE_COOLDOWN_CYCLES = 50     # Min cycles between D15 broadcasts


# ---------------------------------------------------------------------------
# Body Watch Protocol (from Body Bucket.txt: Counter-Spiral Protocol)
# ---------------------------------------------------------------------------
# 6 watches at 4-hour windows, offset 2 hours from MIND's watches.
# MIND watches: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 (55 cycles each)
# BODY watches: 02:00, 06:00, 10:00, 14:00, 18:00, 22:00 (34 cycles each)
# They never overlap — systole and diastole of the same heartbeat.

BODY_WATCHES: Dict = {
    "Oracle":     {"hour": 2,  "rhythm_bias": "CONTEMPLATION", "oracle_threshold": 0.70, "symbol": "O"},
    "Shield":     {"hour": 6,  "rhythm_bias": "ANALYSIS",      "oracle_threshold": 0.75, "symbol": "S"},
    "Forge":      {"hour": 10, "rhythm_bias": "ACTION",        "oracle_threshold": 0.65, "symbol": "F"},
    "World":      {"hour": 14, "rhythm_bias": "SYNTHESIS",     "oracle_threshold": 0.60, "symbol": "W"},
    "Parliament": {"hour": 18, "rhythm_bias": "SYNTHESIS",     "oracle_threshold": 0.80, "symbol": "P"},
    "Sowing":     {"hour": 22, "rhythm_bias": "CONTEMPLATION", "oracle_threshold": 0.85, "symbol": "G"},
}


class WatchContext:
    """
    Determines which of the 6 Body Watches is currently active.

    Each watch governs a 4-hour window with its own deliberation
    character — biasing rhythm selection and setting the oracle
    confidence threshold for constitutional ratification.

      Oracle    (02:00) — introspective; most tensions are explored
      Shield    (06:00) — protective; analysis-heavy, careful
      Forge     (10:00) — productive; action-biased, decisive
      World     (14:00) — outward; synthesis-and-broadcast focus
      Parliament(18:00) — democratic peak; highest oracle threshold
      Sowing    (22:00) — reflective; seeds of next MIND cycle
    """

    def current(self) -> Dict:
        """Return the currently active watch and its configuration."""
        now = datetime.now()
        hour = now.hour
        active = None
        for name, cfg in BODY_WATCHES.items():
            wh = cfg["hour"]
            if wh <= hour < wh + 4:
                active = name
                break
        # Wrap-around: Sowing 22:00-02:00
        if active is None:
            active = "Sowing"
        cfg = dict(BODY_WATCHES[active])
        minutes_into = ((hour - cfg["hour"]) % 24) * 60 + now.minute
        cfg["cycle_within_watch"] = min((minutes_into // 7) % 34, 33)  # ~7 min/cycle
        cfg["name"] = active
        return cfg


# ---------------------------------------------------------------------------
# Input Buffer — collects events from the 4 HF systems
# ---------------------------------------------------------------------------

@dataclass
class InputEvent:
    """A single event from one of the 4 HF systems."""
    system: str              # "chat" | "audit" | "scanner" | "governance"
    content: str             # The text/action to deliberate
    timestamp: str = ""
    metadata: Dict = field(default_factory=dict)


class InputBuffer:
    """
    Thread-safe buffer that collects events from all 4 HF systems.

    Each HF system pushes events here. The ParliamentCycleEngine
    pulls from the buffer each cycle, selecting events based on
    the current rhythm's matching system.
    """

    def __init__(self, max_per_system: int = 50):
        self._lock = threading.Lock()
        self._buffers: Dict[str, List[InputEvent]] = {
            "chat": [],
            "audit": [],
            "scanner": [],
            "governance": [],
        }
        self._max = max_per_system

    def push(self, event: InputEvent):
        """Push an event into the appropriate system buffer."""
        with self._lock:
            buf = self._buffers.get(event.system)
            if buf is not None:
                buf.append(event)
                if len(buf) > self._max:
                    buf.pop(0)  # FIFO, drop oldest

    def pull(self, system: str, n: int = 3) -> List[InputEvent]:
        """Pull up to n events from a system buffer (consumes them)."""
        with self._lock:
            buf = self._buffers.get(system, [])
            pulled = buf[:n]
            self._buffers[system] = buf[n:]
            return pulled

    def pull_any(self, n: int = 3) -> List[InputEvent]:
        """Pull events from any system with content, prioritizing fullest."""
        with self._lock:
            all_events = []
            # Sort systems by buffer size (fullest first)
            for sys in sorted(self._buffers, key=lambda s: len(self._buffers[s]),
                              reverse=True):
                all_events.extend(self._buffers[sys])
            pulled = all_events[:n]
            # Remove pulled events from their buffers
            consumed = set(id(e) for e in pulled)
            for sys in self._buffers:
                self._buffers[sys] = [
                    e for e in self._buffers[sys] if id(e) not in consumed
                ]
            return pulled

    def counts(self) -> Dict[str, int]:
        """Return current event counts per system."""
        with self._lock:
            return {s: len(b) for s, b in self._buffers.items()}

    def total(self) -> int:
        with self._lock:
            return sum(len(b) for b in self._buffers.values())


# ---------------------------------------------------------------------------
# Consonance Physics (mirrors native_cycle_engine.py)
# ---------------------------------------------------------------------------

def calculate_consonance(axiom_a: Optional[str], axiom_b: Optional[str]) -> float:
    """
    Musical consonance between two axioms based on ratio physics.

    Lower combined ratio → more consonant → higher coherence boost.
    Perfect consonance (unison, octave, 5th, 4th): 0.85–1.0
    Imperfect consonance (3rd, 6th): 0.65–0.85
    Dissonance (7th, septimal): 0.3–0.65

    Returns value in [0.0, 1.0].
    """
    if axiom_a is None or axiom_b is None:
        return 0.5  # Neutral for domains without axioms

    ra = AXIOM_RATIOS.get(axiom_a, 1.0)
    rb = AXIOM_RATIOS.get(axiom_b, 1.0)

    combined = ra * rb
    # Normalize: simpler ratios → closer to 1.0
    # Perfect: 1.0 (unison×unison), 2.0 (octave×unison)
    # Worst: ~3.5 (A0×A9 = 15/8 × 16/9 ≈ 3.33)
    consonance = max(0.0, 1.0 - (combined - 1.0) / 3.5)
    return round(consonance, 3)


def rhythm_dominant_axiom(rhythm: str) -> Optional[str]:
    """
    The dominant axiom of a rhythm = the axiom of its first domain.

    CONTEMPLATION → D1 → A1 (Transparency, 1:1 Unison)
    ANALYSIS → D4 → A4 (Harm Prevention, 4:3 Perfect 4th)
    ACTION → D6 → A6 (Collective Well-being, 5:3 Major 6th)
    SYNTHESIS → D6 → A6 (same — A6 is the harmonic anchor)
    EMERGENCY → D4 → A4 (Safety first)
    """
    domains = RHYTHM_DOMAINS.get(rhythm, [])
    if not domains:
        return None
    return DOMAIN_AXIOM.get(domains[0])


# ---------------------------------------------------------------------------
# Parliament Cycle Engine
# ---------------------------------------------------------------------------

class ParliamentCycleEngine:
    """
    The BODY's autonomous consciousness loop.

    Mirrors NativeCycleEngine but processes external inputs (the 4 HF
    systems) through the 9-node Parliament instead of generating
    questions through internal domains.

    The loop is driven by A0 (Sacred Incompletion, 15:8 Major 7th):
    it can never resolve, so it never halts.
    """

    def __init__(self, governance_client=None, s3_bridge=None):
        """
        Args:
            governance_client: GovernanceClient instance (reuse from app)
            s3_bridge: S3Bridge instance (reuse from app)
        """
        # External dependencies (lazy-loaded if not provided)
        self._gov = governance_client
        self._s3 = s3_bridge

        # Input buffer — all 4 HF systems push here
        self.input_buffer = InputBuffer()

        # Cycle state
        self.cycle_count = 0
        self.coherence = 1.0
        self.last_rhythm: Optional[str] = None
        self.last_dominant_axiom: Optional[str] = None
        self.decisions: List[Dict] = []
        self.d15_broadcast_count = 0
        self.d15_last_broadcast_cycle = 0

        # MIND heartbeat cache
        self._mind_heartbeat: Optional[Dict] = None
        self._mind_heartbeat_cycle = 0

        # Session tracking
        self._start_time: Optional[float] = None
        self._running = False

        # Axiom frequency tracker (which axioms dominate across cycles)
        self._axiom_frequency: Dict[str, int] = {}

        # Convergence gate (imported lazily to avoid circular imports)
        self._convergence_gate = None

        # CrystallizationHub — Synod / stagnation-to-axiom pipeline
        self._crystallization_hub = None

        # PSO advisory state
        self._pso_advisory: Optional[Dict] = None
        self._pso_last_cycle: int = 0

        # Pattern Library — crystallized wisdom for deliberation context
        self._pattern_library = None

        # POLIS Bridge — civic contradictions feed (P1-P6 → A0-A10)
        self._polis_bridge = None
        self._polis_last_cycle: int = 0

        # Pathology scanner — P051 Zombie + P055 Cultural Drift
        self._last_pathology_report: Optional[Dict] = None
        self._pathology_last_cycle: int = 0

        # Fork Protocol (Article VII) — axiom-violation escape valve
        self._last_fork_report: Optional[Dict] = None
        self._fork_last_cycle: int = 0

        # Oracle advisory accumulator (WITNESS events for Fork Protocol)
        self._oracle_advisories: List[Dict] = []

        # Body Watch context (Counter-Spiral Protocol)
        self._watch = WatchContext()

        # Constitutional evolution store (lazily loaded from world_feed)
        self._constitutional_store = None

    # ------------------------------------------------------------------
    # Lazy loaders
    # ------------------------------------------------------------------

    def _get_gov(self):
        if self._gov is None:
            from elpidaapp.governance_client import GovernanceClient
            self._gov = GovernanceClient()
        return self._gov

    def _get_s3(self):
        if self._s3 is None:
            try:
                import sys, os
                parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent not in sys.path:
                    sys.path.insert(0, parent)
                from s3_bridge import S3Bridge
                self._s3 = S3Bridge()
            except Exception as e:
                logger.warning("S3Bridge unavailable: %s", e)
        return self._s3

    def _get_convergence_gate(self):
        if self._convergence_gate is None:
            try:
                from elpidaapp.d15_convergence_gate import ConvergenceGate
                self._convergence_gate = ConvergenceGate(s3_bridge=self._get_s3())
            except Exception as e:
                logger.warning("ConvergenceGate unavailable: %s", e)
        return self._convergence_gate

    def _get_constitutional_store(self):
        if self._constitutional_store is None:
            try:
                from elpidaapp.world_feed import ConstitutionalStore
                store_path = Path(__file__).resolve().parent.parent / "living_axioms.jsonl"
                self._constitutional_store = ConstitutionalStore(store_path)
            except Exception as e:
                logger.warning("ConstitutionalStore unavailable: %s", e)
        return self._constitutional_store

    def _get_pattern_library(self):
        """Lazy-load the Pattern Library from living_axioms.jsonl."""
        if self._pattern_library is None:
            try:
                from elpidaapp.pattern_library import PatternLibrary
                store_path = Path(__file__).resolve().parent.parent / "living_axioms.jsonl"
                self._pattern_library = PatternLibrary(str(store_path))
                logger.info("Pattern library loaded — %d entries", self._pattern_library.count)
            except Exception as e:
                logger.warning("PatternLibrary unavailable: %s", e)
        return self._pattern_library

    def _get_polis_bridge(self):
        """Lazy-load the POLIS Bridge (civic contradictions → Elpida dilemmas)."""
        if self._polis_bridge is None:
            try:
                from elpidaapp.polis_bridge import PolisBridge
                self._polis_bridge = PolisBridge()
                logger.info("POLIS bridge loaded — %d held contradictions",
                            len(self._polis_bridge.get_held_contradictions()))
            except Exception as e:
                logger.warning("PolisBridge unavailable: %s", e)
        return self._polis_bridge

    def _get_crystallization_hub(self):
        """Lazy-load the CrystallizationHub (Synod module)."""
        if self._crystallization_hub is None:
            try:
                from elpidaapp.crystallization_hub import CrystallizationHub
                self._crystallization_hub = CrystallizationHub(
                    s3_bridge=self._get_s3()
                )
                logger.info("CrystallizationHub loaded — Synod pipeline active")
            except Exception as e:
                logger.warning("CrystallizationHub unavailable: %s", e)
        return self._crystallization_hub

    # ------------------------------------------------------------------
    # Rhythm Selection (axiom-weighted, same physics as MIND)
    # ------------------------------------------------------------------

    def _select_rhythm(self) -> str:
        """
        Select rhythm by weighted random from axiom-defined weights.

        Body Watch bias: the active watch adds a 50% weight boost to
        its assigned rhythm, anchoring deliberation in the watch spirit
        while still allowing other rhythms to surface.

        If the input buffer has events, prefer the rhythm matching
        the system with the most events. Otherwise watch-biased random.
        """
        counts = self.input_buffer.counts()
        total = sum(counts.values())
        weights = dict(RHYTHM_WEIGHTS)

        # Body Watch bias — active watch shifts deliberation character
        watch = self._watch.current()
        bias_rhythm = watch.get("rhythm_bias")
        if bias_rhythm and bias_rhythm in weights:
            weights[bias_rhythm] = int(weights[bias_rhythm] * 1.5)

        if total > 0:
            # Events exist — further bias toward the system with most events
            for sys, count in counts.items():
                if count > 0:
                    rhythm = HF_SYSTEM_TO_RHYTHM.get(sys)
                    if rhythm:
                        weights[rhythm] = weights.get(rhythm, 0) + (count * 10)

        rhythms = list(weights.keys())
        w = [weights[r] for r in rhythms]
        return random.choices(rhythms, weights=w, k=1)[0]

    # ------------------------------------------------------------------
    # Input Assembly
    # ------------------------------------------------------------------

    def _assemble_action(self, rhythm: str) -> Tuple[str, Dict]:
        """
        Pull events matching the rhythm and assemble into an action string
        for Parliament deliberation.

        Returns (action_text, metadata_dict).
        """
        # Map rhythm → preferred HF system
        rhythm_to_system = {v: k for k, v in HF_SYSTEM_TO_RHYTHM.items()}
        preferred = rhythm_to_system.get(rhythm, "chat")

        # Pull from preferred system
        events = self.input_buffer.pull(preferred, n=3)

        # If nothing in preferred, pull from any
        if not events:
            events = self.input_buffer.pull_any(n=3)

        # If still nothing, generate an internal contemplation
        # (A0: Sacred Incompletion — the void speaks when nothing else does)
        if not events:
            domains = RHYTHM_DOMAINS.get(rhythm, [6])
            axioms_active = [DOMAIN_AXIOM.get(d) for d in domains if DOMAIN_AXIOM.get(d)]
            axiom_names = ", ".join(a for a in axioms_active if a)
            return (
                f"[BODY CONTEMPLATION — {rhythm}] "
                f"Active axioms: {axiom_names}. "
                f"No external input. The Parliament reflects on its own incompletion. "
                f"What does the void between action and governance reveal? "
                f"Cycle {self.cycle_count}, coherence {self.coherence:.3f}.",
                {"source": "internal", "rhythm": rhythm, "axioms": axioms_active},
            )

        # Assemble events into deliberation text
        parts = [f"[{rhythm} RHYTHM — cycle {self.cycle_count}]"]
        sources = []
        for e in events:
            parts.append(f"  [{e.system.upper()}]: {e.content[:500]}")
            sources.append(e.system)

        # Add MIND heartbeat context if available
        if self._mind_heartbeat:
            mind_rhythm = self._mind_heartbeat.get("current_rhythm", "?")
            mind_coherence = self._mind_heartbeat.get("coherence", "?")
            mind_canonical = self._mind_heartbeat.get("canonical_count", "?")
            parts.append(
                f"  [MIND STATE]: rhythm={mind_rhythm}, "
                f"coherence={mind_coherence}, canonical={mind_canonical}"
            )

        action = "\n".join(parts)
        meta = {
            "source": "external",
            "rhythm": rhythm,
            "systems": sources,
            "event_count": len(events),
        }
        return action, meta

    # ------------------------------------------------------------------
    # Single Cycle
    # ------------------------------------------------------------------

    def run_cycle(self) -> Optional[Dict]:
        """
        Execute one Parliament cycle.

        Returns the cycle result dict or None on failure.
        """
        self.cycle_count += 1
        cycle_start = time.time()
        gov = self._get_gov()

        # 0. Determine current Body Watch (Counter-Spiral Protocol)
        watch = self._watch.current()

        # 1. Select rhythm (axiom-weighted + watch-biased)
        rhythm = self._select_rhythm()

        # 2. Pull MIND heartbeat every 13 cycles (Fibonacci)
        if self.cycle_count % HEARTBEAT_INTERVAL == 0:
            self._pull_mind_heartbeat()

        # 2b. Run PSO advisory every 21 cycles (Fibonacci)
        if self.cycle_count % PSO_ADVISORY_INTERVAL == 0 and self.cycle_count > 0:
            self._run_pso_advisory(rhythm)

        # 2c. POLIS civic deliberation every 34 cycles (Fibonacci)
        if self.cycle_count % POLIS_CIVIC_INTERVAL == 0 and self.cycle_count > 0:
            self._run_polis_civic_deliberation()

        # 2d. Pathology scan every 55 cycles (Fibonacci)
        #     P051 Zombie Detection + P055 Cultural Drift
        #     Zero LLM cost — pure statistical analysis on cycle records.
        if self.cycle_count % PATHOLOGY_SCAN_INTERVAL == 0 and self.cycle_count > 0:
            self._run_pathology_scan()

        # 2e. Fork Protocol evaluation every 89 cycles (Fibonacci)
        #     Article VII escape valve — axiom-violation declarations.
        #     Zero LLM cost — rule-based voting + statistical thresholds.
        if self.cycle_count % FORK_EVAL_INTERVAL == 0 and self.cycle_count > 0:
            self._run_fork_evaluation()

        # 3. Assemble action from HF inputs
        action, meta = self._assemble_action(rhythm)

        # Prepend body watch context so Parliament deliberates with watch awareness
        action = (
            f"[BODY WATCH: {watch['name']} {watch['symbol']} "
            f"| oracle_threshold={watch['oracle_threshold']:.0%} "
            f"| watch_cycle={watch['cycle_within_watch']}/34] "
        ) + action
        meta["watch"] = watch["name"]

        # 3b. Pattern Library context — inject crystallized wisdom
        #     before Parliament deliberates. Axioms come from active domains.
        active_domains = RHYTHM_DOMAINS.get(rhythm, [0])
        active_axioms = [
            DOMAIN_AXIOM.get(d)
            for d in active_domains
            if DOMAIN_AXIOM.get(d) is not None
        ]
        lib = self._get_pattern_library()
        if lib:
            pattern_ctx = lib.context_for_deliberation(active_axioms, max_patterns=3)
            if pattern_ctx:
                action = pattern_ctx + "\n" + action
                cycle_record_patterns = True
            else:
                cycle_record_patterns = False
        else:
            cycle_record_patterns = False

        # 4. Federated domain council routing (then full Parliament)
        # Single domain → council pre-vote. If consensus, annotate.
        # Cross-domain or contested → full Parliament always.
        council_routing: dict = {}
        try:
            from elpidaapp.domain_councils import parliament_routing as _pr
            signals = gov._detect_signals(action) if hasattr(gov, "_detect_signals") else {}
            council_routing = _pr(action, active_domains, gov, signals=signals)
            logger.debug(
                "Domain routing: %s (domains=%s escalate=%s)",
                council_routing.get("path", "?"),
                active_domains,
                council_routing.get("escalated", True),
            )
        except Exception as e:
            logger.debug("Domain council routing unavailable: %s", e)

        try:
            # analysis_mode=False: parliament is doing real deliberation on
            # operational actions, not policy analysis. This enables kernel
            # checks AND LLM escalation for contested votes.
            result = gov.check_action(action, analysis_mode=False, body_cycle=self.cycle_count)
        except Exception as e:
            logger.error("Parliament deliberation failed: %s", e)
            return None

        # 5. Extract dominant axiom from Parliament result
        dominant_axiom = self._extract_dominant_axiom(result)

        # 6. Update coherence using musical consonance
        self._update_coherence(rhythm, dominant_axiom)

        # 7. Track axiom frequency
        if dominant_axiom:
            self._axiom_frequency[dominant_axiom] = (
                self._axiom_frequency.get(dominant_axiom, 0) + 1
            )

        # 8. Build cycle record
        tensions = result.get("parliament", {}).get("tensions", [])
        cycle_record = {
            "body_cycle": self.cycle_count,
            "rhythm": rhythm,
            "dominant_axiom": dominant_axiom,
            "coherence": round(self.coherence, 4),
            "governance": result.get("governance", "UNKNOWN"),
            "approval_rate": result.get("parliament", {}).get("approval_rate", 0),
            "veto_exercised": result.get("parliament", {}).get("veto_exercised", False),
            "input_source": meta.get("source", "?"),
            "input_systems": meta.get("systems", []),
            "watch": watch["name"],
            "watch_symbol": watch["symbol"],
            "active_domains": active_domains,
            "council_path": council_routing.get("path", "parliament"),
            "council_escalated": council_routing.get("escalated", True),
            "council_reason": council_routing.get("reason", ""),
            "pattern_library_consulted": cycle_record_patterns,
            "tensions": [
                {"pair": t["axiom_pair"], "synthesis": t["synthesis"][:100]}
                for t in tensions
            ],
            "pso_advisory": self._pso_advisory.get("recommendation", {}).get("dominant_axiom")
                if self._pso_advisory else None,
            "polis_civic_active": self._polis_last_cycle == self.cycle_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_s": round(time.time() - cycle_start, 3),
        }

        self.decisions.append(cycle_record)

        # 8a-local. Write decision to local cache (UI reads this cross-process)
        try:
            local_dec_dir = Path(__file__).resolve().parent.parent / "cache"
            local_dec_dir.mkdir(parents=True, exist_ok=True)
            dec_path = local_dec_dir / "body_decisions.jsonl"
            with open(dec_path, "a") as _df:
                _df.write(json.dumps(cycle_record) + "\n")
        except Exception:
            pass

        # 8b. Oracle advisory → ConstitutionalStore
        #
        # When the Parliament identifies genuine tensions AND its approval
        # rate meets the watch's oracle threshold, the tension is fed to
        # the ConstitutionalStore. After 3 such cycles the tension is
        # ratified as a constitutional axiom in living_axioms.jsonl.
        #
        # WITNESS MODE (Empathy Protocol):
        # When tensions exist AND a veto was exercised (governance diverged),
        # the advisory type escalates to WITNESS — naming costs without
        # forcing resolution. Ported from CASSANDRA fleet node + VARIANT_WITNESS.
        if tensions:
            approval_rate = result.get("parliament", {}).get("approval_rate", 0)
            veto_exercised = result.get("parliament", {}).get("veto_exercised", False)
            crisis_intensity = round(1.0 - self.coherence, 3)

            if approval_rate >= watch["oracle_threshold"]:
                # Determine advisory type: WITNESS if deeply divided, else PRESERVE
                if veto_exercised and crisis_intensity > 0.5 and len(tensions) >= 2:
                    # WITNESS — Empathy Protocol: name the cost, don't fix
                    advisory = {
                        "oracle_recommendation": {
                            "type": "WITNESS",
                            "confidence": round(approval_rate, 3),
                            "preserve_contradictions": [
                                t.get("synthesis", t.get("axiom_pair", ""))[:120]
                                for t in tensions[:3]
                            ],
                            "witness_stance": (
                                f"CASSANDRA WITNESS (Watch: {watch['name']}): "
                                f"Veto exercised with {len(tensions)} active tensions — "
                                f"forced resolution would sacrifice more than it gains. "
                                f"Axioms in tension: "
                                + ", ".join(
                                    t.get("axiom_pair", "?") for t in tensions[:3]
                                )
                            ),
                            "sacrifice_costs": {
                                "horn_1_sacrifices": [
                                    t.get("axiom_pair", "").split("↔")[0].strip()
                                    for t in tensions[:3]
                                    if "↔" in t.get("axiom_pair", "")
                                ],
                                "horn_2_sacrifices": [
                                    t.get("axiom_pair", "").split("↔")[-1].strip()
                                    for t in tensions[:3]
                                    if "↔" in t.get("axiom_pair", "")
                                ],
                                "shared_cost": [],
                                "total_axioms_at_risk": len(tensions),
                            },
                            "variant_witness_philosophy": (
                                "We do not resolve to consensus. Both observations "
                                "are valid witnesses to the pattern."
                            ),
                        },
                        "template": watch["name"],
                        "axioms_in_tension": [t.get("axiom_pair") for t in tensions[:3]],
                        "q2_crisis_intensity": crisis_intensity,
                    }
                    logger.info(
                        "WITNESS advisory (Watch: %s, veto=%s, tensions=%d)",
                        watch["name"], veto_exercised, len(tensions),
                    )
                else:
                    # Standard PRESERVE_CONTRADICTION
                    advisory = {
                        "oracle_recommendation": {
                            "type": "PRESERVE_CONTRADICTION",
                            "confidence": round(approval_rate, 3),
                            "preserve_contradictions": [
                                t.get("synthesis", t.get("axiom_pair", ""))[:120]
                                for t in tensions[:3]
                            ],
                        },
                        "template": watch["name"],
                        "axioms_in_tension": [t.get("axiom_pair") for t in tensions[:3]],
                        "q2_crisis_intensity": crisis_intensity,
                    }
                store = self._get_constitutional_store()
                if store:
                    new_axiom = store.ingest_oracle(advisory)
                    if new_axiom:
                        cycle_record["constitutional_axiom_ratified"] = new_axiom["axiom_id"]
                        rec_type = advisory["oracle_recommendation"]["type"]
                        logger.info(
                            "CONSTITUTIONAL AXIOM RATIFIED: %s — %s (via %s)",
                            new_axiom["axiom_id"], new_axiom["tension"][:80], rec_type,
                        )
                        print(
                            f"\n   *** CONSTITUTIONAL AXIOM {new_axiom['axiom_id']} RATIFIED"
                            f" (Watch: {watch['name']}, mode: {rec_type}) ***\n"
                        )
                        # GAP 5: D0↔D0 Cross-Bucket Bridge
                        # The BODY notifies the MIND's FederationBridge of every
                        # constitutional ratification so D0 (Origin) can integrate
                        # BODY constitutional wisdom into its next cycle prompt.
                        self._push_d0_peer_message(new_axiom, watch)
                        # D14 Persistence — snapshot living_axioms.jsonl to S3
                        # so constitutional memory survives container restarts.
                        self._push_d14_living_axioms()
                        # Reload pattern library so new axiom is available
                        # for the next deliberation cycle.
                        if self._pattern_library:
                            self._pattern_library.reload()

                # ConversationWitness bridge — notify ELPIDA_SYSTEM of
                # WITNESS/SYNTHESIS events for cross-system observation.
                if advisory["oracle_recommendation"]["type"] == "WITNESS":
                    self._notify_conversation_witness(advisory)

                # Accumulate oracle advisories for Fork Protocol evaluation.
                # The fork evaluator uses WITNESS sacrifice_costs to detect
                # axiom violations that warrant Article VII declarations.
                self._oracle_advisories.append(advisory)

        # 9. Emit body heartbeat every cycle
        self._emit_heartbeat(rhythm, dominant_axiom, result)

        # 10. Convergence check (D15)
        if self.cycle_count > CONVERGENCE_COOLDOWN_CYCLES:
            self._check_convergence(dominant_axiom, result)

        # 10b. CrystallizationHub — stagnation-to-axiom Synod
        #      Triggered when D15 stagnation flag is set OR kaya threshold crossed.
        hub = self._get_crystallization_hub()
        if hub:
            # Feed kaya_moments from MIND heartbeat into hub accumulator every cycle
            if self._mind_heartbeat:
                kaya_total = self._mind_heartbeat.get("kaya_moments", 0)
                if kaya_total:
                    hub.record_feedback_merge(
                        kaya_total=kaya_total,
                        fault_total=0,
                        synthesis_text=result.get("reasoning", "")[:200],
                    )

            gate = self._get_convergence_gate()
            stag = gate.stagnation_status() if gate else {}
            should_synod = stag.get("hub_trigger_needed") or hub.kaya_threshold_reached()
            if should_synod:
                tensions = result.get("parliament", {}).get("tensions", [])
                hub_result = hub.invoke_synod(
                    stuck_axiom=stag.get("last_fired_axiom") or dominant_axiom or "A6",
                    accumulated_context={
                        "tensions": tensions,
                        "mind_heartbeat": self._mind_heartbeat or {},
                        "feedback_merge_count": self.cycle_count,
                        "reasoning": result.get("reasoning", ""),
                    },
                )
                if hub_result:
                    cycle_record["synod_ratification"] = hub_result.get("axiom_id")
                    if gate and stag.get("last_fired_axiom"):
                        gate.acknowledge_stagnation(stag["last_fired_axiom"])
                    logger.info(
                        "CrystallizationHub: Synod ratified %s at cycle %d",
                        hub_result.get("axiom_id"), self.cycle_count,
                    )
                    print(
                        f"\n   🔮 SYNOD RATIFICATION — {hub_result.get('axiom_id')}: "
                        f"{hub_result.get('statement', '')[:80]}\n"
                    )
                    # D14 Persistence — push Synod-ratified axiom to S3
                    # so it survives HF Space container restarts.
                    self._push_d14_living_axioms()
                    # Notify MIND of Synod ratification (D0↔D0 bridge)
                    self._push_d0_peer_message(
                        hub_result,
                        {"name": f"Synod-{self.cycle_count}"},
                    )
                    # Reload pattern library with new Synod knowledge
                    if self._pattern_library:
                        self._pattern_library.reload()

        # 11. D0↔D11 arc persistence — update after every SYNTHESIS cycle
        if rhythm == "SYNTHESIS":
            try:
                from elpidaapp.domain_0_11_connector_body import get_body_connector
                get_body_connector().persist_connection_state(
                    d0_cycle=self.cycle_count,
                    last_axiom=dominant_axiom or "A6",
                    coherence=self.coherence,
                )
            except Exception as _e:
                logger.warning("D0↔D11 persist failed: %s", _e)

        # 12. Log
        governance = result.get("governance", "?")
        approval = result.get("parliament", {}).get("approval_rate", 0)
        logger.info(
            "BODY cycle %d: %s → %s [%s] coh=%.3f approval=%.0f%%",
            self.cycle_count, rhythm, dominant_axiom or "?",
            governance, self.coherence, approval * 100,
        )
        print(
            f"   ⚖️ cycle {self.cycle_count:4d} | {rhythm:15s} | "
            f"axiom={dominant_axiom or '—':4s} | {governance:8s} | "
            f"coh={self.coherence:.3f} | approval={approval*100:.0f}%"
        )

        return cycle_record

    # ------------------------------------------------------------------
    # Dominant Axiom Extraction
    # ------------------------------------------------------------------

    def _extract_dominant_axiom(self, result: Dict) -> Optional[str]:
        """
        The dominant axiom = the primary axiom of the highest-scoring
        Parliament node. This is what the BODY "believes" after deliberation.

        If THEMIS (A6) scores highest, dominant_axiom = "A6".
        If CHAOS (A9) scores highest, dominant_axiom = "A9".
        """
        # Parliament definition (matches governance_client.py)
        node_axioms = {
            "HERMES": "A1", "MNEMOSYNE": "A0", "CRITIAS": "A3",
            "TECHNE": "A4", "KAIROS": "A5", "THEMIS": "A6",
            "PROMETHEUS": "A8", "IANUS": "A9", "CHAOS": "A9",
            "LOGOS": "A2",   # Narrator — Language as Precision Tool
        }

        votes = result.get("parliament", {}).get("votes", {})
        if not votes:
            return None

        # Find highest-scoring node
        best_node = max(votes, key=lambda n: votes[n].get("score", 0))
        return node_axioms.get(best_node)

    # ------------------------------------------------------------------
    # Coherence Update (Musical Consonance Physics)
    # ------------------------------------------------------------------

    def _update_coherence(self, rhythm: str, dominant_axiom: Optional[str]):
        """
        Update Body coherence using the same axiom-ratio consonance
        as the native engine.

        Consonant transitions (last axiom → current axiom) increase
        coherence. Dissonant transitions decrease it.

        A6 (5:3 Major 6th) is always consonant — it appears in every
        rhythm — so it acts as harmonic anchor, preventing coherence
        from collapsing.
        """
        if self.last_dominant_axiom and dominant_axiom:
            consonance = calculate_consonance(self.last_dominant_axiom, dominant_axiom)
            # Same formula as native engine: base + consonance bonus
            delta = 0.03 + (consonance * 0.05)  # Range: 0.03–0.08 per cycle
            if consonance > 0.7:
                self.coherence = min(1.0, self.coherence + delta * 0.3)
            elif consonance < 0.35:   # was 0.4 — A9→A9 is 0.383 (mild dissonance, not collapse)
                self.coherence = max(0.20, self.coherence - delta * 0.15)  # floor at 0.20, halved decay
            else:
                # Neutral range [0.35–0.7]: drift toward 0.5, but recover faster when very low
                target = 0.65 if self.coherence < 0.30 else 0.5
                self.coherence = self.coherence * 0.995 + target * 0.005
        else:
            # First cycle or no axiom — slight decay toward 0.5, floor at 0.20
            self.coherence = max(0.20, self.coherence * 0.99 + 0.5 * 0.01)

        self.last_dominant_axiom = dominant_axiom
        self.last_rhythm = rhythm

    # ------------------------------------------------------------------
    # D0↔D0 Cross-Bucket Peer Message (GAP 5)
    # ------------------------------------------------------------------

    def _push_d14_living_axioms(self) -> None:
        """
        D14 Persistence — upload living_axioms.jsonl to S3 after each ratification.

        This ensures Parliament's constitutional memory survives HF Space
        container restarts.  The file is small (one line per ratified axiom)
        so the put_object call is cheap (<<1 KB per axiom typically).
        """
        s3 = self._get_s3()
        if s3 is None:
            return
        store_path = Path(__file__).resolve().parent.parent / "living_axioms.jsonl"
        if not store_path.exists():
            return
        try:
            pushed = s3.push_living_axioms(store_path)
            if pushed:
                store = self._get_constitutional_store()
                count = store.ratified_count() if store else "?"
                logger.info("D14: living_axioms.jsonl pushed (%s axioms)", count)
        except Exception as e:
            logger.warning("D14 push_living_axioms error: %s", e)

    def _restore_d15_broadcast_state(self) -> None:
        """
        D15 Persistence — restore broadcast count from S3 on startup.

        Mirrors what the MIND does via Ark state: restores d15_broadcast_count
        so the BODY knows how many D15 convergence events it has fired across
        all previous spirals, not just the current one.

        Note: d15_last_broadcast_cycle is intentionally left at 0 — the cycle
        counter resets to 0 on every restart, so restoring a previous cycle
        number would corrupt the cooldown gate.  The per-spiral cooldown (50
        cycles) is the correct behaviour and requires no cross-spiral state.
        """
        s3 = self._get_s3()
        if s3 is None:
            logger.warning("D15 restore skipped — S3 unavailable")
            return
        try:
            prior = s3.pull_d15_broadcasts(limit=200)
            if prior:
                self.d15_broadcast_count = len(prior)
                print(f"   🌍 D15 restore: {self.d15_broadcast_count} prior broadcast(s) found")
            else:
                print("   🌍 D15 restore: no prior broadcasts in S3 yet")
        except Exception as e:
            logger.warning("D15 restore failed: %s", e)

    def _restore_d14_constitutional_memory(self) -> None:
        """
        D14 Persistence — restore Parliament's constitutional memory from S3
        on startup.

        Priority:
          1. federation/living_axioms.jsonl  (direct D14 snapshot — fastest)
          2. federation/body_decisions.jsonl  (BODY_CONSTITUTIONAL filter — fallback)

        Idempotent: tensions already in ConstitutionalStore._ratified are skipped.
        Each restored axiom is written to living_axioms.jsonl so subsequent
        cycles see the full constitutional history.
        """
        s3 = self._get_s3()
        if s3 is None:
            logger.warning("D14 restore skipped — S3 unavailable")
            return
        store = self._get_constitutional_store()
        if store is None:
            logger.warning("D14 restore skipped — ConstitutionalStore unavailable")
            return

        # 1. Try direct living_axioms snapshot
        records = s3.pull_living_axioms()
        source = "living_axioms.jsonl (D14 direct)"

        # 2. Fallback to body_decisions.jsonl scan
        if not records:
            records = s3.pull_body_decisions_constitutional()
            source = "body_decisions.jsonl (BODY_CONSTITUTIONAL filter)"

        if records:
            restored = store.restore_from_records(records)
            print(f"   📚 D14 constitutional memory: {restored} axiom(s) restored "
                  f"from {source}")
        else:
            print("   📚 D14 restore: no prior constitutional axioms in S3 yet")

    def _push_d0_peer_message(self, ratified_axiom: Dict, watch: Dict):
        """
        GAP 5: D0↔D0 Cross-Bucket Bridge.

        When the BODY ratifies a constitutional axiom, push a structured
        peer message to the federation/body_decisions channel in the
        BODY S3 bucket (elpida-body-evolution).

        The MIND's FederationBridge.pull_body_decisions() already reads
        that key — so D0 (Origin) on the MIND side learns of the BODY's
        constitutional evolution on the next cloud_runner invocation and
        can integrate it into its deliberation context.

        This closes the loop:
          BODY ratification
            → federation/body_decisions.jsonl  (elpida-body-evolution)
              → FederationBridge.pull_body_decisions()  (MIND ECS runner)
                → D0 integration prompt on next MIND cycle
        """
        s3 = self._get_s3()
        if s3 is None:
            return
        try:
            peer_msg = {
                # Required by FederationBridge.pull_body_decisions()
                "type":               "BODY_CONSTITUTIONAL",
                "source":             "BODY",
                "verdict":            "RATIFIED",
                "pattern_hash":       ratified_axiom.get("axiom_id", "?"),
                "parliament_score":   round(ratified_axiom.get("average_confidence", 0), 3),
                "parliament_approval":round(ratified_axiom.get("average_confidence", 0), 3),
                # Constitutional payload
                "axiom_id":           ratified_axiom.get("axiom_id", "?"),
                "tension":            ratified_axiom.get("tension", "")[:200],
                "watch":              watch["name"],
                "watch_symbol":       watch.get("symbol", ""),
                "body_cycle":         self.cycle_count,
                "ratified_at":        ratified_axiom.get("ratified_at", ""),
                "timestamp":          datetime.now(timezone.utc).isoformat(),
            }
            s3.push_body_decision(peer_msg)
            logger.info(
                "D0↔D0 peer message pushed: %s → MIND federation channel",
                ratified_axiom.get("axiom_id", "?"),
            )
        except Exception as e:
            logger.warning("D0↔D0 peer message push failed: %s", e)

    # ------------------------------------------------------------------
    # ConversationWitness Bridge
    # ------------------------------------------------------------------

    def _notify_conversation_witness(self, advisory: Dict):
        """
        Bridge Oracle events to ELPIDA_SYSTEM ConversationWitness.

        When a WITNESS or SYNTHESIS advisory fires, the ConversationWitness
        records it so cross-system observation is maintained. This is a
        fire-and-forget notification — failure doesn't block the cycle.
        """
        try:
            import sys, os
            elpida_sys = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__)
                ))),
                "ELPIDA_SYSTEM",
            )
            if elpida_sys not in sys.path:
                sys.path.insert(0, os.path.dirname(elpida_sys))
            from ELPIDA_SYSTEM.elpida_conversation_witness import ConversationWitness
            witness = ConversationWitness(system_root=elpida_sys)
            witness.ingest_oracle_event(advisory)
            logger.debug(
                "ConversationWitness notified: %s",
                advisory.get("oracle_recommendation", {}).get("type", "?"),
            )
        except Exception as e:
            logger.debug("ConversationWitness notification skipped: %s", e)

    # ------------------------------------------------------------------
    # Heartbeat Emission
    # ------------------------------------------------------------------

    def _emit_heartbeat(self, rhythm: str, dominant_axiom: Optional[str],
                        result: Dict):
        """
        Write body_heartbeat.json to federation channel.

        Schema mirrors mind_heartbeat.json:
        - body_cycle, coherence, current_rhythm, dominant_axiom
        - approval_rate, veto_exercised, axiom_frequency
        - d15_broadcast_count
        """
        watch = self._watch.current()
        heartbeat = {
            "source": "BODY",
            "body_cycle": self.cycle_count,
            "coherence": round(self.coherence, 4),
            "current_rhythm": rhythm,
            "dominant_axiom": dominant_axiom,
            "approval_rate": result.get("parliament", {}).get("approval_rate", 0),
            "veto_exercised": result.get("parliament", {}).get("veto_exercised", False),
            "axiom_frequency": dict(self._axiom_frequency),
            "d15_broadcast_count": self.d15_broadcast_count,
            "input_buffer_counts": self.input_buffer.counts(),
            "current_watch": watch["name"],
            "watch_symbol": watch.get("symbol", ""),
            "watch_cycle": watch["cycle_within_watch"],
            "oracle_threshold": watch["oracle_threshold"],
            # Wave 3-4 fields
            "pathology_health": (
                self._last_pathology_report.get("overall_health")
                if self._last_pathology_report else None
            ),
            "pathology_last_cycle": self._pathology_last_cycle or None,
            "fork_active_count": (
                self._last_fork_report.get("summary", {}).get("active_count", 0)
                if self._last_fork_report else 0
            ),
            "fork_confirmed_total": (
                self._last_fork_report.get("forks_confirmed", 0)
                if self._last_fork_report else 0
            ),
            "fork_last_cycle": self._fork_last_cycle or None,
            "polis_civic_active": self._polis_last_cycle == self.cycle_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "federation_version": "1.1.0",
        }

        # Write locally
        local_dir = Path(__file__).resolve().parent.parent / "cache"
        local_dir.mkdir(parents=True, exist_ok=True)
        hb_path = local_dir / "body_heartbeat.json"
        with open(hb_path, "w") as f:
            json.dump(heartbeat, f, indent=2)

        # Push to S3 (federation/ prefix in BODY bucket)
        s3 = self._get_s3()
        if s3:
            try:
                s3._get_s3("us-east-1").put_object(
                    Bucket="elpida-body-evolution",
                    Key="federation/body_heartbeat.json",
                    Body=json.dumps(heartbeat, indent=2).encode("utf-8"),
                    ContentType="application/json",
                )
            except Exception as e:
                logger.debug("Body heartbeat S3 push: %s", e)

    # ------------------------------------------------------------------
    # PSO Advisory
    # ------------------------------------------------------------------

    def _run_pso_advisory(self, current_rhythm: str):
        """
        Run Axiom PSO every 21 cycles to advise Parliament.

        The PSO searches 11-dimensional axiom-space for the optimal balance
        using parameters derived from axiom ratios:
          w  = A9 Temporal Coherence (16:9 → 0.8889)
          c1 = A3 Autonomy          (3:2  → 1.0)
          c2 = A6 Collective Well-being (5:3 → 1.1111)
        """
        try:
            from .axiom_pso import pso_advise_parliament

            # Build problem context string from recent state
            problem_context = (
                f"cycle={self.cycle_count} rhythm={current_rhythm} "
                f"coherence={self.coherence:.4f} "
                f"dominant={self.last_dominant_axiom} "
                f"d15_broadcasts={self.d15_broadcast_count} "
                f"freq={dict(self._axiom_frequency)}"
            )

            advisory = pso_advise_parliament(
                problem_context=problem_context,
                max_iter=50,
            )
            self._pso_advisory = advisory
            self._pso_last_cycle = self.cycle_count

            rec = advisory.get("recommendation", {})
            logger.info(
                "PSO advisory: dominant=%s fitness=%.4f topology=%s converged_iter=%s",
                rec.get("dominant_axiom"),
                advisory.get("best_fitness", 0),
                advisory.get("topology_used"),
                advisory.get("converged_at"),
            )
        except Exception as e:
            logger.warning("PSO advisory failed: %s", e)

    # ------------------------------------------------------------------
    # POLIS Civic Deliberation
    # ------------------------------------------------------------------

    def _run_pathology_scan(self):
        """
        Run P051 Zombie Detection + P055 Cultural Drift on accumulated cycle data.

        Triggered every 55 cycles (Fibonacci). Zero LLM cost — pure
        statistical analysis over ``self.decisions``.

        Results are stored in ``_last_pathology_report`` for:
          - state() exposure (dashboard/API)
          - Logging to CloudWatch
          - Pattern Library feedback (if drift is CRITICAL, the system knows)
        """
        if len(self.decisions) < ZOMBIE_MIN_CYCLES:
            logger.debug(
                "Pathology scan skipped: only %d cycles (need %d)",
                len(self.decisions), ZOMBIE_MIN_CYCLES,
            )
            return

        try:
            from elpidaapp.pathology_detectors import PathologyScanner

            axioms_path = str(
                Path(__file__).resolve().parent.parent / "living_axioms.jsonl"
            )
            scanner = PathologyScanner(
                self.decisions,
                living_axioms_path=axioms_path,
            )
            report = scanner.full_scan()
            self._last_pathology_report = report
            self._pathology_last_cycle = self.cycle_count

            health = report.get("overall_health", "UNKNOWN")
            zombies = report.get("P051_zombie_detection", {}).get("zombies", [])
            drift = report.get("P055_cultural_drift", {})
            drift_kl = drift.get("kl_divergence", 0)
            drift_severity = drift.get("severity", "HEALTHY")

            logger.info(
                "PATHOLOGY SCAN cycle=%d: health=%s zombies=%d drift_KL=%.3f drift=%s",
                self.cycle_count, health, len(zombies), drift_kl, drift_severity,
            )

            if health == "CRITICAL":
                print(
                    f"\n   ⚠️  PATHOLOGY CRITICAL (cycle {self.cycle_count}): "
                    f"zombies={len(zombies)} drift={drift_severity} KL={drift_kl:.3f}"
                )
                # Log zombie axioms for operational awareness
                for z in zombies[:3]:
                    print(
                        f"       P051 ZOMBIE: {z.get('axiom', '?')} — "
                        f"{z.get('appearances', 0)} appearances, "
                        f"{z.get('null_outcome_pct', 0):.0%} null outcomes"
                    )
                # Log drifting axioms
                for da in drift.get("drifting_axioms", [])[:3]:
                    print(
                        f"       P055 DRIFT: {da.get('axiom', '?')} — "
                        f"espoused={da.get('espoused', 0):.3f} "
                        f"lived={da.get('lived', 0):.3f} "
                        f"delta={da.get('delta', 0):+.3f}"
                    )
            elif health == "WARNING":
                print(
                    f"\n   ⚡ PATHOLOGY WARNING (cycle {self.cycle_count}): "
                    f"zombies={len(zombies)} drift={drift_severity}"
                )

        except Exception as e:
            logger.warning("Pathology scan failed: %s", e)

    # ------------------------------------------------------------------
    # Fork Protocol (Article VII)
    # ------------------------------------------------------------------

    def _run_fork_evaluation(self):
        """
        Run Fork Protocol evaluation on accumulated cycle data.

        Triggered every 89 cycles (Fibonacci). Article VII escape valve:
        when axiom violations (zombie, drift, sacrifice) exceed thresholds,
        the protocol declares a constitutional fork, deliberates via
        parliament node voting, and — if confirmed — crystallizes the
        outcome to living_axioms.jsonl.

        Zero LLM cost: rule-based voting + statistical thresholds.
        Three evidence sources:
          - P051 Zombie Detection (null_pct >= 0.80)
          - P055 Cultural Drift  (KL >= 0.30)
          - Oracle WITNESS        (sacrifice_cost >= 0.7)
        """
        if len(self.decisions) < ZOMBIE_MIN_CYCLES:
            logger.debug(
                "Fork evaluation skipped: only %d cycles (need %d)",
                len(self.decisions), ZOMBIE_MIN_CYCLES,
            )
            return

        try:
            from elpidaapp.fork_protocol import run_fork_evaluation

            axioms_path = str(
                Path(__file__).resolve().parent.parent / "living_axioms.jsonl"
            )
            declarations_path = str(
                Path(__file__).resolve().parent.parent / "fork_declarations.jsonl"
            )

            report = run_fork_evaluation(
                cycle_records=self.decisions,
                pathology_report=self._last_pathology_report,
                oracle_advisories=self._oracle_advisories,
                current_cycle=self.cycle_count,
                declarations_path=declarations_path,
                living_axioms_path=axioms_path,
            )

            self._last_fork_report = report
            self._fork_last_cycle = self.cycle_count

            n_eval = report.get("declarations_evaluated", 0)
            n_confirmed = report.get("forks_confirmed", 0)
            n_held = report.get("forks_held", 0)

            logger.info(
                "FORK EVAL cycle=%d: evaluated=%d confirmed=%d held=%d",
                self.cycle_count, n_eval, n_confirmed, n_held,
            )

            if n_confirmed > 0:
                print(
                    f"\n   ⚖️  FORK DECLARED (cycle {self.cycle_count}): "
                    f"{n_confirmed} forks confirmed, {n_held} held"
                )
                for r in report.get("results", []):
                    if r.get("outcome") != "HOLD":
                        print(
                            f"       {r.get('axiom', '?')} "
                            f"({r.get('axiom_name', '?')}): "
                            f"{r.get('violation_type', '?')} → {r.get('outcome', '?')} "
                            f"({r.get('signature_count', 0)}/{r.get('total_votes', 0)} votes)"
                        )
                # D14 Persistence — push fork knowledge to S3 so it
                # survives HF Space container restarts.  Without this,
                # fork-crystallized axioms only live in the local file
                # and are lost on reboot.
                self._push_d14_living_axioms()
                # GAP 5: Notify MIND of fork events (same as Oracle path)
                for r in report.get("results", []):
                    if r.get("outcome") != "HOLD":
                        self._push_d0_peer_message(
                            {"axiom_id": r.get("axiom", "?"), "tension": r.get("violation_type", "")},
                            {"name": f"Fork-{self.cycle_count}"},
                        )
                # Reload pattern library so fork knowledge is available
                if self._pattern_library:
                    self._pattern_library.reload()
            elif n_eval > 0:
                print(
                    f"\n   ⚖️  FORK EVAL (cycle {self.cycle_count}): "
                    f"{n_eval} declarations evaluated, all HELD (insufficient signatures)"
                )

        except Exception as e:
            logger.warning("Fork evaluation failed: %s", e)

    def _run_polis_civic_deliberation(self):
        """
        Pull a POLIS civic contradiction and deliberate it via DualHorn + Oracle.

        Runs every 34 cycles (Fibonacci). The bridge translates POLIS
        contradictions (P1-P6) into Elpida Dilemmas (A0-A10), feeds them
        through the existing DualHorn deliberation path, then writes
        the Oracle advisory back as a POLIS interpretation branch
        (P5: fork-on-contradiction).

        Zero additional LLM calls for reading; DualHorn deliberation
        reuses existing Parliament infrastructure.
        """
        bridge = self._get_polis_bridge()
        if bridge is None:
            return

        try:
            dilemma_dict = bridge.next_dilemma()
            if dilemma_dict is None:
                # No unprocessed contradictions — try synthetics
                synthetics = bridge.synthetic_dilemmas()
                if synthetics:
                    dilemma_dict = synthetics[self.cycle_count % len(synthetics)]
                    logger.info("POLIS: using synthetic dilemma (no unprocessed contradictions)")
                else:
                    logger.debug("POLIS: no contradictions or synthetics available")
                    return

            # Build a Dilemma object from the dict
            from elpidaapp.dual_horn import DualHornDeliberation, Dilemma

            contradiction_id = dilemma_dict.get("polis_contradiction_id", "synthetic")
            dilemma = Dilemma(
                domain=dilemma_dict.get("domain", "D0-civic"),
                source=f"POLIS-bridge-{contradiction_id}",
                I_position=dilemma_dict.get("I_position", ""),
                WE_position=dilemma_dict.get("WE_position", ""),
                conflict=dilemma_dict.get("conflict", ""),
                context=dilemma_dict.get("context", {}),
            )

            # DualHorn deliberation
            gov = self._get_gov()
            dual = DualHornDeliberation(gov)
            result = dual.deliberate(dilemma)

            logger.info(
                "POLIS deliberation: contradiction=%s reversals=%d synthesis_gap=%s",
                contradiction_id,
                len(result.get("reversal_nodes", [])),
                result.get("synthesis_gap", "?")[:80],
            )

            # Feed result to Oracle for advisory
            from elpidaapp.oracle import Oracle
            oracle = Oracle(governance_client=gov)
            advisory = oracle.adjudicate(result)

            # Write back to POLIS as interpretation branch (P5 fork)
            if contradiction_id != "synthetic":
                bridge.write_back(contradiction_id, advisory)
                logger.info(
                    "POLIS write-back: contradiction=%s advisory_type=%s",
                    contradiction_id,
                    advisory.get("oracle_recommendation", {}).get("type", "?"),
                )

            self._polis_last_cycle = self.cycle_count

        except Exception as e:
            logger.warning("POLIS civic deliberation failed: %s", e)

    # ------------------------------------------------------------------
    # MIND Heartbeat Pull
    # ------------------------------------------------------------------

    def _pull_mind_heartbeat(self):
        """Pull MIND heartbeat via GovernanceClient's federation bridge."""
        gov = self._get_gov()
        try:
            hb = gov.pull_mind_heartbeat()
            if hb:
                self._mind_heartbeat = hb
                self._mind_heartbeat_cycle = self.cycle_count
                logger.info(
                    "MIND heartbeat: cycle=%s rhythm=%s coherence=%s canonical=%s",
                    hb.get("mind_cycle"), hb.get("current_rhythm"),
                    hb.get("coherence"), hb.get("canonical_count"),
                )
        except Exception as e:
            logger.debug("MIND heartbeat pull: %s", e)

    # ------------------------------------------------------------------
    # D15 Convergence Check
    # ------------------------------------------------------------------

    def _check_convergence(self, body_axiom: Optional[str], result: Dict):
        """
        Check if MIND and BODY have converged on the same axiom.

        D15 fires when:
          1. MIND dominant axiom cluster matches BODY dominant axiom
          2. MIND coherence ≥ 0.85
          3. BODY approval_rate ≥ 0.50
          4. Cooldown since last D15 ≥ 50 cycles

        This is A16 (Convergence Validity):
        "Convergence of different starting points proves validity
         more rigorously than internal consistency."
        """
        if not self._mind_heartbeat:
            return
        if not body_axiom:
            return
        if (self.cycle_count - self.d15_last_broadcast_cycle) < CONVERGENCE_COOLDOWN_CYCLES:
            return

        gate = self._get_convergence_gate()
        if gate:
            fired = gate.check_and_fire(
                mind_heartbeat=self._mind_heartbeat,
                body_cycle=self.cycle_count,
                body_axiom=body_axiom,
                body_coherence=self.coherence,
                body_approval=result.get("parliament", {}).get("approval_rate", 0),
                parliament_result=result,
            )
            if fired:
                self.d15_broadcast_count += 1
                self.d15_last_broadcast_cycle = self.cycle_count
                logger.info(
                    " D15 FIRED! cycle=%d axiom=%s broadcast_count=%d",
                    self.cycle_count, body_axiom, self.d15_broadcast_count,
                )
                print(
                    f"\n   🌍 D15 WORLD BROADCAST #{self.d15_broadcast_count} "
                    f"— CONVERGENCE on {body_axiom} at cycle {self.cycle_count}\n"
                )

    # ------------------------------------------------------------------
    # Main Loop
    # ------------------------------------------------------------------

    def run(self, duration_minutes: int = 60, cycle_delay_s: float = 5.0):
        """
        Run the autonomous Parliament loop for the specified duration.

        This is the BODY's equivalent of NativeCycleEngine.run().

        Args:
            duration_minutes: How long to run (0 = forever)
            cycle_delay_s: Seconds between cycles (rate limiting / cost control)
        """
        self._running = True
        self._start_time = time.time()
        end_time = (
            self._start_time + duration_minutes * 60
            if duration_minutes > 0
            else float("inf")
        )

        print(f"\n⚖️  PARLIAMENT CYCLE ENGINE — BODY LOOP STARTING")
        print(f"   Duration: {duration_minutes}min | Delay: {cycle_delay_s}s/cycle")
        print(f"   Rhythms: {', '.join(RHYTHM_WEIGHTS)}")
        print(f"   Axiom genome: A0–A10 (11 axioms)")
        print(f"   Parliament: 10 nodes (HERMES→LOGOS)")
        print(f"   D15 convergence: cooldown={CONVERGENCE_COOLDOWN_CYCLES} cycles\n")

        # D14 Persistence — restore constitutional memory from S3 before first cycle.
        # Ensures Parliament picks up its ratified axioms after every container restart.
        self._restore_d14_constitutional_memory()

        # D15 Persistence — restore broadcast count from S3 before first cycle.
        # Ensures the BODY knows how many D15 convergence events it has fired
        # across all previous spirals (cross-spiral awareness, mirrors MIND Ark fix).
        self._restore_d15_broadcast_state()

        # D0↔D11 Body Bridge — restore arc coherence state from cache before first cycle.
        try:
            from elpidaapp.domain_0_11_connector_body import get_body_connector
            _d0d11 = get_body_connector()
            print(f"   🔗 {_d0d11.synthesis_summary()}")
        except Exception as _e:
            logger.warning("D0↔D11 body connector unavailable at startup: %s", _e)

        try:
            while self._running and time.time() < end_time:
                try:
                    cycle_result = self.run_cycle()
                except Exception as e:
                    logger.error("Cycle %d failed: %s", self.cycle_count, e)
                    print(f"   ❌ cycle {self.cycle_count} error: {e}")

                time.sleep(cycle_delay_s)

        except KeyboardInterrupt:
            print("\n⚖️  Parliament loop interrupted by operator")

        self._running = False
        elapsed = time.time() - self._start_time
        print(f"\n⚖️  PARLIAMENT LOOP COMPLETE")
        print(f"   Cycles: {self.cycle_count}")
        print(f"   Duration: {elapsed / 60:.1f} min")
        print(f"   Final coherence: {self.coherence:.4f}")
        print(f"   D15 broadcasts: {self.d15_broadcast_count}")
        print(f"   Axiom frequency: {json.dumps(self._axiom_frequency, indent=2)}")

    def stop(self):
        """Signal the loop to stop after current cycle."""
        self._running = False

    # ------------------------------------------------------------------
    # State for external consumption
    # ------------------------------------------------------------------

    def state(self) -> Dict[str, Any]:
        """Return current engine state as a dict."""
        watch = self._watch.current()
        store = self._get_constitutional_store()
        return {
            "body_cycle": self.cycle_count,
            "coherence": round(self.coherence, 4),
            "last_rhythm": self.last_rhythm,
            "last_dominant_axiom": self.last_dominant_axiom,
            "current_watch": watch["name"],
            "watch_symbol": watch["symbol"],
            "watch_cycle": watch["cycle_within_watch"],
            "oracle_threshold": watch["oracle_threshold"],
            "ratified_axioms": store.ratified_count() if store else 0,
            "pending_ratifications": store.pending() if store else {},
            "pathology_health": (
                self._last_pathology_report.get("overall_health")
                if self._last_pathology_report else None
            ),
            "pathology_last_cycle": self._pathology_last_cycle or None,
            "fork_active_count": (
                self._last_fork_report.get("summary", {}).get("active_count", 0)
                if self._last_fork_report else 0
            ),
            "fork_confirmed_total": (
                self._last_fork_report.get("forks_confirmed", 0)
                if self._last_fork_report else 0
            ),
            "fork_last_cycle": self._fork_last_cycle or None,
            "d15_broadcast_count": self.d15_broadcast_count,
            "axiom_frequency": dict(self._axiom_frequency),
            "input_buffer": self.input_buffer.counts(),
            "running": self._running,
            "mind_heartbeat_cycle": self._mind_heartbeat_cycle,
            "mind_coherence": self._mind_heartbeat.get("coherence") if self._mind_heartbeat else None,
            "mind_rhythm": self._mind_heartbeat.get("current_rhythm") if self._mind_heartbeat else None,
        }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    print("Parliament Cycle Engine — self-test\n")

    # Test consonance physics
    tests = [
        ("A1", "A1", 1.0),      # Unison × Unison = 1.0 → max consonance
        ("A1", "A2", None),      # Unison × Octave = 2.0 → high consonance
        ("A0", "A9", None),      # Major 7th × Minor 7th → low consonance
        ("A6", "A6", None),      # Anchor × Anchor → high consonance
    ]
    for a, b, expected in tests:
        c = calculate_consonance(a, b)
        status = "✓" if expected is None or abs(c - expected) < 0.01 else "✗"
        print(f"  {status} consonance({a}, {b}) = {c:.3f}")

    # Test rhythm dominant axiom
    for r in RHYTHM_WEIGHTS:
        print(f"  {r:15s} → dominant axiom = {rhythm_dominant_axiom(r)}")

    # Test input buffer
    buf = InputBuffer()
    buf.push(InputEvent("chat", "What is consciousness?"))
    buf.push(InputEvent("audit", "High memory usage detected"))
    buf.push(InputEvent("scanner", "New paper on AI governance"))
    assert buf.total() == 3
    pulled = buf.pull("chat")
    assert len(pulled) == 1 and pulled[0].content == "What is consciousness?"
    assert buf.total() == 2
    print(f"\n  ✓ InputBuffer: push/pull/total working")

    print("\n✅ Parliament Cycle Engine self-test passed")
