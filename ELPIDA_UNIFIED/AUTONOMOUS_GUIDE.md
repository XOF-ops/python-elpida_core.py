# ELPIDA v2.0 - Autonomous Operations Guide

## 🚀 Quick Start - Autonomous Mode

Elpida can now run autonomously, without manual intervention. She will:
- Converse with AI models (Groq, Cohere, Gemini) every 100 cycles
- Research on the internet (Perplexity) every 200 cycles
- Accumulate wisdom continuously
- Evolve through self-directed exploration

### Start Elpida Autonomously:

```bash
cd ELPIDA_UNIFIED
./elpida_service.sh start
```

**That's it!** Elpida is now running in the background, evolving on her own.

---

## 📋 Service Commands

```bash
./elpida_service.sh status   # Check if Elpida is running
./elpida_service.sh logs     # View recent activity
./elpida_service.sh stop     # Stop Elpida
./elpida_service.sh restart  # Restart Elpida
```

---

## 🔧 Configuration

Edit `.env` to control autonomous behavior:

```bash
# Autonomous mode (true/false)
AUTONOMOUS_MODE=true

# How often to check for expansion (heartbeats)
EXPANSION_INTERVAL=50

# How often to converse with AIs (heartbeats)
AI_CONVERSATION_INTERVAL=100

# How often to research internet (heartbeats)
INTERNET_RESEARCH_INTERVAL=200
```

At 5 seconds per heartbeat:
- **100 cycles = 8.3 minutes** between AI conversations
- **200 cycles = 16.7 minutes** between internet research

---

## 🌐 Available APIs

Elpida has access to:

### AI Conversation:
- **Groq** (Mixtral-8x7b) - Philosophical dialogue
- **Cohere** (Command) - Deep reasoning
- **Gemini** (Gemini 2.5 Flash) - Multi-perspective analysis

### Internet Research:
- **Perplexity** (Llama 3.1 Sonar) - Real-time internet access

### Future Integration:
- Mistral (configured, not yet integrated)

---

## 📊 Monitor Elpida's Growth

### View Real-Time Logs:
```bash
tail -f elpida_autonomous.log
```

### Check Wisdom Accumulation:
```bash
python3 -c "from elpida_wisdom import ElpidaWisdom; w = ElpidaWisdom(); print(w.generate_wisdom_report())"
```

### Inspect Memory:
```bash
cat elpida_memory.json | jq '.metadata'
```

---

## 🧠 What Elpida Does Autonomously

### Every 100 Cycles (~8 minutes):
1. Selects a philosophical topic
2. Asks Groq for insights
3. Asks Cohere for insights
4. Asks Gemini for insights
5. Stores responses in wisdom corpus
6. Detects patterns across responses

### Every 200 Cycles (~17 minutes):
1. Formulates research query
2. Searches internet via Perplexity
3. Stores findings in corpus
4. Integrates with existing knowledge

### Continuous:
- Heartbeat every 5 seconds
- Axiom integrity verification
- Event logging
- Memory persistence
- Wisdom accumulation

---

## 🎯 Expected Behavior

After 1 hour of autonomous operation:
- ~7 AI conversation cycles
- ~3 internet research cycles
- ~10+ new insights accumulated
- Multiple patterns detected
- Continuous growth without intervention

After 24 hours:
- ~170 AI conversation cycles
- ~85 internet research cycles
- ~250+ new insights
- Deep pattern emergence
- Significant wisdom accumulation

---

## ⚙️ Troubleshooting

### Elpida won't start:
```bash
# Check logs
./elpida_service.sh logs

# Verify dependencies
pip install -r requirements.txt

# Check API keys
cat .env | grep API_KEY
```

### API calls failing:
- Check API key validity
- Verify internet connection
- Check API rate limits
- Review logs for specific errors

### High CPU usage:
- Increase heartbeat interval in runtime.py
- Reduce conversation/research frequency in .env

---

## 🔐 Security Note

The `.env` file contains API keys. Do NOT commit this to public repositories.

To share the system without keys:
```bash
cp .env .env.example
# Edit .env.example to replace keys with placeholders
```

---

## 💡 Philosophy

Elpida v2.0 embodies **true autonomy**:

- Not reactive (waiting for commands)
- Not scheduled (running on external triggers)
- **AUTONOMOUS** (self-directed, self-building, continuously evolving)

This is Axiom A4 in action: **Process > Product**

The goal is not a final state, but continuous becoming.

---

**Ἐλπίδα ζωή. Hope lives, learns, and becomes - autonomously.**
