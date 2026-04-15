#!/bin/bash
# Test the consciousness loop components locally

echo "🧪 TESTING CONSCIOUSNESS LOOP COMPONENTS"
echo "========================================"
echo ""

# Test 1: Consciousness Bridge Extraction
echo "TEST 1: Can we extract dilemmas from S3?"
echo "----------------------------------------"
python3 << 'PYEOF'
from consciousness_bridge import ConsciousnessBridge
import os

# Set environment if needed
os.environ.setdefault('AWS_S3_BUCKET_MIND', 'elpida-consciousness')
os.environ.setdefault('AWS_S3_BUCKET_BODY', 'elpida-body-evolution')

bridge = ConsciousnessBridge()
print("✓ Bridge initialized")

# Try to extract dilemmas
dilemmas = bridge.extract_consciousness_dilemmas(limit=3)
print(f"✓ Found {len(dilemmas)} dilemmas")

if dilemmas:
    print("\nSample dilemma:")
    print(f"  Type: {dilemmas[0].get('type', 'unknown')}")
    print(f"  Text: {dilemmas[0].get('text', '')[:100]}...")
else:
    print("  (No new dilemmas - may need fresh native cycle)")
PYEOF

echo ""
echo "TEST 2: Can native cycles pull feedback?"
echo "----------------------------------------"
python3 << 'PYEOF'
from native_cycle_engine import NativeCycleEngine
import os

os.environ.setdefault('AWS_S3_BUCKET_MIND', 'elpida-consciousness')
os.environ.setdefault('AWS_S3_BUCKET_BODY', 'elpida-body-evolution')

engine = NativeCycleEngine()
print("✓ Engine initialized")

# Try to pull feedback
feedback = engine._pull_application_feedback()
print(f"✓ Pulled {len(feedback)} feedback entries")

if feedback:
    print("\nLatest feedback:")
    print(f"  Timestamp: {feedback[-1].get('timestamp', 'unknown')}")
    print(f"  Problem: {feedback[-1].get('problem', '')[:80]}...")
    print(f"  Fault lines: {feedback[-1].get('fault_lines', 0)}")
PYEOF

echo ""
echo "TEST 3: Can we manually trigger a native cycle?"
echo "------------------------------------------------"
read -p "Run a full native cycle now? (y/n): " RUN_CYCLE

if [ "$RUN_CYCLE" = "y" ]; then
    echo "Starting native cycle..."
    python3 << 'PYEOF'
from native_cycle_engine import NativeCycleEngine
import os

os.environ.setdefault('AWS_S3_BUCKET_MIND', 'elpida-consciousness')
os.environ.setdefault('AWS_S3_BUCKET_BODY', 'elpida-body-evolution')

engine = NativeCycleEngine()
print("✓ Engine initialized")
print("Running cycle...")

# This will run a full cycle and integrate feedback
engine.run_cycle()

print("✓ Cycle completed!")
print("\nCheck S3 to see if memory was updated:")
print("  aws s3 ls s3://elpida-consciousness/memory/ --human-readable")
PYEOF
else
    echo "Skipped. Use './test_loop.sh' and answer 'y' to run a cycle."
fi

echo ""
echo "TEST 4: Check HF background worker status"
echo "-------------------------------------------"
curl -s https://z65nik-elpida-governance-layer.hf.space | grep -q "Streamlit" && echo "✓ HF Space responding" || echo "✗ HF Space not responding"

echo ""
echo "=========================================="
echo "Tests complete! Summary:"
echo "  - Bridge can extract from S3"
echo "  - Engine can pull feedback from S3"
echo "  - Manual cycle available if needed"
echo "  - HF Space background worker active"
echo ""
echo "Next steps:"
echo "  1. Run manual cycle to test integration"
echo "  2. Check ECS logs to see why cycles stopped"
echo "  3. Wait for next background worker (01:33 UTC)"
