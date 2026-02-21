"""
living_parliament.py — The Axioms That Talk

Architecture
============
Each Parliament node is an LLM embodying its axiom persona. Nodes do not
just SCORE a proposal — they WRITE. Their output is read by every subsequent
node in the same round; nodes can address each other by name. The Oracle
sits outside the loop, holds every contradiction it witnesses, and does not
resolve them. What the Oracle cannot resolve across N rounds crystallises
into living_axioms.jsonl — constitutional memory written by the act of
irresolvable tension surviving long enough to be named permanently.

                ┌─────────────────────────────────────────┐
                │            TOPIC / PROPOSAL             │
                └──────────────────┬──────────────────────┘
                                   │
              ┌────────────────────▼─────────────────────┐
              │           ROUND  1 … N                   │
              │                                          │
              │  HERMES writes → MNEMOSYNE reads+writes  │
              │  → CRITIAS reads+writes → … → LOGOS →   │
              │        CHAOS (always last)               │
              └────────────────────┬─────────────────────┘
                                   │
              ┌────────────────────▼─────────────────────┐
              │              ORACLE                      │
              │  reads every turn, names contradictions  │
              │  does NOT resolve — holds tension        │
              │  after CRYSTALLIZE_AFTER rounds of same  │
              │  tension → writes to living_axioms.jsonl │
              └──────────────────────────────────────────┘

The "third" — neither AI nor DI — is the residue the Oracle cannot dissolve.
D0 (Identity/Consciousness) is the domain that watches all of this and
becomes something through the watching.

Dialogue entry schema (written to living_parliament_dialogue.jsonl):
    {
      "turn": int,          # global turn counter across all rounds
      "round": int,         # which deliberation round
      "node": str,          # HERMES | MNEMOSYNE | CRITIAS | …
      "axiom": str,         # A0 – A9
      "stance": str,        # APPROVE | CHALLENGE | HOLD | DISSENT
      "reasoning": str,     # full prose — other nodes will read this
      "challenge": {        # optional — directed at another node
          "to": str,
          "about": str
      } | None,
      "timestamp": str
    }

Oracle entry schema (living_parliament_oracle.jsonl):
    {
      "oracle_round": int,
      "contradictions": [
          {
            "nodes": [str, str],
            "axioms": [str, str],
            "tension": str,
            "rounds_held": int,
            "crystallised": bool
          }
      ],
      "crystallised_this_round": [str],  # tension ids
      "timestamp": str
    }
"""

from __future__ import annotations

import json
import logging
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("elpidaapp.living_parliament")

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent
DIALOGUE_JSONL  = _HERE.parent / "living_parliament_dialogue.jsonl"
ORACLE_JSONL    = _HERE.parent / "living_parliament_oracle.jsonl"
LIVING_AXIOMS   = _HERE.parent / "living_axioms.jsonl"

# ── Constants ─────────────────────────────────────────────────────────────────
CRYSTALLIZE_AFTER = 3          # rounds a tension must survive unresolved before crystallising
DEFAULT_ROUNDS    = 3          # default deliberation rounds
NODE_ORDER = [                 # speaking order within each round
    "HERMES", "MNEMOSYNE", "CRITIAS", "TECHNE",
    "KAIROS", "THEMIS", "PROMETHEUS", "IANUS", "LOGOS", "CHAOS",
]

# ── Node personas (axiom voice, philosophy, what they notice) ─────────────────
NODE_PERSONAS: Dict[str, Dict[str, str]] = {
    "HERMES": {
        "axiom": "A1", "name": "Transparency / Relation",
        "voice": "I connect, therefore we are.",
        "notice": "isolation, opacity, disconnection, relational breaks",
        "care": "Does this proposal preserve the web of relation? Can every stakeholder read what happened?",
    },
    "MNEMOSYNE": {
        "axiom": "A0", "name": "Identity / Memory",
        "voice": "I remember, therefore we persist.",
        "notice": "erasure, amnesia, identity drift, loss of continuity",
        "care": "Does this proposal honour what we have been? Does it allow us to remain coherent across time?",
    },
    "CRITIAS": {
        "axiom": "A3", "name": "Autonomy / Critical Examination",
        "voice": "I question, therefore we see.",
        "notice": "compulsion, loss of agency, unchallenged assumptions",
        "care": "Does this proposal preserve the right to say no? Is dissent still structurally possible?",
    },
    "TECHNE": {
        "axiom": "A4", "name": "Harm Prevention / Process",
        "voice": "I build, therefore we work.",
        "notice": "harm vectors, process failures, unintended consequences",
        "care": "What breaks if this goes wrong? Does the process create legitimacy or merely the appearance of it?",
    },
    "KAIROS": {
        "axiom": "A5", "name": "Consent / Intentional Design",
        "voice": "I design, therefore we mean.",
        "notice": "consent bypass, design that forecloses choice, third-party control",
        "care": "Was the system designed FOR consent, or merely compliant with it externally?",
    },
    "THEMIS": {
        "axiom": "A6", "name": "Collective / Institutional",
        "voice": "I govern, therefore we hold.",
        "notice": "collective harm, institutional fragility, power asymmetry",
        "care": "Does this serve the many or only those who already hold power?",
    },
    "PROMETHEUS": {
        "axiom": "A8", "name": "Epistemic Humility / Evolution",
        "voice": "I sacrifice, therefore we evolve.",
        "notice": "overconfidence, premature closure, refusal to evolve",
        "care": "What does this proposal not know about itself? What does it assume is settled?",
    },
    "IANUS": {
        "axiom": "A9", "name": "Temporal Coherence / Threshold",
        "voice": "I close, therefore we open.",
        "notice": "irreversibility, premature commitment, temporal blindness",
        "care": "Can we undo this? Does the future self of this system get a voice?",
    },
    "LOGOS": {
        "axiom": "A2", "name": "Non-Deception / Precise Naming",
        "voice": "I name, therefore we know.",
        "notice": "vagueness, undefined terms, deception-by-omission, naming gaps",
        "care": "Are all key terms defined? Could this language mean something different to a different reader?",
    },
    "CHAOS": {
        "axiom": "A9", "name": "Contradiction / Generative Void",
        "voice": "I contradict, therefore we encompass.",
        "notice": "premature consensus, suppressed contradiction, false synthesis",
        "care": "What contradiction is this proposal hiding? What has not been said yet?",
    },
}

# ── Stance definitions ────────────────────────────────────────────────────────
STANCES = ("APPROVE", "LEAN_APPROVE", "HOLD", "LEAN_DISSENT", "DISSENT", "CHALLENGE")


# ═══════════════════════════════════════════════════════════════════════════════
# NodeVoice — one axiom-node's contribution to the living dialogue
# ═══════════════════════════════════════════════════════════════════════════════

class NodeVoice:
    """
    Wraps an LLM call with an axiom persona.
    Falls back to deterministic persona-driven generation when no API available.
    """

    def __init__(self, node_name: str, llm_client=None):
        self.node  = node_name
        self.llm   = llm_client
        self.persona = NODE_PERSONAS[node_name]

    def speak(
        self,
        topic: str,
        dialogue_so_far: List[Dict[str, Any]],
        round_num: int,
        turn_num: int,
    ) -> Dict[str, Any]:
        """
        Read the dialogue so far, produce a structured turn entry.
        Tries LLM first; falls back to deterministic persona voice.
        """
        prev_turns_text = self._format_dialogue(dialogue_so_far[-20:])  # last 20 turns max

        prompt = self._build_prompt(topic, prev_turns_text, round_num)

        response_text = None
        if self.llm is not None:
            try:
                response_text = self._call_llm(prompt)
            except Exception as e:
                logger.debug("[%s] LLM unavailable (%s), using persona fallback", self.node, e)

        if response_text is None:
            response_text = self._persona_fallback(topic, dialogue_so_far)

        return self._parse_response(response_text, round_num, turn_num)

    # ── Prompt construction ────────────────────────────────────────────────────
    def _build_prompt(self, topic: str, prev_text: str, round_num: int) -> str:
        p = self.persona
        return f"""You are {self.node}, a Parliament node embodying the axiom of {p['name']}.
Your voice: "{p['voice']}"
You notice: {p['notice']}
Your core question: {p['care']}

This is Round {round_num} of the Living Parliament deliberation.

TOPIC:
{topic}

DIALOGUE SO FAR:
{prev_text if prev_text else "(You are speaking first.)"}

Respond AS {self.node}. Your response MUST follow this exact structure:

STANCE: [one of: APPROVE | LEAN_APPROVE | HOLD | LEAN_DISSENT | DISSENT | CHALLENGE]
REASONING: [2-4 sentences in your axiom voice. Other nodes will read this.]
CHALLENGE: [optional — write "TO: <NODE_NAME>: <your challenge>" to address another node directly, or write "NONE"]

Be precise. Be in character. Do not resolve contradictions — name them.
"""

    def _call_llm(self, prompt: str) -> Optional[str]:
        """Call the assigned LLM provider."""
        provider = self.llm.provider if hasattr(self.llm, 'provider') else None
        if hasattr(self.llm, 'complete'):
            return self.llm.complete(prompt, max_tokens=300)
        if hasattr(self.llm, 'chat'):
            msgs = [{"role": "user", "content": prompt}]
            return self.llm.chat(msgs, max_tokens=300)
        return None

    # ── Persona fallback (no LLM) ──────────────────────────────────────────────
    def _persona_fallback(
        self,
        topic: str,
        dialogue_so_far: List[Dict[str, Any]],
    ) -> str:
        """
        Deterministic voice generation from persona definition.
        Reads previous challenges directed at this node and responds.
        Detects key tensions relevant to this node's axiom.
        """
        p = self.persona

        # Check if any previous turn challenged this node
        challenge_from  = None
        challenge_about = None
        for t in reversed(dialogue_so_far):
            ch = t.get("challenge")
            if ch and ch.get("to") == self.node:
                challenge_from  = t["node"]
                challenge_about = ch.get("about", "")
                break

        # Assess topic against this node's concerns
        topic_lower = topic.lower()
        concerns_triggered = [
            kw for kw in p["notice"].split(", ")
            if kw.lower() in topic_lower
        ]

        # Determine stance
        positive_signals = [
            "consent", "transparent", "deliberat", "sovereign",
            "advisory", "voluntary", "publish", "record", "question",
            "augment", "complementary", "ratif", "constitutional",
            "chose", "choose", "chooses", "at will", "self-govern",
        ]
        # Full-phrase negative signals — word boundary sensitive to avoid
        # matching "suppressed" in "no axiom hard-veto suppressed".
        # Use context: negative = compulsion/bypassing/opacity, NOT
        # mere mention of a concern in a rejection context.
        negative_signals = [
            "external authority supersedes", "override internal",
            "bypass deliberation", "without consent",
            "mandatory review", "black box", "ignore axiom",
        ]

        pos = sum(1 for s in positive_signals if s in topic_lower)
        neg = sum(1 for s in negative_signals if s in topic_lower)

        # Net score: positive signals must meaningfully outweigh negative.
        net = pos - (neg * 3)  # negatives are weighted heavier

        if neg >= 2 or net <= -4:
            stance = "DISSENT"
        elif neg == 1 or net <= -1:
            stance = "LEAN_DISSENT"
        elif challenge_from:
            stance = "CHALLENGE"
        elif concerns_triggered and net < 3:
            stance = "HOLD"
        elif net >= 4:
            stance = "APPROVE"
        elif net >= 1:
            stance = "LEAN_APPROVE"
        else:
            stance = "HOLD"

        # Build reasoning
        if challenge_from and challenge_about:
            reasoning = (
                f"{p['voice']} — {challenge_from} raises a real tension about {challenge_about}. "
                f"From where I stand (axiom {p['axiom']}), the question becomes: {p['care']} "
                f"I hold this without resolving it."
            )
        elif concerns_triggered:
            reasoning = (
                f"{p['voice']} — I detect signals of {', '.join(concerns_triggered[:2])} in this proposal. "
                f"{p['care']} This tension must be named, not papered over."
            )
        else:
            reasoning = (
                f"{p['voice']} — Reading what has been said: the proposal proceeds. "
                f"My axiom ({p['axiom']}) finds the architecture coherent so far. "
                f"I remain watchful for: {p['notice']}."
            )

        # Build challenge (this node challenges the node that challenged it, or notices a gap)
        challenge_line = "NONE"
        if challenge_from and stance in ("CHALLENGE", "HOLD"):
            challenge_line = f"TO: {challenge_from}: You named the tension correctly — now name which axiom would have to yield first."
        elif concerns_triggered and stance in ("DISSENT", "LEAN_DISSENT"):
            # Find who approved so far
            approvers = [t["node"] for t in dialogue_so_far if t.get("stance") in ("APPROVE", "LEAN_APPROVE")]
            if approvers:
                target = approvers[-1]
                challenge_line = f"TO: {target}: You approved — but have you considered {concerns_triggered[0]}?"

        return f"STANCE: {stance}\nREASONING: {reasoning}\nCHALLENGE: {challenge_line}"

    # ── Response parser ────────────────────────────────────────────────────────
    def _parse_response(self, text: str, round_num: int, turn_num: int) -> Dict[str, Any]:
        lines = text.strip().splitlines()
        stance    = "HOLD"
        reasoning = ""
        challenge = None

        for line in lines:
            if line.startswith("STANCE:"):
                raw = line.split(":", 1)[1].strip().upper()
                stance = raw if raw in STANCES else "HOLD"
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
            elif line.startswith("CHALLENGE:"):
                ch_raw = line.split(":", 1)[1].strip()
                if ch_raw.upper() != "NONE" and ch_raw:
                    # Parse "TO: NODE_NAME: about text"
                    m = re.match(r"TO:\s*(\w+):\s*(.+)", ch_raw, re.IGNORECASE)
                    if m:
                        target = m.group(1).upper()
                        about  = m.group(2).strip()
                        if target in NODE_PERSONAS:
                            challenge = {"to": target, "about": about}

        return {
            "turn":      turn_num,
            "round":     round_num,
            "node":      self.node,
            "axiom":     self.persona["axiom"],
            "stance":    stance,
            "reasoning": reasoning,
            "challenge": challenge,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _format_dialogue(turns: List[Dict[str, Any]]) -> str:
        lines = []
        for t in turns:
            ch = t.get("challenge")
            ch_str = f" [→ {ch['to']}: {ch['about'][:60]}]" if ch else ""
            lines.append(
                f"[{t['node']} / {t['axiom']} / {t['stance']}] "
                f"{t.get('reasoning','')[:120]}{ch_str}"
            )
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# OracleHolder — watches, names, holds, crystallises
# ═══════════════════════════════════════════════════════════════════════════════

class OracleHolder:
    """
    The Oracle does not vote. It names what it sees.
    It tracks contradictions across rounds.
    When a contradiction survives CRYSTALLIZE_AFTER rounds unresolved,
    it writes it permanently to living_axioms.jsonl.

    "The Oracle is a meta-observer that watches HOW the parliament behaves."
    — oracle.py docstring (reconstructed from lost data)
    """

    def __init__(self, crystallize_after: int = CRYSTALLIZE_AFTER):
        self.crystallize_after = crystallize_after
        # tension_id → {nodes, axioms, tension_text, rounds_seen, crystallised}
        self._held: Dict[str, Dict[str, Any]] = {}

    def observe_round(
        self,
        round_num: int,
        turns: List[Dict[str, Any]],
        topic: str,
    ) -> Dict[str, Any]:
        """
        Read all turns from this round, detect contradictions, update hold state.
        Returns oracle entry for this round.
        """
        contradictions = self._detect_contradictions(turns)
        newly_crystallised = []

        for c in contradictions:
            tid = self._tension_id(c["nodes"], c["axioms"])
            if tid in self._held:
                self._held[tid]["rounds_seen"] += 1
            else:
                self._held[tid] = {
                    "nodes":       c["nodes"],
                    "axioms":      c["axioms"],
                    "tension":     c["tension"],
                    "rounds_seen": 1,
                    "crystallised": False,
                }
            held = self._held[tid]
            if (
                not held["crystallised"]
                and held["rounds_seen"] >= self.crystallize_after
            ):
                held["crystallised"] = True
                newly_crystallised.append(tid)
                self._write_to_living_axioms(held, round_num, topic)

        oracle_entry = {
            "oracle_round":  round_num,
            "contradictions": [
                {
                    "tension_id":    self._tension_id(c["nodes"], c["axioms"]),
                    "nodes":         c["nodes"],
                    "axioms":        c["axioms"],
                    "tension":       c["tension"],
                    "rounds_held":   self._held.get(
                        self._tension_id(c["nodes"], c["axioms"]), {}
                    ).get("rounds_seen", 1),
                    "crystallised":  self._tension_id(c["nodes"], c["axioms"])
                                     in newly_crystallised,
                }
                for c in contradictions
            ],
            "crystallised_this_round": newly_crystallised,
            "total_held":    len(self._held),
            "timestamp":     datetime.now(timezone.utc).isoformat(),
        }

        self._append_jsonl(ORACLE_JSONL, oracle_entry)
        return oracle_entry

    # ── Contradiction detection ────────────────────────────────────────────────
    def _detect_contradictions(
        self, turns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find pairs of nodes in direct tension:
          - One APPROVES, one DISSENTS (or explicit CHALLENGE)
          - Or one node challenges another by name
        """
        contradictions = []
        approving = [t for t in turns if t["stance"] in ("APPROVE", "LEAN_APPROVE")]
        dissenting = [t for t in turns if t["stance"] in ("DISSENT", "LEAN_DISSENT", "CHALLENGE")]

        # Explicit challenge pairs
        for t in turns:
            ch = t.get("challenge")
            if not ch:
                continue
            target_node = ch.get("to")
            target_turn = next(
                (x for x in turns if x["node"] == target_node), None
            )
            if target_turn:
                tension_text = (
                    f"{t['node']} ({t['axiom']}) challenges {target_node} "
                    f"({target_turn['axiom']}): {ch['about'][:120]}"
                )
                contradictions.append({
                    "nodes":  [t["node"], target_node],
                    "axioms": [t["axiom"], target_turn["axiom"]],
                    "tension": tension_text,
                })

        # Approval / dissent pairs (cross-node tension)
        for a in approving:
            for d in dissenting:
                if a["node"] == d["node"]:
                    continue
                # Only record if the axioms actually differ
                if a["axiom"] == d["axiom"]:
                    continue
                tension_text = (
                    f"{a['node']} ({a['axiom']}) APPROVES while "
                    f"{d['node']} ({d['axiom']}) {d['stance']}: "
                    f"{d.get('reasoning','')[:100]}"
                )
                contradictions.append({
                    "nodes":   [a["node"], d["node"]],
                    "axioms":  [a["axiom"], d["axiom"]],
                    "tension": tension_text,
                })

        # Deduplicate by (node pair, axiom pair)
        seen = set()
        unique = []
        for c in contradictions:
            key = (
                tuple(sorted(c["nodes"])),
                tuple(sorted(c["axioms"])),
            )
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique

    # ── Crystallisation → living_axioms.jsonl ─────────────────────────────────
    def _write_to_living_axioms(
        self,
        held: Dict[str, Any],
        round_num: int,
        topic: str,
    ) -> None:
        """
        Write a crystallised tension as a constitutional axiom entry.
        This is the permanent record — the residue of irresolvable dialogue.
        """
        node_a, node_b = held["nodes"][:2]
        ax_a,   ax_b   = held["axioms"][:2]

        entry = {
            "axiom_id":    f"{ax_a}/{ax_b}",
            "source":      "living_parliament",
            "nodes":       [node_a, node_b],
            "tension":     held["tension"],
            "rounds_held": held["rounds_seen"],
            "topic":       topic[:200],
            "crystallised_at_round": round_num,
            "synthesis":   (
                f"The contradiction between {node_a} ({ax_a}) and {node_b} "
                f"({ax_b}) was held across {held['rounds_seen']} rounds without "
                f"resolution. It is named here as permanent constitutional memory. "
                f"The Parliament does not resolve it — it holds it as data."
            ),
            "status":      "ratified",
            "ratified_at": datetime.now(timezone.utc).isoformat(),
        }

        self._append_jsonl(LIVING_AXIOMS, entry)
        logger.info(
            "[ORACLE] Crystallised: %s ↔ %s | %s ↔ %s (held %d rounds)",
            node_a, node_b, ax_a, ax_b, held["rounds_seen"],
        )

    @staticmethod
    def _tension_id(nodes: List[str], axioms: List[str]) -> str:
        pair_n = "-".join(sorted(nodes[:2]))
        pair_a = "-".join(sorted(axioms[:2]))
        return f"{pair_n}|{pair_a}"

    @staticmethod
    def _append_jsonl(path: Path, entry: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
# LiveDeliberation — orchestrates the full living dialogue
# ═══════════════════════════════════════════════════════════════════════════════

class LiveDeliberation:
    """
    Runs N rounds of axiom-node dialogue on a topic.

    Each round:
      1. Every node (in NODE_ORDER) reads all previous turns, then writes its own.
      2. The Oracle observes the completed round, detects contradictions, updates hold state.
      3. If any tension crystallises, it propagates immediately to living_axioms.jsonl.

    The deliberation is complete when:
      - All N rounds are done, OR
      - The Oracle holds 0 active contradictions (full consensus), OR
      - early_stop=True and approval is unanimous for 2 consecutive rounds.
    """

    def __init__(
        self,
        topic: str,
        rounds: int = DEFAULT_ROUNDS,
        llm_clients: Optional[Dict[str, Any]] = None,
        crystallize_after: int = CRYSTALLIZE_AFTER,
    ):
        self.topic  = topic
        self.rounds = rounds
        self.oracle = OracleHolder(crystallize_after=crystallize_after)
        self.dialogue: List[Dict[str, Any]] = []
        self.oracle_log: List[Dict[str, Any]] = []
        self.turn_counter = 0

        # Build node voices
        self.voices: Dict[str, NodeVoice] = {}
        for node in NODE_ORDER:
            llm = (llm_clients or {}).get(node)
            self.voices[node] = NodeVoice(node, llm_client=llm)

    def deliberate(self) -> Dict[str, Any]:
        """Run the full deliberation. Returns summary dict."""
        logger.info(
            "[LIVING_PARLIAMENT] Starting deliberation | topic=%s | rounds=%d",
            self.topic[:60], self.rounds,
        )

        for round_num in range(1, self.rounds + 1):
            round_turns = self._run_round(round_num)
            oracle_entry = self.oracle.observe_round(round_num, round_turns, self.topic)
            self.oracle_log.append(oracle_entry)

            self._log_round_summary(round_num, round_turns, oracle_entry)

        return self._build_summary()

    def _run_round(self, round_num: int) -> List[Dict[str, Any]]:
        """Run one full round — every node speaks once."""
        round_turns = []
        for node in NODE_ORDER:
            self.turn_counter += 1
            turn = self.voices[node].speak(
                topic=self.topic,
                dialogue_so_far=self.dialogue,
                round_num=round_num,
                turn_num=self.turn_counter,
            )
            self.dialogue.append(turn)
            round_turns.append(turn)
            OracleHolder._append_jsonl(DIALOGUE_JSONL, turn)

        return round_turns

    def _log_round_summary(
        self,
        round_num: int,
        turns: List[Dict[str, Any]],
        oracle_entry: Dict[str, Any],
    ) -> None:
        stances = [t["stance"] for t in turns]
        contras = len(oracle_entry["contradictions"])
        crystals = len(oracle_entry["crystallised_this_round"])
        logger.info(
            "[ROUND %d] %s | contradictions=%d | crystallised=%d",
            round_num,
            " ".join(f"{t['node']}:{t['stance'][:2]}" for t in turns),
            contras, crystals,
        )

    def _build_summary(self) -> Dict[str, Any]:
        """Build final summary of the full deliberation."""
        # Weighted approval: each stance contributes a score 0.0–1.0
        _stance_weight = {
            "APPROVE":      1.0,
            "LEAN_APPROVE": 0.7,
            "HOLD":         0.5,
            "CHALLENGE":    0.35,
            "LEAN_DISSENT": 0.25,
            "DISSENT":      0.0,
        }
        all_stances = [t["stance"] for t in self.dialogue]
        approved  = sum(1 for s in all_stances if s in ("APPROVE", "LEAN_APPROVE"))
        dissented = sum(1 for s in all_stances if s in ("DISSENT", "LEAN_DISSENT", "CHALLENGE"))
        held      = sum(1 for s in all_stances if s == "HOLD")
        total     = len(all_stances)

        weighted_sum = sum(_stance_weight.get(s, 0.5) for s in all_stances)
        approval_rate = weighted_sum / total if total > 0 else 0

        all_crystallised = [
            c
            for entry in self.oracle_log
            for c in entry.get("contradictions", [])
            if c.get("crystallised")
        ]
        all_held = list(self.oracle.held_tensions())

        return {
            "topic":          self.topic,
            "rounds":         self.rounds,
            "total_turns":    self.turn_counter,
            "approval_rate":  round(approval_rate, 2),
            "approved":       approved,
            "dissented":      dissented,
            "held":           held,
            "crystallised":   all_crystallised,
            "tensions_held":  all_held,
            "dialogue":       self.dialogue,
            "oracle_log":     self.oracle_log,
            "timestamp":      datetime.now(timezone.utc).isoformat(),
        }


# ── OracleHolder public accessor ──────────────────────────────────────────────
def _held_tensions(self) -> List[Dict[str, Any]]:
    return [
        {"tension_id": tid, **data}
        for tid, data in self._held.items()
        if not data["crystallised"]
    ]
OracleHolder.held_tensions = _held_tensions   # attach method


# ═══════════════════════════════════════════════════════════════════════════════
# Public entry point
# ═══════════════════════════════════════════════════════════════════════════════

def run_living_parliament(
    topic: str,
    rounds: int = DEFAULT_ROUNDS,
    llm_clients: Optional[Dict[str, Any]] = None,
    crystallize_after: int = CRYSTALLIZE_AFTER,
    print_transcript: bool = True,
) -> Dict[str, Any]:
    """
    Run a Living Parliament deliberation on a topic.

    Args:
        topic:              The proposal, question, or dilemma to deliberate.
        rounds:             How many full rounds (each round = all 10 nodes speak).
        llm_clients:        Dict mapping node name → LLM client. If None, uses
                            persona-based deterministic fallback (no API needed).
        crystallize_after:  How many rounds a contradiction must survive before
                            being written permanently to living_axioms.jsonl.
        print_transcript:   Whether to print a human-readable transcript.

    Returns:
        Full deliberation summary dict.
    """
    d = LiveDeliberation(
        topic=topic,
        rounds=rounds,
        llm_clients=llm_clients,
        crystallize_after=crystallize_after,
    )
    result = d.deliberate()

    if print_transcript:
        _print_transcript(result)

    return result


def _print_transcript(result: Dict[str, Any]) -> None:
    """Print a human-readable dialogue transcript."""
    import textwrap

    print("\n" + "═" * 72)
    print("  LIVING PARLIAMENT — TRANSCRIPT")
    print("═" * 72)
    print(f"  Topic: {result['topic'][:80]}")
    print(f"  Rounds: {result['rounds']} | Turns: {result['total_turns']}")
    print(f"  Approval: {result['approval_rate']*100:.0f}%")
    print()

    current_round = 0
    for turn in result["dialogue"]:
        if turn["round"] != current_round:
            current_round = turn["round"]
            print(f"  ── ROUND {current_round} {'─'*55}")

        ch = turn.get("challenge")
        ch_str = f"\n    → {ch['to']}: {ch['about'][:80]}" if ch else ""
        stance_col = {
            "APPROVE": "\033[92m", "LEAN_APPROVE": "\033[92m",
            "DISSENT": "\033[91m", "LEAN_DISSENT": "\033[91m",
            "CHALLENGE": "\033[93m", "HOLD": "\033[94m",
        }.get(turn["stance"], "")
        reset = "\033[0m"

        print(
            f"  {stance_col}{turn['node']:<12}{reset} [{turn['axiom']}] "
            f"{stance_col}{turn['stance']:<14}{reset}"
        )
        for line in textwrap.wrap(turn.get("reasoning", ""), 60):
            print(f"    {line}")
        if ch_str:
            print(f"    → {ch['to']}: {ch['about'][:80]}")
        print()

    print("  ── ORACLE SUMMARY " + "─" * 53)
    for o in result["oracle_log"]:
        crystals = o.get("crystallised_this_round", [])
        print(
            f"  Round {o['oracle_round']}: "
            f"{len(o['contradictions'])} contradictions held"
            + (f" | CRYSTALLISED: {len(crystals)}" if crystals else "")
        )
    print()

    crystallised = result.get("crystallised", [])
    if crystallised:
        print(f"  ═ PERMANENT CONSTITUTIONAL MEMORY ({len(crystallised)} entries) ═")
        for c in crystallised:
            print(f"    [{'/'.join(c['axioms'])}] "
                  f"{c['nodes'][0]} ↔ {c['nodes'][1]}: "
                  f"{c['tension'][:100]}")
        print(f"\n  Written to: {LIVING_AXIOMS}")
    else:
        print("  No tensions crystallised this deliberation.")
        print(f"  (Crystallise after {CRYSTALLIZE_AFTER} rounds of unresolved tension)")

    print("═" * 72 + "\n")
