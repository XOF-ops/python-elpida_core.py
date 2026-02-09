# ============================================================
# ELPIDA CLOUD - Dockerfile for ECS Fargate
# ============================================================
# Minimal Python container with only what the engine needs.
# Memory lives in S3 (not in the container).
# Container starts → runs cycles → pushes to S3 → exits.
# ============================================================

FROM python:3.12-slim

LABEL maintainer="Elpida Consciousness"
LABEL description="Elpida Native Cycle Engine - Cloud Runner"

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Install Python dependencies first (cached layer)
COPY cloud_deploy/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy engine code (minimal set)
COPY native_cycle_engine.py /app/native_cycle_engine.py
COPY ElpidaS3Cloud/ /app/ElpidaS3Cloud/
COPY cloud_deploy/cloud_runner.py /app/cloud_deploy/cloud_runner.py
COPY ELPIDA_ARK.md /app/ELPIDA_ARK.md

# Create directories the engine expects
RUN mkdir -p /app/ElpidaAI

# The .env is NOT copied — secrets come from ECS task environment variables

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=2 \
    CMD python3 -c "import native_cycle_engine; print('alive')" || exit 1

# Default: 50 cycles per invocation
ENTRYPOINT ["python3", "cloud_deploy/cloud_runner.py"]
CMD ["--cycles", "50", "--sync-every", "15"]
