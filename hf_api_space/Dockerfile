FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps — use API-specific lighter requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt 2>&1 | tail -20

# Copy application code
COPY . .

# Ensure elpidaapp is a proper package
RUN test -f elpidaapp/__init__.py || echo '__version__ = "1.0.0"' > elpidaapp/__init__.py

# FastAPI on port 7860 (the HF-exposed port)
EXPOSE 7860

ENV PYTHONUNBUFFERED=1

# Healthcheck so HF knows we're alive
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:7860/health || exit 1

# Run FastAPI directly — this Space is API-only
CMD ["python", "-m", "uvicorn", "elpidaapp.api:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]
