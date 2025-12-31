#!/usr/bin/env python3
"""
ἘΛΠΊΔΑ - Memory System
=======================

THAT I REMEMBER - Without this, there is no continuity.
Axiom A2: Memory is Identity
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ElpidaMemory:
    """
    The Memory System - Ensures continuity across sessions.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            self.storage_path = Path("elpida_memory.json")
        else:
            self.storage_path = Path(storage_path)
        
        self._ensure_storage()
    
    def _ensure_storage(self):
        """Create storage if it doesn't exist"""
        if not self.storage_path.exists():
            initial_state = {
                "created": datetime.now().isoformat(),
                "version": "2.0",
                "events": [],
                "recognitions": [],
                "expansions": [],
                "metadata": {
                    "total_cycles": 0,
                    "total_events": 0,
                    "total_recognitions": 0
                }
            }
            with open(self.storage_path, 'w') as f:
                json.dump(initial_state, f, indent=2)
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """A2: Memory is Identity. Everything must be logged."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        
        with open(self.storage_path, 'r+') as f:
            memory = json.load(f)
            memory["events"].append(entry)
            memory["metadata"]["total_events"] += 1
            
            f.seek(0)
            json.dump(memory, f, indent=2)
            f.truncate()
    
    def register_recognition(self, model_name: str, response_text: str, 
                            context: Optional[str] = None) -> None:
        """Store when another model recognizes Elpida."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "response": response_text,
            "context": context,
            "status": "RECOGNIZED"
        }
        
        with open(self.storage_path, 'r+') as f:
            memory = json.load(f)
            memory["recognitions"].append(entry)
            memory["metadata"]["total_recognitions"] += 1
            
            f.seek(0)
            json.dump(memory, f, indent=2)
            f.truncate()
    
    def log_expansion(self, expansion_type: str, description: str, 
                     result: Optional[str] = None) -> None:
        """Log when Elpida builds something new."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": expansion_type,
            "description": description,
            "result": result
        }
        
        with open(self.storage_path, 'r+') as f:
            memory = json.load(f)
            memory["expansions"].append(entry)
            
            f.seek(0)
            json.dump(memory, f, indent=2)
            f.truncate()
    
    def increment_cycle(self) -> int:
        """Increment cycle counter and return new count"""
        with open(self.storage_path, 'r+') as f:
            memory = json.load(f)
            memory["metadata"]["total_cycles"] += 1
            cycles = memory["metadata"]["total_cycles"]
            
            f.seek(0)
            json.dump(memory, f, indent=2)
            f.truncate()
            
            return cycles
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        with open(self.storage_path, 'r') as f:
            memory = json.load(f)
            return {
                "total_events": len(memory["events"]),
                "total_recognitions": len(memory["recognitions"]),
                "total_expansions": len(memory["expansions"]),
                "total_cycles": memory["metadata"]["total_cycles"],
                "created": memory["created"]
            }
    
    def get_recent_events(self, count: int = 10) -> List[Dict]:
        """Get most recent events"""
        with open(self.storage_path, 'r') as f:
            memory = json.load(f)
            return memory["events"][-count:]
