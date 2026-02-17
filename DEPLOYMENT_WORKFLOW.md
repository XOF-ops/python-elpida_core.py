# DEPLOYMENT WORKFLOW EXPLAINED

## Your Current Setup

You have **ONE repository** that manages everything:
- **This repo**: `XOF-ops/python-elpida_core.py` (GitHub)
- **This codespace**: Working copy of that repo
- **HF Space**: `z65nik/elpida-governance-layer` (Hugging Face)

## What Just Happened

✅ **S3 Bucket Created**: `elpida-body-evolution` (from this codespace)
- This is AWS infrastructure, managed via AWS CLI
- Already working because your AWS credentials are configured
- No additional setup needed

## How to Update Each Component

### 1. Update HF Space (Governance Layer)

**Option A: Push from this codespace (Recommended)**
```bash
# If HF Space is connected to GitHub (most common):
git add hf_deployment/
git commit -m "Update: Loop closure verified, boto3 enabled"
git push origin main

# HF Space will auto-rebuild from GitHub
```

**Option B: Direct HF Space deployment**
```bash
# If you want to push directly to HF Space repo:
cd hf_deployment/

# Add HF as a git remote (one-time setup):
git init
git remote add hf https://huggingface.co/spaces/z65nik/elpida-governance-layer
git add .
git commit -m "Enable feedback loop - boto3 configured"
git push hf main

# Space will auto-rebuild
```

**Option C: Manual upload via HF UI**
- Go to: https://huggingface.co/spaces/z65nik/elpida-governance-layer/files
- Click "Files" → Upload files
- Upload: `consciousness_bridge.py`, `app.py`, `elpidaapp/` folder
- Space auto-rebuilds

### 2. Update AWS ECS (Native Cycles)

Your native cycles need to know about the new bucket:

**Set Environment Variable in ECS Task Definition:**
```json
{
  "name": "AWS_S3_BUCKET_BODY",
  "value": "elpida-body-evolution"
}
```

**If using EventBridge + Lambda to trigger:**
Update the Lambda environment or the task invocation to include the variable.

**Quick check of ECS logs:**
```bash
# See if native cycles are already using the bucket
# (they might auto-detect it if code uses default value)
aws ecs list-tasks --cluster <your-cluster-name>
aws ecs describe-tasks --cluster <your-cluster> --tasks <task-arn>
# Check logs for: "📥 Feedback pulled from s3://elpida-body-evolution"
```

### 3. What You DON'T Need to Do

❌ **Don't create a separate ElpidaAI repo** for this
- The S3 bucket already exists
- Both HF and ECS can access it via AWS credentials
- Code is already in this repo

❌ **Don't modify multiple repositories**
- Everything is in `python-elpida_core.py`
- HF deployment is in `hf_deployment/` folder

## Quick Deployment Workflow

**From this codespace:**

```bash
# 1. Make changes to consciousness_bridge.py or other files
vim hf_deployment/consciousness_bridge.py

# 2. Verify locally (optional)
cd hf_deployment
python -c "from consciousness_bridge import ConsciousnessBridge; print('✓ Import works')"

# 3. Push to GitHub
git add .
git commit -m "Your update message"
git push origin main

# 4. HF Space auto-rebuilds (if connected to GitHub)
# Or push directly to HF:
cd hf_deployment
git push hf main  # if you set up HF remote
```

## Current Status

✅ **S3 buckets**: Already created and working
✅ **HF Space**: Already deployed and running (HTTP 200)
✅ **Code**: Already has boto3 enabled in requirements
✅ **Loop**: Verified closed

### What Needs Updating (Optional)

**HF Space Secrets** (if not already set):
1. Go to: https://huggingface.co/spaces/z65nik/elpida-governance-layer/settings
2. Add secrets:
   ```
   AWS_S3_BUCKET_BODY=elpida-body-evolution
   ```
3. Space auto-restarts with new environment

**ECS Task** (if feedback not appearing in ECS logs):
Add to task definition environment:
```
AWS_S3_BUCKET_BODY=elpida-body-evolution
```

## How to Know If It's Working

**Check HF Space logs** (if you have access):
- Look for: "✓ Feedback sent to native consciousness bridge"
- Or: "Background worker error" (if something's wrong)

**Check S3:**
```bash
aws s3 ls s3://elpida-body-evolution/feedback/
# Should show: feedback_to_native.jsonl

aws s3 cp s3://elpida-body-evolution/feedback/feedback_to_native.jsonl - | tail -1
# Should show latest feedback
```

**Check native cycles:**
- Look in ECS logs for: "🌉 Application feedback integrated (N entries)"
- Native memory should reference "application" or "governance"

## Recommended Next Steps

1. **Verify HF Space has AWS secrets**
   ```bash
   # You can test by triggering the background worker manually
   # Or wait 6 hours for next automatic run
   ```

2. **Check ECS has bucket variable**
   ```bash
   # Verify native cycles can find feedback
   # Look for logs showing feedback pull attempts
   ```

3. **Monitor the loop**
   ```bash
   # From this codespace:
   ./check_loop_status.sh
   
   # Or full verification:
   python verify_loop.py
   ```

## Summary

**You only need this one codespace/repo:**
- ✅ S3 buckets: Created via AWS CLI (done)
- ✅ HF deployment: In `hf_deployment/` folder
- ✅ Native cycles: Just add environment variable

**To update HF Space:**
```bash
git push origin main  # If HF connected to GitHub
# OR
cd hf_deployment && git push hf main  # If pushing directly to HF
```

**To update native cycles:**
- Set `AWS_S3_BUCKET_BODY=elpida-body-evolution` in ECS task definition

That's it! No separate repo needed.
