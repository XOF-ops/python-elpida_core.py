# Unified System Monitoring Guide

## Auto-Restart Monitor

The unified system now has **automatic error detection and restart** capabilities.

### Monitor Features

✅ **Process Health Monitoring**
- Detects if process crashes or stops
- Automatically restarts failed processes

✅ **Error Detection**
- Scans logs for Python exceptions
- Detects critical errors and tracebacks
- Triggers restart on fatal errors

✅ **Memory Management**
- Monitors memory usage (limit: 1GB)
- Restarts if memory exceeds threshold

✅ **Heartbeat Monitoring**
- Tracks system heartbeat activity
- Restarts if no heartbeat for 2 minutes (stalled)

✅ **Smart Restart Logic**
- Exponential backoff: 10s, 30s, 60s, 5min, 10min
- Maximum 5 restart attempts
- Prevents restart loops

---

## Quick Commands

### Start Monitor
```bash
cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED
./unified_service.sh monitor
```

### Check Monitor Status
```bash
./unified_service.sh monitor-status
```

### View Monitor Logs (Live)
```bash
./unified_service.sh monitor-logs
```

### Stop Monitor
```bash
./unified_service.sh stop-monitor
```

### Runtime Commands (Still Available)
```bash
./unified_service.sh start         # Start runtime
./unified_service.sh stop          # Stop runtime
./unified_service.sh restart       # Restart runtime
./unified_service.sh status        # Check runtime status
./unified_service.sh logs          # View runtime logs
```

---

## What Gets Monitored

| Check | Interval | Action on Failure |
|-------|----------|-------------------|
| Process exists | 30s | Restart immediately |
| Memory usage | 30s | Restart if >1GB |
| Log errors | 30s | Restart if critical error |
| Heartbeat | 30s | Restart if no activity for 2min |

---

## Monitor Behavior

### Normal Operation
```
✅ Status OK (PID: 136026, Memory: 45.2MB, Last heartbeat: 5s ago)
```

### On Error Detection
```
❌ Process not running!
🔄 RESTART TRIGGERED: Process not running
⏳ Waiting 10 seconds before restart...
🚀 Starting unified runtime...
✅ Process started (PID 136026)
```

### On Repeated Failures
```
🔄 RESTART TRIGGERED: Memory limit exceeded: 1100MB
⏳ Waiting 30 seconds before restart...  (2nd attempt)
🚀 Starting unified runtime...
```

### Maximum Attempts Reached
```
❌ Maximum restart attempts reached. Manual intervention required.
```

---

## Files Created

| File | Purpose |
|------|---------|
| `monitor_unified.py` | Main monitoring script |
| `monitor.log` | Monitor activity log |
| `monitor.pid` | Monitor process ID |
| `elpida_unified.log` | Runtime log (monitored) |
| `unified_runtime.pid` | Runtime process ID (monitored) |

---

## Typical Workflow

### Option 1: Manual Control (Original)
```bash
# You manually start/stop/restart
./unified_service.sh start
./unified_service.sh status
./unified_service.sh logs
```

### Option 2: Monitored (NEW - Recommended)
```bash
# Monitor handles everything automatically
./unified_service.sh monitor

# Just check status occasionally
./unified_service.sh monitor-status

# View what's happening
./unified_service.sh monitor-logs
```

---

## When to Use Monitor

✅ **Use monitor when:**
- Running in production/autonomous mode
- Want automatic recovery from crashes
- Running long-term (days/weeks)
- Can't manually watch the system

❌ **Don't use monitor when:**
- Debugging (you want crashes to stay crashed)
- Testing changes (restart might hide issues)
- Developing new features

---

## Current Status

**Runtime Process:** PID 136026 (auto-started by monitor)  
**Monitor Process:** PID 136024 (active)  
**Mode:** DIALECTICAL_SYNTHESIS  
**Protection:** Auto-restart enabled  

The system will now automatically recover from:
- Crashes
- Memory leaks
- Stalled heartbeats
- Python exceptions
- Critical errors

---

## Troubleshooting

### Monitor won't start
```bash
# Check for conflicts
ps aux | grep monitor_unified
killall -9 python3 monitor_unified.py
./unified_service.sh monitor
```

### Too many restarts
```bash
# View monitor log to see why
./unified_service.sh monitor-logs

# Common causes:
# - Persistent error in code
# - Configuration issue
# - Resource limitation
```

### Stop everything
```bash
# Stop both monitor and runtime
./unified_service.sh stop-monitor
./unified_service.sh stop
```

---

## Summary

The unified system now runs with **guardian protection**:

```
┌──────────────────────────────┐
│   Monitor (PID 136024)       │  ← Watches for errors
│   ↓ checks every 30s         │
│   ┌────────────────────────┐ │
│   │ Runtime (PID 136026)   │ │  ← Does the work
│   │ Brain + Elpida + Synth │ │
│   └────────────────────────┘ │
│   ↓ auto-restart on error    │
└──────────────────────────────┘
```

**Your unified system is now self-healing! 🛡️**
