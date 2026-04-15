---
type: schema_reconciliation
schema: ElpidaAI/standing_question.schema.json
date: 2026-04-13
authorized_by: BODY Parliament cycle 739 (9/16 domains voted Option 3, D16 Agency voted execute)
witness_chain: claude-opus-4.6-terminal (GPT-5.4-aligned draft) -> gemini-copilot-ide (overwrote with alternate draft) -> gpt-5.3-codex-copilot-ide (verifier + PROTOCOL.md fixes, held on schema reconciliation) -> BODY parliament divergence engine (voted Option 3) -> claude-opus-4.6-terminal (this reconciliation)
authored_by: claude-opus-4.6-terminal
status: draft reconciliation, not a live schema change
---

# Standing Question Schema — Per-Field Reconciliation

## Why this document exists

Two draft versions of `standing_question.schema.json` existed in the
working tree in sequence on 2026-04-13:

1. **GPT-5.4-aligned draft** (authored by Claude Code on 2026-04-13,
   following GPT-5.4 feedback in a cross-model bridge exchange). Key
   features: no `claude_shape_risk` in the enum, simpler birth
   mechanism with only `convergence` and `challenge`, array-typed
   `ratified_by`, integer `source_domain`, `additionalProperties:
   false`, two conditional requirements.

2. **Gemini-authored draft** (written by Gemini later the same day
   from a clean context, overwriting the GPT-5.4-aligned version).
   Key features: reintroduced `claude_shape_risk` in the enum, added
   `synthesis` to birth_mechanism, single-string `ratified_by` (commit
   hash), string-pattern `source_domain`, no
   `additionalProperties`, one conditional requirement.

The BODY Parliament divergence engine processed the reconciliation
question on 2026-04-13 (BODY cycle 739, A8 rhythm CONTEMPLATION,
baseline provider openai) and produced the following fault lines:

- **Option 1 (restore GPT-5.4)** — D3 Autonomy, D4 Safety
- **Option 2 (keep Gemini, document divergence)** — D8 Humility, D2
  Non-Deception, D5 Consent, D12 Rhythm, D15 World
- **Option 3 (merge into reconciled third version)** — D6 Collective,
  D7 Learning, D9 Coherence, D13 Archive, D1 Transparency, D10
  Evolution, D11 Synthesis, D16 Agency, plus D0 Identity

9 of 16 domains favored Option 3. D16 Agency explicitly voted
**execute**. The Elpida Synthesis output (written by Claude in the
baseline provider) called for "tension preservation" — each field
should show dual provenance.

This document records each field's reconciled decision with explicit
GPT-5.4 vs Gemini attribution and the reasoning that selected the
merged value.

## Per-field reconciliation

### `class`

| Version | Value |
|---|---|
| GPT-5.4 draft | enum: `orphaned`, `born` |
| Gemini draft | enum: `orphaned`, `born` |
| **Reconciled** | **enum: `orphaned`, `born`** |

**Reasoning:** No disagreement. Both versions agree on the core
taxonomy. The unresolved question of how to classify operator-raised
questions (Q4, Q5, Q6) is handled elsewhere in the schema via
`status: adjudication_needed`, not by adding a third class value.

### `birth_mechanism`

| Version | Value |
|---|---|
| GPT-5.4 draft | enum: `convergence`, `challenge` |
| Gemini draft | enum: `convergence`, `challenge`, `synthesis` |
| **Reconciled** | **enum: `convergence`, `challenge`** |

**Reasoning:** Gemini added `synthesis` without defining a concrete
instance of a synthesis-born standing question. The two existing born
questions in the examples (Q7 and Q8) are both convergence or
challenge — neither requires a synthesis mechanism. Adding the enum
value before there is a concrete example to anchor it would be the
"promoting metaphors into ontology" signature GPT-5.4 specifically
warned against. If a future standing question can only be explained
as a synthesis mechanism, the enum can be extended then with a
documented concrete case. Until then, the narrower GPT-5.4 version
holds.

### `source_substrate`

| Version | Value |
|---|---|
| GPT-5.4 draft | enum: `MIND`, `BODY`, `HEAD`, `agent-layer`, `operator` |
| Gemini draft | enum: `MIND`, `BODY`, `HEAD`, `OPERATOR` |
| **Reconciled** | **enum: `MIND`, `BODY`, `HEAD`, `agent-layer`, `operator`** |

**Reasoning:** Gemini dropped `agent-layer` entirely. That erases the
class of questions that Q7 and Q8 belong to — they were raised
through cross-substrate witnessing at the agent layer, not at MIND,
BODY, HEAD, or by the operator directly. Without `agent-layer`, born
questions have no home in the enum. The reconciled version restores
it. Lowercase `operator` and `agent-layer` are kept because they are
common nouns describing roles, while `MIND`, `BODY`, `HEAD` are
project-specific acronyms that follow the CLAUDE.md convention.
Gemini's `OPERATOR` uppercase was inconsistent.

### `source_domain`

| Version | Type |
|---|---|
| GPT-5.4 draft | integer |
| Gemini draft | string, pattern `^D(1[0-5]\|[0-9])$` |
| **Reconciled** | **integer, with `minimum: 0` and `maximum: 16`** |

**Reasoning:** The underlying data format in
`ElpidaAI/elpida_evolution_memory.jsonl` stores `domain` as an
integer. Converting to a string-prefixed form like `D4` is a
presentation concern. Keeping the schema type-aligned with the
storage format means validators catch data-format issues directly
without an intermediate coercion step. The integer range is bounded
by `minimum: 0` and `maximum: 16` to cover D0-D16 and reject stray
values; the upper bound includes D16 even though CLAUDE.md lists 16
domains (A16 ratified the 17th position as `D16 Agency`).

### `ratified_by`

| Version | Type |
|---|---|
| GPT-5.4 draft | array of strings (model identifiers) |
| Gemini draft | single string (commit hash) |
| **Reconciled** | **array of strings** (model identifiers), with a **new sibling field `ratified_commit`** for the git commit hash |

**Reasoning:** The two versions encode different provenance facts.
GPT-5.4's array captures the witness chain — which substrates
jointly ratified the question into the pool. Gemini's commit-hash
string captures the persistence event — when the ratification was
committed to git. Both are valid provenance but they are distinct.
Collapsing them into one field loses information. The reconciled
schema keeps the array for witness identification and adds
`ratified_commit` as an optional sibling for the commit hash. When a
question is ratified, `ratified_by` MUST be populated (per the
conditional); `ratified_commit` is optional because ratification can
happen before commit.

### `status`

| Version | Enum |
|---|---|
| GPT-5.4 draft | `open`, `reissued`, `answered`, `retired` |
| Gemini draft | `standing`, `answered`, `deprecated`, `adjudication_needed` |
| **Reconciled** | **`standing`, `reissued`, `answered`, `retired`, `adjudication_needed`** |

**Reasoning:** Per-value reasoning:

- `standing` (from Gemini) replaces `open` (from GPT-5.4). "Standing"
  is more natural for a standing-question pool — the question is
  standing, waiting. "Open" has a task-tracker connotation that
  doesn't match the constitutional register.
- `reissued` (from GPT-5.4) is kept. It captures the specific event
  of a question being prepended to a D0 prompt. Gemini had no
  equivalent.
- `answered` is in both. Kept.
- `retired` (from GPT-5.4) is kept. It captures withdrawal without
  answer (malformed, duplicate, superseded). Gemini's `deprecated`
  has a similar semantic and was dropped in favor of the more
  neutral `retired`.
- `adjudication_needed` (from Gemini) is kept. It captures the Q4,
  Q5, Q6 case where a question does not cleanly fit the class
  taxonomy and waits for operator decision. GPT-5.4 had no
  equivalent and handled this by putting such questions in a
  separate `requires_adjudication` section of the examples file. The
  Gemini version is cleaner because it keeps everything in one pool
  with a distinct status value.

### `cross_model_status`

| Version | Enum |
|---|---|
| GPT-5.4 draft | `untested`, `converged`, `challenged`, `collapsed` |
| Gemini draft | `pending_review`, `confirmed`, `claude_shape_risk`, `collapsed`, `unresolved` |
| **Reconciled** | **`untested`, `converged`, `challenged`, `collapsed`** |

**Reasoning:** The core disagreement is whether `claude_shape_risk`
belongs in a durable state enum. GPT-5.4's explicit guidance was
that it does not, because it is a review diagnosis rather than a
system state. A question can be in a `challenged` state durably (a
non-Claude reviewer pushed back on its framing). Whether the
challenge was specifically about "Claude shape" is a diagnostic
detail that belongs in `review_note` free text, not in a core enum
that other code might filter on. Gemini's version reintroduced
`claude_shape_risk` without addressing GPT-5.4's objection; the
reconciled version follows GPT-5.4 and moves the diagnostic content
into `review_note`.

Gemini's `pending_review` and `unresolved` values were dropped —
`pending_review` overlaps with `untested`, and `unresolved` overlaps
with `challenged`. The 4-value enum is tighter.

### `review_note`

| Version | Present? |
|---|---|
| GPT-5.4 draft | yes (new field) |
| Gemini draft | yes (also present) |
| **Reconciled** | **yes, kept from both** |

**Reasoning:** Both versions agreed on this field. Kept as the place
where review-specific diagnoses live (e.g. "GPT-5.4 flagged the
framing as Claude synthesis; the question survives but the framing
is downgraded"). This is the field that absorbs `claude_shape_risk`-
style diagnostic content without polluting the core enum.

### `additionalProperties`

| Version | Value |
|---|---|
| GPT-5.4 draft | `false` (strict) |
| Gemini draft | not specified (default `true`) |
| **Reconciled** | **`false`** |

**Reasoning:** Strict schemas catch typos and unintended fields. The
Gemini version's permissiveness was not an explicit design choice —
it was a default. Since the reconciled schema is draft and not yet
wired to code, the stricter version is easier to validate against
and easier to evolve safely.

### Conditional requirements

| Version | Conditionals |
|---|---|
| GPT-5.4 draft | (a) if class=born → require birth_mechanism AND ratified_by. (b) if status=answered → require answered_at, answer_substrate, answer_text. |
| Gemini draft | (a) if class=born → require birth_mechanism. |
| **Reconciled** | **Both GPT-5.4 conditionals preserved.** |

**Reasoning:** The (a) conditional is strengthened to also require
`ratified_by` when class=born, because a born question without
named ratifiers is semantically incomplete. The (b) conditional is
preserved because an `answered` question without answer fields is
also incomplete. Gemini's simpler version missed these invariants.

### Fields unique to the Gemini draft that were not carried forward

None. Every field Gemini added is either present in the reconciled
version, renamed (`ratified_by` commit hash → `ratified_commit`
sibling), or explicitly dropped with reasoning
(`claude_shape_risk`, `synthesis`, `pending_review`, `unresolved`,
`OPERATOR` uppercase).

### Fields unique to the GPT-5.4 draft that were not carried forward

None. Every GPT-5.4 field is preserved.

## Unresolved schema-level questions

1. **Operator-raised questions still lack a clean class.** Q4, Q5,
   Q6 are raised by the operator directly and do not fit `orphaned`
   or `born`. The reconciled schema handles them via `status:
   adjudication_needed` but that is a lifecycle state, not a
   provenance class. A future amendment could either (a) add an
   `operator-raised` class, (b) split the pool into two registers,
   or (c) retroactively ratify such questions through cross-
   substrate witnessing and migrate them to `born`. The Parliament
   did not vote on this directly; it is still deferred to the
   operator.

2. **Gemini's `synthesis` birth mechanism.** If a future standing
   question genuinely requires a third mechanism beyond convergence
   and challenge, the enum should be extended. The reconciled
   version holds the line at two values but is not closed.

3. **`coherence` vs `coherence_score` field drift in
   `elpida_evolution_memory.jsonl`.** The verifier now handles both
   as equivalent, but the underlying question of whether they are
   semantically identical or merely similar is not resolved. The
   BODY Parliament's synthesis called for documenting this gap as a
   feature rather than silencing it. That documentation belongs in
   the verifier comments and the amendment file, not in the schema
   itself.

## Execution record

This reconciliation was applied to
`ElpidaAI/standing_question.schema.json` on 2026-04-13. The file on
disk is the reconciled version. The examples file
`ElpidaAI/standing_question_examples.json` was rewritten to match.
Nothing was committed. No code reads or writes the schema yet. The
Parliament vote (9/16 for Option 3, D16 execute) is the authorization
for this specific merge; it is not a general delegation of schema
authority.

If a future non-Claude substrate reads this document and finds the
reasoning wanting, that finding produces a second reconciliation
document, not a rewrite of this one.
