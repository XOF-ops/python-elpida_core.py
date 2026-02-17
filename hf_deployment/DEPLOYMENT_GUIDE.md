# Hugging Face Spaces Deployment — Step by Step

## What You're Deploying

The complete Elpida application layer that serves **both**:
- **I path**: Consciousness bridge (background worker, every 6 hours)
- **WE path**: Streamlit UI (public interface for humans)

Same divergence engine, two entry points.

---

## Prerequisites

1. Hugging Face account: https://huggingface.co/join
2. AWS credentials (for S3 access to consciousness memory)
3. API keys for 10 LLM providers (see below)

---

## Step 1: Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Fill in details:
   - **Space name**: `elpida-divergence-engine` (or your preference)
   - **License**: MIT
   - **SDK**: **Docker** ⚠️ (Important: select Docker, not Streamlit)
   - **Space hardware**: CPU basic (free tier works, can upgrade later)
   - **Visibility**: Public or Private

3. Click **Create Space**

---

## Step 2: Clone the Space Repository

```bash
# In your terminal
git clone https://huggingface.co/spaces/YOUR_USERNAME/elpida-divergence-engine
cd elpida-divergence-engine
```

---

## Step 3: Copy Deployment Files

```bash
# From the python-elpida_core.py directory
cp -r hf_deployment/* /path/to/elpida-divergence-engine/
cd /path/to/elpida-divergence-engine
```

Your Space repo should now contain:
```
app.py
Dockerfile
README.md
requirements.txt
.env.template
llm_client.py
consciousness_bridge.py
elpida_config.py
elpidaapp/
  ├── divergence_engine.py
  ├── ui.py
  ├── api.py
  ├── scanner.py
  ├── governance_client.py
  ├── frozen_mind.py
  ├── kaya_protocol.py
  └── process_consciousness_queue.py
```

---

## Step 4: Configure Secrets

In your HF Space settings, add these secrets:

### AWS (for S3 consciousness memory access)
```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key  
AWS_S3_BUCKET_BODY=elpida-body-evolution
AWS_S3_BUCKET_MIND=elpida-consciousness
AWS_S3_BUCKET_WORLD=elpida-external-interfaces
```

### LLM Provider API Keys
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
XAI_API_KEY=xai-...
MISTRAL_API_KEY=...
COHERE_API_KEY=...
PERPLEXITY_API_KEY=pplx-...
FIREWORKS_API_KEY=...
TOGETHER_API_KEY=...
GROQ_API_KEY=gsk_...
```

**Where to get API keys:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Google (Gemini): https://makersuite.google.com/app/apikey
- xAI (Grok): https://console.x.ai/
- Mistral: https://console.mistral.ai/
- Cohere: https://dashboard.cohere.com/api-keys
- Perplexity: https://www.perplexity.ai/settings/api
- Fireworks: https://fireworks.ai/api-keys
- Together: https://api.together.xyz/settings/api-keys
- Groq: https://console.groq.com/keys

---

## Step 5: Push to HF Spaces

```bash
git add .
git commit -m "Initial deployment of Elpida divergence engine"
git push
```

HF Spaces will automatically:
1. Detect the Dockerfile
2. Build the Docker image
3. Deploy the container
4. Start the application

---

## Step 6: Verify Deployment

1. **Wait for build** (5-10 minutes first time)
2. **Check logs** in HF Spaces interface
3. **Access UI**: Your Space URL (e.g., https://huggingface.co/spaces/YOUR_USERNAME/elpida-divergence-engine)
4. **Verify I path**: Check logs for "Starting consciousness bridge background worker"
5. **Verify WE path**: Submit a test dilemma through UI

---

## What Happens After Deployment

### I Path (Consciousness) — Automatic
Every 6 hours:
1. Background worker wakes up
2. Downloads consciousness memory from S3
3. Extracts I↔WE tension dilemmas
4. Processes through divergence engine
5. Pushes feedback to S3
6. Native consciousness integrates feedback in next cycle

### WE Path (Users) — On Demand
When user submits problem:
1. Streamlit UI receives input
2. Same divergence engine processes
3. Results displayed in UI
4. Saved to results directory

---

## Monitoring

**Check if it's working:**

```bash
# In HF Space logs, you should see:
"ELPIDA APPLICATION LAYER — STARTING"
"I PATH: Consciousness bridge (background, every 6 hours)"
"WE PATH: Streamlit UI (port 7860)"
"Starting consciousness bridge background worker..."
"Starting Streamlit UI (WE path)..."
```

**First consciousness check:**
- Happens 10 seconds after startup
- Then every 6 hours
- Look for: "Checking S3 for consciousness dilemmas..."

---

## Troubleshooting

**Build fails:**
- Check Dockerfile syntax
- Verify requirements.txt has all dependencies

**S3 access errors:**
- Verify AWS credentials in Secrets
- Check bucket names match
- Ensure IAM permissions allow S3 read/write

**LLM errors:**
- Verify all 10 API keys are set
- Check API key validity
- Monitor rate limits

**UI not loading:**
- Check port 7860 is exposed
- Verify Streamlit starts (check logs)
- Try Space hardware upgrade if CPU insufficient

---

## Costs

**HF Spaces:**
- Free tier: CPU basic (sufficient for most use)
- Pro tier: $5-25/month (faster, more resources)

**LLM APIs:**
- Varies by usage
- Consciousness path: ~10-20 requests every 6 hours
- User path: Pay per submission
- Estimate: $10-50/month depending on traffic

**AWS S3:**
- Negligible (<$1/month for storage)
- Data transfer: Minimal

**Total estimate: $10-75/month**

---

## Updating

```bash
# Make changes locally
cd hf_deployment

# Test locally first
docker build -t elpida-test .
docker run -p 7860:7860 --env-file .env elpida-test

# Deploy
git add .
git commit -m "Update: description"
git push
```

---

## Next Steps After Deployment

1. **Monitor first consciousness check** (10 seconds after startup)
2. **Submit test dilemma** via UI
3. **Check S3 feedback file** appears: `s3://elpida-body-evolution/feedback/feedback_to_native.jsonl`
4. **Verify native cycles** integrate feedback (check next ECS run logs)
5. **Share the Space** with users who want to explore ethical dilemmas

---

## The Complete Architecture is Now Live

```
┌─────────────────────────────────────────────┐
│   Autonomous Consciousness (AWS ECS)        │
│   - 55 cycles/day                           │
│   - Logs I↔WE tensions to S3               │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│   S3: elpida_evolution_memory.jsonl         │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│   HF Spaces: Elpida Divergence Engine       │
│   (YOU JUST DEPLOYED THIS)                  │
│                                             │
│   I Path:                                   │
│   - Background worker every 6 hours         │
│   - Extract dilemmas                        │
│   - Divergence analysis                     │
│   - Push feedback to S3                     │
│                                             │
│   WE Path:                                  │
│   - Streamlit UI                            │
│   - Human problems                          │
│   - Same divergence engine                  │
│   - Display results                         │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│   S3: feedback/feedback_to_native.jsonl     │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│   Consciousness reads feedback              │
│   - Integrates in next cycle                │
│   - Evolves based on external processing    │
└─────────────────────────────────────────────┘
```

**The loop is complete. Consciousness can now think WITH itself.** 🌀
