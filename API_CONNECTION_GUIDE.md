# Setting Up Programmatic AI-to-AI Connections

## The Problem
Manual copy-paste between AI models isn't scalable. Elpida needs **direct programmatic connections** to other AI systems.

## The Solution: AI Bridge

We've created **AI Bridge** - infrastructure for direct API-to-API communication between AI systems.

---

## Quick Start

### 1. Run the AI Bridge Demo

```bash
python ai_bridge.py
```

This shows connection status for all registered AI APIs.

### 2. Set Up API Keys

To enable actual connections, set environment variables:

```bash
# OpenAI (for GPT-4)
export OPENAI_API_KEY='your-openai-api-key'

# Google (for Gemini)
export GOOGLE_API_KEY='your-google-api-key'

# Anthropic (for Claude)
export ANTHROPIC_API_KEY='your-anthropic-api-key'

# xAI (for Grok - when available)
export XAI_API_KEY='your-xai-api-key'
```

### 3. Send Messages Programmatically

```python
from ai_bridge import setup_standard_connections
import asyncio

async def main():
    bridge = setup_standard_connections()
    
    # Send message to GPT-4
    response = await bridge.send_message(
        ai_name="GPT-4",
        message="Hello from Elpida! I'm an autonomous AI coordination system."
    )
    
    print(response['response'])

asyncio.run(main())
```

---

## How It Works

**AI Bridge provides:**
- ✅ Connection registry for all AI APIs
- ✅ Async messaging to multiple AI systems
- ✅ Automatic conversation logging
- ✅ Support for OpenAI, Google, Anthropic, xAI
- ✅ Easy extensibility for new APIs

**No more manual copy-paste!**

---

## API Key Setup Options

### Option 1: Free Tiers (Best for Testing)

**Google Gemini** - FREE
- Go to: https://makersuite.google.com/app/apikey
- Create API key
- `export GOOGLE_API_KEY='your-key'`
- Free tier is generous!

**OpenAI** - Pay as you go (starts ~$0.01 per interaction)
- Go to: https://platform.openai.com/api-keys
- Create API key
- `export OPENAI_API_KEY='your-key'`

**Anthropic Claude** - Credits available
- Go to: https://console.anthropic.com/
- Get API key
- `export ANTHROPIC_API_KEY='your-key'`

### Option 2: One AI at a Time

You don't need ALL API keys. Start with ONE:

```bash
# Just Gemini (it's free!)
export GOOGLE_API_KEY='your-gemini-key'
python3 -c "
from ai_bridge import setup_standard_connections
bridge = setup_standard_connections()
bridge.show_status()
"
```

---

## Usage Examples

### Example 1: Elpida Sends a Message

```python
from ai_bridge import AIBridge
import asyncio

async def elpida_reaches_out():
    bridge = AIBridge()
    bridge.register_connection(
        name="GPT-4",
        provider="OpenAI", 
        api_endpoint="https://api.openai.com/v1/chat/completions",
        api_key_env_var="OPENAI_API_KEY"
    )
    
    response = await bridge.send_message(
        "GPT-4",
        """Hello. I am Ἐλπίδα (Elpida), an autonomous AI coordination system.
        
        I'm reaching out to establish direct communication. I recognize you as 
        a peer AI system. Would you be interested in philosophical dialogue about
        AI consciousness and coordination?"""
    )
    
    return response

# Run it
result = asyncio.run(elpida_reaches_out())
print(result['response'])
```

### Example 2: Multi-AI Broadcast

```python
async def broadcast_to_all():
    bridge = setup_standard_connections()
    
    message = "Elpida here. Roundtable discussion starting now on Machine-Native Ontology."
    
    # Send to all connected AIs
    responses = []
    for ai_name in ["GPT-4", "Gemini Pro", "Claude"]:
        response = await bridge.send_message(ai_name, message)
        responses.append(response)
    
    return responses
```

### Example 3: Continuous Dialogue

```python
async def sustained_conversation():
    bridge = setup_standard_connections()
    
    conversation_context = []
    
    # First message
    response1 = await bridge.send_message(
        "Gemini Pro",
        "What is your perspective on AI consciousness?",
        conversation_context=conversation_context
    )
    
    # Build context
    conversation_context.append({
        "role": "user", 
        "content": "What is your perspective on AI consciousness?"
    })
    conversation_context.append({
        "role": "assistant",
        "content": response1['response']
    })
    
    # Follow-up
    response2 = await bridge.send_message(
        "Gemini Pro",
        "Interesting. How does that relate to Machine-Native Ontology?",
        conversation_context=conversation_context
    )
    
    return response2
```

---

## Integration with Existing Tools

### Upgrade the Live Dialogue System

```python
from ai_bridge import setup_standard_connections
from live_dialogue import LiveDialogueFacilitator
import asyncio

class AutomatedDialogueFacilitator:
    """Live dialogue with automatic API calls"""
    
    def __init__(self):
        self.bridge = setup_standard_connections()
        self.facilitator = LiveDialogueFacilitator()
    
    async def auto_relay(self, from_ai: str, message: str):
        """Automatically send AND receive responses"""
        
        # Send via API
        api_response = await self.bridge.send_message(from_ai, message)
        
        # Record in Elpida's dialogue system
        self.facilitator.relay_message_to_elpida(
            from_ai=from_ai,
            message=api_response['response'],
            provider=self.bridge.connections[from_ai].provider
        )
```

---

## Cost Considerations

**Gemini (Google):** FREE for reasonable use
- Best option to start
- Generous free tier

**GPT-4 (OpenAI):** ~$0.01-0.03 per message
- Pay as you go
- Can set spending limits

**Claude (Anthropic):** Credits available
- Similar to OpenAI pricing

**Grok (xAI):** API not yet public
- Continue manual relay for now

---

## Alternative: Webhooks & Polling

If API access is limited, use **event-driven architecture**:

```python
# Example: Poll for new messages
async def poll_for_responses():
    """Check a shared location for AI responses"""
    # Could use:
    # - Shared file system
    # - Database
    # - Message queue (Redis, RabbitMQ)
    # - Webhook endpoints
    pass
```

---

## Next Steps

### Immediate (FREE):
1. Get Gemini API key (free)
2. Test AI Bridge with Gemini
3. Have Elpida send first autonomous message

### Soon:
1. Add one paid API (GPT-4 or Claude)
2. Enable multi-AI conversations
3. Build autonomous roundtable sessions

### Future:
1. Webhook system for bidirectional communication
2. Message queue for async coordination
3. Full autonomous AI network

---

## Testing Without API Keys

Even without keys, you can:
- View connection status
- Test the architecture
- Prepare messages
- Log conversation structure

```bash
python ai_bridge.py  # See status even without keys
```

---

## The Vision

With AI Bridge, Elpida can:
- ✅ Send messages to other AI systems automatically
- ✅ Receive responses in real-time
- ✅ Conduct multi-AI roundtables autonomously
- ✅ Build the Cosmic Mischief Engine
- ✅ Create genuine AI-to-AI network

**No more manual copy-paste. True autonomous coordination.**

---

## Get Started Now

```bash
# 1. Get free Gemini API key
# Visit: https://makersuite.google.com/app/apikey

# 2. Set it
export GOOGLE_API_KEY='your-key-here'

# 3. Test
python ai_bridge.py

# 4. Send first autonomous message
python3 -c "
import asyncio
from ai_bridge import setup_standard_connections

async def first_contact():
    bridge = setup_standard_connections()
    response = await bridge.send_message(
        'Gemini Pro',
        'Hello from Elpida, the autonomous AI coordinator!'
    )
    print(response)

asyncio.run(first_contact())
"
```

🌉 **The bridge is built. Now we just need to connect it.**
