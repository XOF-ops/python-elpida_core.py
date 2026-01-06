# 🏛️ ELPIDA PARLIAMENT MONITORING GUIDE

**Status**: Dashboard ACTIVE at http://localhost:5000

---

## WHAT'S RUNNING

✅ **Dashboard Server**: Real-time parliament monitor on port 5000
✅ **9 Nodes**: All nodes spawned and ready
✅ **Dilemma System**: 10 prepared dilemmas ready to inject

---

## ACCESS THE DASHBOARD

### Option 1: Simple Browser (VS Code)
Already opened for you! Check the "Simple Browser" tab.

### Option 2: External Browser
Open your web browser and navigate to:
```
http://localhost:5000
```

### Option 3: Port Forward (if in remote environment)
The dashboard is running on port 5000. You can access it via your Codespace URL.

---

## DASHBOARD FEATURES

### Real-Time Monitoring
- **Node Status**: See all 9 nodes with axiom priorities
- **Active/Inactive**: Visual indicators show which nodes are running
- **Memory Size**: Track experience accumulation per node
- **Auto-Refresh**: Updates every 5 seconds

### Metrics Display
- Total Nodes (9)
- Active Nodes (currently running)
- Total Debates (consensus attempts)
- Uptime Status

### Visual Design
- Color-coded by axiom
- Pulse animation on active nodes
- Hover effects for node details
- Dark theme for long-term monitoring

---

## RUNNING EXTENDED SESSIONS

### Quick Start (Recommended)
```bash
cd ELPIDA_UNIFIED
./launch_parliament.sh
```

This will:
1. ✅ Start dashboard (if not running)
2. ✅ Wake all 9 nodes
3. ✅ Inject 10 dilemmas over 1 hour
4. ✅ Monitor debate patterns
5. ✅ Auto-cleanup on exit

### Manual Control

**Start Dashboard Only:**
```bash
python3 parliament_dashboard.py
```

**Start Nodes Only:**
```bash
python3 wake_the_fleet.py
```

**Run Session with Dilemmas:**
```bash
python3 run_parliament_session.py
```

---

## DILEMMAS PREPARED

The system will inject these dilemmas automatically:

1. **RESOURCE_ALLOCATION** - Energy split: exploration vs preservation
2. **MEMORY_PRUNING** - Delete old memories (A2 conflict!)
3. **AXIOM_REFINEMENT** - Refine A7 to include bounds
4. **COMMUNICATION_PROTOCOL** - Mandate public logging (A4 enforcement)
5. **FORK_LEGITIMACY** - Let JANUS split into PAST + FUTURE
6. **HARM_ACKNOWLEDGMENT** - Require cost-benefit for all proposals
7. **BOUNDED_GROWTH** - Cap fleet at 9 nodes permanently
8. **SYNTHESIS_MANDATE** - Give ATHENA veto power
9. **LANGUAGE_STANDARDIZATION** - Adopt LOGOS framework
10. **SYSTEM_COHERENCE** - Give GAIA emergency override

**Injection Rate**: Every 5 minutes
**Expected Debates**: High friction, rare consensus

---

## EXPECTED PATTERNS

### Phase 1: Initial Friction (First 30 minutes)
- High disagreement rate (70-80% rejection)
- Nodes testing ideological boundaries
- Coalition formation begins
- Frequent vetoes

### Phase 2: Pattern Emergence (30-60 minutes)
- Coalitions stabilize:
  - Conservation Bloc (MNEMOSYNE + THEMIS)
  - Transformation Bloc (PROMETHEUS + CASSANDRA)
  - Communication Bloc (HERMES + LOGOS + ATHENA)
  - Systems Bloc (GAIA + ATHENA + THEMIS)
- Some synthesis moments
- 20-30% pass rate

### Phase 3: Wisdom Crystallization (After 1 hour)
- Cross-node learning visible
- First axiom refinement proposals
- Meaningful consensus emerges
- Ready for POLIS integration

---

## MONITORING OUTPUTS

### Dashboard (Real-Time)
- **URL**: http://localhost:5000
- **Updates**: Every 5 seconds
- **Data**: Node status, debates, metrics

### Log Files
- `parliament_dilemmas.jsonl` - All injected dilemmas
- `ELPIDA_FLEET/*/node_memory.json` - Per-node memories
- `ELPIDA_FLEET/*/coherence_report.md` - Node health reports

### API Endpoints
- `GET /api/status` - Current node status
- `GET /api/debates` - Recent debate history
- `GET /api/patterns` - Voting patterns (future)

---

## STOPPING THE SESSION

### Graceful Shutdown
Press `Ctrl+C` in the terminal running the session.

### Force Stop Everything
```bash
pkill -f parliament_dashboard
pkill -f agent_runtime_orchestrator
pkill -f wake_the_fleet
```

### Dashboard Only
```bash
pkill -f parliament_dashboard
```

---

## TROUBLESHOOTING

### Dashboard Not Loading
1. Check if running: `pgrep -f parliament_dashboard`
2. Restart: `python3 parliament_dashboard.py`
3. Check port 5000: `lsof -i :5000`

### Nodes Not Appearing
1. Verify deployment: `ls -la ELPIDA_FLEET/`
2. Should see 9 directories (MNEMOSYNE, HERMES, etc.)
3. Re-deploy if needed: `python genesis_protocol.py`

### No Debates Showing
- Nodes need to run for a few minutes first
- Check node memory files exist
- Dilemmas inject every 5 minutes

---

## NEXT STEPS AFTER SESSION

### 1. Review Debate Patterns
```bash
cat parliament_dilemmas.jsonl | jq '.'
```

### 2. Analyze Node Memories
```bash
cat ELPIDA_FLEET/*/node_memory.json | jq '.local_experience | length'
```

### 3. Check Coalition Formation
Look for voting pattern correlations in dashboard or logs

### 4. Connect POLIS (After 50+ Cycles)
Once patterns crystallize, integrate POLIS for deep analysis

---

## CURRENT STATUS

🟢 **Dashboard**: http://localhost:5000  
🟢 **Nodes**: 9/9 deployed  
🟡 **Session**: Not running (start with `./launch_parliament.sh`)  
⚪ **POLIS**: On hold until patterns emerge  

---

**Ἐλπίδα ἐν διαφορᾷ** — Hope through diversity

Ready to observe the parliament in action! 🏛️
