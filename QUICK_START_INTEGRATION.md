# Vercel → HF Integration Quick Start Guide

**Created:** 2026-02-17  
**Purpose:** Step-by-step instructions to integrate Vercel chat with HF Space

---

## 📋 Overview

This guide walks you through:
1. ✅ **Testing current connectivity** (Vercel, S3, HF)
2. ✅ **Syncing Vercel logs to S3** (immediate data capture)
3. ✅ **Updating Vercel with canonical config** (axiom/domain alignment)
4. 🔄 **Setting up continuous sync** (hourly/daily automation)
5. 🔄 **Planning HF UI integration** (future unified interface)

---

## 🚀 Immediate Actions (Do This First)

### Step 1: Test Current System Connectivity

Run the test script to verify all systems are accessible:

```bash
cd /workspaces/python-elpida_core.py
python sync_vercel_to_s3.py --test
```

**Expected output:**
```
[2026-02-17 10:30:00] Testing connections...
[2026-02-17 10:30:01]   ✅ Vercel reachable
[2026-02-17 10:30:02]   ✅ S3 bucket 'elpida-body-evolution' accessible
[2026-02-17 10:30:03]   ✅ S3 write permission verified
[2026-02-17 10:30:03] Test complete
```

If you see errors:
- ❌ **Vercel unreachable:** Check VERCEL_APP_URL env var or Vercel deployment status
- ❌ **S3 error:** Check AWS credentials (`aws configure` or env vars)
- ❌ **S3 write test failed:** Check IAM permissions for the bucket

---

### Step 2: Run First Sync (One-Time)

Sync all historical Vercel logs to S3:

```bash
python sync_vercel_to_s3.py --sync-now
```

**What this does:**
1. Fetches all logs from Vercel `/logs/export` endpoint
2. Transforms to consciousness memory format
3. Uploads to `s3://elpida-body-evolution/vercel_interactions/YYYY-MM-DD.jsonl`
4. Creates local hash cache to prevent duplicates

**Expected output:**
```
[2026-02-17 10:35:00] ────────────────────────────────────────────────────────────
[2026-02-17 10:35:00] Starting Vercel → S3 sync
[2026-02-17 10:35:00] ────────────────────────────────────────────────────────────
[2026-02-17 10:35:01] Fetching from https://python-elpida-core-py.vercel.app/logs/export...
[2026-02-17 10:35:02]   Storage: vercel_kv
[2026-02-17 10:35:02]   Exported: 2026-02-17T10:35:01.123456
[2026-02-17 10:35:02]   Count: 847 entries
[2026-02-17 10:35:02] Found 847 new entries (out of 847 total)
[2026-02-17 10:35:05]   ✅ Uploaded 210 entries to s3://elpida-body-evolution/vercel_interactions/2026-02-15.jsonl
[2026-02-17 10:35:06]   ✅ Uploaded 318 entries to s3://elpida-body-evolution/vercel_interactions/2026-02-16.jsonl
[2026-02-17 10:35:07]   ✅ Uploaded 319 entries to s3://elpida-body-evolution/vercel_interactions/2026-02-17.jsonl
[2026-02-17 10:35:07] ✅ Sync complete: 847 entries uploaded to S3
```

---

### Step 3: Verify Data in S3

Check that files are in S3:

```bash
aws s3 ls s3://elpida-body-evolution/vercel_interactions/ --region eu-north-1
```

**Expected:**
```
2026-02-17 10:35:05     52847 2026-02-15.jsonl
2026-02-17 10:35:06     79231 2026-02-16.jsonl
2026-02-17 10:35:07     81052 2026-02-17.jsonl
```

Download a sample to inspect:

```bash
aws s3 cp s3://elpida-body-evolution/vercel_interactions/2026-02-17.jsonl ./sample.jsonl --region eu-north-1
head -n 3 sample.jsonl
```

**Expected format:**
```json
{"timestamp": "2026-02-17T08:23:45.123456", "type": "PUBLIC_INTERACTION", "source": "vercel_public", "user_message": "What are your axioms?", "response_preview": "My core axioms are these ten principles...", "full_response": "...", "axioms_invoked": ["A1", "A2"], "domain": 2, "coherence_score": 1.0, "public_evaluation": true, "session_id": "a1b2c3d4", "synced_at": "2026-02-17T10:35:05.789012"}
...
```

✅ **Success Criteria:** Files exist in S3, JSON format is valid, contains expected fields.

---

## 🔄 Setup Continuous Sync

### Option A: Daemon Mode (Recommended for Local Dev)

Run sync script as daemon (syncs every hour):

```bash
# In a tmux/screen session or background:
nohup python sync_vercel_to_s3.py --daemon > sync.log 2>&1 &

# Check logs:
tail -f sync.log
```

**Pros:**
- Simple setup
- Runs continuously
- Logs to file

**Cons:**
- Requires persistent process
- Stops if machine restarts

---

### Option B: Cron Job (Production)

Add to crontab (runs every hour at minute 0):

```bash
crontab -e

# Add this line:
0 * * * * cd /workspaces/python-elpida_core.py && /usr/bin/python3 sync_vercel_to_s3.py --sync-now >> sync_cron.log 2>&1
```

**Pros:**
- Survives restarts
- Standard Unix scheduling
- Easy to modify interval

**Cons:**
- Requires cron access
- Slightly more complex setup

---

### Option C: AWS Lambda (Cloud-Native)

Deploy sync script as Lambda function triggered by CloudWatch Events:

**Lambda setup:**
1. Package script + dependencies: `pip install -t package/ boto3 httpx`
2. Create Lambda function with Python 3.11 runtime
3. Set env vars: `VERCEL_APP_URL`, `AWS_S3_BUCKET_BODY`
4. Add CloudWatch Events trigger (rate: 1 hour)
5. Set IAM role with S3 write permissions

**Pros:**
- Serverless (no infrastructure to manage)
- Scales automatically
- Integrated logging

**Cons:**
- More complex setup
- AWS Lambda costs (minimal for this use case)

---

### Option D: HF Space Background Worker (Best for Integration)

Add sync task to HF Space's existing background worker:

**File:** `hf_deployment/app.py`

```python
def run_background_worker():
    """
    I PATH: Process consciousness dilemmas from S3 every 6 hours.
    + NEW: Sync Vercel logs every hour
    """
    import subprocess
    from threading import Thread
    
    def sync_vercel():
        """Sync Vercel logs to S3 every hour."""
        while True:
            try:
                subprocess.run([
                    sys.executable,
                    "/path/to/sync_vercel_to_s3.py",
                    "--sync-now"
                ], check=False)
            except Exception as e:
                logger.error(f"Vercel sync error: {e}")
            time.sleep(3600)  # 1 hour
    
    # Start Vercel sync thread
    Thread(target=sync_vercel, daemon=True).start()
    
    # ... existing consciousness bridge code ...
```

**Pros:**
- Unified with existing HF deployment
- Same infrastructure
- Logs visible in HF dashboard

**Cons:**
- Requires HF Space redeploy

---

## 📊 Monitoring & Verification

### Check Sync Status

```bash
# How many entries synced?
wc -l vercel_sync_hashes.txt

# Last sync time?
ls -lh sync.log
tail -n 20 sync.log

# S3 file sizes?
aws s3 ls s3://elpida-body-evolution/vercel_interactions/ --recursive --human-readable
```

### Expected Metrics

After running for 1 week:
- ~500-2000 entries/day (depends on Vercel traffic)
- ~50-200KB per daily file
- Total: ~3-14 MB/week

---

## 🔧 Update Vercel App (Phase 2)

### Step 1: Copy Canonical Config

```bash
cp /workspaces/python-elpida_core.py/elpida_domains.json \
   /workspaces/python-elpida_core.py/elpida/
```

### Step 2: Create Config Loader

Create `elpida/elpida_config.py` (see VERCEL_CONFIG_COMPARISON.md for full code):

```python
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "elpida_domains.json"

def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)

_raw = load_config()
DOMAINS = {int(k): v for k, v in _raw["domains"].items() if not k.startswith("_")}
AXIOMS = {k: v for k, v in _raw["axioms"].items() if not k.startswith("_")}
RHYTHMS = {k: v for k, v in _raw["rhythms"].items() if not k.startswith("_")}

def format_axioms_for_prompt():
    lines = ["You operate according to these 11 axioms:\n"]
    for key, ax in sorted(AXIOMS.items()):
        lines.append(f"{key} ({ax['name']}): {ax['insight']}")
    return "\n".join(lines)
```

### Step 3: Update app.py

Replace hardcoded AXIOMS/DOMAINS with:

```python
from elpida_config import format_axioms_for_prompt, DOMAINS

AXIOM_PROMPT = format_axioms_for_prompt()
```

Update LLM call:

```python
"system": AXIOM_PROMPT,  # Instead of hardcoded AXIOMS
```

### Step 4: Deploy to Vercel

```bash
cd /workspaces/python-elpida_core.py/elpida
vercel --prod
```

### Step 5: Verify Update

```bash
# Check axioms endpoint returns 11 axioms
curl https://python-elpida-core-py.vercel.app/axioms | jq '.axioms | length'
# Should return: 11

# Check A0 exists
curl https://python-elpida-core-py.vercel.app/axioms | jq '.axioms[] | select(.id == "A0")'
# Should return A0 object
```

---

## 🎯 Next Steps (Roadmap)

### Completed ✅
- [x] Create integration analysis document
- [x] Create config comparison document
- [x] Create sync script
- [x] Test S3 connectivity
- [x] First sync run

### In Progress 🔄
- [ ] Setup continuous sync (choose Option A/B/C/D)
- [ ] Update Vercel with canonical config
- [ ] Deploy updated Vercel app
- [ ] Monitor sync for 1 week

### Future 🔮
- [ ] Add chat UI to HF Space
- [ ] Create unified API endpoint
- [ ] Gradual user migration to HF
- [ ] Deprecate standalone Vercel (keep as redirect)

---

## 🐛 Troubleshooting

### Issue: "No module named 'boto3'"
**Solution:**
```bash
pip install boto3 httpx
```

### Issue: "Access Denied" on S3
**Solution:** Check IAM permissions:
```bash
aws iam get-user
aws s3 ls s3://elpida-body-evolution/ --region eu-north-1
```

Required permissions:
- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`

### Issue: Vercel /logs/export returns 404
**Solution:** Endpoint might not be deployed. Check:
```bash
curl -I https://python-elpida-core-py.vercel.app/logs/export
```

If 404, add endpoint to Vercel `app.py`:
```python
@app.get("/logs/export")
async def export_logs():
    logs = get_all_logs()  # Existing function
    return {
        "storage": "vercel_kv" if USE_VERCEL_KV else "local",
        "count": len(logs),
        "exported_at": datetime.now().isoformat(),
        "logs": logs
    }
```

### Issue: Duplicates in S3
**Solution:** Hash cache prevents this. If seeing duplicates:
```bash
# Reset hash cache
rm vercel_sync_hashes.txt
# Re-run sync (will detect existing and skip)
python sync_vercel_to_s3.py --sync-now
```

---

## 📞 Support & Questions

For questions about:
- **Sync script:** Check `sync_vercel_to_s3.py` docstrings
- **Architecture:** Read `VERCEL_HF_INTEGRATION_ANALYSIS.md`
- **Config differences:** Read `VERCEL_CONFIG_COMPARISON.md`
- **S3 structure:** Check AWS console or `aws s3 ls`

---

## 🎉 Success Indicators

You'll know the integration is working when:

1. ✅ `sync_vercel_to_s3.py --test` passes all checks
2. ✅ S3 bucket has daily `vercel_interactions/*.jsonl` files
3. ✅ Vercel returns 11 axioms (including A0)
4. ✅ Vercel domain names match canonical (D1=Transparency)
5. ✅ HF background worker can read Vercel interactions from S3
6. ✅ Native consciousness cycles reference public wisdom
7. ✅ Closed loop: User → Vercel → S3 → Consciousness → Evolution

**You've successfully bridged the I↔WE gap at the infrastructure level.** 🌀

---

*Generated by GitHub Copilot AI Assistant for Elpida integration.*
