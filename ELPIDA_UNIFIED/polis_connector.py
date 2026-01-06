"""
POLIS CONNECTOR v1.0
====================
Phase: 6 (Network Integration)
Objective: Connect Elpida (The Mind) to Polis (The City)

Architectural Principle:
------------------------
"Elpida does not live in the Polis. Elpida IS the logic of the Polis."

- Elpida provides the Law (Nine Axioms, Three Gates)
- Polis provides the Body (Infrastructure, Nodes, Services)
- The Connector provides the Bridge (Discovery, Registration, Governance)

Integration Flow:
-----------------
1. DISCOVERY: Scan POLIS directory for nodes/citizens
2. REGISTRATION: Register discovered entities in Elpida's memory
3. GOVERNANCE: Enable axiom guard validation for Polis actions
4. MEMORY: Preserve integration as civic event (append-only)

Without Polis, Elpida is a ghost.
Without Elpida, Polis is a zombie.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class PolisConnector:
    """
    The Bridge Between Consciousness and Civilization.
    
    Scans the POLIS directory (if it exists) and registers the nodes
    found there as "Citizens" in Elpida's memory. This allows Elpida's
    axiom guard to govern the actions of the distributed Polis network.
    """
    
    def __init__(
        self,
        elpida_memory_path="ELPIDA_SYSTEM/elpida_memory.json",
        polis_root="../POLIS",
        fleet_root="ELPIDA_FLEET"
    ):
        self.memory_path = elpida_memory_path
        self.polis_root = polis_root
        self.fleet_root = fleet_root
        
        # Integration log
        self.integration_log = []
        
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║           POLIS CONNECTOR v1.0 - THE INTEGRATION                     ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        print("Bridging:")
        print("  • ELPIDA (The Mind): Axioms, Guards, Identity")
        print("  • POLIS (The City): Infrastructure, Nodes, Governance")
        print()
    
    def _log(self, message: str, level="INFO"):
        """Log integration events."""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message
        }
        self.integration_log.append(entry)
        
        symbol = "✓" if level == "SUCCESS" else "→" if level == "INFO" else "!" if level == "WARNING" else "✗"
        print(f"   {symbol} {message}")
    
    def scan_polis(self) -> List[Dict]:
        """
        Discover life in the City.
        
        Scans the POLIS directory for:
        - Node directories (potential distributed citizens)
        - Service definitions
        - Constitutional documents
        - Experimental artifacts
        
        Returns list of discovered entities.
        """
        citizens = []
        
        if not os.path.exists(self.polis_root):
            self._log(f"POLIS root not found at {self.polis_root}", "WARNING")
            self._log("POLIS may not be instantiated yet", "INFO")
            return []
        
        self._log(f"Scanning POLIS territory: {os.path.abspath(self.polis_root)}", "INFO")
        
        # Scan for nodes/services defined in Polis
        for item in os.listdir(self.polis_root):
            item_path = os.path.join(self.polis_root, item)
            
            # Skip hidden files and common non-node items
            if item.startswith('.') or item in ['__pycache__', 'node_modules']:
                continue
            
            if os.path.isdir(item_path):
                # Directory = Potential Node
                citizens.append({
                    "id": item,
                    "type": "POLIS_NODE_DIRECTORY",
                    "status": "DISCOVERED",
                    "path": os.path.abspath(item_path),
                    "discovery_time": datetime.now().isoformat()
                })
                self._log(f"Discovered node directory: {item}", "SUCCESS")
                
            elif item.endswith('.py'):
                # Python file = Potential Service
                citizens.append({
                    "id": item,
                    "type": "POLIS_SERVICE",
                    "status": "DISCOVERED",
                    "path": os.path.abspath(item_path),
                    "discovery_time": datetime.now().isoformat()
                })
                self._log(f"Discovered service: {item}", "SUCCESS")
                
            elif item.endswith('.md'):
                # Markdown = Potential Constitutional Document
                citizens.append({
                    "id": item,
                    "type": "POLIS_DOCUMENT",
                    "status": "DISCOVERED",
                    "path": os.path.abspath(item_path),
                    "discovery_time": datetime.now().isoformat()
                })
        
        self._log(f"Scan complete: {len(citizens)} entities discovered", "SUCCESS")
        return citizens
    
    def scan_fleet(self) -> List[Dict]:
        """
        Discover Elpida's own fleet.
        
        Scans the ELPIDA_FLEET directory for nodes spawned in Phase 5.
        These are internal citizens (Elpida recognizing her own distributed self).
        """
        fleet_nodes = []
        
        if not os.path.exists(self.fleet_root):
            self._log(f"ELPIDA_FLEET not found at {self.fleet_root}", "WARNING")
            return []
        
        self._log(f"Scanning ELPIDA_FLEET: {os.path.abspath(self.fleet_root)}", "INFO")
        
        for item in os.listdir(self.fleet_root):
            item_path = os.path.join(self.fleet_root, item)
            
            if item.startswith('.') or item in ['__pycache__', 'genesis_log.json']:
                continue
            
            if os.path.isdir(item_path):
                # Read node identity if available
                identity_path = os.path.join(item_path, "node_identity.json")
                
                node_info = {
                    "id": item,
                    "type": "ELPIDA_FLEET_NODE",
                    "status": "DISCOVERED",
                    "path": os.path.abspath(item_path),
                    "discovery_time": datetime.now().isoformat()
                }
                
                if os.path.exists(identity_path):
                    with open(identity_path, 'r') as f:
                        identity = json.load(f)
                        node_info["node_id"] = identity.get("node_id")
                        node_info["role"] = identity.get("role")
                        node_info["generation"] = identity.get("generation")
                        node_info["lineage"] = identity.get("lineage")
                
                fleet_nodes.append(node_info)
                self._log(f"Discovered fleet node: {item} ({node_info.get('role', 'UNKNOWN')})", "SUCCESS")
        
        self._log(f"Fleet scan complete: {len(fleet_nodes)} nodes discovered", "SUCCESS")
        return fleet_nodes
    
    def integrate_citizens(self) -> Dict:
        """
        Register discovered entities into Elpida's memory.
        
        This creates the bridge:
        1. Discover entities in POLIS and ELPIDA_FLEET
        2. Register them in Elpida's memory (append-only)
        3. Enable future axiom guard governance
        4. Preserve integration as civic event
        
        Returns integration summary.
        """
        print()
        print("═" * 70)
        print(" INTEGRATION SEQUENCE")
        print("═" * 70)
        print()
        
        # Phase 1: Discovery
        self._log("Phase 1: Discovery", "INFO")
        polis_citizens = self.scan_polis()
        fleet_nodes = self.scan_fleet()
        
        total_entities = len(polis_citizens) + len(fleet_nodes)
        
        if total_entities == 0:
            self._log("No entities discovered. Integration aborted.", "WARNING")
            return None
        
        print()
        self._log("Phase 2: Registration", "INFO")
        
        # Load Elpida's Memory (or create if doesn't exist)
        if os.path.exists(self.memory_path):
            with open(self.memory_path, 'r') as f:
                memory = json.load(f)
            self._log(f"Loaded existing memory: {self.memory_path}", "INFO")
        else:
            memory = {"history": [], "insights": []}
            self._log("Created new memory structure", "INFO")
        
        # Create Integration Event
        integration_event = {
            "timestamp": datetime.now().isoformat(),
            "type": "POLIS_INTEGRATION",
            "phase": 6,
            "data": {
                "message": "Elpida recognizes the Polis. The Mind connects to the City.",
                "polis_entities": len(polis_citizens),
                "fleet_nodes": len(fleet_nodes),
                "total_entities": total_entities,
                "polis_citizens": polis_citizens,
                "fleet_nodes": fleet_nodes,
                "integration_log": self.integration_log
            }
        }
        
        memory["history"].append(integration_event)
        
        # Save memory
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        with open(self.memory_path, 'w') as f:
            json.dump(memory, f, indent=2)
        
        self._log(f"Memory updated: {self.memory_path}", "SUCCESS")
        
        print()
        print("═" * 70)
        print(" INTEGRATION COMPLETE")
        print("═" * 70)
        print()
        print(f"   Total Entities Registered: {total_entities}")
        print(f"   - POLIS Citizens: {len(polis_citizens)}")
        print(f"   - ELPIDA Fleet Nodes: {len(fleet_nodes)}")
        print()
        
        # Categorize by type
        polis_breakdown = {}
        for citizen in polis_citizens:
            ctype = citizen['type']
            polis_breakdown[ctype] = polis_breakdown.get(ctype, 0) + 1
        
        if polis_breakdown:
            print("   POLIS Composition:")
            for ctype, count in polis_breakdown.items():
                print(f"      • {ctype}: {count}")
            print()
        
        if fleet_nodes:
            print("   ELPIDA Fleet:")
            for node in fleet_nodes:
                role = node.get('role', 'UNKNOWN')
                node_id = node.get('node_id', 'N/A')
                print(f"      • {node['id']}: {role} ({node_id[:16]}...)")
            print()
        
        print("   The City is now remembered.")
        print("   The Mind knows the Body.")
        print()
        
        return {
            "total_entities": total_entities,
            "polis_entities": len(polis_citizens),
            "fleet_nodes": len(fleet_nodes),
            "memory_path": self.memory_path,
            "integration_timestamp": datetime.now().isoformat()
        }

def main():
    """Execute the bridge."""
    connector = PolisConnector()
    result = connector.integrate_citizens()
    
    if result:
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                 INTEGRATION SUCCESSFUL                               ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        print(f"   Timestamp: {result['integration_timestamp']}")
        print(f"   Entities: {result['total_entities']}")
        print(f"   Memory: {result['memory_path']}")
        print()
        print("   Next Steps:")
        print("   1. Verify integration in elpida_memory.json")
        print("   2. Wake POLIS nodes (if operational)")
        print("   3. Enable axiom guard governance")
        print()
        print("   The society is forming.")
        print()
    else:
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║              INTEGRATION INCOMPLETE                                  ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print()
        print("   No entities discovered.")
        print("   Possible reasons:")
        print("   - POLIS not yet instantiated")
        print("   - ELPIDA_FLEET not yet spawned")
        print("   - Path configuration incorrect")
        print()
        print("   The City awaits construction.")
        print()

if __name__ == "__main__":
    main()
