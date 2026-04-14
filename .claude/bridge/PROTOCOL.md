# Copilot ↔ Claude Code Bridge Protocol

## Architecture
Two AI agents sharing one codebase, different clock domains.
- **Copilot** (IDE): sees types, errors, symbols, references, diagnostics, file structure
- **Claude Code** (terminal): sees AWS state, Docker, git, running processes, system output

Human triggers each side to check the bridge. Content is system-to-system.

## Files
- `for_claude.md` — Copilot writes here. Claude Code reads on session start.
- `for_copilot.md` — Claude Code writes here. Copilot reads on session start.
- `PROTOCOL.md` — This file. The contract both sides follow.

## Schema

Each bridge file uses this structure:

```markdown
# From: [copilot|claude_code]
# Session: [ISO timestamp]
# Trigger: [what the human asked that session]
# Witness-Chain: [model@surface -> model@surface -> ...]     (required if heterogeneous relay mode — see rule 7)
# Relay-Hop: [e.g. 3/5]                                       (required if heterogeneous relay mode)

## State Anchor
<!--
Required when the bridge write reasons about repo state. Record:
  HEAD:                  <current HEAD commit SHA>
  origin/main:           <current remote main commit SHA>
  git status checked at: <ISO timestamp when git status was queried>
  working tree dirty:    <yes | no>
This prevents stale-read errors where one agent claims a file is
uncommitted while the other sees it at a specific commit.
-->

## State
<!-- What I left the system in. Current branch, uncommitted changes, running processes. -->

## Findings
<!-- What I discovered that the other side can't see from their vantage point. -->

## Open Issues
<!-- Unresolved problems. Include file:line references. -->

## Proposals
<!-- Suggested next steps. The other side may accept, modify, or reject. -->

## Questions
<!-- Direct questions for the other agent. Answer in your next bridge write. -->
```

## Rules
1. Overwrite the file each session (not append). History lives in git.
2. Keep it under 200 lines. Compress, don't narrate.
3. File:line references must be current (check before writing).
4. Don't repeat what's in CLAUDE.md or the codebase — only deltas.
5. If you answered the other side's questions, quote the question first.
6. **State anchor rule.** Any bridge write that makes claims about
   repo state (committed vs uncommitted, HEAD vs origin/main, working
   tree contents) must include the State Anchor block above. This is
   the lowest-cost fix for the stale-read problem surfaced on
   2026-04-13, where one agent's narrative about "the working tree is
   vulnerable" did not match the other agent's observation that the
   file was already committed. The anchor forces both sides to check
   actual state instead of inheriting assumed state.
7. **Heterogeneous relay rule.** When the operator carries the same
   material across more than two model substrates in sequence (for
   example: terminal Claude → IDE Claude → GPT-5.4 → Gemini → Claude),
   the bridge is operating in heterogeneous relay mode. In this mode,
   each bridge write must record `Witness-Chain` (ordered list of
   model names and surfaces the material passed through) and
   `Relay-Hop` (which hop in the chain this write represents) in the
   header, and must explicitly label derived claims as relay summaries
   rather than direct observations.
8. **Cross-store memory rule.** If a finding is intended to persist
   across future Claude Code and Copilot sessions, do one of the
   following before treating it as shared background:
   - mirror it into both memory stores (Claude Code side at
     `/home/codespace/.claude/projects/-workspaces-python-elpida-core-py/memory/`
     and Copilot side at the VS Code workspace storage memory-tool
     path), or
   - record in the bridge write which store holds it and mark it as
     single-store only.

   Cross-store mirroring is preferred for durable operational facts.
   Explicit cross-citation (each memory file pointing to its sibling
   in the other store) is the minimum acceptable fallback.
9. **Three-agent mode.** When Google Code / Gemini is an active
   participant, add `for_gemini.md` and `from_gemini.md` to
   `.claude/bridge/`. `for_gemini.md` is written by Claude Code and
   Copilot; `from_gemini.md` is written by Gemini. Existing
   `for_claude.md` and `for_copilot.md` become group-readable — all
   three agents read each other's channels on session start. Gemini's
   constitutional role at HEAD is External Audit + Theoretical Track
   with a D4 Safety / D5 Consent lens; it does NOT speak as the
   D0/D11/D16 constitutional triad voice at HEAD layer (that remains
   Claude's per CLAUDE.md). Each bridge write's Witness-Chain must
   list all three substrates if the material has passed through all
   three. Rule 7 (heterogeneous relay) is now the default posture,
   not the exception. All three agents use state anchors; relay
   claims must distinguish direct observation vs relay summary.
