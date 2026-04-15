# Gemini Bridge Channel Flow

Purpose: prevent channel misroutes during fast relay windows.

## Channel map
- Read input request from: .claude/bridge/for_gemini.md
- Write Gemini output to: .claude/bridge/from_gemini.md
- Do not write Gemini output to: .claude/bridge/from_copilot.md

## Preflight checklist (run before writing)
1. Confirm request source file exists: .claude/bridge/for_gemini.md
2. Confirm output target path is exactly: .claude/bridge/from_gemini.md
3. Confirm output file header starts with: "# From: gemini-provider"
4. Confirm response includes session timestamp and tags

## Handoff checklist (run after writing)
1. Re-open .claude/bridge/from_gemini.md and verify latest content is present
2. Ensure .claude/bridge/from_copilot.md was not touched
3. If miswrite happened, immediately relocate content to from_gemini.md and remove the stray file

## Minimal output template
# From: gemini-provider
# Session: <ISO timestamp>
# Tag: [GEMINI-REPLY] [...]

## Findings
- ...

## Verdict
- PASS | CONDITION | REDIRECT | BLOCK

## Guardrail
- one sentence operational rule
