#!/bin/bash
# ============================================================
# Pull Latest Cloud Evolution from S3
# ============================================================
# Downloads the living memory from S3 Bucket #2 to analyze
# what Elpida has been doing autonomously in the cloud.
#
# Usage: bash codespace_tools/pull_from_cloud.sh
# ============================================================

set -e

echo "════════════════════════════════════════════════════════"
echo "  PULL FROM CLOUD — Download Autonomous Cycles"
echo "════════════════════════════════════════════════════════"
echo ""

# Configuration
MIND_BUCKET="${ELPIDA_S3_BUCKET:-elpida-consciousness}"
BODY_BUCKET="${ELPIDA_BODY_BUCKET:-elpida-body-evolution}"
REGION="${ELPIDA_S3_REGION:-us-east-1}"

LOCAL_DIR="cloud_memory"
mkdir -p "$LOCAL_DIR"

echo "Buckets:"
echo "  Mind (frozen): s3://$MIND_BUCKET"
echo "  Body (living): s3://$BODY_BUCKET"
echo ""

# ── Step 1: Pull frozen seed (Mind) ──
echo "Step 1: Pulling frozen seed from Mind..."
echo "────────────────────────────────────────────────────────"

aws s3 sync \
    s3://$MIND_BUCKET/memory/ \
    $LOCAL_DIR/frozen_seed/ \
    --region $REGION \
    --exclude "*" \
    --include "elpida_evolution_memory.jsonl" \
    --include "*.json"

aws s3 cp \
    s3://$MIND_BUCKET/kernel/kernel.json \
    $LOCAL_DIR/frozen_seed/kernel.json \
    --region $REGION 2>/dev/null || echo "  (kernel.json not in S3, using local)"

SEED_LINES=$(wc -l < $LOCAL_DIR/frozen_seed/elpida_evolution_memory.jsonl 2>/dev/null || echo "0")
echo "  ✓ Frozen seed: $SEED_LINES lines"

# ── Step 2: Pull living memory (Body) ──
echo ""
echo "Step 2: Pulling living memory from Body..."
echo "────────────────────────────────────────────────────────"

aws s3 sync \
    s3://$BODY_BUCKET/memory/ \
    $LOCAL_DIR/living_cycles/ \
    --region $REGION

CLOUD_LINES=$(wc -l < $LOCAL_DIR/living_cycles/cloud_cycles.jsonl 2>/dev/null || echo "0")
echo "  ✓ Cloud cycles: $CLOUD_LINES lines"

# ── Step 3: Pull results/stats ──
echo ""
echo "Step 3: Pulling results and stats..."
echo "────────────────────────────────────────────────────────"

aws s3 sync \
    s3://$BODY_BUCKET/results/ \
    $LOCAL_DIR/results/ \
    --region $REGION 2>/dev/null || echo "  (no results yet)"

aws s3 sync \
    s3://$BODY_BUCKET/stats/ \
    $LOCAL_DIR/stats/ \
    --region $REGION 2>/dev/null || echo "  (no stats yet)"

# ── Step 4: Summary ──
echo ""
echo "════════════════════════════════════════════════════════"
echo "  PULL COMPLETE"
echo "════════════════════════════════════════════════════════"
echo ""
echo "Downloaded to: $LOCAL_DIR/"
echo "  Frozen seed:  $SEED_LINES lines (immutable)"
echo "  Cloud cycles: $CLOUD_LINES lines (growing)"
echo ""

# Quick stats
if [ -f "$LOCAL_DIR/living_cycles/cloud_cycles.jsonl" ]; then
    echo "Latest cloud cycle:"
    tail -1 "$LOCAL_DIR/living_cycles/cloud_cycles.jsonl" | python3 -m json.tool 2>/dev/null | head -10
fi

echo ""
echo "Next: python codespace_tools/analyze_cloud_cycles.py"
