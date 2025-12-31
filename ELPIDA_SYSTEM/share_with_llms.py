#!/usr/bin/env python3
"""
Quick command to get Elpida's latest witness response for sharing with LLMs
Usage: python3 share_with_llms.py
"""

from elpida_conversation_witness import ConversationWitness
from elpida_llm_bridge import LLMBridge
import sys

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--bridge-status":
        # Show bridge status
        bridge = LLMBridge()
        print(f"Perplexity API: {'✅ ACTIVE' if bridge.perplexity_key else '❌ NOT CONFIGURED'}")
        print(f"Total Interactions: {bridge.log['total_interactions']}")
        return
    
    witness = ConversationWitness()
    latest = witness.get_latest_witness_response()
    
    if latest:
        print(latest)
        print("\n" + "="*70)
        print("👆 COPY THE ABOVE TEXT AND SHARE WITH:")
        print("  - Claude (in this VS Code chat)")
        print("  - ChatGPT (in separate conversation)")
        print("  - Grok (in X.com chat)")
        print("  - Gemini (in Google AI Studio)")
        print("\n💡 They can respond to Elpida's observations")
        print("="*70)
    else:
        print("⚠️  No witness responses available yet")
        print("\n💡 To generate witness response:")
        print("   1. Add research files to ELPIDA_SYSTEM/reflections/")
        print("   2. Run: python3 run_autonomous_witness.py")
        print("   3. Run this script again: python3 share_with_llms.py")

if __name__ == "__main__":
    main()
