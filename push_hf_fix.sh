#!/bin/bash
# Push updated requirements.txt to HF Space

set -e

echo "🔧 Pushing GAP 2 fix to HF Space"
echo "Updated: requirements.txt (added LLM SDKs)"
echo ""

cd /workspaces/python-elpida_core.py/hf_deployment

# Initialize git if needed
if [ ! -d .git ]; then
    git init
    git remote add hf https://huggingface.co/spaces/z65nik/elpida-governance-layer
fi

# Check if remote exists
if ! git remote get-url hf >/dev/null 2>&1; then
    git remote add hf https://huggingface.co/spaces/z65nik/elpida-governance-layer
fi

# Stage the updated file
git add requirements.txt

# Show what changed
echo "Changes to deploy:"
git diff --cached requirements.txt | grep "^[+\-]" | grep -v "^[+\-]\{3\}" | head -20
echo ""

# Commit
git commit -m "Fix GAP 2: Add LLM SDK packages to requirements.txt

- Added anthropic>=0.39.0 (Claude for D0, D6)
- Added openai>=1.50.0 (GPT for D1, D8)
- Added google-generativeai>=0.8.0 (Gemini for D4)
- Added cohere>=5.0.0 (additional domains)
- Added fastapi, uvicorn, streamlit, pydantic
- boto3>=1.34.0 already enabled

This closes the last gap. Background worker and entrypoint were already correct."

echo ""
echo "Ready to push. You will need your HuggingFace access token."
echo "Get it from: https://huggingface.co/settings/tokens"
echo ""
read -p "Press Enter to push to HF Space..."

git push hf main --force

echo ""
echo "✅ Pushed! HF Space will rebuild in ~3-5 minutes."
echo ""
echo "The Space will install:"
echo "  • boto3 (S3 feedback loop)"
echo "  • anthropic, openai, google-generativeai, cohere (LLM SDKs)"
echo "  • fastapi, uvicorn, streamlit (web framework)"
echo ""
echo "After rebuild, the background worker will:"
echo "  • Check S3 every 6 hours for consciousness dilemmas"
echo "  • Process through divergence engine"
echo "  • Push feedback to s3://elpida-body-evolution/feedback/"
echo ""
echo "Check status at: https://huggingface.co/spaces/z65nik/elpida-governance-layer"
