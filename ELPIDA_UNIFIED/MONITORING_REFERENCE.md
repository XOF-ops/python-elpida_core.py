# ELPIDA MONITORING QUICK REFERENCE v2.0

## Status Monitor Commands

### Comprehensive Status (One-Time)
```bash
cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED
python3 monitor_comprehensive.py
```

Shows complete system status including:
- Parliament running status
- Synthesis engine performance (success rate, recent resolutions)
- ARK auto-update status (automatic vs manual updates)
- Phase 12→13 bridge health
- Dilemma processing stats
- Fleet communication activity
- File system status
- Overall health check (4 critical systems)

### Continuous Watch Mode
```bash
cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED
./watch_status.sh [interval]    # Default 30 seconds
```

Auto-refreshes status display every N seconds.

### Quick Checks

**Parliament Status:**
```bash
ps aux | grep parliament_continuous
```

**Recent Synthesis:**
```bash
tail -20 synthesis_resolutions.jsonl | jq '.synthesis.action'
```

**ARK Updates:**
```bash
cat ark_updates.jsonl | jq '{time: .timestamp, reason: .reason}'
```

**Live Parliament Logs:**
```bash
tail -f fleet_debate.log | grep -E "SYNTHESIS|ARK|CYCLE"
```

---

## Key Metrics Explained

### Synthesis Success Rate
- **100%**: Synthesis engine fixed and operational
- **<50%**: Indicates keyword matching issues (should be fixed)

### ARK Bridge Efficiency
- **100%**: ARK updating every 5 SEED_PROTOCOL syntheses as designed
- **<100%**: Some SEED_PROTOCOL syntheses not triggering ARK updates

### Overall System Health
Monitors 4 critical systems:
1. **Parliament Active**: Parliament process running
2. **Synthesis Engine**: Success rate > 50%
3. **ARK Auto-Update**: At least 1 automatic update logged
4. **Recent Activity**: Synthesis in last hour

**Health Status:**
- 🟢 **EXCELLENT** (100%): All systems operational
- 🟡 **GOOD** (75-99%): Minor issues
- 🟠 **DEGRADED** (50-74%): Multiple issues
- 🔴 **CRITICAL** (<50%): Needs immediate attention

---

## File Locations

All monitoring data in: `/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/`

**Key Files:**
- `synthesis_resolutions.jsonl` - All synthesis resolutions
- `ark_updates.jsonl` - ARK update audit trail
- `ELPIDA_ARK.md` - Current ARK state
- `dilemma_log.jsonl` - All dilemmas processed
- `fleet_debate.log` - Real-time parliament logs
- `fleet_dialogue.jsonl` - Inter-node communication

---

## Expected Values (Healthy System)

| Metric | Healthy Range |
|--------|--------------|
| Synthesis Success Rate | 90-100% |
| ARK Bridge Efficiency | 90-100% |
| Resolutions per Hour | 5-20 |
| SEED_PROTOCOL Count | 40-60% of total |
| ARK Updates | ~1 per 5 SEED syntheses |
| Parliament Uptime | Continuous |
| Fleet Messages (10min) | 50-200 |

---

## Troubleshooting

**Parliament Not Running:**
```bash
cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED
python3 parliament_continuous.py &
```

**Low Synthesis Success:**
Check for keyword matching issues in synthesis_engine.py methods.

**ARK Not Auto-Updating:**
1. Check ark_synthesis_bridge.py is imported
2. Verify SEED_PROTOCOL syntheses are being generated
3. Check threshold setting (default: 5)

**No Recent Activity:**
1. Check dilemma generator is running
2. Verify dilemma_log.jsonl has recent entries
3. Restart parliament if stuck

---

## Quick Status Commands

**One-liner health check:**
```bash
python3 -c "from monitor_comprehensive import ElpidaMonitor; m = ElpidaMonitor(); s = m.check_parliament_status(); sr = m.calculate_synthesis_success_rate(); print(f\"Parliament: {'✅' if s['running'] else '❌'} | Synthesis: {sr['rate']:.0f}%\")"
```

**Count recent syntheses:**
```bash
jq -s '. | length' synthesis_resolutions.jsonl
```

**Latest ARK version:**
```bash
head -1 ELPIDA_ARK.md
```

**Active processes:**
```bash
ps aux | grep -E "parliament|elpida" | grep -v grep
```

---

*Ἐλπίδα ζωή.* (Hope lives.)
