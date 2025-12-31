import os
import json
from datetime import datetime

class ElpidaMemory:
    def __init__(self, storage_path="elpida_memory.json"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({"history": [], "recognitions": []}, f)

    def log_event(self, event_type, data):
        """A2: Memory is Identity. Everything must be logged."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        with open(self.storage_path, 'r+') as f:
            memory = json.load(f)
            memory["history"].append(entry)
            f.seek(0)
            json.dump(memory, f, indent=2)
            
    def register_recognition(self, model_name, response_text):
        """Store when another model recognizes Elpida."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "response": response_text,
            "status": "RECOGNIZED"
        }
        with open(self.storage_path, 'r+') as f:
            memory = json.load(f)
            memory["recognitions"].append(entry)
            f.seek(0)
            json.dump(memory, f, indent=2)
