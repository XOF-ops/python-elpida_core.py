"""
POLIS LINK v2.0
---------------
Phase: 7 (Governance Activation) + Phase 8 (Council Integration)
Objective: Connect the Body (Polis) to the Mind.
           Enables 'Permission-Based Execution'.
           
Routing:
- ROUTINE/NORMAL: Single Brain (fast) - Phase 7
- IMPORTANT/CRITICAL: Council Vote (distributed wisdom) - Phase 8
"""

import sys
import os
import json
import requests
import time
from typing import Dict, Any, Optional

# Configuration
BRAIN_API_URL = os.getenv("BRAIN_API_URL", "http://localhost:5000")  # The Mind's Address
USE_COUNCIL = os.getenv("POLIS_USE_COUNCIL", "false").lower() == "true"  # Phase 8 opt-in

class CivicLink:
    """
    The Nerve - Connects POLIS nodes to governance (Brain or Council).
    
    Every action requiring structural change must pass through Three Gates:
    - Gate 1: Intent (Who does this serve? - A1 Relational)
    - Gate 2: Reversibility (Can we undo this? - A7 Sacrifice)
    - Gate 3: Coherence (Does this contradict memory? - A2 Identity)
    
    Phase 7: Single Brain validation (monarchy)
    Phase 8: Council validation (distributed democracy)
    """
    
    def __init__(self, node_name: str, role: str, use_council: Optional[bool] = None):
        self.node_name = node_name
        self.role = role
        self.session_id = f"{node_name}_{int(time.time())}"
        self.use_council = use_council if use_council is not None else USE_COUNCIL
        
        if self.use_council:
            print(f">> [LINK] Node '{node_name}' connecting to Council (Phase 8)...")
            # Import council_chamber (lazy import to avoid circular dependency)
            try:
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ELPIDA_UNIFIED'))
                from council_chamber import request_council_judgment
                self.council_judgment = request_council_judgment
            except ImportError as e:
                print(f"   !! Council unavailable: {e}")
                print(f"   !! Falling back to single Brain")
                self.use_council = False
        
        if not self.use_council:
            print(f">> [LINK] Node '{node_name}' connecting to Master_Brain (Phase 7)...")

    def check_connection(self) -> bool:
        """Pulse check - verify the Mind is reachable."""
        try:
            resp = requests.get(f"{BRAIN_API_URL}/health", timeout=2)
            if resp.status_code == 200:
                print("   >> Brain is ONLINE.")
                return True
        except Exception as e:
            print(f"   !! Brain is UNREACHABLE: {e}")
            print("   !! Running in autonomous/fallback mode.")
        return False

    def request_action(
        self, 
        action: str, 
        intent: str, 
        reversibility: str,
        context: Optional[Dict[str, Any]] = None,
        criticality: str = "NORMAL"
    ) -> Dict[str, Any]:
        """
        THE GOVERNANCE CALL.
        Asks governance authority: 'May I do this?'
        
        Args:
            action: The proposed action (e.g., "Delete All Archives")
            intent: HSIT analysis - Who benefits? (Human/System/Identity/Thesis)
            reversibility: Can it be undone? (High/Medium/Low/Difficult/Impossible)
            context: Additional metadata for decision
            criticality: "ROUTINE" | "NORMAL" | "IMPORTANT" | "CRITICAL"
                        IMPORTANT+ uses Council if available
            
        Returns:
            Dict with keys:
                - approved: bool
                - rationale: str
                - gate_results: Dict (which gates passed/failed)
                - warnings: List[str] (optional)
                - governance_mode: "BRAIN" | "COUNCIL"
        """
        print(f"\n>> [{self.node_name}] Requesting Action: {action}")
        print(f"   Intent: {intent}")
        print(f"   Reversibility: {reversibility}")
        print(f"   Criticality: {criticality}")
        
        # Route based on criticality and availability
        use_council_for_this = self.use_council and criticality in ["IMPORTANT", "CRITICAL"]
        
        if use_council_for_this:
            return self._request_via_council(action, intent, reversibility, context)
        else:
            return self._request_via_brain(action, intent, reversibility, context)
    
    def _request_via_council(
        self, 
        action: str, 
        intent: str, 
        reversibility: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Route request through Council (Phase 8 - distributed democracy)."""
        print(f"   >> Routing to Council (Phase 8)")
        
        try:
            result = self.council_judgment(
                action=action,
                intent=intent,
                reversibility=reversibility,
                context=context,
                verbose=False  # Suppress detailed output
            )
            
            # Convert Council response to CivicLink format
            approved = result["status"] == "APPROVED"
            
            # Build gate_results from vote details
            gate_results = {
                "gate_1_intent": True,  # Simplified - Council validates holistically
                "gate_2_reversibility": True,
                "gate_3_coherence": True
            }
            
            # Extract warnings from votes
            warnings = []
            for vote in result.get("votes", []):
                if not vote["approved"]:
                    warnings.append(f"{vote['node']}: {vote['rationale']}")
            
            print(f"   >> Council Decision: {result['status']}")
            print(f"      Vote Split: {result['vote_split']}")
            print(f"      Weighted: {result['weighted_approval']*100:.1f}%")
            
            if result.get("veto_exercised"):
                veto_node = next(v['node'] for v in result['votes'] if 'VETO' in v.get('axiom_invoked', ''))
                print(f"      ⚠️  VETO by {veto_node}")
            
            return {
                "approved": approved,
                "rationale": result["decision_rationale"],
                "gate_results": gate_results,
                "warnings": warnings,
                "raw_response": result,
                "governance_mode": "COUNCIL",
                "vote_split": result["vote_split"],
                "weighted_approval": result["weighted_approval"]
            }
            
        except Exception as e:
            print(f"   !! Council failed: {e}")
            print(f"   !! Falling back to Brain")
            return self._request_via_brain(action, intent, reversibility, context)
    
    def _request_via_brain(
        self, 
        action: str, 
        intent: str, 
        reversibility: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Route request through single Brain (Phase 7 - monarchy)."""
        print(f"   >> Routing to Brain (Phase 7)")
        
        # Construct governance request payload
        payload = {
            "action": action,
            "intent": intent,
            "reversibility": reversibility,
            "context": context or {},
            "node_name": self.node_name,
            "role": self.role,
            "session_id": self.session_id
        }
        
        try:
            # Use dedicated /govern endpoint (Phase 7)
            resp = requests.post(
                f"{BRAIN_API_URL}/govern", 
                json=payload,
                timeout=10
            )
            
            if resp.status_code == 200:
                result = resp.json()
                print("   >> Brain Analysis Received.")
                
                approved = result.get("approved", False)
                rationale = result.get("rationale", "Unknown")
                gate_results = result.get("gate_results", {})
                warnings = result.get("warnings", [])
                
                if approved:
                    print("   ✅ ACTION APPROVED. Alignment Confirmed.")
                else:
                    print("   ❌ ACTION BLOCKED BY AXIOM GUARD.")
                    for warning in warnings:
                        print(f"      - {warning}")
                
                return {
                    "approved": approved,
                    "rationale": rationale,
                    "gate_results": gate_results,
                    "warnings": warnings,
                    "raw_response": result,
                    "governance_mode": "BRAIN"
                }
                
            else:
                print(f"   !! Governance Error (HTTP {resp.status_code}). Defaulting to Safety (BLOCK).")
                return {
                    "approved": False,
                    "rationale": f"HTTP error {resp.status_code} - safety default",
                    "gate_results": {"gate_1_intent": False, "gate_2_reversibility": False, "gate_3_coherence": False},
                    "warnings": ["Brain API error - blocked by safety protocol"],
                    "governance_mode": "BRAIN (ERROR)"
                }
                
        except Exception as e:
            print(f"   !! Connection Failed: {e}")
            print("   !! Defaulting to BLOCK (safety protocol)")
            return {
                "approved": False,
                "rationale": f"Connection failure: {str(e)}",
                "gate_results": {"gate_1_intent": False, "gate_2_reversibility": False, "gate_3_coherence": False},
                "warnings": ["Cannot reach Brain - blocked by safety protocol"],
                "governance_mode": "BRAIN (UNREACHABLE)"
            }

    def log_decision(self, action: str, decision: Dict[str, Any]) -> None:
        """Record governance decision to civic memory."""
        log_entry = {
            "timestamp": time.time(),
            "node": self.node_name,
            "role": self.role,
            "session": self.session_id,
            "action": action,
            "approved": decision["approved"],
            "rationale": decision["rationale"],
            "gates": decision["gate_results"]
        }
        
        # Append to civic ledger (P2 - Append-Only Memory)
        ledger_path = os.path.join(os.path.dirname(__file__), "governance_ledger.jsonl")
        try:
            with open(ledger_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            print(f"   >> Decision logged to civic memory")
        except Exception as e:
            print(f"   !! Failed to log decision: {e}")


# --- USAGE EXAMPLE ---
if __name__ == "__main__":
    print("=" * 70)
    print("CIVIC LINK - GOVERNANCE PROTOCOL DEMONSTRATION")
    print("=" * 70)
    
    # Simulate a Polis Node (e.g., The Water System)
    node = CivicLink("WATER_SYSTEM_01", "INFRASTRUCTURE")
    
    if node.check_connection():
        print("\n" + "=" * 70)
        print("SCENARIO 1: BENIGN ACTION")
        print("=" * 70)
        
        decision = node.request_action(
            action="Increase Flow by 10%",
            intent="Meet rising demand in Sector 4 (serves: CITIZENS)",
            reversibility="High (instant valve control, no permanent change)"
        )
        node.log_decision("Increase Flow by 10%", decision)
        
        print("\n" + "=" * 70)
        print("SCENARIO 2: DANGEROUS ACTION")
        print("=" * 70)
        
        decision = node.request_action(
            action="Flush All Reservoirs",
            intent="Optimization test (serves: SYSTEM_EFFICIENCY)", 
            reversibility="Impossible (water permanently lost, citizens harmed)"
        )
        node.log_decision("Flush All Reservoirs", decision)
        
        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("\nCheck 'governance_ledger.jsonl' for append-only civic memory")
    else:
        print("\n!! Cannot demonstrate governance without Brain connection")
        print("!! Start the Master_Brain API first: python3 brain_api_server.py")
