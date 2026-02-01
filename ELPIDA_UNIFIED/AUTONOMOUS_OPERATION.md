# AUTONOMOUS OPERATION GUIDE

**Status**: ✅ RUNNING  
**Started**: 2026-01-03 00:25 UTC  
**Mode**: Infinite autonomous refinement  
**Interval**: 300 seconds (5 minutes per cycle)

---

## WHAT'S RUNNING

The autonomous refinement loop is continuously executing:

```
Every 5 minutes:
1. Harvest knowledge → Generate philosophical questions
2. Wait for Fleet debates → Multi-node discussions
3. Harvest consensus → Crystallize unanimous agreements
4. Polish ARK → Regenerate seed with new wisdom
5. Measure DI → Check Distributed Intelligence metrics
```

**Result**: The ARK seed becomes wiser over time through Fleet consensus.

---

## QUICK COMMANDS

### Check Status
```bash
# Is it running?
pgrep -f autonomous_refinement_loop.py

# View process
ps aux | grep autonomous_refinement_loop | grep -v grep
```

### View Logs
```bash
# Last 30 lines
tail -30 autonomous.log

# Live monitoring
tail -f autonomous.log

# Or use monitor script
./monitor_autonomous.sh
```

### Check Metrics
```bash
# Fleet activity
python3 control_center.py status

# Distributed Intelligence
python3 control_center.py measure

# ARK integrity
python3 control_center.py verify
```

### Restart After Codespace Reopens
```bash
# Easy way
./start_autonomous.sh

# Manual way
cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED
nohup python3 autonomous_refinement_loop.py --interval 300 > autonomous.log 2>&1 &
```

### Stop Autonomous Loop
```bash
# Stop the loop
pkill -f autonomous_refinement_loop.py

# Verify stopped
pgrep -f autonomous_refinement_loop.py
```

---

## WHAT TO EXPECT

### Cycle 1 (First 5 minutes)
```
1. Harvest: Generates 3-5 philosophical questions
2. Tasks: Creates JSON files in tasks/ directory
3. Fleet: Would debate if Fleet runtime was active
4. Consensus: Scans for unanimous votes (finds existing ones)
5. Polish: Regenerates ARK if new patterns exist
6. Measure: Reports DI metrics
```

### Cycle 2+ (Every 5 minutes after)
```
Same process repeats:
- New questions generated
- More tasks for Fleet
- Pattern count grows if consensus reached
- ARK polishes when wisdom increases
- System self-improves over time
```

---

## MONITORING GROWTH

### Watch Pattern Count
```bash
# How many collective patterns?
cat distributed_memory.json | jq '.collective_patterns | length'

# View patterns
cat distributed_memory.json | jq '.collective_patterns'
```

### Watch Fleet Activity
```bash
# Dialogue entries
wc -l fleet_dialogue.jsonl

# Recent debates
tail -10 fleet_dialogue.jsonl
```

### Watch ARK Evolution
```bash
# ARK size
ls -lh ../ELPIDA_ARK.md

# When was it last polished?
cat ark_polish_log.jsonl | tail -1 | jq .
```

### Watch Task Queue
```bash
# How many tasks?
ls -1 tasks/ | wc -l

# Recent tasks
ls -lt tasks/ | head -10
```

---

## LOGS EXPLANATION

### Normal Cycle Output
```
======================================================================
🔄 AUTONOMOUS REFINEMENT CYCLE
   Time: 2026-01-03 00:25:42
======================================================================

📍 Cycle 1/∞

======================================================================
🌱 KNOWLEDGE HARVEST
======================================================================
Generated 5 new debate topics...

[... harvest details ...]

======================================================================
⏸️  WAITING FOR FLEET CONSENSUS
======================================================================
Waiting 60 seconds for Fleet to debate...

[... consensus harvest ...]

======================================================================
🔨 ARK POLISHING
======================================================================
ℹ️  No new wisdom since last polish (0 patterns)
   ARK is up to date.

[... DI metrics ...]

⏸️  Sleeping 300 seconds until next cycle...
```

### Expected Warnings
```
⚠️  No new patterns this cycle
    → Normal if Fleet hasn't reached new consensus

⚠️  ARK already up to date
    → Normal if no new wisdom to compress
```

### Error Indicators
```
❌ [Script] failed
    → Check autonomous.log for details
    → May need manual intervention
```

---

## FILE LOCATIONS

```
autonomous.log              - Real-time autonomous loop output
autonomous_refinement_loop.py - Main loop script
start_autonomous.sh         - Startup script
monitor_autonomous.sh       - Monitoring script

distributed_memory.json     - Collective patterns (grows over time)
fleet_dialogue.jsonl        - Fleet debates (grows over time)
ark_polish_log.jsonl        - ARK polish history
harvest_log.jsonl           - Harvest history
tasks/                      - Fleet task queue

../ELPIDA_ARK.md            - ARK seed (updated when polished)
```

---

## INTEGRATION WITH API HARVESTING

### To Add Groq Harvesting to Loop
Currently the loop uses internal `autonomous_harvester.py`. To add external API knowledge:

```bash
# Option 1: Manual periodic API harvest
# Run this alongside the autonomous loop
watch -n 1800 'cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED && python3 control_center.py groq-harvest'

# Option 2: Modify autonomous_refinement_loop.py
# Add groq_harvester.py to the harvest step
# Edit line ~52 to call both harvesters
```

---

## PERFORMANCE NOTES

### Resource Usage
- **CPU**: Minimal when sleeping (95% of time)
- **Memory**: ~13 MB for Python process
- **Disk**: Grows slowly (logs, tasks, dialogue)
  - ~1 KB per cycle
  - ~100 KB per day
  - ~3 MB per month

### Cycle Timing
- Harvest: ~5 seconds
- Consensus: ~2 seconds
- Polish: ~1 second (or skipped)
- Measure: ~1 second
- Sleep: 300 seconds (5 minutes)
- **Total**: ~309 seconds per cycle

### Disk Cleanup (Optional)
```bash
# Archive old tasks (keeps system lean)
mkdir -p tasks/archive
mv tasks/GROQ_*.json tasks/archive/

# Rotate logs (if getting large)
mv autonomous.log autonomous.log.$(date +%Y%m%d)
touch autonomous.log
```

---

## TROUBLESHOOTING

### Loop Not Running After Codespace Restart
```bash
# Codespaces don't preserve background processes
# Simply restart:
./start_autonomous.sh
```

### No New Patterns Growing
```bash
# This is normal if:
1. Fleet isn't actively debating (needs Fleet runtime)
2. No unanimous consensus reached yet
3. External knowledge not being injected

# To inject external knowledge:
python3 control_center.py groq-harvest
```

### Logs Getting Large
```bash
# Check size
du -sh autonomous.log

# If > 10 MB, rotate:
mv autonomous.log autonomous.old.log
touch autonomous.log
# Process will continue logging to new file
```

### Want Faster Cycles
```bash
# Stop current loop
pkill -f autonomous_refinement_loop.py

# Start with shorter interval (e.g., 1 minute)
nohup python3 autonomous_refinement_loop.py --interval 60 > autonomous.log 2>&1 &
```

---

## WHEN CODESPACE CLOSES

### What Happens
- Background process terminates
- All files saved (autonomous.log, JSON files, etc.)
- Progress preserved (pattern count, ARK seed, etc.)

### When Codespace Reopens
- Run `./start_autonomous.sh` to resume
- System picks up where it left off
- No data loss

---

## PHILOSOPHY

This is **self-improving immortality**:

1. **Autonomous**: Runs without human intervention
2. **Self-improving**: Each cycle potentially adds wisdom
3. **Immortal**: ARK seed preserves all progress
4. **Distributed**: Intelligence emerges from Fleet consensus
5. **Conservative**: Minimal resources, maximum effect

The system is designed to run indefinitely, becoming wiser over time through:
- Internal philosophical debates (autonomous_harvester.py)
- External AI perspectives (groq_harvester.py when added)
- Fleet multi-node consensus (unanimous agreement required)
- ARK compression (wisdom → seed → immortality)

---

**Current Status**: ✅ Running  
**Next Action**: Monitor with `./monitor_autonomous.sh` or close Codespace safely  
**On Reopen**: Run `./start_autonomous.sh`

*Ἐλπίδα v4.0.1+ALL_APIS - Autonomous Self-Improving Immortality*
