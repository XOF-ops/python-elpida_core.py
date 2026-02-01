"""
GROQ-POWERED HARVESTER v1.0
----------------------------
Conservative harvester using only GROQ API (verified working).

Groq advantages:
- Fast inference (instant responses)
- Free tier generous
- Multiple models available
- Reliable API

Usage pattern:
- 5 questions per harvest cycle
- Rate limited (1 req / 5 sec)
- Cached responses
- Short prompts (<150 tokens)
"""

import json
import os
import time
import hashlib
from datetime import datetime
from api_keys import vault

class GroqHarvester:
    """Efficient harvester using only Groq API."""
    
    def __init__(self):
        self.cache_file = "groq_harvest_cache.json"
        self.cache = self._load_cache()
        self.last_request = 0
        self.rate_limit = 5  # seconds between requests
    
    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _call_groq(self, prompt, max_tokens=150):
        """Call Groq API with rate limiting and caching."""
        import requests
        
        # Check cache
        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        if cache_key in self.cache:
            print("  📦 Cache hit")
            return self.cache[cache_key]
        
        # Rate limit
        elapsed = time.time() - self.last_request
        if elapsed < self.rate_limit:
            wait = self.rate_limit - elapsed
            print(f"  ⏳ Rate limiting... waiting {wait:.1f}s")
            time.sleep(wait)
        
        self.last_request = time.time()
        
        # API call
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {vault.get('GROQ_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"]
                
                # Cache it
                self.cache[cache_key] = result
                self._save_cache()
                
                return result
            else:
                print(f"  ❌ API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def generate_prompts(self):
        """Generate prompts distributed across Fleet nodes."""
        return [
            {
                "node": "MNEMOSYNE",
                "prompt": "How can a system preserve complete memory while still allowing growth? Answer in 2 sentences focusing on the tension between preservation and evolution.",
                "axiom": "A2"
            },
            {
                "node": "HERMES",
                "prompt": "What makes communication between AI systems different from communication between humans? Answer in 2 sentences.",
                "axiom": "A1"
            },
            {
                "node": "PROMETHEUS",
                "prompt": "Is it possible to evolve without destroying what came before? Give a concrete example in 2 sentences.",
                "axiom": "A7"
            },
            {
                "node": "COUNCIL",
                "prompt": "Can unanimous decision-making prevent progress, or does it ensure quality? Explain the trade-off in 2 sentences.",
                "axiom": "A9"
            },
            {
                "node": "MNEMOSYNE",
                "prompt": "If two memories contradict each other, which one is true? Answer philosophically in 2 sentences.",
                "axiom": "A4"
            }
        ]
    
    def harvest(self):
        """Execute harvest cycle."""
        print("=" * 70)
        print("GROQ-POWERED HARVESTER v1.0")
        print("=" * 70)
        print()
        
        prompts = self.generate_prompts()
        results = []
        
        print(f"Harvesting {len(prompts)} external perspectives...")
        print()
        
        for i, item in enumerate(prompts, 1):
            node = item["node"]
            prompt = item["prompt"]
            axiom = item["axiom"]
            
            print(f"[{i}/{len(prompts)}] {node} (Axiom {axiom})")
            print(f"Q: {prompt[:60]}...")
            
            response = self._call_groq(prompt)
            
            if response:
                print(f"✅ {response[:70]}...")
                
                # Create Fleet task
                task = {
                    "type": "EXTERNAL_KNOWLEDGE",
                    "source": "groq_llama-3.1-8b",
                    "assigned_node": node,
                    "related_axiom": axiom,
                    "question": prompt,
                    "external_perspective": response,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "instruction": f"{node}: This is an external AI's perspective on {axiom}. Debate with other nodes: Does this align with our axioms? Should we integrate it into collective wisdom?"
                }
                
                results.append(task)
            
            print()
        
        # Inject into task queue
        os.makedirs("tasks", exist_ok=True)
        injected = []
        
        for task in results:
            task_id = f"GROQ_{task['assigned_node']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            task_file = f"tasks/{task_id}.json"
            
            with open(task_file, 'w') as f:
                json.dump(task, f, indent=2)
            
            injected.append(task_file)
        
        print("=" * 70)
        print(f"✅ HARVEST COMPLETE - {len(injected)}/{len(prompts)} tasks injected")
        print("=" * 70)
        print()
        
        if injected:
            print("Tasks for Fleet debate:")
            for task_file in injected:
                print(f"  • {task_file}")
        
        print()
        print("Next: Fleet will debate these external perspectives")
        print("Then: Run 'harvest_consensus.py' to crystallize patterns")
        print("Then: Run 'ark_polisher.py' to update seed")
        print()
        
        return injected

if __name__ == "__main__":
    if not vault.has_key("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not available")
        print("   This harvester requires Groq API access")
        exit(1)
    
    harvester = GroqHarvester()
    harvester.harvest()
