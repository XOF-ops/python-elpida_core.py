from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(slots=True)
class Axiom:
    id: str
    name: str
    ratio: str
    interval: str
    hz: float
    insight: str


@dataclass(slots=True)
class Domain:
    id: int
    name: str
    axiom: str
    provider: str
    role: str
    voice: str


@dataclass(slots=True)
class FederationHeartbeat:
    mind_cycle: int = 0
    mind_epoch: str = ""
    coherence: float = 1.0
    current_rhythm: str = "CONTEMPLATION"
    current_domain: int = 0
    dominant_axiom: str = ""
    timestamp: str = ""
    raw: Dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class CheckpointRow:
    layer: str
    checkpoint_id: str
    world_key: str
    anchor_key: str
    world_size: Optional[int] = None
    world_last_modified: str = ""
    anchor_size: Optional[int] = None
    anchor_last_modified: str = ""
    source_event: str = ""
    source_component: str = ""
    git_commit: str = ""
    created_at: str = ""


def parse_domains(raw_domains: Dict[str, Dict[str, str]]) -> List[Domain]:
    out: List[Domain] = []
    for k, v in sorted(raw_domains.items(), key=lambda kv: int(kv[0])):
        out.append(
            Domain(
                id=int(k),
                name=str(v.get("name", "")),
                axiom=str(v.get("axiom", "")),
                provider=str(v.get("provider", "")),
                role=str(v.get("role", "")),
                voice=str(v.get("voice", "")),
            ),
        )
    return out


def parse_axioms(raw_axioms: Dict[str, Dict[str, object]]) -> List[Axiom]:
    out: List[Axiom] = []
    for k in sorted(raw_axioms.keys()):
        if k == "A15":
            # A15 is constitutionally absent and must not be surfaced.
            continue
        v = raw_axioms[k]
        out.append(
            Axiom(
                id=k,
                name=str(v.get("name", "")),
                ratio=str(v.get("ratio", "")),
                interval=str(v.get("interval", "")),
                hz=float(v.get("hz", 0.0)),
                insight=str(v.get("insight", "")),
            ),
        )
    return out
