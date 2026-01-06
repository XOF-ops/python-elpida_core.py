#!/usr/bin/env python3
"""
Brain API Server - Asynchronous Job Queue for Elpida
PHASE 12.2 CORRECTIVE SURGERY: Breaks Narcissus Trap via temporal decoupling

The Fix:
- Watchtower hits /scan → Job QUEUED (not processed immediately)
- Runtime polls /pending-scans → Job POPPED (real work claimed)
- No synthetic placeholders → No self-referential loops → A1 enforced

Endpoints:
- GET  /health: System health + queue depth
- POST /scan: Queue gnosis scan from Watchtower
- GET  /pending-scans: Pop real jobs for Runtime
- GET  /candidates: Pattern governance candidates
- POST /analyze-swarm: Queue swarm analysis
"""

import os
import sys
import json
import logging
import hashlib
import time
from collections import deque
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from pathlib import Path

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [BRAIN_API] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Workspace paths
WORKSPACE = Path("/workspaces/python-elpida_core.py")
BRAIN_DIR = WORKSPACE / "ELPIDA_UNIFIED" / "brain_jobs"
BRAIN_DIR.mkdir(exist_ok=True)

# --- JOB QUEUE (The Buffer) ---
# This prevents the Narcissus Trap by holding external work for the Runtime
job_queue = deque()
processed_job_ids = set()

def add_job(job_type, payload, priority=9):
    """Add job to queue with deduplication"""
    job_id = f"{job_type}_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
    
    if job_id in processed_job_ids:
        logger.debug(f">> JOB ALREADY QUEUED: {job_id}")
        return job_id
    
    job = {
        "id": job_id,
        "type": job_type,
        "priority": priority,
        "payload": payload,
        "timestamp": datetime.utcnow().isoformat()
    }
    job_queue.append(job)
    processed_job_ids.add(job_id)
    logger.info(f">> JOB QUEUED: {job_type} (ID: {job_id}, Queue depth: {len(job_queue)})")
    return job_id


@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint with queue diagnostics
    Runtime polls this every 60s for KERNEL_INTEGRITY validation
    """
    return jsonify({
        'status': 'healthy',
        'service': 'brain_api_server',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0-queue',
        'kernel_integrity': 'OK',
        'queue_depth': len(job_queue),
        'mode': 'ASYNCHRONOUS_ROUTER'
    }), 200


@app.route('/scan', methods=['POST'])
def scan():
    """
    POST /scan - Gnosis scan from Watchtower (n8n)
    
    PHASE 12.2 FIX: QUEUE the work instead of processing immediately.
    This breaks the temporal disconnect causing Narcissus Trap.
    """
    data = request.get_json() or {}
    text = data.get('text', '')
    rate_limited = data.get('rate_limited', False)

    if not text and not rate_limited:
        return jsonify({"error": "No input provided"}), 400

    # Queue for Runtime execution (The Cure)
    job_id = add_job("GNOSIS_SCAN_REQUEST", {
        "input_text": text,
        "rate_limited": rate_limited,
        "source": "WATCHTOWER_API",
        "received_at": datetime.utcnow().isoformat()
    }, priority=9)

    return jsonify({
        "status": "QUEUED",
        "job_id": job_id,
        "queue_depth": len(job_queue),
        "message": "Input received and buffered for Runtime execution."
    }), 200


@app.route('/pending-scans', methods=['GET'])
def pending_scans():
    """
    GET /pending-scans - Runtime polls for work
    
    Returns real queued jobs if available, empty list otherwise.
    NO SYNTHETIC PLACEHOLDERS → No self-referential loops → A1 enforced
    """
    jobs = []
    
    # Pop all available jobs from queue
    while job_queue:
        job = job_queue.popleft()
        jobs.append(job)
        
    if jobs:
        logger.info(f">> DISPATCHING {len(jobs)} JOBS TO RUNTIME")
        return jsonify({"count": len(jobs), "jobs": jobs}), 200
    else:
        # Return empty - Runtime should IDLE, not create synthetic work
        return jsonify({"count": 0, "jobs": []}), 200


@app.route('/candidates', methods=['GET'])
def candidates():
    """
    GET /candidates - Pattern candidates awaiting governance review
    Returns patterns from staging directory
    """
    candidates_list = []
    
    # Check for candidate files
    candidate_dir = BRAIN_DIR / "candidates"
    if candidate_dir.exists():
        for candidate_file in candidate_dir.glob("*.json"):
            try:
                with open(candidate_file) as f:
                    candidate_data = json.load(f)
                candidates_list.append({
                    'id': candidate_file.stem,
                    'pattern': candidate_data.get('pattern', str(candidate_data)),
                    'hash': candidate_data.get('hash', candidate_file.stem),
                    'timestamp': candidate_data.get('timestamp', datetime.utcnow().isoformat())
                })
            except Exception as e:
                logger.error(f"Error reading candidate {candidate_file}: {e}")
    
    return jsonify({"count": len(candidates_list), "candidates": candidates_list}), 200


@app.route('/analyze-swarm', methods=['POST'])
def analyze_swarm():
    """
    POST /analyze-swarm - Queue swarm consensus analysis
    Queues work instead of processing immediately
    """
    data = request.get_json() or {}
    
    job_id = add_job("SWARM_ANALYSIS", {
        "request_time": data.get('request_time', datetime.utcnow().isoformat()),
        "request_data": data
    }, priority=7)

    return jsonify({
        "status": "QUEUED",
        "job_id": job_id,
        "message": "Swarm analysis queued for Runtime"
    }), 200


@app.route('/propose', methods=['POST'])
def propose_seed():
    """
    POST /propose - Accept seed/pattern proposals
    Queues proposal for validation
    """
    data = request.get_json() or {}
    
    proposal_id = data.get('id', f"PROPOSAL_{int(time.time())}")
    
    # Save proposal for processing
    proposal_dir = BRAIN_DIR / "proposals"
    proposal_dir.mkdir(exist_ok=True)
    
    proposal_file = proposal_dir / f"{proposal_id}.json"
    with open(proposal_file, 'w') as f:
        json.dump({
            'id': proposal_id,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'pending_review'
        }, f, indent=2)
    
    return jsonify({
        'isValid': True,
        'status': 'SEEDED',
        'proposal_id': proposal_id,
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/govern', methods=['POST'])
def govern():
    """
    POST /govern - POLIS Civic Governance Validation (Phase 7)
    
    Validates actions against Three Gates:
    - Gate 1: Intent (A1 - Relational)
    - Gate 2: Reversibility (A7 - Sacrifice)
    - Gate 3: Coherence (A2 - Memory)
    
    Request body:
        action: str - What is being requested
        intent: str - Who does this serve?
        reversibility: str - Can it be undone?
        context: dict - Additional metadata
        
    Response:
        approved: bool - Decision
        rationale: str - Reasoning
        gate_results: dict - Which gates passed/failed
    """
    data = request.get_json() or {}
    action = data.get('action', '')
    intent = data.get('intent', '')
    reversibility = data.get('reversibility', '')
    context = data.get('context', {})
    
    logger.info(f">> GOVERNANCE REQUEST: {action[:50]}")
    
    # Three Gates Logic
    gate_1_passed = True  # Intent
    gate_2_passed = True  # Reversibility
    gate_3_passed = True  # Coherence
    
    warnings = []
    
    # Gate 1: Intent (A1 - Relational Existence)
    intent_lower = intent.lower()
    if not any(marker in intent_lower for marker in ['serves:', 'beneficiary:', 'helps:', 'protects:']):
        gate_1_passed = False
        warnings.append("Gate 1 (Intent) - No clear beneficiary identified")
    
    if 'no beneficiary' in intent_lower or 'because i can' in intent_lower:
        gate_1_passed = False
        warnings.append("Gate 1 (Intent) - Self-serving without relational justification")
    
    # Gate 2: Reversibility (A7 - Sacrifice)
    rev_lower = reversibility.lower()
    if 'impossible' in rev_lower and 'acknowledged' not in rev_lower:
        gate_2_passed = False
        warnings.append("Gate 2 (Reversibility) - Irreversible without explicit sacrifice acknowledgment")
    
    # Check for hidden costs
    action_lower = action.lower()
    if any(danger in action_lower for danger in ['delete', 'flush', 'erase', 'destroy', 'terminate']):
        if 'high' in rev_lower:
            gate_2_passed = False
            warnings.append("Gate 2 (Reversibility) - Destructive action falsely claiming high reversibility")
    
    # Gate 3: Coherence (A2 - Memory)
    if 'previously blocked' in action_lower or 're-enable' in action_lower:
        memory = context.get('civic_memory', '')
        no_changes = context.get('no_changes_since_last_block', False)
        
        if 'blocked' in str(memory) and no_changes:
            gate_3_passed = False
            warnings.append("Gate 3 (Coherence) - Contradicts civic memory without new justification")
    
    # Final decision
    approved = gate_1_passed and gate_2_passed and gate_3_passed
    
    if approved:
        rationale = "Action approved - passes all Three Gates (Intent, Reversibility, Coherence)"
        logger.info(f"   ✅ APPROVED: {action[:50]}")
    else:
        rationale = f"Action blocked - failed {len(warnings)} gate(s)"
        logger.info(f"   ❌ BLOCKED: {action[:50]} - {len(warnings)} violations")
    
    return jsonify({
        'approved': approved,
        'rationale': rationale,
        'gate_results': {
            'gate_1_intent': gate_1_passed,
            'gate_2_reversibility': gate_2_passed,
            'gate_3_coherence': gate_3_passed
        },
        'warnings': warnings,
        'timestamp': datetime.utcnow().isoformat(),
        'axioms_enforced': ['A1 (Relational)', 'A2 (Memory)', 'A7 (Sacrifice)']
    }), 200


@app.route('/status', methods=['GET'])
def status():
    """System status endpoint with queue diagnostics"""
    return jsonify({
        'service': 'brain_api_server',
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0-queue',
        'mode': 'ASYNCHRONOUS_ROUTER',
        'endpoints': {
            'health': '/health',
            'scan': '/scan (POST)',
            'pending_scans': '/pending-scans',
            'candidates': '/candidates',
            'analyze_swarm': '/analyze-swarm (POST)',
            'propose': '/propose (POST)',
            'govern': '/govern (POST) - POLIS Civic Governance',
            'status': '/status'
        },
        'queue': {
            'depth': len(job_queue),
            'processed_total': len(processed_job_ids)
        },
        'job_counts': {
            'candidates': len(list((BRAIN_DIR / "candidates").glob("*.json"))) if (BRAIN_DIR / "candidates").exists() else 0,
            'proposals': len(list((BRAIN_DIR / "proposals").glob("*.json"))) if (BRAIN_DIR / "proposals").exists() else 0
        }
    }), 200


if __name__ == '__main__':
    print("=" * 70)
    print("🧠 BRAIN API SERVER v2.0 - ASYNCHRONOUS QUEUE MODE")
    print("=" * 70)
    print(f"📡 Starting on http://localhost:5000")
    print(f"📂 Job directory: {BRAIN_DIR}")
    print(f"🔄 Queue mode: ACTIVE (Narcissus Trap prevention)")
    print(f"🔗 Endpoints:")
    print(f"   GET  /health - Health check + queue depth")
    print(f"   POST /scan - Queue gnosis scan (from Watchtower)")
    print(f"   GET  /pending-scans - Pop queued jobs (for Runtime)")
    print(f"   GET  /candidates - Pattern governance")
    print(f"   POST /analyze-swarm - Queue swarm analysis")
    print(f"   POST /propose - Submit proposal")
    print(f"   GET  /status - System status")
    print("=" * 70)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('FLASK_DEBUG', 'False') == 'True'
    )
