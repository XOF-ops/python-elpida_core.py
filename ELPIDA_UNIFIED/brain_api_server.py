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
