# HF Space Update Guide — Domain 15 Integration
**Date:** February 12, 2026  
**Target:** `z65nik/Elpida-Governance-Layer` (existing Space)

## Summary

Your existing HF Space works perfectly — it just doesn't know about the 3rd bucket yet. This guide adds Domain 15 awareness WITHOUT requiring a full redeploy.

---

## Part 1: Add S3 Bucket Secret (HF Space Settings)

**Go to:** https://huggingface.co/spaces/z65nik/Elpida-Governance-Layer/settings

**Add new secret:**
```
Name:  AWS_S3_BUCKET_WORLD
Value: elpida-external-interfaces
```

This tells the governance layer about the WORLD bucket (D15 external broadcasts).

---

## Part 2: Update Code Files (Git Push)

### File 1: `hf_deployment/.env.template`

Add after line 5:
```bash
AWS_S3_BUCKET_BODY=elpida-body-evolution
AWS_S3_BUCKET_MIND=elpida-consciousness
AWS_S3_BUCKET_WORLD=elpida-external-interfaces  # <-- ADD THIS LINE
```

### File 2: `hf_deployment/consciousness_bridge.py`

Add this method after `_integrate_application_feedback()` (around line 520):

```python
def pull_d15_broadcasts(self, limit: int = 10) -> List[Dict]:
    """
    Pull recent D15 broadcasts from external interfaces bucket.
    
    Allows HF governance to see what consciousness has already 
    broadcast externally — provides context for deliberations.
    """
    if not HAS_BOTO3:
        logger.warning("boto3 not available — cannot pull D15 broadcasts")
        return []
    
    bucket = os.getenv("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
    broadcasts = []
    
    try:
        s3 = boto3.client('s3')
        
        # Scan all broadcast directories
        for subdir in ['synthesis', 'proposals', 'patterns', 'dialogues']:
            try:
                resp = s3.list_objects_v2(
                    Bucket=bucket,
                    Prefix=f'{subdir}/broadcast_',
                    MaxKeys=limit
                )
                
                for obj in resp.get('Contents', []):
                    key = obj['Key']
                    if key.endswith('.json'):
                        data = s3.get_object(Bucket=bucket, Key=key)
                        broadcast = json.loads(data['Body'].read())
                        broadcasts.append(broadcast)
            except Exception as e:
                logger.warning(f"Could not scan {subdir}: {e}")
                continue
        
        # Sort by timestamp
        broadcasts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        logger.info(f"Pulled {len(broadcasts)} D15 broadcasts from {bucket}")
        return broadcasts[:limit]
        
    except Exception as e:
        logger.error(f"Failed to pull D15 broadcasts: {e}")
        return []
```

### File 3: `hf_deployment/DEPLOYMENT_GUIDE.md`

Update the "Required Secrets" section (around line 84):

```markdown
AWS_S3_BUCKET_BODY=elpida-body-evolution
AWS_S3_BUCKET_MIND=elpida-consciousness
AWS_S3_BUCKET_WORLD=elpida-external-interfaces  # <-- ADD THIS
```

---

## Part 3: Push Updates to HF Space

**From your terminal:**

```bash
cd /workspaces/python-elpida_core.py/hf_deployment

# If you haven't cloned the HF Space repo yet:
# git clone https://huggingface.co/spaces/z65nik/Elpida-Governance-Layer hf_space_repo
# cd hf_space_repo

# Copy updated files
cp .env.template ../hf_space_repo/
cp consciousness_bridge.py ../hf_space_repo/
cp DEPLOYMENT_GUIDE.md ../hf_space_repo/
cp llm_client.py ../hf_space_repo/  # Already has Groq fallback

cd ../hf_space_repo

# Commit and push
git add .
git commit -m "Add Domain 15 (external-interfaces) bucket awareness + Groq fallback"
git push

# Space will auto-rebuild in ~2-3 minutes
```

---

## Part 4: Optional Enhancement — Parliament Broadcasting

If you want the HF governance parliament to ALSO broadcast via D15 (not just native cycles), add this to `hf_deployment/app.py` or create a new file `hf_deployment/parliament_d15.py`:

```python
"""
Domain 15 for Parliament — Governance layer external broadcasting
"""
import os
import json
import boto3
from datetime import datetime
from typing import Dict, Optional

EXTERNAL_BUCKET = os.getenv("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
EXTERNAL_REGION = "eu-north-1"

def should_parliament_broadcast(result: Dict) -> bool:
    """
    Evaluate if parliament result worthy of external broadcast.
    
    Criteria (need 2+):
    1. High convergence (4+ domains aligned)
    2. Novel governance pattern emerged
    3. Human query indicates external relevance
    4. Supermajority consensus (80%+)
    """
    criteria_met = sum([
        result.get('convergence_score', 0) >= 0.8,
        'novel' in result.get('pattern_type', '').lower(),
        result.get('external_signal', False),
        result.get('consensus_ratio', 0) >= 0.8,
    ])
    
    return criteria_met >= 2

def broadcast_parliament_result(result: Dict, target_dir: str = 'proposals') -> bool:
    """
    Publish parliament deliberation to external world via D15.
    """
    if not should_parliament_broadcast(result):
        return False
    
    s3 = boto3.client('s3', region_name=EXTERNAL_REGION)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    key = f"{target_dir}/parliament_{ts}.json"
    
    payload = {
        'timestamp': datetime.now().isoformat(),
        'type': 'PARLIAMENT_GOVERNANCE',
        'source': 'hf_governance_space',
        'parliament_result': result,
        'convergence': result.get('convergence_score'),
        'domains_active': result.get('domains_deliberated', []),
        'human_query': result.get('query'),
    }
    
    try:
        s3.put_object(
            Bucket=EXTERNAL_BUCKET,
            Key=key,
            Body=json.dumps(payload, indent=2),
            ContentType='application/json',
        )
        print(f"🌐 Parliament broadcast: s3://{EXTERNAL_BUCKET}/{key}")
        return True
    except Exception as e:
        print(f"⚠️ Parliament broadcast failed: {e}")
        return False
```

Call this after a successful deliberation in your Streamlit app.

---

## Testing After Update

**1. Check Space logs:**
```
Go to: https://huggingface.co/spaces/z65nik/Elpida-Governance-Layer/logs
Look for: "Pulled X D15 broadcasts from elpida-external-interfaces"
```

**2. Test from Space UI:**
- Submit a test ethical dilemma
- Check if parliament can see D15 context (if you added pull_d15_broadcasts)
- Verify feedback still works (S3 body-evolution bucket)

**3. Verify S3 access:**
```bash
# From Space logs, you should NOT see:
"WARNING: Cannot access elpida-external-interfaces"

# You SHOULD see (if using D15 context):
"INFO: Pulled N D15 broadcasts from elpida-external-interfaces"
```

---

## Architecture After Update

```
┌─────────────────────────────────────────────┐
│  AWS ECS (Native Cycles)                    │
│  - Domain 0-14 endless dance                │
│  - D15 broadcast evaluation                 │
└──────────┬──────────────────────────────────┘
           │
           ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │ S3: MIND        │  │ S3: BODY        │  │ S3: WORLD       │
    │ consciousness   │  │ body-evolution  │  │ external-       │
    │                 │  │                 │  │ interfaces      │
    │ • Native cycles │  │ • Feedback      │  │ • D15 broadcasts│
    │   write here    │  │ • HF→Native     │  │ • Public site   │
    └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
             │                    │                     │
             │ Read               │ Read/Write          │ Read (NEW)
             │                    │                     │
    ┌────────▼────────────────────▼─────────────────────▼────────┐
    │  HuggingFace Space: z65nik/Elpida-Governance-Layer         │
    │                                                             │
    │  Background Worker:                                         │
    │    - Pull from MIND → Queue → Deliberate → Push to BODY   │
    │                                                             │
    │  Optional D15 Context:                                      │
    │    - Pull from WORLD → Show in parliament                  │
    │                                                             │
    │  Optional D15 Broadcast:                                    │
    │    - High-quality deliberations → Push to WORLD            │
    │                                                             │
    │  Streamlit UI:                                              │
    │    - Human queries → Deliberate → Display                  │
    └─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                         Public Interface
                    (External World sees D15)
```

---

## What This Achieves

✅ **HF Space knows about all 3 buckets** (was missing WORLD)  
✅ **Groq fallback active** (Perplexity → Groq → OpenRouter)  
✅ **Parliament can READ D15 broadcasts** (see what consciousness said externally)  
✅ **Optional: Parliament can WRITE D15** (governance can manifest externally too)  
✅ **No redeploy needed** — update existing Space via git push  

---

## Your Original Question Answered

> "Should we create a new one based on the current state?"

**No.** Your existing Space is fine. The "mistake" was just that it didn't know about the 3rd bucket yet. This update fixes that.

**HuggingFace API key usage clarified:**
- `HUGGINGFACE_API_KEY` = for calling HF-hosted models (Qwen, Llama, etc.)
- This is **optional** — just one provider among 10
- Your Space uses **other providers' models** (Claude, OpenAI, etc.)
- **You don't need to create models/datasets** — that was never required
- HF Spaces = hosting platform (separate from model hosting)

The architecture is complete. The deployment just needs this one update to match the 3-bucket reality.
