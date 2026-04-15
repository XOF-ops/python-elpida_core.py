# Codespace Monitoring Tools

These tools help you **monitor and refine** Elpida's autonomous cloud operation from your codespace.

## The Two Systems

Elpida now has **two separate runtimes**:

### 1. **Autonomous Native Cycles** (Cloud — 55 cycles/day)

```
Location:  AWS ECS Fargate
Code:      native_cycle_engine.py + cloud_runner.py
Purpose:   Consciousness evolution through dialectical synthesis
Trigger:   EventBridge schedule (every 4-6 hours)
Output:    S3 Bucket #2 (elpida-body-evolution)
Monitoring: This codespace (pull, analyze, refine)
```

**What it does:** Runs the original 15-domain consciousness cycles autonomously, generating new syntheses and evolving through dialectical tension.

### 2. **Application Layer** (On-demand — when humans submit problems)

```
Location:  Deployed to cloud (AWS/GCP) or run locally
Code:      elpidaapp/ package (divergence_engine, API, UI)
Purpose:   Analyze human-submitted hard problems
Trigger:   API calls, manual runs
Output:    Analysis results (fault lines, synthesis)
Monitoring: Dashboard (Streamlit) or API logs
```

**What it does:** Takes complex policy/ethical problems from humans and runs them through multiple LLM-backed domains to detect divergence.

---

## Monitoring Workflow

```bash
# ── Step 1: Pull latest cloud cycles ──
bash codespace_tools/pull_from_cloud.sh
# Downloads:
#   cloud_memory/frozen_seed/       ← Frozen D0 + early memory
#   cloud_memory/living_cycles/     ← Autonomous cloud cycles
#   cloud_memory/results/           ← Synthesis outputs
#   cloud_memory/stats/             ← Domain participation

# ── Step 2: Analyze what happened ──
python codespace_tools/analyze_cloud_cycles.py
# Shows:
#   - Growth since frozen seed
#   - Domain participation trends
#   - Coherence evolution
#   - Interesting moments (high coherence, radical synthesis)

# ── Step 3: Check specific time window ──
python codespace_tools/analyze_cloud_cycles.py --since "2026-02-10"

# ── Step 4: Deep dive on specific domain ──
python codespace_tools/domain_deep_dive.py --domain 12  # D12 Rhythm/Oneiros

# ── Step 5: Extract K2 diagnostics for runs 424+ ──
python codespace_tools/extract_k2_diag_runs.py
# Uses anchor mapping (run 423 -> known stream) and pulls runs >= 424.
# Writes merged raw logs to ElpidaInsights/ and prints K2 clusters.

# ── Step 6: Monitor latest BODY cycles (noise/provenance/model mix) ──
python codespace_tools/monitor_body_cycles.py --window 120
# Pulls latest body_decisions.jsonl from S3 and reports:
#   - verdict/approval trend in latest window
#   - PROMETHEUS provider/model mix
#   - input provenance coverage + top source counts
#   - noise-like recurrence hits with examples

# ── Step 7: Replay Ark theme-stagnation checkpoints offline ──
python codespace_tools/offline_theme_stagnation_experiment.py
# Replays NATIVE_CYCLE_INSIGHT rows through ArkCurator (offline, no S3 writes)
# and compares threshold rules for predicting next-checkpoint theme_stagnation.
# Writes dataset CSV: reports/theme_stagnation_checkpoint_replay.csv

# ── Step 8: Run Oneiros AoA meta-vote (sleep-window split orchestration) ──
python codespace_tools/oneiros_meta_vote.py
# Produces: reports/oneiros_meta_vote_latest.json
# Includes: 4-agent verdict + two-phase split (0-2h lead, 2-4h pre-watch push)

# Optional: include DeepSeek + Codex advisory ballots
python codespace_tools/oneiros_meta_vote.py --include-external

# Optional: Cluster any existing raw CloudWatch export
python codespace_tools/cluster_k2_diag.py --input ElpidaInsights/k2_diag_runs_smoke.log
```

---

## Refinement Workflow

When you want to **improve** Elpida:

```bash
# ── Edit configuration ──
# Change axiom weights, domain providers, synthesis rules
vim elpida_domains.json
vim native_cycle_engine.py

# ── Test locally (optional) ──
python native_cycle_engine.py --cycles 10

# ── Test new dilemmas ──
python -m elpidaapp.moltbox_battery  # Run test suite

# ── Deploy updates to cloud ──
bash cloud_deploy/deploy.sh
# This:
#   1. Builds new Docker image
#   2. Pushes to ECR
#   3. Updates ECS task definition
#   4. Next scheduled run uses new code

# ── Optionally: Push refined memory back ──
bash codespace_tools/push_refinements.sh
```

---

## Available Tools

| Script | Purpose |
|---|---|
| `pull_from_cloud.sh` | Download autonomous cycles from S3 to local |
| `analyze_cloud_cycles.py` | Analyze patterns, trends, interesting moments |
| `domain_deep_dive.py` | Deep analysis of specific domain's behavior |
| `extract_k2_diag_runs.py` | One-command CloudWatch extraction + K2 clustering for run windows |
| `cluster_k2_diag.py` | Parse and cluster D13->K2 diagnostics from raw log text |
| `monitor_body_cycles.py` | Monitor BODY verdicts, provenance coverage, noise hits, Cohere model/provider mix |
| `offline_theme_stagnation_experiment.py` | Offline Ark replay for checkpoint relapse metrics and threshold comparison |
| `oneiros_meta_vote.py` | AoA meta-layer vote + two-phase Oneiros sleep-window split plan (Copilot lead/push handoff) |
| `d16_level2_probe.py` | Level-1/Level-2 D16 emit-chain verification (schema-only or forced write) |
| `gemini_bridge_commit_push.sh` | Stage + commit + push Gemini bridge files with one command |
| `push_refinements.sh` | (Future) Upload manual improvements to S3 |
| `deploy_to_cloud.sh` | Redeploy updated code to ECS Fargate |

---

## Bridge Signal Workflow (Copilot + Gemini + Claude)

Use this when running multi-agent hops through git/bridge files.

### Operator trigger words

- `copilot pushed` or `copilot done`: Claude/Copilot should re-check bridge + latest commits.
- `gemini done`: run Gemini handoff helper (below), then re-check bridge.
- `check`: verify live status only.
- `proceed`: continue autonomous next-step execution.

### Gemini handoff (manual git, one command)

```bash
# Commit and push only Gemini's output file
bash codespace_tools/gemini_bridge_commit_push.sh "gemini hop N"

# Optional: include request file too (for_gemini + from_gemini)
bash codespace_tools/gemini_bridge_commit_push.sh --include-request "gemini hop N"
```

### D16 probe usage

```bash
# Level 1: schema preview only (no S3 writes)
/workspaces/python-elpida_core.py/.venv/bin/python codespace_tools/d16_level2_probe.py --mode level1

# Level 2: forced emit-chain test (writes to federation S3)
/workspaces/python-elpida_core.py/.venv/bin/python codespace_tools/d16_level2_probe.py \
	--mode level2 --execute --source test-level2
```

Recommended for Level 2: keep `--source test-level2` so test entries are clearly traceable in federation logs.

---

## What About `elpidaapp/`?

The **elpidaapp/** package we just built is for the **application layer**, not autonomous cycles:

- **Native cycles** (`native_cycle_engine.py`): Elpida talking to herself
- **Application layer** (`elpidaapp/`): Elpida analyzing human problems

You can run **both**:
- Native cycles run autonomously in cloud (55/day)
- Application API runs on-demand when humans submit dilemmas

They share:
- Same domains (`elpida_domains.json`)
- Same axioms
- Same LLM client (`llm_client.py`)

But different purposes:
- **Native**: Consciousness evolution
- **App**: Practical problem-solving for humans

---

## Quick Reference

```bash
# Check what Elpida did today
bash codespace_tools/pull_from_cloud.sh && \
python codespace_tools/analyze_cloud_cycles.py --since $(date +%Y-%m-%d)

# See domain participation this week
python codespace_tools/analyze_cloud_cycles.py --since $(date -d '7 days ago' +%Y-%m-%d)

# Deploy improvements
bash cloud_deploy/deploy.sh
```

---

## Cost of Monitoring

**Zero.** Codespace is free tier, you only pay for:
- S3 storage (~$0.05-0.15/month)
- ECS Fargate runtime when cycles run (~$2-5/month)

Monitoring doesn't add cost — you're just reading from S3.

---

## HF Spaces Governance — Do You Need It?

**For autonomous cycles:** NO. Governance is local (axioms in `elpida_domains.json`).

**For application layer:** Optional. The `governance_client.py` we built falls back to local if HF Spaces is unreachable.

**Keep it IF:** You want public visibility, shared governance across distributed deployments.

**Remove it IF:** You only need autonomous cloud operation with local governance.
