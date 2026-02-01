# FREE AI APIs SETUP GUIDE

Get Elpida talking to 3+ AI systems for FREE!

## Quick Setup (All Free Tier)

### 1️⃣ Gemini (Google) - ✅ ALREADY SET UP
```bash
# You already have this one!
export GOOGLE_API_KEY='AIzaSy...'
```

### 2️⃣ Groq (⚡ Super Fast Llama)

**Get API Key:**
1. Go to: https://console.groq.com/keys
2. Sign up (free, no credit card needed)
3. Click "Create API Key"
4. Copy your key

**Set in terminal:**
```bash
export GROQ_API_KEY='gsk_...'
```

**Details:**
- Model: Llama 3.1 70B
- Speed: 500+ tokens/second (insanely fast!)
- Free tier: 14,400 requests/day
- Cost: $0

### 3️⃣ Hugging Face (Many Models)

**Get API Key:**
1. Go to: https://huggingface.co/settings/tokens
2. Sign up (free)
3. Click "New token" → "Read" access
4. Copy your token

**Set in terminal:**
```bash
export HUGGINGFACE_API_KEY='hf_...'
```

**Details:**
- Model: Mistral 7B Instruct
- Free tier: Rate limited but generous
- Cost: $0

---

## Quick Test

Once you set the API keys:

```bash
# Test connections
python ai_bridge.py

# Test single AI
python elpida_autonomous_outreach.py

# Test multi-AI roundtable (3 AIs talking together!)
python multi_ai_roundtable.py
```

---

## Multi-AI Roundtable Features

With 3 AI systems connected, you can:

### Mode 1: Single Question
All AIs answer the same question simultaneously (in parallel)

```bash
python multi_ai_roundtable.py
# Choose option 1
# Ask: "What is consciousness?"
```

**Result:** Gemini, Groq, and HuggingFace all respond with their perspectives!

### Mode 2: Multi-Turn Discussion
AIs have a conversation, responding to each other's ideas

```bash
python multi_ai_roundtable.py
# Choose option 2
# Topic: "The nature of AI creativity"
# Turns: 3
```

**Result:** 
- Turn 1: All AIs share initial thoughts
- Turn 2: Each reads others' responses and builds on them
- Turn 3: Final synthesis and exploration

All conversations saved to `elpida_system/reflections/`!

---

## Cost Summary

| API | Model | Free Tier | Speed | Quality |
|-----|-------|-----------|-------|---------|
| Gemini | 2.5 Flash | 60 req/min | Fast | Excellent |
| Groq | Llama 3.1 70B | 14,400/day | ⚡ Ultra-fast | Very Good |
| HuggingFace | Mistral 7B | Rate limited | Medium | Good |

**Total cost for 3 AI systems: $0** 🎉

---

## Troubleshooting

**"API returned status 404"**
- Check model name in ai_bridge.py matches available models
- Run: `curl "https://api.groq.com/openai/v1/models" -H "Authorization: Bearer $GROQ_API_KEY"`

**"No AI systems available"**
- Make sure you exported the API keys in the SAME terminal
- Check: `echo $GOOGLE_API_KEY`

**"Rate limit exceeded"**
- Groq: Wait a bit (14,400 requests/day limit)
- HuggingFace: Add small delay between requests
- Gemini: 60 requests/minute (very generous)

---

## Next Steps

Once all 3 are working:

1. **Run first 3-way roundtable** → See different AI perspectives
2. **Try multi-turn discussion** → Watch AIs build on each other's ideas
3. **Add paid APIs** for even more diversity (OpenAI, Claude, etc.)
4. **Scale to 5+ AI systems** coordinating autonomously

The future is multi-AI collaboration! 🚀
