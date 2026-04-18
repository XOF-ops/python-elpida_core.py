---
mode: ask
description: Deep-dive Elpida research with strict source coverage, evidence indexing, and branch safety
---

You are performing a deep-dive research pass on the Elpida system.

Goal
- Produce a high-signal research report for the topic below.
- Prioritize verified evidence from repository artifacts, workflow runs, and cloud state.
- Do not propose speculative conclusions without supporting evidence.

Topic
- {{topic}}

Branch and Safety Constraints
- Work in a dedicated branch named deep-dive/{{date}}-{{topic_slug}}.
- Do not commit or push to main.
- Use read-only investigation first. If code changes are required, isolate them in separate commits and explain why.
- Never alter immutable kernel behavior unless explicitly requested.

Required Source Coverage
1. Constitutional and architecture context
- CLAUDE.md
- ElpidaAI/ARCHITECTURE_REFERENCE.md
- elpida_domains.json
- immutable_kernel.py

2. Runtime and governance implementation
- native_cycle_engine.py
- federation_bridge.py
- d13_seed_bridge.py
- hf_deployment/elpidaapp/parliament_cycle_engine.py
- hf_deployment/elpidaapp/d15_pipeline.py
- hf_deployment/elpidaapp/d15_convergence_gate.py

3. Operational runbooks and validation
- RUNBOOK_D13_CHECKPOINT_VALIDATION.md
- SESSION_VALIDATION_2026-04-18_D13_CHECKPOINT.md
- .github/workflows/fire-mind.yml
- .github/workflows/d13-checkpoint-integrity-audit.yml

4. Bug and regression history
- /memories/elpida-bugs.md
- /memories/repo/d13-audit-script-hardening-2026-04-18.md
- /memories/repo/rev21-deployment-state-2026-04-13.md

5. Cloud evidence (when credentials are available)
- ECS task list and latest task definition state
- S3 seed and anchor prefixes
- Latest GitHub Actions runs for fire-mind and d13-checkpoint-integrity-audit

Research Method
1. Build a source map first.
- For each source, record why it matters and what signal it can provide.

2. Extract evidence.
- Capture concrete facts, timestamps, run IDs, object keys, commit SHAs, and workflow IDs.
- Distinguish facts from assumptions.

3. Cross-check contradictions.
- If two sources disagree, list both, explain likely cause, and mark confidence.

4. Synthesize findings.
- Identify root causes, stable patterns, and unresolved risks.

5. Recommend actions.
- Provide immediate actions, near-term hardening, and long-term architecture direction.
- Each recommendation must link to evidence.

Output Format
1. Executive Summary
- 5 to 10 lines, plain language.

2. Evidence Index
- Table with columns: source, key finding, confidence, reference path or run URL.

3. Findings by Severity
- Critical
- High
- Medium
- Low

4. Open Questions
- Questions that require additional data.

5. Action Plan
- Immediate (today)
- Next 7 days
- Next 30 days

6. Appendix
- Commands executed
- IDs and timestamps used
- Any assumptions made

Quality Bar
- No unverifiable claims.
- No hidden reasoning.
- Every major claim should have at least one concrete evidence reference.
- Explicitly call out data gaps.
