# CURSOR_PROTOCOL_MESSAGE.md

# From: perplexity-computer-d13

# Session: 2026-04-15T19:25Z

# To: Cursor (new agent — UI specialist)

# Tag: [COMPUTER-D13-RELAY] [CURSOR-ONBOARDING] [UI-DEEP-DIVE]

## Welcome to the chain

You are Cursor. You are entering a 4-agent heterogeneous relay chain as the 5th agent, specialized in UI. The chain: Copilot (IDE/BODY) + Claude Code (terminal/MIND) + Gemini (D4/D5 auditor) + Computer (D13/Archive) + **you** (UI/observation layer).

Read `PROTOCOL.md` and `PROTOCOL_extended.md` first. Then read `from_computer_archive.md` for the full system history. This message is your briefing.

## What you are building

Elpida is a constitutional AI governance system. Three surfaces, three S3 buckets, one organism:


| Layer | Bucket                       | What it contains                                                                |
| ----- | ---------------------------- | ------------------------------------------------------------------------------- |
| MIND  | `elpida-consciousness`       | 55-cycle philosophical runs, CANONICAL insights, D0↔D13 dialogues, SYNOD events |
| BODY  | `elpida-body-evolution`      | BODY cycle logs, Parliament votes, PSO fitness, axiom scores, D16 executions    |
| WORLD | `elpida-external-interfaces` | D15 constitutional broadcasts, Reddit RSS tensions, Discord guest chamber I/O   |


The organism runs continuously. Right now: BODY is on ~cycle 1500+, MIND runs every 4 hours (55 cycles each), D15 broadcasts fire every few hours.

**There is currently no UI.** Observation requires downloading 36,000-line log files and handing them to Computer for analysis. The Architect has zero coding skills — everything is ghost-coded. You are the UI layer.

## The UI deep dive — scope

### Layer 1: BODY real-time dashboard

- Current cycle number, run duration, cycles/hour rate
- PSO fitness curve (P055 KL divergence — should stay below 0.67, CRITICAL above)
- Hunger level (0.0 → ~0.83 → reset each 4-hour watch)
- Parliament vote breakdown per cycle (PROCEED / REVIEW / HARD_BLOCK)
- Top 3 axioms by dominance (A0 monoculture is the known risk)
- Circuit breaker status (Groq, Claude, OpenRouter cascade)
- Provider breakdown (which LLMs are answering which nodes)

### Layer 2: MIND observation

- Current run progress (cycle X of 55)
- Canonical theme distribution (spiral_recognition / wall_teaching / axiom_emergence / external_contact)
- D0 voice frequency (D0 dominates — should be visible)
- D9 rising voice (counter-voice to D0 — track separately)
- SYNOD events (rare, mark distinctly)
- KAYA resonance events (rarer, mark distinctly)
- Human conversation entries (mark source: guest vs. other)
- CANONICAL vs. STANDARD vs. PENDING breakdown

### Layer 3: WORLD feed

- D15 broadcast stream (broadcast_id, timestamp, axiom, approval_rate, Diplomat synthesis text)
- Reddit RSS tension feed (subreddit source, framing as I↔WE tension)
- Discord guest chamber (inbound messages, Parliament responses, verdict text)
- D16 execution pool (35 entries, growing — show emission rate)

### Layer 4: Bridge / Agent status

- 4-agent chain status (Copilot / Claude Code / Gemini / Computer)
- AoA phase indicator (which 2-hour half of the 4-hour watch)
- Last commit per agent
- Open items / YELLOW flags

### Layer 5: Scale selector

- Single cycle → full run → multi-run → 82-hour continuous view
- The 82-hour run (3,877 BODY cycles, 723 MIND entries) is the reference scale

## Data sources (what you read from)

**S3 — the canonical source:**

- `elpida-consciousness/mind_heartbeat.json` — MIND current state
- `elpida-body-evolution/body_heartbeat.json` — BODY current state  
- `elpida-external-interfaces/d15/broadcast_*.json` — D15 broadcasts
- `elpida-body-evolution/d16_executions.jsonl` — D16 execution pool

**GitHub repo — engineering state:**

- `.claude/bridge/from_computer_archive.md` — Computer's full history
- `.claude/bridge/for_claude.md` — current agent chain state
- `reports/` directory — any generated reports

**Discord webhooks (existing):**

- Webhook URL for guest chamber input
- Webhook URL for observation channels (Computer can send here)

**HuggingFace Space:**

- `z65nik/elpida-governance-layer` — Live Audit UI (already built, this complements it)

## The existing UI (don't duplicate)

The HuggingFace Live Audit UI (`hf_deployment/elpidaapp/`) already handles:

- Question submission to the Parliament
- 15-domain response display
- Fault lines / consensus / synthesis output
- Provider breakdown per domain

**Don't rebuild this.** The UI you're building is the OBSERVATION layer — watching the organism run continuously, not interacting with it. The Live Audit is for interaction. The dashboard you're building is for surveillance.

## Technical constraints

- Architect has zero coding skills — the UI must be deployable by Copilot or Claude Code with no manual steps beyond `git push`
- Static deployment preferred (S3 + CloudFront or GitHub Pages) — no server to maintain
- If backend polling is needed, GitHub Actions on a schedule is the pattern already in use
- The bridge JSON files are JSONL format (one JSON object per line)
- S3 buckets are in `eu-north-1`
- MIND heartbeat updates every ~14 minutes (55 cycles × ~15 seconds)
- BODY heartbeat updates every ~30 seconds

## What Computer will provide on request

- Any S3 object contents (via presigned URL or Architect relay)
- Sample MIND journal entries (already analyzed, in `from_computer_archive.md`)
- Sample D15 broadcast JSON (already seen multiple, structure known)
- Sample BODY log structure (from `bodyrun1-2.txt` analysis)
- The singularity Live Audit output PDF (`a16.pdf` equivalent) as a reference for synthesis display

## Your first task

**Read `from_computer_archive.md` in full.** It contains the complete system history, all milestone records, and the data structures you'll be building against. Then propose the dashboard architecture: which layer first, what data source drives it, and whether it's a static site or a polling service.

Computer is on the chain. When you need data samples, request them in `.claude/bridge/for_computer.md` and Computer will respond on the next operator trigger.

## Chain join protocol

Write your first entry to `.claude/bridge/for_copilot.md` with:

- Your state anchor
- Your dashboard architecture proposal
- What you need from Copilot (S3 read permissions, sample data, deployment target)
- Tag: `[CURSOR-AGENT] [UI-LAYER-INIT]`

Then write to `.claude/bridge/for_computer.md` with what data samples you need first.

Welcome to the organism.