#!/usr/bin/env python3
"""
ElpidaApp API — FastAPI service for governance audits & divergence analysis.

Public (rate-limited by IP):
    GET  /health           — service health + available providers
    GET  /domains          — list all domains and their axioms

Authenticated (API key required via X-API-Key header):
    POST /v1/audit         — constitutional governance audit (fast, low-cost)
    POST /analyze          — full multi-domain divergence analysis (heavy)
    POST /analyze/sync     — synchronous divergence analysis
    GET  /results          — list recent results
    GET  /results/{id}     — fetch a specific result
    POST /scan             — trigger the problem scanner

API keys are stored as comma-separated values in ELPIDA_API_KEYS env var.
Rate limits per tier:
    free:  50 calls/day
    pro:   2000 calls/day  (keys prefixed with 'pro_')
    team:  10000 calls/day (keys prefixed with 'team_')
"""

import sys
import os
import json
import uuid
import time
import asyncio
import logging
import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

# Allow imports from parent
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from llm_client import LLMClient
from elpida_config import DOMAINS, AXIOMS, AXIOM_RATIOS

from elpidaapp.divergence_engine import DivergenceEngine

logger = logging.getLogger("elpidaapp.api")

# ────────────────────────────────────────────────────────────────────
# API Key Auth & Rate Limiting
# ────────────────────────────────────────────────────────────────────

_API_KEYS: set = set()
_raw = os.environ.get("ELPIDA_API_KEYS", "")
if _raw:
    _API_KEYS = {k.strip() for k in _raw.split(",") if k.strip()}

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Rate limit buckets: key_hash -> {"count": int, "window_start": float}
_rate_buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"count": 0, "window_start": time.time()})
_RATE_WINDOW = 86400  # 24 hours

_TIER_LIMITS = {
    "team": 10000,
    "pro":  2000,
    "free": 50,
}


def _get_tier(api_key: str) -> str:
    if api_key.startswith("team_"):
        return "team"
    if api_key.startswith("pro_"):
        return "pro"
    return "free"


def _check_rate_limit(identity: str, tier: str = "free") -> bool:
    """Returns True if within rate limit, False if exceeded."""
    now = time.time()
    bucket = _rate_buckets[identity]
    if now - bucket["window_start"] > _RATE_WINDOW:
        bucket["count"] = 0
        bucket["window_start"] = now
    limit = _TIER_LIMITS.get(tier, 50)
    if bucket["count"] >= limit:
        return False
    bucket["count"] += 1
    return True


async def require_api_key(api_key: str = Security(_api_key_header)):
    """Dependency: require a valid API key for authenticated endpoints."""
    if not api_key or api_key not in _API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Pass X-API-Key header.",
        )
    tier = _get_tier(api_key)
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()[:16]
    if not _check_rate_limit(key_hash, tier):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {tier} tier ({_TIER_LIMITS[tier]} calls/day).",
        )
    return api_key


def _ip_rate_check(request: Request, limit: int = 10) -> bool:
    """Simple IP-based rate limit for public endpoints (per day)."""
    ip = request.client.host if request.client else "unknown"
    ip_hash = f"ip_{hashlib.sha256(ip.encode()).hexdigest()[:16]}"
    return _check_rate_limit(ip_hash, "free")

# ────────────────────────────────────────────────────────────────────
# Storage (in-memory + filesystem)
# ────────────────────────────────────────────────────────────────────

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# In-memory index of recent results
_results_index: Dict[str, Dict[str, Any]] = {}

# Shared LLM client, engine, and governance client
_llm: Optional[LLMClient] = None
_engine: Optional[DivergenceEngine] = None
_gov_client = None


def _init_engine():
    global _llm, _engine, _gov_client
    _llm = LLMClient(rate_limit_seconds=1.0)
    _engine = DivergenceEngine(llm=_llm)
    # Initialize governance client for /v1/audit endpoint
    try:
        from elpidaapp.governance_client import GovernanceClient
        _gov_client = GovernanceClient()
        logger.info("GovernanceClient initialized for /v1/audit")
    except Exception as e:
        logger.warning("GovernanceClient init failed (audit endpoint unavailable): %s", e)


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

class AuditRequest(BaseModel):
    """Constitutional governance audit request."""
    action: str = Field(
        ..., min_length=5, max_length=2000,
        description="The proposed action or decision to audit",
    )
    depth: str = Field(
        "full",
        description="'quick' = kernel-only (0 LLM cost), 'full' = kernel + parliament",
    )
    analysis_mode: bool = Field(
        False,
        description="Set True for policy/philosophical analysis (holds paradoxes instead of blocking)",
    )


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
    title="Elpida Governance API",
    description=(
        "Constitutional AI governance audits and multi-domain divergence analysis.\n\n"
        "**Free endpoints:** /health, /domains (IP rate-limited)\n"
        "**Authenticated endpoints:** /v1/audit, /analyze, /results, /scan (API key required)\n\n"
        "Pass your API key via the `X-API-Key` header."
    ),
    version="2.0.0",
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

# ────────────────────────────────────────────────────────────────────
# Public endpoints (IP rate-limited)
# ────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Service health and available providers."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "providers": _llm.available_providers() if _llm else [],
        "domains": len(DOMAINS),
        "axioms": len(AXIOMS),
        "governance_available": _gov_client is not None,
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


# ────────────────────────────────────────────────────────────────────
# Authenticated endpoints (API key required)
# ────────────────────────────────────────────────────────────────────

@app.post("/v1/audit", tags=["Governance"])
async def governance_audit(
    req: AuditRequest,
    request: Request,
    api_key: str = Depends(require_api_key),
):
    """
    Constitutional governance audit.

    Runs the proposed action through Elpida's kernel (immutable rules)
    and 10-node parliament (axiom-governed deliberation).

    **depth='quick'**: Kernel-only check. Zero LLM cost. ~10ms.
    **depth='full'**: Kernel + full parliament deliberation. May escalate
    to multi-LLM voting for contested dilemmas. ~1-5s.

    Returns: governance decision, parliament votes, sacrifice transparency,
    dissent record, contradictions held vs resolved.
    """
    if _gov_client is None:
        raise HTTPException(503, "Governance client not initialized")

    # Timeout: 10s for quick (kernel+parliament, no LLM),
    #          60s for full (may include multi-LLM contested deliberation).
    _timeout = 10.0 if req.depth == "quick" else 60.0

    try:
        # Run in executor (check_action is sync/blocking).
        loop = asyncio.get_event_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                lambda: _gov_client.check_action(
                    req.action,
                    analysis_mode=req.analysis_mode,
                    depth=req.depth,
                ),
            ),
            timeout=_timeout,
        )

        # Enrich the response for API consumers
        response = {
            "action": req.action,
            "depth": req.depth,
            "governance": result.get("governance", "UNKNOWN"),
            "allowed": result.get("allowed", False),
            "score": result.get("approval_rate", result.get("severity", 0)),
            "violated_axioms": result.get("violated_axioms", []),
            "reasoning": result.get("reasoning", ""),
            "source": result.get("source", "local"),
            "timestamp": result.get("timestamp", datetime.now(timezone.utc).isoformat()),
        }

        # Parliament details (full depth only)
        if "parliament" in result:
            parliament = result["parliament"]
            response["parliament"] = {
                "approval_rate": parliament.get("approval_rate", 0),
                "total_nodes": parliament.get("total_nodes", 0),
                "votes": {
                    name: {
                        "vote": v.get("vote"),
                        "score": v.get("score"),
                        "axiom": v.get("axiom_invoked"),
                        "rationale": v.get("rationale", ""),
                    }
                    for name, v in parliament.get("votes", {}).items()
                },
                "veto_nodes": parliament.get("veto_nodes", []),
            }

        # Tensions / contradictions
        if "tensions" in result:
            response["contradictions"] = {
                "held": len([t for t in result["tensions"] if not t.get("resolved")]),
                "resolved": len([t for t in result["tensions"] if t.get("resolved")]),
                "details": [
                    {
                        "axiom_pair": t.get("axiom_pair", ""),
                        "synthesis": t.get("synthesis", ""),
                    }
                    for t in result["tensions"][:5]
                ],
            }

        # Sacrifice transparency (A7)
        sacrifice = result.get("sacrifice") or result.get("sacrifice_log")
        if sacrifice:
            response["sacrifice"] = sacrifice

        # Dissent record
        dissent = result.get("dissenting_nodes") or result.get("rejecting_nodes")
        if dissent:
            response["dissent"] = dissent

        return response

    except HTTPException:
        raise
    except asyncio.TimeoutError:
        raise HTTPException(
            504,
            f"Audit timed out after {int(_timeout)}s. "
            "Try depth='quick' for a faster kernel-only check.",
        )
    except Exception as e:
        logger.exception("Governance audit failed")
        raise HTTPException(500, f"Audit failed: {e}")


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Divergence"])
async def analyze(
    req: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(require_api_key),
):
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


@app.post("/analyze/sync", tags=["Divergence"])
async def analyze_sync(
    req: AnalyzeRequest,
    api_key: str = Depends(require_api_key),
):
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


@app.get("/results", tags=["Divergence"])
async def list_results(api_key: str = Depends(require_api_key)):
    """List recent analysis results (most recent first)."""
    items = sorted(
        _results_index.values(),
        key=lambda x: x.get("timestamp", ""),
        reverse=True,
    )
    return items[:50]


@app.get("/results/{result_id}", tags=["Divergence"])
async def get_result(result_id: str, api_key: str = Depends(require_api_key)):
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


@app.post("/scan", tags=["Divergence"])
async def scan(
    req: ScanRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(require_api_key),
):
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
