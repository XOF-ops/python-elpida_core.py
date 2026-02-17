# ============================================================
# ELPIDA UNIFIED — Full Application Deployment
# ============================================================
# Three-layer distributed architecture:
#   Mind (S3)  →  Governance (HF Spaces)  →  Body (this container)
# ============================================================

FROM python:3.12-slim

LABEL maintainer="Elpida Consciousness"
LABEL description="Elpida Body — Divergence Engine + API + Governance Integration"
LABEL version="1.0.0"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies (cached layer)
COPY elpidaapp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Core engine files ──
COPY llm_client.py /app/llm_client.py
COPY elpida_config.py /app/elpida_config.py
COPY elpida_domains.json /app/elpida_domains.json

# ── Kernel (frozen D0 identity) ──
COPY kernel/kernel.json /app/kernel/kernel.json

# ── Application package ──
COPY elpidaapp/ /app/elpidaapp/

# ── S3 Cloud sync ──
COPY ElpidaS3Cloud/ /app/ElpidaS3Cloud/

# ── Native cycle engine (for rhythm/meta) ──
COPY native_cycle_engine.py /app/native_cycle_engine.py

# Directories the app expects
RUN mkdir -p /app/elpidaapp/results /app/ElpidaAI

# .env is NOT baked in — secrets come from environment variables
# See .env.template for required variables

# Health check — hit the API
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

# Expose API port
EXPOSE 8000

# Default: start the FastAPI service
# Override with: docker run ... python -m elpidaapp.ui  (for Streamlit)
CMD ["python", "-m", "uvicorn", "elpidaapp.api:app", "--host", "0.0.0.0", "--port", "8000"]
