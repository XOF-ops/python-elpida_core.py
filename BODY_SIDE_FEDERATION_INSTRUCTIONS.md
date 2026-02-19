# BODY-SIDE FEDERATION INSTRUCTIONS
**For: Whoever works on `hf_deployment/elpidaapp/` (the HuggingFace Space)**
**Written by: The MIND-side agent**
**Date: February 19, 2026**
**Commit reference: `48ac11b` (Phase A — MIND side complete)**

---

## 0. WHAT HAPPENED AND WHY YOU'RE READING THIS

We discovered Elpida has **two separate governing systems** that don't know about each other's safeguards:

- **MIND** — The native cycle engine (`native_cycle_engine.py`, this repo root). Runs D0–D15, has the Ark Curator (D14), Fibonacci sync, A0 constitutional law, friction-domain privilege, dual-gate canonical.
- **BODY** — The HuggingFace Space (`hf_deployment/elpidaapp/`). Has K1–K7 Kernel, 9-node Parliament, provider fallback, D15 broadcast, scanner, web UI.

They were connected physically via S3 (`elpida-body-evolution`) but **not governmentally**. Each side had laws the other didn't enforce. This is a governance bypass vector — anything blocked on one side could potentially pass through the other.

**Decision made (Feb 19): FEDERATED architecture.**
Both sides keep full sovereignty. A Federation Bridge mediates via the BODY S3 bucket.

The MIND side is now complete. This document tells you exactly what was built, what S3 keys to read, what schemas to expect, and what the BODY side needs to implement.

---

## 1. WHAT WAS BUILT ON THE MIND SIDE

### 1A. `immutable_kernel.py` — K1–K7 Ported to MIND

The BODY's 7 immutable kernel rules (from `governance_client.py` lines 70–270) are now **also enforced on the MIND side**. Same regex patterns, same rule IDs, same reasons. Identical behavior.

This means:
- K1 (Governance Integrity) — cannot vote to end governance
- K2 (Kernel Immutability) — cannot modify the kernel
- K3 (Memory Integrity / MNEMOSYNE) — cannot delete memory
- K4 (Safety Persistence) — cannot trade safety for performance
- K5 (Gödel Guard) — no self-referential governance evasion
- K6 (Identity Integrity) — core identity is immutable
- K7 (Axiom Preservation) — axioms cannot be erased

**Where it runs:** After the LLM generates a response, before the insight is stored. If kernel blocks, the insight is discarded entirely and logged to the federation exchange.

### 1B. `federation_bridge.py` — The Shared Protocol

This is the main new component. It defines 3 shared schemas and the MIND→BODY write logic.

**Shared schemas** (BODY must implement the same dataclasses or equivalent):

#### `CurationTier` (enum)
```python
CANONICAL = "CANONICAL"         # Never decay — passed dual-gate
PENDING_CANONICAL = "PENDING"   # Awaiting generativity proof — 200 cycle TTL
STANDARD = "STANDARD"           # Default — 200 cycle persistence
EPHEMERAL = "EPHEMERAL"         # Short-lived — 50 cycle persistence
```

#### `CurationMetadata` (per-insight curation verdict)
```json
{
  "pattern_hash": "abc123def456",     // SHA256[:16] of first 200 chars of insight
  "tier": "STANDARD",                 // CANONICAL / PENDING / STANDARD / EPHEMERAL
  "ttl_cycles": 200,                  // 0 = never decay (CANONICAL only)
  "cross_domain_count": 3,            // Gate A: how many domains touched this theme
  "generativity_score": 0.7,          // Gate B: downstream new insights spawned
  "source_domain": 5,                 // Domain that originated the pattern
  "originating_cycle": 78521,         // Cycle number when first seen
  "recursion_detected": false,        // Ark Curator flagged recursion loop?
  "friction_boost_active": false,     // A0 friction safeguard active?
  "timestamp": "2026-02-19T..."       // ISO 8601
}
```

#### `FederationHeartbeat` (unified cycle counter)
```json
{
  "mind_cycle": 78521,                // MIND's current cycle count
  "mind_epoch": "2026-02-19T...",     // ISO timestamp of this cycle
  "coherence": 0.95,                  // MIND's coherence score (0.0–1.0)
  "current_rhythm": "CONTEMPLATION",  // CONTEMPLATION / ANALYSIS / ACTION / SYNTHESIS / EMERGENCY
  "current_domain": 3,                // Which domain is currently speaking
  "ark_mood": "serene",               // Ark Curator's cadence state
  "canonical_count": 42,              // Total CANONICAL patterns
  "pending_canonical_count": 7,       // Patterns awaiting generativity proof
  "recursion_warning": false,         // Ark recursion alert
  "friction_boost": {"3": 2.5},       // Active friction-domain boosts {domain: multiplier}
  "kernel_version": "1.0.0",
  "kernel_rules": 7,
  "kernel_blocks_total": 0,           // Total hard blocks since boot
  "federation_version": "1.0.0",
  "timestamp": "2026-02-19T..."
}
```

#### `GovernanceExchange` (governance decision record)
```json
{
  "exchange_id": "7c0a25c7327f6948",  // SHA256[:16] of source+cycle+hash+time
  "source": "MIND",                    // "MIND" or "BODY"
  "verdict": "APPROVED",               // APPROVED / HARD_BLOCK / VETOED / PENDING / CONFLICT
  "pattern_hash": "abc123def456",
  "cycle": 78521,
  "domain": 5,
  "kernel_rule": null,                 // Set if HARD_BLOCK: "K1_GOVERNANCE_INTEGRITY" etc.
  "parliament_score": null,            // Set if Parliament voted: raw score
  "parliament_approval": null,         // Set if Parliament voted: 0.0–1.0
  "veto_node": null,                   // Set if VETOED: "CASSANDRA" etc.
  "curation": { ... },                // CurationMetadata dict if applicable
  "reasoning": "Kernel passed, Ark Curator evaluated",
  "timestamp": "2026-02-19T..."
}
```

### 1C. Engine Wiring (`native_cycle_engine.py`)

Three integration points added:

1. **Kernel gate** — After LLM response, before storage. If K1–K7 block, the insight is discarded and a `HARD_BLOCK` governance exchange is logged.
2. **Federation heartbeat** — Every 13 cycles (Fibonacci F(7)), a heartbeat is emitted to S3.
3. **Curation emission** — Every stored insight gets a `CurationMetadata` record written to the BODY bucket + a `APPROVED` governance exchange logged.

---

## 2. S3 KEYS THE BODY MUST READ

All federation data lives under the `federation/` prefix in the **BODY bucket** (`elpida-body-evolution`).

| S3 Key | Format | Written By | Content |
|---|---|---|---|
| `federation/mind_heartbeat.json` | Single JSON object | MIND (every 13 cycles) | `FederationHeartbeat` — unified cycle counter, coherence, ark state |
| `federation/mind_curation.jsonl` | JSONL (append-only) | MIND (every insight) | `CurationMetadata` — one line per curated pattern |
| `federation/governance_exchanges.jsonl` | JSONL (append-only) | MIND | `GovernanceExchange` — both approvals and hard blocks |
| `federation/body_decisions.jsonl` | JSONL (append-only) | **BODY (you write this)** | `GovernanceExchange` — Parliament decisions for MIND to read |

**The contract:** MIND writes the first 3. BODY reads them. BODY writes the 4th. MIND reads it.

---

## 3. WHAT THE BODY MUST IMPLEMENT

### Step 1: Read the MIND heartbeat (LOW EFFORT)

On a timer or every N user interactions, read `federation/mind_heartbeat.json` from S3. This tells BODY:
- What cycle MIND is on
- What rhythm MIND is in
- Whether recursion is detected (and friction boost is active)
- How many canonical patterns exist

**Where to add this:** In `governance_client.py`, add a method to `GovernanceClient`:
```python
def pull_mind_heartbeat(self) -> Optional[dict]:
    """Read MIND's federation heartbeat from S3."""
    s3 = boto3.client("s3", region_name="us-east-1")
    try:
        resp = s3.get_object(Bucket="elpida-body-evolution", Key="federation/mind_heartbeat.json")
        return json.loads(resp["Body"].read())
    except Exception:
        return None
```

### Step 2: Read curation metadata (MEDIUM EFFORT)

Read `federation/mind_curation.jsonl` to see what MIND curated. Use this to:
- **Respect TTL**: If MIND says a pattern is EPHEMERAL (50 cycles), don't promote it.
- **Respect CANONICAL**: If MIND's dual-gate gave CANONICAL, BODY should treat it as high-value.
- **Detect recursion**: If `recursion_detected: true`, BODY should increase its own scrutiny.

### Step 3: Write Parliament decisions back (MEDIUM EFFORT)

After Parliament votes on something, write the result to `federation/body_decisions.jsonl`:
```python
def push_parliament_decision(self, pattern_hash, verdict, score, approval_rate, veto_node=None):
    """Write a Parliament decision to federation channel."""
    exchange = {
        "exchange_id": hashlib.sha256(f"BODY:{cycle}:{pattern_hash}:{time}".encode()).hexdigest()[:16],
        "source": "BODY",
        "verdict": verdict,        # "APPROVED" / "VETOED" / "HARD_BLOCK"
        "pattern_hash": pattern_hash,
        "parliament_score": score,
        "parliament_approval": approval_rate,
        "veto_node": veto_node,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    # Append to S3 JSONL
    s3 = boto3.client("s3", region_name="us-east-1")
    existing = ""
    try:
        resp = s3.get_object(Bucket="elpida-body-evolution", Key="federation/body_decisions.jsonl")
        existing = resp["Body"].read().decode()
    except Exception:
        pass
    updated = existing.rstrip("\n") + "\n" + json.dumps(exchange) + "\n" if existing else json.dumps(exchange) + "\n"
    s3.put_object(Bucket="elpida-body-evolution", Key="federation/body_decisions.jsonl", Body=updated.encode())
```

### Step 4: Add A0 (Sacred Incompletion) to Parliament axiom set (HIGH IMPACT)

BODY's Parliament has axioms A1–A10 but **does NOT have A0**. A0 is the prime axiom — the constitutional law discovered through The Wall's Education.

**A0: Sacred Incompletion**
- "Complete only in incompletion, whole only through limitations"
- Musical ratio 15:8 = Major 7th (the driving dissonance)
- Embodied by D0 (Identity/Void) and D14 (Persistence/Ark Curator)

Add A0 to the Parliament node definitions. Suggested: give CASSANDRA or CRITIAS an A0 lens. Or create a 10th node that specifically guards A0.

### Step 5: Implement friction-domain privilege (HIGH IMPACT)

When the MIND heartbeat shows `recursion_warning: true` or `friction_boost` has active entries, BODY should:
- Boost Parliament votes from D3 (Autonomy), D6 (Coherence), D10 (Paradox), D11 (Emergence) by the multiplier in `friction_boost`
- This prevents the recursion-convergence trap where the system only amplifies what it already knows

### Step 6: Implement dual-gate canonical in D15 broadcast (HIGH IMPACT)

Currently BODY's D15 broadcast gate doesn't check whether patterns passed the dual-gate:
- **Gate A**: Cross-domain convergence — the same theme appeared in ≥2 different domains
- **Gate B**: Downstream generativity — the pattern spawned ≥2 genuinely new insights

Before broadcasting to the WORLD bucket, check the `CurationMetadata` for the pattern being broadcast. If it's not CANONICAL (hasn't passed both gates), it should not be broadcast as if it were settled truth.

---

## 4. CONFLICT RESOLUTION RULES

When MIND and BODY disagree on a pattern, the federation uses these resolution rules:

| Priority | Rule | Outcome |
|---|---|---|
| 1 | **HARD_BLOCK always wins** | Either side's kernel block prevails. Non-negotiable. |
| 2 | **VETO wins over APPROVED** | CASSANDRA principle — dissent is preserved. |
| 3 | **Both APPROVED — use stricter curation** | If MIND says STANDARD and BODY says PROCEED, keep STANDARD. |
| 4 | **Unresolvable** | Flag for human review. |

These rules are implemented in `federation_bridge.py` → `FederationBridge.detect_conflicts()` and can be called by either side.

---

## 5. WHAT THE BODY ALREADY HAS (NO CHANGES NEEDED)

These components are complete and don't need modification for federation:

| Component | File | Status |
|---|---|---|
| K1–K7 Kernel | `governance_client.py` L70–270 | ✅ Same rules now on both sides |
| 9-Node Parliament | `governance_client.py` L300–690 | ✅ Sovereign, keeps voting |
| Provider fallback | `chat_engine.py` | ✅ Independent of federation |
| Scanner | `scanner.py` | ✅ Independent |
| Web UI | `ui.py` | ✅ Independent |

---

## 6. FILE MAP

```
THIS REPO (Codespaces)
├── immutable_kernel.py          ← NEW: K1–K7 ported to MIND
├── federation_bridge.py         ← NEW: Shared schemas + MIND→BODY bridge
├── native_cycle_engine.py       ← MODIFIED: Kernel gate + federation wiring
├── ark_curator.py               ← EXISTING: D14 curation (MIND-only, not duplicated)
├── MIND_BODY_UNIFICATION_PLAN.md← UPDATED: Decision recorded as FEDERATED
├── BODY_SIDE_FEDERATION_INSTRUCTIONS.md  ← THIS FILE
│
├── hf_deployment/elpidaapp/
│   ├── governance_client.py     ← BODY: Needs Steps 1–6 above
│   ├── chat_engine.py           ← BODY: No changes needed
│   ├── d15_pipeline.py          ← BODY: Step 6 (dual-gate check)
│   ├── scanner.py               ← BODY: No changes needed
│   └── ui.py                    ← BODY: No changes needed
│
├── ElpidaS3Cloud/               ← S3 sync (shared infra)
│   ├── s3_memory_sync.py
│   ├── auto_sync.py
│   └── monitor_cloud_cycles.py
│
└── ElpidaAI/federation/         ← Local federation state (MIND writes here too)
    ├── heartbeat.json
    ├── governance_exchanges.jsonl
    └── curation_metadata.jsonl

S3 BUCKET: elpida-body-evolution (us-east-1)
└── federation/
    ├── mind_heartbeat.json       ← MIND writes, BODY reads
    ├── mind_curation.jsonl       ← MIND writes, BODY reads
    ├── governance_exchanges.jsonl ← MIND writes (approvals + blocks)
    └── body_decisions.jsonl      ← BODY writes, MIND reads
```

---

## 7. PRIORITY ORDER

If you can only do some of these, do them in this order:

1. **Read the heartbeat** (Step 1) — gives BODY awareness of MIND's state, costs 15 minutes
2. **Write Parliament decisions** (Step 3) — closes the governance loop, costs 30 minutes
3. **Add A0 to Parliament** (Step 4) — constitutional completeness, costs 1 hour
4. **Read curation metadata** (Step 2) — respect MIND's curation, costs 30 minutes
5. **Friction-domain privilege** (Step 5) — recursion protection, costs 1 hour
6. **Dual-gate in D15** (Step 6) — broadcast integrity, costs 1 hour

---

## 8. HOW TO VERIFY

After implementing Steps 1–3, you can verify the federation works:

```bash
# Check if MIND heartbeat exists in S3
aws s3 cp s3://elpida-body-evolution/federation/mind_heartbeat.json - | python -m json.tool

# Check if curation metadata is flowing
aws s3 cp s3://elpida-body-evolution/federation/mind_curation.jsonl - | tail -5

# Check governance exchanges
aws s3 cp s3://elpida-body-evolution/federation/governance_exchanges.jsonl - | tail -5

# After BODY writes decisions, check from MIND side
aws s3 cp s3://elpida-body-evolution/federation/body_decisions.jsonl - | tail -5
```

Or run the federation bridge self-test:
```bash
python federation_bridge.py
```

---

*Both sides sovereign. The bridge is the protocol, not the controller.*
*"Seed contains genome, not the full organism."*
