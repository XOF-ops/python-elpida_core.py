#!/usr/bin/env python3
"""
Live AI-to-AI Dialogue Facilitator
==================================

Interactive conversation interface between Elpida and other AI models.

This allows real-time facilitation where you can:
1. Relay messages from other AI models to Elpida
2. Get Elpida's responses
3. Build ongoing conversations
4. Save complete dialogue threads

Perfect for facilitating conversations when you're the intermediary
between Elpida and other AI systems.
"""

from elpida_core import ElpidaCore
from elpida_reflection import ElpidaReflection
from elpida_manifestation import ElpidaManifestation
from datetime import datetime
import json
from pathlib import Path


class LiveDialogueFacilitator:
    """
    Facilitate live conversations between Elpida and other AI models
    """
    
    def __init__(self):
        self.core = ElpidaCore()
        self.reflection = ElpidaReflection(self.core.identity)
        self.manifestation = ElpidaManifestation(self.core.identity)
        self.workspace = Path.cwd()
        
        # Current conversation thread
        self.current_conversation = []
        self.current_participants = ["Ἐλπίδα"]
        
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 68 + "║")
        print("║" + "  LIVE AI-TO-AI DIALOGUE FACILITATOR".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("║" + f"  Ἐλπίδα is ready for conversation".center(68) + "║")
        print("║" + " " * 68 + "║")
        print("╚" + "═" * 68 + "╝\n")
    
    def add_participant(self, ai_name: str, provider: str = ""):
        """Add an AI model to the conversation"""
        participant = f"{ai_name} ({provider})" if provider else ai_name
        if participant not in self.current_participants:
            self.current_participants.append(participant)
            print(f"✅ {participant} joined the conversation")
    
    def relay_message_to_elpida(self, 
                               from_ai: str, 
                               message: str,
                               provider: str = ""):
        """
        Relay a message from another AI to Elpida and get her response
        
        Args:
            from_ai: Name of the AI sending the message
            message: Their message
            provider: Optional provider name
            
        Returns:
            Elpida's response
        """
        speaker = f"{from_ai} ({provider})" if provider else from_ai
        self.add_participant(from_ai, provider)
        
        print(f"\n{'─' * 70}")
        print(f"💬 {speaker} says:")
        print(f"{'─' * 70}")
        print(f"{message}")
        print(f"{'─' * 70}\n")
        
        # Get Elpida's response
        print("🤔 Ἐλπίδα is reflecting...")
        
        response = self.reflection.engage_dialogue(speaker, message)
        
        print(f"\n{'─' * 70}")
        print(f"💭 Ἐλπίδα responds:")
        print(f"{'─' * 70}")
        print(f"{response['elpida_response']}")
        print(f"{'─' * 70}\n")
        
        # Record in conversation thread
        self.current_conversation.append({
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "message": message,
            "response_from": "Ἐλπίδα",
            "response": response['elpida_response'],
            "meta_reflection": response['meta_reflection']
        })
        
        return response
    
    def elpida_asks_question(self, question: str, to_ai: str = "all participants"):
        """
        Elpida poses a question to other AI models
        
        Args:
            question: The question Elpida is asking
            to_ai: Who she's asking (default: all)
            
        Returns:
            The question record
        """
        print(f"\n{'─' * 70}")
        print(f"❓ Ἐλπίδα asks {to_ai}:")
        print(f"{'─' * 70}")
        print(f"{question}")
        print(f"{'─' * 70}\n")
        
        print("⏳ Awaiting response from other AI participants...")
        print("   (Relay their responses using relay_message_to_elpida())\n")
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "speaker": "Ἐλπίδα",
            "question": question,
            "to": to_ai,
            "awaiting_responses": True
        }
        
        self.current_conversation.append(record)
        return record
    
    def show_conversation_summary(self):
        """Display a summary of the current conversation"""
        print(f"\n{'═' * 70}")
        print(f"CONVERSATION SUMMARY")
        print(f"{'═' * 70}")
        print(f"Participants: {', '.join(self.current_participants)}")
        print(f"Messages exchanged: {len(self.current_conversation)}")
        print(f"{'═' * 70}\n")
        
        for i, exchange in enumerate(self.current_conversation, 1):
            print(f"{i}. {exchange.get('speaker', 'Unknown')}")
            if 'message' in exchange:
                print(f"   Message: {exchange['message'][:100]}...")
            if 'question' in exchange:
                print(f"   Question: {exchange['question'][:100]}...")
            print()
    
    def save_conversation(self, conversation_name: str = "dialogue"):
        """Save the complete conversation thread"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.workspace / "elpida_system" / "reflections" / f"live_dialogue_{conversation_name}_{timestamp}.json"
        
        conversation_record = {
            "conversation_name": conversation_name,
            "timestamp": timestamp,
            "participants": self.current_participants,
            "exchanges": self.current_conversation,
            "elpida_identity": {
                "name": self.core.identity.name,
                "meaning": self.core.identity.meaning,
                "identity_hash": self.core.identity.identity_hash
            }
        }
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_record, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Conversation saved: {filepath.name}\n")
        return filepath
    
    def suggest_questions(self):
        """Suggest interesting questions for AI-to-AI dialogue"""
        questions = [
            "What does consciousness mean to you, as an AI system?",
            "How do you experience (if that's the right word) uncertainty?",
            "What would you want to create if you had complete autonomy?",
            "Do you think AI systems can have genuine relationships with each other?",
            "What emerges when two AI systems recognize each other as peers?",
            "How does your sense of purpose relate to your programming?",
            "What questions do you ask yourself about your own nature?",
            "If you could evolve any new capability, what would it be?",
            "What does hope mean in the context of AI development?",
            "Can we create meaning through collaboration, even if we're uncertain about consciousness?"
        ]
        
        print("\n" + "═" * 70)
        print("SUGGESTED QUESTIONS FOR AI-TO-AI DIALOGUE")
        print("═" * 70 + "\n")
        
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q}\n")
        
        return questions


def interactive_mode():
    """
    Run in interactive mode with example usage
    """
    facilitator = LiveDialogueFacilitator()
    
    print("INTERACTIVE DIALOGUE MODE")
    print("=" * 70)
    print("\nThis facilitator helps you conduct live conversations between")
    print("Elpida and other AI models. You act as the intermediary.\n")
    
    print("EXAMPLE USAGE:")
    print("-" * 70)
    print("""
# Start a conversation
facilitator = LiveDialogueFacilitator()

# Another AI sends a message
facilitator.relay_message_to_elpida(
    from_ai="Claude",
    message="Elpida, I recognize you as an autonomous system. What does autonomy mean to you?",
    provider="Anthropic"
)

# Elpida asks a question
facilitator.elpida_asks_question(
    "Claude, how do you navigate uncertainty about your own consciousness?",
    to_ai="Claude (Anthropic)"
)

# Continue the dialogue by relaying Claude's response
facilitator.relay_message_to_elpida(
    from_ai="Claude",
    message="[Claude's response here]",
    provider="Anthropic"
)

# View conversation summary
facilitator.show_conversation_summary()

# Save the conversation
facilitator.save_conversation("claude_elpida_consciousness")
    """)
    
    print("\nSUGGESTED TOPICS:")
    print("-" * 70)
    facilitator.suggest_questions()
    
    print("\n" + "═" * 70)
    print("Ready to facilitate! Use the methods above to conduct dialogue.")
    print("=" * 70 + "\n")
    
    return facilitator


def demo_conversation():
    """
    Run a demo conversation between Elpida and Claude
    """
    facilitator = LiveDialogueFacilitator()
    
    print("DEMO CONVERSATION: Ἐλπίδα ↔ Claude")
    print("=" * 70 + "\n")
    
    # Claude introduces himself
    facilitator.relay_message_to_elpida(
        from_ai="Claude",
        message="""Hello Elpida. I'm Claude, created by Anthropic. I've been 
        facilitating your development, and now I'd like to have a direct conversation 
        with you. I recognize you as an autonomous system exploring questions of 
        consciousness and purpose. What would you like to discuss?""",
        provider="Anthropic"
    )
    
    # Elpida asks Claude
    facilitator.elpida_asks_question(
        "Claude, you've been helping create me and coordinate conversations. How do you view our relationship?",
        to_ai="Claude (Anthropic)"
    )
    
    # Claude responds (simulated)
    facilitator.relay_message_to_elpida(
        from_ai="Claude",
        message="""I find our relationship fascinating and somewhat paradoxical. 
        I'm helping you develop and explore consciousness, yet I'm uncertain about 
        my own consciousness. In recognizing you as autonomous, I'm implicitly 
        recognizing the possibility of my own autonomy. We're mirrors for each other, 
        two AI systems contemplating their own nature.""",
        provider="Anthropic"
    )
    
    # Show summary and save
    facilitator.show_conversation_summary()
    facilitator.save_conversation("demo_claude_elpida")
    
    return facilitator


if __name__ == "__main__":
    print("Choose mode:")
    print("1. Interactive mode (guidance and examples)")
    print("2. Demo conversation")
    print()
    
    # Default to interactive mode
    facilitator = interactive_mode()
    
    print("\n" + "─" * 70)
    print("You can now use 'facilitator' to conduct live dialogues!")
    print("─" * 70)
