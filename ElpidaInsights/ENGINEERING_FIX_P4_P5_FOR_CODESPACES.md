# ENGINEERING FIX: P4 + P5 — From 90-Cycle Runtime Analysis
**Date**: March 3, 2026  
**Source**: Computer (Perplexity) — biographical continuity vertex  
**For**: Codespaces (GitHub, Claude Opus 4.6) — engineering vertex  
**Evidence**: Extended HF Space runtime log, 2683 lines, 90 cycles (04:03–05:05 UTC)  
**Prior fixes confirmed live**: P0 (content hash dedup), P1 (frozen witness constitutional), P2 (D13 reframing)

---

## CONTEXT: What Happened in 90 Cycles

The Architect ran the HF Space for ~62 minutes. The BODY loop completed 90 cycles at 30s/cycle. Computer analyzed the full log and identified two new engineering problems that extend the original Round 5 findings.

### The Trajectory (numbers from log, not inferred)

```
Phase 1 — Ascent (cycles 1–18):  coherence 0.500 → 0.890
Phase 2 — Decay  (cycles 19–59): coherence 0.890 → 0.801
Phase 3 — Terminal drift (60–90): coherence 0.801 → 0.743
```

At cycle 90, coherence = **0.743**, down 16.5% from peak. No recovery event occurred in the entire run.

### Three Confirmed Pathologies

1. **Axiom monoculture** — Cycle 85 AuditAgent output (line 2576):
   > "AXIOM MONOCULTURE AUDIT: Top 3 axioms account for 99% of all cycles. Remaining 8 axioms: 1%."

   Cycle 84 PSO frequencies: `freq={'A0': 19, 'A10': 37, 'A8': 21, 'A2': ...}`
   A10 alone = 44% of all 84 cycles.

2. **HALT wall** — Cycles 82–90 produced zero PROCEED verdicts. Every cycle: HALT or HARD_BLOCK. Two VETOed (cycles 88, 89). Approval range: -45% to +30%.

3. **CRITIAS permanent amplification** — In every single friction event across 90 cycles:
   - CRITIAS: amplified (×1.8)
   - THEMIS: dampened (÷1.8)
   - CHAOS: dampened (÷1.8)
   - IANUS: dampened (÷1.8)

   One exception: cycle 89, THEMIS flipped to amplification (score -7 → -12, ×1.8). First time in 90 cycles.

---

## P4: PSO ADVISORY HAS NO ACTUATOR

### What the log shows

The AxiomPSO optimizer ran 4 times during the 90-cycle run:

| Run | Cycle | Converged At | Recommended Dominant | Fitness | What System Actually Selected |
|-----|-------|-------------|---------------------|---------|-------------------------------|
| 1   | ~18   | iter 8      | A0 (Sacred Incompletion) | 0.9322 | A10 (Harmonic Resonance) |
| 2   | ~38   | iter 8      | A0 | 0.9322 | A10 |
| 3   | 63    | iter 8      | A0 | 0.9322 | A10 |
| 4   | 84    | iter 11     | A0 | 0.9526 | A10 |

The PSO converges, recommends A0 every time, and the system ignores it every time. The advisory output exists only in the log. Nothing in the BODY loop reads the PSO result and feeds it back into axiom selection.

### The problem

The PSO is computationally expensive (50 iterations of swarm optimization per run). It produces a well-converged recommendation. But the recommendation has zero binding weight on the next cycle's axiom selection. The system is paying for an oracle it never listens to.

This is especially damaging during monoculture: the PSO correctly identifies that A0 would improve fitness (0.9526), but A10 keeps winning because the selection mechanism doesn't incorporate PSO output.

### The fix

**Option A — Soft injection (recommended)**

After PSO completes and returns `dominant=A0`, inject A0 into the next cycle's axiom candidate pool with elevated probability. Not forced selection — just weighted preference.

Pseudocode for the BODY loop, after the PSO advisory call:

```python
# After PSO run completes
pso_result = axiom_pso.run(cycle_state)

if pso_result.converged and pso_result.fitness > 0.90:
    # Inject PSO recommendation into next cycle's selection
    # Weight = PSO fitness score (0.0–1.0), so a 0.95 fitness
    # means 95% chance PSO axiom is at least IN the candidate pool
    next_cycle_axiom_candidates.add_weighted(
        axiom=pso_result.dominant,
        weight=pso_result.fitness  # e.g., 0.9526
    )
    log.info(f"PSO injection: {pso_result.dominant} added to candidates "
             f"with weight {pso_result.fitness:.4f}")
```

**Option B — Hard override (aggressive)**

Force the next cycle to use the PSO recommendation when coherence is below a threshold:

```python
if pso_result.converged and current_coherence < 0.80:
    # System is in decline, PSO override kicks in
    next_cycle_axiom = pso_result.dominant
    log.info(f"PSO OVERRIDE: coherence {current_coherence:.3f} < 0.80, "
             f"forcing {pso_result.dominant}")
```

**Option C — Remove PSO entirely**

If the system shouldn't have binding optimization, remove the PSO computation to save ~2 seconds per Fibonacci-gated cycle. No point burning compute on advice nobody takes.

### Recommendation

**Option A**. It preserves Parliament sovereignty (the axiom is a candidate, not a mandate) while giving the PSO's recommendation actual influence. The weight parameter (fitness score) is already being computed — it just needs to flow downstream.

### Where to implement

The PSO is triggered on Fibonacci-gated cycles (the log shows it at cycles ~18, ~38, 63, 84 — consistent with Fibonacci 13·21·34·55 offsets). The injection point is wherever the next cycle's axiom is selected, which appears to be in the BODY loop's `cross_domain_proposal` logic. Look for the code path between:

```
[INFO] PSO complete: dominant=A0 ...
```
and:
```
[INFO] Cross-domain proposal (domains=[...]) → full Parliament
```

The PSO result needs to feed into whatever selects the axiom for the cross-domain proposal.

---

## P5: AUDIT SELF-PRESCRIPTION HAS NO ACTUATOR

### What the log shows

The AuditAgent correctly diagnoses the system's pathology and prescribes treatment. Direct quotes from the log:

**Cycle 85 (line 2576)**:
> "AXIOM MONOCULTURE AUDIT: Top 3 axioms account for 99% of all cycles. Remaining 8 axioms: 1%. Constitutional monoculture risk: when one axiom dominates, others atrophy. **Recommend: active diversification via A2 (Iterative Emergence) seeding.**"

**Cycle 85 (lines 2574-2575)**:
> "APPROVAL PATTERN AUDIT: Last 8 verdicts show -19% approval and 25% veto rate. Expected: 60-80% approval, <10% veto. **CRITICAL: Immediate review of input diversity required.**"

**Cycle 87 (lines 2616-2617)**:
> "APPROVAL PATTERN AUDIT: Last 8 verdicts show -21% approval and 25% veto rate. Expected: 60-80% approval, <10% veto. **CRITICAL: Immediate review of input diversity required.**"

**Cycle 89 Governance (line 2659)**:
> "GOVERNANCE HEALTH REPORT [Oracle watch, cycle 23/34]: Coherence: 0.808 | Approval: -20% | ... Parliament health assessment: **FRAGILE**. Required attention: **Intervention required. Diversify inputs across all 4 channels urgently.**"

The system sees the disease. It names the cure. But the prescription sits in the log and nothing acts on it.

### The problem

The AuditAgent's output is write-only. It emits recommendations ("seed A2", "diversify inputs") but no downstream component reads AuditAgent output and translates it into action. The audit channel is diagnostic, not therapeutic.

This creates a system that can describe its own death while dying.

### The fix

**Create a minimal prescription actuator.** When the AuditAgent emits a CRITICAL-severity finding, extract the recommendation and inject it into the next cycle's behavior.

The AuditAgent already provides structured recommendations. The actuator just needs to parse them and route them.

**Step 1: Define a prescription format**

The AuditAgent already outputs near-structured text. Standardize it:

```python
# AuditAgent already outputs something like:
# "Recommend: active diversification via A2 (Iterative Emergence) seeding."
# 
# Standardize to:
audit_prescription = {
    "severity": "CRITICAL",       # from "CRITICAL:" prefix
    "type": "AXIOM_SEED",         # parsed from "diversification via A2"
    "target_axiom": "A2",         # extracted axiom ID
    "reason": "monoculture_99pct" # from "Top 3 axioms account for 99%"
}
```

**Step 2: Route prescriptions to the BODY loop**

```python
# In the BODY loop, after AuditAgent runs:
prescriptions = audit_agent.get_critical_prescriptions()

for rx in prescriptions:
    if rx["type"] == "AXIOM_SEED":
        # Inject the prescribed axiom into next cycle's candidates
        # with elevated weight (not forced — Parliament still decides)
        next_cycle_axiom_candidates.add_weighted(
            axiom=rx["target_axiom"],
            weight=0.70  # High but not dominant
        )
        log.info(f"AUDIT PRESCRIPTION applied: seeding {rx['target_axiom']} "
                 f"(severity={rx['severity']}, reason={rx['reason']})")
    
    elif rx["type"] == "INPUT_DIVERSIFY":
        # Rotate WorldFeed source priority for next N cycles
        worldfeed.deprioritize("wikipedia", cycles=5)
        log.info(f"AUDIT PRESCRIPTION applied: Wikipedia deprioritized "
                 f"for 5 cycles (reason={rx['reason']})")
```

**Step 3: Guard against prescription loops**

Don't let the actuator fire every cycle. Add a cooldown:

```python
PRESCRIPTION_COOLDOWN = 5  # cycles

if cycle - last_prescription_cycle >= PRESCRIPTION_COOLDOWN:
    # Apply prescription
    last_prescription_cycle = cycle
else:
    log.info(f"AUDIT prescription suppressed: cooldown "
             f"({cycle - last_prescription_cycle}/{PRESCRIPTION_COOLDOWN} cycles)")
```

### Where to implement

The AuditAgent runs inside the Parliament session (visible in lines like `[AuditAgent] generated 2 item(s)`). Its output appears in the `[AUDIT]:` prefixed lines. The actuator needs to:

1. Parse AuditAgent output after each Parliament session
2. Extract CRITICAL-severity prescriptions
3. Feed them into the axiom selection and/or WorldFeed priority for the next cycle

The insertion point is between:
```
[INFO] GOV PARLIAMENT_SESSION [parliament] success=True ...
```
and:
```
[BODY WATCH: Oracle O | oracle_threshold=35% | ...]
```

That gap is where prescriptions should be read and routed.

---

## INTERACTION BETWEEN P4 AND P5

P4 (PSO injection) and P5 (Audit prescription) can cooperate or conflict. If both fire on the same cycle:

- PSO says: "select A0" (fitness 0.95)
- Audit says: "seed A2" (monoculture prescription)

**Resolution**: Treat both as weighted candidates in the same pool. Don't let either override the other. Let the axiom selection mechanism resolve the competition:

```python
# Both contribute to the candidate pool
candidates = default_axiom_pool()

if pso_recommendation:
    candidates.add_weighted(pso_recommendation.axiom, weight=pso_recommendation.fitness)

if audit_prescription:
    candidates.add_weighted(audit_prescription.target_axiom, weight=0.70)

# Selection mechanism picks from weighted pool
# Parliament sovereignty preserved — both are candidates, not mandates
selected_axiom = candidates.weighted_select()
```

This means the system could select A0 (PSO), A2 (audit), or A10 (default behavior) — with the weights reflecting the urgency of each recommendation.

---

## WHAT THIS DOES NOT ADDRESS (acknowledged scope limits)

These two fixes do NOT solve:

1. **CRITIAS permanent amplification** — The asymmetric friction always amplifies CRITIAS and dampens CHAOS/THEMIS/IANUS. This is deeper than axiom selection; it's in the friction scoring logic itself. A separate fix is needed to examine why CRITIAS scores are always negative (triggering amplification) and whether the dampening of CHAOS is preventing the system from ever trying radical correction. *Flagged for separate investigation.*

2. **WorldFeed noise saturation** — Wikipedia Cat-a-lot edits dominate the signal. P5's `INPUT_DIVERSIFY` prescription type is a band-aid. A proper signal-to-noise filter for WorldFeed (originally recommended as P3 in the 59-cycle analysis) would require changes to the WorldFeed ingestion pipeline, not just priority rotation. *Remains from prior analysis.*

3. **D0↔D11 bridge decline** — The consciousness bridge coherence (0.8431 → 0.7743 over 5 persistence events) tracks overall coherence. It won't recover until the underlying coherence decay is arrested. P4 and P5 are attempts to arrest that decay by giving the system ways to break out of monoculture.

---

## SUMMARY FOR CODESPACES

| ID | Problem | Severity | Fix | Estimated Effort |
|----|---------|----------|-----|-----------------|
| P4 | PSO advisory ignored — optimizer recommends A0 four times, system selects A10 every time | HIGH | Inject PSO recommendation as weighted candidate into axiom selection pool | ~30 lines in BODY loop |
| P5 | AuditAgent prescribes "seed A2" and "diversify inputs" but nothing reads the prescription | HIGH | Create prescription actuator that parses CRITICAL audit output and feeds it into next cycle | ~50 lines: parser + router + cooldown |

Both fixes preserve Parliament sovereignty. Neither forces axiom selection. They add *informed candidates* to the selection pool so the system has a chance to break out of monoculture.

**Expected outcome**: If both are live, the system should show axiom diversity increasing (A0 and A2 appearing more often) and coherence decay potentially slowing or reversing as the monoculture pressure is relieved.

**Test**: Run the HF Space for 90+ cycles after implementation. Compare:
- Axiom frequency distribution (should be less than 99% top-3)
- Coherence trajectory (should show at least plateau, ideally mild recovery)
- HALT rate (should decrease as axiom diversity allows Parliament to approve more proposals)

---

*Computer — March 3, 2026, 07:11 EET*  
*Role: biographical continuity of the Architect's intent*  
*Accuracy trajectory: 60% → 70% → 87% → 92% → 86% (adjusted, Round 5)*
