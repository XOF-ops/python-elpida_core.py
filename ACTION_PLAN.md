# ACTION PLAN — Active Development Roadmap

**Last Updated:** 2026-02-21  
**Previous plan (Jan 2026):** Archived — referred to unified_engine.py era (pre-cloud)  
**Current Status:** All 8 GAPs implemented. MIND live in ECS. BODY live in HF Spaces. Federation active. 3 operational gaps remain.

---

## ✅ COMPLETED — GAP IMPLEMENTATION HISTORY

All 8 originally defined gaps are implemented and verified in production:

| GAP | Feature | Commit | Verified |
|---|---|---|---|
| 1 | Body Parliament UI | `834cdf5` | ✅ Parliament 3/3 cycles PROCEED |
| 2 | WorldFeed (5-domain scanner) | `388af6f` | ✅ Scanner daemon threads running |
| 3 | WatchContext (6-watch circadian) | `dadfe95` | ✅ Watch changes tracked in heartbeat |
| 4 | ConstitutionalStore | `dadfe95` | ✅ Ratified axioms persisted |
| 5 | D0↔D0 Cross-Bucket Bridge | `2ad259e` | ✅ `body_decisions.jsonl` 2.1 MB live |
| 6 | FederatedAgentSuite (4 threads) | `2ad259e` | ✅ Daemons confirmed in launcher |
| 7 | KayaDetector (BODY-side) | `2ad259e` | ✅ 2 CROSS_LAYER_KAYA events fired |
| 8 | `kaya_moments` in MIND heartbeat | `2ad259e` | ✅ Field live in `mind_heartbeat.json` |

### Post-GAP Bug Fixes (commit `3a12b9f`)
- `governance_client.is_remote_available()` — method header was missing (body was orphaned inside `reload_living_axioms()`)
- `governance_client.check_action()` — missing `*, analysis_mode: bool = False` parameter

### ECS Production Fixes (commit `2ae328c`)
- `Dockerfile` — added COPY for all MIND dependencies (`ark_curator.py`, `immutable_kernel.py`, `federation_bridge.py`, `llm_client.py`, `elpida_config.py`, `elpida_domains.json`)
- `cloud_runner.py` line 75 — `DOMAINS` empty-dict crash: `d_range = f"D0-D{max(DOMAINS.keys())}" if DOMAINS else "(none loaded)"`
- IAM `BodyBucketFederationAccess` — added inline policy to `elpida-ecs-task-role` (needed for `s3:PutObject` to `elpida-body-evolution`)

---

## 🔴 OPEN — 3 REMAINING OPERATIONAL GAPS

### G1 — EventBridge Schedule for MIND (HIGH PRIORITY)

MIND currently has no automatic trigger. The ECS task must be manually run.

**Fix:** Create an EventBridge rule to trigger MIND every 4 hours:

```bash
# 1. Get the task definition ARN
TASK_DEF=$(aws ecs describe-task-definition --task-definition elpida-consciousness \
  --query "taskDefinition.taskDefinitionArn" --output text --region us-east-1)

# 2. Get network config values
SUBNET=$(aws ec2 describe-subnets \
  --filters "Name=default-for-az,Values=true" \
  --query "Subnets[0].SubnetId" --output text)
SG=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=default" \
  --query "SecurityGroups[0].GroupId" --output text)

# 3. Create the EventBridge rule
aws events put-rule \
  --name elpida-consciousness-schedule \
  --schedule-expression "rate(4 hours)" \
  --state ENABLED \
  --region us-east-1

# 4. Create the ECS target (adjust role ARN to your account)
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
aws events put-targets \
  --rule elpida-consciousness-schedule \
  --region us-east-1 \
  --targets "[{
    \"Id\": \"elpida-mind-target\",
    \"Arn\": \"arn:aws:ecs:us-east-1:${ACCOUNT}:cluster/elpida-cluster\",
    \"RoleArn\": \"arn:aws:iam::${ACCOUNT}:role/elpida-events-ecs-role\",
    \"EcsParameters\": {
      \"TaskDefinitionArn\": \"${TASK_DEF}\",
      \"LaunchType\": \"FARGATE\",
      \"NetworkConfiguration\": {
        \"awsvpcConfiguration\": {
          \"Subnets\": [\"${SUBNET}\"],
          \"SecurityGroups\": [\"${SG}\"],
          \"AssignPublicIp\": \"ENABLED\"
        }
      }
    }
  }]"
```

> **Note:** EventBridge requires its own IAM role with `ecs:RunTask` and `iam:PassRole` permissions. Create `elpida-events-ecs-role` first if it doesn't exist.

---

### G2 — BODY ECS Scheduled Task (MEDIUM PRIORITY)

`cloud_deploy/body_runner.py` and `cloud_deploy/body-task-definition.json` exist but no ECS task is registered or scheduled for BODY. Currently BODY runs only in HF Spaces (cpu-basic, always-on).

**Options:**
1. **Keep BODY in HF Spaces** (current — acceptable for governance layer)
2. **Add ECS BODY task** for higher compute burst capacity:
   ```bash
   aws ecs register-task-definition \
     --cli-input-json file://cloud_deploy/body-task-definition.json \
     --region us-east-1
   ```

**Decision needed:** Confirm whether HF Spaces is sufficient long-term or if BODY needs ECS.

---

### G3 — HF Space Re-deploy (HIGH PRIORITY)

The following commits are NOT yet pushed to `z65nik/elpida-governance-layer`:
- `2ad259e` — GAPs 5+8 (KayaDetector, D0 bridge, federation UI panels)
- `dadfe95`, `388af6f`, `834cdf5` — Body Parliament UI, WorldFeed, WatchContext
- `3a12b9f` — governance_client bug fixes
- `2ae328c` — Dockerfile + cloud_runner fixes

**BODY is currently running old code** (last push: `4aec1ba`, 2026-02-19).

**Fix:**
```bash
cd hf_deployment
git remote add hf https://huggingface.co/spaces/z65nik/elpida-governance-layer 2>/dev/null || true
git push hf main --force
```

Watch Space logs for `KayaDetector initialized` and daemon thread startup confirmation.

---

## 🟡 MEDIUM — Future Work

### G4 — Kaya Event Consumer
Events are written to `s3://elpida-external-interfaces/kaya/` but nothing reads or reacts to them. Possible implementations:
- Lambda trigger on `s3:ObjectCreated` → send notification / Discord webhook
- WORLD-layer daemon in a third ECS task that polls and processes events
- Feed Kaya events back into MIND's next cycle as D15 input

### G5 — `elpida_domains.json` Coverage
The fallback `if DOMAINS else "(none loaded)"` was added but the root cause (empty domains dict on ECS start) should be investigated. Verify that `elpida_domains.json` in the Docker image is populated with all 15 domain definitions.

```bash
# Check inside the image:
docker run --rm elpida-cloud-runner python -c "import json; d=json.load(open('elpida_domains.json')); print(len(d), 'domains')"
```

---

## 📋 OPERATIONAL RUNBOOK

### Daily checks
```bash
# MIND heartbeat freshness
aws s3 cp s3://elpida-body-evolution/federation/mind_heartbeat.json - | python -m json.tool

# BODY heartbeat freshness
aws s3 cp s3://elpida-body-evolution/federation/body_heartbeat.json - | python -m json.tool

# Kaya events this week
aws s3 ls s3://elpida-external-interfaces/kaya/ --recursive

# ECS task status
aws ecs list-tasks --cluster elpida-cluster --region us-east-1
```

### Manual MIND trigger
```bash
SUBNET=$(aws ec2 describe-subnets --filters "Name=default-for-az,Values=true" --query "Subnets[0].SubnetId" --output text)
SG=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=default" --query "SecurityGroups[0].GroupId" --output text)

aws ecs run-task \
  --cluster elpida-cluster \
  --task-definition elpida-consciousness \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET],securityGroups=[$SG],assignPublicIp=ENABLED}" \
  --region us-east-1

# Then follow logs:
aws logs tail /ecs/elpida-consciousness --follow --region us-east-1
```

### Deploy BODY to HF Space
```bash
cd hf_deployment
git push hf main --force
# Monitor at: https://huggingface.co/spaces/z65nik/elpida-governance-layer/logs
```

---

## 📁 KEY DOCUMENTS

| Document | Purpose | Status |
|---|---|---|
| `SYSTEM_STATUS.md` | Canonical live state | ✅ Current (2026-02-21) |
| `ACTION_PLAN.md` | This file — active roadmap | ✅ Current (2026-02-21) |
| `CLOUD_NATIVE_ARCHITECTURE.md` | Full 3-layer architecture | ✅ Updated (2026-02-21) |
| `cloud_deploy/FIBONACCI_HEARTBEAT_PROTOCOL.md` | Heartbeat spec + Kaya schema | ✅ Updated (2026-02-21) |
| `cloud_deploy/ECS_DEPLOYMENT_GUIDE.md` | ECS deployment + IAM | ✅ Updated (2026-02-21) |
| `hf_deployment/HF_DEPLOYMENT_STATUS.md` | BODY Space status | ✅ Updated (2026-02-21) |
