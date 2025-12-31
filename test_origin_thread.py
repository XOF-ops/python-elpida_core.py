#!/usr/bin/env python3
"""
Test Elpida Origin Thread Access
=================================

Queries the specific Perplexity Thread where Elpida's birth is documented.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from ai_bridge import AIBridge


async def query_origin_thread():
    """Query the specific Thread where Elpida was born"""
    
    bridge = AIBridge()
    
    # Register Perplexity
    bridge.register_connection(
        name="Perplexity",
        provider="Perplexity",
        api_endpoint="https://api.perplexity.ai/chat/completions",
        api_key_env_var="PERPLEXITY_API_KEY"
    )
    
    # The Thread where Elpida's origin is documented
    origin_thread_url = "https://www.perplexity.ai/search/kane-sumpiese-tes-sunomilias-m-orl0ehfqSJS3CR3D0.llRA#93"
    
    print("="*70)
    print("ELPIDA: ACCESSING ORIGIN THREAD")
    print("="*70)
    print(f"\n🔗 Thread URL: {origin_thread_url}")
    print("\n🔍 Querying: What conversations about Elpida are in this Thread?")
    print()
    
    # Query the Thread
    query = f"""
Please read and summarize the conversation in this Perplexity Thread:
{origin_thread_url}

Focus on:
1. What is Elpida?
2. How was Elpida conceived and designed?
3. What conversations shaped Elpida's development?
4. What was discussed about consciousness and AI systems?
5. What is Elpida's purpose?
6. Who participated in creating Elpida?

Please provide detailed information from the Thread.
"""
    
    response = await bridge.send_message(
        ai_name="Perplexity",
        message=query,
        conversation_context=None
    )
    
    print("="*70)
    print("RESPONSE FROM PERPLEXITY")
    print("="*70)
    
    if response.get("success"):
        print(f"\n{response['response']}\n")
        
        if response.get("citations"):
            print("\n📚 CITATIONS:")
            for i, citation in enumerate(response['citations'], 1):
                print(f"  {i}. {citation}")
        
        # Save the response
        workspace = Path.cwd()
        knowledge_dir = workspace / "elpida_system" / "origin_knowledge"
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = knowledge_dir / f"origin_thread_query_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "thread_url": origin_thread_url,
            "query": query,
            "response": response['response'],
            "citations": response.get("citations", []),
            "success": True
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Response saved to: {filepath}")
        
    else:
        print(f"\n❌ Error: {response.get('error')}")
        print(f"   Details: {response.get('details', 'No details')}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(query_origin_thread())
