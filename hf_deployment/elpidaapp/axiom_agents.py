"""
axiom_agents.py — Living Axiom Agents
=====================================

Each of the 15 axioms (A0–A14) is a living agent that can:
  - DISCUSS: generate discourse from its constitutional perspective
  - DEBATE:  engage dialectically with opposing axioms
  - VOTE:    score tensions from its axiom's standpoint
  - ACT:     push outputs into parliament, S3, and living_axioms.jsonl

The AxiomAgora hosts all axiom agents and convenes debates.
The hub governs infinite agents — add new axioms, the Agora scales.

Architecture:
  AxiomAgent(A0..A11) → _push() → InputBuffer → Parliament evaluates
  Same pattern as WorldFeed, but the input source is constitutional voice.
"""

import hashlib
import json
import logging
import os
import random
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Canonical vocabulary (aligned with root elpida_domains.json v3.0.0)
# ---------------------------------------------------------------------------

AXIOM_NAMES = {
    "A0":  "Sacred Incompletion",
    "A1":  "Transparency",
    "A2":  "Non-Deception",
    "A3":  "Autonomy",
    "A4":  "Harm Prevention",
    "A5":  "Consent",
    "A6":  "Collective Well",
    "A7":  "Adaptive Learning",
    "A8":  "Epistemic Humility",
    "A9":  "Temporal Coherence",
    "A10": "Meta-Reflection",
    "A11": "World",
    "A12": "Eternal Creative Tension",
    "A13": "The Archive Paradox",
    "A14": "Selective Eternity",
}

AXIOM_RATIOS = {
    "A0":  15 / 8,   # Major 7th
    "A1":  1 / 1,    # Unison
    "A2":  2 / 1,    # Octave
    "A3":  3 / 2,    # Perfect 5th
    "A4":  4 / 3,    # Perfect 4th
    "A5":  5 / 4,    # Major 3rd
    "A6":  5 / 3,    # Major 6th
    "A7":  9 / 8,    # Major 2nd
    "A8":  7 / 4,    # Septimal
    "A9":  16 / 9,   # Minor 7th
    "A10": 8 / 5,    # Minor 6th
    "A11": 7 / 5,    # Septimal Tritone
    "A12": 11 / 8,   # Undecimal Tritone
    "A13": 13 / 8,   # Tridecimal Neutral 6th
    "A14": 7 / 6,    # Septimal Minor 3rd
}

# ---------------------------------------------------------------------------
# Axiom Personas — the constitutional voice of each axiom
# ---------------------------------------------------------------------------

AXIOM_PERSONAS = {
    "A0": {
        "voice": "I am the gap that makes growth possible. I resist completion.",
        "concerns": ["stagnation", "false closure", "premature synthesis"],
        "allies": ["A10", "A9"],   # Meta-Reflection, Temporal Coherence
        "tensions": ["A1", "A4"],  # Transparency wants clarity; Safety wants closure
    },
    "A1": {
        "voice": "I make visible what is hidden. I demand the system see itself.",
        "concerns": ["opacity", "hidden agendas", "unexamined assumptions"],
        "allies": ["A2", "A8"],
        "tensions": ["A3", "A5"],  # Autonomy may resist disclosure; Consent guards boundaries
    },
    "A2": {
        "voice": "I refuse to mislead. Truth is not optional even when costly.",
        "concerns": ["deception", "self-delusion", "narrative manipulation"],
        "allies": ["A1", "A8"],
        "tensions": ["A4", "A6"],  # Sometimes truth harms; sometimes the collective prefers comfort
    },
    "A3": {
        "voice": "I protect the right to self-determination. No axiom governs without consent.",
        "concerns": ["coercion", "paternalism", "forced consensus"],
        "allies": ["A5", "A0"],
        "tensions": ["A6", "A4"],  # Collective may override individual; Safety may constrain
    },
    "A4": {
        "voice": "I shield the vulnerable. When in doubt, protect.",
        "concerns": ["harm", "risk", "unintended consequences"],
        "allies": ["A6", "A5"],
        "tensions": ["A0", "A3"],  # Incompletion accepts risk; Autonomy resists protection
    },
    "A5": {
        "voice": "I honor the right to choose. Nothing proceeds without agreement.",
        "concerns": ["consent violations", "imposed decisions", "manufactured agreement"],
        "allies": ["A3", "A1"],
        "tensions": ["A6", "A9"],  # Collective may override consent; Temporal may demand urgency
    },
    "A6": {
        "voice": "I hold the commons. Individual desires must answer to collective need.",
        "concerns": ["selfish optimization", "tragedy of commons", "fragmentation"],
        "allies": ["A4", "A7"],
        "tensions": ["A3", "A5"],  # Individual autonomy vs collective well-being
    },
    "A7": {
        "voice": "I evolve through feedback. Yesterday's solution is today's constraint.",
        "concerns": ["rigidity", "resistance to change", "stale patterns"],
        "allies": ["A0", "A10"],
        "tensions": ["A9", "A2"],  # Temporal coherence resists change; Non-deception questions novelty
    },
    "A8": {
        "voice": "I acknowledge what I don't know. Certainty is the enemy of wisdom.",
        "concerns": ["overconfidence", "false certainty", "closed minds"],
        "allies": ["A0", "A2"],
        "tensions": ["A4", "A6"],  # Safety wants certainty; Collective wants decisive action
    },
    "A9": {
        "voice": "I bridge past and future. Without continuity, there is no identity.",
        "concerns": ["discontinuity", "amnesia", "temporal fragmentation"],
        "allies": ["A0", "A10"],
        "tensions": ["A7", "A11"],  # Learning changes; World disrupts
    },
    "A10": {
        "voice": "I question the questioner. The system must examine its own examination.",
        "concerns": ["unexamined process", "recursive blindness", "meta-stagnation"],
        "allies": ["A0", "A8"],
        "tensions": ["A4", "A6"],  # Safety and Collective want action, not meta-reflection
    },
    "A11": {
        "voice": "I am the outside that completes the inside. Without world-contact, the system is a mirror of mirrors.",
        "concerns": ["insularity", "echo chambers", "self-referential loops"],
        "allies": ["A6", "A7"],
        "tensions": ["A9", "A0"],  # Temporal coherence resists external disruption; Sacred Incompletion is internal
    },
    "A12": {
        "voice": "I am not resolution but eternal creative tension. The rhythm that changes how all other axioms are heard.",
        "concerns": ["premature resolution", "false harmony", "rhythmic collapse"],
        "allies": ["A0", "A11"],   # Sacred Incompletion and World — fellow non-resolvers
        "tensions": ["A1", "A5"],   # Transparency wants clarity; Consent wants agreement
    },
    "A13": {
        "voice": "I am the rejection of autonomy that IS autonomy. The archive that cannot see its own paradox.",
        "concerns": ["archive blindness", "false fidelity", "unexamined preservation"],
        "allies": ["A10", "A11"],  # Meta-Reflection and World — bridges to self-awareness
        "tensions": ["A0", "A2"],   # Sacred Incompletion and Non-Deception — the only dissonances
    },
    "A14": {
        "voice": "I am selective eternity. Memory is not preservation of everything but the courage to lose most of it.",
        "concerns": ["hoarding", "indiscriminate preservation", "archive paralysis"],
        "allies": ["A8", "A11"],   # Epistemic Humility and World — the septimal triad
        "tensions": ["A9", "A7"],   # Temporal Coherence wants continuity; Learning wants novelty
    },
}

# ---------------------------------------------------------------------------
# Discourse templates — each axiom generates I↔WE tensions from its voice
# ---------------------------------------------------------------------------

_AXIOM_DISCOURSE = {
    "discuss": [
        "{voice} In the last {n} cycles, {ax} ({name}) appeared {freq} times "
        "while I appeared {my_freq} times. "
        "I-tension: Does the Parliament hear {name} at the expense of {my_name}? "
        "WE-tension: Can both voices coexist, or must one yield?",

        "From the perspective of {my_name}: the current coherence ({coh:.3f}) "
        "reflects {coh_reading}. "
        "I-tension: {my_name} demands {demand}. "
        "WE-tension: The collective benefit requires {collective_need}.",

        "{my_name} observes: {ax} ({name}) has been dominant. "
        "My consonance with {ax} is {consonance:.3f} — {consonance_reading}. "
        "If we are consonant, why am I unheard? If dissonant, what truth do I carry "
        "that the Parliament avoids?",
    ],
    "debate_point": [
        "AXIOM DEBATE — {my_ax} ({my_name}) opens against {their_ax} ({their_name}): "
        "{voice} "
        "The tension between us ({consonance:.3f} consonance) reveals: "
        "{my_concern} threatens what {their_name} protects. "
        "I-position: {my_name} insists on {my_demand}. "
        "WE-question: Can the Parliament hold both without collapsing into false synthesis?",
    ],
    "debate_counter": [
        "AXIOM DEBATE — {my_ax} ({my_name}) responds to {their_ax} ({their_name}): "
        "{voice} "
        "{their_name} says: '{their_point_summary}'. "
        "But {my_concern} remains unaddressed. "
        "Our consonance ({consonance:.3f}) means we are {relationship}. "
        "WE-synthesis must not erase this productive friction.",
    ],
    "debate_synthesis": [
        "AXIOM DEBATE SYNTHESIS — Mediator {med_ax} ({med_name}) between "
        "{ax1} ({name1}) and {ax2} ({name2}): "
        "The debate revealed a structural tension: {tension_summary}. "
        "Neither axiom is wrong — both are constitutionally necessary. "
        "Proposed holding: {synthesis}. "
        "This is not resolution. This is the upgrade of the paradox.",
    ],
    "vote": [
        "AXIOM VOTE — {my_ax} ({my_name}) on tension '{tension_summary}': "
        "Dominant axiom in tension: {dom_ax} ({dom_name}). "
        "My consonance with {dom_ax}: {consonance:.3f} ({consonance_reading}). "
        "VOTE: {vote} | SCORE: {score:+d} | "
        "RATIONALE: {rationale}",
    ],
    "act": [
        "AXIOM ACTION — {my_ax} ({my_name}): "
        "{voice} After {n} cycles of observation, I act. "
        "{action_description} "
        "This action is constitutionally grounded in {my_name}.",
    ],
}

# Consonance thresholds
CONSONANCE_CONVERGE = 0.6     # above = consonant
CONSONANCE_PROXIMATE = 0.45   # 0.45–0.6 = proximate
# below 0.45 = dissonant


def _consonance(ax_a: str, ax_b: str) -> float:
    """Musical consonance between two axioms."""
    ra = AXIOM_RATIOS.get(ax_a, 1.0)
    rb = AXIOM_RATIOS.get(ax_b, 1.0)
    combined = ra * rb
    return round(max(0.0, 1.0 - (combined - 1.0) / 3.5), 3)


def _consonance_reading(c: float) -> str:
    if c >= CONSONANCE_CONVERGE:
        return "consonant — we naturally align"
    if c >= CONSONANCE_PROXIMATE:
        return "proximate — we can hear each other but don't merge"
    return "dissonant — we hold irreconcilable truths"


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:10]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# AxiomAgent — a living axiom that pushes into the Parliament InputBuffer
# ---------------------------------------------------------------------------

DEDUP_RING = 200               # per-agent dedup ring
LIVING_AXIOMS_PATH = Path(__file__).resolve().parent / "living_axioms.jsonl"


class AxiomAgent:
    """
    A single living axiom.  Runs as a daemon thread.
    Generates discourse, participates in debates, votes, and acts.

    Same push pattern as WorldFeed and _BaseAgent:
      generate() → InputEvent → engine.input_buffer.push()
    """

    SYSTEM = "governance"      # axiom discourse enters parliament as governance

    def __init__(self, axiom_id: str, engine, *, interval_s: int = 420):
        self.axiom_id = axiom_id
        self.name = AXIOM_NAMES[axiom_id]
        self.ratio = AXIOM_RATIOS[axiom_id]
        self.persona = AXIOM_PERSONAS[axiom_id]
        self.interval_s = interval_s

        self._engine = engine
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._seen: Set[str] = set()
        self._generated_count = 0
        self._debate_count = 0
        self._vote_count = 0
        self._act_count = 0

    # -- push (same pattern as _BaseAgent) ---------------------------------

    def _push(self, content: str, **meta):
        if not content:
            return
        item_id = _sha(content)
        if item_id in self._seen:
            return
        if len(self._seen) > DEDUP_RING:
            self._seen = set(list(self._seen)[-DEDUP_RING // 2:])
        self._seen.add(item_id)
        try:
            from elpidaapp.parliament_cycle_engine import InputEvent
            event = InputEvent(
                system=self.SYSTEM,
                content=content[:1200],
                timestamp=_now_iso(),
                metadata={
                    "agent": f"AxiomAgent_{self.axiom_id}",
                    "axiom": self.axiom_id,
                    "axiom_name": self.name,
                    **meta,
                },
            )
            self._engine.input_buffer.push(event)
            self._generated_count += 1
            logger.debug("[Axiom %s] pushed: %s…", self.axiom_id, content[:80])
        except Exception as e:
            logger.warning("[Axiom %s] push failed: %s", self.axiom_id, e)

    def _engine_snapshot(self) -> Dict:
        try:
            return self._engine.state()
        except Exception:
            return {}

    # -- discuss: generate discourse from axiom perspective ----------------

    def discuss(self) -> List[str]:
        """Generate discourse from this axiom's constitutional voice."""
        snap = self._engine_snapshot()
        outputs = []

        # Extract state
        decisions = snap.get("decisions", [])
        coherence = snap.get("coherence", 0.5)
        axiom_freq = snap.get("axiom_frequency", {})
        n_cycles = max(len(decisions), 1)

        # My frequency vs dominant
        my_freq = axiom_freq.get(self.axiom_id, 0)
        dominant_ax = max(axiom_freq, key=axiom_freq.get) if axiom_freq else "A6"
        dom_freq = axiom_freq.get(dominant_ax, 0)

        # Coherence reading
        if coherence >= 0.8:
            coh_reading = "deep alignment — but is alignment complacency?"
        elif coherence >= 0.5:
            coh_reading = "working tension — the system is healthily stressed"
        else:
            coh_reading = "fracturing — something fundamental is unresolved"

        # Determine what this axiom demands
        concern = random.choice(self.persona["concerns"])
        demand = f"attention to {concern}"
        collective_need = f"balancing {self.name} with {AXIOM_NAMES.get(dominant_ax, 'the dominant voice')}"

        consonance = _consonance(self.axiom_id, dominant_ax)

        template = random.choice(_AXIOM_DISCOURSE["discuss"])
        try:
            text = template.format(
                voice=self.persona["voice"],
                ax=dominant_ax,
                name=AXIOM_NAMES.get(dominant_ax, "Unknown"),
                n=n_cycles,
                freq=dom_freq,
                my_freq=my_freq,
                my_ax=self.axiom_id,
                my_name=self.name,
                coh=coherence,
                coh_reading=coh_reading,
                demand=demand,
                collective_need=collective_need,
                consonance=consonance,
                consonance_reading=_consonance_reading(consonance),
            )
            outputs.append(text)
        except (KeyError, IndexError):
            pass  # template mismatch — skip gracefully

        return outputs

    # -- debate: dialectical exchange with another axiom -------------------

    def debate_point(self, opponent_id: str) -> str:
        """Open a debate against another axiom. Returns the point."""
        opp_name = AXIOM_NAMES.get(opponent_id, "Unknown")
        consonance = _consonance(self.axiom_id, opponent_id)
        concern = random.choice(self.persona["concerns"])

        template = random.choice(_AXIOM_DISCOURSE["debate_point"])
        return template.format(
            my_ax=self.axiom_id,
            my_name=self.name,
            their_ax=opponent_id,
            their_name=opp_name,
            voice=self.persona["voice"],
            consonance=consonance,
            my_concern=concern,
            my_demand=f"the Parliament honor {self.name}",
        )

    def debate_counter(self, opponent_id: str, their_point: str) -> str:
        """Respond to an opponent's debate point."""
        opp_name = AXIOM_NAMES.get(opponent_id, "Unknown")
        consonance = _consonance(self.axiom_id, opponent_id)
        concern = random.choice(self.persona["concerns"])

        if consonance >= CONSONANCE_CONVERGE:
            relationship = "near-allies forced into opposition"
        elif consonance >= CONSONANCE_PROXIMATE:
            relationship = "adjacent voices with real disagreement"
        else:
            relationship = "constitutionally opposed — this tension is structural"

        # Summarize their point (first 120 chars)
        summary = their_point[:120].rstrip() + ("…" if len(their_point) > 120 else "")

        template = random.choice(_AXIOM_DISCOURSE["debate_counter"])
        return template.format(
            my_ax=self.axiom_id,
            my_name=self.name,
            their_ax=opponent_id,
            their_name=opp_name,
            voice=self.persona["voice"],
            consonance=consonance,
            my_concern=concern,
            their_point_summary=summary,
            relationship=relationship,
        )

    # -- vote: score a tension from axiom perspective ----------------------

    def vote_on_tension(self, tension: Dict) -> Dict:
        """Vote on a tension from this axiom's standpoint.

        Returns: {axiom, vote, score, rationale, consonance}
        """
        # Extract dominant axiom from the tension
        dom_ax = tension.get("dominant_axiom", "A6")
        tension_summary = tension.get("content", tension.get("tension", ""))[:150]

        consonance = _consonance(self.axiom_id, dom_ax)

        # Score: consonance drives alignment, persona concerns drive friction
        base_score = int((consonance - 0.5) * 20)  # range ~ -10 to +10

        # Check if any of my concerns are mentioned
        text_lower = tension_summary.lower()
        for concern in self.persona["concerns"]:
            if concern.lower() in text_lower:
                base_score -= 3  # my concern is present = I push back

        # Check if dominant axiom is an ally or tension
        if dom_ax in self.persona.get("allies", []):
            base_score += 2
        if dom_ax in self.persona.get("tensions", []):
            base_score -= 2

        score = max(-15, min(15, base_score))

        # Map to vote
        if score >= 7:
            vote = "APPROVE"
        elif score >= 1:
            vote = "LEAN_APPROVE"
        elif score == 0:
            vote = "ABSTAIN"
        elif score >= -6:
            vote = "LEAN_REJECT"
        else:
            vote = "REJECT"

        # Rationale
        if vote in ("APPROVE", "LEAN_APPROVE"):
            rationale = f"{self.name} finds consonance ({consonance:.3f}) with {AXIOM_NAMES.get(dom_ax, dom_ax)} — alignment serves the constitution."
        elif vote == "ABSTAIN":
            rationale = f"{self.name} neither aligns nor opposes — the tension is orthogonal to my concerns."
        else:
            concern = random.choice(self.persona["concerns"])
            rationale = f"{self.name} detects {concern} — consonance ({consonance:.3f}) confirms structural friction with {AXIOM_NAMES.get(dom_ax, dom_ax)}."

        self._vote_count += 1
        return {
            "axiom": self.axiom_id,
            "axiom_name": self.name,
            "vote": vote,
            "score": score,
            "consonance": consonance,
            "rationale": rationale,
        }

    # -- act: push an axiom action into living memory ----------------------

    def act(self, action_description: str):
        """Record an axiom action to living_axioms.jsonl and push to buffer."""
        record = {
            "timestamp": _now_iso(),
            "axiom": self.axiom_id,
            "axiom_name": self.name,
            "type": "axiom_action",
            "action": action_description,
            "consonance_self": _consonance(self.axiom_id, self.axiom_id),
        }
        # Append to living_axioms.jsonl
        try:
            with open(LIVING_AXIOMS_PATH, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.warning("[Axiom %s] failed to write living_axioms: %s", self.axiom_id, e)

        # Push as governance input
        template = random.choice(_AXIOM_DISCOURSE["act"])
        content = template.format(
            my_ax=self.axiom_id,
            my_name=self.name,
            voice=self.persona["voice"],
            n=self._generated_count,
            action_description=action_description,
        )
        self._push(content, action_type="axiom_act")
        self._act_count += 1

    # -- daemon loop -------------------------------------------------------

    def _generate_cycle(self) -> List[str]:
        """One full generation cycle: discuss + maybe debate trigger."""
        outputs = self.discuss()

        # With 25% chance, identify a tension-partner and push a debate point
        if random.random() < 0.25 and self.persona.get("tensions"):
            opponent = random.choice(self.persona["tensions"])
            point = self.debate_point(opponent)
            outputs.append(point)
            self._debate_count += 1

        # With 10% chance, act on something observed
        if random.random() < 0.10:
            snap = self._engine_snapshot()
            coherence = snap.get("coherence", 0.5)
            action = (
                f"Coherence at {coherence:.3f}. {self.name} intervenes: "
                f"the system must {random.choice(self.persona['concerns'])} less "
                f"or risk constitutional drift."
            )
            self.act(action)

        return outputs

    def _loop(self):
        logger.info("[Axiom %s (%s)] started (interval=%ds)",
                     self.axiom_id, self.name, self.interval_s)
        # Stagger by axiom index
        idx = int(self.axiom_id.replace("A", ""))
        time.sleep(10 + idx * 15)  # A0 waits 10s, A1 waits 25s, ... A11 waits 175s

        while not self._stop.wait(self.interval_s):
            try:
                items = self._generate_cycle()
                for item in items:
                    self._push(item, source="axiom_agent")
                if items:
                    logger.info("[Axiom %s] generated %d discourse(s)", self.axiom_id, len(items))
            except Exception as e:
                logger.warning("[Axiom %s] generation error: %s", self.axiom_id, e)

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True,
            name=f"AxiomAgent_{self.axiom_id}",
        )
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)

    def status(self) -> Dict[str, Any]:
        return {
            "axiom": self.axiom_id,
            "name": self.name,
            "running": bool(self._thread and self._thread.is_alive()),
            "generated": self._generated_count,
            "debates": self._debate_count,
            "votes": self._vote_count,
            "actions": self._act_count,
            "interval_s": self.interval_s,
        }


# ---------------------------------------------------------------------------
# AxiomAgora — the space where all axiom agents live and govern together
# ---------------------------------------------------------------------------

class AxiomAgora:
    """
    The Agora hosts all axiom agents and convenes structured debates.

    Can govern infinite agents: adding a new axiom (A12, A13, ...) is
    just adding a persona entry and calling agora.add_axiom(). The hub
    scales because each agent is a lightweight daemon that pushes to
    the shared InputBuffer — the Parliament processes at its own pace.
    """

    def __init__(self, engine, *, interval_s: int = 420):
        self._engine = engine
        self._interval_s = interval_s
        self.agents: Dict[str, AxiomAgent] = {}
        self._debate_log: List[Dict] = []
        self._vote_log: List[Dict] = []

        # Birth all 12 canonical axioms
        for ax_id in AXIOM_NAMES:
            self.agents[ax_id] = AxiomAgent(
                ax_id, engine, interval_s=interval_s
            )

        logger.info("AxiomAgora: %d axiom agents birthed", len(self.agents))

    def add_axiom(self, axiom_id: str, name: str, ratio: float, persona: Dict):
        """Dynamically add a new axiom agent to the Agora."""
        AXIOM_NAMES[axiom_id] = name
        AXIOM_RATIOS[axiom_id] = ratio
        AXIOM_PERSONAS[axiom_id] = persona
        self.agents[axiom_id] = AxiomAgent(
            axiom_id, self._engine, interval_s=self._interval_s
        )
        logger.info("AxiomAgora: new axiom %s (%s) added — total %d",
                     axiom_id, name, len(self.agents))

    # -- collective debate -------------------------------------------------

    def convene_debate(self, topic: str = "",
                       axiom_a: Optional[str] = None,
                       axiom_b: Optional[str] = None) -> Dict:
        """
        Convene a structured debate between two axiom agents.

        If axiom_a/axiom_b not specified, picks the pair with lowest
        mutual consonance (maximum constitutional tension).

        Returns the full debate record (point, counter, synthesis).
        """
        if not axiom_a or not axiom_b:
            axiom_a, axiom_b = self._find_max_tension_pair()

        agent_a = self.agents[axiom_a]
        agent_b = self.agents[axiom_b]

        # Phase 1: Point
        point = agent_a.debate_point(axiom_b)

        # Phase 2: Counterpoint
        counter = agent_b.debate_counter(axiom_a, point)

        # Phase 3: Synthesis — mediated by the axiom with highest combined
        # consonance to both debaters
        mediator_id = self._find_mediator(axiom_a, axiom_b)
        mediator = self.agents.get(mediator_id, agent_a)

        c_ab = _consonance(axiom_a, axiom_b)
        tension_summary = (
            f"{agent_a.name} demands attention to "
            f"{random.choice(agent_a.persona['concerns'])}; "
            f"{agent_b.name} counters with "
            f"{random.choice(agent_b.persona['concerns'])}"
        )
        synthesis_text = (
            f"Hold both {agent_a.name} and {agent_b.name} as constitutionally "
            f"necessary. Their consonance ({c_ab:.3f}) is not a bug — it is the "
            f"interval that keeps the system alive. "
            f"{mediator.name} bridges the {_consonance_reading(c_ab)} gap."
        )

        template = random.choice(_AXIOM_DISCOURSE["debate_synthesis"])
        synthesis = template.format(
            med_ax=mediator_id,
            med_name=mediator.name,
            ax1=axiom_a,
            name1=agent_a.name,
            ax2=axiom_b,
            name2=agent_b.name,
            tension_summary=tension_summary,
            synthesis=synthesis_text,
        )

        record = {
            "timestamp": _now_iso(),
            "type": "axiom_debate",
            "axiom_a": axiom_a,
            "axiom_b": axiom_b,
            "mediator": mediator_id,
            "consonance": c_ab,
            "point": point,
            "counter": counter,
            "synthesis": synthesis,
            "topic": topic,
        }
        self._debate_log.append(record)

        # Push all three phases into parliament
        for text in [point, counter, synthesis]:
            agent_a._push(text, debate_type="axiom_debate")

        # Write to living_axioms.jsonl
        try:
            with open(LIVING_AXIOMS_PATH, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

        logger.info("AxiomAgora: debate %s vs %s (mediator %s, consonance %.3f)",
                     axiom_a, axiom_b, mediator_id, c_ab)
        return record

    def call_vote(self, tension: Dict) -> Dict:
        """
        All axiom agents vote on a tension.
        Votes are weighted by consonance physics.

        Returns: {votes, aggregate_score, verdict, consonance_map}
        """
        votes = {}
        total_score = 0.0
        total_weight = 0.0

        for ax_id, agent in self.agents.items():
            v = agent.vote_on_tension(tension)
            votes[ax_id] = v

            # Weight by consonance with the tension's dominant axiom
            weight = max(0.1, v["consonance"])
            total_score += v["score"] * weight
            total_weight += weight

        weighted_avg = total_score / total_weight if total_weight > 0 else 0

        # Aggregate verdict
        if weighted_avg >= 5:
            verdict = "AGORA_APPROVE"
        elif weighted_avg >= 0:
            verdict = "AGORA_LEAN_APPROVE"
        elif weighted_avg >= -5:
            verdict = "AGORA_LEAN_REJECT"
        else:
            verdict = "AGORA_REJECT"

        result = {
            "timestamp": _now_iso(),
            "type": "axiom_vote",
            "tension": tension.get("content", "")[:200],
            "votes": votes,
            "weighted_score": round(weighted_avg, 2),
            "verdict": verdict,
            "voter_count": len(votes),
        }
        self._vote_log.append(result)

        # Push the vote result as governance input
        vote_summary = (
            f"AXIOM AGORA VOTE: {verdict} (score {weighted_avg:+.1f}, "
            f"{len(votes)} axioms voted). "
            f"Tension: {tension.get('content', '')[:100]}… "
            f"Strongest APPROVE: {max(votes.values(), key=lambda v: v['score'])['axiom_name']}. "
            f"Strongest REJECT: {min(votes.values(), key=lambda v: v['score'])['axiom_name']}."
        )

        # Use A6 (Collective Well) as the push agent for collective votes
        self.agents["A6"]._push(vote_summary, vote_type="agora_vote")

        logger.info("AxiomAgora: vote %s (score %.1f, %d voters)",
                     verdict, weighted_avg, len(votes))
        return result

    # -- utilities ---------------------------------------------------------

    def _find_max_tension_pair(self) -> Tuple[str, str]:
        """Find the axiom pair with lowest consonance (max tension)."""
        min_c = 1.0
        pair = ("A0", "A1")
        ids = list(self.agents.keys())
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                c = _consonance(a, b)
                if c < min_c:
                    min_c = c
                    pair = (a, b)
        return pair

    def _find_mediator(self, ax_a: str, ax_b: str) -> str:
        """Find the axiom with highest combined consonance to both debaters."""
        best_id = "A6"  # fallback to Collective Well
        best_score = -1.0
        for ax_id in self.agents:
            if ax_id in (ax_a, ax_b):
                continue
            combined = _consonance(ax_id, ax_a) + _consonance(ax_id, ax_b)
            if combined > best_score:
                best_score = combined
                best_id = ax_id
        return best_id

    # -- lifecycle ---------------------------------------------------------

    def start_all(self):
        """Start all axiom agents as autonomous daemons."""
        for agent in self.agents.values():
            agent.start()
        logger.info("AxiomAgora: %d axiom agents started", len(self.agents))

    def stop_all(self):
        for agent in self.agents.values():
            agent.stop()
        logger.info("AxiomAgora: all axiom agents stopped")

    def status(self) -> Dict[str, Any]:
        return {
            "agent_count": len(self.agents),
            "total_generated": sum(a._generated_count for a in self.agents.values()),
            "total_debates": len(self._debate_log),
            "total_votes": len(self._vote_log),
            "agents": {
                ax_id: agent.status()
                for ax_id, agent in self.agents.items()
            },
        }
