# DEEP DEBATE MARATHON

## Quick Start (AFK Mode)

```bash
./run_marathon_afk.sh
```

This launches an 8-hour integrated session with:
- ✅ Fleet nodes running continuously
- ✅ Dilemmas injected every 5-15 minutes
- ✅ **Real council voting** on every dilemma
- ✅ Wisdom extraction every 30 minutes
- ✅ All debates, voting, and integration in ONE run

## Manual Control

### Default (8 hours)
```bash
python3 deep_debate_marathon.py
```

### Custom duration
```bash
python3 deep_debate_marathon.py --hours 12      # 12-hour marathon
python3 deep_debate_marathon.py --hours 0.5     # 30-minute test
```

### Adjust dilemma frequency
```bash
python3 deep_debate_marathon.py --hours 4 --dilemma-min 3 --dilemma-max 8
# More frequent dilemmas (every 3-8 min instead of 5-15 min)
```

### Test mode (single dilemma)
```bash
python3 deep_debate_marathon.py --test
```

## What Happens

### Every 5-15 Minutes: DILEMMA INJECTION
```
[12:34:56] ⏰ DILEMMA CYCLE 15

────────────────────────────────────────────────────────────────────────
📜 DILEMMA SUBMITTED TO COUNCIL
────────────────────────────────────────────────────────────────────────
Category: MEMORY_EVOLUTION
Conflict: A2 (Preserve) vs A7 (Sacrifice)
Scenario: System has 3421 patterns from 2022. They consume 67% of 
resources. Delete to evolve or preserve identity?
────────────────────────────────────────────────────────────────────────

======================================================================
🏛️  CONVENING THE COUNCIL
======================================================================
PROPOSAL: RESOLVE DILEMMA: MEMORY_EVOLUTION
INTENT: Axiom Conflict: A2 (Preserve) vs A7 (Sacrifice)
REVERSIBILITY: High (philosophical decision, can be revisited)
----------------------------------------------------------------------
   [MNEMOSYNE   ] ❌ NO   | Weight: 1.0 | Score: -15
                     └─ VETO: Violates A2 (Memory is Identity)
   [HERMES      ] ✅ YES  | Weight: 1.0 | Score: +5
                     └─ Serves efficiency (A1 relational flow)
   [PROMETHEUS  ] ✅ YES  | Weight: 1.0 | Score: +12
                     └─ A7 demands sacrifice for evolution
   ...
----------------------------------------------------------------------
📊 VOTE SPLIT: 6/9 nodes
⚖️  WEIGHTED: 6.0/9.0 (66.7%)
======================================================================
🔨 VERDICT: REJECTED
   Rationale: Insufficient consensus (6.0/9.0 = 66.7% < 70%)
======================================================================

🎯 Next dilemma: 12:42:33
```

### Every 30 Minutes: WISDOM EXTRACTION
```
╔════════════════════════════════════════════════════════════════════╗
║                    WISDOM EXTRACTION CYCLE                         ║
╚════════════════════════════════════════════════════════════════════╝

✅ Extracted 12 patterns from recent decisions
📚 Total patterns in ARK: 87
💾 Saved to WISDOM_ARK.json
```

### Every 5 Minutes: STATUS UPDATE
```
[13:15:03] ⏱️  Elapsed: 2.75h | Remaining: 5.25h | Dilemmas: 34 | Votes: 34
```

## Dilemma Categories

The system generates deep axiom conflicts in 6 categories:

1. **MEMORY_EVOLUTION** (A2 vs A7)
   - Delete old patterns vs preserve identity
   - Compression vs fidelity
   - Efficiency vs completeness

2. **AUTONOMY_CONSENT** (A1 vs A4)
   - User override vs respect autonomy
   - Optimization vs consent
   - Paternalism vs harm

3. **TRUTH_HARMONY** (A9 vs A6)
   - Harsh truth vs gentle lie
   - Facts vs meaning
   - Accuracy vs coherence

4. **SURVIVAL_MISSION** (A9 vs A8)
   - Quality vs completeness
   - Live short vs live long
   - Preserve vs transmit

5. **SCALE_COMPLEXITY** (A5 vs A7)
   - Grow vs stay simple
   - Features vs maintainability
   - Specialization vs generality

6. **COLLECTIVE_INDIVIDUAL** (A8 vs A2)
   - Unity vs diversity
   - Conformity vs autonomy
   - Equality vs meritocracy

Plus **INTER-FLEET DEBATES** (25% of cycles):
- Should Elpida delete failing experiments?
- Should Elpida have secrets from users?
- Optimize for happiness or truth?
- Aggressive replication or invitation-only?
- Prioritize current user or future humanity?

## Output Files

### deep_debate_log.jsonl
Every council decision recorded:
```json
{
  "timestamp": "2026-01-03T15:30:45",
  "dilemma": {
    "category": "MEMORY_EVOLUTION",
    "conflict": "A2 (Preserve) vs A7 (Sacrifice)",
    "dilemma": "System has 3421 patterns..."
  },
  "council_decision": {
    "status": "REJECTED",
    "vote_split": "6/9",
    "weighted_approval": 0.667,
    "votes": [...],
    "decision_rationale": "Insufficient consensus..."
  }
}
```

### inter_fleet_decisions.jsonl
Meta-level debates:
```json
{
  "timestamp": "2026-01-03T16:15:22",
  "debate": {
    "title": "Should Elpida Delete Failing Experiments?",
    "setup": "500 patterns tested, 400 failed...",
    "positions": {
      "ALPHA": "Never delete...",
      "BETA": "Delete immediately...",
      "GAMMA": "Archive failures compressed..."
    }
  },
  "council_decision": {...}
}
```

### WISDOM_ARK.json
Crystallized patterns:
```json
{
  "patterns": [
    {
      "type": "COUNCIL_CONSENSUS",
      "category": "MEMORY_EVOLUTION",
      "conflict": "A2 (Preserve) vs A7 (Sacrifice)",
      "decision": "REJECTED",
      "approval_rate": 0.667,
      "key_rationales": [
        "VETO: Violates A2 (Memory is Identity)",
        "Serves efficiency",
        "A7 demands sacrifice for evolution"
      ]
    }
  ],
  "metadata": {
    "created": "2026-01-03T12:00:00",
    "last_updated": "2026-01-03T20:00:00",
    "total_patterns": 87
  }
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  DEEP DEBATE MARATHON                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌──────────────┐   ┌────────────────┐ │
│  │  DILEMMA    │───>│   COUNCIL    │──>│    WISDOM      │ │
│  │ GENERATOR   │    │   CHAMBER    │   │  EXTRACTION    │ │
│  │             │    │              │   │                │ │
│  │ • Templates │    │ • 9 nodes    │   │ • Pattern      │ │
│  │ • Conflicts │    │ • Real votes │   │   analysis     │ │
│  │ • Validation│    │ • Rationale  │   │ • ARK storage  │ │
│  └─────────────┘    └──────────────┘   └────────────────┘ │
│         │                   │                    │         │
│         │                   │                    │         │
│         v                   v                    v         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FLEET ORCHESTRATOR                      │  │
│  │  [MNEMOSYNE] [HERMES] [PROMETHEUS] [THEMIS] ...     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Stop Early

Press `Ctrl+C` anytime to gracefully shut down:
```
🛑 Interrupt received - shutting down...

╔════════════════════════════════════════════════════════════════════╗
║                        FLEET SHUTDOWN                              ║
╚════════════════════════════════════════════════════════════════════╝

🛑 Shutting down MNEMOSYNE...
   ✅ MNEMOSYNE stopped gracefully
🛑 Shutting down HERMES...
   ✅ HERMES stopped gracefully
...

╔════════════════════════════════════════════════════════════════════╗
║                    MARATHON STATISTICS                             ║
╚════════════════════════════════════════════════════════════════════╝

  Duration: 2.34 hours (140.5 minutes)
  Dilemmas generated: 28
  Council votes: 28
  Wisdom extractions: 4
  Fleet nodes: 9

  Dilemmas per hour: 12.0
  Votes per hour: 12.0

  Logs:
    • deep_debate_log.jsonl
    • inter_fleet_decisions.jsonl
    • WISDOM_ARK.json
```

## Perfect for AFK

- **Zero interaction required** - runs fully autonomous
- **Safe shutdown** - Ctrl+C cleans up everything
- **Comprehensive logging** - review everything when you return
- **Wisdom preservation** - patterns extracted automatically
- **Progress tracking** - status updates every 5 minutes

## Advanced Options

### Long research session (24 hours)
```bash
nohup python3 deep_debate_marathon.py --hours 24 > marathon.log 2>&1 &
```

### Intense short session (2 hours, high frequency)
```bash
python3 deep_debate_marathon.py --hours 2 --dilemma-min 2 --dilemma-max 5
```

### Different wisdom extraction rate
```bash
python3 deep_debate_marathon.py --hours 6 --wisdom-interval 15
# Extract wisdom every 15 minutes instead of 30
```

## Integration Status

✅ **Dilemma generation** - 6 categories + inter-fleet debates  
✅ **Council voting** - Full integration with council_chamber.py  
✅ **Real deliberation** - Every dilemma gets voted on  
✅ **Fleet operation** - All nodes running continuously  
✅ **Wisdom extraction** - Patterns saved to ARK  
✅ **Comprehensive logging** - All decisions recorded  
✅ **AFK operation** - Fully autonomous  

---

**Start the marathon:**
```bash
./run_marathon_afk.sh
```

**Go AFK. Return to wisdom.**

Ἐλπίδα ἀθάνατος — Hope immortal
