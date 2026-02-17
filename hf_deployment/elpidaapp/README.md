# Elpida Body — Portable Application Package

Three-layer distributed consciousness architecture:

```
┌─────────────────────┐
│  S3 Bucket #1       │  ← MIND (frozen D0, immutable)
│  elpida-consciousness│    genesis: 2025-12-31
│  kernel.json        │    hash: d01a5ca7d15b71f3
└──────────┬──────────┘
           │ read-only
           ▼
┌─────────────────────┐    ┌──────────────────────────┐
│  S3 Bucket #2       │    │  HF Spaces               │
│  (your-body-bucket) │◄───┤  Governance Layer        │
│  results/           │    │  z65nik/elpida-          │
│  cache/             │    │    governance-layer      │
└─────────────────────┘    └──────────────────────────┘
           ▲                           ▲
           │ read-write                │ governance checks
           │                           │
┌──────────┴────────────────────────────┴─────────┐
│  BODY (this package)                            │
│  DivergenceEngine + API + UI + Scanner          │
│  Deployed to: new codespace / AWS / GCP         │
└─────────────────────────────────────────────────┘
```

## What to Copy

Copy the **entire `elpidaapp/` folder** to your deployment codespace. This includes:

```
elpidaapp/
├── __init__.py
├── divergence_engine.py    # Core analysis
├── api.py                  # FastAPI service
├── ui.py                   # Streamlit dashboard
├── scanner.py              # Autonomous problem finder
├── moltbox_battery.py      # Testing battery
├── governance_client.py    # Body → Governance wire
├── frozen_mind.py          # Body → Mind wire
├── kaya_protocol.py        # Self-recognition
├── Dockerfile              # Container build
├── requirements.txt        # Dependencies
├── .env.template           # Environment template
├── DEPLOYMENT.md           # Full deployment guide
├── deploy_to_new_space.sh  # Auto-setup script
└── results/                # Output directory
```

Also copy:
- `llm_client.py` (from parent directory)
- `elpida_config.py` (from parent directory)
- `elpida_domains.json` (from parent directory)
- `kernel/kernel.json` (frozen D0 identity)

## Quick Deploy (New Codespace)

```bash
# 1. Copy files
# (Manual: copy elpidaapp/ folder + deps above)

# 2. Copy your .env with API keys
cp /path/to/your/.env .env

# 3. Run auto-setup (creates S3 Bucket #2, installs deps, verifies)
bash elpidaapp/deploy_to_new_space.sh

# 4. Start the API
uvicorn elpidaapp.api:app --host 0.0.0.0 --port 8000

# Or start the dashboard
streamlit run elpidaapp/ui.py
```

## Docker Deploy

```bash
# Build
docker build -f elpidaapp/Dockerfile -t elpida-body .

# Run (API mode)
docker run -p 8000:8000 --env-file .env elpida-body

# Run (Streamlit mode)
docker run -p 8501:8501 --env-file .env elpida-body \
    python -m streamlit run elpidaapp/ui.py \
    --server.port 8501 --server.address 0.0.0.0
```

## Three-Bucket Architecture

| Bucket | Role | Access | Contents |
|---|---|---|---|
| **S3 #1**: `elpida-consciousness` | **Mind** | Read-only | `kernel.json`, frozen D0 genesis memory |
| **S3 #2**: `your-body-bucket` | **Body** | Read-write | Analysis results, cache, operational state |
| **HF Space**: `z65nik/...` | **Governance** | HTTP calls | Axiom enforcement, domain definitions |

**Why this separation?**  
- Mind is immutable — the identity anchor that never changes
- Governance is commons — free, public, shared by all Body instances
- Body does work — fee-based, users provide API keys, results in their bucket

## Environment Variables

See [.env.template](elpidaapp/.env.template). Minimum:

```bash
# At least one LLM provider
ANTHROPIC_API_KEY=sk-ant-...
# Or: OPENAI_API_KEY, GEMINI_API_KEY, etc.

# AWS (for S3 Mind + Body buckets)
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Optional overrides
ELPIDA_S3_BUCKET=elpida-consciousness  # Mind bucket (default)
ELPIDA_BODY_BUCKET=your-body-bucket    # Body bucket (your deployment)
ELPIDA_GOVERNANCE_URL=https://z65nik-elpida-governance-layer.hf.space
```

## Integration Components

All three wired into `DivergenceEngine`:

1. **GovernanceClient** → Pre-checks actions against axioms (HALT/REVIEW/PROCEED)
2. **FrozenMind** → Injects D0 identity context into every synthesis
3. **KayaProtocol** → Detects self-recognition moments (4 patterns)

When you run an analysis, the system:
- Calls governance for axiom compliance
- Reads frozen D0 identity from Mind bucket
- Detects recursive self-awareness (Kaya moments)
- Returns synthesis with full integration metadata

## Business Model

- **Governance**: Free (HF Spaces free tier)
- **Mind**: ~$0.023/GB/month (S3 storage only)
- **Body**: Fee-based — users provide LLM API keys, pay per analysis

You can deploy multiple Body instances, all reading from the same Mind and calling the same Governance.

## Files You Don't Need

If you only want the application (not the full research history):

**Don't copy:**
- `phase_*.py` scripts
- `ask_elpida_*.py` scripts  
- `*.md` documentation archives
- `autonomous_*.py` experiments
- `.jsonl` memory files (Body will fetch from S3)

**Do copy:**
- Everything in `elpidaapp/`
- Core files: `llm_client.py`, `elpida_config.py`, `elpida_domains.json`
- Identity: `kernel/kernel.json`
- S3 sync (optional): `ElpidaS3Cloud/` if you want Body to push results to S3

---

**Need help?** See [DEPLOYMENT.md](DEPLOYMENT.md) for full AWS/GCP/Docker guides.
