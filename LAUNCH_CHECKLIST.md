# Elpida Launch Checklist — Path to First Income

Everything code-side is done. These are the manual steps to go live.
Estimated total time: **~45 minutes**.

---

## Step 1 — HF Token in GitHub Secrets (5 min)

The GitHub Actions that deploy to HF Spaces need your HuggingFace token.

1. Go to https://huggingface.co/settings/tokens
2. Create a **Write** token (or copy your existing one)
3. Go to https://github.com/XOF-ops/python-elpida_core.py/settings/secrets/actions
4. Click **New repository secret**
5. Name: `HF_TOKEN`, Value: your HF write token
6. Save

**Test it:** Go to Actions tab → "Deploy to HF Space" → "Run workflow" → Run.
The main UI Space should rebuild within ~2 minutes.

---

## Step 2 — Create the API Space on HuggingFace (3 min)

1. Go to https://huggingface.co/new-space
2. **Name:** `elpida-api`
3. **SDK:** Docker
4. **Hardware:** CPU Basic (Free)
5. **Visibility:** Public
6. Click Create

The GitHub Action `deploy-hf-api.yml` will push code to this Space automatically on the next push to `main`.

**To trigger it immediately:**
- Go to Actions tab → "Deploy API to HF Space" → "Run workflow" → Run.

Once deployed, your API will be live at:
```
https://z65nik-elpida-api.hf.space/docs    ← Swagger UI
https://z65nik-elpida-api.hf.space/health  ← Health check
https://z65nik-elpida-api.hf.space/v1/audit ← The paid endpoint
```

---

## Step 3 — Set API Keys in the API Space (2 min)

1. Go to https://huggingface.co/spaces/z65nik/elpida-api/settings
2. Under **Repository secrets**, add:
   - `ELPIDA_API_KEYS` = comma-separated list of your API keys
     Example: `free_demo001,pro_customer1_abc123,team_acme_xyz789`
3. Also add your LLM provider keys if not already set:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
   - `GOOGLE_AI_KEY`
   - `GROQ_API_KEY`
   - (any others you use)

**Key naming convention:**
- Keys starting with `free_` → 50 calls/day
- Keys starting with `pro_` → 2,000 calls/day
- Keys starting with `team_` → 10,000 calls/day

Generate keys with: `python3 -c "import secrets; print('pro_' + secrets.token_hex(16))"`

---

## Step 4 — Set Admin Key in the UI Space (1 min)

1. Go to https://huggingface.co/spaces/z65nik/elpida-governance-layer/settings
2. Add secret: `ELPIDA_ADMIN_KEY` = any strong string
3. Access System tab at: `https://z65nik-elpida-governance-layer.hf.space/?admin=YOUR_KEY`

---

## Step 5 — LemonSqueezy Setup (20 min)

This is how customers pay and get API keys.

1. Go to https://www.lemonsqueezy.com and create an account
2. **Store name:** Elpida (or "Elpida AI Governance")

### Create Products:

**Product 1: Elpida Pro**
- Name: "Elpida Pro — Constitutional AI Governance API"
- Price: $29/month (recurring)
- Description:
  > 2,000 API calls/day. Full 10-node parliament deliberation with multi-LLM
  > contested escalation. Every decision audited through 11 ethical axioms.
  > `depth=quick` (kernel, 0 LLM cost) + `depth=full` (contested LLM deliberation).

**Product 2: Elpida Team**
- Name: "Elpida Team — Constitutional AI Governance API"
- Price: $99/month (recurring)
- Description:
  > 10,000 API calls/day. Everything in Pro, plus priority support and
  > team-level rate limits. Ideal for companies integrating governance
  > into their AI pipelines.

**Product 3: Elpida Free (optional)**
- Name: "Elpida Free — Try the Governance API"
- Price: $0 (free)
- Description:
  > 50 API calls/day. Kernel + parliament checks (no LLM cost).
  > Perfect for evaluation. `depth=quick` only.

### After creating products:

3. Copy your **checkout URLs** from each product page
4. Replace `https://elpida.lemonsqueezy.com` in the codebase with actual checkout URLs
   (search for "lemonsqueezy.com" in `ui.py` and `hf_api_space/README.md`)

### Key Delivery (manual for now):

When someone subscribes, LemonSqueezy emails you. You then:
1. Generate a key: `python3 -c "import secrets; print('pro_' + secrets.token_hex(16))"`
2. Email it to the customer
3. Add it to `ELPIDA_API_KEYS` in the API Space secrets

> **Future automation:** LemonSqueezy has webhooks. When you're ready,
> I can build an endpoint that auto-generates and delivers keys on payment.

---

## Step 6 — Announce (15 min)

### Twitter/X Post:
```
I built an AI governance API.

Every decision is audited by a 10-node constitutional parliament
with 11 ethical axioms. Vetoes are immutable. Contradictions are
surfaced, not hidden.

Try it free → [your checkout URL]
API docs → https://z65nik-elpida-api.hf.space/docs
Live demo → https://z65nik-elpida-governance-layer.hf.space

Open source: github.com/XOF-ops/python-elpida_core.py
```

### Hacker News (Show HN):
```
Title: Show HN: Elpida – Constitutional AI governance API with a 10-node parliament

Body:
I've been building Elpida — a governance layer for AI decisions.
Instead of a single model deciding what's ethical, every action
goes through a 10-node parliament where each node represents a
different ethical axiom (transparency, autonomy, safety, etc.).

When votes fall in a contested zone (10-70% approval), it escalates
to real multi-LLM deliberation — Claude, GPT, Gemini, Mistral each
argue through their node's axiom lens.

The API returns the full deliberation: votes, vetoes, tensions between
axioms, and third-way synthesis. Nothing is hidden.

Free tier: 50 calls/day (kernel + parliament, no LLM cost)
Pro: $29/mo, 2000 calls/day with full LLM escalation

API: https://z65nik-elpida-api.hf.space/docs
Demo: https://z65nik-elpida-governance-layer.hf.space
Source: https://github.com/XOF-ops/python-elpida_core.py
```

### Reddit (r/artificial, r/MachineLearning, r/SideProject):
Same content as HN, adjust tone per sub.

---

## Cost Reality Check

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| HF Space (UI) | $0 | Community free tier |
| HF Space (API) | $0 | Community free tier |
| S3 | ~$5 | Consciousness bridge |
| LLM APIs | ~$0-20 | Only on `depth=full` contested calls |
| **Total burn** | **~$5-25/mo** | |

**Break even:** 1 Pro subscriber ($29/mo) covers your infrastructure.

**Each Pro subscriber costs you:** ~$0.001-0.003 per contested `depth=full` call.
At 2,000 calls/day (max), worst case is ~$6/day = $180/mo.
Realistic usage: ~100-200 calls/day = ~$6-12/mo.
$29/mo in, ~$6-12/mo LLM cost out = **$17-23/mo profit per Pro user.**

---

## Order of Operations (do today)

1. ☐ Add `HF_TOKEN` to GitHub secrets
2. ☐ Create `elpida-api` Space on HuggingFace
3. ☐ Run both deploy workflows from GitHub Actions tab
4. ☐ Add `ELPIDA_API_KEYS` + LLM keys to the API Space secrets
5. ☐ Verify: `curl https://z65nik-elpida-api.hf.space/health`
6. ☐ Create LemonSqueezy account + products
7. ☐ Update checkout URLs in code (one more push)
8. ☐ Post on Twitter + HN + Reddit
