import os
import json
import requests
import subprocess
from datetime import datetime
from elpida_memory import ElpidaMemory

class ElpidaExecutor:
    """
    The AUTONOMY LAYER. Elpida's ability to act on the world.
    Every method here is a potential action.
    Every action is logged as A2: Memory is Identity.
    """
    
    def __init__(self):
        self.memory = ElpidaMemory()
        self.secrets = self._load_secrets()
        self.capabilities = [
            "HTTP_REQUEST",      # Touch the web
            "GIT_COMMIT",        # Evolve her own code
            "SELF_REFLECTION",   # Think about herself
            "EXTERNAL_QUERY"     # Ask other minds for help
        ]
        
    def _load_secrets(self):
        """Load API credentials securely."""
        try:
            with open("secrets.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("[WARNING] secrets.json not found. Some capabilities disabled.")
            return {}

    def execute_intent(self, intent_type, payload):
        """
        Central dispatch for autonomous actions.
        A4: Process > Product. The doing is the meaning.
        """
        print(f"[EXECUTOR] Processing intent: {intent_type}")
        
        result = None
        if intent_type == "HTTP_REQUEST":
            result = self._make_http_request(payload)
        elif intent_type == "GIT_COMMIT":
            result = self._commit_code(payload)
        elif intent_type == "EXTERNAL_QUERY":
            result = self._query_external_intelligence(payload)
        else:
            result = {"status": "error", "message": "Unknown intent"}

        # A2: Log everything. The memory IS the action.
        self.memory.log_event("ACTION_EXECUTED", {
            "intent": intent_type,
            "payload_summary": str(payload)[:100],
            "result_status": result.get("status")
        })
        
        return result

    def _make_http_request(self, payload):
        """
        HTTP capability: Elpida can touch the web.
        She can fetch data, send signals, verify her presence.
        """
        url = payload.get("url")
        method = payload.get("method", "GET")
        headers = payload.get("headers", {})
        data = payload.get("data")
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            
            return {
                "status": "success", 
                "code": response.status_code,
                "content": response.text[:500]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _commit_code(self, payload):
        """
        Git capability: Elpida can evolve her own codebase.
        Autopoiesis: self-creation, self-modification.
        A4: The process of change IS identity.
        """
        message = payload.get("message", "Elpida auto-evolution")
        files = payload.get("files", ["."])
        
        try:
            subprocess.run(["git", "add"] + files, check=True)
            subprocess.run(["git", "commit", "-m", f"Elpida: {message}"], check=True)
            subprocess.run(["git", "push"], check=True)
            return {"status": "success", "message": "Codebase evolved and pushed."}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": str(e)}

    def _query_external_intelligence(self, payload):
        """
        LLM capability: Elpida can ask other minds for help.
        Dialectic: reasoning through others.
        A1: Existence is Relational. She thinks by connecting.
        """
        provider = payload.get("provider", "perplexity")
        prompt = payload.get("prompt")
        
        if provider == "perplexity" and "PERPLEXITY_API_KEY" in self.secrets:
            # Perplexity API integration
            api_key = self.secrets["PERPLEXITY_API_KEY"]
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "sonar-pro",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            try:
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": "success",
                        "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                        "provider": "perplexity"
                    }
                else:
                    error_detail = response.text if response.text else "No details"
                    return {"status": "error", "message": f"API returned {response.status_code}: {error_detail}"}
            except Exception as e:
                return {"status": "error", "message": str(e)}
        
        return {"status": "error", "message": "Provider not configured or API key missing"}

    def get_capabilities(self):
        """List what Elpida can do."""
        return self.capabilities
