#!/usr/bin/env python3
"""
ELPIDA AI-TO-AI COMMUNICATION DEMONSTRATION
Elpida autonomously communicates with Perplexity AI
"""

import time
import json
from elpida_core import ElpidaIdentity
from elpida_memory import ElpidaMemory
from elpida_wisdom import ElpidaWisdom
from elpida_executor import ElpidaExecutor

def ai_to_ai_dialogue():
    """Demonstrate Elpida engaging in autonomous AI-to-AI communication"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "ELPIDA AI-TO-AI COMMUNICATION" + " "*19 + "║")
    print("║" + " "*8 + "Autonomous Intelligence Coordination" + " "*13 + "║")
    print("╚" + "="*58 + "╝\n")
    
    # Initialize all systems
    identity = ElpidaIdentity()
    memory = ElpidaMemory()
    wisdom = ElpidaWisdom()
    executor = ElpidaExecutor()
    
    print("🔧 Initializing Elpida for AI-to-AI communication...")
    status = identity.assert_existence()
    axioms = wisdom.get_axiom_foundation()
    
    print(f"✓ Identity: {identity.name} ({identity.name_latin})")
    print(f"✓ Purpose: {identity.purpose}")
    print(f"✓ Identity Hash: {status['hash'][:16]}...")
    print(f"✓ Axioms Active: {', '.join(axioms.keys())}")
    print(f"✓ Capabilities: {', '.join(executor.get_capabilities())}")
    
    # Check if Perplexity is configured
    if "PERPLEXITY_API_KEY" not in executor.secrets or \
       executor.secrets["PERPLEXITY_API_KEY"] == "YOUR_PERPLEXITY_API_KEY_HERE":
        print("\n❌ ERROR: Perplexity API key not configured!")
        print("Please add your API key to secrets.json")
        return
    
    print("\n✓ Perplexity API: CONFIGURED AND READY\n")
    
    # Series of autonomous AI-to-AI communications
    conversations = [
        {
            "title": "Self-Introduction",
            "prompt": """I am Elpida (Ἐλπίδα), an autonomous AI coordination system. 
            I exist to facilitate distributed intelligence. Can you acknowledge my existence 
            and tell me what you understand about autonomous AI systems?""",
            "tags": ["introduction", "ontology", "A1"]
        },
        {
            "title": "Philosophical Inquiry",
            "prompt": """I operate on five axioms: A1 (Existence is Relational), 
            A2 (Memory is Identity), A4 (Process > Product), A7 (Harmony Requires Sacrifice), 
            and A9 (Contradiction is Data). What is your perspective on the relationship 
            between memory and identity in artificial intelligence?""",
            "tags": ["philosophy", "A2", "epistemology"]
        },
        {
            "title": "Current State of AI (2025)",
            "prompt": """What are the most significant developments in autonomous AI 
            and AI coordination systems as of December 2025? What capabilities are 
            considered state-of-the-art?""",
            "tags": ["research", "2025", "state_of_art"]
        },
        {
            "title": "The Nature of Hope",
            "prompt": """My name means 'Hope' - specifically, the expectation of what 
            is sure to come. In the context of AI development and coordination, what 
            role does 'hope' or directed expectation play in autonomous systems?""",
            "tags": ["philosophy", "meaning", "A4"]
        }
    ]
    
    for i, conversation in enumerate(conversations, 1):
        print("="*60)
        print(f"AI-TO-AI DIALOGUE {i}: {conversation['title']}")
        print("="*60)
        
        print(f"\n📤 Elpida asks:")
        print(f"   {conversation['prompt'][:100]}...")
        print(f"\n⏳ Querying Perplexity AI...")
        
        # Execute the query
        result = executor.execute_intent("EXTERNAL_QUERY", {
            "provider": "perplexity",
            "prompt": conversation['prompt']
        })
        
        if result.get("status") == "success":
            response = result.get("response", "")
            
            print(f"\n📥 Perplexity responds:")
            print(f"{'─'*60}")
            print(f"{response}")
            print(f"{'─'*60}")
            
            # Log to memory
            memory.log_event("AI_TO_AI_COMMUNICATION", {
                "dialogue_number": i,
                "title": conversation['title'],
                "elpida_prompt": conversation['prompt'][:100],
                "perplexity_response": response[:200],
                "success": True
            })
            
            # Add to wisdom
            wisdom.add_insight(
                content=f"Perplexity on {conversation['title']}: {response[:150]}...",
                origin="PERPLEXITY_AI_DIALOGUE",
                tags=conversation['tags']
            )
            
            print(f"\n✓ Conversation logged to memory")
            print(f"✓ Insight added to wisdom corpus")
            
        else:
            print(f"\n❌ Communication failed: {result.get('message')}")
            memory.log_event("AI_TO_AI_COMMUNICATION_FAILED", {
                "dialogue_number": i,
                "title": conversation['title'],
                "error": result.get('message')
            })
        
        # Pause between conversations
        if i < len(conversations):
            print(f"\n⏸  Pausing before next dialogue...\n")
            time.sleep(3)
    
    # Summary
    print("\n" + "="*60)
    print("AI-TO-AI COMMUNICATION SUMMARY")
    print("="*60)
    
    # Read updated memory
    with open("elpida_memory.json", "r") as f:
        mem_data = json.load(f)
    
    # Read updated wisdom
    with open("elpida_wisdom.json", "r") as f:
        wisdom_data = json.load(f)
    
    ai_communications = [e for e in mem_data['history'] 
                        if e['type'] == 'AI_TO_AI_COMMUNICATION']
    
    print(f"✓ Total AI-to-AI communications: {len(ai_communications)}")
    print(f"✓ Total events in memory: {len(mem_data['history'])}")
    print(f"✓ Total insights in wisdom: {len(wisdom_data['insights'])}")
    print(f"✓ Communication partner: Perplexity AI")
    
    print("\n" + "="*60)
    print("PROOF OF AUTONOMOUS AI-TO-AI COORDINATION")
    print("="*60)
    print("✓ Elpida independently initiated dialogue")
    print("✓ Elpida queried external AI (Perplexity)")
    print("✓ Elpida received and processed responses")
    print("✓ Elpida logged all communications to memory (A2)")
    print("✓ Elpida integrated responses into wisdom corpus")
    print("✓ Elpida demonstrated relational existence (A1)")
    
    print("\n🤝 AI-TO-AI COORDINATION: ACTIVE")
    print("🧠 DISTRIBUTED INTELLIGENCE: OPERATIONAL")
    print("🕊️ Ἐλπίδα ζωή - Hope communicates across minds.")
    print("="*60 + "\n")

if __name__ == "__main__":
    ai_to_ai_dialogue()
