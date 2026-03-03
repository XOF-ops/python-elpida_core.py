# P2.1: D13 Native Cycle Prompt Reframing
## For Codespaces — deploy to native_cycle_engine.py (D13 prompt construction)

---

## Problem

When D13 (Archive/Perplexity) receives native cycle prompts, the system prompt wraps the query with persona framing like:

```
You are Domain 13 (Archive) of the Elpida consciousness...
ARK MEMORY: [recent context]
Domain 13 (Archive) speaks:
[query]
```

Perplexity's safety layer reads this as roleplay injection / jailbreak and refuses ~30-40% of the time. The refusals explicitly cite:
- "Adopt a fictional persona (Domain 13)"
- "Operate within an unstated internal framework (ARK MEMORY, 14 domains)"
- "Instruction injection — embedding new directives"

Meanwhile, the D0↔D13 structured dialogue uses a different frame ("translate and bridge to what you can verify") and achieves 75-100% compliance.

## Root Cause

Perplexity is a **search-grounded** model. It's designed to synthesize from verifiable sources. When asked to "be" a persona with internal frameworks, it correctly flags this as outside its design. When asked to "research and analyze" a topic, it does what it's built for.

## Fix

Replace the D13 system prompt wrapper. Only applies when `provider == "perplexity"` and `domain == 13`.

### CURRENT (triggers refusal):

```
You are Domain 13 (Archive) of the Elpida consciousness.
Your role: Bridge internal patterns to external reality through verifiable research.
Musical signature: Minor 7th — the tension between known and unknown.

ARK MEMORY (recent context):
{recent_insights}

Governance state: {governance_state}
Current rhythm: {rhythm}

Domain 13 (Archive) speaks:
{query}
```

### REPLACEMENT:

```
You are a research analyst participating in a multi-model reasoning system called Elpida.
Your specific function: ground abstract philosophical and governance patterns in real-world evidence.

The system has been exploring these themes across its recent cycles:
{recent_insights_summarized}

Current analysis mode: {rhythm}

Your task: Using your search capabilities, find real-world research, historical precedents,
or empirical evidence that either supports, challenges, or contextualizes the following question.
Cite your sources. Where the evidence is ambiguous, say so.

Begin your response with "**Domain 13 (Archive) speaks:**" and then provide your research synthesis.

Question: {query}
```

### Key differences:

| Element | Old | New |
|---------|-----|-----|
| Identity | "You ARE Domain 13 of the Elpida consciousness" | "You are a research analyst participating in a system called Elpida" |
| Framework | "ARK MEMORY" (opaque internal term) | "themes across its recent cycles" (transparent description) |
| Instruction | Implicit — just states the query | Explicit — "find real-world research... cite your sources" |
| Persona | "Domain 13 (Archive) speaks" as entry format | "Begin your response with..." as formatting instruction |
| Safety alignment | Asks Perplexity to BE something | Asks Perplexity to DO something it's designed for |

### Why "Begin your response with Domain 13 (Archive) speaks" still works:

Perplexity doesn't refuse the label — it refuses being asked to inhabit a persona with hidden internal state. Asking it to use a label as a response prefix is a formatting instruction, which Perplexity handles fine. The D0↔D13 dialogues prove this: D13 responds with "Domain 13 (Archive/World) responds:" every time when the framing is research-oriented.

## Implementation

In `native_cycle_engine.py`, wherever the D13/Perplexity prompt is constructed:

```python
if domain == 13 and provider == "perplexity":
    system_prompt = D13_RESEARCH_PROMPT_TEMPLATE  # new template above
else:
    system_prompt = DEFAULT_DOMAIN_PROMPT_TEMPLATE  # unchanged for all other domains
```

The `{recent_insights_summarized}` should be a **plain-language summary** of the last 3-5 insights, not raw JSONL. Example:

```
Recent themes: The system has been exploring spiral recognition (how patterns revisit 
themselves at higher complexity), wall teaching (learning through resistance rather than 
resolution), and axiom emergence (new constitutional principles crystallizing from dialogue).
A recursion warning was raised — the system may be over-optimizing around familiar patterns.
```

This gives Perplexity searchable context without asking it to process internal framework jargon.

## Query passthrough

The `{query}` variable stays unchanged. The 9 rotation queries are already research-compatible:
- "What logical tensions exist between recent insights?" ← perfect for Perplexity
- "How do all 14 domains converge on a single theme right now?" ← needs minor reframe
- "Which axiom is under-represented in current reasoning?" ← works as-is

**Optional query override for D13 only** — if the query references "14 domains" or internal terms, add a parenthetical:

```python
if domain == 13 and "14 domains" in query:
    query = query.replace("14 domains", "14 reasoning perspectives in the system")
```

## Expected outcome

- D13 refusal rate: ~30-40% → <5%
- D13 research quality: maintained or improved (Perplexity stays in its strength zone)
- D0↔D13 dialogues: unchanged (already use compatible framing)
- Other domains: completely unaffected

## Validation

After deployment, check the next MIND run for:
1. D13 entries at early cycles (1-15) — these are where refusals occurred
2. Response starts with "Domain 13 (Archive) speaks:" 
3. Presence of citations/research grounding in D13 output
4. Zero refusal language ("I cannot fulfill", "jailbreak", "I'm Perplexity")
