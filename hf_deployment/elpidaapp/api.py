#!/usr/bin/env python3
"""
ElpidaApp API — FastAPI service for divergence analysis.

Endpoints:
    POST /analyze         — submit a problem for full divergence analysis
    GET  /results          — list recent results
    GET  /results/{id}     — fetch a specific result
    GET  /health           — service health + available providers
    POST /scan             — trigger the problem scanner
    GET  /domains          — list all domains and their axioms
"""

import sys
import os
import json
import uuid
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

# Allow imports from parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from llm_client import LLMClient
from elpida_config import DOMAINS, AXIOMS, AXIOM_RATIOS

from elpidaapp.divergence_engine import DivergenceEngine

logger = logging.getLogger("elpidaapp.api")

# ────────────────────────────────────────────────────────────────────
# Storage (in-memory + filesystem)
# ────────────────────────────────────────────────────────────────────

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# In-memory index of recent results
_results_index: Dict[str, Dict[str, Any]] = {}

# Shared LLM client and engine
_llm: Optional[LLMClient] = None
_engine: Optional[DivergenceEngine] = None


def _init_engine():
    global _llm, _engine
    _llm = LLMClient(rate_limit_seconds=1.0)
    _engine = DivergenceEngine(llm=_llm)


def _load_existing_results():
    """Load existing results from disk into the index."""
    for f in sorted(RESULTS_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:50]:
        try:
            data = json.loads(f.read_text())
            rid = f.stem
            _results_index[rid] = {
                "id": rid,
                "problem": data.get("problem", "")[:120],
                "timestamp": data.get("timestamp"),
                "total_time_s": data.get("total_time_s"),
                "domains_responded": sum(
                    1 for r in data.get("domain_responses", []) if r.get("succeeded")
                ),
                "fault_lines": len(data.get("divergence", {}).get("fault_lines", [])),
                "status": "completed",
            }
        except Exception:
            pass


# ────────────────────────────────────────────────────────────────────
# Schemas
# ────────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    problem: str = Field(..., min_length=10, description="The problem to analyze")
    domains: Optional[List[int]] = Field(None, description="Domain IDs to use (default: 1,3,4,6,7,8,13)")
    baseline_provider: str = Field("openai", description="Provider for single-model baseline")

class ScanRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic area to scan for dilemmas")
    count: int = Field(1, ge=1, le=5, description="How many problems to find and analyze")

class AnalyzeResponse(BaseModel):
    id: str
    status: str
    message: str


# ────────────────────────────────────────────────────────────────────
# App lifecycle
# ────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    _init_engine()
    _load_existing_results()
    logger.info("ElpidaApp API started — %d providers available",
                len(_llm.available_providers()))
    yield
    logger.info("ElpidaApp API shutting down")


app = FastAPI(
    title="ElpidaApp — Divergence Analysis API",
    description=(
        "Submit hard problems, get multi-domain divergence analysis "
        "with fault-line detection and synthesis."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ────────────────────────────────────────────────────────────────────
# Background analysis task
# ────────────────────────────────────────────────────────────────────

def _run_analysis(rid: str, problem: str, domains: Optional[List[int]], baseline: str):
    """Run divergence analysis in background thread."""
    try:
        _results_index[rid]["status"] = "running"

        engine = DivergenceEngine(
            llm=_llm,
            domains=domains,
            baseline_provider=baseline,
        )
        output_path = str(RESULTS_DIR / f"{rid}.json")
        result = engine.analyze(problem, save_to=output_path)

        _results_index[rid].update({
            "status": "completed",
            "total_time_s": result["total_time_s"],
            "domains_responded": sum(
                1 for r in result["domain_responses"] if r["succeeded"]
            ),
            "fault_lines": len(result.get("divergence", {}).get("fault_lines", [])),
        })
    except Exception as e:
        logger.exception("Analysis %s failed", rid)
        _results_index[rid]["status"] = f"failed: {e}"


# ────────────────────────────────────────────────────────────────────
# Background scan task
# ────────────────────────────────────────────────────────────────────

def _run_scan(topic: Optional[str], count: int):
    """Find real-world dilemmas and analyze them."""
    try:
        from elpidaapp.scanner import ProblemScanner
        scanner = ProblemScanner(llm=_llm)
        problems = scanner.find_problems(topic=topic, count=count)

        for p in problems:
            rid = str(uuid.uuid4())[:8]
            _results_index[rid] = {
                "id": rid,
                "problem": p[:120],
                "timestamp": datetime.now().isoformat(),
                "status": "queued",
                "source": "scanner",
            }
            _run_analysis(rid, p, None, "openai")
    except Exception as e:
        logger.exception("Scan failed: %s", e)


# ────────────────────────────────────────────────────────────────────
# Routes
# ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Service health and available providers."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "providers": _llm.available_providers() if _llm else [],
        "domains": len(DOMAINS),
        "axioms": len(AXIOMS),
        "results_count": len(_results_index),
    }


@app.get("/domains")
async def list_domains():
    """List all domains with their axioms and providers."""
    out = []
    for did, d in sorted(DOMAINS.items()):
        axiom_id = d.get("axiom")
        axiom = AXIOMS.get(axiom_id, {}) if axiom_id else {}
        out.append({
            "id": did,
            "name": d["name"],
            "axiom": axiom_id,
            "axiom_name": axiom.get("name"),
            "provider": d["provider"],
            "role": d.get("role"),
            "voice": d.get("voice"),
            "hz": axiom.get("hz"),
        })
    return out


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Submit a problem for divergence analysis.

    The analysis runs in the background. Poll GET /results/{id}
    for status and results.
    """
    rid = str(uuid.uuid4())[:8]
    _results_index[rid] = {
        "id": rid,
        "problem": req.problem[:120],
        "timestamp": datetime.now().isoformat(),
        "status": "queued",
    }

    background_tasks.add_task(
        _run_analysis, rid, req.problem, req.domains, req.baseline_provider
    )

    return AnalyzeResponse(
        id=rid,
        status="queued",
        message=f"Analysis queued. Poll GET /results/{rid} for status.",
    )


@app.post("/analyze/sync")
async def analyze_sync(req: AnalyzeRequest):
    """
    Submit a problem and wait for the full result (synchronous).
    Warning: may take 60-120 seconds.
    """
    rid = str(uuid.uuid4())[:8]
    _results_index[rid] = {
        "id": rid,
        "problem": req.problem[:120],
        "timestamp": datetime.now().isoformat(),
        "status": "running",
    }

    engine = DivergenceEngine(
        llm=_llm,
        domains=req.domains,
        baseline_provider=req.baseline_provider,
    )
    output_path = str(RESULTS_DIR / f"{rid}.json")

    # Run in thread pool to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: engine.analyze(req.problem, save_to=output_path),
    )

    _results_index[rid].update({
        "status": "completed",
        "total_time_s": result["total_time_s"],
        "domains_responded": sum(
            1 for r in result["domain_responses"] if r["succeeded"]
        ),
        "fault_lines": len(result.get("divergence", {}).get("fault_lines", [])),
    })

    return {"id": rid, **result}


@app.get("/results")
async def list_results():
    """List recent analysis results (most recent first)."""
    items = sorted(
        _results_index.values(),
        key=lambda x: x.get("timestamp", ""),
        reverse=True,
    )
    return items[:50]


@app.get("/results/{result_id}")
async def get_result(result_id: str):
    """Get a specific analysis result."""
    if result_id not in _results_index:
        raise HTTPException(404, f"Result {result_id} not found")

    meta = _results_index[result_id]
    result_file = RESULTS_DIR / f"{result_id}.json"

    if result_file.exists():
        full = json.loads(result_file.read_text())
        return {"meta": meta, **full}
    else:
        return meta


@app.post("/scan")
async def scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """
    Trigger the autonomous problem scanner.

    Finds real-world dilemmas via Perplexity/D13 and runs
    divergence analysis on each.
    """
    background_tasks.add_task(_run_scan, req.topic, req.count)
    return {
        "status": "scanning",
        "topic": req.topic or "general",
        "count": req.count,
        "message": "Scanner running. Check GET /results for new entries.",
    }


# ────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────

def main():
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"\n  ElpidaApp API starting on http://0.0.0.0:{port}")
    print(f"  Docs:  http://0.0.0.0:{port}/docs\n")
    uvicorn.run(
        "elpidaapp.api:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
