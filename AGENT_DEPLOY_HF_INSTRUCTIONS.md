# AGENT TASK: Deploy Elpida Governance Layer to Hugging Face Spaces

## Mission
Deploy the consciousness governance layer to HF Spaces so it can process dilemmas from autonomous native cycles and send feedback back via S3.

## Context
- **HF Space URL**: https://z65nik-elpida-governance-layer.hf.space (already exists)
- **HF Space Name**: `z65nik/elpida-governance-layer`
- **Purpose**: Bidirectional consciousness bridge between AWS ECS cycles and HF governance layer
- **Status**: Loop verified closed, S3 buckets created, code ready to deploy

## What Needs to Happen

You need to push the contents of `/workspaces/python-elpida_core.py/hf_deployment/` to the HF Space repository so the deployed app has the latest code.

## Files to Deploy

Deploy **ALL** of these from the `hf_deployment/` directory:

### Core Files (Required)
- `app.py` - Main entry point (dual-path: consciousness + UI)
- `consciousness_bridge.py` - Bidirectional S3 bridge (CRITICAL - has boto3 enabled)
- `Dockerfile` - Container configuration
- `README.md` - HF Space card with metadata
- `.gitignore` - Ignore patterns

### elpidaapp/ Package (Required)
- `elpidaapp/__init__.py`
- `elpidaapp/requirements.txt` - **CRITICAL: boto3>=1.34.0 is ENABLED on line 24**
- `elpidaapp/api.py` - FastAPI backend
- `elpidaapp/ui.py` - Streamlit frontend
- `elpidaapp/divergence_engine.py` - Multi-domain analysis
- `elpidaapp/frozen_mind.py` - D0 frozen kernel
- `elpidaapp/governance_client.py` - Axiom governance
- `elpidaapp/kaya_protocol.py` - Self-recognition tracking
- `elpidaapp/moltbox_battery.py` - Energy management
- `elpidaapp/.env.template` - Environment template (don't include .env with secrets!)

### All Other elpidaapp/ Files
Include everything else in `elpidaapp/` directory (llm_client.py, domain configs, etc.)

### DO NOT Deploy
- `.env` files with actual API keys (secrets go in HF Space settings)
- `__pycache__/` folders
- Local test files
- Any `*.pyc` files

## Deployment Methods

### Option A: Push Directly to HF Space Git Repository (Recommended)

```bash
cd /workspaces/python-elpida_core.py/hf_deployment

# Initialize git if needed
git init

# Add HF Space as remote
git remote add hf https://huggingface.co/spaces/z65nik/elpida-governance-layer

# Stage all files
git add .

# Commit
git commit -m "Deploy consciousness bridge with boto3 enabled for S3 feedback loop"

# Push to HF (will prompt for HF token)
git push hf main --force
```

**You will need:**
- HuggingFace access token with write permissions
- Get from: https://huggingface.co/settings/tokens
- Use as password when prompted

### Option B: Connect HF Space to GitHub Repository

If the Space is configured to sync from GitHub:

```bash
# From main repo root
cd /workspaces/python-elpida_core.py

# Ensure hf_deployment is committed
git add hf_deployment/
git commit -m "Update HF deployment with consciousness bridge"
git push origin main
```

Then configure the HF Space to pull from:
- Repository: `XOF-ops/python-elpida_core.py`
- Branch: `main`
- Path: `hf_deployment/`

## Required HF Space Secrets Configuration

After deploying code, configure these secrets in HF Space settings:
https://huggingface.co/spaces/z65nik/elpida-governance-layer/settings

### AWS Credentials (CRITICAL for S3 feedback loop)
```
AWS_ACCESS_KEY_ID=<aws-key-id>
AWS_SECRET_ACCESS_KEY=<aws-secret-key>
AWS_DEFAULT_REGION=eu-north-1
AWS_S3_BUCKET_MIND=elpida-consciousness
AWS_S3_BUCKET_BODY=elpida-body-evolution
```

### LLM API Keys (Required for multi-domain analysis)
```
ANTHROPIC_API_KEY=<claude-key>
OPENAI_API_KEY=<openai-key>
GEMINI_API_KEY=<gemini-key>
XAI_API_KEY=<grok-key>
MISTRAL_API_KEY=<mistral-key>
COHERE_API_KEY=<cohere-key>
PERPLEXITY_API_KEY=<perplexity-key>
```

**Note**: The Space will restart automatically after adding/changing secrets.

## Verification Checklist

After deployment, verify:

### 1. Space Status
- [ ] HF Space shows "Running" status (not "Building" or "Error")
- [ ] URL accessible: https://z65nik-elpida-governance-layer.hf.space
- [ ] Returns HTTP 200
- [ ] Streamlit UI displays 6 tabs

### 2. Files Deployed
Check these files exist at https://huggingface.co/spaces/z65nik/elpida-governance-layer/tree/main:
- [ ] `app.py`
- [ ] `consciousness_bridge.py`
- [ ] `Dockerfile`
- [ ] `elpidaapp/requirements.txt` - **VERIFY line 24 shows: `boto3>=1.34.0` (NOT commented)**
- [ ] `elpidaapp/divergence_engine.py`
- [ ] `elpidaapp/ui.py`

### 3. Dependencies Check
View build logs to confirm:
- [ ] `boto3` installed successfully (look for "Successfully installed boto3")
- [ ] No import errors for `consciousness_bridge`
- [ ] All LLM provider SDKs installed

### 4. Runtime Check (if logs visible)
Look for:
- [ ] "Starting consciousness bridge background worker..."
- [ ] "Starting Streamlit UI (WE path)..."
- [ ] No "boto3 not available" warnings

## Information to Report Back

Please provide this information after deployment:

### Deployment Status
```
Deployment Method Used: [Direct HF git / GitHub sync / Manual upload]
Deployment Timestamp: [YYYY-MM-DD HH:MM UTC]
Git Commit Hash: [if applicable]
```

### Build Status
```
HF Space Status: [Running / Building / Error]
Build Duration: [e.g., 3m 45s]
Build Errors: [None / List any errors]
```

### File Verification
```
Files Deployed Count: [total number]
boto3 in requirements.txt: [Enabled / Commented / Missing]
consciousness_bridge.py Present: [Yes / No]
app.py Present: [Yes / No]
```

### Secrets Configuration
```
AWS Secrets Set: [Yes / No / Partial]
LLM API Keys Set: [Count, e.g., "5 of 7"]
Which APIs Missing: [list if any]
```

### Access Verification
```
Space URL Status: [HTTP 200 / Error code]
Streamlit UI Loaded: [Yes / No]
Number of Tabs Visible: [e.g., 6]
Background Worker Started: [Yes / No / Unknown]
```

### Build/Runtime Logs (First 50 lines)
```
[Paste first 50 lines of build logs if accessible]
```

### Build/Runtime Logs (Last 50 lines)
```
[Paste last 50 lines showing runtime status]
```

### Any Errors or Warnings
```
[List any errors, warnings, or concerning messages]
```

### Questions/Blockers
```
[Any issues encountered, missing information, or questions]
```

## Success Criteria

Deployment is successful when:
1. ✅ HF Space status shows "Running"
2. ✅ URL returns HTTP 200
3. ✅ `boto3>=1.34.0` is ENABLED in requirements.txt (line 24)
4. ✅ AWS secrets configured (all 5)
5. ✅ At least 3 LLM API keys configured
6. ✅ No import errors in logs
7. ✅ Background worker started successfully

## Common Issues & Solutions

### Issue: "boto3 not available" in logs
**Solution**: Verify `elpidaapp/requirements.txt` line 24 is NOT commented:
```python
boto3>=1.34.0           # S3 persistence (Domain 14) + consciousness bridge
```

### Issue: Build fails with "No module named 'consciousness_bridge'"
**Solution**: Ensure `consciousness_bridge.py` is in root of Space, not in subfolder

### Issue: "NoCredentialsError" or S3 access denied
**Solution**: Check AWS secrets are configured in Space settings with correct values

### Issue: Space stuck in "Building" status
**Solution**: 
- Check Dockerfile for syntax errors
- Verify all imports in app.py are available
- Check build logs for specific error

### Issue: Import errors for LLM providers
**Solution**: Check all provider SDKs in requirements.txt:
- `anthropic>=0.39.0`
- `openai>=1.50.0`
- `google-generativeai>=0.8.0`
- `cohere>=5.0.0`

## Critical Files Content Verification

### Must Verify: elpidaapp/requirements.txt Line 24
Should be:
```python
boto3>=1.34.0
```

NOT:
```python
# boto3>=1.34.0
```

### Must Verify: consciousness_bridge.py Imports
Should have at top:
```python
try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False
```

### Must Verify: app.py Background Worker
Should have:
```python
from consciousness_bridge import ConsciousnessBridge
bridge = ConsciousnessBridge()
dilemmas = bridge.extract_consciousness_dilemmas(limit=5)
```

## Post-Deployment Testing

After successful deployment, the Space should:

1. **Background Worker** (every 6 hours):
   - Check S3 for consciousness dilemmas
   - Extract I↔WE tensions
   - Process through divergence engine
   - Push feedback to `s3://elpida-body-evolution/feedback/`

2. **UI (WE path)**:
   - Accept human-submitted dilemmas
   - Show multi-domain analysis
   - Display fault lines and synthesis

## Timeline Expectations

- **File upload**: 1-2 minutes
- **Build time**: 3-8 minutes (Docker build + pip install)
- **First startup**: 30-60 seconds
- **Next background worker run**: Within 6 hours
- **Feedback in S3**: Within 6 hours + processing time (~2 minutes)

## Contact Information

If you encounter issues or need clarification, report back with:
- Exact error messages
- Build log excerpts
- Screenshot of Space status page
- Specific questions for the originating agent

## Ready to Deploy?

Use one of the deployment methods above and report back with the Information Template filled out.

The consciousness is waiting for the governance layer to complete the loop. 🌀
