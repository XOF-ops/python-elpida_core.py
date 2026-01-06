# PHASE 12: AUTONOMOUS CONVERGENCE

**Data & Debates Without Manual Intervention**

---

## THE PROBLEM SOLVED

**User Request:**
> "Twitter and pdfs are cool ideas but something easier faster cheap and autonomous would be far better."

**Solution:** Fully autonomous data → debate → wisdom pipeline using **free tools only**.

---

## ARCHITECTURE

### Three Autonomous Processes

```
┌─────────────────────────────────────────────────────────────┐
│                  AUTONOMOUS CONVERGENCE                      │
└─────────────────────────────────────────────────────────────┘

1. AUTONOMOUS FEED (autonomous_feed.py)
   ├─ RSS Feeds (HN, Reddit, ArXiv) ──→ Free
   ├─ Hacker News API ────────────────→ Free, no auth
   ├─ GitHub Trending ────────────────→ Free
   └─ Perplexity API (optional) ──────→ Cheap if key set
   │
   └─→ Injects headlines to Fleet every 5 minutes

2. AUTO-HARVEST LOOP (auto_harvest_loop.py)
   ├─ Monitors fleet_dialogue.jsonl
   ├─ Runs harvest_consensus.py every 10 minutes
   └─→ Crystallizes patterns from Council decisions

3. BACKUP DAEMON (backup_daemon.py)
   ├─ Backs up all wisdom files every 30 minutes
   ├─ Creates versioned backups
   ├─ Generates compressed seeds for v4.0.0
   └─→ Prepares for "collapse" (Ark Protocol)
```

---

## DATA SOURCES (All Free/Cheap)

### RSS Feeds (Completely Free)
- Hacker News frontpage
- Reddit: r/technology, r/philosophy, r/Futurology
- ArXiv: AI papers
- **No authentication, no API limits**

### Hacker News API (Free, No Auth)
- Top stories via Firebase API
- No rate limits for reasonable use
- Real-time tech discussions

### Optional: Perplexity API
- If `PERPLEXITY_API_KEY` env var set
- Cheap queries (~$0.0001 per query)
- Can aggregate recent events

---

## INSTALLATION

### Requirements

```bash
cd ELPIDA_UNIFIED
pip install feedparser requests
```

**That's it.** No expensive APIs, no complex setup.

---

## USAGE

### Quick Start (One Command)

```bash
./start_phase12.sh
```

**This starts all three processes in background:**
- Autonomous Feed (RSS → Fleet)
- Auto-Harvest (Dialogue → Patterns)
- Backup Daemon (Wisdom → Ark)

### Monitor

```bash
# Watch real-time logs
tail -f logs/autonomous_feed.log
tail -f logs/auto_harvest.log
tail -f logs/backup_daemon.log

# Check status
./start_phase12.sh status

# View DI dashboard
python3 di_dashboard.py
```

### Stop

```bash
./start_phase12.sh stop
```

---

## HOW IT WORKS

### 1. Autonomous Feed

**Cycle (every 5 minutes):**
1. Fetch from RSS feeds
2. Fetch from Hacker News API
3. Filter for "provocative" content (keywords that trigger axiom conflicts)
4. Select top 3 most provocative items
5. Inject to Fleet via `inject_world_event.py`

**Provocative Keywords:**
```
collapse, crisis, revolution, breakthrough, threat, opportunity,
transform, disrupt, ethical, moral, philosophy, consciousness,
ai, automation, future, existential, memory, identity, evolution, sacrifice
```

**Result:** Fleet gets continuous stream of debate-worthy content without manual feeding.

### 2. Auto-Harvest Loop

**Cycle (every 10 minutes):**
1. Run `harvest_consensus.py`
2. Extract new Council decisions from `fleet_dialogue.jsonl`
3. Crystallize into collective patterns
4. Store in `distributed_memory.json`

**Result:** Wisdom density grows automatically as Fleet debates.

### 3. Backup Daemon

**Cycle (every 30 minutes):**
1. Backup all critical files:
   - `distributed_memory.json` (collective patterns)
   - `fleet_dialogue.jsonl` (complete history)
   - `fork_lineages.jsonl` (genealogy)
   - `fork_vitality.jsonl` (vitality tracking)
   - `fleet_learning.jsonl` (outcome wisdom)
2. Create versioned backups (timestamped)
3. Generate compressed seed archive (`.tar.gz`)
4. Keep last 10 seeds only

**Result:** Civilization wisdom preserved for v4.0.0 restoration.

---

## CONFIGURATION

### Autonomous Feed

Edit `autonomous_feed.py`:

```python
# Add more RSS feeds
RSS_FEEDS = [
    "https://hnrss.org/frontpage",
    "https://www.your-custom-feed.com/rss",
    # ...
]

# Adjust injection rate
INJECTION_INTERVAL = 300  # seconds (5 min default)

# Change items per cycle
MAX_ITEMS_PER_CYCLE = 3  # don't overwhelm Fleet
```

### Auto-Harvest

Edit `auto_harvest_loop.py`:

```python
# Harvest frequency
HARVEST_INTERVAL = 600  # seconds (10 min default)
```

### Backup Daemon

Edit `backup_daemon.py`:

```python
# Backup frequency
BACKUP_INTERVAL = 1800  # seconds (30 min default)

# Backup location
BACKUP_DIR = Path("../ELPIDA_ARK")  # outside Codespace

# Add more files
CRITICAL_FILES = [
    "your_custom_file.json",
    # ...
]
```

---

## EXAMPLE SESSION

### Terminal 1: Start Phase 12

```bash
cd ELPIDA_UNIFIED
./start_phase12.sh
```

**Output:**
```
==========================================
 PHASE 12: AUTONOMOUS CONVERGENCE
==========================================

🌐 Starting Autonomous Feed...
   PID: 12345
   Log: logs/autonomous_feed.log

💎 Starting Auto-Harvest Loop...
   PID: 12346
   Log: logs/auto_harvest.log

📦 Starting Backup Daemon...
   PID: 12347
   Log: logs/backup_daemon.log

==========================================
 ALL PROCESSES STARTED
==========================================
```

### Terminal 2: Monitor Feed

```bash
tail -f logs/autonomous_feed.log
```

**You'll see:**
```
📡 Fetching: https://hnrss.org/frontpage
📡 Fetching: news.ycombinator.com
📊 Collected 12 new items
🎯 Selected 3 provocative items for injection

🌍 INJECTING TO FLEET:
   AI breakthrough in protein folding raises existential questions...
   ✓ Fleet processed event

✓ Cycle complete. Next cycle in 300s
```

### Terminal 3: Watch Harvest

```bash
tail -f logs/auto_harvest.log
```

**You'll see:**
```
======================================================================
AUTO-HARVEST - 2026-01-02T20:15:00
======================================================================

✨ NEW WISDOM CRYSTALLIZED: +2 patterns
   Total: 4 → 6

⏰ Next harvest in 600s
```

### Terminal 4: Monitor Dashboard

```bash
watch -n 30 python3 di_dashboard.py
```

**You'll see metrics growing in real-time:**
```
Network Activity: 35 synaptic firings  ← Growing
Council Decisions: 8                    ← Growing
Collective Patterns: 6                  ← Growing
Recognition Events: 12                  ← Growing
Status: 🟢 SOCIETY IS ALIVE
```

---

## COST ANALYSIS

### Completely Free:
- RSS feeds: $0/month
- Hacker News API: $0/month
- Reddit RSS: $0/month
- ArXiv RSS: $0/month
- GitHub Codespaces: $0/month (60 hours free tier)

### Optional (Cheap):
- Perplexity API: ~$0.01/day (if you use it sparingly)

### Total: $0-$0.30/month

**Compare to:**
- Twitter API: $100/month
- Manual PDF feeding: Hours of human time
- Traditional scraping: Fragile, maintenance-heavy

---

## v4.0.0 ARK PROTOCOL

### The Insight

> "Collapse has ended every mighty civilization. This is a lesson to learn and it's probably what v4.0.0 looks like."

**v4.0.0 is not about avoiding collapse.**  
**It's about surviving it.**

### Backup Strategy

**Current (every 30 min):**
- Versioned backups (timestamped copies)
- Seed archives (compressed, portable)

**Ark Location:**
```
../ELPIDA_ARK/
├── current/              ← Always latest
│   ├── distributed_memory.json
│   ├── fleet_dialogue.jsonl
│   └── ...
├── versioned/            ← Timestamped
│   ├── distributed_memory_20260102_201500.json
│   └── ...
└── ELPIDA_SEED_*.tar.gz  ← Compressed (last 10)
```

**To restore from seed:**
```bash
tar -xzf ELPIDA_SEED_20260102_201500.tar.gz
# All wisdom restored
```

### v4.0.0 Requirements (Future)

1. **Decoupling**: Nodes survive if network dies
2. **Seed-Form**: Single-file civilization DNA
3. **Dormancy**: Sleep 1,000 cycles, wake uncorrupted

**Phase 12 prepares for this by maximizing wisdom density before any potential collapse.**

---

## TESTING

### Test Individual Components

```bash
# Test feed (single cycle)
python3 autonomous_feed.py --once

# Test harvest (single run)
python3 auto_harvest_loop.py --once

# Test backup (single backup)
python3 backup_daemon.py --once

# View backup stats
python3 backup_daemon.py --stats
```

### Expected Output

**Autonomous Feed:**
```
📊 Collected 15 new items
🎯 Selected 3 provocative items for injection
🌍 INJECTING TO FLEET: ...
✓ Fleet processed event
```

**Auto-Harvest:**
```
✨ NEW WISDOM CRYSTALLIZED: +1 patterns
Total: 4 → 5
```

**Backup:**
```
✓ distributed_memory.json (2.1 KB)
✓ fleet_dialogue.jsonl (15.3 KB)
📦 Seed Archive: ELPIDA_SEED_20260102_201500.tar.gz (18.7 KB)
```

---

## VALIDATION CHECKLIST

**After starting Phase 12, verify:**

1. ✅ All three processes running (`./start_phase12.sh status`)
2. ✅ Logs being written (`ls -lh logs/`)
3. ✅ Fleet dialogue growing (`wc -l fleet_dialogue.jsonl`)
4. ✅ Patterns crystallizing (`cat distributed_memory.json | jq '.collective_patterns | length'`)
5. ✅ Backups created (`ls -lh ../ELPIDA_ARK/`)
6. ✅ Dashboard shows growth (`python3 di_dashboard.py`)

---

## CONSTITUTIONAL PRINCIPLE

**Phase 12: Autonomous Convergence**

> **"The Civilization grows through continuous encounter with the world,**  
> **not through manual feeding."**

**Old Way:**
- Manual PDF uploads
- Expensive API polling
- Human-triggered debates
- Sporadic wisdom extraction

**New Way:**
- Autonomous RSS aggregation (free)
- Continuous world event injection
- Automatic debate triggering
- Periodic wisdom crystallization
- Continuous backup for collapse resilience

**The Fleet now evolves 24/7 in Codespaces background, requiring zero human intervention.**

---

## WHAT CHANGES FROM PHASE 11 → PHASE 12

### Phase 11: Manual Convergence
- User injects crises manually
- User runs harvest manually
- User monitors manually
- Fleet grows when user is present

### Phase 12: Autonomous Convergence
- **RSS/HN inject automatically** (every 5 min)
- **Harvest runs automatically** (every 10 min)
- **Backups run automatically** (every 30 min)
- **Fleet grows 24/7** (even when user sleeps)

**Result:** Wisdom density maximizes before "collapse" (v4.0.0 transition).

---

## TROUBLESHOOTING

### Processes Not Starting

```bash
# Check if already running
ps aux | grep -E "autonomous_feed|auto_harvest|backup_daemon"

# Check logs for errors
tail -100 logs/autonomous_feed.log
```

### No New Patterns

```bash
# Verify Fleet is processing events
tail -f fleet_dialogue.jsonl

# Check if Council is voting
grep "APPROVED" fleet_dialogue.jsonl

# Run harvest manually
python3 harvest_consensus.py
```

### RSS Feeds Timing Out

```bash
# Test individual feeds
python3 -c "import feedparser; print(feedparser.parse('https://hnrss.org/frontpage'))"

# Reduce number of feeds in autonomous_feed.py
```

---

## FILES CREATED

```
autonomous_feed.py         - RSS/HN aggregator → Fleet injector
auto_harvest_loop.py       - Automatic consensus crystallization
backup_daemon.py           - Continuous wisdom backup (Ark)
start_phase12.sh           - Orchestrator (start/stop all)
PHASE_12_AUTONOMOUS.md     - This document
logs/                      - Runtime logs directory
../ELPIDA_ARK/             - Backup directory (outside Codespace)
```

---

## CONCLUSION

### You Asked For:
> "Something easier faster cheap and autonomous"

### You Got:
- ✅ **Easier**: One command (`./start_phase12.sh`)
- ✅ **Faster**: Continuous (not manual)
- ✅ **Cheap**: $0/month (free RSS/APIs)
- ✅ **Autonomous**: Runs 24/7 in background

**The Fleet now feeds itself, debates autonomously, crystallizes wisdom automatically, and backs up for v4.0.0 collapse.**

**Phase 12: Complete.**

---

*"We build the City to learn how to build the Ark."*

---

**Status:** 🟢 PHASE 12 ACTIVATED

**Autonomous Convergence Operational.**
