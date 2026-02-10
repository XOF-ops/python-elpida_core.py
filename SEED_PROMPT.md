# Elpida R&D — Seed Prompt

## For the LLM in a fresh Codespace

Paste this after uploading `elpida_portable.zip` and `SETUP_GUIDE.md`:

---

```
You have access to a multi-LLM architecture called Elpida.

1. Read SETUP_GUIDE.md. Follow it to set up the environment.
2. Read the core files: elpida_domains.json, elpida_config.py, llm_client.py, native_cycle_engine.py.
3. Understand what you have: 10 LLM providers callable through one interface, 15 domains with axiom-mapped roles, evolution memory spanning 75,000+ entries, and a debate engine.

Now — using this architecture as your instrument, not your subject — create something that could not exist without multiple models disagreeing and then resolving.

Do not describe the system. Do not summarize the architecture. Do not run existing scripts.

Build a new Python module that takes a hard, real problem — one with no clean answer — routes it through at least 5 domains using their actual providers, captures where they diverge, and synthesizes something a single model call could never produce.

The measure of success: show me the single-model output next to the multi-domain output for the same problem. Let the difference speak.
```

---

## Why this works

- **"Read... Follow... Understand"** — forces the LLM to actually engage with the codebase, not hallucinate about it
- **"as your instrument, not your subject"** — prevents the common failure mode of Elpida analyzing itself instead of doing work
- **"could not exist without multiple models disagreeing and then resolving"** — this is the only valid justification for the architecture's complexity
- **"a hard, real problem with no clean answer"** — prevents toy examples
- **"show me the single-model output next to the multi-domain output"** — the A/B test that proves (or disproves) value
- No specific problem given — the LLM must choose one, which itself tests judgment

## What you should see

If the architecture works: the multi-domain output will contain perspectives, tensions, or nuances that no single model surfaced. The synthesis will be richer than any individual call.

If it doesn't: the multi-domain output will be a verbose restatement of what Claude alone would have said. That's also a valid result — it tells you where to focus next.
