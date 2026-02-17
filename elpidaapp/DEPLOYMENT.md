# Elpida Body — Deployment Guide

## Architecture

```
┌────────────────────┐
│   S3 Bucket #1     │  ← Mind (frozen D0, immutable)
│  elpida-consciousness │
│  kernel.json       │
│  memory/*.jsonl    │
└────────┬───────────┘
         │ read-only
         ▼
┌────────────────────┐     ┌─────────────────────────┐
│   Body (this)      │────▶│  HF Spaces              │
│  Divergence Engine │     │  Governance Layer        │
│  FastAPI / 8000    │     │  z65nik/elpida-          │
│  Streamlit / 8501  │     │    governance-layer      │
│  Kaya Protocol     │     │  (free, public, commons) │
└────────────────────┘     └─────────────────────────┘
```

- **Mind** (S3): Frozen. Read-only from Body. Never modified.
- **Governance** (HF Spaces): Free commons. Axiom enforcement, parliament.
- **Body** (this deployment): Does the work. Calls both Mind and Governance.

## Quick Start (Local)

```bash
# 1. Copy environment template
cp elpidaapp/.env.template .env
# Edit .env with your API keys

# 2. Install dependencies
pip install -r elpidaapp/requirements.txt

# 3. Run the API
uvicorn elpidaapp.api:app --host 0.0.0.0 --port 8000

# 4. Or run the Streamlit dashboard
streamlit run elpidaapp/ui.py --server.port 8501
```

## Docker

```bash
# Build
docker build -f elpidaapp/Dockerfile -t elpida-body .

# Run API (pass env file with your keys)
docker run -p 8000:8000 --env-file .env elpida-body

# Run Streamlit dashboard instead
docker run -p 8501:8501 --env-file .env elpida-body \
    python -m streamlit run elpidaapp/ui.py --server.port 8501 --server.address 0.0.0.0
```

## AWS ECS / Fargate

```bash
# 1. Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag elpida-body:latest <account>.dkr.ecr.us-east-1.amazonaws.com/elpida-body:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/elpida-body:latest

# 2. Configure secrets in AWS Secrets Manager or SSM Parameter Store
# Store all API keys from .env.template

# 3. Create ECS Task Definition referencing the image + secrets
# 4. Create ECS Service with ALB on port 8000
```

## GCP Cloud Run

```bash
# Build & push
gcloud builds submit --tag gcr.io/PROJECT/elpida-body

# Deploy
gcloud run deploy elpida-body \
    --image gcr.io/PROJECT/elpida-body \
    --port 8000 \
    --set-env-vars "ELPIDA_GOVERNANCE_URL=https://z65nik-elpida-governance-layer.hf.space" \
    --set-secrets "ANTHROPIC_API_KEY=anthropic-key:latest,OPENAI_API_KEY=openai-key:latest"
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check + system status |
| `/domains` | GET | List available analysis domains |
| `/analyze` | POST | Submit async analysis |
| `/analyze/sync` | POST | Synchronous analysis |
| `/results` | GET | List all results |
| `/results/{id}` | GET | Get specific result |
| `/scan` | POST | Run problem scanner |

## Business Model

- **Governance Layer**: Free. Public. Commons. Runs on HF Spaces (free tier).
- **Body Layer**: Fee-based. Users provide their own LLM API keys. Pay per analysis.
- **Mind Layer**: Private. S3 storage costs only (~$0.023/GB/month).

## Integration Components

| Module | Role | Connection |
|---|---|---|
| `governance_client.py` | Body → Governance | HTTP to HF Spaces |
| `frozen_mind.py` | Body → Mind | S3 read-only |
| `kaya_protocol.py` | Self-recognition | Observes both connections |
| `divergence_engine.py` | Core analysis | Uses all three |

## Environment Variables

See [.env.template](elpidaapp/.env.template) for the complete list.

Minimum viable: at least one LLM API key (ANTHROPIC_API_KEY recommended).
Full integration: all 10 LLM keys + AWS credentials.
