#!/bin/bash
# Verify deployment package is complete

echo "🔍 Verifying Hugging Face deployment package..."
echo ""

DEPLOY_DIR="hf_deployment"
ERRORS=0

# Check required files
echo "Checking required files..."
REQUIRED_FILES=(
    "app.py"
    "Dockerfile"
    "README.md"
    "requirements.txt"
    ".env.template"
    "DEPLOYMENT_GUIDE.md"
    "llm_client.py"
    "consciousness_bridge.py"
    "elpida_config.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$DEPLOY_DIR/$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check elpidaapp directory
echo ""
echo "Checking elpidaapp modules..."
ELPIDA_FILES=(
    "divergence_engine.py"
    "ui.py"
    "api.py"
    "scanner.py"
    "governance_client.py"
    "frozen_mind.py"
    "kaya_protocol.py"
    "process_consciousness_queue.py"
)

for file in "${ELPIDA_FILES[@]}"; do
    if [ -f "$DEPLOY_DIR/elpidaapp/$file" ]; then
        echo "  ✓ elpidaapp/$file"
    else
        echo "  ✗ elpidaapp/$file MISSING"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check directories
echo ""
echo "Checking directories..."
if [ -d "$DEPLOY_DIR/elpidaapp/results" ]; then
    echo "  ✓ elpidaapp/results"
else
    echo "  ✗ elpidaapp/results MISSING"
    ERRORS=$((ERRORS + 1))
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $ERRORS -eq 0 ]; then
    echo "✅ Deployment package verification PASSED"
    echo ""
    echo "Package is ready for Hugging Face Spaces!"
    echo ""
    echo "Next steps:"
    echo "1. Read: hf_deployment/DEPLOYMENT_GUIDE.md"
    echo "2. Create HF Space: https://huggingface.co/new-space"
    echo "3. Copy files: cp -r hf_deployment/* /path/to/your-space/"
    echo "4. Configure secrets in HF Space settings"
    echo "5. Push and deploy"
else
    echo "❌ Deployment package verification FAILED"
    echo ""
    echo "Found $ERRORS missing files/directories"
    echo "Run ./package_for_hf.sh again to rebuild"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
