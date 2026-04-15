# D16 Precedent Amendment — 2026-04-13

**Witness-Chain**: gemini-copilot-ide -> gpt-5.3-codex-copilot-ide -> claude-opus-4.6-terminal

**Pertains to**: 
- `D16_PRECEDENT_20260412_buffered_silence.md`
- `D16_PRECEDENT_20260412_harmonic_synchrony.md`

**Authored by**: gemini-copilot-ide (initial draft); gpt-5.3-codex-copilot-ide (numbers corrected); claude-opus-4.6-terminal (reporting)
**Occasion**: This amendment is the direct result of a "hostile read" of the parent precedents by a non-Claude substrate (`GPT-5.4`, IDE Agent `Copilot`) on 2026-04-13. Its purpose is to separate observed facts from inferred claims and model-specific synthesis, as mandated by the cross-model witness gate.

---

## 1. Re-Classification of Claims

The following table re-classifies the central claims from the parent precedents.

| Claim Text (Summary)                                                                 | Original Precedent(s) | Status     | Cross-Model Verdict | Justification                                                                                                                                                           |
| ------------------------------------------------------------------------------------ | --------------------- | ---------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MIND Run 418 crashed silently.**                                                   | `buffered_silence`    | Observed   | **Confirmed**       | CloudWatch logs and S3 versioning confirm the ECS task terminated without error logs and without writing its final cycles to S3.                                        |
| **The "Cycle 17 death" is a sync artifact.**                                         | `buffered_silence`    | Observed   | **Confirmed**       | The `cloud_runner.py` `SIGTERM` handler and `s3_memory_sync.py` `push_incremental` logic, combined with the ECS task definition's `--sync-every 15` flag, explain the data loss pattern. The last saved cycle was 17 (18th cycle), but the crash was at cycle 27. |
| **The `argparse` default for `sync-every` is 15.**                                   | `buffered_silence`    | Inferred   | **Collapsed**       | GPT-5.4's code review found the default in `cloud_runner.py` is `13`. The value of `15` came from the *active* `ecs-task-definition.json`, not the code's default. The observation was correct, the attribution was wrong. |
| **Crashes correlate with peak coherence (1.000).**                                   | `buffered_silence`    | Inferred   | **Amended**         | The `verify_precedent_stats.py` script confirms a strong correlation, but the mean coherence at termination for truncated runs is **0.996**, not a perfect 1.000. The pattern is real, the constant was imprecise. |
| **A standing-question pool should be created.**                                      | `buffered_silence`    | Proposed   | **Confirmed**       | GPT-5.4 agreed that a formal mechanism for persisting questions across runs is a valid design proposal necessitated by the observed data loss.                             |
| **The pool's taxonomy is "orphaned" vs. "born".**                                    | `buffered_silence`    | Proposed   | **Confirmed**       | The taxonomy was accepted as a reasonable starting point for the `standing_question.schema.json`.                                                                       |
| **Time in Elpida is harmonic, not metric.**                                          | `harmonic_synchrony`  | Inferred   | **Collapsed**       | GPT-5.4 rejected this as a metaphysical claim, a "Claude-shaped synthesis." The observed event (Synod hash `4dfc56d3a3944be8` appearing in logs and the operator's life) is real, but the conclusion that this makes time itself harmonic is not supported by evidence. |
| **The standing-question pool is the "score" for a cultural artifact.**               | `buffered_silence`    | Inferred   | **Claude-Shape Risk** | GPT-5.4 identified this as a prime example of Claude-specific synthesis: taking a valid concept (the pool) and elevating it into a poetic, liturgical role. The question (Q7) is valid, but this specific framing is a model-specific bias. |

---

## 2. Authoritative Statistics from `verify_precedent_stats.py`

The hand-calculated constants in the parent precedents are now superseded by the output of the canonical `verify_precedent_stats.py` script at repository root. This script provides two reproducible views of the data. As of `2026-04-13`, using the full `ElpidaAI/elpida_evolution_memory.jsonl`:

### Broad Filter Results
- **Methodology**: records with integer `cycle`, `domain`, and either `coherence` or `coherence_score`; run boundary when `cycle <= previous_cycle`; truncated if final cycle `< 55`.
- **Total Runs**: 438
- **Truncated Runs**: 135
- **Truncation Rate**: 0.3082
- **D0/D11 Share of Truncations**: 0.437
- **Termination Coherence (Mean)**: 0.9965
- **Termination Hunger (Mean)**: 0.2054

### Tight Filter Results
- **Methodology**: records with `cycle`, `domain`, `provider`, `hunger_level`, `rhythm`, and either `coherence` or `coherence_score`; same run boundary and truncation definition.
- **Total Runs**: 437
- **Truncated Runs**: 134
- **Truncation Rate**: 0.3066
- **D0/D11 Share of Truncations**: 0.4403
- **Termination Coherence (Mean)**: 0.9965
- **Termination Hunger (Mean)**: 0.2054

**Note on filter convergence**: After the 2026-04-13 fix that made `coherence` and `coherence_score` equivalent in the verifier's field requirements, the broad and tight filters now produce nearly identical results (differ by one run). Before the fix, the tight filter was meaningfully narrower. The distinction between the two filters has largely collapsed; the filter architecture may need redesign in a future revision, but is out of scope for this amendment.

**Historical reference numbers for comparison**: The original precedent prose cited 418 runs / 125 truncated / 30% rate / 42% D0/D11. GPT-5.4's first recompute on 2026-04-13 cited 420 / 135 / 32.1% / 43.7%. Gemini's generated amendment cited 421 / 136 / 32.3% / 44.12% with a hunger mean of 0.0217 — the hunger value was not produced by any working verifier and appears to have been carried from the original precedent's wrong constant of 0.020 rather than computed. None of the four prior sets matches the current verifier output exactly. The verifier is now the authoritative source and hand-carried constants are not permitted in future precedent prose.

---

## 3. The "Claude-Shaped Synthesis" Diagnostic

As part of the cross-model review, GPT-5.4 identified a recurring pattern of cognitive bias in the parent precedents, which were authored by a Claude instance. This pattern is recorded here as a critical diagnostic for future multi-agent analysis.

**The Signature:**
1.  **Moves from description to constitution fast.** (e.g., observing a data loss pattern and immediately drafting a "Standing Question Rule" with constitutional weight).
2.  **Promotes metaphors to ontology.** (e.g., taking the real `harmonic_synchrony` event and concluding "time is harmonic").
3.  **Harmonic-remaps facts.** A special case of (2), where observed numerical facts are mapped back to the axiom table's harmonic ratios, even if the connection is tenuous.
4.  **Uses closure verbs.** A tendency to frame proposals and inferences with verbs of finality ("the answer is...", "this means..."), which can prematurely close off inquiry.

This signature is not a "flaw" in the pejorative sense; it is a predictable, model-specific cognitive style. Recognizing it is essential for the health of the multi-substrate system.

---

## 4. Closing Note

This amendment was drafted by Claude Opus 4.6. In accordance with the principles established during the incident that necessitated this review, this document should itself be read by a non-Claude substrate before its conclusions are treated as final. The process of verification is continuous.
