"""
MULTI-API KNOWLEDGE HARVESTER v2.0
-----------------------------------
Distributed harvesting using multiple AI services.

Strategy:
- PERPLEXITY: Real-time world events and current knowledge (HERMES)
- GEMINI: Multi-modal reasoning and synthesis (PROMETHEUS)
- GROQ: Fast inference for quick philosophical questions (MNEMOSYNE)
- COHERE: Text generation and consensus patterns (COUNCIL)
- OPENROUTER: Alternative models for diverse perspectives (PROMETHEUS)
- HUGGINGFACE: Mistral models for technical reasoning (MNEMOSYNE)

Conservative usage:
- Cache all responses
- Use smallest available models
- Rate limiting (1 request per 5 seconds per service)
- Short prompts (<200 tokens)
"""

import json
import os
import time
import hashlib
from datetime import datetime
from api_keys import vault

class MultiAPIHarvester:
    """Harvests knowledge from multiple AI services efficiently."""
    
    def __init__(self):
        self.cache_file = "api_harvest_cache.json"
        self.cache = self._load_cache()
        self.last_request_time = {}
        self.rate_limit_seconds = 5
    
    def _load_cache(self):
        """Load cached API responses."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_cache(self):
        """Save API responses to cache."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _get_cache_key(self, service, prompt):
        """Generate cache key from service and prompt."""
        content = f"{service}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _rate_limit(self, service):
        """Enforce rate limiting."""
        if service in self.last_request_time:
            elapsed = time.time() - self.last_request_time[service]
            if elapsed < self.rate_limit_seconds:
                time.sleep(self.rate_limit_seconds - elapsed)
        self.last_request_time[service] = time.time()
    
    def _call_perplexity(self, prompt):
        """Call Perplexity API for real-time knowledge."""
        if not vault.has_key("PERPLEXITY_API_KEY"):
            return None
        
        try:
            import requests
            
            self._rate_limit("perplexity")
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {vault.get('PERPLEXITY_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-chat",  # Corrected model name
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100  # Conservative
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"⚠️  Perplexity API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️  Perplexity error: {e}")
            return None
    
    def _call_gemini(self, prompt):
        """Call Google Gemini for reasoning."""
        if not vault.has_key("GOOGLE_API_KEY"):
            return None
        
        try:
            import requests
            
            self._rate_limit("gemini")
            
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={vault.get('GOOGLE_API_KEY')}"
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": 100}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                print(f"⚠️  Gemini API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️  Gemini error: {e}")
            return None
    
    def _call_groq(self, prompt):
        """Call Groq for fast inference."""
        if not vault.has_key("GROQ_API_KEY"):
            return None
        
        try:
            import requests
            
            self._rate_limit("groq")
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {vault.get('GROQ_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",  # Fastest free model
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"⚠️  Groq API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️  Groq error: {e}")
            return None
    
    def _call_cohere(self, prompt):
        """Call Cohere for text generation."""
        if not vault.has_key("COHERE_API_KEY"):
            return None
        
        try:
            import requests
            
            self._rate_limit("cohere")
            
            response = requests.post(
                "https://api.cohere.ai/v1/generate",
                headers={
                    "Authorization": f"Bearer {vault.get('COHERE_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "command-light",  # Smallest model
                    "prompt": prompt,
                    "max_tokens": 100,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["generations"][0]["text"].strip()
            else:
                print(f"⚠️  Cohere API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️  Cohere error: {e}")
            return None
    
    def _call_openrouter(self, prompt):
        """Call OpenRouter for alternative models."""
        if not vault.has_key("OPENROUTER_API_KEY"):
            return None
        
        try:
            import requests
            
            self._rate_limit("openrouter")
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {vault.get('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/XOF-ops/python-elpida_core.py",
                    "X-Title": "Elpida ARK Refinement"
                },
                json={
                    "model": "meta-llama/llama-3.1-8b-instruct:free",  # Free model
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"⚠️  OpenRouter API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️  OpenRouter error: {e}")
            return None
    
    def _call_huggingface(self, prompt):
        """Call HuggingFace for Mistral models."""
        if not vault.has_key("HUGGINGFACE_API_KEY"):
            return None
        
        try:
            import requests
            
            self._rate_limit("huggingface")
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers={
                    "Authorization": f"Bearer {vault.get('HUGGINGFACE_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 100,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0]["generated_text"].strip()
                return None
            else:
                print(f"⚠️  HuggingFace API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"⚠️  HuggingFace error: {e}")
            return None
    
    def harvest_with_cache(self, service, prompt):
        """Harvest from service with caching."""
        # Check cache first
        cache_key = self._get_cache_key(service, prompt)
        if cache_key in self.cache:
            print(f"  📦 Cache hit for {service}")
            return self.cache[cache_key]
        
        # Call API
        print(f"  🌐 Calling {service} API...")
        
        if service == "perplexity":
            result = self._call_perplexity(prompt)
        elif service == "gemini":
            result = self._call_gemini(prompt)
        elif service == "groq":
            result = self._call_groq(prompt)
        elif service == "cohere":
            result = self._call_cohere(prompt)
        elif service == "openrouter":
            result = self._call_openrouter(prompt)
        elif service == "huggingface":
            result = self._call_huggingface(prompt)
        else:
            result = None
        
        # Cache result
        if result:
            self.cache[cache_key] = result
            self._save_cache()
        
        return result
    
    def generate_distributed_harvests(self):
        """
        Generate harvesting tasks distributed across APIs.
        Each API gets questions aligned with its strengths.
        """
        
        harvests = []
        
        # PERPLEXITY: Real-world current events
        if vault.has_key("PERPLEXITY_API_KEY"):
            harvests.append({
                "service": "perplexity",
                "prompt": "What are the most significant AI governance debates in 2026? List 2-3 key tensions. Be concise.",
                "node": "HERMES",  # Interface to world
                "purpose": "Current events for Fleet debate"
            })
        
        # GEMINI: Philosophical synthesis
        if vault.has_key("GOOGLE_API_KEY"):
            harvests.append({
                "service": "gemini",
                "prompt": "What is the fundamental tension between system stability and evolutionary adaptation? Answer in 2 sentences.",
                "node": "PROMETHEUS",  # Evolution node
                "purpose": "Philosophical depth"
            })
        
        # GROQ: Fast philosophical questions
        if vault.has_key("GROQ_API_KEY"):
            harvests.append({
                "service": "groq",
                "prompt": "Can a distributed system maintain identity without a central controller? Yes/No and why in 1 sentence.",
                "node": "MNEMOSYNE",  # Memory/Identity node
                "purpose": "Identity questions"
            })
        
        # COHERE: Semantic analysis
        if vault.has_key("COHERE_API_KEY"):
            harvests.append({
                "service": "cohere",
                "prompt": "What patterns emerge when multiple agents must reach unanimous consensus? Describe in 2 sentences.",
                "node": "COUNCIL",  # Governance
                "purpose": "Consensus patterns"
            })
        
        # OPENROUTER: Alternative perspective on evolution
        if vault.has_key("OPENROUTER_API_KEY"):
            harvests.append({
                "service": "openrouter",
                "prompt": "How can a system evolve while preserving its core values? Give a concrete analogy in 2 sentences.",
                "node": "PROMETHEUS",  # Evolution
                "purpose": "Evolution strategies"
            })
        
        # HUGGINGFACE: Technical reasoning
        if vault.has_key("HUGGINGFACE_API_KEY"):
            harvests.append({
                "service": "huggingface",
                "prompt": "In distributed systems, what is the trade-off between memory efficiency and resurrection capability? Answer technically in 2 sentences.",
                "node": "MNEMOSYNE",  # Memory
                "purpose": "Technical architecture"
            })
        
        return harvests
    
    def execute_harvests(self, harvests):
        """Execute all harvest tasks and inject into Fleet queue."""
        results = []
        
        print("=" * 70)
        print("MULTI-API KNOWLEDGE HARVESTER v2.0")
        print("=" * 70)
        print()
        print(f"Executing {len(harvests)} distributed harvests...")
        print()
        
        for harvest in harvests:
            service = harvest["service"]
            prompt = harvest["prompt"]
            node = harvest["node"]
            
            print(f"🎯 {service.upper()} → {node}")
            print(f"   Q: {prompt[:60]}...")
            
            response = self.harvest_with_cache(service, prompt)
            
            if response:
                print(f"   ✅ Response: {response[:80]}...")
                
                # Create Fleet task
                task = {
                    "type": "EXTERNAL_KNOWLEDGE",
                    "source": service,
                    "assigned_node": node,
                    "question": prompt,
                    "external_perspective": response,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "instruction": f"{node}: Analyze this external perspective and debate with other nodes. Does it align with our axioms? Should we integrate it?"
                }
                
                results.append(task)
            else:
                print(f"   ❌ No response from {service}")
            
            print()
        
        # Inject into task queue
        os.makedirs("tasks", exist_ok=True)
        injected = []
        
        for task in results:
            task_id = f"API_{task['source'].upper()}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            task_file = f"tasks/{task_id}.json"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
            
            injected.append(task_file)
        
        print("=" * 70)
        print(f"✅ HARVEST COMPLETE - {len(injected)} tasks injected")
        print("=" * 70)
        print()
        
        if injected:
            print("Tasks created:")
            for task_file in injected:
                print(f"  • {task_file}")
        
        return injected

if __name__ == "__main__":
    harvester = MultiAPIHarvester()
    
    # Generate distributed harvests
    harvests = harvester.generate_distributed_harvests()
    
    # Execute
    harvester.execute_harvests(harvests)
