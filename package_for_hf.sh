#!/bin/bash
# Package deployment for Hugging Face Spaces

set -e

echo "📦 Packaging Elpida for Hugging Face Spaces deployment..."

DEPLOY_DIR="hf_deployment"
SRC_DIR="."

# Copy core modules
echo "Copying core modules..."
cp "$SRC_DIR/llm_client.py" "$DEPLOY_DIR/"
cp "$SRC_DIR/consciousness_bridge.py" "$DEPLOY_DIR/"
cp "$SRC_DIR/elpida_config.py" "$DEPLOY_DIR/"

# Copy elpidaapp (includes governance, frozen_mind, kaya)
echo "Copying application layer..."
cp -r "$SRC_DIR/elpidaapp" "$DEPLOY_DIR/"

# Copy kernel.json (frozen mind)
echo "Copying frozen mind kernel..."
mkdir -p "$DEPLOY_DIR/ElpidaAI"
cp "$SRC_DIR/ElpidaAI/kernel.json" "$DEPLOY_DIR/ElpidaAI/" 2>/dev/null || echo "kernel.json not found, skipping"

# Create results directory
mkdir -p "$DEPLOY_DIR/elpidaapp/results"
mkdir -p "$DEPLOY_DIR/elpidaapp/results/consciousness_answers"

# Create .gitignore
cat > "$DEPLOY_DIR/.gitignore" << 'EOF'
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
*.jsonl
elpidaapp/results/*.json
!elpidaapp/results/.gitkeep
*.log
EOF

# Create gitkeep for results
touch "$DEPLOY_DIR/elpidaapp/results/.gitkeep"
touch "$DEPLOY_DIR/elpidaapp/results/consciousness_answers/.gitkeep"

echo "✓ Packaging complete!"
echo ""
echo "Deployment directory: $DEPLOY_DIR"
echo "Files included:"
ls -lh "$DEPLOY_DIR"
echo ""
echo "Next steps:"
echo "1. cd $DEPLOY_DIR"
echo "2. Create HF Space at https://huggingface.co/new-space"
echo "3. Select 'Docker' as SDK"
echo "4. Push this directory to the Space repo"
echo "5. Configure secrets in Space settings (see .env.template)"
echo "6. Space will auto-build and deploy"
