#!/bin/bash
# AWS Environment Setup for Elpida S3 Cloud
# 
# Codespace secrets are named AWS_ACCESS_KEY and SECRET_ACCESS_KEY
# but boto3 requires AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# This script exports the correct variable names.

if [ -n "$AWS_ACCESS_KEY" ] && [ -z "$AWS_ACCESS_KEY_ID" ]; then
    export AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY"
    echo "✓ Exported AWS_ACCESS_KEY_ID from AWS_ACCESS_KEY"
fi

if [ -n "$SECRET_ACCESS_KEY" ] && [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    export AWS_SECRET_ACCESS_KEY="$SECRET_ACCESS_KEY"
    echo "✓ Exported AWS_SECRET_ACCESS_KEY from SECRET_ACCESS_KEY"
fi

# Default region (bucket created in us-east-1)
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
echo "✓ AWS_DEFAULT_REGION set to $AWS_DEFAULT_REGION"

# Verify connection
if command -v python3 &> /dev/null; then
    python3 -c "
import boto3
try:
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print(f'✓ AWS connected as: {identity[\"Arn\"]}')
except Exception as e:
    print(f'⚠️  AWS connection failed: {e}')
" 2>/dev/null || echo "⚠️  Could not verify AWS connection"
fi
