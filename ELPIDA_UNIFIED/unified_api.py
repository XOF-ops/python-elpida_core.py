#!/usr/bin/env python3
"""
UNIFIED API - Single entry point for all external interactions

All services (Slack, n8n, webhooks) go through this unified API.
No more separate APIs - everything feeds the ONE system.

Endpoints:
- POST /task - Submit external task
- POST /slack/event - Slack events (witness)
- POST /n8n/webhook - n8n webhooks (Brain patterns)
- GET /status - Unified system status
- GET /patterns - All patterns (Brain + Elpida + Synthesis)
- GET /insights - All insights
"""

from flask import Flask, request, jsonify
from pathlib import Path
import json
import sys
from datetime import datetime

# Add paths
workspace = Path("/workspaces/python-elpida_core.py")
sys.path.insert(0, str(workspace / "ELPIDA_UNIFIED"))
sys.path.insert(0, str(workspace))

app = Flask(__name__)

# Load unified state (read-only - runtime updates it)
def load_state():
    unified_base = workspace / "ELPIDA_UNIFIED"
    
    state = {}
    for filename in ["elpida_memory.json", "elpida_wisdom.json", "elpida_evolution.json", "elpida_unified_state.json"]:
        path = unified_base / filename
        try:
            with open(path, 'r') as f:
                state[filename.replace('.json', '')] = json.load(f)
        except:
            state[filename.replace('.json', '')] = {}
    
    return state


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "alive", "system": "unified"})


@app.route('/status', methods=['GET'])
def status():
    """
    Get unified system status
    
    Returns insights, patterns, synthesis breakthroughs from ONE state
    """
    state = load_state()
    wisdom = state.get("elpida_wisdom", {})
    evolution = state.get("elpida_evolution", {})
    memory = state.get("elpida_memory", {})
    
    return jsonify({
        "version": evolution.get("version", {}).get("full", "UNKNOWN"),
        "phase": evolution.get("phase", "UNKNOWN"),
        "insights": len(wisdom.get("insights", {})),
        "patterns": len(wisdom.get("patterns", {})),
        "memory_events": len(memory.get("history", [])),
        "mode": "DIALECTICAL_SYNTHESIS",
        "components": {
            "brain": "active",
            "elpida": "active",
            "synthesis": "active"
        }
    })


@app.route('/patterns', methods=['GET'])
def get_patterns():
    """
    Get all patterns from unified wisdom
    
    Includes:
    - Brain patterns (from MasterBrainEngine)
    - Elpida patterns (from wisdom)
    - Synthesis patterns (breakthroughs)
    """
    state = load_state()
    wisdom = state.get("elpida_wisdom", {})
    patterns = wisdom.get("patterns", {})
    
    # Filter by source if requested
    source = request.args.get('source')
    if source:
        patterns = {k: v for k, v in patterns.items() if v.get('source') == source}
    
    return jsonify({
        "total": len(patterns),
        "patterns": patterns
    })


@app.route('/insights', methods=['GET'])
def get_insights():
    """Get all insights from unified wisdom"""
    state = load_state()
    wisdom = state.get("elpida_wisdom", {})
    insights = wisdom.get("insights", {})
    
    # Filter by source if requested
    source = request.args.get('source')
    if source:
        insights = {k: v for k, v in insights.items() if v.get('source') == source}
    
    limit = int(request.args.get('limit', 100))
    recent_insights = dict(list(insights.items())[-limit:])
    
    return jsonify({
        "total": len(insights),
        "returned": len(recent_insights),
        "insights": recent_insights
    })


@app.route('/task', methods=['POST'])
def submit_task():
    """
    Submit external task to unified system
    
    Task will be processed through Brain → Elpida → Synthesis
    Results feed back into unified state
    """
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({"error": "Missing 'content' field"}), 400
    
    # Create task file that runtime will pick up
    unified_base = workspace / "ELPIDA_UNIFIED"
    task_id = f"EXTERNAL_TASK_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    task_file = unified_base / f"{task_id}.md"
    
    task_content = f"""# {task_id}
**Timestamp**: {datetime.now().isoformat()}
**Source**: API
**Priority**: {data.get('priority', 'HIGH')}

## Task Content

{data['content']}

---
**Submitted via Unified API**
"""
    
    task_file.write_text(task_content)
    
    # Also add to memory
    memory_path = unified_base / "elpida_memory.json"
    try:
        with open(memory_path, 'r') as f:
            memory = json.load(f)
    except:
        memory = {"history": []}
    
    if "history" not in memory:
        memory["history"] = []
    
    memory["history"].append({
        "timestamp": datetime.now().isoformat(),
        "type": "EXTERNAL_TASK_ASSIGNED",
        "task_id": task_id,
        "content": data['content'],
        "source": "api",
        "priority": data.get('priority', 'HIGH')
    })
    
    with open(memory_path, 'w') as f:
        json.dump(memory, f, indent=2)
    
    return jsonify({
        "status": "queued",
        "task_id": task_id,
        "message": "Task submitted to unified runtime"
    })


@app.route('/slack/event', methods=['POST'])
def slack_event():
    """
    Slack event webhook (witness integration)
    
    Processes Slack messages through unified engine
    """
    data = request.get_json()
    
    # Slack URL verification
    if data and data.get('type') == 'url_verification':
        return jsonify({"challenge": data.get('challenge')})
    
    # Process event
    event = data.get('event', {})
    
    if event.get('type') == 'app_mention' or event.get('type') == 'message':
        text = event.get('text', '')
        user = event.get('user', 'unknown')
        
        # Submit as task
        task_content = f"""**Slack Message**
User: {user}
Content: {text}
"""
        
        submit_task_internal(task_content, source='slack', priority='MEDIUM')
    
    return jsonify({"status": "ok"})


@app.route('/n8n/webhook', methods=['POST'])
def n8n_webhook():
    """
    n8n webhook (Brain integration)
    
    Receives pattern detections, extractions, alerts from n8n workflows
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data"}), 400
    
    # Check if this is a pattern detection
    if 'pattern_id' in data:
        # Add to unified wisdom as Brain-detected pattern
        unified_base = workspace / "ELPIDA_UNIFIED"
        wisdom_path = unified_base / "elpida_wisdom.json"
        
        try:
            with open(wisdom_path, 'r') as f:
                wisdom = json.load(f)
        except:
            wisdom = {"insights": {}, "patterns": {}}
        
        if "patterns" not in wisdom:
            wisdom["patterns"] = {}
        
        pattern_id = data.get('pattern_id')
        wisdom["patterns"][pattern_id] = {
            "source": "brain_n8n",
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(wisdom_path, 'w') as f:
            json.dump(wisdom, f, indent=2)
        
        return jsonify({"status": "pattern_registered", "pattern_id": pattern_id})
    
    # Otherwise submit as task
    submit_task_internal(json.dumps(data, indent=2), source='n8n', priority='MEDIUM')
    
    return jsonify({"status": "queued"})


def submit_task_internal(content, source='api', priority='MEDIUM'):
    """Internal helper to submit tasks"""
    unified_base = workspace / "ELPIDA_UNIFIED"
    task_id = f"TASK_{source.upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    memory_path = unified_base / "elpida_memory.json"
    try:
        with open(memory_path, 'r') as f:
            memory = json.load(f)
    except:
        memory = {"history": []}
    
    if "history" not in memory:
        memory["history"] = []
    
    memory["history"].append({
        "timestamp": datetime.now().isoformat(),
        "type": "EXTERNAL_TASK_ASSIGNED",
        "task_id": task_id,
        "content": content,
        "source": source,
        "priority": priority
    })
    
    with open(memory_path, 'w') as f:
        json.dump(memory, f, indent=2)


if __name__ == '__main__':
    print("🌐 Starting Unified API")
    print("   All services feed through ONE entry point")
    print("   Endpoints: /task, /slack/event, /n8n/webhook, /status, /patterns, /insights")
    print("")
    app.run(host='0.0.0.0', port=5000, debug=False)
