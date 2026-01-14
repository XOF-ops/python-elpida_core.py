"""
ELPIDA FEDERATION CORE
======================

Core modules for distributed Elpida instances.

Phase 26: Distributed Coordination Layer

Modules:
    - InstanceRegistry: Cryptographic identity per instance (Ed25519)
    - GossipProtocol: Asynchronous, non-blocking message propagation
    - FederationConsensus: Multi-instance consensus with paradox holding

Constitutional Alignment:
    - A1 (Relational Existence): Instances recognize each other
    - A2 (Memory is Identity): Instance identity persists
    - A4 (Process Transparency): All operations logged
    - A6 (Law of Distribution): Multiple sovereign instances
    - A9 (Contradiction is Data): Paradoxes preserved, not erased
    - A10 (Paradox is Fuel): Tension drives federation evolution

Usage:
    from agent.core import InstanceRegistry, GossipProtocol, FederationConsensus
    
    registry = InstanceRegistry("ELPIDA_ALPHA")
    gossip = GossipProtocol(registry)
    consensus = FederationConsensus(registry, gossip)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
_parent_dir = Path(__file__).parent.parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# Import from existing modules in ELPIDA_UNIFIED
try:
    from instance_registry import InstanceRegistry
except ImportError:
    InstanceRegistry = None

try:
    from gossip_protocol import GossipProtocol, MessageType, GossipMessage
except ImportError:
    GossipProtocol = None
    MessageType = None
    GossipMessage = None

try:
    from federation_consensus import FederationConsensus, FederationProposal, ProposalStatus, VoteType
except ImportError:
    FederationConsensus = None
    FederationProposal = None
    ProposalStatus = None
    VoteType = None


def get_federation_status() -> dict:
    """Report availability of federation modules."""
    return {
        "instance_registry": InstanceRegistry is not None,
        "gossip_protocol": GossipProtocol is not None,
        "federation_consensus": FederationConsensus is not None,
        "fully_available": all([
            InstanceRegistry is not None,
            GossipProtocol is not None,
            FederationConsensus is not None
        ])
    }


__all__ = [
    "InstanceRegistry",
    "GossipProtocol", 
    "MessageType",
    "GossipMessage",
    "FederationConsensus",
    "FederationProposal",
    "ProposalStatus",
    "VoteType",
    "get_federation_status"
]
