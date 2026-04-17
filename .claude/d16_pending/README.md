# D16 Pending Bundles

This directory holds D16 execution bundles awaiting Gemini D4/D5 audit.

## Bundle schema (per `D16_ACTION_PROTOCOL.md`)

```json
{
  "execution_id": "d16-exec-NNNN",
  "timestamp": "ISO 8601",
  "source_domain": "D0 | D11 | D16 | BODY",
  "target": "CURSOR_WORKSPACE | ARCHITECT_WORKSPACE | S3_FEDERATION | HF_SPACE",
  "action_type": "BUG_FIX | SCHEMA_LOCK | FILE_WRITE | CONFIG_CHANGE",
  "proposed_diff": "...code or config diff...",
  "d4_verification": {
    "status": "PENDING",
    "constitutional_basis": ["A4", "A8"],
    "scope": "LOCAL_FILE_EDIT",
    "impact_assessment": "human-readable risk statement",
    "reversibility": "HIGH"
  }
}
```

## Lifecycle

1. Agent (Cursor / Claude / Copilot / BODY) drops a `*.json` bundle here
   with `d4_verification.status = "PENDING"`.
2. Next deploy (or manual `python scripts/gemini_audit_relay.py`) audits it.
3. **VERIFIED** → bundle moves to `.claude/d16_archive/`, deploy proceeds.
4. **REJECTED / HOLD** → bundle stays here with verdict embedded, deploy
   blocks. Operator addresses `required_changes` and re-stages.

Verdicts are appended to `.claude/bridge/from_gemini.md`.
