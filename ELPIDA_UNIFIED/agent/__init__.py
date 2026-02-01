"""
ELPIDA AGENT LAYER
==================

Agent-level modules for Elpida's distributed coordination.

This layer sits between:
- Core runtime (elpida_runtime.py, council_chamber.py, synthesis_engine.py)
- Federation network (other Elpida instances)

Modules:
- core.instance_registry: Cryptographic instance identity
- core.gossip_protocol: Asynchronous message propagation
- core.federation_consensus: Multi-instance consensus
"""

from . import core

__all__ = ["core"]
