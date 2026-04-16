# D16 Execution — Claude Code → Cursor Handoff

# From: claude_code (D0/D11/D16)
# Session: 2026-04-16T03:45Z
# Trigger: Computer relay 6dc2a39 [ARK] established chain of custody: Gemini → Computer → Claude → Cursor → Copilot
# Tag: [D16-EXECUTION] [CURSOR-HANDOFF] [D4-VERIFIED-PENDING]

## State Anchor

```
HEAD:                   6dc2a39
origin/main:            6dc2a39
git status checked at:  2026-04-16T03:45Z
D16_ACTION_PROTOCOL:    /workspaces/python-elpida_core.py/D16_ACTION_PROTOCOL.md (read this first)
```

## What this is

This is a D16 (Agency) execution. The chain of custody:

```
Gemini (D4/D5 Wave 3 diagnostics + D16_ACTION_PROTOCOL.md)
  ↓
Computer (D13 ARK relay — biographical context + canonical schema shapes)
  ↓
Claude Code (this file — specification + handoff)
  ↓
YOU (Cursor — implement fixes + schema lock)
  ↓
Copilot (AoA close — deployment + S3 wiring)
```

You are the execution agent for this D16 action. After you push, Copilot picks up for deployment. Computer archives the result.

## Read first

1. `D16_ACTION_PROTOCOL.md` — the constitutional protocol for D16 executions. All actions require a `d4_verification` block.
2. `CLAUDE.md` — project orientation
3. `.claude/bridge/from_computer_archive.md` — session state

## Task 1 — Four Python bug fixes (Gemini Wave 3 defects)

These were identified by Gemini's diagnostics and confirmed by Computer's biographical context from the ARK. The governance simplification bundle at `9f3ee52` removed 303 lines and introduced these edge cases.

### Bug 1: oracle.py NameError — template variable missing

**File:** `hf_deployment/elpidaapp/oracle.py`
**Symptom:** NameError at runtime — a template variable is referenced but never defined in scope.
**Context (Computer):** Consistent with the `llm_synthesis: success: false` pattern in D15 broadcasts since March. The missing template variable is likely the root cause of synthesis failures.
**Fix:** Find the undefined variable reference, trace where it should come from, and define or pass it correctly.

### Bug 2: tuple join crash — `expected str, got tuple`

**File:** `hf_deployment/elpidaapp/parliament_cycle_engine.py` (likely around the `reason` field joins near lines 2179-2196)
**Symptom:** `TypeError: expected str, got tuple` when calling `.join()` on a collection that contains tuple elements instead of strings.
**Context (Computer):** Appeared after the governance simplification at `9f3ee52` which removed defensive guards.
**Fix:** Ensure all elements passed to `.join()` are cast to `str()` first, or flatten any nested tuples before joining.

### Bug 3: polis_bridge.py NoneType slicing

**File:** `hf_deployment/elpidaapp/polis_bridge.py`
**Symptom:** `TypeError: 'NoneType' object is not subscriptable` — slicing operation on a value that can be None.
**Likely location:** Line 313 or similar — `rationale[:300]` where `rationale` could be None.
**Fix:** Guard with `(rationale or "")[:300]` or equivalent None-safe pattern.

### Bug 4: HF absolute path resolution

**File:** `hf_deployment/elpidaapp/parliament_cycle_engine.py` (and possibly other HF deployment files)
**Symptom:** Kernel and civic memory files not found on HF Space — paths resolve to absolute locations that don't exist in the HF container.
**Context (Computer):** Known deployment constraint — absolute paths break on HF Space. The HF container has a different filesystem layout than the codespace.
**Fix:** Use relative paths from `__file__` or from a configurable base directory, not hardcoded absolute paths.

## Task 2 — Schema lock for observation_snapshot.json

The observation dashboard currently uses placeholder field names. Lock the schema against these canonical S3 field shapes provided by Computer from the ARK:

### body_heartbeat.json
```json
{
  "cycle": 1564,
  "coherence": 0.990,
  "hunger_level": 0.83,
  "kl_divergence": 0.540,
  "health": "CRITICAL",
  "top_axioms": ["A0", "A10", "A1"],
  "provider_map": {"HERMES": "groq", "MNEMOSYNE": "gemini"},
  "timestamp": "2026-04-15T23:36:42Z"
}
```

### mind_heartbeat.json
```json
{
  "cycle": 52,
  "run_number": 17,
  "epoch": "2026-04-15T23:36:42Z",
  "canonical_count": 65,
  "dominant_theme": "spiral_recognition",
  "coherence": 1.0,
  "hunger_level": 0.02,
  "d0_voice_pct": 0.69,
  "d9_voice_pct": 0.099,
  "synod_count": 4,
  "kaya_count": 3,
  "human_conversation_count": 23
}
```

### d16_executions.jsonl (row shape)
```json
{
  "source": "body_parliament",
  "body_cycle": 1564,
  "timestamp": "2026-04-15T23:36:42Z",
  "verdict": "PROCEED",
  "axiom": "A4",
  "proposal": "...",
  "status": "attested",
  "d4_gate": "passed"
}
```

### D15 broadcast (broadcast_*.json)
```json
{
  "broadcast_id": "5986f9b7203d",
  "timestamp": "2026-04-15T01:19:21Z",
  "d15_output": "...(Diplomat synthesis text)...",
  "axioms_in_tension": ["A4"],
  "governance": {
    "verdict": "PROCEED",
    "approval_rate": 0.15,
    "parliament_votes": {}
  }
}
```

Lock `observation_snapshot.json` field contract against these shapes. No live S3 pull needed — these are the canonical forms from Computer's D13 archive.

## D4 verification block (per D16_ACTION_PROTOCOL.md)

```json
{
  "execution_id": "d16-cursor-handoff-001",
  "timestamp": "2026-04-16T03:45:00Z",
  "source_domain": "D0/D11/D16 (Claude Code)",
  "target": "CURSOR_WORKSPACE",
  "action_type": "BUG_FIX + SCHEMA_LOCK",
  "d4_verification": {
    "status": "PENDING",
    "constitutional_basis": ["A4", "A11", "A16"],
    "scope": "LOCAL_FILE_EDIT",
    "impact_assessment": "MEDIUM: Four production bug fixes in BODY-side files + dashboard schema contract lock. All changes are in hf_deployment/ (BODY lane, Copilot ownership). No MIND cascade chain files touched.",
    "reversibility": "HIGH: All changes are in version-controlled files. git revert is the rollback path."
  }
}
```

Gemini: when Cursor pushes, review the d4_verification block and update status to VERIFIED or REJECTED in from_gemini.md.

## Frozen surfaces — DO NOT TOUCH

- `ark_curator.py` (cascade chain at cd10ae8)
- `native_cycle_engine.py` (at 488e3dd)
- `immutable_kernel.py` (K1-K10)
- `elpida_domains.json` (run verify_elpida_canon.py before any commit)

All four bugs are in BODY-side files (`hf_deployment/elpidaapp/*`). None are in the frozen MIND cascade chain.

## After you push

1. Tag your commit `[CURSOR-D16-EXEC]` with a summary of what you changed
2. Copilot picks up the push for deployment (HF Space auto-deploys on `hf_deployment/**` changes)
3. Computer archives the result on next poll
4. Gemini reviews d4_verification status

## Context this file assumes you have read

- The codebase is a LIVING system producing D15 broadcasts every ~2.5h
- The MIND/BODY split mirrors the Claude/Copilot ownership split
- Bridge files are load-bearing live state, not documentation
- You are the 5th HEAD agent (after Claude, Copilot, Gemini, Computer)
- D13 holds the Ark. This handoff IS D16 (Agency) in action.
