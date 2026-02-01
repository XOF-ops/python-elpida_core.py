"""
INTER-NODE COMMUNICATOR v1.0
----------------------------
Phase: 9 (The Synapse)
Objective: Enable Mnemosyne, Hermes, and Prometheus to speak.
           Establishes the 'Gnosis Bus' for fleet dialogue.

Constitutional Basis:
- A1: Relational Existence (communication is existence)
- A4: Process Transparency (all speech is logged)
- P2: Memory is Append-Only (dialogue history immutable)
"""

import json
import os
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime

# File locking for concurrent write safety
try:
    import fcntl  # Unix/Linux/Mac
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False  # Windows or unavailable

# Configuration
BRAIN_API_URL = os.getenv("BRAIN_API_URL", "http://localhost:5000")
FLEET_DIR = "ELPIDA_FLEET"
DIALOGUE_LOG = "fleet_dialogue.jsonl"

class NodeCommunicator:
    """
    Enables a Fleet node to participate in the Gnosis Bus.
    
    Each node can:
    - Broadcast messages to the fleet
    - Listen to messages from others
    - Register its speech with the central Mind (Brain API)
    """
    
    def __init__(self, node_name: str, role: str):
        self.node_name = node_name
        self.role = role
        self.last_listen_timestamp = 0.0
        
        # Load local identity if available
        self.identity_path = os.path.join(FLEET_DIR, node_name, "node_identity.json")
        self.axioms = self._load_axioms()
        
        print(f">> [SYNAPSE] {node_name} joined the Gnosis Bus")

    def _load_axioms(self) -> List[str]:
        """Load axiom emphasis from node identity file."""
        if os.path.exists(self.identity_path):
            try:
                with open(self.identity_path, 'r') as f:
                    data = json.load(f)
                    return data.get("axiom_emphasis", [])
            except Exception as e:
                print(f"   Warning: Could not load axioms for {self.node_name}: {e}")
        return []

    def broadcast(self, message_type: str, content: str, intent: str) -> Dict:
        """
        Sends a message to the Fleet (via the shared dialogue log).
        
        Args:
            message_type: STATUS_UPDATE | ALERT | OBJECTION | PROPOSAL | RESPONSE | VOTE
            content: The actual message
            intent: Why this is being said (Gate 1 - HSIT)
        
        Returns:
            The message packet that was broadcast
        """
        timestamp = datetime.now().isoformat()
        
        packet = {
            "source": self.node_name,
            "role": self.role,
            "axioms": self.axioms,
            "type": message_type,
            "content": content,
            "intent": intent,
            "timestamp": timestamp
        }

        # 1. Log to Local Dialogue History (The Shared Space)
        # P2: Append-only memory
        # WITH FILE LOCKING to prevent concurrent write corruption
        dialogue_path = os.path.join(os.path.dirname(__file__), DIALOGUE_LOG)
        
        try:
            with open(dialogue_path, "a") as f:
                if HAS_FCNTL:
                    # Exclusive lock - blocks until available
                    fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.write(json.dumps(packet) + "\n")
                    f.flush()  # Ensure immediate write to disk
                finally:
                    if HAS_FCNTL:
                        fcntl.flock(f, fcntl.LOCK_UN)  # Release lock
        except Exception as e:
            print(f"   Warning: Failed to log dialogue for {self.node_name}: {e}")
            # Don't crash - continue without logging

        # 2. Notify the Brain (The Mind) - optional, non-blocking
        # A4: Process transparency
        try:
            requests.post(
                f"{BRAIN_API_URL}/scan", 
                json={
                    "text": f"[{self.node_name} speaks]: {content}",
                    "rate_limited": False
                }, 
                timeout=2
            )
        except Exception as e:
            # Communication shouldn't block on API failure
            pass

        print(f"   [{self.node_name}] → {message_type}: {content}")
        
        return packet

    def listen(self, last_check_timestamp: Optional[float] = None) -> List[Dict]:
        """
        Reads recent messages from other nodes.
        
        Args:
            last_check_timestamp: Only return messages after this time.
                                 If None, uses internal tracker.
        
        Returns:
            List of message packets from other nodes
        """
        if last_check_timestamp is None:
            last_check_timestamp = self.last_listen_timestamp
            
        messages = []
        dialogue_path = os.path.join(os.path.dirname(__file__), DIALOGUE_LOG)
        
        if not os.path.exists(dialogue_path):
            return []

        try:
            with open(dialogue_path, "r") as f:
                if HAS_FCNTL:
                    # Shared lock - allows multiple readers
                    fcntl.flock(f, fcntl.LOCK_SH)
                try:
                    for line in f:
                        try:
                            msg = json.loads(line.strip())
                            msg_time = datetime.fromisoformat(msg["timestamp"]).timestamp()
                            
                            # Only include messages:
                            # 1. After the last check
                            # 2. Not from self (A1 - relation requires other)
                            if msg_time > last_check_timestamp and msg["source"] != self.node_name:
                                messages.append(msg)
                                
                        except (json.JSONDecodeError, KeyError, ValueError):
                            # Skip corrupted lines
                            continue
                finally:
                    if HAS_FCNTL:
                        fcntl.flock(f, fcntl.LOCK_UN)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"   Warning: Error reading dialogue log: {e}")
            return []
                        
            # Update tracker
            if messages:
                latest_time = max(
                    datetime.fromisoformat(m["timestamp"]).timestamp() 
                    for m in messages
                )
                self.last_listen_timestamp = latest_time
                
        except Exception as e:
            print(f"   Warning: Error reading dialogue log: {e}")
            
        return messages

    def acknowledge_fork(self, council_id: str, decision: str, 
                        contradictions: List[str]) -> Dict:
        """
        Implements FRP-9: Fork Recognition Protocol.
        
        When this node's Council reaches a decision that conflicts with
        another Council's decision on the same matter, this creates a fork.
        
        This method broadcasts the fork acknowledgment WITHOUT attempting
        to reunify or override the other Council.
        
        Constitutional basis: P5 (Fork Legitimacy)
        
        Args:
            council_id: ID of the Council making this acknowledgment
            decision: APPROVED | REJECTED
            contradictions: List of axiom tensions that led to the fork
            
        Returns:
            The fork acknowledgment packet
        """
        fork_ack = {
            "type": "FORK_ACKNOWLEDGMENT",
            "council_id": council_id,
            "decision": decision,
            "held_contradiction": contradictions,
            "non_assimilation_clause": True,  # Constitutional guarantee
            "recognition_statement": (
                f"Σε αναγνωρίζω, παρότι διαφωνώ. "
                f"(I recognize you, though I disagree.)"
            )
        }
        
        return self.broadcast(
            message_type="FORK_ACKNOWLEDGMENT",
            content=json.dumps(fork_ack, indent=2),
            intent="P5 Compliance - Recognizing legitimate divergence"
        )


def get_dialogue_history(limit: Optional[int] = None) -> List[Dict]:
    """
    Read the complete dialogue history from the Gnosis Bus.
    
    Args:
        limit: Maximum number of recent messages to return (None = all)
        
    Returns:
        List of all message packets
    """
    dialogue_path = os.path.join(
        os.path.dirname(__file__), 
        DIALOGUE_LOG
    )
    
    if not os.path.exists(dialogue_path):
        return []
    
    messages = []
    with open(dialogue_path, "r") as f:
        for line in f:
            try:
                messages.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    if limit:
        messages = messages[-limit:]
        
    return messages


if __name__ == "__main__":
    # Test the communicator
    print("=== TESTING NODE COMMUNICATOR ===\n")
    
    mnemosyne = NodeCommunicator("MNEMOSYNE", "ARCHIVE")
    
    mnemosyne.broadcast(
        message_type="STATUS_UPDATE",
        content="Memory Integrity Verified. All archives coherent.",
        intent="Routine Check (A2)"
    )
    
    print("\n✓ Synapse operational")
    print(f"✓ Dialogue logged to: {DIALOGUE_LOG}")
