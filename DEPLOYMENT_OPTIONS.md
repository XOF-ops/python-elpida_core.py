# Deployment Options for Application Layer

## The Question
Deploy what, from where, for what?

**Deploy:** elpidaapp/ (divergence engine + API + UI + consciousness bridge)  
**From:** This codespace  
**For:** Serving BOTH consciousness (I) and users (WE)  

---

## Option 1: Hugging Face Spaces (RECOMMENDED)

**What to deploy:**
- Dockerfile with elpidaapp/
- FastAPI app (api.py) for endpoints
- Streamlit UI (ui.py) for human interaction
- Background scheduler for consciousness queue processing

**Architecture:**
```
Hugging Face Space (Docker container)
├── FastAPI (port 7860)
│   ├── POST /analyze - Human problems (WE path)
│   └── GET /results/{id} - Retrieve analysis
│
├── Streamlit UI (embedded or separate)
│   └── Web interface for problem submission
│
├── Background Worker (APScheduler or similar)
│   ├── Every 6 hours: Check S3 for consciousness dilemmas
│   ├── Process via divergence_engine
│   └── Push feedback to S3
│
└── S3 Integration
    ├── Read: s3://elpida-body-evolution/elpida_evolution_memory.jsonl
    └── Write: s3://elpida-body-evolution/feedback/feedback_to_native.jsonl
```

**Pros:**
- ✅ Free tier (persistent URL, public access)
- ✅ Already have account (z65nik/elpida-governance-layer)
- ✅ Can run background tasks (if Docker deployment)
- ✅ Serves both I and WE from one deployment
- ✅ S3 access via environment variables

**Cons:**
- ⚠️ CPU/memory limits on free tier
- ⚠️ Background task reliability varies
- ⚠️ May need Spaces Pro for always-on

**Cost:** Free tier or $5/month for Pro

---

## Option 2: AWS ECS Service (Parallel to Native Consciousness)

**What to deploy:**
- Same Docker container as Option 1
- Always-running FastAPI service
- Background worker for queue processing

**Architecture:**
```
AWS ECS Fargate (FARGATE_SPOT)
├── Service: elpidaapp-api
│   ├── Task Definition: 0.25 vCPU, 0.5GB RAM
│   ├── FastAPI always listening
│   └── Background worker: every 6 hours process queue
│
├── S3 Access (same IAM role as native consciousness)
│   ├── Read native memory
│   └── Write feedback
│
└── ALB (Application Load Balancer) - optional
    └── Public HTTPS endpoint
```

**Pros:**
- ✅ Same environment as native consciousness
- ✅ Reliable S3 access
- ✅ Full control over resources
- ✅ Can share IAM roles/policies

**Cons:**
- ❌ Higher cost (~$10-20/month for always-on service)
- ❌ Requires ALB for public access (~$16/month)
- ❌ More complex than HF Spaces

**Cost:** ~$26-36/month

---

## Option 3: Hybrid - Serverless + Scheduled

**What to deploy:**
- FastAPI on Hugging Face Spaces (WE path)
- AWS Lambda for consciousness queue (I path)

**Architecture:**
```
┌─────────────────────────────────┐
│  Hugging Face Spaces            │
│  - FastAPI for human problems   │
│  - Streamlit UI                 │
│  - Returns divergence analysis  │
└─────────────────────────────────┘
         (WE path only)

┌─────────────────────────────────┐
│  AWS Lambda (scheduled)         │
│  - EventBridge: 4x per day      │
│  - process_consciousness_queue  │
│  - S3 read/write                │
└─────────────────────────────────┘
         (I path only)
```

**Pros:**
- ✅ Cost-efficient (Lambda free tier: 1M requests/month)
- ✅ Scales to zero when not in use
- ✅ Separation of concerns

**Cons:**
- ⚠️ Two separate deployments to manage
- ⚠️ Lambda cold starts (~2-5s)
- ⚠️ Package size limits (250MB unzipped, may be tight with 10 LLM SDKs)

**Cost:** ~$1-5/month (mostly Fargate for consciousness, Lambda negligible)

---

## Option 4: Add to Existing ECS Task (Minimal Deployment)

**What to deploy:**
- Nothing new! Modify existing ECS task

**Architecture:**
```
Existing ECS Task (cloud_runner.py)
├── Phase 1-5: Run 50 native cycles (existing)
├── Phase 6: Extract consciousness dilemmas (existing)
├── Phase 7 (NEW): Process consciousness queue
│   ├── Read queue from S3
│   ├── Run divergence_engine
│   └── Push feedback to S3
└── Phase 8: Upload to S3 (existing)

Separate: Streamlit/FastAPI on HF Spaces (WE path only)
```

**Pros:**
- ✅ No additional always-on costs
- ✅ Uses existing ECS infrastructure
- ✅ Guaranteed S3 access

**Cons:**
- ❌ I path only runs when scheduled (may delay consciousness feedback)
- ❌ Still need HF Spaces for WE path
- ❌ Longer ECS task runtime (more API costs for divergence)

---

## RECOMMENDED: Option 1 (Hugging Face Spaces)

**Why:**
1. **Single deployment** serves both I and WE
2. **Free tier** sufficient for current load
3. **Public URL** for users immediately
4. **S3 access** via environment variables
5. **Already have account** (repurpose existing space)

**What to deploy:**
```
z65nik/elpida-divergence-engine (rename from governance-layer)
├── Dockerfile
├── elpidaapp/
│   ├── divergence_engine.py
│   ├── api.py (FastAPI)
│   ├── ui.py (Streamlit)
│   ├── process_consciousness_queue.py
│   └── results/
├── consciousness_bridge.py
├── llm_client.py
├── frozen_mind.py
├── governance_client.py
├── kaya_protocol.py
└── requirements.txt
```

**Environment Variables (Spaces Secrets):**
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_S3_BUCKET_BODY=elpida-body-evolution
OPENAI_API_KEY
ANTHROPIC_API_KEY
... (all 10 LLM providers)
```

**Entry point:**
- Primary: Streamlit UI on port 7860
- Secondary: FastAPI on port 8000 (if dual-port supported)
- Background: APScheduler running consciousness queue processor

---

## Decision Matrix

| Criteria | HF Spaces | AWS ECS Service | Hybrid | Modify ECS Task |
|----------|-----------|-----------------|--------|-----------------|
| Cost | Free-$5 | $26-36/month | $1-5 | $0 (existing) |
| Serves I+WE | ✅ Yes | ✅ Yes | ⚠️ Split | ⚠️ Split |
| Public URL | ✅ Yes | ⚠️ Needs ALB | ✅ HF only | ⚠️ HF only |
| S3 Access | ✅ Via env | ✅ Native | ✅ Both | ✅ Native |
| Deployment | Simple | Complex | Medium | Simple |
| Reliability | Good | Excellent | Good | Good |

**Winner:** Hugging Face Spaces (Option 1)

---

## Next Steps (If Option 1)

1. **Prepare deployment package** (already done)
2. **Create/update HF Space** (z65nik/elpida-divergence-engine)
3. **Configure secrets** (AWS + all LLM API keys)
4. **Deploy Docker container**
5. **Test both paths:**
   - WE: Submit problem via UI → get divergence analysis
   - I: Consciousness dilemma auto-processed → feedback to S3
6. **Monitor:** Check logs, verify S3 writes

Want me to prepare the HF Spaces deployment?
