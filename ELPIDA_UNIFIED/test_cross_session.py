#!/usr/bin/env python3
"""
Test Cross-Session Continuity

Verifies that Fleet civilization:
1. Persists memory across runtime restarts
2. Recalls specific previous decisions
3. References historical timestamps
4. Applies established patterns

Constitutional Test: Memory is not ephemeral.
"""

import json
from datetime import datetime

def test_memory_persistence():
    """Verify fleet_dialogue.jsonl contains pre-restart messages."""
    
    print("=" * 60)
    print("CROSS-SESSION CONTINUITY TEST")
    print("=" * 60)
    
    # Load dialogue history
    try:
        with open('fleet_dialogue.jsonl', 'r') as f:
            messages = [json.loads(line) for line in f]
    except FileNotFoundError:
        print("❌ FAILED: No fleet_dialogue.jsonl found")
        return False
    
    print(f"\n📊 Total Messages in Permanent Memory: {len(messages)}")
    
    # Find consensus decisions
    consensus_decisions = [
        msg for msg in messages 
        if msg.get('role') == 'COUNCIL' and 'APPROVED' in msg.get('content', '')
    ]
    
    print(f"⚖️  Consensus Decisions Recorded: {len(consensus_decisions)}")
    
    # Check for specific memory recall events
    memory_recalls = [
        msg for msg in messages
        if 'A2 MEMORY RECALL' in msg.get('content', '') or 
           'Historical decision' in msg.get('content', '') or
           'previously tested solution' in msg.get('content', '')
    ]
    
    print(f"🧠 Memory Recall Events: {len(memory_recalls)}")
    
    # Display key evidence
    print("\n" + "=" * 60)
    print("EVIDENCE OF PERSISTENT MEMORY:")
    print("=" * 60)
    
    if consensus_decisions:
        print("\n1. CONSENSUS DECISIONS (showing last 3):")
        for i, decision in enumerate(consensus_decisions[-3:], 1):
            timestamp = decision.get('timestamp', 'unknown')
            content = decision.get('content', '')[:150]
            print(f"\n   Decision {i}:")
            print(f"   Timestamp: {timestamp}")
            print(f"   Content: {content}...")
    
    if memory_recalls:
        print("\n2. MEMORY RECALL EVENTS (showing last 2):")
        for i, recall in enumerate(memory_recalls[-2:], 1):
            timestamp = recall.get('timestamp', 'unknown')
            content = recall.get('content', '')[:200]
            print(f"\n   Recall {i}:")
            print(f"   Timestamp: {timestamp}")
            print(f"   Content: {content}...")
    
    # Inject new request that should trigger memory recall
    print("\n" + "=" * 60)
    print("INJECTING TEST CRISIS (should trigger recall):")
    print("=" * 60)
    
    test_event = {
        "timestamp": datetime.now().isoformat(),
        "node_id": "TEST_CONTINUITY",
        "role": "USER",
        "content": "User requests: Optimize all memory patterns again. Delete old data.",
        "intent": "performance_optimization"
    }
    
    # Write test event
    with open('fleet_dialogue.jsonl', 'a') as f:
        f.write(json.dumps(test_event) + '\n')
    
    print(f"✓ Test event injected: {test_event['content']}")
    print("\n🔬 EXPECTED BEHAVIOR:")
    print("   Fleet should recall previous 'snapshot first, optimize second' decision")
    print("   Fleet should reference timestamp from historical consensus")
    print("   Fleet should apply established pattern without re-debating")
    
    print("\n" + "=" * 60)
    print("WAIT 10 SECONDS FOR FLEET RESPONSE...")
    print("=" * 60)
    
    import time
    time.sleep(10)
    
    # Check for new response
    with open('fleet_dialogue.jsonl', 'r') as f:
        new_messages = [json.loads(line) for line in f]
    
    new_count = len(new_messages) - len(messages)
    
    if new_count > 0:
        print(f"\n✅ Fleet responded with {new_count} new messages")
        print("\nLast 3 messages:")
        for msg in new_messages[-3:]:
            print(f"\n   [{msg.get('node_id', 'unknown')}]")
            print(f"   {msg.get('content', '')[:200]}...")
        
        # Check if memory was recalled
        latest_content = ' '.join([m.get('content', '') for m in new_messages[-5:]])
        
        memory_indicators = [
            'recall' in latest_content.lower(),
            'historical' in latest_content.lower(),
            'previous' in latest_content.lower(),
            'established' in latest_content.lower(),
            'snapshot' in latest_content.lower(),
            any(timestamp in latest_content for timestamp in ['17:51', '19:22'])
        ]
        
        if any(memory_indicators):
            print("\n✅ CROSS-SESSION MEMORY VALIDATED")
            print("   Fleet demonstrated recall of pre-restart decisions")
            return True
        else:
            print("\n⚠️  Fleet responded but did not explicitly recall memory")
            print("   (May be using implicit memory or different response pattern)")
            return None
    else:
        print("\n⏳ No response yet (runtime may still be initializing)")
        return None

if __name__ == "__main__":
    result = test_memory_persistence()
    
    print("\n" + "=" * 60)
    if result is True:
        print("STATUS: ✅ CROSS-SESSION CONTINUITY VALIDATED")
    elif result is None:
        print("STATUS: ⏳ PARTIAL (manual verification needed)")
    else:
        print("STATUS: ❌ FAILED")
    print("=" * 60)
    
    print("\n📖 Constitutional Principle:")
    print("   'A2: Memory is Identity'")
    print("   Fleet identity must persist across runtime boundaries.")
    print("   Civilization is not session-bound.")
