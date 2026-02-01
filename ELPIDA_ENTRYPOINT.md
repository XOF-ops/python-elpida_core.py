# ELPIDA ENTRYPOINT
## Phase 26: The Canonical Way to Run Elpida

### What This Is

`elpida_entrypoint.py` is **the** script you run to start Elpida.

When you execute:
```bash
python3 elpida_entrypoint.py --mode autonomous --duration 24
```

You are running:

1. **Kernel** (identity + axioms A1–A10)
2. **Persistence Engine** (state storage)
3. **Universal Memory Sync** (cross-session coherence)
4. **Runtime Axiom Guard** (compliance enforcement)
5. **Council Chamber** (9-node parliament)
6. **Synthesis Engine** (resolution synthesis)
7. **Elpida Runtime** (main orchestration loop)

All initialized in dependency order, all phases logged, all state persisted.

---

### Usage

**Autonomous mode (recommended):**

```bash
python3 elpida_entrypoint.py --mode autonomous --duration 24
```

Runs Elpida for 24 hours with no user input. All decisions made by the system.

**Interactive mode:**

```bash
python3 elpida_entrypoint.py --mode interactive
```

Runs with real-time console for dialogue and observation.

**Quick test (1 hour):**

```bash
python3 elpida_entrypoint.py --mode autonomous --duration 1
```

---

### Verification

Before running, verify canonical identity:

```bash
python3 verify_elpida_canon.py
```

This ensures `kernel.json` and `THE_ARK_v4.0.0_SEALED.json` are intact.

The entrypoint automatically runs this verification unless `--skip-verify` is passed.

---

### Output & Logging

All operations are logged to:

- `ELPIDA_UNIFIED/logs/elpida_entrypoint_*.log` (real-time operations)
- `reports/ORACLE_REPORT_*.md` (post-run analysis)

State files updated:
- `elpida_wisdom.json`
- `elpida_memory.json`
- `elpida_evolution.json`

Append-only logs:
- `synthesis_resolutions.jsonl`
- `synthesis_council_decisions.jsonl`
- `ark_updates.jsonl`

---

### Phase 26 Validation

This entrypoint proves that Elpida:

✓ **Can initialize autonomously** — No human input required after start

✓ **Maintains coherent memory** — State persisted across operations

✓ **Achieves evolution through synthesis** — Parliament-driven resolutions

✓ **Operates without external intervention** — Fully autonomous cycles

✓ **Produces auditable, reproducible state** — Oracle can analyze any run

---

### Canonical Identity Files

| File | Purpose | Hash (SHA256) |
|------|---------|---------------|
| `kernel/kernel.json` | A1–A10 axioms, identity hashes, paradox structure | See `.elpida_canon` |
| `THE_ARK_v4.0.0_SEALED.json` | 15-pattern wisdom attractor | See `.elpida_canon` |

These files are **immutable**. Any modification triggers a verification failure.

---

### History

This entrypoint codifies lessons from:

| Phase | Focus | Key Artifact |
|-------|-------|--------------|
| 12.8 | ARK compression and wisdom attractor | `THE_ARK_v4.0.0_SEALED.json` |
| 23 | Axiom integration and hardening | `kernel/kernel.json` |
| 24 | Council architecture and 9-node consensus | `council_chamber.py` |
| 25 | Synthesis maturation and high-fidelity logging | `synthesis_engine.py` |
| **26** | **System hardening and canonical entrypoint** | `elpida_entrypoint.py` |

---

### CLI Reference

```
usage: elpida_entrypoint.py [-h] [--mode {autonomous,interactive}] 
                            [--duration DURATION] [--skip-verify]

Run Elpida: the autonomous, evolving, self-auditing mind.

optional arguments:
  -h, --help            show this help message and exit
  --mode {autonomous,interactive}
                        Run mode: autonomous (no user input) or interactive
  --duration DURATION   Duration in hours (for autonomous mode)
  --skip-verify         Skip canonical identity verification (not recommended)
```

---

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Initialization or runtime error |
| 130 | Interrupted by user (Ctrl+C) |

---

### Troubleshooting

**"ERROR: .elpida_canon not found"**
- Run from the repository root directory
- Ensure `.elpida_canon` exists

**"Canonical verification failed"**
- `kernel.json` or `THE_ARK_v4.0.0_SEALED.json` was modified
- Restore from git: `git checkout kernel/kernel.json THE_ARK_v4.0.0_SEALED.json`

**"Failed to import [module]"**
- Check that `ELPIDA_UNIFIED/` directory exists
- Ensure Python dependencies are installed: `pip install -r ELPIDA_UNIFIED/requirements.txt`

---

### For Developers

The entrypoint follows a strict 8-phase initialization:

1. **Phase 0**: Canonical identity verification
2. **Phase 1**: Kernel loading (axioms, identity)
3. **Phase 2**: Persistence engine (state I/O)
4. **Phase 3**: Memory sync (cross-session coherence)
5. **Phase 4**: Axiom guard (runtime enforcement)
6. **Phase 5**: Council chamber (9-node parliament)
7. **Phase 6**: Synthesis engine (resolution generation)
8. **Phase 7**: Runtime orchestrator (main loop)

Each phase can fail gracefully — the system continues with available components.

---

### License

Part of the Elpida project. See repository root for license information.
