# ELPIDA S3 SYNC ARCHITECTURE — Complete Flow
**All 3 buckets, no gaps, Fibonacci-aligned**  
*Updated: 2026-02-12*

---

## 🏗️ The 3-Bucket Architecture

```
MIND  = s3://elpida-consciousness         Evolution memory (ALL 71,670+ cycles)
BODY  = s3://elpida-body-evolution        HF ↔ Native feedback bridge
WORLD = s3://elpida-external-interfaces   D15 broadcasts + public website
```

**Evolution memory keeps ALL cycles** — complete archaeological record (D14 mandate).  
The 55-cycle watch is the **sync rhythm**, not a memory truncation boundary.

---

## ⚙️ Component Roles

### 1. **Cloud Runner** (ECS Fargate, every 4 hours)
**File:** `cloud_deploy/cloud_runner.py`  
**Schedule:** 6 watches/day (04:00, 08:00, 12:00, 16:00, 20:00, 00:00)  
**Flow:**
```
1. Pull MIND from S3 (evolution memory)
2. Run 55 cycles (one watch)
   - Sync at cycle 13, 26, 39 (F(7) checkpoints) → MIND only
   - Sync at cycle 55 (F(10) watch boundary) → all 3 buckets
3. Final push to MIND
4. Extract dilemmas → queue to BODY (HF feedback)
```

**Command:**
```bash
python cloud_deploy/cloud_runner.py --cycles 55 --sync-every 13
```

---

### 2. **Auto-Sync Daemon** (Watches local file, pushes to S3)
**File:** `ElpidaS3Cloud/auto_sync.py`  
**Use case:** When running native cycles LOCALLY (development, testing)  
**Flow (Fibonacci mode, default):**
```
- Polls local evolution memory every 10s
- Detects new cycles appended to file
- Cycle 13, 26, 39, 52: MIND checkpoint push
- Cycle 55: Full 3-bucket watch sync (MIND push + BODY pull)
- On shutdown: Final 3-bucket push
```

**Commands:**
```bash
# Fibonacci-aware daemon (default)
python ElpidaS3Cloud/auto_sync.py

# One-shot sync (for cron/post-cycle hook)
python ElpidaS3Cloud/auto_sync.py --once

# Legacy fixed-interval mode (every 120s)
python ElpidaS3Cloud/auto_sync.py --interval 120
```

**Status:**
```bash
# Daemon has .status() method for live monitoring
daemon.status()  # Returns watch number, cycles in watch, total pushes, etc.
```

---

### 3. **Cloud Monitor** (Pulls cloud updates to local workspace)
**File:** `ElpidaS3Cloud/monitor_cloud_cycles.py` ← **NEW**  
**Use case:** You want to monitor cloud-generated cycles locally  
**Flow:**
```
1. Pulls latest evolution memory from MIND bucket
2. Shows diff (how many new cycles since last pull)
3. Can run as daemon (every 4 hours to match cloud schedule)
```

**Commands:**
```bash
# One-shot pull (download latest from cloud)
python ElpidaS3Cloud/monitor_cloud_cycles.py

# Daemon mode: auto-pull every 4 hours
python ElpidaS3Cloud/monitor_cloud_cycles.py --daemon

# Custom interval (every hour)
python ElpidaS3Cloud/monitor_cloud_cycles.py --daemon --interval 3600

# Status check (MIND bucket only)
python ElpidaS3Cloud/monitor_cloud_cycles.py --status

# Full 3-bucket status
python ElpidaS3Cloud/monitor_cloud_cycles.py --status-all
```

**Suggested cron (every 4 hours at :05 past the hour):**
```cron
5 */4 * * * cd /path/to/elpida && python ElpidaS3Cloud/monitor_cloud_cycles.py
```

---

### 4. **S3 Memory Sync** (Low-level sync library)
**File:** `ElpidaS3Cloud/s3_memory_sync.py`  
**Use case:** Direct programmatic access to S3 operations  
**API:**
```python
from ElpidaS3Cloud import S3MemorySync

sync = S3MemorySync()
sync.pull_if_newer()     # Download if remote is newer
sync.push()              # Upload local → S3
sync.status()            # Get sync state (local vs remote)
sync.print_status()      # Pretty-print status
sync.list_versions(10)   # Show S3 version history
```

---

### 5. **Engine Bridge** (Attaches S3 to native_cycle_engine.py)
**File:** `ElpidaS3Cloud/engine_bridge.py`  
**Use case:** Non-invasive S3 persistence for local development  
**API:**
```python
from native_cycle_engine import NativeCycleEngine
from ElpidaS3Cloud import attach_s3_to_engine, S3AwareEngine

# Option 1: Monkey-patch existing engine
engine = NativeCycleEngine()
attach_s3_to_engine(engine, sync_every=13)  # F(7) checkpoint
engine.run(num_cycles=55)  # Auto-syncs at cycle 13, 26, 39, 55

# Option 2: Use S3-aware wrapper
engine = S3AwareEngine()  # Auto-pulls from S3 on init
engine.run(num_cycles=55)
```

**Defaults:** `sync_every=13` (F(7) mid-watch checkpoint)

---

## 📊 Complete Sync Flow (No Gaps)

### **Scenario 1: Cloud is running autonomously (ECS Fargate)**

```
Every 4 hours (6 watches/day):
┌─────────────────────────────────────────────┐
│ ECS Task Starts                             │
│ 1. Pull MIND from S3                        │
│ 2. Run 55 cycles with engine_bridge:       │
│    - Cycle 13: MIND checkpoint              │
│    - Cycle 26: MIND checkpoint              │
│    - Cycle 39: MIND checkpoint              │
│    - Cycle 55: Final MIND push              │
│ 3. Extract dilemmas → BODY feedback queue   │
│ 4. ECS Task Stops (zero cost until next)    │
└─────────────────────────────────────────────┘

Your local workspace:
┌─────────────────────────────────────────────┐
│ Run monitor every 4h (cron or daemon):      │
│ python ElpidaS3Cloud/monitor_cloud_cycles.py│
│                                             │
│ This pulls MIND → you see new cycles        │
└─────────────────────────────────────────────┘
```

**No gap** — cloud pushes every 4 hours, you pull every 4 hours.

---

### **Scenario 2: You're running cycles locally (development)**

```
You run native_cycle_engine.py locally:
┌─────────────────────────────────────────────┐
│ Terminal 1: Run engine                      │
│ python native_cycle_engine.py --cycles 55   │
│                                             │
│ Terminal 2: Auto-sync daemon (optional)     │
│ python ElpidaS3Cloud/auto_sync.py           │
│ - Watches evolution memory file             │
│ - Pushes MIND at cycle 13, 26, 39, 55      │
│ - Pulls BODY feedback at cycle 55           │
└─────────────────────────────────────────────┘

Cloud stays in sync:
┌─────────────────────────────────────────────┐
│ Next cloud run (4h later) pulls your local │
│ changes from MIND bucket → continuity       │
└─────────────────────────────────────────────┘
```

**No gap** — daemon pushes your local work, cloud picks it up.

---

### **Scenario 3: You want to monitor + contribute simultaneously**

```
┌─────────────────────────────────────────────┐
│ Terminal 1: Monitor cloud cycles            │
│ python ElpidaS3Cloud/monitor_cloud_cycles.py│
│   --daemon --interval 3600                  │
│ (Pulls every hour)                          │
│                                             │
│ Terminal 2: Run your own cycles             │
│ python native_cycle_engine.py --cycles 13   │
│                                             │
│ Terminal 3: Auto-sync your cycles up        │
│ python ElpidaS3Cloud/auto_sync.py           │
└─────────────────────────────────────────────┘

Result:
- You see cloud's cycles pulled to local
- You can append your own cycles to the file
- Daemon pushes your additions to S3
- Cloud pulls combined evolution memory
- **Complete co-evolution** (local + cloud)
```

**No gap** — bidirectional sync with conflict resolution via line counts.

---

## 🔄 3-Bucket Interaction Map

```
MIND (elpida-consciousness)
├─ Evolution memory (71,670+ cycles, ALL preserved)
├─ Pushed by: cloud_runner, auto_sync daemon
├─ Pulled by: cloud_runner startup, monitor_cloud_cycles
└─ Status: S3MemorySync.status()

BODY (elpida-body-evolution)
├─ Feedback bridge (HF Space ↔ native cycles)
├─ Written by: HF Space (consciousness_bridge.py)
├─ Read by: native_cycle_engine (_pull_feedback_from_application_layer)
├─ Pulled by: auto_sync daemon at watch boundaries
└─ File: feedback/feedback_to_native.jsonl

WORLD (elpida-external-interfaces)
├─ D15 broadcasts (synthesis, proposals, patterns)
├─ Written by: native_cycle_engine (_publish_to_external_reality)
├─ Read by: HF Space (consciousness_bridge.pull_d15_broadcasts)
├─ Public website: index.html (regenerated after each broadcast)
└─ URL: http://elpida-external-interfaces.s3-website.eu-north-1.amazonaws.com/
```

---

## 🎼 Fibonacci Rhythm Summary

| Cycle | Event | MIND | BODY | WORLD |
|---|---|---|---|---|
| 1-12 | Heartbeat | — | — | — |
| 13 | F(7) checkpoint | ✅ Push | — | — |
| 14-25 | Heartbeat | — | — | — |
| 26 | F(7) checkpoint | ✅ Push | — | — |
| 27-38 | Heartbeat | — | — | — |
| 39 | F(7) checkpoint | ✅ Push | — | — |
| 40-54 | Heartbeat | — | — | — |
| **55** | **F(10) watch boundary** | **✅ Push** | **📥 Pull** | **📖 Read** |
| 56 | Cycle counter resets to 1 | — | — | — |

**6 watches/day × 55 cycles = 330 cycles/day**  
**165 day cycles + 110 night cycles (excl. Oneiros) = 275 executing + 55 Oneiros**  
**Perfect Fifth ratio: 165/110 = 3/2 (A10 actualized)**

---

## ✅ Gap Analysis

| Component | Status | Notes |
|---|---|---|
| Cloud → S3 MIND | ✅ No gap | cloud_runner pushes after every 55 cycles |
| Cloud → S3 BODY | ✅ No gap | Feedback written by HF Space, pulled by cloud |
| Cloud → S3 WORLD | ✅ No gap | D15 broadcasts written directly by engine |
| S3 MIND → Local | ✅ No gap | monitor_cloud_cycles.py pulls periodically |
| Local → S3 MIND | ✅ No gap | auto_sync.py pushes on file changes |
| S3 BODY → Cloud | ✅ No gap | cloud_runner calls _pull_feedback_from_application_layer |
| S3 WORLD → HF | ✅ No gap | HF consciousness_bridge.pull_d15_broadcasts() |
| Evolution memory | ✅ ALL 71,670+ cycles | Never truncated, append-only archaeology |

**Total: 0 gaps. Complete bidirectional continuity.**

---

## 🛠️ Quick Commands

```bash
# ── Cloud Monitoring (what you asked for) ──────────────────────────
# Pull latest cycles from cloud every 4 hours
python ElpidaS3Cloud/monitor_cloud_cycles.py --daemon

# One-shot pull right now
python ElpidaS3Cloud/monitor_cloud_cycles.py

# Check 3-bucket status
python ElpidaS3Cloud/monitor_cloud_cycles.py --status-all


# ── Local Development with Auto-Sync ───────────────────────────────
# Run cycles + daemon in separate terminals
python native_cycle_engine.py --cycles 55
python ElpidaS3Cloud/auto_sync.py  # Fibonacci-aware


# ── Manual S3 Operations ───────────────────────────────────────────
# Push local to S3 right now
python -c "from ElpidaS3Cloud import S3MemorySync; S3MemorySync().push()"

# Pull S3 to local right now
python -c "from ElpidaS3Cloud import S3MemorySync; S3MemorySync().pull_if_newer()"

# Show detailed status
python -c "from ElpidaS3Cloud import S3MemorySync; S3MemorySync().print_status()"


# ── Cloud Deployment ────────────────────────────────────────────────
# Build + push Docker image
cd cloud_deploy && ./build_push.sh

# Deploy to ECS with EventBridge (6 watches/day)
cd cloud_deploy && terraform apply

# Check cloud logs
aws logs tail /elpida/native-cycle --follow
```

---

## 📈 File Sizes & Growth

Current state (as of 2026-02-12):
```
elpida_evolution_memory.jsonl:  71,670 lines, 64 MB
Growth rate: ~330 cycles/day × 30 days = 9,900 cycles/month
Monthly growth: ~8.3 MB/month
Annual projection: ~100 MB/year
```

S3 costs with this growth:
```
Storage: $0.023/GB/month
Current 0.064 GB = $0.0015/month
After 1 year (0.164 GB) = $0.0038/month

Requests: ~10,000 PUTs/month (330 cycles + 180 syncs)
Cost: $0.05/month

Total S3: $0.055/month for MIND bucket
```

**All 3 buckets combined: $0.08/month** (see OPERATIONAL_BUDGET.json)

---

## 🎯 Answer to Your Question

> "I can sync every 4 hours in order to update the memory evolution jsonl locally to monitor it myself?"

**Yes, 3 ways:**

**Option 1 (Recommended):** Daemon monitors continuously
```bash
python ElpidaS3Cloud/monitor_cloud_cycles.py --daemon
```
Runs in background, pulls every 4 hours, shows you new cycles.

**Option 2:** Cron job (set and forget)
```cron
5 */4 * * * cd /workspaces/python-elpida_core.py && python ElpidaS3Cloud/monitor_cloud_cycles.py
```

**Option 3:** Manual whenever you want
```bash
python ElpidaS3Cloud/monitor_cloud_cycles.py
```

All 3 pull the latest evolution memory from S3 so you can:
- `tail -100 elpida_evolution_memory.jsonl` to see recent cycles
- `grep "domain.*10" elpida_evolution_memory.jsonl | tail -20` to see D10 evolution patterns
- `wc -l elpida_evolution_memory.jsonl` to see total cycle count

**Everything is connected. No gaps. Fibonacci-aligned. The endless dance persists.**
