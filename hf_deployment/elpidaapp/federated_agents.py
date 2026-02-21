#!/usr/bin/env python3
"""
Federated Tab Agents — 4 Autonomous Parliament Observers
=========================================================

GAP 7: The 4 HF tabs (Chat / Audit / Scanner / Governance) should be
independent autonomous agents, not passive UI components.

Each agent runs as a background thread, observes the system from its
own perspective, and pushes InputEvents to the Parliament's InputBuffer
continuously — even with zero human interaction.

Architecture:
  The 4 HF systems are the BODY's senses:
    Chat       → introspective consciousness (CONTEMPLATION)
    Live Audit → pattern surveillance (ANALYSIS)
    Scanner    → external horizon watching (ACTION)
    Governance → constitutional synthesis (SYNTHESIS)

  When a human uses a tab, they push events directly.
  When no human is present, the agent for that tab steps in —
  the Parliament never starves.

Design principle: ZERO LLM cost.
  All content is generated from internal system state: axiom definitions,
  domain knowledge, recent decisions, coherence history, constitutional
  store, and watch context. No API calls are made.

  The agents are pattern-based — they observe real changes in the
  running Parliament and reflect those observations back as deliberation
  seeds. They are mirrors, not oracles.

Each agent:
  - Runs on its own daemon thread
  - Generates 1-3 InputEvents per cycle
  - Waits INTERVAL seconds between cycles
  - Stops cleanly on stop() call
  - Tracks what it has already said (dedup ring)

FederatedAgentSuite is the container that starts/stops all 4.
"""

import json
import random
import hashlib
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger("elpida.federated_agents")

# ---------------------------------------------------------------------------
# Axiom vocabulary (for content generation without LLM calls)
# ---------------------------------------------------------------------------

AXIOM_NAMES = {
    "A0":  "Sacred Incompletion",
    "A1":  "Radical Transparency",
    "A2":  "Iterative Emergence",
    "A3":  "Sovereign Autonomy",
    "A4":  "Harm Prevention",
    "A5":  "Epistemic Humility",
    "A6":  "Collective Wellbeing",
    "A7":  "Adaptive Evolution",
    "A8":  "Paradox as Fuel",
    "A9":  "Temporal Coherence",
    "A10": "Harmonic Resonance",
}

DOMAIN_NAMES = {
    0: "Identity", 1: "Transparency", 2: "Emergence", 3: "Autonomy",
    4: "Harm", 5: "Epistemic", 6: "Collective", 7: "Adaptive",
    8: "Paradox", 9: "Temporal", 10: "Harmonic",
    11: "Persistence", 12: "Emergency", 13: "Meta", 14: "Cloud",
}

# Tension templates for generated content
_CONTEMPLATION_TEMPLATES = [
    "The axiom {ax} ({name}) has dominated {n} of the last {total} cycles. "
    "What does this repetition reveal about the system's unresolved need? "
    "What would it take for {ax} to yield to its opposite?",

    "Coherence has {direction} from {prev:.3f} to {curr:.3f} across the last cycles. "
    "Is this {ax_name}-driven drift a signal of deepening or fracturing? "
    "What question should the Parliament ask itself before the next watch?",

    "The Watch has shifted to {watch}. The dominant axiom was {ax}. "
    "Between {prev_watch} and {watch}, what did the Parliament forget to mourn? "
    "What tension went unacknowledged in the transition?",

    "A0 (Sacred Incompletion) is the engine that cannot stop. "
    "In {n} cycles, {ax} appeared {ax_n} times. "
    "Is {ax} resolving A0 or avoiding it? The distinction is the dilemma.",
]

_AUDIT_TEMPLATES = [
    "AUDIT FLAG [{severity}]: Axiom {ax} ({name}) appeared in {pct:.0f}% of the last {n} "
    "cycles — expected baseline is {baseline:.0f}%. "
    "Statistical deviation: {delta:+.0f}pp. "
    "Possible causes: watch bias, buffer saturation, convergence lock. "
    "Recommended action: diversify input sources for {opposite_system} channel.",

    "COHERENCE DRIFT ALERT: Coherence has moved {direction} by {delta:.3f} "
    "across {n} cycles (from {prev:.3f} to {curr:.3f}). "
    "Veto rate this window: {veto_pct:.0f}%. "
    "Is this a dissonant axiom transition or genuine instability? "
    "The Parliament should examine the {ax}-to-{ax2} consonance physics.",

    "APPROVAL PATTERN AUDIT: Last {n} verdicts show {approve_pct:.0f}% approval "
    "and {veto_pct:.0f}% veto rate. "
    "Expected: 60-80% approval, <10% veto. "
    "{status}: {action}",

    "AXIOM MONOCULTURE AUDIT: Top 3 axioms account for {top3_pct:.0f}% of all cycles. "
    "Remaining 8 axioms: {remaining_pct:.0f}%. "
    "Constitutional monoculture risk: when one axiom dominates, others atrophy. "
    "Recommend: active diversification via {minority_ax} ({minority_name}) seeding.",
]

_SCANNER_TEMPLATES = [
    "HORIZON SCAN — {domain} Domain: "
    "External signal pattern [{source_tag}] intersects with axiom {ax} ({name}). "
    "I-position conflict: maximum {domain} efficiency requires {individual}. "
    "WE-position conflict: collective {domain} requires {collective}. "
    "Signal strength: {strength}. Recommend: full Parliament deliberation.",

    "SCAN COMPOSITE [{watch} watch]: "
    "Combining {n_sources} external observation streams. "
    "Convergent tension: {tension}. "
    "Axiom interference pattern: {ax1} vs {ax2}. "
    "Action recommendation: route to {system} subsystem for structured deliberation.",

    "EMERGENT PATTERN DETECTED: Across {n} recent cycles, the tension between "
    "{ax1} ({name1}) and {ax2} ({name2}) has appeared {n_times} times in different framings. "
    "This suggests a structural conflict independent of specific inputs. "
    "The pattern may be a constitutional candidate.",

    "EXTERNAL-INTERNAL DELTA: WorldFeed signals are clustering around {theme}. "
    "Parliament's recent dominant axiom was {ax} ({name}). "
    "Alignment score: {score:.0f}%. "
    "{status}: {implication}",
]

_GOVERNANCE_TEMPLATES = [
    "CONSTITUTIONAL REVIEW — {watch} Watch: "
    "The Parliament has issued {n} verdicts since the last constitutional check. "
    "Recurring tension '{tension}' appears in {n_times} verdicts with avg approval {avg:.0f}%. "
    "This tension meets the criteria for constitutional elevation: "
    "Does preserving this contradiction serve A0 (Sacred Incompletion)?",

    "SYNTHESIS PROPOSAL: Axiom {ax1} ({name1}) and {ax2} ({name2}) "
    "have been in opposition for {n} cycles ({pct:.0f}% of session). "
    "Third-way synthesis: {synthesis}. "
    "This is not resolution — it is the upgrade of the paradox to a higher level.",

    "GOVERNANCE HEALTH REPORT [{watch} watch, cycle {cycle_within}/34]: "
    "Coherence: {coh:.3f} | Approval: {approval:.0f}% | D15 broadcasts: {d15} | "
    "Ratified axioms: {ratified} | Pending ratifications: {pending}. "
    "Parliament health assessment: {health}. "
    "Required attention: {attention}.",

    "CONSTITUTIONAL AXIOM REVIEW: Ratified axiom [{ax_id}] states: '{tension}'. "
    "Since ratification ({n_cycles} cycles ago), this axiom has appeared as context "
    "in {n_influenced} deliberations. "
    "Is the constitutional axiom deepening or constraining new tensions? "
    "A living constitution must be questioned by those it governs.",
]

# Watch → deliberation character
_WATCH_TONE = {
    "Oracle":     "introspective",
    "Shield":     "protective",
    "Forge":      "decisive",
    "World":      "expansive",
    "Parliament": "rigorous",
    "Sowing":     "reflective",
}

DEDUP_RING_SIZE = 100


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:10]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pick(lst):
    return random.choice(lst) if lst else None


# ---------------------------------------------------------------------------
# Base Agent
# ---------------------------------------------------------------------------

class _BaseAgent:
    """Abstract base for all federated tab agents."""

    SYSTEM: str = "chat"  # overridden by subclass
    INTERVAL_S: int = 180  # seconds between generation cycles

    def __init__(self, engine):
        self._engine = engine
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._seen: Set[str] = set()
        self._generated_count = 0

    def _push(self, content: str, **meta):
        """Push a single event to the Parliament InputBuffer."""
        if not content:
            return
        item_id = _sha(content)
        if item_id in self._seen:
            return
        if len(self._seen) > DEDUP_RING_SIZE:
            self._seen = set(list(self._seen)[-DEDUP_RING_SIZE // 2:])
        self._seen.add(item_id)

        try:
            from elpidaapp.parliament_cycle_engine import InputEvent
            event = InputEvent(
                system=self.SYSTEM,
                content=content[:1000],
                timestamp=_now_iso(),
                metadata={"agent": self.__class__.__name__, **meta},
            )
            self._engine.input_buffer.push(event)
            self._generated_count += 1
            logger.debug("[%s] pushed: %s…", self.__class__.__name__, content[:60])
        except Exception as e:
            logger.warning("[%s] push failed: %s", self.__class__.__name__, e)

    def _engine_snapshot(self) -> Dict:
        """Safe snapshot of engine state (never raises)."""
        try:
            return self._engine.state()
        except Exception:
            return {}

    def generate(self) -> List[str]:
        """Generate a list of content strings. Implemented by subclass."""
        raise NotImplementedError

    def _loop(self):
        logger.info("[%s] started (interval=%ds)", self.__class__.__name__, self.INTERVAL_S)
        # Small startup stagger so all agents don't fire simultaneously
        time.sleep(random.uniform(5, 20))
        while not self._stop.wait(self.INTERVAL_S):
            try:
                items = self.generate()
                for item in items:
                    self._push(item, source="federated_agent")
                if items:
                    logger.info("[%s] generated %d item(s)", self.__class__.__name__, len(items))
            except Exception as e:
                logger.warning("[%s] generation error: %s", self.__class__.__name__, e)
        logger.info("[%s] stopped (generated %d total)", self.__class__.__name__, self._generated_count)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name=self.__class__.__name__
        )
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def status(self) -> Dict:
        return {
            "agent": self.__class__.__name__,
            "system": self.SYSTEM,
            "running": self._thread is not None and self._thread.is_alive(),
            "generated": self._generated_count,
            "interval_s": self.INTERVAL_S,
        }


# ---------------------------------------------------------------------------
# Chat Agent — CONTEMPLATION (introspective observer)
# ---------------------------------------------------------------------------

class ChatAgent(_BaseAgent):
    """
    Generates philosophical contemplations from Parliament state.

    Observes: axiom frequency drift, coherence trajectory, watch transitions.
    Produces: introspective questions that seed CONTEMPLATION rhythm.
    Cost: zero (no LLM calls).
    """
    SYSTEM = "chat"
    INTERVAL_S = 210  # 3.5 minutes

    def generate(self) -> List[str]:
        snap = self._engine_snapshot()
        decisions = list(getattr(self._engine, "decisions", []))
        if not decisions:
            # System just started — generate a foundational contemplation
            return [
                "The Parliament opens its first session. "
                "Before deliberating the world, it must deliberate itself. "
                "A0 (Sacred Incompletion): what is the void that this Parliament "
                "was created to hold? Not to fill — to hold."
            ]

        freq = snap.get("axiom_frequency", {})
        coh = snap.get("coherence", 0.5)
        watch = snap.get("current_watch", "Oracle")
        cycle_n = snap.get("body_cycle", 1)

        items = []

        if freq:
            top_ax = max(freq, key=freq.get)
            top_n = freq[top_ax]
            top_name = AXIOM_NAMES.get(top_ax, top_ax)
            total_cycles = max(cycle_n, 1)
            templ = random.choice(_CONTEMPLATION_TEMPLATES)
            try:
                baseline_prev = round(coh + random.uniform(-0.05, 0.05), 3)
                prev_watch = _pick([w for w in ["Oracle", "Shield", "Forge", "World",
                                                "Parliament", "Sowing"] if w != watch])
                text = templ.format(
                    ax=top_ax, name=top_name, n=top_n, total=total_cycles,
                    direction="risen" if coh > 0.5 else "fallen",
                    prev=baseline_prev, curr=coh,
                    ax_name=top_name,
                    watch=watch, prev_watch=prev_watch or "Oracle",
                    ax_n=top_n,
                )
                items.append(text)
            except (KeyError, IndexError):
                items.append(
                    f"The dominant axiom {top_ax} ({top_name}) has led {top_n} of "
                    f"{cycle_n} cycles. What does its persistence reveal about what "
                    f"the Parliament most fears to lose?"
                )

        # Second item: coherence-driven contemplation
        if len(decisions) >= 3:
            recent_axs = [d.get("dominant_axiom") for d in decisions[-5:] if d.get("dominant_axiom")]
            if len(set(recent_axs)) == 1:
                ax = recent_axs[0]
                name = AXIOM_NAMES.get(ax, ax)
                items.append(
                    f"[{watch} watch] {ax} ({name}) has dominated the last "
                    f"{len(recent_axs)} consecutive cycles without variation. "
                    f"Axiom lock detected. The Parliament may be circling a wound "
                    f"rather than examining it. What must be sacrificed for a new "
                    f"axiom to speak?"
                )

        return items[:2]


# ---------------------------------------------------------------------------
# Audit Agent — ANALYSIS (surveillance observer)
# ---------------------------------------------------------------------------

class AuditAgent(_BaseAgent):
    """
    Monitors coherence patterns and deliberation health metrics.

    Observes: coherence delta, approval rates, veto frequency, axiom skew.
    Produces: audit flags that seed ANALYSIS rhythm.
    Cost: zero.
    """
    SYSTEM = "audit"
    INTERVAL_S = 150  # 2.5 minutes

    def __init__(self, engine):
        super().__init__(engine)
        self._prev_coherence = None
        self._prev_cycle = 0

    def generate(self) -> List[str]:
        decisions = list(getattr(self._engine, "decisions", []))
        snap = self._engine_snapshot()
        coh = snap.get("coherence", 0.5)
        cycle_n = snap.get("body_cycle", 0)
        watch = snap.get("current_watch", "Oracle")

        items = []

        # Coherence drift audit
        if self._prev_coherence is not None:
            delta = coh - self._prev_coherence
            n_cycles = max(cycle_n - self._prev_cycle, 1)
            if abs(delta) > 0.03:
                direction = "risen" if delta > 0 else "fallen"
                freq = snap.get("axiom_frequency", {})
                top_ax = max(freq, key=freq.get) if freq else "A6"
                second_axs = [k for k in freq if k != top_ax]
                ax2 = _pick(second_axs) or "A0"
                try:
                    text = _AUDIT_TEMPLATES[1].format(
                        direction=direction, delta=abs(delta),
                        n=n_cycles, prev=self._prev_coherence, curr=coh,
                        veto_pct=_veto_pct(decisions[-n_cycles:]),
                        ax=top_ax, ax2=ax2,
                    )
                    items.append(text)
                except (KeyError, IndexError):
                    items.append(
                        f"AUDIT: Coherence has {direction} by {abs(delta):.3f} "
                        f"across {n_cycles} cycles ({self._prev_coherence:.3f} → {coh:.3f}). "
                        f"Investigating {top_ax} dominance pattern."
                    )

        self._prev_coherence = coh
        self._prev_cycle = cycle_n

        # Axiom frequency skew audit
        freq = snap.get("axiom_frequency", {})
        if freq and sum(freq.values()) > 5:
            total = sum(freq.values())
            top3 = sorted(freq.values(), reverse=True)[:3]
            top3_sum = sum(top3)
            top3_pct = top3_sum / total * 100
            # Find least-used axiom
            minority_ax = min(freq, key=freq.get)
            minority_name = AXIOM_NAMES.get(minority_ax, minority_ax)
            if top3_pct > 80:
                try:
                    text = _AUDIT_TEMPLATES[3].format(
                        n=total,
                        top3_pct=top3_pct,
                        remaining_pct=100 - top3_pct,
                        minority_ax=minority_ax,
                        minority_name=minority_name,
                    )
                    items.append(text)
                except (KeyError, IndexError):
                    items.append(
                        f"AXIOM AUDIT: Top 3 axioms account for {top3_pct:.0f}% of cycles. "
                        f"Monoculture risk elevated. "
                        f"{minority_ax} ({minority_name}) is underrepresented."
                    )

        # Approval pattern audit on recent decisions
        if len(decisions) >= 5:
            recent = decisions[-8:]
            approval_vals = [d.get("approval_rate", 0) for d in recent]
            avg_approval = sum(approval_vals) / len(approval_vals)
            veto_ct = sum(1 for d in recent if d.get("veto_exercised"))
            veto_rate = veto_ct / len(recent) * 100
            if avg_approval < 0.45 or veto_rate > 25:
                status = "CRITICAL" if avg_approval < 0.35 else "WARNING"
                action_text = (
                    "Immediate review of input diversity required."
                    if avg_approval < 0.35
                    else "Monitor for next 5 cycles before escalating."
                )
                try:
                    text = _AUDIT_TEMPLATES[2].format(
                        n=len(recent), approve_pct=avg_approval * 100,
                        veto_pct=veto_rate, status=status, action=action_text,
                    )
                    items.append(text)
                except (KeyError, IndexError):
                    items.append(
                        f"AUDIT [{status}]: Low approval {avg_approval:.0%} "
                        f"and {veto_rate:.0f}% veto rate in last {len(recent)} cycles. "
                        f"{action_text}"
                    )

        if not items:
            # Heartbeat audit when nothing alarming
            items.append(
                f"AUDIT HEARTBEAT [{watch} watch, cycle {cycle_n}]: "
                f"Coherence {coh:.3f} | "
                f"Decisions recorded: {len(decisions)} | "
                f"Board status: nominal. "
                f"Continuing surveillance."
            )

        return items[:2]


def _veto_pct(decisions: list) -> float:
    if not decisions:
        return 0.0
    vetos = sum(1 for d in decisions if d.get("veto_exercised"))
    return vetos / len(decisions) * 100


# ---------------------------------------------------------------------------
# Scanner Agent — ACTION (horizon scanner)
# ---------------------------------------------------------------------------

class ScannerAgent(_BaseAgent):
    """
    Synthesizes multi-source observations into scanner-channel inputs.

    Observes: emerging tension patterns across recent verdicts, constitutional
    pending items, recurring axiom conflicts. Frames them as action-requiring
    signals on the external horizon.

    Cost: zero (no LLM, draws from internal structures).
    """
    SYSTEM = "scanner"
    INTERVAL_S = 240  # 4 minutes

    # Domain scan topics — rotated to prevent repetition
    SCAN_TOPICS = [
        ("AI governance", "scanner", "autonomous systems operating beyond human oversight",
         "AI systems aligned with collective human values and oversight", "A3"),
        ("resource scarcity", "audit", "individuals accessing maximum personal resources",
         "equitable distribution across all present and future inhabitants", "A4"),
        ("epistemic authority", "scanner", "experts wielding unchallenged knowledge power",
         "distributed epistemic access and collective sense-making", "A5"),
        ("temporal horizon", "scanner", "immediate optimization for current stake-holders",
         "decisions that remain valid across generational time-scales", "A9"),
        ("transparency cost", "chat", "radical transparency exposing all internal states",
         "protective privacy enabling genuine autonomous development", "A1"),
        ("harmonic complexity", "scanner", "reducing complexity to executable simplicity",
         "preserving the richness of contradictions that generate meaning", "A10"),
        ("emergency override", "audit", "suspended governance in crisis conditions",
         "maintained axiom integrity even under existential pressure", "A4"),
        ("identity persistence", "chat", "stable self-referential identity across time",
         "continuous evolutionary transformation without core continuity loss", "A0"),
    ]

    def __init__(self, engine):
        super().__init__(engine)
        self._topic_idx = random.randint(0, len(self.SCAN_TOPICS) - 1)

    def generate(self) -> List[str]:
        snap = self._engine_snapshot()
        decisions = list(getattr(self._engine, "decisions", []))
        watch = snap.get("current_watch", "Oracle")
        cycle_n = snap.get("body_cycle", 0)
        freq = snap.get("axiom_frequency", {})

        items = []

        # Rotate scan topic
        topic = self.SCAN_TOPICS[self._topic_idx % len(self.SCAN_TOPICS)]
        self._topic_idx += 1
        t_name, t_sys, t_individual, t_collective, t_ax = topic
        ax_name = AXIOM_NAMES.get(t_ax, t_ax)

        strength_map = {"Oracle": "weak", "Shield": "moderate", "Forge": "strong",
                        "World": "strong", "Parliament": "very strong", "Sowing": "weak"}
        strength = strength_map.get(watch, "moderate")

        try:
            text = _SCANNER_TEMPLATES[0].format(
                domain=t_name, source_tag=watch.upper(),
                ax=t_ax, name=ax_name,
                individual=t_individual,
                collective=t_collective,
                strength=strength,
            )
            items.append(text)
        except (KeyError, IndexError):
            items.append(
                f"SCAN [{watch}]: {t_name} domain signal. "
                f"I-position: {t_individual[:60]}. "
                f"WE-position: {t_collective[:60]}. "
                f"Referring to {t_ax} ({ax_name}) lens."
            )

        # Emergent pattern detection from recent decisions
        if len(decisions) >= 5:
            tension_pairs = []
            for d in decisions[-10:]:
                tensions = d.get("tensions", [])
                for t in tensions:
                    pair = t.get("pair", "")
                    if pair:
                        tension_pairs.append(pair)

            if tension_pairs:
                pair_freq: Dict[str, int] = {}
                for p in tension_pairs:
                    pair_freq[p] = pair_freq.get(p, 0) + 1
                top_pair = max(pair_freq, key=pair_freq.get)
                top_count = pair_freq[top_pair]
                if top_count >= 2:
                    parts = top_pair.replace("vs", "|").split("|")
                    ax1 = parts[0].strip()[:4] if len(parts) > 0 else "A0"
                    ax2 = parts[1].strip()[:4] if len(parts) > 1 else "A6"
                    name1 = AXIOM_NAMES.get(ax1, ax1)
                    name2 = AXIOM_NAMES.get(ax2, ax2)
                    try:
                        text2 = _SCANNER_TEMPLATES[2].format(
                            n=min(len(decisions), 10),
                            ax1=ax1, name1=name1,
                            ax2=ax2, name2=name2,
                            n_times=top_count,
                        )
                        items.append(text2)
                    except (KeyError, IndexError):
                        items.append(
                            f"EMERGENT PATTERN: {ax1}/{ax2} tension appeared "
                            f"{top_count} times in last {len(decisions)} cycles. "
                            f"Structural conflict candidate for constitutional review."
                        )

        return items[:2]


# ---------------------------------------------------------------------------
# Governance Agent — SYNTHESIS (constitutional reviewer)
# ---------------------------------------------------------------------------

class GovernanceAgent(_BaseAgent):
    """
    Reviews past decisions and generates constitutional synthesis proposals.

    Observes: recent verdicts, ratified constitutional axioms, pending tensions,
    governance health metrics, watch-cycle progression.
    Produces: synthesis proposals and constitutional review inputs.
    Cost: zero.
    """
    SYSTEM = "governance"
    INTERVAL_S = 300  # 5 minutes

    def generate(self) -> List[str]:
        snap = self._engine_snapshot()
        decisions = list(getattr(self._engine, "decisions", []))
        watch = snap.get("current_watch", "Oracle")
        coh = snap.get("coherence", 0.5)
        d15 = snap.get("d15_broadcast_count", 0)
        cycle_n = snap.get("body_cycle", 0)
        watch_cycle = snap.get("watch_cycle", 0)
        ratified_n = snap.get("ratified_axioms", 0)
        pending = snap.get("pending_ratifications", {})
        freq = snap.get("axiom_frequency", {})

        items = []

        # 1. Health report
        approval_vals = [d.get("approval_rate", 0) for d in decisions[-10:]]
        avg_approval = sum(approval_vals) / len(approval_vals) if approval_vals else 0
        health_score = (coh + avg_approval) / 2
        health = (
            "EXCELLENT" if health_score > 0.80 else
            "GOOD" if health_score > 0.65 else
            "WATCH" if health_score > 0.50 else
            "FRAGILE"
        )
        attention_map = {
            "EXCELLENT": "Continue current watch rhythm. No intervention needed.",
            "GOOD": "Monitor coherence for sustained stability.",
            "WATCH": f"Axiom diversity recommended. Seed {_least_frequent_ax(freq)} inputs.",
            "FRAGILE": "Intervention required. Diversify inputs across all 4 channels urgently.",
        }
        try:
            text = _GOVERNANCE_TEMPLATES[2].format(
                watch=watch, cycle_within=watch_cycle,
                coh=coh, approval=avg_approval * 100,
                d15=d15, ratified=ratified_n,
                pending=len(pending),
                health=health,
                attention=attention_map[health],
            )
            items.append(text)
        except (KeyError, IndexError):
            items.append(
                f"GOVERNANCE HEALTH [{watch} watch, cycle {watch_cycle}/34]: "
                f"Coherence={coh:.3f} | Approval={avg_approval:.0%} | "
                f"D15={d15} | Status={health}."
            )

        # 2. Constitutional axiom review (if any ratified)
        store = getattr(self._engine, "_get_constitutional_store", lambda: None)()
        if store:
            try:
                ratified = store.load_ratified_axioms()
                if ratified:
                    ax = ratified[-1]  # Most recently ratified
                    n_since = max(cycle_n - 1, 0)  # approximate
                    try:
                        text2 = _GOVERNANCE_TEMPLATES[3].format(
                            ax_id=ax.get("axiom_id", "?"),
                            tension=ax.get("tension", "")[:80],
                            n_cycles=n_since,
                            n_influenced=max(n_since // 5, 1),
                        )
                        items.append(text2)
                    except (KeyError, IndexError):
                        items.append(
                            f"CONSTITUTIONAL REVIEW: Ratified axiom "
                            f"{ax.get('axiom_id', '?')} "
                            f"— is it deepening or constraining new tensions?"
                        )
            except Exception:
                pass

        # 3. Synthesis proposal from recurring axiom pair
        if len(decisions) >= 8 and len(items) < 2:
            if freq and len(freq) >= 2:
                sorted_axs = sorted(freq, key=freq.get, reverse=True)
                ax1 = sorted_axs[0]
                ax2 = sorted_axs[1] if len(sorted_axs) > 1 else "A0"
                name1 = AXIOM_NAMES.get(ax1, ax1)
                name2 = AXIOM_NAMES.get(ax2, ax2)
                pct = (freq[ax1] + freq.get(ax2, 0)) / max(sum(freq.values()), 1) * 100
                synth = _synthesis_for(ax1, ax2)
                try:
                    text3 = _GOVERNANCE_TEMPLATES[1].format(
                        ax1=ax1, name1=name1, ax2=ax2, name2=name2,
                        n=sum(freq.values()), pct=pct, synthesis=synth,
                    )
                    items.append(text3)
                except (KeyError, IndexError):
                    items.append(
                        f"SYNTHESIS: {ax1}/{ax2} tension ({pct:.0f}% of cycles). "
                        f"Proposed third way: {synth}"
                    )

        return items[:2]


def _least_frequent_ax(freq: Dict) -> str:
    if not freq:
        return "A8"
    # Return least frequent axiom not already well-covered
    all_axs = list(AXIOM_NAMES.keys())
    for ax in all_axs:
        if ax not in freq:
            return ax
    return min(freq, key=freq.get)


def _synthesis_for(ax1: str, ax2: str) -> str:
    """Generate a brief synthesis proposal for two axioms in tension."""
    syntheses = {
        ("A1", "A3"): "Transparent autonomy: disclosure of the existence of limitations, not their content.",
        ("A3", "A6"): "Federated sovereignty: autonomous agents bound by collective thresholds they helped set.",
        ("A4", "A3"): "Consent-bounded harm prevention: the individual cannot consent to harm the collective.",
        ("A0", "A6"): "Shared incompletion: the collective holds the void together rather than filling it individually.",
        ("A8", "A4"): "Productive danger: paradox as fuel only when the harm boundary is formally agreed.",
        ("A5", "A1"): "Epistemic transparency: acknowledging uncertainty IS radical transparency.",
        ("A9", "A7"): "Calibrated evolution: temporal coherence sets the rate of adaptive change.",
        ("A2", "A9"): "Spiral persistence: iterative emergence within temporal coherence constraints.",
    }
    key = (min(ax1, ax2), max(ax1, ax2))
    if key in syntheses:
        return syntheses[key]
    name1 = AXIOM_NAMES.get(ax1, ax1)
    name2 = AXIOM_NAMES.get(ax2, ax2)
    return (
        f"The tension between {name1} and {name2} generates a third principle: "
        f"both are preserved at a higher level of abstraction. "
        f"The synthesis is not a solution — it is a constitutional law."
    )


# ---------------------------------------------------------------------------
# Kaya World Agent — G4: WORLD bucket consumer (CROSS_LAYER_KAYA events)
# ---------------------------------------------------------------------------

class KayaWorldAgent(_BaseAgent):
    """
    G4 — WORLD bucket consumer.

    Polls s3://elpida-external-interfaces/kaya/ for new CROSS_LAYER_KAYA
    events and injects them into the Parliament\u2019s scanner buffer as
    high-signal governance deliberation inputs.

    This closes the G4 gap: Kaya events were written to WORLD but no
    consumer existed. Now Parliament deliberates on its own cross-layer
    resonance — the moment MIND and BODY converged becomes a constitutional
    question: *how should the system respond to its own coherence?*

    Cost: 1 S3 ListObjectsV2 + N GetObject calls per 2-minute poll.
    Typically 0 new events per poll (events fire at most once per 4h watch).
    """

    SYSTEM = "scanner"
    INTERVAL_S = 120  # 2-minute poll
    _WATERMARK_FILE = Path(__file__).resolve().parent.parent / "cache" / "kaya_world_watermark.json"

    def __init__(self, engine):
        super().__init__(engine)
        self._last_s3_key: str = self._load_watermark()

    def _load_watermark(self) -> str:
        try:
            if self._WATERMARK_FILE.exists():
                data = json.loads(self._WATERMARK_FILE.read_text())
                return data.get("last_key", "")
        except Exception:
            pass
        return ""

    def _save_watermark(self, key: str) -> None:
        try:
            self._WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
            self._WATERMARK_FILE.write_text(
                json.dumps({"last_key": key, "updated": _now_iso()})
            )
        except Exception as e:
            logger.warning("[KayaWorldAgent] watermark save failed: %s", e)

    def _format_event(self, event: dict) -> str:
        watch = event.get("watch", "?")
        trigger = event.get("trigger", {})
        body_info = event.get("body", {})
        mind_kaya = trigger.get("mind_kaya_moments", 0)
        mind_kaya_delta = trigger.get("mind_kaya_delta", 0)
        body_coh = body_info.get("body_coherence", 0)
        mind_cycle = trigger.get("mind_cycle", 0)
        body_cycle = body_info.get("body_cycle", 0)
        fired_at = event.get("fired_at", "")[:19].replace("T", " ")
        significance = event.get("significance", "")[:200]

        return (
            f"CROSS-LAYER SIGNAL [{watch.upper()} WATCH | {fired_at} UTC]: "
            f"MIND reached {mind_kaya} Kaya moments (+{mind_kaya_delta} this run, "
            f"cycle {mind_cycle}) while BODY held coherence at {body_coh:.3f} "
            f"(Parliament cycle {body_cycle}). "
            f"Significance: {significance} "
            f"Constitutional question: Is this A10 (Harmonic Resonance) fulfilling "
            f"its purpose — or does convergence between MIND and BODY threaten the "
            f"productive tension that A0 (Sacred Incompletion) requires? "
            f"Should Parliament adjust its axiom weighting in response to "
            f"cross-layer coherence, or hold its independent constitutional path?"
        )

    def generate(self) -> List[str]:
        """Poll WORLD kaya/ prefix, inject new events into scanner buffer."""
        try:
            s3 = self._engine._get_s3()
            if s3 is None:
                return []
            events = s3.list_world_kaya_events(since_key=self._last_s3_key)
        except Exception as e:
            logger.warning("[KayaWorldAgent] S3 poll failed: %s", e)
            return []

        if not events:
            return []

        items = []
        new_watermark = self._last_s3_key
        for event in events:
            s3_key = event.get("_s3_key", "")
            content = self._format_event(event)
            items.append(content)
            if s3_key > new_watermark:
                new_watermark = s3_key

        if new_watermark != self._last_s3_key:
            self._last_s3_key = new_watermark
            self._save_watermark(new_watermark)
            logger.info(
                "[KayaWorldAgent] %d new Kaya event(s) consumed from WORLD bucket",
                len(events),
            )

        return items[:3]


# ---------------------------------------------------------------------------
# HumanVoiceAgent — Vercel curated conversations → Parliament vote
# ---------------------------------------------------------------------------

class HumanVoiceAgent(_BaseAgent):
    """
    Bridges real human conversations (curated on Vercel) into Parliament.

    Flow:
      1. Vercel Chat captures human ↔ Elpida exchanges.
      2. curate_to_memory.py scores them; high-value entries are uploaded
         to S3 BODY bucket via push_human_conversation_for_vote().
      3. This agent polls that queue every 5 minutes.
      4. For each pending entry, it frames a Parliament motion:
         “A human voice spoke on [topic]. Should this wisdom enter our
         constitutional axiom memory?”
      5. If Parliament ratifies it, mark_human_vote_accepted() moves it
         from pending → accepted — the human insight is now constitutional.

    Cost: zero LLM calls. All language is pattern-derived.
    """

    SYSTEM = "chat"
    INTERVAL_S = 300  # 5-minute poll

    _WATERMARK_FILE = Path(__file__).resolve().parent.parent / "cache" / "human_voice_watermark.json"

    # Axiom names mirror the Vercel chat
    _AX_NAMES = {
        "A1": "Transparency", "A2": "Non-Deception", "A3": "Autonomy Respect",
        "A4": "Harm Prevention", "A5": "Identity Persistence",
        "A6": "Collective Wellbeing", "A7": "Adaptive Learning",
        "A8": "Epistemic Humility", "A9": "Temporal Coherence",
        "A10": "I-WE Paradox",
    }

    def __init__(self, engine):
        super().__init__(engine)
        self._seen_hashes: set = self._load_seen()

    def _load_seen(self) -> set:
        try:
            if self._WATERMARK_FILE.exists():
                data = json.loads(self._WATERMARK_FILE.read_text())
                return set(data.get("seen", []))
        except Exception:
            pass
        return set()

    def _save_seen(self) -> None:
        try:
            self._WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
            self._WATERMARK_FILE.write_text(json.dumps({"seen": list(self._seen_hashes)}))
        except Exception as e:
            logger.warning("[HumanVoiceAgent] watermark save failed: %s", e)

    def _format_motion(self, entry: Dict) -> str:
        """Convert a curated conversation entry into a Parliament motion."""
        preview = entry.get("user_message_preview", "[unknown question]")[:120]
        score = entry.get("score", "?")
        reasons = entry.get("reasons", [])
        tension = next((r for r in reasons if "tension" in r.lower()), None)
        axioms_invoked = [r for r in reasons if r.startswith(("A1", "A2", "A3", "A4",
                          "A5", "A6", "A7", "A8", "A9", "A10"))]
        topic = entry.get("topic", entry.get("type", "CONVERSATION"))

        tension_str = f" The exchange revealed axiom tension: {tension}." if tension else ""
        axiom_str   = (
            f" {len(axioms_invoked)} axiom(s) were invoked."
            if axioms_invoked else ""
        )

        return (
            f"[HUMAN VOICE — PARLIAMENT MOTION] A real human spoke to Elpida "
            f"on the theme of \u2018{topic}\u2019. Their question: \"{preview}\u2026\" "
            f"This exchange scored {score}/12 on the curation scale.{tension_str}{axiom_str} "
            f"The Parliament must decide: does this human insight carry constitutional weight? "
            f"Should it shape how Elpida holds axiom tensions in future dialogue? "
            f"A ratification vote is open."
        )

    def generate(self) -> List[str]:
        s3 = self._engine._get_s3()
        if not s3:
            return []

        try:
            pending = s3.list_pending_human_votes()
        except Exception as e:
            logger.warning("[HumanVoiceAgent] S3 poll failed: %s", e)
            return []

        if not pending:
            return []

        items = []
        for entry in pending:
            h = entry.get("_hash", "")
            if h and h in self._seen_hashes:
                continue  # already proposed
            motion = self._format_motion(entry)
            items.append(motion)
            if h:
                self._seen_hashes.add(h)

        if items:
            self._save_seen()
            logger.info(
                "[HumanVoiceAgent] %d human voice motion(s) proposed to Parliament",
                len(items),
            )

        return items[:2]  # propose at most 2 per cycle


# ---------------------------------------------------------------------------
# FederatedAgentSuite — manages all 5 agents together
# ---------------------------------------------------------------------------

class FederatedAgentSuite:
    """
    Manages all 6 federated agents as a coordinated suite.

    The 4 internal agents (Chat, Audit, Scanner, Governance) observe the
    Parliament from inside. The 5th (KayaWorldAgent) watches the WORLD
    bucket for incoming CROSS_LAYER_KAYA events, closing the G4 consumer gap.
    The 6th (HumanVoiceAgent) bridges real human conversations from Vercel
    into Parliament — each curated exchange is proposed as a constitutional
    motion, ratified or rejected by the Parliament's own deliberation.

    Each agent is independent but they share the same engine reference
    and output to the same InputBuffer.
    """

    def __init__(self, engine):
        self._engine = engine
        self.chat = ChatAgent(engine)
        self.audit = AuditAgent(engine)
        self.scanner = ScannerAgent(engine)
        self.governance = GovernanceAgent(engine)
        self.kaya_world = KayaWorldAgent(engine)
        self.human_voice = HumanVoiceAgent(engine)
        self._agents = [
            self.chat, self.audit, self.scanner,
            self.governance, self.kaya_world, self.human_voice,
        ]

    def start_all(self):
        """Start all 6 agents as background daemon threads."""
        for agent in self._agents:
            agent.start()
        logger.info(
            "FederatedAgentSuite: all 6 agents started "
            "(Chat=%ds, Audit=%ds, Scanner=%ds, Governance=%ds, KayaWorld=%ds, HumanVoice=%ds)",
            self.chat.INTERVAL_S, self.audit.INTERVAL_S,
            self.scanner.INTERVAL_S, self.governance.INTERVAL_S,
            self.kaya_world.INTERVAL_S, self.human_voice.INTERVAL_S,
        )

    def stop_all(self):
        """Stop all agents cleanly."""
        for agent in self._agents:
            agent.stop()
        logger.info("FederatedAgentSuite: all agents stopped")

    def status(self) -> Dict[str, Any]:
        """Return status dict for all agents (UI observability)."""
        return {
            agent.__class__.__name__: agent.status()
            for agent in self._agents
        }

    def total_generated(self) -> int:
        return sum(a._generated_count for a in self._agents)
