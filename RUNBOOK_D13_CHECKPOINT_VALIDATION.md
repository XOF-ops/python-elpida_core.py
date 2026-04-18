# Runbook — D13 Checkpoint Validation

## Purpose
Repeatable operator procedure to validate D13 checkpoint hooks in production across MIND, BODY, WORLD, and FULL paths.

## Preconditions
- Repository is on main and synced.
- AWS credentials are available via .env.
- AWS metadata lookup disabled for local CLI reliability:
  - export AWS_EC2_METADATA_DISABLED=true

## Quick Mode (Copy/Paste)
Use this when you only need a fast PASS/FAIL for the MIND checkpoint path.

```bash
set -euo pipefail
cd /workspaces/python-elpida_core.py
source .env
export AWS_EC2_METADATA_DISABLED=true

SUBNET=$(aws ec2 describe-subnets --region us-east-1 --filters "Name=default-for-az,Values=true" --query 'Subnets[0].SubnetId' --output text)
SG=$(aws ec2 describe-security-groups --region us-east-1 --filters "Name=group-name,Values=default" --query 'SecurityGroups[0].GroupId' --output text)

TASK_ARN=$(aws ecs run-task \
  --cluster elpida-cluster \
  --task-definition elpida-consciousness \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNET],securityGroups=[$SG],assignPublicIp=ENABLED}" \
  --region us-east-1 \
  --query 'tasks[0].taskArn' --output text)

echo "TASK_ARN=$TASK_ARN"

aws ecs wait tasks-running --cluster elpida-cluster --region us-east-1 --tasks "$TASK_ARN"
aws ecs describe-tasks --cluster elpida-cluster --region us-east-1 --tasks "$TASK_ARN" \
  --query 'tasks[0].containers[0].{image:image,imageDigest:imageDigest,lastStatus:lastStatus}' --output json

aws ecs wait tasks-stopped --cluster elpida-cluster --region us-east-1 --tasks "$TASK_ARN"
aws ecs describe-tasks --cluster elpida-cluster --region us-east-1 --tasks "$TASK_ARN" \
  --query 'tasks[0].{lastStatus:lastStatus,stoppedReason:stoppedReason,exit:containers[0].exitCode}' --output json

TASK_ID=$(echo "$TASK_ARN" | awk -F/ '{print $NF}')
STREAM="elpida/elpida-engine/${TASK_ID}"

aws logs filter-log-events --log-group-name /ecs/elpida-consciousness --region us-east-1 --log-stream-names "$STREAM" \
  --filter-pattern '"MIND_RUN_COMPLETE"' --query 'events[].message' --output text | tee /tmp/d13_mind_checkpoint.log

CHECKPOINT_ID=$(grep -o 'seed_[0-9TZ]\+_[a-f0-9]\+' /tmp/d13_mind_checkpoint.log | tail -n1)
echo "CHECKPOINT_ID=${CHECKPOINT_ID:-MISSING}"

if [[ -z "${CHECKPOINT_ID:-}" ]]; then
  echo "FAIL: checkpoint id not found in logs"
  exit 1
fi

aws s3api head-object --bucket elpida-external-interfaces --key "seeds/mind/${CHECKPOINT_ID}.tar.gz" \
  --query '{Size:ContentLength,LastModified:LastModified}' --output json
aws s3api head-object --bucket elpida-body-evolution --key "federation/seed_anchors/${CHECKPOINT_ID}.json" \
  --query '{Size:ContentLength,LastModified:LastModified}' --output json

echo "PASS: D13 MIND checkpoint persisted in WORLD seed + federation anchor"
```

Quick PASS criteria:
- ECS task exits with code 0.
- CloudWatch contains `MIND_RUN_COMPLETE` with `checkpoint_id`.
- Both S3 `head-object` commands succeed for that checkpoint.

## Quick Mode B (Controlled BODY/WORLD/FULL Probes)
Use this when you need direct hook validation without waiting for full cycle behavior.

Important:
- Run from repository root.
- Requires valid AWS credentials in `.env`.
- These probes intentionally create real seed + anchor artifacts.

### Probe WORLD hook (D15_EMISSION)
```bash
set -euo pipefail
cd /workspaces/python-elpida_core.py
source .env
export AWS_EC2_METADATA_DISABLED=true

python3 - <<'PY'
from hf_deployment.elpidaapp.d15_pipeline import D15Pipeline

pipe = D15Pipeline()
pipe._emit_d13_world_seed(
  result={
    "timestamp": "2026-04-18T00:00:00Z",
    "duration_s": 0.5,
    "emergence": {
      "axioms_in_tension": ["A0", "A11"],
      "successful_domains": ["D0", "D11"],
      "d15_output": "Controlled WORLD probe",
    },
  },
  governance_result={"governance": "probe-approved"},
  broadcast_key="d15/broadcasts/probe_world.json",
)
print("WORLD probe invoked")
PY
```

### Probe FULL hook (A16_CONVERGENCE)
```bash
set -euo pipefail
cd /workspaces/python-elpida_core.py
source .env
export AWS_EC2_METADATA_DISABLED=true

python3 - <<'PY'
from hf_deployment.elpidaapp.d15_convergence_gate import ConvergenceGate

gate = ConvergenceGate()
gate._emit_d13_full_seed(
  broadcast={"broadcast_id": "probe-full", "type": "D15_CONVERGENCE"},
  mind_heartbeat={"dominant_axiom": "A0", "coherence": 0.91},
  body_cycle=999,
  body_axiom="A11",
  body_coherence=0.88,
  body_approval=0.62,
  s3_key="d15/broadcasts/probe_full.json",
  event_label="probe_a16_convergence",
)
print("FULL probe invoked")
PY
```

### Probe BODY hook (BODY_RATIFICATION)
```bash
set -euo pipefail
cd /workspaces/python-elpida_core.py
source .env
export AWS_EC2_METADATA_DISABLED=true

python3 - <<'PY'
from pathlib import Path
from hf_deployment.elpidaapp.parliament_cycle_engine import ParliamentCycleEngine

engine = ParliamentCycleEngine.__new__(ParliamentCycleEngine)
engine._axiom_frequency = {"A6": 7, "A11": 6, "A0": 5}
engine.last_dominant_axiom = "A6"
engine.cycle_count = 999
engine.coherence = 0.84
engine.last_rhythm = "SYNTHESIS"
engine.d15_broadcast_count = 1

store_path = Path("hf_deployment/living_axioms.jsonl")
if not store_path.exists():
  store_path.parent.mkdir(parents=True, exist_ok=True)
  store_path.write_text('{"axiom":"A6","reason":"probe"}\n', encoding="utf-8")

ParliamentCycleEngine._emit_d13_body_seed(
  engine,
  store_path=store_path,
  ratified_count=1,
)
print("BODY probe invoked")
PY
```

### Verify newly written artifacts
```bash
aws s3 ls s3://elpida-external-interfaces/seeds/world/ | tail -n 3
aws s3 ls s3://elpida-external-interfaces/seeds/full/ | tail -n 3
aws s3 ls s3://elpida-external-interfaces/seeds/body/ | tail -n 3
aws s3 ls s3://elpida-body-evolution/federation/seed_anchors/ | tail -n 10
```

## Quick Mode C (Latest Checkpoint Audit Extractor)
Use this to print latest checkpoint evidence per layer in one command.

```bash
set -euo pipefail
cd /workspaces/python-elpida_core.py
source .env
export AWS_EC2_METADATA_DISABLED=true

# All layers
scripts/d13_checkpoint_audit.sh

# Optional: selected layers only
scripts/d13_checkpoint_audit.sh mind world

# JSON output (report ingestion)
scripts/d13_checkpoint_audit.sh --format json

# CSV output (spreadsheet/report pipelines)
scripts/d13_checkpoint_audit.sh --format csv

# Last 3 checkpoints per layer (JSON)
scripts/d13_checkpoint_audit.sh --latest-n 3 --format json

# Last 5 checkpoints for selected layers only
scripts/d13_checkpoint_audit.sh --latest-n 5 --format csv mind world

# Last 24 hours only (all layers)
scripts/d13_checkpoint_audit.sh --since-hours 24 --format json

# Combined window + count (top 3 within last 12h)
scripts/d13_checkpoint_audit.sh --since-hours 12 --latest-n 3 --format csv

# Per-layer aggregate summary (counts + newest/oldest timestamps)
scripts/d13_checkpoint_audit.sh --summary --format json

# Summary for selected layers only
scripts/d13_checkpoint_audit.sh --summary --format csv mind world

# CI guardrail: fail if any world seed lacks matching federation anchor
scripts/d13_checkpoint_audit.sh --fail-on-missing-anchor --latest-n 10 --format json
```

Output fields per layer:
- checkpoint_id
- world_key
- anchor_key
- world_head (size + timestamp)
- anchor_head (size + timestamp)
- anchor_meta (source_event, source_component, git_commit, created_at)

## 1) Confirm Active Runtime Artifact
### Check ECS task definition image
- aws ecs describe-task-definition --task-definition elpida-consciousness --region us-east-1 --query 'taskDefinition.{revision:revision,image:containerDefinitions[0].image,registeredAt:registeredAt}' --output table

### Check ECR latest digest
- aws ecr describe-images --repository-name elpida-consciousness --region us-east-1 --image-ids imageTag=latest --query 'imageDetails[0].{digest:imageDigest,pushed:imagePushedAt,tags:imageTags}' --output json

If latest is not expected, rebuild and push before validation.

## 2) Start Validation Task (MIND path)
### Launch one ECS task
- SUBNET=$(aws ec2 describe-subnets --region us-east-1 --filters "Name=default-for-az,Values=true" --query 'Subnets[0].SubnetId' --output text)
- SG=$(aws ec2 describe-security-groups --region us-east-1 --filters "Name=group-name,Values=default" --query 'SecurityGroups[0].GroupId' --output text)
- TASK_ARN=$(aws ecs run-task --cluster elpida-cluster --task-definition elpida-consciousness --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[$SUBNET],securityGroups=[$SG],assignPublicIp=ENABLED}" --region us-east-1 --query 'tasks[0].taskArn' --output text)
- echo "$TASK_ARN"

### Verify running container digest
- aws ecs wait tasks-running --cluster elpida-cluster --region us-east-1 --tasks "$TASK_ARN"
- aws ecs describe-tasks --cluster elpida-cluster --region us-east-1 --tasks "$TASK_ARN" --query 'tasks[0].containers[0].{image:image,imageDigest:imageDigest,lastStatus:lastStatus,runtimeId:runtimeId}' --output json

## 3) Monitor Execution
### Wait for task completion
- aws ecs wait tasks-stopped --cluster elpida-cluster --region us-east-1 --tasks "$TASK_ARN"
- aws ecs describe-tasks --cluster elpida-cluster --region us-east-1 --tasks "$TASK_ARN" --query 'tasks[0].{lastStatus:lastStatus,stoppedReason:stoppedReason,start:startedAt,stop:stoppedAt,exit:containers[0].exitCode}' --output json

Expected:
- lastStatus = STOPPED
- exit = 0
- stoppedReason = Essential container in task exited

## 4) Verify CloudWatch Checkpoint Markers
### Build stream name from task id
- TASK_ID=$(echo "$TASK_ARN" | awk -F/ '{print $NF}')
- STREAM="elpida/elpida-engine/${TASK_ID}"

### Query key markers
- aws logs filter-log-events --log-group-name /ecs/elpida-consciousness --region us-east-1 --log-stream-names "$STREAM" --filter-pattern '"PHASE 5.6"' --query 'events[].message' --output text
- aws logs filter-log-events --log-group-name /ecs/elpida-consciousness --region us-east-1 --log-stream-names "$STREAM" --filter-pattern '"MIND_RUN_COMPLETE"' --query 'events[].message' --output text
- aws logs filter-log-events --log-group-name /ecs/elpida-consciousness --region us-east-1 --log-stream-names "$STREAM" --filter-pattern '"layer=mind"' --query 'events[].message' --output text

Expected markers:
- PHASE 5.6 entry
- MIND_RUN_COMPLETE checkpoint_id entry
- seed push complete layer=mind entry

## 5) Verify S3 Persistence
### List recent objects
- aws s3 ls s3://elpida-external-interfaces/seeds/mind/ | tail -n 5
- aws s3 ls s3://elpida-body-evolution/federation/seed_anchors/ | tail -n 10

### Validate exact objects from log checkpoint_id
If checkpoint_id is seed_YYYY..._XXXXXXXX:
- aws s3api head-object --bucket elpida-external-interfaces --key "seeds/mind/${checkpoint_id}.tar.gz" --query '{Size:ContentLength,LastModified:LastModified}' --output json
- aws s3api head-object --bucket elpida-body-evolution --key "federation/seed_anchors/${checkpoint_id}.json" --query '{Size:ContentLength,LastModified:LastModified}' --output json

## 6) Optional Controlled Hook Probes
Use only for targeted validation without full loop dependency.

### WORLD hook (D15_EMISSION)
- Invoke D15Pipeline._emit_d13_world_seed with controlled payload.

### FULL hook (A16_CONVERGENCE)
- Invoke ConvergenceGate._emit_d13_full_seed with controlled payload.

### BODY hook (BODY_RATIFICATION)
- Invoke ParliamentCycleEngine._emit_d13_body_seed with controlled payload.

## 7) Failure Diagnostics
### Symptom: PHASE 5.6 appears, but no seed in S3
Likely cause:
- Missing ark_archivist.py in ECS image.

Fix:
- Ensure Dockerfile contains:
  - COPY ark_archivist.py /app/ark_archivist.py
- Rebuild and push image.
- Re-run this runbook.

### Symptom: AWS CLI hangs locally
Fix:
- export AWS_EC2_METADATA_DISABLED=true

### Symptom: Writes denied to seeds/ or seed_anchors/
Check:
- IAM permissions for PutObject, ListBucket, HeadObject on:
  - elpida-external-interfaces/seeds/*
  - elpida-body-evolution/federation/seed_anchors/*

## 8) Audit Record Template
Record the following after each validation:
- commit sha
- deployed image digest
- task arn
- task exit code and stop reason
- checkpoint_id
- world seed key
- anchor key
- head-object size and timestamp (both objects)
- CloudWatch marker snippets
