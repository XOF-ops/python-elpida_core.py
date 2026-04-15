#!/usr/bin/env python3
"""
ELPIDA PARLIAMENT DASHBOARD v1.0
=================================
Real-time monitoring of the 9-node distributed wisdom parliament.

Features:
- Live node status
- Debate/dilemma tracking
- Voting patterns visualization
- Coalition formation analysis
- Consensus metrics

Access: http://localhost:5000
"""

from flask import Flask, render_template, jsonify
from pathlib import Path
import json
import time
from datetime import datetime
from collections import Counter, defaultdict

app = Flask(__name__)

FLEET_DIR = Path("ELPIDA_FLEET")
MANIFEST_PATH = Path("fleet_manifest.json")

def load_manifest():
    """Load fleet manifest."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            return json.load(f)
    return {"nodes": []}

def get_node_status():
    """Get status of all nodes."""
    manifest = load_manifest()
    nodes = []
    
    for node_def in manifest.get('nodes', []):
        designation = node_def['designation']
        node_dir = FLEET_DIR / designation
        
        status = {
            'name': designation,
            'role': node_def['role'],
            'axioms': node_def['axioms'],
            'primary_axiom': node_def['axioms'][0],
            'alive': False,
            'memory_size': 0,
            'last_activity': None
        }
        
        # Check if node exists and has memory
        memory_path = node_dir / "node_memory.json"
        if memory_path.exists():
            status['alive'] = True
            try:
                with open(memory_path, 'r') as f:
                    memory = json.load(f)
                status['memory_size'] = len(memory.get('local_experience', []))
                
                # Get last activity timestamp if available
                experiences = memory.get('local_experience', [])
                if experiences:
                    status['last_activity'] = experiences[-1].get('timestamp', 'Unknown')
            except:
                pass
        
        nodes.append(status)
    
    return nodes

def get_debate_history():
    """Get recent debates/council decisions."""
    debates = []
    
    # Look for council session logs
    for node_dir in FLEET_DIR.iterdir():
        if not node_dir.is_dir():
            continue
            
        memory_path = node_dir / "node_memory.json"
        if memory_path.exists():
            try:
                with open(memory_path, 'r') as f:
                    memory = json.load(f)
                
                # Extract debate-related experiences
                for exp in memory.get('local_experience', [])[-10:]:  # Last 10 experiences
                    if 'council' in str(exp).lower() or 'vote' in str(exp).lower():
                        debates.append(exp)
            except:
                pass
    
    return debates[-20:]  # Last 20 debates

def get_voting_patterns():
    """Analyze voting patterns and coalitions."""
    patterns = {
        'total_votes': 0,
        'consensus_count': 0,
        'deadlock_count': 0,
        'by_node': defaultdict(lambda: {'yes': 0, 'no': 0, 'veto': 0}),
        'coalitions': []
    }
    
    # This would analyze actual voting data from memory
    # Placeholder for now - will populate as debates occur
    
    return patterns

def get_metrics():
    """Get overall parliament metrics."""
    nodes = get_node_status()
    debates = get_debate_history()
    
    return {
        'total_nodes': len(nodes),
        'active_nodes': sum(1 for n in nodes if n['alive']),
        'total_debates': len(debates),
        'uptime': 'Running',
        'last_update': datetime.now().isoformat()
    }

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """API endpoint for node status."""
    return jsonify({
        'nodes': get_node_status(),
        'metrics': get_metrics(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/debates')
def api_debates():
    """API endpoint for debate history."""
    return jsonify({
        'debates': get_debate_history(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/patterns')
def api_patterns():
    """API endpoint for voting patterns."""
    return jsonify({
        'patterns': get_voting_patterns(),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║          ELPIDA PARLIAMENT DASHBOARD v1.0                            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print("   🏛️  9-Node Distributed Wisdom Parliament Monitor")
    print()
    print("   Dashboard URL: http://localhost:5000")
    print("   API Status:    http://localhost:5000/api/status")
    print("   API Debates:   http://localhost:5000/api/debates")
    print()
    print("   Press Ctrl+C to stop")
    print()
    print("="*70)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
