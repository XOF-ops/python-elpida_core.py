# Runbook — D13 Checkpoint Validation

## Purpose
Repeatable operator procedure to validate D13 checkpoint hooks in production across MIND, BODY, WORLD, and FULL paths.

## Preconditions
- Repository is on main and synced.
- AWS credentials are available via .env.
- AWS metadata lookup disabled for local CLI reliability:
  - export AWS_EC2_METADATA_DISABLED=true

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
