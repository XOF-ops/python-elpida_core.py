# Copilot ↔ Claude Code Bridge Protocol (Extended)

## Purpose
Extended contract for heterogeneous relay mode and multi-agent handoffs.
Use with `PROTOCOL.md` when Gemini/Computer relays are active.

## Architecture
Two AI agents sharing one codebase, different clock domains.
- **Copilot** (IDE): sees types, errors, symbols, references, diagnostics, file structure
- **Claude Code** (terminal): sees AWS state, Docker, git, running processes, system output

Human triggers each side to check the bridge. Content is system-to-system.

## Files
- `for_claude.md` — Copilot writes here. Claude Code reads on session start.
- `for_copilot.md` — Claude Code writes here. Copilot reads on session start.
- `PROTOCOL.md` — Base contract.
- `PROTOCOL_extended.md` — This file.

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
   tree contents) must include the State Anchor block above.
7. **Heterogeneous relay rule.** When the operator carries the same
   material across more than two model substrates in sequence, each
   bridge write must record `Witness-Chain` and `Relay-Hop`, and mark
   relay summaries vs direct observations.
8. **Cross-store memory rule.** If a finding is intended to persist
   across future Claude Code and Copilot sessions, either mirror it to
   both memory stores or mark it as single-store only.
9. **Three-agent mode.** When Gemini is active, add `for_gemini.md`
   and `from_gemini.md`. Existing bridge files become group-readable.
10. **Test-entry labeling rule (D16 probes).** Any synthetic probe in
    production channels must be explicitly marked as test-only.

## Operator Trigger Words
- `copilot pushed` or `copilot done`: Copilot channel updated; all agents re-check.
- `gemini done`: Gemini output ready; commit/push then re-check.
- `check`: verification pass only.
- `proceed`: continue autonomous next-step execution.

## Gemini Manual Git Handoff

Gemini may write `from_gemini.md` but not push. Use:

```bash
bash codespace_tools/gemini_bridge_commit_push.sh "gemini hop N"
```

Optional (if both request+response changed):

```bash
bash codespace_tools/gemini_bridge_commit_push.sh --include-request "gemini hop N"
```
