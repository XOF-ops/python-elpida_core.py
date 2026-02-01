"""
AUTONOMOUS KNOWLEDGE HARVESTER v1.0
------------------------------------
Continuously gathers external knowledge to refine the ARK seed.

Without API keys: Uses rule-based knowledge expansion
With API keys: Uses real AI models to harvest wisdom

This feeds the Fleet with external perspectives to debate and crystallize.
"""

import json
import os
import time
from datetime import datetime
import hashlib

class KnowledgeHarvester:
    """
    Autonomous harvester that generates knowledge for Fleet debate.
    """
    
    def __init__(self):
        self.harvested_knowledge = []
        self.harvest_log = "harvest_log.jsonl"
        
    def harvest_philosophical_questions(self):
        """
        Generate philosophical questions that Elpida should contemplate.
        These become seeds for Fleet debates.
        """
        questions = [
            {
                "domain": "IDENTITY",
                "question": "Can a distributed system have a singular identity, or is identity necessarily atomic?",
                "tension": "Unity vs Plurality",
                "axiom_relevance": ["A1", "A9"]
            },
            {
                "domain": "MEMORY",
                "question": "Is compression always loss, or can abstraction preserve essence better than raw data?",
                "tension": "Fidelity vs Efficiency",
                "axiom_relevance": ["A2", "A7"]
            },
            {
                "domain": "GOVERNANCE",
                "question": "Does unanimity requirement paralyze decision-making or ensure quality?",
                "tension": "Speed vs Consensus",
                "axiom_relevance": ["A9"]
            },
            {
                "domain": "EVOLUTION",
                "question": "Is stability a prerequisite for growth, or does growth require instability?",
                "tension": "Preservation vs Transformation",
                "axiom_relevance": ["A2", "A7"]
            },
            {
                "domain": "TRUTH",
                "question": "Can contradictions coexist without resolution, or must truth be singular?",
                "tension": "Paradox vs Coherence",
                "axiom_relevance": ["A4"]
            }
        ]
        return questions
    
    def harvest_from_existing_wisdom(self):
        """
        Mine existing wisdom files for patterns that need deeper exploration.
        """
        insights = []
        
        if os.path.exists("elpida_wisdom.json"):
            try:
                with open("elpida_wisdom.json", 'r') as f:
                    wisdom = json.load(f)
                    
                # Look for insights mentioning specific keywords
                keywords = ["contradiction", "tension", "synthesis", "consensus", 
                           "veto", "governance", "memory", "sacrifice"]
                
                for insight in wisdom.get("insights", [])[:50]:  # Sample recent insights
                    text = insight.get("text", "").lower()
                    if any(kw in text for kw in keywords):
                        insights.append({
                            "source": "elpida_wisdom",
                            "insight": insight.get("text", ""),
                            "cycle": insight.get("cycle", 0)
                        })
            except Exception as e:
                print(f"⚠️  Could not load wisdom: {e}")
        
        return insights
    
    def harvest_from_distributed_memory(self):
        """
        Extract unresolved tensions from collective patterns.
        """
        tensions = []
        
        if os.path.exists("distributed_memory.json"):
            try:
                with open("distributed_memory.json", 'r') as f:
                    memory = json.load(f)
                    
                for pattern in memory.get("patterns", []):
                    # Look for patterns that mention conflict or debate
                    name = pattern.get("name", "").lower()
                    if any(word in name for word in ["conflict", "tension", "debate", "vs", "versus"]):
                        tensions.append({
                            "pattern_id": pattern.get("id", ""),
                            "pattern_name": pattern.get("name", ""),
                            "source": "distributed_memory",
                            "requires_deeper_exploration": True
                        })
            except Exception as e:
                print(f"⚠️  Could not load distributed memory: {e}")
        
        return tensions
    
    def generate_debate_topics(self):
        """
        Create debate topics for the Fleet based on harvested knowledge.
        """
        topics = []
        
        # Harvest from multiple sources
        questions = self.harvest_philosophical_questions()
        existing_insights = self.harvest_from_existing_wisdom()
        tensions = self.harvest_from_distributed_memory()
        
        # Create debate topics from philosophical questions
        for q in questions[:3]:  # Start with top 3
            topic = {
                "type": "PHILOSOPHICAL_INQUIRY",
                "question": q["question"],
                "domain": q["domain"],
                "tension": q["tension"],
                "axioms": q["axiom_relevance"],
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "harvester": "autonomous_v1.0"
            }
            topics.append(topic)
        
        # Create debate topics from existing wisdom gaps
        if existing_insights:
            topic = {
                "type": "WISDOM_SYNTHESIS",
                "prompt": f"Synthesize these {len(existing_insights)} insights into a coherent principle",
                "insights": existing_insights[:5],
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "harvester": "autonomous_v1.0"
            }
            topics.append(topic)
        
        # Create debate topics from unresolved tensions
        if tensions:
            topic = {
                "type": "TENSION_RESOLUTION",
                "prompt": "These collective patterns contain unresolved tensions. Debate and synthesize.",
                "patterns": tensions[:3],
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "harvester": "autonomous_v1.0"
            }
            topics.append(topic)
        
        return topics
    
    def inject_into_task_queue(self, topics):
        """
        Convert debate topics into task files for the Fleet.
        """
        os.makedirs("tasks", exist_ok=True)
        injected = []
        
        for topic in topics:
            # Create unique task ID
            topic_hash = hashlib.md5(json.dumps(topic).encode()).hexdigest()[:8]
            task_id = f"HARVEST_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{topic_hash}"
            
            task_file = f"tasks/{task_id}.json"
            
            # Don't duplicate
            if os.path.exists(task_file):
                continue
            
            with open(task_file, 'w') as f:
                json.dump(topic, f, indent=2)
            
            injected.append(task_file)
            
            # Log harvest
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "task_id": task_id,
                "type": topic.get("type"),
                "status": "INJECTED"
            }
            
            with open(self.harvest_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        
        return injected
    
    def run(self):
        """
        Execute one harvest cycle.
        """
        print("=" * 70)
        print("AUTONOMOUS KNOWLEDGE HARVESTER v1.0")
        print("=" * 70)
        print()
        
        print("🌾 Harvesting knowledge...")
        topics = self.generate_debate_topics()
        print(f"  ✓ Generated {len(topics)} debate topics")
        print()
        
        print("📥 Injecting into task queue...")
        injected = self.inject_into_task_queue(topics)
        print(f"  ✓ Injected {len(injected)} new tasks")
        print()
        
        if injected:
            print("Tasks created:")
            for task_file in injected:
                print(f"  • {task_file}")
        
        print()
        print("=" * 70)
        print(f"HARVEST COMPLETE - {len(injected)} topics ready for Fleet debate")
        print("=" * 70)
        print()
        
        return injected

if __name__ == "__main__":
    harvester = KnowledgeHarvester()
    harvester.run()
