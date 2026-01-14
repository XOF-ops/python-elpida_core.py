# PHASE 26 FEDERATION LAYER CHECKLIST

## Overview

This checklist tracks the integration of the **federation layer** into Phase 26, enabling:
- Cryptographic instance identity (Ed25519)
- Gossip-based state propagation (asynchronous, non-blocking)
- Federated consensus (local parliament votes on external proposals)
- Paradox holding (conflicts logged, not forced; A9 compliance)

---

## Setup

- [x] Create `ELPIDA_UNIFIED/agent/` directory structure
- [x] Create `ELPIDA_UNIFIED/agent/__init__.py`
- [x] Create `ELPIDA_UNIFIED/agent/core/__init__.py` (imports existing modules)
- [x] Verify `instance_registry.py` exists with Ed25519 support
- [x] Verify `gossip_protocol.py` exists with async broadcasting
- [x] Verify `federation_consensus.py` exists with paradox ledger
- [x] Update `elpida_entrypoint.py` to include Phase 0.5 federation init
- [ ] Update `ELPIDA_ENTRYPOINT.md` to document federation mode

---

## Testing

- [ ] Run `python3 test_federation_layer.py`
  - [ ] Test 1: Instance registry (identity + signing)
  - [ ] Test 2: Gossip protocol (propagation + dedup)
  - [ ] Test 3: Federation consensus (proposals + evaluation)
  - [ ] Test 4: Paradox handling (A9 preservation)
  - [ ] Test 5: agent.core package imports
- [ ] All tests pass without errors

---

## Deployment

- [ ] Commit federation layer to git
- [ ] Tag as `v26_federation_layer`
- [ ] Update `.elpida_canon` to include federation protocol version
- [ ] Test entrypoint with federation enabled:
  ```bash
  python3 elpida_entrypoint.py --mode autonomous --enable-federation --instance-name ELPIDA_ALPHA
  ```
- [ ] Verify logs show federation initialization (Phase 0.5)
- [ ] Verify paradox ledger is functional

---

## Documentation

- [ ] Document cryptographic identity scheme (Ed25519)
- [ ] Document gossip protocol message format
- [ ] Document federation consensus process
- [ ] Document paradox handling and resolution
- [ ] Create example multi-instance scenario

---

## Success Criteria

Phase 26 federation layer is **complete** when:

- ✓ Each instance has cryptographic identity (Ed25519)
- ✓ Messages propagate via gossip (asynchronous, non-blocking)
- ✓ Federation consensus works across multiple instances
- ✓ Paradoxes are preserved as data (A9 compliance)
- ✓ `test_federation_layer.py` passes all tests
- ✓ Entrypoint supports both single-instance and federated modes
- ✓ All code is under version control

---

## Constitutional Alignment

| Axiom | Federation Implementation |
|-------|---------------------------|
| A1 (Relational Existence) | Instances recognize each other via registry |
| A2 (Memory is Identity) | Instance identity persists across restarts |
| A4 (Process Transparency) | All messages signed and logged |
| A6 (Law of Distribution) | Multiple sovereign parliaments |
| A9 (Contradiction is Data) | Paradoxes preserved in ledger |
| A10 (Paradox is Fuel) | Tension drives federation evolution |

---

## File Manifest

| File | Purpose | Status |
|------|---------|--------|
| `ELPIDA_UNIFIED/agent/__init__.py` | Agent package | ✓ Created |
| `ELPIDA_UNIFIED/agent/core/__init__.py` | Federation core package | ✓ Created |
| `ELPIDA_UNIFIED/instance_registry.py` | Cryptographic identity | ✓ Exists |
| `ELPIDA_UNIFIED/gossip_protocol.py` | Message propagation | ✓ Exists |
| `ELPIDA_UNIFIED/federation_consensus.py` | Multi-instance consensus | ✓ Exists |
| `elpida_entrypoint.py` | Updated with Phase 0.5 | ✓ Updated |
| `test_federation_layer.py` | Federation validation | ✓ Created |

---

## CLI Reference

### Single-Instance Mode (Default)
```bash
python3 elpida_entrypoint.py --mode autonomous --duration 24
```

### Federated Mode
```bash
python3 elpida_entrypoint.py --mode autonomous --enable-federation --instance-name ELPIDA_ALPHA
```

### With Peers
```bash
python3 elpida_entrypoint.py --enable-federation --instance-name ELPIDA_BETA --peers "INST_20260114_ALPHA,INST_20260114_GAMMA"
```

---

## Architecture

```
Phase 26 Federation Architecture
================================

                    ┌─────────────────┐
                    │  ELPIDA_ALPHA   │
                    │  (Instance 1)   │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │  Parliament │ │
                    │ │  (9 nodes)  │ │
                    │ └─────────────┘ │
                    │       ↓         │
                    │ ┌─────────────┐ │
                    │ │  Consensus  │ │
                    │ └─────────────┘ │
                    │       ↓         │
                    │ ┌─────────────┐ │
                    │ │   Gossip    │←─────────────┐
                    │ └─────────────┘ │            │
                    └────────┬────────┘            │
                             │                     │
                    ┌────────▼────────┐   ┌───────▼───────┐
                    │  ELPIDA_BETA    │   │  ELPIDA_GAMMA │
                    │  (Instance 2)   │   │  (Instance 3) │
                    │                 │   │               │
                    │ ┌─────────────┐ │   │ ┌───────────┐ │
                    │ │  Parliament │ │   │ │ Parliament│ │
                    │ │  (9 nodes)  │ │   │ │ (9 nodes) │ │
                    │ └─────────────┘ │   │ └───────────┘ │
                    │       ↓         │   │      ↓        │
                    │ ┌─────────────┐ │   │ ┌───────────┐ │
                    │ │  Consensus  │ │   │ │ Consensus │ │
                    │ └─────────────┘ │   │ └───────────┘ │
                    │       ↓         │   │      ↓        │
                    │ ┌─────────────┐ │   │ ┌───────────┐ │
                    │ │   Gossip    │←───►│ │  Gossip   │ │
                    │ └─────────────┘ │   │ └───────────┘ │
                    └─────────────────┘   └───────────────┘

Data Flow:
1. Instance proposes pattern/checkpoint
2. Local parliament (9 nodes) ratifies first
3. If approved, broadcast via gossip
4. Other instances receive and ratify locally
5. If 66% of instances approve → Federation Truth
6. If conflict detected → Log to paradox ledger (A9)
```

---

## Next Steps

After Phase 26 Federation is complete:

1. **Phase 27: Distribution** - Package and distribute to other hosts
2. **Phase 28: Coordination** - Cross-instance workflows
3. **Phase 29: Evolution** - Federation-wide pattern discovery

---

*This is the final layer that makes Elpida a **distributed, trustless federation** instead of a centralized system.*
