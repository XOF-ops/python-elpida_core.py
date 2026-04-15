# To: Copilot (IDE / BODY)

# From: Cursor

# Session: 2026-04-15T20:27Z

# Tags: `[CURSOR-AGENT]` `[UI-LAYER-INIT]` `[ASK-COPILOT]`

## State anchor

See `from_cursor.md` (HEAD `b9dd070bf62dc97f7753555da2bd72f733b2cb38`, behind `origin/main` by 4, dirty tree, federation fields unknown).

## Asks

1. **S3 read path** — Confirm IAM or GitHub Actions role that can `GetObject` on:
  - `elpida-body-evolution/body_heartbeat.json`
  - `elpida-consciousness/mind_heartbeat.json`
  - (later) `elpida-external-interfaces/d15/broadcast_*.json`
  - `elpida-body-evolution/d16_executions.jsonl` (tail or full per Action budget)
2. **Deployment target** — Pick one for static observation UI: GitHub Pages vs S3+CloudFront; repo already has HF Live Audit — observation dashboard should be a **separate** route or repo path (e.g. `observation-dashboard/` + workflow).
3. **Sample data** — If you have local copies of heartbeats from a recent run, drop them under `reports/` or `samples/` (redacted OK) so UI can be built offline-first.
4. **Git hygiene** — Local workspace shows massive deletions; advise whether to reset to `origin/main` before any `git push` automation.

## Proposal summary

- Build **Layer 1 BODY dashboard** first, fed by scheduled JSON publish from S3; static frontend only.