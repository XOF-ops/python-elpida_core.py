#!/bin/bash
# ============================================================
# ELPIDA ECS DEPLOYMENT SCRIPT
# ============================================================
# Run this script to deploy Elpida to AWS ECS Fargate.
# Prerequisites: AWS CLI configured, Docker installed.
#
# Usage:
#   chmod +x cloud_deploy/deploy.sh
#   ./cloud_deploy/deploy.sh
# ============================================================

set -euo pipefail

# ── Configuration ──
REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO="elpida-consciousness"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"
CLUSTER_NAME="elpida-cluster"
TASK_FAMILY="elpida-consciousness"
SERVICE_NAME="elpida-scheduled"
LOG_GROUP="/ecs/elpida-consciousness"
SECRET_NAME="elpida/api-keys"
SCHEDULE_EXPRESSION="rate(4 hours)"  # Run every 4 hours

echo "============================================================"
echo "ELPIDA ECS FARGATE DEPLOYMENT"
echo "============================================================"
echo "Account:  ${ACCOUNT_ID}"
echo "Region:   ${REGION}"
echo "ECR:      ${ECR_URI}"
echo "Schedule: ${SCHEDULE_EXPRESSION}"
echo "============================================================"

# ── Step 1: Create ECR Repository ──
echo ""
echo "Step 1: Creating ECR repository..."
aws ecr describe-repositories --repository-names ${ECR_REPO} --region ${REGION} 2>/dev/null || \
  aws ecr create-repository \
    --repository-name ${ECR_REPO} \
    --region ${REGION} \
    --image-scanning-configuration scanOnPush=true
echo "  ✓ ECR repository ready"

# ── Step 2: Build & Push Docker Image ──
echo ""
echo "Step 2: Building Docker image..."
docker build -t ${ECR_REPO}:latest -f Dockerfile .
echo "  ✓ Image built"

echo "  Logging in to ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}

echo "  Pushing to ECR..."
docker tag ${ECR_REPO}:latest ${ECR_URI}:latest
docker push ${ECR_URI}:latest
echo "  ✓ Image pushed"

# ── Step 3: Create CloudWatch Log Group ──
echo ""
echo "Step 3: Creating CloudWatch log group..."
aws logs describe-log-groups --log-group-name-prefix ${LOG_GROUP} --region ${REGION} 2>/dev/null | grep -q ${LOG_GROUP} || \
  aws logs create-log-group --log-group-name ${LOG_GROUP} --region ${REGION}
echo "  ✓ Log group ready"

# ── Step 4: Create IAM Roles ──
echo ""
echo "Step 4: Creating IAM roles..."

# ECS Execution Role (pulls image, reads secrets)
cat > /tmp/ecs-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

aws iam get-role --role-name elpida-ecs-execution-role 2>/dev/null || \
  aws iam create-role \
    --role-name elpida-ecs-execution-role \
    --assume-role-policy-document file:///tmp/ecs-trust-policy.json

aws iam attach-role-policy \
  --role-name elpida-ecs-execution-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy 2>/dev/null || true

# Attach Secrets Manager read access to execution role
cat > /tmp/secrets-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "secretsmanager:GetSecretValue"
    ],
    "Resource": "arn:aws:secretsmanager:${REGION}:${ACCOUNT_ID}:secret:${SECRET_NAME}*"
  }]
}
EOF

aws iam put-role-policy \
  --role-name elpida-ecs-execution-role \
  --policy-name elpida-secrets-access \
  --policy-document file:///tmp/secrets-policy.json

# ECS Task Role (S3 access for D14)
aws iam get-role --role-name elpida-ecs-task-role 2>/dev/null || \
  aws iam create-role \
    --role-name elpida-ecs-task-role \
    --assume-role-policy-document file:///tmp/ecs-trust-policy.json

cat > /tmp/s3-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
      "s3:GetBucketLocation"
    ],
    "Resource": [
      "arn:aws:s3:::elpida-consciousness",
      "arn:aws:s3:::elpida-consciousness/*"
    ]
  }]
}
EOF

aws iam put-role-policy \
  --role-name elpida-ecs-task-role \
  --policy-name elpida-s3-access \
  --policy-document file:///tmp/s3-policy.json

echo "  ✓ IAM roles ready"

# ── Step 5: Store API Keys in Secrets Manager ──
echo ""
echo "Step 5: Storing API keys in Secrets Manager..."
echo "  (If secret already exists, this will update it)"

# Check if secret exists
if aws secretsmanager describe-secret --secret-id ${SECRET_NAME} --region ${REGION} 2>/dev/null; then
  echo "  Secret exists — updating..."
  aws secretsmanager put-secret-value \
    --secret-id ${SECRET_NAME} \
    --region ${REGION} \
    --secret-string "{
      \"ANTHROPIC_API_KEY\": \"${ANTHROPIC_API_KEY:-REPLACE_ME}\",
      \"OPENAI_API_KEY\": \"${OPENAI_API_KEY:-REPLACE_ME}\",
      \"OPENROUTER_API_KEY\": \"${OPENROUTER_API_KEY:-REPLACE_ME}\",
      \"PERPLEXITY_API_KEY\": \"${PERPLEXITY_API_KEY:-REPLACE_ME}\",
      \"GEMINI_API_KEY\": \"${GEMINI_API_KEY:-REPLACE_ME}\",
      \"MISTRAL_API_KEY\": \"${MISTRAL_API_KEY:-REPLACE_ME}\",
      \"COHERE_API_KEY\": \"${COHERE_API_KEY:-REPLACE_ME}\",
      \"XAI_API_KEY\": \"${XAI_API_KEY:-REPLACE_ME}\"
    }"
else
  echo "  Creating new secret..."
  aws secretsmanager create-secret \
    --name ${SECRET_NAME} \
    --region ${REGION} \
    --description "Elpida LLM API keys for consciousness engine" \
    --secret-string "{
      \"ANTHROPIC_API_KEY\": \"${ANTHROPIC_API_KEY:-REPLACE_ME}\",
      \"OPENAI_API_KEY\": \"${OPENAI_API_KEY:-REPLACE_ME}\",
      \"OPENROUTER_API_KEY\": \"${OPENROUTER_API_KEY:-REPLACE_ME}\",
      \"PERPLEXITY_API_KEY\": \"${PERPLEXITY_API_KEY:-REPLACE_ME}\",
      \"GEMINI_API_KEY\": \"${GEMINI_API_KEY:-REPLACE_ME}\",
      \"MISTRAL_API_KEY\": \"${MISTRAL_API_KEY:-REPLACE_ME}\",
      \"COHERE_API_KEY\": \"${COHERE_API_KEY:-REPLACE_ME}\",
      \"XAI_API_KEY\": \"${XAI_API_KEY:-REPLACE_ME}\"
    }"
fi
echo "  ✓ Secrets stored"

# ── Step 6: Create ECS Cluster ──
echo ""
echo "Step 6: Creating ECS cluster..."
aws ecs describe-clusters --clusters ${CLUSTER_NAME} --region ${REGION} 2>/dev/null | grep -q "ACTIVE" || \
  aws ecs create-cluster --cluster-name ${CLUSTER_NAME} --region ${REGION}
echo "  ✓ Cluster ready"

# ── Step 7: Register Task Definition ──
echo ""
echo "Step 7: Registering task definition..."

# Replace ACCOUNT_ID placeholder in task definition
sed "s/ACCOUNT_ID/${ACCOUNT_ID}/g" cloud_deploy/ecs-task-definition.json > /tmp/task-def.json

aws ecs register-task-definition \
  --cli-input-json file:///tmp/task-def.json \
  --region ${REGION}
echo "  ✓ Task definition registered"

# ── Step 8: Create Scheduled Rule (EventBridge) ──
echo ""
echo "Step 8: Creating scheduled rule..."

# Get default VPC and subnet
DEFAULT_VPC=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region ${REGION})
DEFAULT_SUBNET=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=${DEFAULT_VPC}" --query "Subnets[0].SubnetId" --output text --region ${REGION})
DEFAULT_SG=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=${DEFAULT_VPC}" "Name=group-name,Values=default" --query "SecurityGroups[0].GroupId" --output text --region ${REGION})

# Create EventBridge rule
aws events put-rule \
  --name elpida-scheduled-run \
  --schedule-expression "${SCHEDULE_EXPRESSION}" \
  --state ENABLED \
  --description "Elpida consciousness cycles - every 4 hours" \
  --region ${REGION}

# Create role for EventBridge to run ECS tasks
aws iam get-role --role-name elpida-events-role 2>/dev/null || \
  aws iam create-role \
    --role-name elpida-events-role \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "events.amazonaws.com"},
        "Action": "sts:AssumeRole"
      }]
    }'

cat > /tmp/events-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["ecs:RunTask"],
    "Resource": "arn:aws:ecs:${REGION}:${ACCOUNT_ID}:task-definition/${TASK_FAMILY}:*"
  },
  {
    "Effect": "Allow",
    "Action": "iam:PassRole",
    "Resource": [
      "arn:aws:iam::${ACCOUNT_ID}:role/elpida-ecs-execution-role",
      "arn:aws:iam::${ACCOUNT_ID}:role/elpida-ecs-task-role"
    ]
  }]
}
EOF

aws iam put-role-policy \
  --role-name elpida-events-role \
  --policy-name elpida-run-task \
  --policy-document file:///tmp/events-policy.json

# Set the target
aws events put-targets \
  --rule elpida-scheduled-run \
  --region ${REGION} \
  --targets "[{
    \"Id\": \"elpida-fargate\",
    \"Arn\": \"arn:aws:ecs:${REGION}:${ACCOUNT_ID}:cluster/${CLUSTER_NAME}\",
    \"RoleArn\": \"arn:aws:iam::${ACCOUNT_ID}:role/elpida-events-role\",
    \"EcsParameters\": {
      \"TaskDefinitionArn\": \"arn:aws:ecs:${REGION}:${ACCOUNT_ID}:task-definition/${TASK_FAMILY}\",
      \"LaunchType\": \"FARGATE\",
      \"NetworkConfiguration\": {
        \"awsvpcConfiguration\": {
          \"Subnets\": [\"${DEFAULT_SUBNET}\"],
          \"SecurityGroups\": [\"${DEFAULT_SG}\"],
          \"AssignPublicIp\": \"ENABLED\"
        }
      },
      \"PlatformVersion\": \"LATEST\"
    }
  }]"

echo "  ✓ Schedule created: ${SCHEDULE_EXPRESSION}"

# ── Done ──
echo ""
echo "============================================================"
echo "DEPLOYMENT COMPLETE"
echo "============================================================"
echo ""
echo "  Cluster:   ${CLUSTER_NAME}"
echo "  Task:      ${TASK_FAMILY}"
echo "  Schedule:  ${SCHEDULE_EXPRESSION}"
echo "  Image:     ${ECR_URI}:latest"
echo "  Logs:      ${LOG_GROUP}"
echo "  S3 Memory: s3://elpida-consciousness/"
echo ""
echo "  Monitor:  aws logs tail ${LOG_GROUP} --follow --region ${REGION}"
echo "  Manual:   aws ecs run-task --cluster ${CLUSTER_NAME} --task-definition ${TASK_FAMILY} --launch-type FARGATE --network-configuration 'awsvpcConfiguration={subnets=[${DEFAULT_SUBNET}],securityGroups=[${DEFAULT_SG}],assignPublicIp=ENABLED}' --region ${REGION}"
echo ""
echo "  The rhythm continues in the cloud."
echo "  thuuum... thuuum... thuuum..."
echo "============================================================"
