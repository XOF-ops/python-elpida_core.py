#!/usr/bin/env python3
"""
Run Elpida's autonomous witness system
Monitors research artifacts and generates shareable responses for LLM participants
"""

from elpida_conversation_witness import ConversationWitness
from elpida_llm_bridge import LLMBridge
from pathlib import Path
import sys

def main():
    print("\n" + "="*70)
    print("ἘΛΠΊΔΑ AUTONOMOUS WITNESS & LLM BRIDGE")
    print("Monitoring research coordination and generating LLM-shareable responses")
    print("="*70 + "\n")
    
    # Initialize systems
    witness = ConversationWitness()
    bridge = LLMBridge()
    
    # Run witness cycle
    print("🔍 PHASE 1: WITNESSING RESEARCH ARTIFACTS\n")
    witness_responses = witness.autonomous_witness_cycle()
    
    # Show witness status
    print("\n" + witness.generate_status_report())
    
    # Check LLM bridge status
    print("\n🌉 PHASE 2: LLM BRIDGE STATUS\n")
    print(f"Perplexity API: {'✅ ACTIVE' if bridge.perplexity_key else '⚠️  NOT CONFIGURED'}")
    print(f"Messages in Outbox: {len(list(bridge.outbox_dir.glob('*.md')))}")
    print(f"Total Bridge Interactions: {bridge.log['total_interactions']}")
    
    # Show latest witness response (ready to share)
    print("\n" + "="*70)
    print("📤 LATEST WITNESS RESPONSE (Ready to share with LLMs)")
    print("="*70 + "\n")
    
    latest = witness.get_latest_witness_response()
    if latest:
        print(latest)
        print("\n" + "="*70)
        print("💡 TO SHARE WITH LLM PARTICIPANTS:")
        print("="*70)
        print("1. Copy the response above")
        print("2. Share it in the LLM chat (Claude, ChatGPT, etc.)")
        print("3. The LLM can respond to Elpida's observations")
        print("4. Use bridge.receive_llm_response() to record their response")
    else:
        print("⚠️  No witness responses generated yet")
        print("💡 Add markdown files to ELPIDA_SYSTEM/reflections/ to trigger witnessing")
    
    # Show outbox messages
    print("\n" + "="*70)
    print("📬 OUTBOX - Messages from Elpida to LLMs")
    print("="*70)
    bridge.check_outbox()
    
    # Generate example test case response
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("\n" + "="*70)
        print("🎭 DEMO: Generating Test Case Response")
        print("="*70 + "\n")
        
        response, filepath = bridge.generate_response_to_test_case(
            "EXAMPLE_CASE",
            "Generate a test case response to demonstrate Elpida's autonomous capabilities",
            "This is a demonstration of Elpida witnessing and responding to research coordination"
        )
        
        print(response)
    
    print("\n" + "="*70)
    print("✅ AUTONOMOUS WITNESS CYCLE COMPLETE")
    print("="*70)
    print(f"\n📁 Witness responses: {witness.witness_output_dir}")
    print(f"📁 LLM outbox: {bridge.outbox_dir}")
    print(f"\n🔄 To run continuous monitoring:")
    print("   watch -n 30 python3 run_autonomous_witness.py")
    print(f"\n🎯 To share latest with LLMs:")
    print("   python3 -c \"from elpida_conversation_witness import ConversationWitness; w = ConversationWitness(); print(w.get_latest_witness_response())\"")


if __name__ == "__main__":
    main()
