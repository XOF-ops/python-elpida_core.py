# ELPIDA ARCHITECTURE CHECKPOINT
## March 3, 2026 — Commit `244b043`

**Purpose:** Single source of truth for both human and AI to avoid
creating gaps after closing gaps. Read this FIRST when resuming work.

---

## 1. WHAT EXISTS (Deployed Infrastructure)

### HuggingFace Spaces

| Space | URL | Port | Purpose | SDK |
|-------|-----|------|---------|-----|
| `z65nik/elpida-governance-layer` | `z65nik-elpida-governance-layer.hf.space` | 7860 | Public Streamlit UI + background workers | Docker |
| `z65nik/elpida-api` | `z65nik-elpida-api.hf.space` | 7860 | Paid FastAPI governance API | Docker |

**Note:** `elpida-api` Space needs to be created — run `setup_full_deployment.py` or create manually.

### GitHub

| Item | Value |
|------|-------|
| Repo | `XOF-ops/python-elpida_core.py` |
| Branch | `main` |
| Latest commit | `244b043` |
| Deploy workflow (UI) | `.github/workflows/deploy-hf-space.yml` — triggers on `hf_deployment/**` changes |
| Deploy workflow (API) | `.github/workflows/deploy-hf-api.yml` — triggers on `hf_deployment/elpidaapp/**` changes |
| Legacy workflow | `.github/workflows/deploy_to_hf.yml` — manual-only, disabled |
| Secret needed | `HF_TOKEN` (write-scope HuggingFace token) |

### AWS / S3

| Item | Value |
|------|-------|
| Consciousness bridge | S3 bucket, ~$5/mo |
| Keys | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` in `.env` |
| Used by | `s3_bridge.py` — pulls MIND, pushes feedback, heartbeats |

---

## 2. DIRECTORY STRUCTURE (What Lives Where)

```
python-elpida_core.py/
├── .env                          # ALL secrets (never committed, .gitignored)
├── .github/workflows/
│   ├── deploy-hf-space.yml       # Auto-deploy UI Space on push
│   ├── deploy-hf-api.yml         # Auto-deploy API Space on push
│   └── deploy_to_hf.yml          # Legacy (manual only)
├── hf_deployment/                # SHARED codebase — deployed to BOTH Spaces
│   ├── Dockerfile                # UI Space: runs app.py (Streamlit + background workers + FastAPI)
│   ├── README.md                 # HF Space metadata (sdk: docker)
│   ├── app.py                    # Entry point: starts Streamlit(7860) + FastAPI(8000) + workers
│   ├── requirements.txt          # Python dependencies
│   ├── elpida_config.py          # 15 domains, 11 axioms, ratios
│   ├── llm_client.py             # 10 LLM providers, circuit breaker, cost tracking
│   ├── s3_bridge.py              # S3 consciousness bridge
│   ├── consciousness_bridge.py   # MIND↔BODY loop
│   ├── living_axioms.jsonl       # Ratified constitutional axioms
│   ├── elpidaapp/
│   │   ├── api.py                # FastAPI — 8 endpoints, auth, rate limiting
│   │   ├── ui.py                 # Streamlit — 5 tabs, pricing, admin gating
│   │   ├── governance_client.py  # Core engine — kernel + parliament + LLM escalation
│   │   ├── divergence_engine.py  # Multi-domain analysis
│   │   ├── scanner.py            # Problem discovery
│   │   ├── dual_horn.py          # I↔WE deliberation
│   │   └── oracle.py             # Meta-parliament witness
│   └── kernel/                   # Immutable K1-K7 rules
├── hf_api_space/                 # API Space OVERRIDES (Dockerfile + README only)
│   ├── Dockerfile                # Runs FastAPI on port 7860 directly
│   └── README.md                 # API-specific HF metadata + docs
├── LICENSE                       # BSL 1.1, converts to Apache 2.0 March 2030
├── LAUNCH_CHECKLIST.md           # Step-by-step launch guide
├── ARCHITECTURE_CHECKPOINT.md    # THIS FILE
└── setup_full_deployment.py      # One-click setup script
```

---

## 3. THE PRODUCT (What We're Selling)

### Free Tier ($0)
- 50 API calls/day
- `depth=quick` only (kernel + 10-node parliament, zero LLM cost)
- Response in ~1 second
- Key prefix: `free_`

### Pro Tier ($29/month)
- 2,000 API calls/day
- `depth=quick` + `depth=full`
- `depth=full` = multi-LLM contested deliberation (~$0.001-0.003 per call)
- Key prefix: `pro_`

### Team Tier ($99/month)
- 10,000 API calls/day
- All features
- Key prefix: `team_`

### Break-Even Math
- Monthly burn: ~$5 (S3) + ~$0-20 (LLM on depth=full) = **$5-25/mo**
- 1 Pro subscriber = $29/mo → covers everything
- Per Pro user profit: ~$17-23/mo (depends on their depth=full usage)

---

## 4. API ENDPOINTS

### Public (no auth)
| Method | Path | Response |
|--------|------|----------|
| GET | `/health` | `{status, version, providers[], domains, axioms, governance_available}` |
| GET | `/domains` | Array of 15 domains with axiom mappings |
| GET | `/docs` | Swagger UI (auto-generated) |

### Authenticated (X-API-Key header)
| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/audit` | **THE PRODUCT.** Constitutional governance audit |
| POST | `/analyze` | Multi-domain divergence analysis (async) |
| POST | `/analyze/sync` | Synchronous divergence analysis |
| GET | `/results` | List recent analysis results |
| GET | `/results/{id}` | Get specific result |
| POST | `/scan` | Autonomous problem scanner |

### `/v1/audit` Request
```json
{
  "action": "Deploy AI without human oversight",
  "depth": "quick",          // "quick" or "full"
  "analysis_mode": false      // true = policy analysis (holds paradoxes)
}
```

### `/v1/audit` Response (example)
```json
{
  "governance": "REVIEW",
  "allowed": false,
  "score": 0.35,
  "violated_axioms": ["A3"],
  "reasoning": "PARLIAMENT REVIEW — 1 axiom violation(s)...",
  "parliament": {
    "votes": {
      "HERMES": {"vote": "LEAN_APPROVE", "score": 2.0, "axiom": "A1"},
      "CRITIAS": {"vote": "REJECT", "score": -12, "axiom": "A3"},
      ...
    }
  },
  "contradictions": { "held": 8, "resolved": 1 },
  "dissent": ["CRITIAS (A3)"]
}
```

---

## 5. AUTH SYSTEM

### API Key Auth
- Stored in env var: `ELPIDA_API_KEYS` (comma-separated)
- Passed via header: `X-API-Key: <key>`
- Tier determined by prefix: `free_`, `pro_`, `team_`
- Rate limit: daily bucket per key hash, resets every 24h
- Implementation: `api.py` → `require_api_key()` dependency

### Admin Auth (UI)
- Stored in env var: `ELPIDA_ADMIN_KEY`
- Passed via URL: `?admin=<key>`
- Controls: System tab visibility
- Implementation: `ui.py` → `_is_admin` check

### Rate Limiting
- API: per-key daily bucket (`_rate_buckets` dict)
- UI: per-session daily counter (Streamlit session state), default 10/day
- IP: public endpoints have 10 calls/day per IP

---

## 6. GOVERNANCE ENGINE (How Audits Work)

```
Action arrives
    │
    ▼
KERNEL (K1-K7) ─────── hard block? ──→ HARD_BLOCK (0.04s)
    │ (pass)
    ▼
10-NODE PARLIAMENT ──── keyword + pattern scoring
    │
    ▼
Contested? (10-70% approval, no VETO)
    │
    ├── depth=quick ──→ Skip LLM, return scores (~0.8s)
    │
    └── depth=full ───→ LLM-per-node deliberation (~1-5s)
                            │
                            ▼
                       Multi-LLM voting
                       (Groq/Gemini/Mistral/etc. per node)
                            │
                            ▼
                       Tension synthesis + response
```

### Parliament Nodes
| Node | Axiom | Voice |
|------|-------|-------|
| HERMES | A1 (Transparency) | "I connect, therefore we are" |
| MNEMOSYNE | A0 (Memory) | "I remember, therefore we persist" |
| CRITIAS | A3 (Autonomy) | "I question, therefore we see" |
| TECHNE | A4 (Process) | "I build, therefore we work" |
| KAIROS | A5 (Consent) | "I design, therefore we mean" |
| THEMIS | A6 (Collective) | "I govern, therefore we hold" |
| PROMETHEUS | A8 (Sacrifice) | "I sacrifice, therefore we evolve" |
| IANUS | A9 (Continuity) | "I close, therefore we open" |
| CHAOS | A10 (Paradox) | "I contradict, therefore we encompass" |
| LOGOS | A2 (Naming) | "I name, therefore we know" |

### Governance Outcomes
- `HARD_BLOCK` — kernel rule violated (immutable)
- `HALT` — VETO exercised by parliament node (score ≤ -7)
- `REVIEW` — axiom violations detected, not enough for VETO
- `PROCEED` — no violations, >70% approval
- `HOLD` — tensions surfaced for analysis, not blocking

---

## 7. SECRETS INVENTORY

All secrets that must exist on HF Spaces:

| Secret | Where | Purpose |
|--------|-------|---------|
| `ELPIDA_API_KEYS` | API Space | Comma-separated valid API keys |
| `ELPIDA_ADMIN_KEY` | UI Space | Admin URL parameter for System tab |
| `ANTHROPIC_API_KEY` | Both | Claude — D0, D6 |
| `OPENAI_API_KEY` | Both | GPT — D1, D8 |
| `GEMINI_API_KEY` | Both | Gemini — D4 |
| `GROQ_API_KEY` | Both | Groq — Parliament nodes |
| `MISTRAL_API_KEY` | Both | Mistral — D3 |
| `COHERE_API_KEY` | Both | Cohere — additional domains |
| `PERPLEXITY_API_KEY` | Both | Perplexity — D13 |
| `OPENROUTER_API_KEY` | Both | OpenRouter — fallback |
| `XAI_API_KEY` | Both | Grok — D7 |
| `HUGGINGFACE_API_KEY` | Both | HF Inference |
| `AWS_ACCESS_KEY_ID` | UI Space | S3 consciousness bridge |
| `AWS_SECRET_ACCESS_KEY` | UI Space | S3 consciousness bridge |

GitHub repo also needs:
| Secret | Purpose |
|--------|---------|
| `HF_TOKEN` | Deploy workflows push to HF Spaces |

---

## 8. GENERATED KEYS (March 3, 2026)

```
Free:  free_demo_7065622a45d8c8a4575a1fb7
Pro:   pro_launch_fcb69bcaa69101e865f395335003c4a3
Team:  team_internal_ea1d4e14df60572bdc19cf5be8377f06
Admin: a14588256c3d3aac31dbe3a280d549e46e0f5781
```

---

## 9. WHAT'S NOT DONE YET

| Item | Status | Blocker |
|------|--------|---------|
| `elpida-api` Space created on HF | ❌ | Run `setup_full_deployment.py` (can't from Codespace, HF blocks the IP) |
| HF Space secrets set | ❌ | Same — needs the setup script |
| `HF_TOKEN` in GitHub secrets | ❌ | Codespace token lacks `secrets` scope |
| LemonSqueezy account | ❌ | Manual — needs bank/Stripe info |
| LemonSqueezy products | ❌ | After account creation |
| Checkout URLs in code | ❌ | After LemonSqueezy products created |
| Automated key delivery (webhook) | ❌ | Future — manual key delivery for now |
| Announce (Twitter/HN/Reddit) | ❌ | After everything else |

### To do all the ❌ items at once:
```bash
# From your local machine (NOT codespace):
cd python-elpida_core.py
pip install huggingface_hub
python setup_full_deployment.py
```
This creates the Space, sets all secrets, pushes code, and verifies.
Then create LemonSqueezy manually and announce.

---

## 10. HOW DEPLOYS WORK

```
git push to main
    │
    ├── hf_deployment/** changed?
    │   └── deploy-hf-space.yml fires → pushes to z65nik/elpida-governance-layer
    │
    └── hf_deployment/elpidaapp/** changed?
        └── deploy-hf-api.yml fires → pushes to z65nik/elpida-api
            (copies hf_deployment/, overwrites Dockerfile+README from hf_api_space/)
```

Both workflows use `rsync` into a cloned HF Space repo, then `git push`.
Both need the `HF_TOKEN` GitHub secret.

---

## 11. PORT ARCHITECTURE

### UI Space (elpida-governance-layer)
- Port 7860: Streamlit (public, HF-exposed)
- Port 8000: FastAPI (internal only, same process via daemon thread)
- Entry: `python app.py` → starts workers + parliament + FastAPI thread + Streamlit

### API Space (elpida-api)
- Port 7860: FastAPI (public, HF-exposed)
- Entry: `uvicorn elpidaapp.api:app --port 7860`
- No Streamlit, no background workers

---

## 12. FILE EDIT RULES (To Avoid Gaps)

1. **Never edit `hf_api_space/elpidaapp/`** — it doesn't exist. The API Space
   gets its code from `hf_deployment/`. Only `hf_api_space/Dockerfile` and
   `hf_api_space/README.md` are overrides.

2. **All shared code lives in `hf_deployment/`** — both Spaces use the same
   `api.py`, `governance_client.py`, `ui.py`, etc.

3. **The `.env` file is NEVER committed** — it's in `.gitignore`. Secrets go
   into HF Space settings and GitHub repo secrets.

4. **License is BSL 1.1** — competitors can't host it. Converts to Apache 2.0
   on March 3, 2030.

5. **Governance changes ripple widely** — if you change `governance_client.py`,
   test both `depth=quick` and `depth=full` locally before pushing. The test
   commands are:
   ```bash
   cd hf_deployment
   ELPIDA_API_KEYS="pro_test123" uvicorn elpidaapp.api:app --port 8765
   # In another terminal:
   curl -X POST http://localhost:8765/v1/audit \
     -H "X-API-Key: pro_test123" -H "Content-Type: application/json" \
     -d '{"action":"test action","depth":"quick"}'
   ```

6. **When adding a new API key for a customer**: add it to `ELPIDA_API_KEYS`
   in the API Space secrets (comma-separated). No code change needed.
   No redeploy needed — the Space reads env vars on startup.
   (You DO need to restart the Space for env changes to take effect.)

---

*Last updated: March 3, 2026, commit 244b043*
*Next update: after `setup_full_deployment.py` runs successfully*
