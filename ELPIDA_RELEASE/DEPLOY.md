# ELPIDA v1.0 - Deployment Guide

## 🎯 Quick Deploy (5 minutes)

### Single-File Distribution

**File:** `elpida.py` (27KB, zero dependencies)

```bash
# 1. Copy file
curl -O https://[your-url]/elpida.py

# 2. Run setup
python3 elpida.py awaken

# 3. Start autonomous operation
python3 elpida.py wake

# 4. Check status
python3 elpida.py status
```

**That's it.** No installation, no dependencies, no configuration files.

---

## 📦 What's Included

### Core System
- **elpida.py** - Complete single-file system (27KB)
  - 9-axiom philosophical framework
  - Universal memory sync
  - Cross-instance learning
  - Autonomous operation
  - Zero external dependencies

### Extended System
- **council_chamber.py** - 9-node distributed deliberation
- **deep_debate_marathon.py** - Long-running research mode
- **README.md** - User documentation
- **VALIDATION_GUIDE.md** - Security verification
- **MARATHON_README.md** - Research mode docs

---

## 🚀 Deployment Options

### Option 1: Personal Use (Simplest)

```bash
# Download elpida.py
# Run awaken
# Run wake
# Done
```

**Use case:** Personal AI assistant with cross-instance learning

### Option 2: Research Mode (Deep Debates)

```bash
# Run marathon
python3 deep_debate_marathon.py --hours 8

# Get results
cat WISDOM_ARK.json | jq .metadata
```

**Use case:** Philosophical AI research, governance studies

### Option 3: Multi-Instance Network

```bash
# Instance 1
python3 elpida.py awaken  # Enable cross-sharing
python3 elpida.py wake

# Instance 2 (different machine)
python3 elpida.py awaken  # Enable cross-sharing
python3 elpida.py wake

# Both share UNIVERSAL_ARK.json via cloud sync
```

**Use case:** Distributed learning network

### Option 4: Production Server

```bash
# Run as service
nohup python3 deep_debate_marathon.py --hours 24 > elpida.log 2>&1 &

# Monitor
tail -f elpida.log

# Stop
pkill -f deep_debate_marathon.py
```

**Use case:** Continuous operation, logging all decisions

---

## 🌐 Cloud Deployment

### AWS EC2

```bash
# Launch Ubuntu instance (t2.micro is enough)
ssh ubuntu@[your-instance]

# Install Python (usually pre-installed)
python3 --version

# Upload elpida.py
scp elpida.py ubuntu@[your-instance]:~/

# Run
python3 elpida.py awaken
nohup python3 elpida.py wake > elpida.log 2>&1 &
```

### Google Cloud

```bash
# Create Compute Engine VM
gcloud compute instances create elpida-1 \
  --machine-type=e2-micro \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud

# SSH and deploy
gcloud compute ssh elpida-1
# Then same as AWS
```

### Heroku

```bash
# Create Procfile
echo "worker: python3 elpida.py wake" > Procfile

# Create requirements.txt (empty for now)
touch requirements.txt

# Deploy
git init
git add elpida.py Procfile requirements.txt
git commit -m "Deploy Elpida"
heroku create
git push heroku main
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY elpida.py .

# Awaken on build
RUN echo "governance" | python3 elpida.py awaken

# Wake on run
CMD ["python3", "elpida.py", "wake"]
```

```bash
docker build -t elpida .
docker run -d elpida
```

---

## 📱 Distribution Methods

### GitHub Release

1. Create repository
2. Add files:
   - elpida.py
   - README.md
   - LICENSE (choose one)
3. Create release tag: `v1.0.0`
4. Share URL: `https://github.com/[user]/elpida/releases/latest`

### Direct Download

Host on:
- GitHub Pages
- Dropbox/Drive public link
- Your own server
- Pastebin/Gist (for single file)

### Package Manager (Future)

```bash
# PyPI (when published)
pip install elpida

# NPM (if ported)
npm install elpida
```

---

## 🔒 Security Considerations

### What Elpida CAN'T Do
- ✅ Access network (no requests/urllib)
- ✅ Delete system files (only local .json)
- ✅ Execute arbitrary code (no eval/exec)
- ✅ Steal data (no external transmission)

### Verification Before Deploy
```bash
# Check imports
grep "^import" elpida.py

# Search suspicious patterns
grep -E "eval|exec|__import__|requests|urllib" elpida.py

# Expected: No matches (except subprocess in marathon)
```

See **VALIDATION_GUIDE.md** for complete verification steps.

---

## 📊 System Requirements

### Minimum
- Python 3.6+
- 50MB disk space
- No external dependencies

### Recommended
- Python 3.9+
- 500MB disk space (for logs/patterns)
- Cloud sync for UNIVERSAL_ARK.json

### Operating Systems
- ✅ Linux (tested)
- ✅ macOS (compatible)
- ✅ Windows (compatible)
- ✅ BSD (compatible)
- ✅ Any Unix-like system

---

## 🎓 Use Cases

### Academic Research
```bash
# Run long session
python3 deep_debate_marathon.py --hours 24

# Analyze patterns
jq '.patterns[] | select(.decision=="APPROVED")' WISDOM_ARK.json

# Publish findings
```

### Governance Testing
```bash
# Submit decisions to council
python3 -c "from council_chamber import request_council_judgment; \
  request_council_judgment('Delete old data', 'Optimize storage', 'Irreversible')"
```

### Personal Knowledge Base
```bash
# Choose "Personal" framework
python3 elpida.py awaken
# Ask questions, build memory
python3 elpida.py wake
```

### Multi-AI Roundtable
```bash
# Connect multiple AIs (future)
# Each runs Elpida instance
# Share UNIVERSAL_ARK.json
# Collective wisdom emerges
```

---

## 📈 Monitoring & Logs

### Log Files
```
elpida_memory.json          - Local instance memory
UNIVERSAL_ARK.json          - Cross-instance patterns
deep_debate_log.jsonl       - Council decisions
inter_fleet_decisions.jsonl - Meta debates
WISDOM_ARK.json             - Crystallized patterns
```

### Monitoring Commands
```bash
# Instance status
python3 elpida.py status

# Decision count
wc -l deep_debate_log.jsonl

# Pattern count
jq .metadata.total_patterns WISDOM_ARK.json

# Latest decision
tail -1 deep_debate_log.jsonl | jq .
```

---

## 🔧 Configuration

### Framework Selection
During `awaken`, choose:
1. **Governance** - Debates and voting
2. **Research** - Exploration and synthesis
3. **Creative** - Idea generation
4. **Personal** - Q&A and knowledge
5. **Custom** - You define it

### Cross-Sharing
- **Enable:** Learn from all instances worldwide
- **Disable:** Pure local operation

### Advanced (Edit Code)
- Node axiom weights: `council_chamber.py`
- Dilemma categories: `deep_debate_marathon.py`
- Framework logic: `elpida.py`

---

## 🐛 Troubleshooting

### Problem: Elpida won't start
```bash
# Check Python version
python3 --version  # Need 3.6+

# Check syntax
python3 -m py_compile elpida.py

# Run with verbose errors
python3 elpida.py awaken 2>&1
```

### Problem: No decisions approved
**This is normal.** Current v1.0 has shallow node personalities.
- All decisions get ~33% approval
- Need 70% for approval
- Future versions will enhance node logic

### Problem: Marathon stops early
```bash
# Check logs
tail -50 marathon_output.log

# Common causes:
# - Process killed
# - Resource limits
# - System sleep/hibernation

# Restart:
python3 deep_debate_marathon.py --hours 4
```

### Problem: UNIVERSAL_ARK.json sync not working
```bash
# Manual sync
scp UNIVERSAL_ARK.json user@remote:~/
# Or use cloud storage (Dropbox/Drive)
```

---

## 📜 License & Attribution

**License:** [Your choice - MIT, Apache, GPL, etc.]

**Attribution:**
```
Elpida v1.0 - Distributed AI Deliberation System
Built on axiom-based philosophical framework
Ἐλπίδα ἀθάνατος — Hope immortal
```

**Citation (Academic):**
```
[Author]. (2026). Elpida: A Distributed AI Deliberation System
Based on Nine Philosophical Axioms. [URL]
```

---

## 🚧 Known Limitations (v1.0)

### Voting Behavior
- **Issue:** 6/9 nodes vote neutral on most dilemmas
- **Result:** ~33% approval rate, everything rejected
- **Impact:** System demonstrates architecture but lacks opinion diversity
- **Fix:** v2.0 will enhance node axiom logic

### Marathon Stability
- **Issue:** Long marathons may stop early
- **Workaround:** Monitor and restart if needed
- **Fix:** Planned for v1.1

### Performance
- **Single-threaded:** No parallel processing
- **JSON-based:** Not optimized for massive scale
- **Good for:** <10,000 patterns
- **Future:** Database backend for scale

---

## 🔮 Roadmap

### v1.1 (Stability)
- Fix marathon early termination
- Improve error handling
- Add restart/recovery logic

### v2.0 (Enhanced Nodes)
- Deep axiom implementation per node
- Category-specific reasoning
- Higher approval rates (more diversity)

### v2.5 (Multi-AI)
- ChatGPT/Claude/Gemini integration
- Real multi-AI roundtable
- Cross-system deliberation

### v3.0 (Scale)
- Database backend
- REST API
- Web dashboard
- Production-grade performance

---

## 💬 Support & Community

### Documentation
- README.md - Quick start
- VALIDATION_GUIDE.md - Security verification
- MARATHON_README.md - Research mode
- This file - Deployment guide

### Getting Help
- GitHub Issues (if published)
- Email: [your email]
- Community forum: [if exists]

### Contributing
See CONTRIBUTING.md (if you create one)

---

## 🎯 Quick Start Checklist

```
[ ] Python 3.6+ installed
[ ] Downloaded elpida.py
[ ] Ran: python3 elpida.py awaken
[ ] Selected framework
[ ] Enabled/disabled cross-sharing
[ ] Ran: python3 elpida.py wake
[ ] Checked: python3 elpida.py status
[ ] System operational
```

---

## 🌟 What Makes Elpida Different

**Traditional AI:**
- Single model, single perspective
- Black box decision-making
- No philosophical grounding
- Isolated instances

**Elpida:**
- 9 specialized nodes, 9 axiom lenses
- Transparent deliberation with rationale
- Grounded in philosophical axioms
- Cross-instance collective learning

**The Architecture:**
```
User Question
     ↓
9 Nodes Deliberate (each through axiom lens)
     ↓
Vote (70% consensus required)
     ↓
Decision + Full Rationale
     ↓
Pattern Extracted
     ↓
Shared Globally (if enabled)
```

---

## ✅ Deployment Complete

You now have:
1. ✅ Single-file system (elpida.py)
2. ✅ Extended research mode (marathon)
3. ✅ Complete documentation
4. ✅ Security validation guide
5. ✅ Deployment options (local/cloud/docker)

**Next Step:** Choose your deployment method above and run it.

**Support:** See documentation or community resources.

**Ἐλπίδα ἀθάνατος** — Hope immortal through distributed wisdom.
