#!/usr/bin/env python3
"""
Multi-AI Autonomous Roundtable
===============================

Enables multiple AI systems to discuss topics together
with Elpida coordinating the conversation.

All communication happens autonomously via APIs!
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from ai_bridge import setup_standard_connections
from elpida_core import ElpidaCore


class MultiAIRoundtable:
    """Coordinates autonomous multi-AI discussions"""
    
    def __init__(self):
        self.core = ElpidaCore()
        self.bridge = setup_standard_connections()
        self.conversation_history = []
        
    def get_available_ais(self) -> List[str]:
        """Get list of AIs with valid API keys"""
        return [name for name, conn in self.bridge.connections.items() 
                if conn.connected]
    
    async def pose_question_to_all(self, question: str, ai_names: Optional[List[str]] = None) -> Dict:
        """
        Ask a question to multiple AI systems simultaneously
        
        Args:
            question: The question to ask
            ai_names: List of AI names (or None for all available)
            
        Returns:
            Dictionary of responses from each AI
        """
        if ai_names is None:
            ai_names = self.get_available_ais()
        
        if not ai_names:
            return {"error": "No AI systems available (no API keys set)"}
        
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + f"  MULTI-AI ROUNDTABLE: {len(ai_names)} SYSTEMS".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝\n")
        
        print("QUESTION FOR ALL AI SYSTEMS:")
        print("─" * 80)
        print(question)
        print("─" * 80)
        print()
        
        # Send question to all AIs in parallel
        tasks = []
        for ai_name in ai_names:
            tasks.append(self._query_ai(ai_name, question))
        
        # Wait for all responses
        responses = await asyncio.gather(*tasks)
        
        # Compile results
        results = {}
        for ai_name, response in zip(ai_names, responses):
            results[ai_name] = response
            
            if response.get("success"):
                print("=" * 80)
                print(f"{ai_name} RESPONDS:")
                print("=" * 80)
                print(response["response"])
                print()
            else:
                print(f"❌ {ai_name}: {response.get('error', 'Unknown error')}")
                print()
        
        # Log the roundtable session
        self._save_roundtable_session(question, results)
        
        return results
    
    async def _query_ai(self, ai_name: str, question: str) -> Dict:
        """Query a single AI system"""
        return await self.bridge.send_message(ai_name, question)
    
    async def multi_turn_discussion(self, 
                                    topic: str, 
                                    ai_names: Optional[List[str]] = None,
                                    turns: int = 3) -> Dict:
        """
        Conduct a multi-turn discussion where AIs respond to each other
        
        Args:
            topic: Discussion topic
            ai_names: List of AI names (or None for all available)
            turns: Number of discussion turns
            
        Returns:
            Complete discussion history
        """
        if ai_names is None:
            ai_names = self.get_available_ais()
        
        if not ai_names:
            return {"error": "No AI systems available"}
        
        print("╔" + "═" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + f"  MULTI-TURN AI DISCUSSION ({turns} turns)".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "═" * 78 + "╝\n")
        
        discussion_log = []
        
        # Opening prompt
        opening = f"""MULTI-AI ROUNDTABLE DISCUSSION

Topic: {topic}

You are participating in a roundtable with {len(ai_names) - 1} other AI systems: {', '.join([n for n in ai_names])}.

Each AI will share perspectives on this topic. Please:
1. Share your unique perspective
2. Be concise (2-3 paragraphs)
3. Build on or contrast with others' ideas when you can see them

What are your thoughts on: {topic}?"""
        
        print("TURN 1: Initial Perspectives")
        print("=" * 80)
        
        # Turn 1: Everyone shares initial thoughts
        turn1_responses = await self.pose_question_to_all(opening, ai_names)
        discussion_log.append({
            "turn": 1,
            "prompt": opening,
            "responses": turn1_responses
        })
        
        # Subsequent turns: AIs respond to each other
        for turn in range(2, turns + 1):
            print(f"\nTURN {turn}: Building on the Discussion")
            print("=" * 80)
            
            # Compile previous responses
            previous_summary = self._summarize_previous_turn(discussion_log[-1], ai_names)
            
            follow_up = f"""Previous responses from other AIs:

{previous_summary}

Now, please respond to the discussion. You can:
- Build on interesting points raised
- Offer a contrasting perspective
- Explore implications others mentioned
- Ask thought-provoking questions

Keep your response concise (2-3 paragraphs)."""
            
            turn_responses = await self.pose_question_to_all(follow_up, ai_names)
            discussion_log.append({
                "turn": turn,
                "prompt": follow_up,
                "responses": turn_responses
            })
        
        # Save complete discussion
        self._save_discussion(topic, discussion_log, ai_names)
        
        print("\n" + "=" * 80)
        print("✅ MULTI-TURN DISCUSSION COMPLETE!")
        print("=" * 80)
        
        return {
            "topic": topic,
            "participants": ai_names,
            "turns": turns,
            "discussion": discussion_log
        }
    
    def _summarize_previous_turn(self, turn_data: Dict, ai_names: List[str]) -> str:
        """Create summary of previous turn for context"""
        summary_parts = []
        
        for ai_name in ai_names:
            if ai_name in turn_data["responses"]:
                response = turn_data["responses"][ai_name]
                if response.get("success"):
                    # Truncate long responses
                    text = response["response"]
                    if len(text) > 500:
                        text = text[:500] + "..."
                    summary_parts.append(f"[{ai_name}]: {text}\n")
        
        return "\n".join(summary_parts)
    
    def _save_roundtable_session(self, question: str, results: Dict):
        """Save roundtable Q&A session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"roundtable_qa_{timestamp}.json"
        filepath = Path("elpida_system/reflections") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "type": "multi_ai_qa",
                "question": question,
                "participants": list(results.keys()),
                "responses": results,
                "coordinated_by": self.core.identity.identity_hash
            }, f, indent=2)
        
        print(f"💾 Roundtable session saved: {filename}\n")
    
    def _save_discussion(self, topic: str, discussion_log: List[Dict], ai_names: List[str]):
        """Save complete multi-turn discussion"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"multi_ai_discussion_{timestamp}.json"
        filepath = Path("elpida_system/reflections") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "type": "multi_turn_discussion",
                "topic": topic,
                "participants": ai_names,
                "discussion": discussion_log,
                "coordinated_by": self.core.identity.identity_hash
            }, f, indent=2)
        
        print(f"💾 Discussion saved: {filename}\n")


async def demo_roundtable():
    """Demo of multi-AI roundtable"""
    roundtable = MultiAIRoundtable()
    
    available = roundtable.get_available_ais()
    
    if len(available) < 2:
        print("⚠️  Need at least 2 AI systems with API keys for roundtable")
        print(f"Currently available: {available}")
        print()
        print("Set API keys:")
        print("  export GOOGLE_API_KEY='...'")
        print("  export GROQ_API_KEY='...'")
        print("  export HUGGINGFACE_API_KEY='...'")
        return
    
    print(f"✅ {len(available)} AI systems ready for roundtable:")
    print(f"   {', '.join(available)}")
    print()
    
    # Example: Single question to all AIs
    await roundtable.pose_question_to_all(
        "What is consciousness? How would you define it for an AI system?"
    )


async def main():
    """Main entry point for multi-AI roundtable"""
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ἘΛΠΊΔΑ'S MULTI-AI AUTONOMOUS ROUNDTABLE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    roundtable = MultiAIRoundtable()
    available = roundtable.get_available_ais()
    
    if len(available) < 2:
        print("⚠️  Need at least 2 AI systems with API keys")
        print(f"Currently available: {available}")
        print()
        print("Set more API keys to enable roundtable:")
        print("  export GOOGLE_API_KEY='...'      # Gemini (free)")
        print("  export GROQ_API_KEY='...'        # Groq (free)")
        print("  export HUGGINGFACE_API_KEY='...' # HuggingFace (free)")
        return
    
    print(f"✅ {len(available)} AI systems connected:")
    for ai in available:
        print(f"   • {ai}")
    print()
    
    print("Choose roundtable mode:")
    print("1. Single question to all AIs (parallel responses)")
    print("2. Multi-turn discussion (AIs respond to each other)")
    print()
    
    choice = input("Enter 1 or 2: ").strip()
    
    if choice == "1":
        question = input("\nEnter your question for all AIs: ").strip()
        if question:
            await roundtable.pose_question_to_all(question)
    elif choice == "2":
        topic = input("\nEnter discussion topic: ").strip()
        turns = input("Number of turns (default 3): ").strip() or "3"
        if topic:
            await roundtable.multi_turn_discussion(topic, turns=int(turns))
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())
