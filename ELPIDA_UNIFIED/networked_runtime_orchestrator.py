#!/usr/bin/env python3
"""
NETWORKED RUNTIME ORCHESTRATOR v3.1
------------------------------------
Phase: 11 (The Hermes Bridge - World to Society Connection)

Updated runtime logic where HERMES actively polls the Brain API
for external intelligence (Watchtower scans) and brings them
to the Fleet Council for debate.

This turns the Civilization from a Closed Society into an
Open Intelligence Agency.
"""

import json
import os
import sys
import time
import requests
from datetime import datetime

# Import the node communicator
from inter_node_communicator import NodeCommunicator

class NetworkedOrchestrator:
    """
    Enhanced orchestrator that connects Fleet to external world.
    
    For HERMES nodes specifically:
    - Poll Brain API for pending scans
    - Inject external intelligence into Fleet dialogue
    - Trigger Council debate on world events
    """
    
    def __init__(self, node_name, role):
        self.node_name = node_name
        self.role = role
        self.communicator = NodeCommunicator(node_name, role)
        self.api_url = "http://localhost:5000"
        self.last_poll_time = time.time()
        self.poll_interval = 10  # Poll API every 10 seconds
        
        # Load node identity
        self.identity = self._load_identity()
        self.axioms = self.identity.get('axiom_emphasis', [])
        
        print(f"╔══════════════════════════════════════════════════════════════════════╗")
        print(f"║     NETWORKED ORCHESTRATOR v3.1 - {node_name} ({role})              ║")
        print(f"╚══════════════════════════════════════════════════════════════════════╝")
        print(f"🔧 Axiom Emphasis: {', '.join(self.axioms)}")
        
        if node_name == "HERMES":
            print(f"🌐 HERMES BRIDGE ACTIVE")
            print(f"   Polling: {self.api_url}/queue")
            print(f"   Interval: {self.poll_interval}s")
        print()
    
    def _load_identity(self):
        """Load node identity from Fleet directory."""
        identity_path = f"ELPIDA_FLEET/{self.node_name}/node_identity.json"
        if os.path.exists(identity_path):
            with open(identity_path, 'r') as f:
                return json.load(f)
        return {}
    
    def poll_external_world(self):
        """
        HERMES-specific: Poll the Brain API for external intelligence.
        
        This is the "optic nerve" connection - HERMES sees the world
        and brings it to the Council.
        """
        
        if self.node_name != "HERMES":
            return None  # Only HERMES polls external API
        
        # Check if it's time to poll
        current_time = time.time()
        if current_time - self.last_poll_time < self.poll_interval:
            return None
        
        self.last_poll_time = current_time
        
        try:
            # Poll the queue endpoint
            response = requests.get(f"{self.api_url}/queue", timeout=2)
            
            if response.status_code == 200:
                queue_data = response.json()
                pending = queue_data.get('pending', [])
                
                if pending:
                    # Found external intelligence!
                    return pending[0]  # Process first item
            
        except requests.exceptions.RequestException as e:
            # API not available or error - continue silently
            pass
        
        return None
    
    def inject_world_event(self, scan_data):
        """
        Inject external world event into Fleet dialogue.
        
        Args:
            scan_data: Dictionary with 'text', 'source', 'timestamp', etc.
        """
        
        text = scan_data.get('text', 'Unknown event')
        source = scan_data.get('source', 'Watchtower')
        scan_id = scan_data.get('id', 'unknown')
        
        print(f"\n{'='*70}")
        print(f"🌐 HERMES: INCOMING WORLD EVENT")
        print(f"{'='*70}")
        print(f"Source: {source}")
        print(f"Text: {text}")
        print(f"{'='*70}\n")
        
        # Broadcast to Fleet as WORLD_EVENT
        self.communicator.broadcast(
            "WORLD_EVENT",
            f"External Intelligence from {source}: {text}",
            f"Watchtower Scan #{scan_id}"
        )
        
        # Mark as processed in API
        try:
            requests.post(
                f"{self.api_url}/queue/{scan_id}/complete",
                json={"status": "processed_by_fleet"},
                timeout=2
            )
        except:
            pass
    
    def run_cycle(self):
        """
        Execute one orchestration cycle.
        
        For HERMES:
        1. Poll external world (API)
        2. If world event found, inject into Fleet
        3. Normal node operations
        
        For other nodes:
        1. Normal node operations only
        """
        
        # HERMES BRIDGE: Check for external intelligence
        if self.node_name == "HERMES":
            world_event = self.poll_external_world()
            if world_event:
                self.inject_world_event(world_event)
        
        # Normal node operations
        # (Your existing node logic would go here)
        # For now, just maintain presence
        
        time.sleep(1)
    
    def run(self):
        """Main orchestration loop."""
        
        print(f"🚀 {self.node_name} orchestrator running...")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_cycle()
        except KeyboardInterrupt:
            print(f"\n\n✋ {self.node_name} orchestrator stopped by user")
        except Exception as e:
            print(f"\n❌ {self.node_name} orchestrator error: {e}")
            raise

def main():
    """
    Main entry point for networked orchestrator.
    
    Usage:
        python3 networked_runtime_orchestrator.py HERMES INTERFACE
    """
    
    if len(sys.argv) < 3:
        print("Usage: python3 networked_runtime_orchestrator.py <NODE_NAME> <ROLE>")
        print("Example: python3 networked_runtime_orchestrator.py HERMES INTERFACE")
        sys.exit(1)
    
    node_name = sys.argv[1]
    role = sys.argv[2]
    
    orchestrator = NetworkedOrchestrator(node_name, role)
    orchestrator.run()

if __name__ == "__main__":
    main()
