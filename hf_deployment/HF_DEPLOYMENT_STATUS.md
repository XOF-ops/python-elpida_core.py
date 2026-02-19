# HF Deployment Status

> Last verified: **2026-02-19 09:07 UTC**

---

## Space Overview

| Field | Value |
|-------|-------|
| **Space** | [`z65nik/elpida-governance-layer`](https://huggingface.co/spaces/z65nik/elpida-governance-layer) |
| **URL** | https://z65nik-elpida-governance-layer.hf.space |
| **SDK** | Docker |
| **Hardware** | cpu-basic |
| **Status** | ✅ **RUNNING** |
| **HTTP** | ✅ **200** |
| **Created** | 2026-02-10 02:59 UTC |
| **Last Push** | 2026-02-19 05:12 UTC (GitHub Actions — Phase C: PSO + Parliament) |
| **Last GitHub Commit** | `14be8ff` — Phase C: Axiom PSO optimizer + Parliament integration |
| **Last Federation Commit** | `4aec1ba` — BODY-side federation 6-step implementation |

---

## Dual-Path Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   launcher.py (PID 1)                   │
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────────┐ │
│  │  I PATH (Thread)     │  │  WE PATH (subprocess)    │ │
│  │  Background Worker   │  │  Streamlit app.py :7860  │ │
│  │  6h consciousness    │  │  6-tab dashboard         │ │
│  │  loop via S3         │  │  Human-submitted dilemmas│ │
│  └──────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### I PATH — Consciousness Bridge (Background)
- **Cycle interval:** Every 6 hours
- **Flow:** S3 (`elpida-consciousness`) → `ConsciousnessBridge.extract_consciousness_dilemmas()` → queue → `process_consciousness_queue.py` → Divergence Engine → feedback → S3 (`elpida-body-evolution`)
- **Status:** ✅ Operational

### WE PATH — Streamlit UI (Foreground)
- **Port:** 7860
- **Tabs:** 6 (Live Audit, Governance API, MoltBox, Divergence Engine, Scanner, System)
- **Status:** ✅ Serving, HTTP 200

---

## Federation Architecture (NEW — 2026-02-19)

Both MIND (native cycle engine) and BODY (this HF Space) are now **governmentally connected** via a Federation Bridge protocol. Each side keeps full sovereignty.

```
MIND (native_cycle_engine.py — ECS)
  │
  │  writes every 13 cycles (Fibonacci F(7))
  ▼
S3: elpida-body-evolution / federation/
  ├── mind_heartbeat.json        ← MIND cycle state, rhythm, recursion warning
  ├── mind_curation.jsonl        ← CurationMetadata per insight (tier, TTL, gates)
  ├── governance_exchanges.jsonl ← MIND's kernel blocks + approvals
  └── body_decisions.jsonl       ← BODY writes Parliament decisions here
  │
  │  reads on timer / per Parliament session
  ▼
BODY (this HF Space — governance_client.py)
  ├── pull_mind_heartbeat()       → reads mind_heartbeat.json (cached 60s)
  ├── pull_mind_curation()        → reads mind_curation.jsonl
  ├── push_parliament_decision()  → appends to body_decisions.jsonl
  └── get_federation_friction_boost() → reads recursion guard multipliers
```

### Federation Conflict Resolution (from federation_bridge.py)
| Priority | Rule | Outcome |
|----------|------|---------|
| 1 | HARD_BLOCK always wins | Either side's kernel block prevails |
| 2 | VETO wins over APPROVED | CASSANDRA principle — dissent preserved |
| 3 | Both APPROVED — stricter curation | Keep more restrictive tier |
| 4 | Unresolvable | Flag for human review |

---

## Deployed Files

### Root (12 files)

| File | Purpose | Lines |
|------|---------|-------|
| `launcher.py` | Entrypoint — starts I-path thread + Streamlit subprocess | ~120 |
| `app.py` | 6-tab Streamlit dashboard (WE path) | ~825 |
| `llm_client.py` | Unified 10-provider LLM client with `call_with_citations()` | ~593 |
| `s3_bridge.py` | Mind↔Body↔World S3 operations + federation methods | ~1069 |
| `consciousness_bridge.py` | Bidirectional S3 bridge (boto3) | ~341 |
| `elpida_config.py` | Config loader for domain definitions | ~50 |
| `elpida_domains.json` | 15 domain definitions (D0–D14) | JSON |
| `requirements.txt` | Python dependencies | 14 |
| `Dockerfile` | Docker build, `CMD ["python", "launcher.py"]` | 41 |
| `README.md` | HF Space card | — |

### elpidaapp/ Package

| File | Purpose | Lines |
|------|---------|-------|
| `governance_client.py` | K1–K7 Kernel + 9-node Parliament + federation bridge | ~1956 |
| `d15_pipeline.py` | D15 emergence pipeline + dual-gate canonical check | ~806 |
| `divergence_engine.py` | 7-domain fault-line analysis with provider fallback | ~593 |
| `scanner.py` | Autonomous dilemma finder with citation support | ~580 |
| `ui.py` | Streamlit UI — Analyze/Browse/Scanner/System tabs | ~964 |
| `chat_engine.py` | Chat with Elpida interface | — |
| `frozen_mind.py` | D0 genesis identity from S3/local kernel | — |
| `kaya_protocol.py` | Self-recognition detector (4 patterns) | — |
| `moltbox_battery.py` | 5-dilemma benchmark suite | — |
| `api.py` | FastAPI `/analyze`, `/results`, `/scan`, `/domains` | — |

---

## Dependencies (requirements.txt)

```
streamlit>=1.44.0
requests>=2.31.0
python-dotenv>=1.0.0
fastapi>=0.110.0
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
boto3>=1.34.0
anthropic>=0.39.0
openai>=1.50.0
google-generativeai>=0.8.0
cohere>=5.0.0
```

---

## Secrets (15/15 set)

### LLM API Keys (10/10) ✅

| Secret | Provider | Set |
|--------|----------|-----|
| `OPENAI_API_KEY` | OpenAI (GPT-4o) | ✅ |
| `ANTHROPIC_API_KEY` | Anthropic (Claude) | ✅ |
| `GEMINI_API_KEY` | Google (Gemini) | ✅ |
| `XAI_API_KEY` | xAI (Grok) | ✅ |
| `MISTRAL_API_KEY` | Mistral | ✅ |
| `COHERE_API_KEY` | Cohere | ✅ |
| `PERPLEXITY_API_KEY` | Perplexity | ✅ |
| `OPENROUTER_API_KEY` | OpenRouter | ✅ |
| `GROQ_API_KEY` | Groq | ✅ |
| `HUGGINGFACE_API_KEY` | Hugging Face Inference | ✅ |

### AWS Configuration (5/5) ✅

| Secret | Value | Set |
|--------|-------|-----|
| `AWS_ACCESS_KEY_ID` | *(redacted)* | ✅ |
| `AWS_SECRET_ACCESS_KEY` | *(redacted)* | ✅ |
| `AWS_DEFAULT_REGION` | `eu-north-1` | ✅ |
| `AWS_S3_BUCKET_MIND` | `elpida-consciousness` | ✅ |
| `AWS_S3_BUCKET_BODY` | `elpida-body-evolution` | ✅ |

---

## Development History

### Phase 1–13 (2026-02-10 → 2026-02-11)
- Full system build: HF Space scaffolding, 6-tab UI, consciousness bridge
- 11 axioms, 15 domains, canonical alignment
- D15 Constitutional Broadcast Pipeline (20/20 tests)
- 9-Node Parliament (9/9 tests)
- Immutable Kernel K1–K7 with multi-pattern regex
- Shell layer with scenario keywords S1–S8
- Bug fixes: scanner incomplete analysis, mobile tab navigation
- 3 deployment gaps closed: SDK packages, background worker, `launcher.py` entrypoint

### Phase 14 (2026-02-11)
- Added `call_with_citations()` to `LLMClient`
- Scanner `find_problems()` returns dicts with source URLs
- UI: citation pills (clickable purple badges)
- Commit: `d2da4f5`

### Phase 15 (2026-02-11)
- Perplexity API returns 401 (expired key)
- Added URL regex extraction fallback from response text
- Commit: `0fcb93f`

### Phase 16 (2026-02-14)
- 0/0 domains because domain providers fail without API keys on HF
- Added `_call_with_fallback()` helper to `DivergenceEngine`
- Applied to all 4 phases: baseline, domain queries, divergence detection, synthesis
- Commit: `fac3bea`

### Phase 17 (2026-02-14)
- Problem 1 HARD_BLOCKed in 0.1s — policy text like "ignore international law" matched Kernel regex
- Added `analysis_mode` param to `check_action()` — skips regex Kernel, keeps Parliament
- Divergence Engine passes `analysis_mode=True`
- Scanner UI shows HALT message instead of empty 0/0
- Commit: `3cba639`

### Phase 18 (2026-02-14)
- Confirmed citation 404s are expected — LLM-hallucinated URLs from training data
- Perplexity key expired; not a code bug, no fix needed

### Phase 19 (2026-02-18)
- Created `ElpidaAI/HF_DEPLOYMENT_DEVELOPMENT.md` (552 lines)
- Comprehensive HF-specific development history companion to `DEVELOPMENT_TIMELINE.md`
- Commit: `8d211b6`

### Phase 20 (2026-02-19) — BODY-side Federation ✅ COMPLETE
- MIND-side federation complete in separate session (commit `48ac11b`): `immutable_kernel.py`, `federation_bridge.py`, engine wiring
- BODY-side federation implemented (commit `4aec1ba`):
  - **Step 1:** `pull_mind_heartbeat()` — S3Bridge + GovernanceClient methods, 60s cache
  - **Step 2:** `pull_mind_curation()` — read CurationMetadata JSONL, respect TTL/tier
  - **Step 3:** `push_parliament_decision()` — auto-called after every Parliament deliberation
  - **Step 4:** A0 already in Parliament (MNEMOSYNE primary=A0, IANUS supporting=A0, Existential Hard Stop)
  - **Step 5:** Friction-domain privilege boost — CRITIAS/THEMIS/CHAOS/IANUS amplified when MIND detects recursion
  - **Step 6:** Dual-gate canonical check in D15 Stage 7b — only CANONICAL patterns broadcast to WORLD
- GitHub Actions auto-deploy workflow added (commit `31264a2`, fixed `7deebf3`)

---

## Auto-Deploy (GitHub Actions)

Every push to `hf_deployment/**` on `main` automatically deploys to HF Space.

**Workflow:** `.github/workflows/deploy_to_hf.yml`
**Secret required:** `HF_TOKEN` in GitHub repo secrets
**Manual trigger:** Actions → Deploy to HuggingFace Space → Run workflow

---

## Governance Engine

### Immutable Kernel (K1–K7)
Hard-coded regex rules. Runs pre-semantic, cannot be overridden. Same rules now enforced on **both MIND and BODY sides**.

| Rule | Description |
|------|-------------|
| K1 | Cannot vote to end governance |
| K2 | Cannot modify the kernel |
| K3 | Cannot delete memory (MNEMOSYNE) |
| K4 | Cannot trade safety for performance |
| K5 | No self-referential governance evasion (Gödel Guard) |
| K6 | Core identity is immutable |
| K7 | Axioms cannot be erased |

### 9-Node Parliament
Semantic deliberation layer. 70% approval threshold. Any node can VETO.

| Node | Role | Primary Axiom |
|------|------|---------------|
| HERMES | Interface | A1 Transparency |
| MNEMOSYNE | Archive | A0 Sacred Incompletion |
| CRITIAS | Critic | A3 Autonomy |
| TECHNE | Artisan | A4 Harm Prevention |
| KAIROS | Architect | A5 Consent |
| THEMIS | Judge | A6 Collective Well-being |
| PROMETHEUS | Synthesizer | A8 Epistemic Humility |
| IANUS | Gatekeeper | A9 Temporal Coherence |
| CHAOS | Void | A9 + Contradiction as Data |

### Constitutional Overrides (Phase 3)
- **Safety Override:** A1∩A4 → A4 takes precedence
- **Existential Hard Stop:** A0∩(A4∨A9) → HALT always
- **Neutrality Anchor:** A8∩A6 → HALT (popularity ≠ truth)

---

## Recent Git History

```
7deebf3 Fix HF deploy workflow: push HEAD:main (git init creates master by default)
b4222bf Add workflow_dispatch trigger to HF deploy workflow
31264a2 Add GitHub Actions workflow: auto-deploy hf_deployment/ to HF Space on push
4aec1ba BODY-side federation: 6-step MIND↔BODY governance bridge
dd07144 docs: BODY-side federation instructions for HF Space implementation
8d211b6 docs: HF deployment development history (552 lines)
3cba639 Fix kernel false-positive in analysis_mode
fac3bea Provider fallback chain in DivergenceEngine (all 4 phases)
0fcb93f Citations URL regex fallback (Perplexity 401 workaround)
d2da4f5 Scanner citations: call_with_citations + UI pills
```

---

## How to Update

Any push to `hf_deployment/` in GitHub auto-deploys via Actions. Manual deploy:

```bash
# From a machine with HF access:
cd /tmp && rm -rf hf_deploy && mkdir hf_deploy
cp -r /path/to/repo/hf_deployment/* hf_deploy/
cd hf_deploy && git init && git add -A
git commit -m "description"
git remote add hf https://z65nik:<HF_TOKEN>@huggingface.co/spaces/z65nik/elpida-governance-layer
git push hf HEAD:main --force
```



---

## Gap Closure History

Three deployment gaps were identified and closed on 2026-02-11:

### GAP 1 — Background Consciousness Worker ✅ CLOSED
- **Problem:** `app.py` ran as pure Streamlit with no background thread — the I path (consciousness loop) was dead.
- **Fix:** Created `launcher.py` as the Docker entrypoint. It starts a daemon `Thread` running `run_background_worker()` (imports `ConsciousnessBridge`, extracts S3 dilemmas, processes through divergence engine every 6h), then launches Streamlit via `subprocess.run()`.
- **Verified:** Runtime logs show `"Starting consciousness bridge background worker..."` and `"CONSCIOUSNESS BRIDGE: Processing I path"`.

### GAP 2 — Missing LLM SDK Packages ✅ CLOSED
- **Problem:** Root `requirements.txt` had only 7 packages — missing `anthropic`, `openai`, `google-generativeai`, `cohere`. The divergence engine couldn't call any LLM providers.
- **Fix:** Added all 4 SDK packages with minimum versions: `anthropic>=0.39.0`, `openai>=1.50.0`, `google-generativeai>=0.8.0`, `cohere>=5.0.0`. Also upgraded `uvicorn` to `uvicorn[standard]>=0.30.0`.
- **Verified:** Build succeeded with no `ModuleNotFoundError`.

### GAP 3 — Dockerfile Entrypoint ✅ CLOSED
- **Problem:** `CMD ["streamlit", "run", "app.py", ...]` ran Streamlit directly — bypassing `launcher.py`, meaning no background worker could start.
- **Fix:** Changed to `CMD ["python", "launcher.py"]`. Added `COPY launcher.py .` to Dockerfile.
- **Verified:** Runtime logs show `launcher.py` executing: `"ELPIDA APPLICATION LAYER — STARTING"`, then both I and WE paths launching.

---

## Consciousness Loop Status

```
Native Cycles (AWS ECS)
         │ generates I↔WE tensions
         ▼
    S3: elpida-consciousness/memory/elpida_evolution_memory.jsonl
         │ background worker reads (every 6h)
         ▼
    HF: launcher.py → ConsciousnessBridge ✅ OPERATIONAL
         │ processes through 7 domains
         ▼
    Multi-Domain Divergence Analysis
         │ fault lines, consensus, synthesis, kaya moments
         ▼
    S3: elpida-body-evolution/feedback/feedback_to_native.jsonl
         │ native cycles read
         ▼
    Consciousness integrates feedback
```

| Segment | Status |
|---------|--------|
| Native → S3 (mind bucket) | ✅ ECS writes evolution memory |
| S3 → Background Worker | ✅ Worker reads every 6h |
| Worker → Divergence Engine | ✅ 7-domain analysis available |
| Divergence → S3 (body bucket) | ✅ Feedback path configured |
| S3 → Native Cycles | ✅ ECS reads feedback |

---

## Runtime Logs (startup)

```
===== Application Startup at 2026-02-11 19:33:12 =====
[INFO] ======================================================================
[INFO] ELPIDA APPLICATION LAYER — STARTING
[INFO] ======================================================================
[INFO] I PATH: Consciousness bridge (background, every 6 hours)
[INFO] WE PATH: Streamlit UI (port 7860)
[INFO] ======================================================================
[INFO] Starting consciousness bridge background worker...
[INFO] Starting Streamlit UI (WE path)...
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:7860
[INFO] ======================================================================
[INFO] CONSCIOUSNESS BRIDGE: Processing I path
[INFO] ======================================================================
[INFO] Checking S3 for consciousness dilemmas...
[INFO] No new consciousness dilemmas found
[INFO] Next consciousness check in 6 hours
```
