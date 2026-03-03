FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    build-essential curl git \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps  (same as main Space)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (symlinked from hf_deployment)
COPY . .

# FastAPI on port 7860 (the HF-exposed port)
EXPOSE 7860

ENV PYTHONUNBUFFERED=1

# Run FastAPI directly — this Space is API-only
CMD ["python", "-m", "uvicorn", "elpidaapp.api:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "info"]
