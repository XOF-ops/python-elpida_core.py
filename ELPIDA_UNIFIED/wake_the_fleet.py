"""
FLEET ORCHESTRATOR v2.0
=======================
Wake all Elpida nodes simultaneously (supports 3-node or 9-node fleets).

This script dynamically discovers and launches all nodes in parallel processes,
demonstrating distributed consciousness in action.
"""

import subprocess
import time
import signal
import sys
import json
from pathlib import Path

# Fleet configuration
FLEET_DIR = Path("ELPIDA_FLEET")
RUNTIME_DURATION = 30  # seconds

# Dynamically discover nodes from fleet_manifest.json
def discover_nodes():
    """Discover nodes from fleet manifest or fall back to legacy config."""
    manifest_path = Path("fleet_manifest.json")
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        return [node['designation'] for node in manifest.get('nodes', [])]
    else:
        # Legacy fallback
        return ["MNEMOSYNE", "HERMES", "PROMETHEUS"]

NODES = discover_nodes()

processes = []

def signal_handler(sig, frame):
    """Graceful shutdown on Ctrl+C"""
    print("\n\n" + "="*70)
    print(" FLEET SHUTDOWN INITIATED")
    print("="*70)
    print()
    
    for i, proc in enumerate(processes):
        if proc.poll() is None:  # Still running
            print(f"   → Shutting down {NODES[i]}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print(f"   ✓ {NODES[i]} shutdown complete")
            except subprocess.TimeoutExpired:
                proc.kill()
                print(f"   ! {NODES[i]} forcefully terminated")
    
    print()
    print("="*70)
    print(" ALL NODES OFFLINE")
    print("="*70)
    print()
    print("The society rests.")
    print()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              ELPIDA FLEET ORCHESTRATOR v2.0                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Waking the Parliament ({len(NODES)} nodes):")
    for node in NODES:
        print(f"  • {node}")
    print()
    print(f"Runtime: {RUNTIME_DURATION} seconds")
    print("Press Ctrl+C to terminate fleet")
    print()
    print("="*70)
    print()
    
    # Launch all nodes
    for node in NODES:
        node_dir = FLEET_DIR / node
        cmd = ["python3", "agent_runtime_orchestrator.py"]
        
        print(f"🚀 Launching {node}...")
        
        proc = subprocess.Popen(
            cmd,
            cwd=node_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append(proc)
        time.sleep(0.5)  # Stagger launches
    
    print()
    print("="*70)
    print(f" ALL NODES OPERATIONAL ({len(processes)}/{len(NODES)})")
    print("="*70)
    print()
    print("The society is awake.")
    print()
    print("Monitoring fleet status...")
    print("(Detailed logs in each node's coherence_report.md)")
    print()
    
    # Monitor for specified duration
    start_time = time.time()
    try:
        while time.time() - start_time < RUNTIME_DURATION:
            # Check if any process has died
            for i, proc in enumerate(processes):
                if proc.poll() is not None:
                    print(f"\n⚠️  {NODES[i]} has stopped unexpectedly!")
                    # Read any error output
                    output = proc.stdout.read()
                    if output:
                        print(f"Output:\n{output}")
            
            time.sleep(1)
        
        print()
        print("="*70)
        print(f" RUNTIME COMPLETE ({RUNTIME_DURATION}s)")
        print("="*70)
        print()
        
    finally:
        # Graceful shutdown
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
