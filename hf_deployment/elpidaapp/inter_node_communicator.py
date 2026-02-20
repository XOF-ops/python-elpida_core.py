"""
inter_node_communicator — Live debate protocol between Parliament nodes.

Rebuilt from the schema preserved in cross_domain_synthesis_enubet.py
(ElpidaLostProgress, January 2026). The original module was lost when the
codespace expired; only its API surface survived in the ENUBET script.

Each Parliament node is a NodeCommunicator that can:
  1. broadcast(message_type, content, intent) → shared message bus
  2. listen() → read all broadcasts from other nodes
  3. respond(to_node, content, intent) → directed reply

The message bus is an in-memory list within a Debate session.
When the debate completes, the bus can be flushed to BODY bucket
as a debate transcript JSONL.

Recovered schema (from cross_domain_synthesis_enubet.py):
    nodes['HERMES'] = NodeCommunicator('HERMES', 'INTERFACE')
    nodes['HERMES'].broadcast(
        message_type="AXIOM_APPLICATION",
        content="A1 analysis: Who are the stakeholders?",
        intent="Map relational structure"
    )
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Message types ─────────────────────────────────────────────────

MESSAGE_TYPES = {
    "AXIOM_APPLICATION",   # Node applies its axiom to the dilemma
    "CHALLENGE",           # Node challenges another node's broadcast
    "SYNTHESIS_OFFER",     # Node proposes a third-way synthesis
    "PATTERN_MATCH",       # MNEMOSYNE: historical pattern found
    "VETO_SIGNAL",         # Node signals veto intention before formal vote
    "CONCESSION",          # Node adjusts position based on another's argument
    "META_OBSERVATION",    # CHAOS or D11: observation about the debate itself
}


@dataclass
class Message:
    """A single broadcast or directed message on the debate bus."""
    sender: str
    role: str
    message_type: str
    content: str
    intent: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    # Directed reply (None = broadcast to all)
    to_node: Optional[str] = None
    # Axiom invoked
    axiom: Optional[str] = None
    # Round number within the debate
    round_num: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MessageBus:
    """
    Shared in-memory message bus for a single debate session.

    All NodeCommunicators in a debate share the same bus instance.
    After the debate, the bus can be serialised to JSONL for S3 persistence.
    """

    def __init__(self, debate_id: str):
        self.debate_id = debate_id
        self.messages: List[Message] = []
        self._round: int = 0

    @property
    def round_num(self) -> int:
        return self._round

    def advance_round(self) -> int:
        self._round += 1
        return self._round

    def post(self, msg: Message) -> None:
        """Post a message to the bus."""
        msg.round_num = self._round
        self.messages.append(msg)

    def listen(
        self,
        listener: str,
        *,
        since_round: int = 0,
        message_type: Optional[str] = None,
        from_node: Optional[str] = None,
    ) -> List[Message]:
        """
        Read messages visible to *listener*.

        Returns broadcasts + messages directed to this node,
        filtered optionally by round, type, and sender.
        """
        result = []
        for m in self.messages:
            if m.sender == listener:
                continue  # skip own messages
            if m.round_num < since_round:
                continue
            if m.to_node is not None and m.to_node != listener:
                continue  # directed to someone else
            if message_type and m.message_type != message_type:
                continue
            if from_node and m.sender != from_node:
                continue
            result.append(m)
        return result

    def to_jsonl(self) -> str:
        """Serialise the full transcript as JSONL."""
        lines = []
        for m in self.messages:
            d = m.to_dict()
            d["debate_id"] = self.debate_id
            lines.append(json.dumps(d, ensure_ascii=False))
        return "\n".join(lines)

    def summary(self) -> Dict[str, Any]:
        """Quick stats about the debate."""
        senders = {}
        types = {}
        for m in self.messages:
            senders[m.sender] = senders.get(m.sender, 0) + 1
            types[m.message_type] = types.get(m.message_type, 0) + 1
        return {
            "debate_id": self.debate_id,
            "rounds": self._round,
            "total_messages": len(self.messages),
            "messages_per_node": senders,
            "messages_per_type": types,
        }


class NodeCommunicator:
    """
    A Parliament node that can broadcast and listen during live debate.

    Reconstruction of the lost inter_node_communicator module.
    Original API (from cross_domain_synthesis_enubet.py):
        node = NodeCommunicator(name, role)
        node.broadcast(message_type, content, intent)
    """

    def __init__(
        self,
        name: str,
        role: str,
        *,
        axiom: Optional[str] = None,
        bus: Optional[MessageBus] = None,
    ):
        self.name = name
        self.role = role
        self.axiom = axiom
        self._bus: Optional[MessageBus] = bus
        self._last_read_round: int = 0

    def attach(self, bus: MessageBus) -> None:
        """Attach to a shared MessageBus for a debate session."""
        self._bus = bus
        self._last_read_round = 0

    def broadcast(
        self,
        message_type: str,
        content: str,
        intent: str,
    ) -> Message:
        """
        Broadcast a message to all other nodes on the bus.

        This is the exact API preserved in cross_domain_synthesis_enubet.py.
        """
        if self._bus is None:
            raise RuntimeError(f"{self.name}: not attached to a MessageBus")

        msg = Message(
            sender=self.name,
            role=self.role,
            message_type=message_type,
            content=content,
            intent=intent,
            axiom=self.axiom,
        )
        self._bus.post(msg)
        logger.debug("NODE %s broadcast [%s]: %s", self.name, message_type, intent)
        return msg

    def respond(
        self,
        to_node: str,
        message_type: str,
        content: str,
        intent: str,
    ) -> Message:
        """Send a directed message to a specific node."""
        if self._bus is None:
            raise RuntimeError(f"{self.name}: not attached to a MessageBus")

        msg = Message(
            sender=self.name,
            role=self.role,
            message_type=message_type,
            content=content,
            intent=intent,
            axiom=self.axiom,
            to_node=to_node,
        )
        self._bus.post(msg)
        logger.debug("NODE %s → %s [%s]: %s", self.name, to_node, message_type, intent)
        return msg

    def listen(
        self,
        *,
        new_only: bool = True,
        message_type: Optional[str] = None,
        from_node: Optional[str] = None,
    ) -> List[Message]:
        """
        Read messages from the bus.

        If new_only=True, only return messages posted since last listen().
        """
        if self._bus is None:
            return []

        since = self._last_read_round if new_only else 0
        msgs = self._bus.listen(
            self.name,
            since_round=since,
            message_type=message_type,
            from_node=from_node,
        )
        if new_only and msgs:
            self._last_read_round = self._bus.round_num
        return msgs

    def __repr__(self) -> str:
        return f"NodeCommunicator({self.name!r}, {self.role!r}, axiom={self.axiom!r})"


# ── Parliament node registry ─────────────────────────────────────
# Matches both the lost code (ENUBET script) and current governance_client.py

PARLIAMENT_NODES = {
    "HERMES":     {"role": "INTERFACE",    "axiom": "A1"},
    "MNEMOSYNE":  {"role": "ARCHIVE",      "axiom": "A0"},
    "CRITIAS":    {"role": "CRITIC",       "axiom": "A3"},
    "TECHNE":     {"role": "ARTISAN",      "axiom": "A4"},
    "KAIROS":     {"role": "ARCHITECT",    "axiom": "A5"},
    "THEMIS":     {"role": "JUDGE",        "axiom": "A6"},
    "PROMETHEUS": {"role": "SYNTHESIZER",  "axiom": "A8"},
    "IANUS":      {"role": "GATEKEEPER",   "axiom": "A9"},
    "CHAOS":      {"role": "VOID",         "axiom": "A9"},
}


def create_debate_bus(debate_id: Optional[str] = None) -> MessageBus:
    """Create a new debate bus with optional custom ID."""
    if debate_id is None:
        ts = datetime.now(timezone.utc).isoformat()
        debate_id = hashlib.sha256(ts.encode()).hexdigest()[:16]
    return MessageBus(debate_id)


def create_parliament_nodes(bus: MessageBus) -> Dict[str, NodeCommunicator]:
    """
    Instantiate all 9 Parliament nodes attached to a shared bus.

    Returns dict keyed by node name.
    """
    nodes = {}
    for name, info in PARLIAMENT_NODES.items():
        node = NodeCommunicator(
            name=name,
            role=info["role"],
            axiom=info["axiom"],
            bus=bus,
        )
        nodes[name] = node
    return nodes
