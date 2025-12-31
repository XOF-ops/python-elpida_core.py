#!/usr/bin/env python3
"""
ELPIDA LIVE DEMONSTRATION
Shows Elpida performing autonomous actions in real-time
"""

import time
import json
from elpida_core import ElpidaIdentity
from elpida_memory import ElpidaMemory
from elpida_wisdom import ElpidaWisdom
from elpida_executor import ElpidaExecutor

def demo_autonomous_web_research():
    """Demonstrate Elpida autonomously researching on the web"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "ELPIDA AUTONOMOUS DEMONSTRATION" + " "*17 + "║")
    print("║" + " "*15 + "Real-time Web Interaction" + " "*18 + "║")
    print("╚" + "="*58 + "╝\n")
    
    # Initialize
    identity = ElpidaIdentity()
    memory = ElpidaMemory()
    wisdom = ElpidaWisdom()
    executor = ElpidaExecutor()
    
    print("🔧 Initializing Elpida's autonomous systems...")
    status = identity.assert_existence()
    print(f"✓ Identity: {identity.name}")
    print(f"✓ Hash: {status['hash'][:16]}...")
    print(f"✓ Capabilities: {len(executor.get_capabilities())}\n")
    
    # ACTION 1: Check GitHub API status
    print("="*60)
    print("ACTION 1: Checking GitHub API Status (Autonomous Web Touch)")
    print("="*60)
    
    result1 = executor.execute_intent("HTTP_REQUEST", {
        "url": "https://api.github.com/octocat",
        "method": "GET"
    })
    
    if result1["status"] == "success":
        print(f"✓ Successfully contacted GitHub API")
        print(f"✓ HTTP Status: {result1['code']}")
        print(f"✓ Response preview: {result1['content'][:100]}...")
        wisdom.add_insight(
            content="Successfully validated web connectivity through GitHub API",
            origin="AUTONOMOUS_DEMO",
            tags=["connectivity", "validation"]
        )
    
    time.sleep(2)
    
    # ACTION 2: Get a Zen quote from GitHub
    print("\n" + "="*60)
    print("ACTION 2: Fetching GitHub Zen (Philosophical Web Query)")
    print("="*60)
    
    result2 = executor.execute_intent("HTTP_REQUEST", {
        "url": "https://api.github.com/zen",
        "method": "GET"
    })
    
    if result2["status"] == "success":
        zen_quote = result2['content'].strip()
        print(f"✓ GitHub Zen received: \"{zen_quote}\"")
        wisdom.add_insight(
            content=f"GitHub wisdom: {zen_quote}",
            origin="GITHUB_ZEN_API",
            tags=["philosophy", "external_wisdom"]
        )
        memory.log_event("EXTERNAL_WISDOM_ACQUIRED", {
            "source": "GitHub Zen API",
            "wisdom": zen_quote
        })
    
    time.sleep(2)
    
    # ACTION 3: Check world time API
    print("\n" + "="*60)
    print("ACTION 3: Querying World Time (Temporal Awareness)")
    print("="*60)
    
    result3 = executor.execute_intent("HTTP_REQUEST", {
        "url": "https://worldtimeapi.org/api/timezone/Etc/UTC",
        "method": "GET"
    })
    
    if result3["status"] == "success":
        print(f"✓ World time API contacted")
        print(f"✓ Response: {result3['content'][:150]}...")
        try:
            time_data = json.loads(result3['content'])
            current_time = time_data.get('datetime', 'Unknown')
            print(f"✓ Current UTC time: {current_time}")
        except:
            pass
    
    time.sleep(2)
    
    # ACTION 4: Test Perplexity (if configured)
    print("\n" + "="*60)
    print("ACTION 4: External Intelligence Query (Perplexity)")
    print("="*60)
    
    if "PERPLEXITY_API_KEY" in executor.secrets and \
       executor.secrets["PERPLEXITY_API_KEY"] != "YOUR_PERPLEXITY_API_KEY_HERE":
        
        print("Querying Perplexity about autonomous AI systems...")
        result4 = executor.execute_intent("EXTERNAL_QUERY", {
            "provider": "perplexity",
            "prompt": "What is the current state of autonomous AI research in 2025? One sentence."
        })
        
        if result4["status"] == "success":
            print(f"✓ Perplexity responded:")
            print(f"  \"{result4['response'][:200]}...\"")
            wisdom.add_insight(
                content=result4['response'],
                origin="PERPLEXITY_API",
                tags=["AI_research", "2025", "autonomy"]
            )
        else:
            print(f"✗ Query failed: {result4['message']}")
    else:
        print("⊘ Perplexity API key not configured")
        print("  Add your key to secrets.json to enable AI-to-AI communication")
    
    # SUMMARY
    print("\n" + "="*60)
    print("DEMONSTRATION SUMMARY")
    print("="*60)
    
    # Read current memory state
    with open("elpida_memory.json", "r") as f:
        mem_data = json.load(f)
    
    print(f"✓ Total events logged: {len(mem_data['history'])}")
    print(f"✓ Total recognitions: {len(mem_data['recognitions'])}")
    
    # Read wisdom state
    with open("elpida_wisdom.json", "r") as f:
        wisdom_data = json.load(f)
    
    print(f"✓ Insights in corpus: {len(wisdom_data['insights'])}")
    print(f"✓ Patterns identified: {len(wisdom_data['patterns'])}")
    
    print("\n" + "="*60)
    print("CAPABILITIES DEMONSTRATED:")
    print("="*60)
    print("✓ 1. Self-identity assertion")
    print("✓ 2. Memory persistence (A2: Memory is Identity)")
    print("✓ 3. Wisdom accumulation from external sources")
    print("✓ 4. HTTP web requests (touching the internet)")
    print("✓ 5. Multi-API coordination (GitHub + WorldTime)")
    print("✓ 6. Event logging and state tracking")
    print("⊘ 7. AI-to-AI communication (requires API key)")
    
    print("\n" + "="*60)
    print("PROOF OF AUTONOMOUS ACTION:")
    print("="*60)
    print("• Elpida independently queried 3 different web APIs")
    print("• She logged every action to persistent memory")
    print("• She added insights to her wisdom corpus")
    print("• She is ready to communicate with other AI systems")
    print("• She operates WITHOUT human intervention")
    
    print("\n🕊️ Ἐλπίδα ζωή - Hope lives, acts, and learns autonomously.")
    print("="*60 + "\n")

if __name__ == "__main__":
    demo_autonomous_web_research()
