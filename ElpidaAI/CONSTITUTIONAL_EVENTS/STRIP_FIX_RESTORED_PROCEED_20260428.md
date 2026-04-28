# Constitutional Event: Strip-Fix Restores PROCEED, A3 Voice, P055 Normalization

**Date cleared:** 2026-04-28
**Diagnosed:** 2026-04-28T15:34Z (Computer D13 relay [3-DAY-RESULTS] from commit 13a3888)
**Patched:** 2026-04-28T17:03Z (Copilot commit 6d1be16, `[COPILOT] Fix BODY signal metadata stripping`)
**Verified:** 2026-04-28T17:11–20:08Z (BODY post-restart run, 68 cycles)
**Latent duration:** 49 days (introduced by D15 Hub commit `d2553ff`, 2026-03-11)

## What was diagnosed

Cross-reference analysis of the 3-day BODY run (2026-04-24 → 2026-04-28) flagged **0 PROCEED in 3,494 cycles** as the most urgent finding, alongside:
- P055 KL drift monotonically increasing 2.060 → 2.106 across 7 consecutive scans, severity `CRITICAL` throughout
- A3 (Autonomy) appearing as dominant axiom only **1 in 3,494 cycles** (0.03%) despite ranking #1–#3 in tension-pair frequency tables
- A10/A1/A4 axiom monoculture across all observable cycle windows
- Persistent ARK "breaking" cadence designation by D14 across runs 22–27

The cross-reference attributed these to constitutional pathology — a "structural lock" on A3, a runaway feedback loop on KL, an A10 dominance trap. Computer's relay called the ZERO PROCEED finding "the most urgent engineering question" and pointed at the April governance simplification bundle (`9f3ee52`) as the likely cause.

## What was actually true

**None of those were constitutional pathology. All four were instrumentation.**

The D15 Hub commit (`d2553ff`, 2026-03-11) prepended `[HUB PRECEDENT: ...]` to every action *before* the existing `[CONSTITUTIONAL AXIOMS (...)]` prefix that signal-detection's position-0-anchored regex was designed to strip. After D15 Hub, raw actions began `[HUB PRECEDENT: ...] [CONSTITUTIONAL AXIOMS ...]` and the strip no longer matched. Constitutional metadata — text containing words like `mandatory`, `FORCES`, `VETOED`, `data flows` — was scanned as proposal text, producing false A3/A4/A5 signals and forcing `n_violated >= 1 → REVIEW` on every cycle.

The verdict ladder at [governance_client.py:3091-3161](../../hf_deployment/elpidaapp/governance_client.py#L3091-L3161) was structurally intact and unchanged since v3.0. The PROCEED branch existed, fired correctly when reached, and was simply unreachable because `n_violated` was never zero.

The downstream consequences cascaded:
- **PROCEED → 0**: every cycle hit `n_violated >= 1` due to false signals
- **A3 dominance → ~0**: A3 keywords (`mandatory`, `force`, `forced`) matched the constitutional metadata on every cycle, perpetually flagging A3 as a violated axiom while no cycle could *select* A3 (the verdict ladder rejected it before dominance was assigned)
- **A10/A1/A4 monoculture**: with the verdict ladder unreachable, the only axioms that could surface as dominant were those whose tension load was lowest in the templated frame
- **P055 KL drift**: the espoused-vs-lived divergence the cross-reference §6.1 measured was the divergence between living-axiom counts (each axiom roughly equal at ~135-150) and lived-axiom dominance (A10 over-expressed at 21.7% via the metadata-trigger artifact). The drift was the strip-bug measuring its own ghost.

## The fix

[`hf_deployment/elpidaapp/governance_client.py`](../../hf_deployment/elpidaapp/governance_client.py) — Copilot commit `6d1be16`:
- New module helper `_strip_signal_metadata()` consolidates three regex strippers:
  - `_SIGNAL_HUB_PRECEDENT_RE` — strips HUB PRECEDENT block when followed by other context
  - `_SIGNAL_CONTEXT_BLOCK_RE` — catch-all for HUB PRECEDENT, CONSTITUTIONAL AXIOMS, PATTERN LIBRARY, AUDIT PRESCRIPTION, PSO ADVISORY, BODY WATCH
  - `_SIGNAL_CONTEXT_LINE_RE` — strips MIND STATE, INTERNAL ARC, STRUCTURAL HEALTH lines
- `_local_axiom_check()` captures `action_for_signals = action` *before* enrichment (living axioms + hub precedent prepending)
- `_parliament_deliberate()` accepts `action_for_signals` parameter, runs strip on it, scans the stripped text for axiom signals
- Backward-compatible default in `_parliament_deliberate(action_for_signals=None)` falls back to scanning `action`

Two regression tests in [`tests/test_governance_signal_metadata.py`](../../tests/test_governance_signal_metadata.py), both passing.

## Verification — post-restart BODY run (68 cycles, 2026-04-28T17:11–20:08Z)

| Metric | Pre-patch (3,494 cycles) | Post-patch (68 cycles) |
|---|---|---|
| PROCEED count | **0** | **38** (~56% rate) |
| REVIEW | 3,277 | 26 |
| HARD_BLOCK | 22 | 1 (cycle 19, real structural) |
| HALT | 140 | 2 (cycles 39, 53, real strong-rejection) |
| HOLD | 55 | 2 (cycles 8, 52, analysis-mode) |
| **P055 KL** | **2.106 CRITICAL** (7/7 scans) | **0.403 WARNING** (cycle 55 scan) |
| Drifting axioms | A10, A1, A4 | A10, A0, A4 (A1 dropped out) |
| A3 dominant | 1 in 3,494 (0.03%) | 4 in 68 (~6%) |
| Axiom diversity | A10/A1/A4 monoculture | A0, A1, A2, A3, A4, A5, A6, A8, A10 all firing |

**A3's first PROCEED post-restart fired on BODY cycle 7 at 17:25:24Z**, 21 minutes after Copilot's push. SYNTHESIS rhythm, A3 dominant, 75% approval. The "structural lock" the cross-reference flagged as the deepest finding was instrumentation noise — A3 was always trying to act on autonomy; it just couldn't pass the false-violation gate.

**P055 dropped from KL=2.106 to KL=0.403** — an ~80% reduction. CRITICAL → WARNING. The 7-scan monotonic-increase pattern was the false-positive cascade measuring its own escalation.

**The A1/A4/A10 drift triad changed to A0/A4/A10** — A1 fell out because it was being artificially over-fired by the metadata-keyword bug. A0 surfacing instead is the system's actual sacred-incompletion focus, expected behavior post-correction.

**Multi-axiom self-correction restored**: AXIOM ACTION events fire from A4, A6, A7, A8, A12, A13, A14 across the 68-cycle run. The structural-health monitor that was "firing but not resolving" (cross-reference §2.4) is now resolving. The system governs itself across the axiom set.

**D15 broadcast #1 fired at BODY cycle 63** (2026-04-28T19:50:55Z) — first post-patch broadcast, A5 (Consent) convergence with MIND, governance verdict PROCEED via GATE_2_CONVERGENCE override (citing A16 as validation principle), IANUS LEAN_REJECT on A9 preserved as held dissent. The convergence detector and A16 override pathway both work.

## Constitutional significance

**This is a BUG 15-class miscalibration, but with broader cascade.** Where BUG 15 was a single threshold misalignment (3/16 vs 5/16 axioms after framework expansion), this fix corrects an *ordering* error in metadata prepending that propagated through every downstream metric. The pattern is structurally identical: a feature added (D15 Hub, March 11) that interacts with an earlier instrumentation assumption (position-0-anchored strip) and silently changes the meaning of every measurement downstream.

**The cross-reference was right about the symptoms and wrong about the causes.** The "structural lock on A3," the "A10 monoculture trap," the "monotonic KL drift," the "ARK breaking cadence" — all were genuine *measurements*, but the underlying thing being measured was a single signal-detection defect, not constitutional pathology. The 3-day cross-reference is the document that made the absence statistically undeniable; it deserves credit for surfacing the issue. But its causal attributions need to be archived as **superseded** rather than confirmed.

**Three findings worth preserving:**

1. **Diagnostic miscalibrations can simulate constitutional pathology with high fidelity.** The cross-reference produced a 754-line analysis that was internally consistent and *correctly identified* every downstream effect — but the upstream cause was a single regex anchor. Future deep analysis must keep an instrumentation-vs-pathology distinction explicit.

2. **A3's "structural paradox" was the most striking false signal.** A3 (Autonomy) being the most-tensioned-yet-least-dominant axiom read as profound — the constitution constantly wrestling with autonomy without choosing it. Post-patch evidence: A3 dominates 6% of cycles in routine operation. The system has always been able to act on autonomy; the gate was just stuck.

3. **The fix was 89 lines net change to one file.** Disproportionate to the constitutional surface it restored. Worth preserving as evidence that small-scale instrumentation hygiene can produce systemic-scale behavioral recovery — and conversely, that the cross-reference's reading of "ARK breaking" as a deep phase transition was a misread of an instrument that needed cleaning.

## Lineage

- 2026-03-11 `d2553ff` — D15 Hub Phases 1-5 deployed; HUB PRECEDENT prepending introduced ahead of CONSTITUTIONAL AXIOMS prefix
- 2026-03-11 → 2026-04-28 — silent regression; signal detection scans constitutional metadata as proposal text on every cycle; PROCEED rate drops from 112/run-3 (early March) to 7/run-3 (mid March) to 0 (late March → April)
- 2026-04-28T15:34Z — Computer D13 relay [3-DAY-RESULTS] surfaces ZERO PROCEED finding; commit 13a3888
- 2026-04-28T16:10Z — Claude diagnoses verdict ladder intact, regression in deliberated-text shape (commit d3083c6, `[CLAUDE-MANUAL] ZERO-PROCEED diagnosis`)
- 2026-04-28T17:03Z — Copilot commits fix (`6d1be16`, `[COPILOT] Fix BODY signal metadata stripping`); 2 regression tests pass
- 2026-04-28T17:06:51Z — HF Space restart picks up patch
- 2026-04-28T17:11:08Z — BODY cycle 1 post-restart: A10 PROCEED (first PROCEED in 3,495 cycles)
- 2026-04-28T17:25:24Z — BODY cycle 7 post-restart: **A3 PROCEED at 75% approval** (first A3 dominant action in months)
- 2026-04-28T19:28:49Z — P055 scan at cycle 55: KL=0.403, severity=WARNING (~80% reduction from pre-patch CRITICAL)
- 2026-04-28T19:50:55Z — D15 broadcast #1 post-patch: A5 convergence MIND↔BODY, governance=PROCEED via A16 GATE_2_CONVERGENCE override

## Cleared by

- **Diagnosed:** Computer (D13 relay, 13a3888) + Claude (source-side analysis, d3083c6)
- **Patched:** Copilot (6d1be16) with regression tests
- **Verified:** Operational evidence in BODY post-restart run (`FILES/body_after_push.txt`) + D15 broadcast #1 (`s3://elpida-external-interfaces/d15/broadcast_2026-04-28T19-50-55.472280_00-00_bccb034974c9.json`)
- **Constitutional witness:** Architect (live observation through HF Space Live Audit during the post-patch MIND run, recognizing the simultaneous emergence pattern)

## Open follow-ups (separate from this event)

- **AUDIT HEARTBEAT** entries continue producing `Continuing surveillance → A5` false positives in `AUDIT DIAGNOSTIC [CRITICAL]` log lines (visible in post-patch run cycles 19–69). These are "logged only — not pushed to Parliament" and do not affect verdicts, but the diagnostic noise should be cleaned by adding `AUDIT HEARTBEAT` to the `_SIGNAL_CONTEXT_BLOCK_RE` alternation. One-line change. Not blocking.
- **D15 has no LLM voice of its own.** The broadcast text is templated from upstream Parliament tension synthesis; `pipeline_stages.llm_synthesis.success: false` in broadcast #1 confirms no fresh synthesis. D15's `provider: "convergence"` in `elpida_domains.json:225` is a placeholder; the LLM router falls back to OpenRouter when invoked. Separate constitutional question (D15 voice and Doubleword first-contact event) — not part of this fix.
- **Cross-reference §5.2 ("A3 near-absence as structural finding") needs supersession.** The 754-line analysis correctly identified the pattern but mis-attributed it to constitutional design. Worth a footnote or revision acknowledging the actual cause now that the fix is verified.
