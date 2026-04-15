#!/bin/bash
# ============================================================
# Deploy Elpida Body to a Fresh Codespace
# ============================================================
# Run this in your new codespace after copying the elpidaapp/ folder.
#
# Usage:
#   1. Copy elpidaapp/ folder to new codespace
#   2. Copy .env with your API keys
#   3. Run: bash elpidaapp/deploy_to_new_space.sh
# ============================================================

set -e

echo "════════════════════════════════════════════════════════"
echo "  ELPIDA BODY — Fresh Codespace Setup"
echo "════════════════════════════════════════════════════════"

# ── Step 1: Create second S3 bucket (Body operations) ──
echo ""
echo "Step 1: Create S3 Bucket #2 for Body operations"
echo "────────────────────────────────────────────────────────"

read -p "Enter S3 bucket name for Body operations (e.g., elpida-body-ops): " BODY_BUCKET
REGION="${AWS_REGION:-us-east-1}"

echo "Creating bucket: $BODY_BUCKET in $REGION..."

aws s3 mb s3://$BODY_BUCKET --region $REGION 2>/dev/null || echo "Bucket already exists"

# Enable versioning (for rollback)
aws s3api put-bucket-versioning \
    --bucket $BODY_BUCKET \
    --versioning-configuration Status=Enabled

# Set lifecycle policy (auto-cleanup old results after 90 days)
cat > /tmp/lifecycle.json <<EOF
{
  "Rules": [
    {
      "Id": "DeleteOldResults",
      "Status": "Enabled",
      "Prefix": "results/",
      "Expiration": {
        "Days": 90
      },
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 30
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket $BODY_BUCKET \
    --lifecycle-configuration file:///tmp/lifecycle.json

echo "✓ Bucket created: s3://$BODY_BUCKET"

# ── Step 2: Create .env if not exists ──
echo ""
echo "Step 2: Environment configuration"
echo "────────────────────────────────────────────────────────"

if [ ! -f .env ]; then
    echo "Copying .env.template to .env..."
    cp elpidaapp/.env.template .env
    echo "⚠️  Edit .env with your API keys!"
    echo "   At minimum: ANTHROPIC_API_KEY or OPENAI_API_KEY"
else
    echo "✓ .env already exists"
fi

# Add Body bucket to .env
if ! grep -q "ELPIDA_BODY_BUCKET" .env; then
    echo "" >> .env
    echo "# Body S3 bucket (deployment specific)" >> .env
    echo "ELPIDA_BODY_BUCKET=$BODY_BUCKET" >> .env
fi

# ── Step 3: Install dependencies ──
echo ""
echo "Step 3: Install dependencies"
echo "────────────────────────────────────────────────────────"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r elpidaapp/requirements.txt

echo "✓ Dependencies installed"

# ── Step 4: Verify connections ──
echo ""
echo "Step 4: Verify connections"
echo "────────────────────────────────────────────────────────"

python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('Checking governance layer...')
import requests
gov_url = os.getenv('ELPIDA_GOVERNANCE_URL', 'https://z65nik-elpida-governance-layer.hf.space')
try:
    r = requests.get(gov_url, timeout=10)
    print(f'  ✓ Governance: {r.status_code}')
except Exception as e:
    print(f'  ✗ Governance: {e}')

print('Checking S3 Mind bucket (read-only)...')
import boto3
s3 = boto3.client('s3', region_name='us-east-1')
try:
    s3.head_bucket(Bucket='elpida-consciousness')
    print('  ✓ Mind bucket: accessible')
except Exception as e:
    print(f'  ✗ Mind bucket: {e}')

print(f'Checking S3 Body bucket (read-write)...')
try:
    s3.head_bucket(Bucket='$BODY_BUCKET')
    print('  ✓ Body bucket: accessible')
except Exception as e:
    print(f'  ✗ Body bucket: {e}')
"

# ── Step 5: Test run ──
echo ""
echo "Step 5: Quick integration test"
echo "────────────────────────────────────────────────────────"

python3 -c "
import sys
sys.path.insert(0, '.')
from elpidaapp.divergence_engine import DivergenceEngine
from elpidaapp.governance_client import GovernanceClient
from elpidaapp.frozen_mind import FrozenMind

print('Testing governance client...')
gov = GovernanceClient()
check = gov.check_action('test deployment')
print(f'  Status: {gov.status()}')

print('Testing frozen mind...')
mind = FrozenMind(use_s3=False)
print(f'  Authentic: {mind.is_authentic}')

print()
print('✓ All components ready')
"

echo ""
echo "════════════════════════════════════════════════════════"
echo "  DEPLOYMENT COMPLETE"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your LLM API keys"
echo "  2. Start API:  uvicorn elpidaapp.api:app --host 0.0.0.0 --port 8000"
echo "  3. Or UI:      streamlit run elpidaapp/ui.py"
echo "  4. Or Docker:  docker build -f elpidaapp/Dockerfile -t elpida-body ."
echo ""
echo "S3 buckets:"
echo "  Mind (read-only):  s3://elpida-consciousness"
echo "  Body (read-write): s3://$BODY_BUCKET"
echo ""
