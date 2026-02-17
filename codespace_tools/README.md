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
| `push_refinements.sh` | (Future) Upload manual improvements to S3 |
| `deploy_to_cloud.sh` | Redeploy updated code to ECS Fargate |

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
