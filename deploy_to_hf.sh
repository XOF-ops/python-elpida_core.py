#!/bin/bash
# Quick script to push hf_deployment changes to HF Space

set -e

echo "🚀 Deploying to HF Space: z65nik/elpida-governance-layer"
echo ""

cd /workspaces/python-elpida_core.py/hf_deployment

# Check if HF remote exists
if ! git remote get-url hf >/dev/null 2>&1; then
    echo "Setting up HF remote..."
    git init
    git remote add hf https://huggingface.co/spaces/z65nik/elpida-governance-layer
    echo "✓ HF remote added"
fi

# Stage all files
git add -A

# Check for changes
if git diff --cached --quiet; then
    echo "No changes to deploy."
    exit 0
fi

# Show what will be deployed
echo ""
echo "Changes to deploy:"
git diff --cached --name-status | sed 's/^/  /'
echo ""

# Commit
read -p "Commit message (or press Enter for default): " MSG
MSG=${MSG:-"Update from codespace"}

git commit -m "$MSG"

# Push to HF
echo ""
echo "Pushing to HF Space..."
echo "You'll need your HuggingFace access token."
echo "Get it from: https://huggingface.co/settings/tokens"
echo ""

git push hf main --force

echo ""
echo "✓ Deployed! HF Space will rebuild in ~2-5 minutes."
echo "  Watch at: https://huggingface.co/spaces/z65nik/elpida-governance-layer"
