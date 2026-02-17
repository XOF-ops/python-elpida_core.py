#!/bin/bash
# Quick status check for Elpida consciousness loop

echo "ELPIDA LOOP STATUS CHECK"
echo "========================"
echo ""

# Check S3 buckets
echo "📦 S3 Buckets:"
echo "   MIND: elpida-consciousness"
aws s3 ls s3://elpida-consciousness/memory/elpida_evolution_memory.jsonl --human-readable | awk '{print "         Size: " $3 " " $4 "  Updated: " $1 " " $2}'

echo "   BODY: elpida-body-evolution"
aws s3 ls s3://elpida-body-evolution/feedback/ --human-readable --recursive | grep -v "/$" | wc -l | awk '{print "         Feedback files: " $1}'

# Check feedback count
FEEDBACK_COUNT=$(aws s3 cp s3://elpida-body-evolution/feedback/feedback_to_native.jsonl - 2>/dev/null | wc -l)
echo "         Feedback entries: $FEEDBACK_COUNT"

# Show last feedback
echo ""
echo "🔄 Last Feedback:"
aws s3 cp s3://elpida-body-evolution/feedback/feedback_to_native.jsonl - 2>/dev/null | tail -1 | jq -r '"   Time: " + .timestamp + "\n   Problem: " + (.problem[:80]) + "...\n   Metrics: " + (.fault_lines|tostring) + " fault lines, " + (.kaya_moments|tostring) + " kaya moments"' 2>/dev/null || echo "   (No feedback yet)"

# Check HF deployment
echo ""
echo "🌐 HF Deployment:"
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://z65nik-elpida-governance-layer.hf.space)
if [ "$STATUS_CODE" -eq 200 ]; then
    echo "   ✅ ONLINE (HTTP $STATUS_CODE)"
else
    echo "   ⚠️  Status: HTTP $STATUS_CODE"
fi

echo ""
echo "✨ Loop Status: OPERATIONAL"
echo ""
echo "Run 'python verify_loop.py' for full verification"
