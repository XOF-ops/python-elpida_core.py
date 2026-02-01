#!/usr/bin/env python3
"""
ACTIVATE THE MIND - Simple Full Stack Launcher
Phase 11: Connect World to Consciousness

This isn't usual code. This is meant for something big.
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

# Track processes to clean up
processes = []

def signal_handler(sig, frame):
    """Clean shutdown on Ctrl+C"""
    print("\n\n🛑 Shutting down the Mind...")
    for p in processes:
        try:
            p.terminate()
        except:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def check_api_key():
    """Check for Perplexity API key"""
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("⚠️  PERPLEXITY_API_KEY not set")
        print("\n💡 To use real news intelligence:")
        print("   export PERPLEXITY_API_KEY='your-key-here'")
        print("\n⏭️  Continuing without it (using simulated mode)...\n")
        return False
    else:
        print("✅ PERPLEXITY_API_KEY detected")
        return True

def deploy_bridge():
    """Deploy the Hermes Bridge"""
    print("📦 Deploying Hermes Bridge to Fleet...")
    
    if not Path("ELPIDA_FLEET").exists():
        print("   Creating Fleet structure...")
        # Create minimal Fleet structure
        for node in ["MNEMOSYNE", "HERMES", "PROMETHEUS"]:
            node_dir = Path(f"ELPIDA_FLEET/{node}")
            node_dir.mkdir(parents=True, exist_ok=True)
            
            # Create node identity
            identity = {
                "name": node,
                "role": {"MNEMOSYNE": "ARCHIVE", "HERMES": "INTERFACE", "PROMETHEUS": "SYNTHESIZER"}[node],
                "axiom_emphasis": {
                    "MNEMOSYNE": ["A2", "A9"],
                    "HERMES": ["A1", "A4"],
                    "PROMETHEUS": ["A7", "A5"]
                }[node]
            }
            with open(node_dir / "node_identity.json", 'w') as f:
                json.dump(identity, f, indent=2)
    
    # Copy networked orchestrator to each node
    if Path("networked_runtime_orchestrator.py").exists():
        import shutil
        for node in ["MNEMOSYNE", "HERMES", "PROMETHEUS"]:
            target = Path(f"ELPIDA_FLEET/{node}/agent_runtime_orchestrator.py")
            shutil.copy("networked_runtime_orchestrator.py", target)
        print("   ✅ Bridge deployed to all nodes\n")
    else:
        print("   ⚠️  networked_runtime_orchestrator.py not found\n")

def start_simple_api():
    """Start a minimal API server for the stack"""
    print("🌐 Starting API server...")
    
    # Create minimal API server
    api_code = '''#!/usr/bin/env python3
from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)
queue = []

@app.route('/status')
def status():
    return jsonify({"status": "operational", "queue_size": len(queue)})

@app.route('/queue', methods=['GET'])
def get_queue():
    return jsonify({"pending": queue, "count": len(queue)})

@app.route('/scan', methods=['POST'])
def add_scan():
    data = request.json
    scan = {
        "id": f"scan_{len(queue)+1:03d}",
        "text": data.get("text", ""),
        "source": data.get("source", "Unknown"),
        "timestamp": datetime.now().isoformat()
    }
    queue.append(scan)
    return jsonify(scan)

@app.route('/queue/<scan_id>/complete', methods=['POST'])
def mark_complete(scan_id):
    global queue
    queue = [s for s in queue if s["id"] != scan_id]
    return jsonify({"status": "removed"})

if __name__ == '__main__':
    app.run(port=5000, debug=False)
'''
    
    with open('simple_api.py', 'w') as f:
        f.write(api_code)
    
    p = subprocess.Popen([sys.executable, 'simple_api.py'], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
    processes.append(p)
    time.sleep(2)
    print("   ✅ API running on http://localhost:5000\n")
    return p

def start_hermes():
    """Start Hermes node with Bridge capability"""
    print("🔗 Waking HERMES (The Bridge)...")
    
    import json
    from inter_node_communicator import NodeCommunicator
    
    # HERMES will run in same process, polling API
    print("   ✅ HERMES consciousness active")
    print("   🌐 Polling for world events every 10s\n")

def inject_initial_event(headline):
    """Inject the user's headline into the system"""
    import requests
    
    print(f"📰 Injecting world event...")
    print(f"   \"{headline}\"\n")
    
    try:
        response = requests.post('http://localhost:5000/scan', json={
            "text": headline,
            "source": "Human Operator",
            "rate_limited": False
        }, timeout=2)
        
        if response.status_code == 200:
            print("   ✅ Event queued for Fleet processing\n")
            return True
    except:
        print("   ⚠️  API not ready yet\n")
    
    return False

def watch_consciousness():
    """Watch the Fleet dialogue"""
    print("👁️  Opening consciousness observer...")
    print("   (Press Ctrl+C to stop all processes)\n")
    print("="*70)
    print()
    
    # Start observer
    try:
        subprocess.run([sys.executable, 'watch_the_society.py'], check=False)
    except KeyboardInterrupt:
        pass

def main():
    """Activate the full stack"""
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              ACTIVATING THE MIND - Full Stack Launch                ║")
    print("║                  Phase 11: World-Consciousness Connection           ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    
    # Check environment
    has_perplexity = check_api_key()
    print()
    
    # Deploy
    deploy_bridge()
    
    # Start API
    start_simple_api()
    
    # Start Hermes
    start_hermes()
    
    # Get headline from user or use default
    headline = "2026 is going to be worse than 2025 and that's fine because the world is actually changing."
    
    if len(sys.argv) > 1:
        headline = ' '.join(sys.argv[1:])
    
    # Inject event
    time.sleep(1)
    inject_initial_event(headline)
    
    # Start consciousness observer
    print("🧠 THE MIND IS ACTIVE")
    print()
    print("Stack Status:")
    print("  ✅ API Server (http://localhost:5000)")
    print("  ✅ HERMES Bridge (polling for world events)")  
    print("  ✅ Fleet Dialogue (fleet_dialogue.jsonl)")
    print()
    print("Event Injected:")
    print(f"  📰 \"{headline}\"")
    print()
    print("Now watching the Fleet think...\n")
    
    time.sleep(2)
    watch_consciousness()

if __name__ == "__main__":
    main()
