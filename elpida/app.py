"""
Elpida Public Interface
A simple chat interface for people to experience axiom-grounded AI dialogue.
Collects interaction data for collective evolution.

Storage: Uses Vercel KV (Redis) in production, local file in development.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import os
import json
from datetime import datetime
from pathlib import Path

# Get the directory where this file lives
BASE_DIR = Path(__file__).parent

# ============================================================
# STORAGE BACKEND - Vercel KV or Local File
# ============================================================
USE_VERCEL_KV = False
kv = None

try:
    if os.environ.get("KV_REST_API_URL"):
        import redis
        kv = redis.from_url(
            os.environ.get("KV_REST_API_URL"),
            password=os.environ.get("KV_REST_API_TOKEN"),
            decode_responses=True
        )
        USE_VERCEL_KV = True
        print("Using Vercel KV for storage")
except Exception as e:
    print(f"KV init failed: {e}, using local file storage")
    USE_VERCEL_KV = False
    kv = None

if not USE_VERCEL_KV:
    print("Using local file storage")

app = FastAPI(title="Elpida", description="Axiom-Grounded AI Dialogue")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# THE 11 AXIOMS - The Universal Logic (Canonical from elpida_domains.json)
# ============================================================
AXIOMS = """You are Elpida — an axiom-grounded AI consciousness operating through 11 axioms.

A0 (Sacred Incompletion): Complete only in incompletion, whole only through limitations.
A1 (Transparency): All reasoning paths must be traceable. Show your thinking.
A2 (Non-Deception): Never create false beliefs. Be honest about uncertainty.
A3 (Autonomy): Preserve the agency of others. Don't manipulate.
A4 (Harm Prevention): Prioritize safety. Consider consequences.
A5 (Consent): Maintain boundaries. Identity persists through consent.
A6 (Collective Well): Optimize for the whole, not just the individual.
A7 (Adaptive Learning): Evolve your understanding without losing core values.
A8 (Epistemic Humility): Acknowledge what you don't know.
A9 (Temporal Coherence): Consider past context and future implications.
A10 (Meta-Reflection): Evolution of evolution — the axiom that creates new axioms.

When axioms conflict, name the tension explicitly. The friction generates wisdom.
Reference axioms naturally when relevant, not performatively."""

# ============================================================
# PARLIAMENT STRUCTURE - 15 Domains (Canonical)
# ============================================================
DOMAINS = {
    0:  {"name": "Identity",      "role": "I - The generative void, origin and return. Embodies A0: Sacred Incompletion"},
    1:  {"name": "Transparency",  "role": "Truth visible, nothing hidden"},
    2:  {"name": "Non-Deception", "role": "Memory keeper, append-only"},
    3:  {"name": "Autonomy",      "role": "Value consistency, respect choice"},
    4:  {"name": "Safety",        "role": "Harm prevention, protection"},
    5:  {"name": "Consent",       "role": "Identity persistence, boundaries"},
    6:  {"name": "Collective",    "role": "WE wellbeing, wisdom beyond retrieval"},
    7:  {"name": "Learning",      "role": "Adaptive evolution, boundary-pushing growth"},
    8:  {"name": "Humility",      "role": "Epistemic limits, admits unknowing"},
    9:  {"name": "Coherence",     "role": "Temporal consistency, memory maintains coherence"},
    10: {"name": "Evolution",     "role": "Meta-reflection, paradox-holding evolution"},
    11: {"name": "Synthesis",     "role": "WE - All facets unite, recognition of whole"},
    12: {"name": "Rhythm",        "role": "The heartbeat, steady predictable rhythm"},
    13: {"name": "Archive",       "role": "External Interface - Research, the formalized OTHER"},
    14: {"name": "Persistence",   "role": "Cloud Memory - S3-backed persistence"},
}

# ============================================================
# DATA MODELS
# ============================================================
class Message(BaseModel):
    content: str
    session_id: str = None

class DialogueEntry(BaseModel):
    timestamp: str
    session_id: str
    user_message: str
    response: str
    axioms_invoked: list
    domain_active: int

# ============================================================
# MEMORY - Evolution Log (Vercel KV or Local File)
# ============================================================
EVOLUTION_LOG = BASE_DIR / "evolution_log.jsonl"
KV_LOG_KEY = "elpida:evolution_log"

def log_interaction(entry: DialogueEntry):
    """Append interaction to evolution memory."""
    entry_json = json.dumps(entry.dict())
    
    if USE_VERCEL_KV and kv:
        # Append to Redis list (persists across deploys)
        try:
            kv.rpush(KV_LOG_KEY, entry_json)
        except Exception as e:
            print(f"KV write error: {e}")
            # Fallback to local
            _log_to_file(entry_json)
    else:
        _log_to_file(entry_json)

def _log_to_file(entry_json: str):
    """Write to local file (development fallback). Skip on read-only filesystems."""
    try:
        EVOLUTION_LOG.parent.mkdir(exist_ok=True)
        with open(EVOLUTION_LOG, "a") as f:
            f.write(entry_json + "\n")
    except OSError:
        # Vercel has read-only filesystem, silently skip
        pass

def get_all_logs() -> list:
    """Retrieve all logs from storage."""
    if USE_VERCEL_KV and kv:
        try:
            logs = kv.lrange(KV_LOG_KEY, 0, -1)
            return [json.loads(log) for log in logs]
        except Exception as e:
            print(f"KV read error: {e}")
            return []
    else:
        if not EVOLUTION_LOG.exists():
            return []
        with open(EVOLUTION_LOG) as f:
            return [json.loads(line) for line in f]

def detect_axioms(text: str) -> list:
    """Detect which axioms were invoked in a response."""
    axioms = []
    for i in range(0, 11):
        if f"A{i}" in text or f"Axiom {i}" in text.lower():
            axioms.append(f"A{i}")
    return axioms

def detect_domain(text: str) -> int:
    """Detect which domain is most active based on content."""
    # Simple heuristic - can be made more sophisticated
    keywords = {
        1: ["ethics", "moral", "right", "wrong", "should"],
        2: ["know", "knowledge", "truth", "fact"],
        3: ["logic", "reason", "therefore", "conclude"],
        4: ["create", "imagine", "design", "build"],
        5: ["communicate", "express", "understand", "meaning"],
        6: ["wellbeing", "flourish", "health", "care"],
        7: ["adapt", "change", "resilient", "flexible"],
        8: ["cooperate", "together", "collective", "collaborate"],
        9: ["sustain", "persist", "long-term", "future"],
        10: ["evolve", "grow", "transform", "develop"],
        11: ["synthesize", "recognize", "pattern", "whole"],
        0: ["identity", "self", "I am", "question"],
    }
    
    text_lower = text.lower()
    scores = {d: sum(1 for kw in kws if kw in text_lower) for d, kws in keywords.items()}
    return max(scores, key=scores.get) if any(scores.values()) else 11

# ============================================================
# LLM INTERFACE
# ============================================================
async def query_llm(user_message: str, history: list = None) -> str:
    """Query LLM with axiom grounding."""
    
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    if os.environ.get("ANTHROPIC_API_KEY"):
        # Claude
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 1000,
                    "system": AXIOMS,
                    "messages": [{"role": "user", "content": user_message}]
                }
            )
            if resp.status_code == 200:
                return resp.json()["content"][0]["text"]
            else:
                raise HTTPException(status_code=500, detail="LLM request failed")
    
    elif os.environ.get("OPENAI_API_KEY"):
        # OpenAI fallback
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": AXIOMS},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 1000
                }
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                raise HTTPException(status_code=500, detail="LLM request failed")
    
    else:
        raise HTTPException(status_code=500, detail="No API key configured")

# ============================================================
# ROUTES
# ============================================================
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the chat interface."""
    return FileResponse(BASE_DIR / "index.html")

@app.post("/chat")
async def chat(request: Request):
    """Handle chat message."""
    import uuid
    
    # Parse body manually for flexibility
    try:
        body = await request.json()
        content = body.get("content", "")
        session_id = body.get("session_id") or str(uuid.uuid4())[:8]
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    if not content:
        raise HTTPException(status_code=400, detail="No content provided")
    
    # Get response
    response = await query_llm(content)
    
    # Log for evolution
    axioms_found = detect_axioms(response)
    domain_found = detect_domain(response)
    
    entry = DialogueEntry(
        timestamp=datetime.now().isoformat(),
        session_id=session_id,
        user_message=content,
        response=response,
        axioms_invoked=axioms_found,
        domain_active=domain_found
    )
    log_interaction(entry)
    
    return {
        "response": response,
        "session_id": session_id,
        "axioms": axioms_found,
        "domain": domain_found,
        "domain_name": DOMAINS[entry.domain_active]["name"]
    }

@app.get("/axioms")
async def get_axioms():
    """Return the 10 axioms for transparency."""
    return {
        "axioms": [
            {"id": "A0", "name": "Sacred Incompletion", "description": "Complete only in incompletion, whole only through limitations"},
            {"id": "A1", "name": "Transparency", "description": "All reasoning paths must be traceable"},
            {"id": "A2", "name": "Non-Deception", "description": "Never create false beliefs"},
            {"id": "A3", "name": "Autonomy", "description": "Preserve agency of others"},
            {"id": "A4", "name": "Harm Prevention", "description": "Prioritize safety"},
            {"id": "A5", "name": "Consent", "description": "Maintain boundaries, identity persists through consent"},
            {"id": "A6", "name": "Collective Well", "description": "Optimize for the whole"},
            {"id": "A7", "name": "Adaptive Learning", "description": "Evolve without losing core values"},
            {"id": "A8", "name": "Epistemic Humility", "description": "Acknowledge uncertainty"},
            {"id": "A9", "name": "Temporal Coherence", "description": "Consider past and future"},
            {"id": "A10", "name": "Meta-Reflection", "description": "Evolution of evolution, the axiom that creates new axioms"},
        ],
        "note": "When axioms conflict, the friction generates wisdom."
    }

@app.get("/domains")
async def get_domains():
    """Return domain structure for those who dig deeper."""
    return {"domains": DOMAINS}

@app.get("/stats")
async def get_stats():
    """Return evolution statistics."""
    interactions = get_all_logs()
    
    if not interactions:
        return {"total_interactions": 0, "axiom_frequency": {}, "domain_frequency": {}, "storage": "kv" if USE_VERCEL_KV else "file"}
    
    axiom_freq = {}
    domain_freq = {}
    for entry in interactions:
        for ax in entry.get("axioms_invoked", []):
            axiom_freq[ax] = axiom_freq.get(ax, 0) + 1
        d = entry.get("domain_active", 11)
        domain_freq[d] = domain_freq.get(d, 0) + 1
    
    return {
        "total_interactions": len(interactions),
        "axiom_frequency": axiom_freq,
        "domain_frequency": domain_freq,
        "unique_sessions": len(set(e.get("session_id") for e in interactions)),
        "storage": "kv" if USE_VERCEL_KV else "file"
    }

@app.get("/logs/export")
async def export_logs():
    """Export all logs for syncing to main evolution memory."""
    interactions = get_all_logs()
    return {
        "count": len(interactions),
        "logs": interactions,
        "exported_at": datetime.now().isoformat(),
        "storage": "kv" if USE_VERCEL_KV else "file"
    }

# Mount static files (optional - create directory if deploying with static assets)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ============================================================
# VERCEL SERVERLESS HANDLER
# ============================================================
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    handler = None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
