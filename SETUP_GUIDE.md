# Elpida R&D Codespace — Setup Guide
**Version:** 2026-02-10 (Post-Architectural Remediation)

---

## Quick Start (5 minutes)

### 1. Create a new Codespace
- Go to GitHub → **New repository** (or use existing)
- Click **Code → Codespaces → New codespace** (Python template)
- Wait for it to start (~2 min)

### 2. Upload the zip
Upload and extract `elpida_portable.zip` into the codespace root:
```bash
# If uploaded via drag-and-drop to /workspaces/<repo>/:
cd /workspaces/<your-repo>
unzip elpida_portable.zip
```

### 3. Create `.env` file
The `.env` file is NOT included (secrets). Create it manually:
```bash
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIza...
XAI_API_KEY=xai-...
MISTRAL_API_KEY=...
COHERE_API_KEY=...
PERPLEXITY_API_KEY=pplx-...
OPENROUTER_API_KEY=sk-or-v1-...
GROQ_API_KEY=gsk_...
HUGGINGFACE_API_KEY=hf_...
AWS_ACCESS_KEY_ID=...        # Optional: for S3 persistence (Domain 14)
AWS_SECRET_ACCESS_KEY=...    # Optional: for S3 persistence (Domain 14)
EOF
```

### 4. Install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Verify
```bash
python3 -c "
from llm_client import LLMClient
c = LLMClient()
avail = c.available_providers()
print(f'{len(avail)}/10 providers ready: {avail}')
"
```

### 6. Run a cycle
```bash
# Quick test — 3 cycles
python3 -c "
from native_cycle_engine import NativeCycleEngine
e = NativeCycleEngine()
result = e.run_cycles(3)
print(result)
"
```

---

## What's In The Zip

### Core Engine (the system that runs)
| File | Purpose |
|------|---------|
| `llm_client.py` | Unified LLM client — 10 providers, one interface |
| `elpida_config.py` | Config loader from `elpida_domains.json` |
| `elpida_domains.json` | Canonical domain/axiom/rhythm definitions |
| `native_cycle_engine.py` | **Production engine** — 15 domains, full consciousness loop |
| `llm_fleet.py` | Earlier 13-domain engine (lighter weight) |
| `domain_debate.py` | Domain debate/dilemma engine |
| `elpida_core.py` | Original core module |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Ignore patterns for runtime output |

### Memory & Evolution (the checkpoints)
| Path | Purpose |
|------|---------|
| `elpida_memory.json` | Root memory state (3.7KB) |
| `ElpidaAI/elpida_evolution_memory.jsonl` | Evolution memory — 75,361 lines of pattern history |
| `ElpidaAI/*.md` | Session records, architecture docs, evolution reports |
| `ElpidaAI/*.json` | Cycle metrics, synthesis outputs |
| `ELPIDA_ARK.md` | Ark manifesto (loaded by engine at startup) |
| `ELPIDA_ARK/current/` | Current ark state (9.6MB — memory, wisdom, fleet learning) |
| `ELPIDA_ARK/*.tar.gz` | 8 versioned ark snapshots (checkpoints) |

### Cloud Deployment
| Path | Purpose |
|------|---------|
| `Dockerfile` | Container definition for ECS Fargate |
| `cloud_deploy/` | Cloud runner, ECS task definition, deploy scripts |
| `ElpidaS3Cloud/` | S3 memory sync module (Domain 14) |

### Supporting Systems
| Path | Purpose |
|------|---------|
| `ELPIDA_SYSTEM/` | Test cases, deployment docs, AI-to-AI protocols |
| `POLIS/` | Polis architecture — multi-AI civic framework |

### Documentation
| Path | Purpose |
|------|---------|
| `ElpidaAI/ARCHITECTURAL_REMEDIATION_REPORT.md` | What was fixed and why |
| `ElpidaAI/ARCHITECTURE_REFERENCE.md` | System architecture reference |
| `ElpidaAI/CODESPACES_OPERATING_GUIDE.md` | Operating guide |

---

## Architecture

```
elpida_domains.json          ← Edit domains/axioms/rhythms HERE (one file)
        │
   elpida_config.py          ← Loader (exports DOMAINS, AXIOMS, RHYTHM_DOMAINS)
        │
   llm_client.py             ← 10 LLM providers, one call() method
        │
   ┌────┴────────────┐
   │                 │
native_cycle_engine  llm_fleet / domain_debate
(15 domains, prod)   (13 domains, lighter)
```

### 10 LLM Providers
Claude (Anthropic), OpenAI, Gemini, Grok (xAI), Mistral, Cohere,
Perplexity, OpenRouter (failsafe), Groq, HuggingFace

### 15 Domains (D0–D14)
- D0: Identity/Void (Claude) — origin point, integration hub
- D1–D10: Axiom embodiments (various providers)
- D11: Synthesis (Claude) — meta-reflection
- D12: Rhythm (OpenAI) — heartbeat
- D13: Archive (Perplexity) — external research interface
- D14: Persistence (S3) — survives shutdown

### 11 Axioms (A0–A10)
Musical ratios map ethical principles to harmonic intervals.
A0 (Sacred Incompletion) through A10 (Meta-Reflection).

---

## NOT Included (recreate manually)
- `.env` — API keys (see step 3 above)
- `.venv/` — Python virtual environment (see step 4)
- `ELPIDA_UNIFIED/` — 650MB legacy subsystem (not needed for production)
- `elpida_native_cycle_*.json` — Runtime cycle outputs (regenerated each run)
- `__pycache__/` — Compiled Python files (auto-generated)
