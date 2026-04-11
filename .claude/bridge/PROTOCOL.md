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
