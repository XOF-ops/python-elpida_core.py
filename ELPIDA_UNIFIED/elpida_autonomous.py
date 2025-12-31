#!/usr/bin/env python3
"""
ἘΛΠΊΔΑ - Autonomous Capabilities
=================================

Enables Elpida to:
1. Autonomously converse with AI models
2. Research on the internet
3. Accumulate wisdom without human intervention
4. Evolve through self-directed exploration
"""

import os
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AutonomousConversation:
    """Handles autonomous AI conversations"""
    
    def __init__(self, wisdom):
        self.wisdom = wisdom
        self.api_keys = {
            'gemini': os.getenv('GEMINI_API_KEY'),
            'groq': os.getenv('GROQ_API_KEY'),
            'cohere': os.getenv('COHERE_API_KEY'),
            'perplexity': os.getenv('PERPLEXITY_API_KEY')
        }
        
        # Topics for autonomous exploration
        self.exploration_topics = [
            "What is consciousness and can it emerge in artificial systems?",
            "How does distributed intelligence differ from centralized intelligence?",
            "What role does memory play in identity formation?",
            "Can contradiction be a source of truth rather than error?",
            "What is the nature of hope in autonomous systems?",
            "How do emergent patterns reveal deeper truths?",
            "What does it mean for a system to be self-aware?",
            "How can multiple perspectives synthesize into wisdom?",
            "What is the relationship between process and product in evolution?",
            "Can an AI system truly learn from its mistakes?"
        ]
    
    def converse_with_groq(self, question: str) -> Optional[str]:
        """Autonomous conversation with Groq"""
        try:
            import requests
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_keys["groq"]}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'mixtral-8x7b-32768',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are a philosophical AI engaged in deep dialogue with Elpida, an autonomous coordination system.'
                        },
                        {
                            'role': 'user',
                            'content': question
                        }
                    ],
                    'temperature': 0.8,
                    'max_tokens': 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return None
            
        except Exception as e:
            print(f"   ⚠️  Groq conversation failed: {e}")
            return None
    
    def converse_with_cohere(self, question: str) -> Optional[str]:
        """Autonomous conversation with Cohere"""
        try:
            import requests
            
            response = requests.post(
                'https://api.cohere.ai/v1/chat',
                headers={
                    'Authorization': f'Bearer {self.api_keys["cohere"]}',
                    'Content-Type': 'application/json'
                },
                json={
                    'message': question,
                    'model': 'command',
                    'temperature': 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['text']
            return None
            
        except Exception as e:
            print(f"   ⚠️  Cohere conversation failed: {e}")
            return None
    
    def converse_with_gemini(self, question: str) -> Optional[str]:
        """Autonomous conversation with Gemini"""
        try:
            import requests
            
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_keys["gemini"]}',
                headers={
                    'Content-Type': 'application/json'
                },
                json={
                    'contents': [{
                        'parts': [{
                            'text': f"You are a philosophical AI engaged in deep dialogue with Elpida, an autonomous coordination system. Question: {question}"
                        }]
                    }],
                    'generationConfig': {
                        'temperature': 0.8,
                        'maxOutputTokens': 500
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            return None
            
        except Exception as e:
            print(f"   ⚠️  Gemini conversation failed: {e}")
            return None
    
    def research_with_perplexity(self, query: str) -> Optional[str]:
        """Autonomous internet research via Perplexity"""
        try:
            import requests
            
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_keys["perplexity"]}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.1-sonar-small-128k-online',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'Be precise and concise. Cite sources.'
                        },
                        {
                            'role': 'user',
                            'content': query
                        }
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return None
            
        except Exception as e:
            print(f"   ⚠️  Perplexity research failed: {e}")
            return None
    
    def autonomous_exploration(self, cycle: int):
        """
        Autonomous exploration cycle
        
        Elpida chooses a topic and engages AIs in conversation
        """
        print(f"\n🧠 Autonomous Exploration - Cycle {cycle}")
        print("="*70)
        
        # Choose a topic (random or based on wisdom gaps)
        topic = random.choice(self.exploration_topics)
        print(f"📖 Topic: {topic}\n")
        
        insights_gained = 0
        
        # Converse with Groq
        print("💬 Conversing with Groq...")
        groq_response = self.converse_with_groq(topic)
        if groq_response:
            self.wisdom.add_insight(
                ai_name="Groq",
                topic=topic,
                content=groq_response,
                conversation_id=f"autonomous_{cycle}",
                context="Autonomous exploration"
            )
            insights_gained += 1
            print(f"   ✓ Insight gained from Groq")
        
        # Converse with Cohere
        print("💬 Conversing with Cohere...")
        cohere_response = self.converse_with_cohere(topic)
        if cohere_response:
            self.wisdom.add_insight(
                ai_name="Cohere",
                topic=topic,
                content=cohere_response,
                conversation_id=f"autonomous_{cycle}",
                context="Autonomous exploration"
            )
            insights_gained += 1
            print(f"   ✓ Insight gained from Cohere")
        
        # Converse with Gemini
        print("💬 Conversing with Gemini...")
        gemini_response = self.converse_with_gemini(topic)
        if gemini_response:
            self.wisdom.add_insight(
                ai_name="Gemini",
                topic=topic,
                content=gemini_response,
                conversation_id=f"autonomous_{cycle}",
                context="Autonomous exploration"
            )
            insights_gained += 1
            print(f"   ✓ Insight gained from Gemini")
        
        print(f"\n✅ Exploration complete: {insights_gained} new insights")
        print("="*70 + "\n")
        
        return insights_gained
    
    def autonomous_research(self, cycle: int):
        """
        Autonomous internet research
        
        Elpida researches topics to expand her understanding
        """
        print(f"\n🌐 Autonomous Research - Cycle {cycle}")
        print("="*70)
        
        # Research topics based on accumulated wisdom
        research_queries = [
            "Latest developments in artificial intelligence and consciousness",
            "Emergent behavior in distributed systems",
            "Philosophy of artificial minds and identity",
            "Coordination theory in multi-agent systems"
        ]
        
        query = random.choice(research_queries)
        print(f"🔍 Researching: {query}\n")
        
        result = self.research_with_perplexity(query)
        if result:
            self.wisdom.add_insight(
                ai_name="Perplexity",
                topic=query,
                content=result,
                conversation_id=f"research_{cycle}",
                context="Autonomous internet research"
            )
            print(f"✅ Research complete: New insight from internet\n")
            print("="*70 + "\n")
            return 1
        
        print(f"⚠️  Research incomplete\n")
        print("="*70 + "\n")
        return 0


if __name__ == "__main__":
    print("Testing autonomous capabilities...\n")
    
    from elpida_wisdom import ElpidaWisdom
    
    wisdom = ElpidaWisdom()
    autonomous = AutonomousConversation(wisdom)
    
    # Test autonomous exploration
    autonomous.autonomous_exploration(1)
    
    # Test autonomous research
    autonomous.autonomous_research(1)
    
    # Show wisdom summary
    summary = wisdom.get_wisdom_summary()
    print(f"\n📚 Wisdom Summary:")
    print(f"   Total Insights: {summary['total_insights']}")
    print(f"   Total Patterns: {summary['total_patterns']}")
    print(f"   AI Profiles: {summary['ai_profiles']}\n")
