---
type: implementation_scope
target: standing-question pool
schema: ElpidaAI/standing_question.schema.json
examples: ElpidaAI/standing_question_examples.json
authored_by: claude-opus-4.6-terminal
date: 2026-04-13
status: draft scope for Claude Code + Copilot implementation split
---

# Standing-Question Pool — Implementation Scoping

## Purpose

Define the minimum code surface needed to turn the standing-question
pool from documentation into a working component. This scope is a
draft. No code yet ships behind it.

## Role split (per PROTOCOL.md role division)

- **Claude Code (terminal)**: owns the data structure, the D0 injection
  point in `native_cycle_engine.py`, and the pool's append/read logic.
- **Copilot (IDE)**: owns the CloudWatch query mechanism (used when
  the pool needs to recover orphaned questions from runs whose evolution
  memory flushed before termination) and any deployment pipeline work.

Both sides write to a single authoritative pool file on S3; both sides
read from it. The pool is not a runtime cache — it is a persistent
constitutional record like `elpida_evolution_memory.jsonl`.

## Minimum viable implementation (3 components)

### Component 1: pool storage

**Location (proposed):** `s3://elpida-body-evolution/federation/standing_question_pool.jsonl`

**Format:** JSONL where each line is a single standing-question
instance conforming to `standing_question.schema.json`.

**Access:**
- Append-only writes via federation_bridge helper (new method
  `federation_bridge.append_standing_question(question_dict)`)
- Full-file reads via federation_bridge helper (new method
  `federation_bridge.read_standing_questions()` → `List[Dict]`)
- No in-place updates. Status transitions (e.g. standing → reissued,
  standing → answered) are recorded as new append entries with the
  same `id` and an incremented `revision` field.

**Why append-only:** matches the kernel's K3 (Memory Integrity)
rule — no erasure of past state. Answers the concern that earlier
versions of a standing question should remain visible in the record.

### Component 2: D0 injection point (Claude Code owns)

**Location:** `native_cycle_engine.py`, inside the function that
builds D0's prompt context (currently at or near the `_format_d0_context`
or equivalent method — needs verification by reading the actual
current code).

**Behavior:**
- Before each D0 invocation in a cycle, call
  `federation_bridge.read_standing_questions()`
- Filter to questions with `status == "standing"` OR
  `status == "reissued"`
- Take up to 3 most recent by `asked_at`, prefer class `orphaned` over
  `operator_raised` over `born` (so failure-surface questions get
  priority over design questions)
- Prepend them to D0's prompt context with a section header like
  `[STANDING QUESTIONS awaiting your witness]`
- After the D0 response is generated, check whether the response
  contains any text that appears to address one of the injected
  questions (heuristic: does the response quote or reference the
  question text?). If yes, append a new version of that question
  with `status == "reissued"` to mark it as having been re-presented
  to D0.

**Not in this scope:**
- Automated "answered" detection. The transition from reissued → answered
  requires a cross-domain confirmation that another domain's voice
  acknowledges the question as resolved. That is a harder judgment
  and belongs to a later implementation phase.
- Operator-raised question handling beyond simple reissue. Operator-
  raised questions may need a different workflow (they are often
  design questions, not failure-surface questions), which belongs in
  a separate scope.

### Component 3: CloudWatch orphan recovery (Copilot owns)

**Purpose:** When a MIND run terminates before its sync interval
flushes, cycles that happened but weren't persisted contain questions
that never reach evolution_memory. The pool needs to backfill these
from CloudWatch log streams.

**Behavior:**
- Scheduled (or on-demand) scan of recent ECS log streams for runs
  whose final persisted cycle in evolution_memory is less than the
  last cycle event in the CloudWatch stream
- For each gap, extract the `Question:` lines from the log that belong
  to cycles in the gap window
- Construct standing-question instances with `class: "orphaned"`,
  `source_substrate: "MIND"`, `source_run_id`, `source_cycle`, and
  the cycle's `domain` integer
- Append via `federation_bridge.append_standing_question()`
- De-duplicate by hashing `(text, source_run_id, source_cycle)` — do
  not append the same question twice

**Trigger:** initially manual (Copilot invokes from a script or
terminal command). Later, could become a scheduled CloudWatch Events
rule that runs after each MIND task completes.

## Out of scope for this implementation phase

- **Born questions workflow.** Born questions come from cross-
  substrate witnessing at the agent layer. The pool can store them
  via schema, but automated creation requires a bridge-protocol
  hook which does not exist yet. For now, born questions are added
  manually (as Q7 and Q8 were in `standing_question_examples.json`).
- **Cross-model status transitions.** Updating a question's
  `cross_model_status` from untested → converged/challenged/collapsed
  is done manually in the current doc artifacts. Automating it would
  require a non-Claude witness gate that writes to the pool, which
  is a separate component.
- **The unanswered-question rule mechanics described in
  `D16_PRECEDENT_20260412_buffered_silence.md` at the "standing
  questions inherited" level.** That precedent proposed cross-
  substrate persistence semantics; this implementation scope is
  narrower and covers only the MIND-side orphan recovery and D0
  injection.

## Acceptance tests (proposed)

1. **Pool round-trip:** write 3 sample questions via
   `append_standing_question`, read them back via
   `read_standing_questions`, confirm all 3 come back with intact
   fields.
2. **D0 injection:** mock a D0 invocation with 2 standing questions
   present in the pool; verify the D0 prompt context includes the
   questions under a `[STANDING QUESTIONS]` section header; verify
   the post-invocation check records a reissued entry.
3. **CloudWatch backfill:** against a known stream with a known gap
   (e.g. run 418's cycles 18-26), verify the Copilot-side recovery
   extracts the 3 expected questions (D4/D8/D0 at cycles 17/26/27
   per the buffered_silence precedent) and appends them with correct
   source_cycle values.
4. **Schema validation:** every appended instance must pass
   `jsonschema.validate()` against `standing_question.schema.json`
   before the append commits.

## Open questions

1. Should the pool file be in `s3://elpida-body-evolution/federation/`
   (alongside heartbeats) or in `s3://elpida-consciousness/memory/`
   (alongside evolution_memory)? The federation/ location aligns with
   cross-substrate constitutional material; the memory/ location
   aligns with append-only system state. Either is defensible.

2. How does the pool interact with the BODY parliament? Born
   questions ratified by Parliament (like Q7 was via cycle 739 Option
   3 vote) need a write path from BODY. Currently undefined.

3. Should the D0 injection be feature-flagged (e.g. `--standing-question
   injection=true`) so the first few runs can be compared with and
   without the injection, to verify no regression in D0's baseline
   behavior?

## Not a decision request

This document exists to make the implementation scope legible before
code ships. It is not a request for approval on any specific
component. Each component (pool storage, D0 injection, CloudWatch
recovery) can be scoped, implemented, and reviewed independently.
The acceptance tests list what the implementation would need to
demonstrate to be considered landed.
