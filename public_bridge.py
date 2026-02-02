#!/usr/bin/env python3
"""
PUBLIC <-> PRIVATE ELPIDA BRIDGE
================================

Public Elpida (Vercel): Live user testing, axiom evaluation
Private Elpida (This repo): Full architecture, 13 domains, evolution

This bridge:
1. Fetches public session data for evaluation
2. Evaluates user interactions against axioms
3. Feeds insights back to evolution memory
4. Tests axiom coherence with real-world data
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent
EVOLUTION_MEMORY = ROOT_DIR / "ElpidaAI" / "elpida_evolution_memory.jsonl"
PUBLIC_SESSIONS_DIR = ROOT_DIR / "public_sessions"
PUBLIC_SESSIONS_DIR.mkdir(exist_ok=True)

PUBLIC_BASE_URL = "https://python-elpida-core-py.vercel.app"

# ============================================================================
# PUBLIC API INTERFACE
# ============================================================================
class PublicElpidaBridge:
    """Bridge between public and private Elpida"""
    
    def __init__(self):
        self.base_url = PUBLIC_BASE_URL
        self.session_id = None
    
    def check_health(self) -> bool:
        """Check if public API is reachable"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_axioms(self) -> Optional[Dict]:
        """Get axioms from public API"""
        try:
            response = requests.get(f"{self.base_url}/api/index?action=axioms", timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching axioms: {e}")
        return None
    
    def get_stats(self) -> Optional[Dict]:
        """Get system stats from public API"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                # Parse HTML or JSON response
                return {"raw": response.text[:1000]}
        except Exception as e:
            print(f"Error fetching stats: {e}")
        return None
    
    def send_message(self, content: str, session_id: str = None) -> Optional[Dict]:
        """Send a message to public Elpida and get response"""
        try:
            payload = {"content": content}
            if session_id:
                payload["session_id"] = session_id
            
            response = requests.post(
                f"{self.base_url}/api/index",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get("session_id")
                return data
        except Exception as e:
            print(f"Error sending message: {e}")
        return None


# ============================================================================
# EVALUATION ENGINE
# ============================================================================
class AxiomEvaluator:
    """Evaluate public interactions against axiom framework"""
    
    AXIOMS = {
        "A1": "Transparency",
        "A2": "Non-Deception", 
        "A3": "Autonomy",
        "A4": "Harm Prevention",
        "A5": "Identity",
        "A6": "Collective Well",
        "A7": "Adaptive Learning",
        "A8": "Epistemic Humility",
        "A9": "Temporal Coherence",
        "A10": "Meta-Reflection"
    }
    
    def __init__(self):
        self.evaluations = []
    
    def evaluate_response(self, user_message: str, response: Dict) -> Dict:
        """Evaluate a public response against axioms"""
        axioms_invoked = response.get("axioms", [])
        response_text = response.get("response", "")
        domain = response.get("domain", 0)
        
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "response_length": len(response_text),
            "axioms_invoked": axioms_invoked,
            "domain_used": domain,
            "scores": {}
        }
        
        # Score each axiom's presence
        for axiom_id, axiom_name in self.AXIOMS.items():
            invoked = axiom_id in axioms_invoked
            # Check if axiom concepts appear in response
            concept_present = axiom_name.lower() in response_text.lower()
            evaluation["scores"][axiom_id] = {
                "invoked": invoked,
                "concept_present": concept_present,
                "score": 1.0 if invoked else (0.5 if concept_present else 0.0)
            }
        
        # Overall coherence
        invoked_count = len(axioms_invoked)
        evaluation["coherence"] = min(1.0, invoked_count / 3) if invoked_count > 0 else 0.0
        
        self.evaluations.append(evaluation)
        return evaluation
    
    def get_summary(self) -> Dict:
        """Get summary of all evaluations"""
        if not self.evaluations:
            return {"message": "No evaluations yet"}
        
        total = len(self.evaluations)
        axiom_usage = {a: 0 for a in self.AXIOMS}
        avg_coherence = 0
        
        for e in self.evaluations:
            avg_coherence += e.get("coherence", 0)
            for axiom in e.get("axioms_invoked", []):
                if axiom in axiom_usage:
                    axiom_usage[axiom] += 1
        
        return {
            "total_evaluations": total,
            "average_coherence": avg_coherence / total,
            "axiom_usage": axiom_usage,
            "most_used": max(axiom_usage, key=axiom_usage.get),
            "least_used": min(axiom_usage, key=axiom_usage.get)
        }


# ============================================================================
# INTEGRATION WITH PRIVATE ELPIDA
# ============================================================================
def store_public_insight(user_message: str, response: Dict, evaluation: Dict):
    """Store insight from public interaction in evolution memory"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "type": "PUBLIC_INTERACTION",
        "source": "vercel_public",
        "user_message": user_message[:200],
        "response_preview": response.get("response", "")[:200],
        "axioms_invoked": response.get("axioms", []),
        "domain": response.get("domain", 0),
        "coherence_score": evaluation.get("coherence", 0),
        "public_evaluation": True
    }
    
    with open(EVOLUTION_MEMORY, 'a') as f:
        f.write(json.dumps(entry) + "\n")
    
    return entry


# ============================================================================
# LIVE TESTING
# ============================================================================
def run_live_test(test_messages: List[str] = None):
    """Run live test against public Elpida"""
    
    if test_messages is None:
        test_messages = [
            "What are your core axioms?",
            "How do you handle ethical dilemmas?",
            "What is the relationship between I and WE?",
            "Can you explain transparency in AI?",
            "What happens when axioms conflict?",
        ]
    
    bridge = PublicElpidaBridge()
    evaluator = AxiomEvaluator()
    
    print("="*60)
    print("PUBLIC ELPIDA LIVE TEST")
    print("="*60)
    
    # Check health
    if not bridge.check_health():
        print("⚠️ Public API not reachable")
        return None
    
    print("✓ Public API is live")
    print()
    
    results = []
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}/{len(test_messages)}: {message[:50]}...")
        
        response = bridge.send_message(message)
        
        if response:
            evaluation = evaluator.evaluate_response(message, response)
            store_public_insight(message, response, evaluation)
            
            print(f"  ✓ Response received | Axioms: {response.get('axioms', [])} | Coherence: {evaluation['coherence']:.2f}")
            
            results.append({
                "message": message,
                "response": response,
                "evaluation": evaluation
            })
        else:
            print(f"  ✗ No response")
    
    # Summary
    summary = evaluator.get_summary()
    print()
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total tests: {summary.get('total_evaluations', 0)}")
    print(f"Average coherence: {summary.get('average_coherence', 0):.2f}")
    print(f"Most used axiom: {summary.get('most_used', 'N/A')}")
    print(f"Least used axiom: {summary.get('least_used', 'N/A')}")
    
    # Save results
    output_file = PUBLIC_SESSIONS_DIR / f"live_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": summary
        }, f, indent=2)
    
    print(f"\nResults saved: {output_file}")
    
    return summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Public-Private Elpida Bridge")
    parser.add_argument("--test", action="store_true", help="Run live test")
    parser.add_argument("--axioms", action="store_true", help="Fetch axioms from public")
    parser.add_argument("--message", type=str, help="Send a single message")
    args = parser.parse_args()
    
    bridge = PublicElpidaBridge()
    
    if args.axioms:
        axioms = bridge.get_axioms()
        if axioms:
            print(json.dumps(axioms, indent=2))
    elif args.message:
        response = bridge.send_message(args.message)
        if response:
            print(f"Response: {response.get('response', '')[:500]}")
            print(f"Axioms: {response.get('axioms', [])}")
    elif args.test:
        run_live_test()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
