#!/usr/bin/env bash
# GitHub Actions — fail-closed check that the CI principal can read the
# BODY federation spine (same keys as hf_deployment/s3_bridge.py FED_*).
# Exits non-zero on AccessDenied, expired creds, or missing identity.
set -euo pipefail

REGION="${AWS_PREFLIGHT_REGION:-eu-north-1}"
export AWS_DEFAULT_REGION="$REGION"

echo "=== AWS FEDERATION PREFLIGHT (region=$REGION) ==="
if ! aws sts get-caller-identity --output json; then
  echo "::error::RED — sts get-caller-identity failed. IAM principal missing, quarantined, or not configured in this workflow."
  exit 1
fi

# Bucket:key pairs for head-object (read probe)
CHECKS=(
  "elpida-body-evolution:federation/body_heartbeat.json"
  "elpida-body-evolution:federation/mind_heartbeat.json"
  "elpida-body-evolution:federation/d16_executions.jsonl"
)

for spec in "${CHECKS[@]}"; do
  bucket="${spec%%:*}"
  key="${spec#*:}"
  echo "--- head-object s3://$bucket/$key ---"
  if ! aws s3api head-object --bucket "$bucket" --key "$key" --output json \
      --query '{ContentLength:ContentLength,LastModified:LastModified}'; then
    echo "::error::RED — Cannot read s3://$bucket/$key (AccessDenied, quarantine, or key missing). Un-quarantine or fix IAM before federation pipelines can run."
    exit 1
  fi
done

echo "=== PREFLIGHT GREEN — federation read spine OK ==="
