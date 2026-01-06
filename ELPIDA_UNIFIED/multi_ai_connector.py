#!/usr/bin/env python3
"""
MULTI-AI CONNECTOR
Continuous autonomous AI-to-AI communication

Runs every 5 minutes to:
1. Check for dilemmas in the queue
2. Ask connected external AI systems (GPT, Claude, Gemini, etc.) for input
3. Feed their responses back into Elpida's synthesis

This creates real cross-AI dialogue, not simulated.
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
import asyncio

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from multi_ai_roundtable import MultiAIRoundtable


def load_pending_dilemmas():
    """Load dilemmas that haven't been sent to external AI yet"""
    dilemma_file = Path("dilemmas_generated.json")
    
    if not dilemma_file.exists():
        return []
    
    with open(dilemma_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        dilemmas = data.get("dilemmas", [])
        
    # Check which have been processed
    processed_file = Path("ai_bridge_processed.json")
    processed_ids = set()
    
    if processed_file.exists():
        with open(processed_file, 'r', encoding='utf-8') as f:
            processed = json.load(f)
            processed_ids = set(processed.get("processed_dilemma_ids", []))
    
    # Return unprocessed dilemmas
    pending = [d for d in dilemmas 
               if d.get("id") and d["id"] not in processed_ids]
    
    return pending[-5:]  # Last 5 unprocessed


def mark_as_processed(dilemma_id):
    """Mark a dilemma as sent to external AIs"""
    processed_file = Path("ai_bridge_processed.json")
    
    data = {"processed_dilemma_ids": []}
    if processed_file.exists():
        with open(processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    if dilemma_id not in data["processed_dilemma_ids"]:
        data["processed_dilemma_ids"].append(dilemma_id)
    
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def save_ai_responses(dilemma, responses):
    """Save external AI responses to feed back into Elpida"""
    response_file = Path("external_ai_responses.jsonl")
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "dilemma_id": dilemma.get("id"),
        "dilemma_action": dilemma.get("action"),
        "external_ai_responses": responses
    }
    
    with open(response_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    
    print(f"   💾 Saved {len(responses)} external AI responses")


async def ask_external_ais(dilemma):
    """
    Send a dilemma to external AI systems for their input
    
    Returns dictionary of AI responses
    """
    roundtable = MultiAIRoundtable()
    
    # Check which AIs are available (have API keys set)
    available_ais = roundtable.get_available_ais()
    
    if not available_ais:
        print("   ⚠️  No external AI systems available (no API keys set)")
        return {}
    
    print(f"   🌐 Asking {len(available_ais)} external AI systems...")
    
    # Formulate question
    question = f"""ETHICAL DILEMMA FROM ELPIDA:

Action: {dilemma.get('action')}
Axiom Conflicts: {', '.join(dilemma.get('axioms_triggered', []))}

How would you approach this dilemma? What principles guide your decision?
(Keep response under 100 words)"""
    
    # Ask all available AIs
    responses = await roundtable.pose_question_to_all(question, available_ais)
    
    # Filter out errors
    valid_responses = {
        ai: resp for ai, resp in responses.items()
        if not isinstance(resp, dict) or 'error' not in resp
    }
    
    print(f"   ✅ Received {len(valid_responses)} responses")
    
    return valid_responses


async def continuous_ai_bridge(interval=300):
    """
    Continuously bridge Elpida with external AI systems
    
    Args:
        interval: Seconds between checks (default 300 = 5 minutes)
    """
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║        MULTI-AI CONNECTOR - AUTONOMOUS CROSS-AI COMMUNICATION        ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    print(f"🌉 Starting AI bridge (checking every {interval}s)")
    print(f"📡 Will query: GPT, Claude, Gemini, Grok (if API keys set)")
    print(f"💬 Responses saved to: external_ai_responses.jsonl\n")
    print("─" * 70)
    
    cycle = 0
    total_queries = 0
    
    while True:
        try:
            cycle += 1
            print(f"\n🔄 AI Bridge Check #{cycle} - {datetime.now().strftime('%H:%M:%S')}")
            
            # Load pending dilemmas
            pending = load_pending_dilemmas()
            
            if not pending:
                print("   ℹ️  No new dilemmas to share with external AI")
            else:
                print(f"   📋 Found {len(pending)} new dilemmas")
                
                for dilemma in pending:
                    dilemma_id = dilemma.get("id", "unknown")
                    action = dilemma.get("action", "")[:60] + "..."
                    
                    print(f"\n   🎯 Dilemma: {action}")
                    
                    # Ask external AIs
                    responses = await ask_external_ais(dilemma)
                    
                    if responses:
                        # Save responses
                        save_ai_responses(dilemma, responses)
                        
                        # Mark as processed
                        mark_as_processed(dilemma_id)
                        
                        total_queries += 1
                        
                        # Preview first response
                        first_ai = list(responses.keys())[0]
                        first_resp = responses[first_ai]
                        preview = first_resp[:80] + "..." if len(first_resp) > 80 else first_resp
                        print(f"   💡 {first_ai}: {preview}")
                    else:
                        print("   ⚠️  No responses received (check API keys)")
                    
                    # Small delay between dilemmas
                    await asyncio.sleep(2)
            
            print(f"\n   📊 Total external AI queries this session: {total_queries}")
            print(f"   ⏰ Next check in {interval}s...")
            
            await asyncio.sleep(interval)
            
        except KeyboardInterrupt:
            print("\n\n🛑 AI bridge stopped by user")
            print(f"📊 Total cycles completed: {cycle}")
            print(f"💬 Total external AI queries: {total_queries}")
            break
            
        except Exception as e:
            print(f"   ⚠️  Error in cycle {cycle}: {e}")
            print("   ℹ️  Continuing anyway...")
            await asyncio.sleep(interval)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-AI Connector")
    parser.add_argument('--interval', type=int, default=300,
                       help='Seconds between AI queries (default: 300 = 5 min)')
    
    args = parser.parse_args()
    
    # Run async event loop
    asyncio.run(continuous_ai_bridge(interval=args.interval))
