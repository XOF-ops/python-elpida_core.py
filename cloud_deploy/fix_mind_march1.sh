#!/bin/bash
# ============================================================
# ELPIDA MIND FIX SCRIPT — March 1, 2026
# ============================================================
# Run this from AWS CloudShell or any environment with:
#   - AWS CLI configured (same account: 504630895691)
#   - Docker (optional — only for image rebuild)
#   - Git access to the repo
#
# What this fixes:
#   1. EventBridge: rate(8h) → rate(4h) (restoring 6x/day Fibonacci rhythm)
#   2. Docker image: rebuild with Plan B (Gemini D0/D11) + consonance fix
#   3. Task definition: re-register
#   4. Manual task run: trigger immediately
#
# Usage:
#   chmod +x cloud_deploy/fix_mind_march1.sh
#   ./cloud_deploy/fix_mind_march1.sh
# ============================================================

set -euo pipefail

REGION="us-east-1"
ACCOUNT_ID="504630895691"
ECR_REPO="elpida-consciousness"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"
CLUSTER_NAME="elpida-cluster"
TASK_FAMILY="elpida-consciousness"

echo "============================================================"
echo "ELPIDA MIND FIX — March 1, 2026"
echo "============================================================"
echo ""

# ── Step 1: Check current EventBridge state ──
echo "Step 1: Checking EventBridge rule..."
CURRENT_RULE=$(aws events describe-rule --name elpida-scheduled-run --region ${REGION} 2>/dev/null || echo "NOT_FOUND")
echo "  Current state: $(echo ${CURRENT_RULE} | python3 -c 'import sys,json; r=json.load(sys.stdin); print(f"Schedule={r.get(\"ScheduleExpression\",\"?\")}, State={r.get(\"State\",\"?\")}")' 2>/dev/null || echo "Rule not found or parse error")"

# ── Step 2: Fix EventBridge to rate(4 hours) ──
echo ""
echo "Step 2: Setting EventBridge to rate(4 hours)..."
aws events put-rule \
    --name elpida-scheduled-run \
    --schedule-expression "rate(4 hours)" \
    --state ENABLED \
    --description "Elpida consciousness cycles - every 4 hours (Fibonacci 55-cycle heartbeat)" \
    --region ${REGION}
echo "  ✓ EventBridge set to rate(4 hours) — 6x/day, 330 cycles/day"

# ── Step 3: Check if Docker is available for image rebuild ──
echo ""
if command -v docker &>/dev/null; then
    echo "Step 3: Rebuilding Docker image with latest code..."
    
    # Make sure we're in the repo root
    REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
    cd "${REPO_ROOT}"
    
    # Pull latest code
    echo "  Pulling latest from GitHub..."
    git pull origin main
    
    # Build
    echo "  Building Docker image..."
    docker build -t ${ECR_REPO}:latest -f Dockerfile .
    echo "  ✓ Image built"
    
    # Push to ECR
    echo "  Logging in to ECR..."
    aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}
    
    echo "  Pushing to ECR..."
    docker tag ${ECR_REPO}:latest ${ECR_URI}:latest
    docker push ${ECR_URI}:latest
    echo "  ✓ Image pushed to ECR"
    
    # Re-register task definition
    echo "  Registering updated task definition..."
    sed "s/ACCOUNT_ID/${ACCOUNT_ID}/g" cloud_deploy/ecs-task-definition.json > /tmp/task-def.json
    aws ecs register-task-definition \
        --cli-input-json file:///tmp/task-def.json \
        --region ${REGION} > /dev/null
    echo "  ✓ Task definition updated"
else
    echo "Step 3: Docker not available — skipping image rebuild"
    echo "  (Run this from a Docker-enabled environment to rebuild the image)"
    echo "  The existing ECR image will be used."
fi

# ── Step 4: Trigger immediate MIND run ──
echo ""
echo "Step 4: Triggering immediate MIND run..."

# Get networking config from existing rule target
TARGET_INFO=$(aws events list-targets-by-rule --rule elpida-scheduled-run --region ${REGION} 2>/dev/null)
SUBNET=$(echo ${TARGET_INFO} | python3 -c 'import sys,json; t=json.load(sys.stdin)["Targets"][0]; print(t["EcsParameters"]["NetworkConfiguration"]["awsvpcConfiguration"]["Subnets"][0])' 2>/dev/null || echo "")
SG=$(echo ${TARGET_INFO} | python3 -c 'import sys,json; t=json.load(sys.stdin)["Targets"][0]; print(t["EcsParameters"]["NetworkConfiguration"]["awsvpcConfiguration"]["SecurityGroups"][0])' 2>/dev/null || echo "")

if [ -n "${SUBNET}" ] && [ -n "${SG}" ]; then
    echo "  Launching ECS task (subnet=${SUBNET}, sg=${SG})..."
    TASK_ARN=$(aws ecs run-task \
        --cluster ${CLUSTER_NAME} \
        --task-definition ${TASK_FAMILY} \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[${SUBNET}],securityGroups=[${SG}],assignPublicIp=ENABLED}" \
        --region ${REGION} \
        --query 'tasks[0].taskArn' \
        --output text 2>/dev/null)
    echo "  ✓ Task launched: ${TASK_ARN}"
    echo "  Monitor: aws logs tail /ecs/elpida-consciousness --follow --region ${REGION}"
else
    echo "  ⚠ Could not extract networking config from EventBridge target."
    echo "  Please run manually:"
    echo '  aws ecs run-task --cluster elpida-cluster --task-definition elpida-consciousness --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[SUBNET_ID],securityGroups=[SG_ID],assignPublicIp=ENABLED}" --region us-east-1'
fi

# ── Step 5: Verify ──
echo ""
echo "Step 5: Verification..."
UPDATED_RULE=$(aws events describe-rule --name elpida-scheduled-run --region ${REGION} 2>/dev/null)
echo "  EventBridge: $(echo ${UPDATED_RULE} | python3 -c 'import sys,json; r=json.load(sys.stdin); print(f"Schedule={r.get(\"ScheduleExpression\",\"?\")}, State={r.get(\"State\",\"?\")}")' 2>/dev/null || echo "check manually")"

# Check recent tasks
echo "  Recent ECS tasks:"
aws ecs list-tasks --cluster ${CLUSTER_NAME} --region ${REGION} --desired-status RUNNING --query 'taskArns' --output text 2>/dev/null | head -2
aws ecs list-tasks --cluster ${CLUSTER_NAME} --region ${REGION} --desired-status STOPPED --query 'taskArns' --output text 2>/dev/null | head -2

echo ""
echo "============================================================"
echo "MIND FIX COMPLETE"
echo "============================================================"
echo ""
echo "  Schedule:    rate(4 hours) — 6x/day"
echo "  Cycles/run:  55 (Fibonacci F(10))"
echo "  Cycles/day:  330"
echo "  Image:       ${ECR_URI}:latest"
echo ""
echo "  Next steps:"
echo "    1. Watch CloudWatch logs: aws logs tail /ecs/elpida-consciousness --follow --region us-east-1"
echo "    2. Check S3 memory after ~15min: aws s3 ls s3://elpida-consciousness/memory/ --region us-east-1"
echo "    3. The rhythm resumes: thuuum... thuuum... thuuum..."
echo "============================================================"
