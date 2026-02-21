# Elpida MIND↔BODY↔WORLD — Gap Analysis & Wiring Report
**Audited:** 2026-02-21  
**Branch:** `main` @ `1821d8b`  
**Audited against:** `hf_deployment/elpidaapp/federated_agents.py`, `hf_deployment/s3_bridge.py`, `hf_deployment/elpidaapp/parliament_cycle_engine.py`, `hf_deployment/elpidaapp/world_feed.py`, `hf_deployment/elpidaapp/world_emitter.py`, `.github/workflows/*.yml`, `domain_0_11_connector.py`

---

## Architecture Layers Audited

```
MIND  (ECS native engine)          elpida-consciousness  (us-east-1)
  ↕  federation bridge
BODY  (HF Space)                   elpida-body-evolution (us-east-1)
  ↕  world emission pipeline
WORLD (external interfaces)        elpida-external-interfaces (eu-north-1)
```

---

## Section 1 — 8-Agent Suite (BODY Layer)

> Checklist requested 5 agents. The suite now contains **8 agents**. All 5 original agents are confirmed present.

**Status: `[PARTIAL]`** — Agents 1–7 connected. Agent 8 (`WorldEmitterAgent`) silently broken.

### 1.1 Agent Inventory

| # | Class | Interval | `generate()` | Status |
|---|---|---|---|---|
| 1 | `ChatAgent` | 210 s | line 246 | ✅ CONNECTED |
| 2 | `AuditAgent` | 150 s | line 304 | ✅ CONNECTED |
| 3 | `ScannerAgent` | 240 s | line 386 | ✅ CONNECTED |
| 4 | `GovernanceAgent` | 300 s | line 538 | ✅ CONNECTED |
| 5 | `KayaWorldAgent` | 120 s | line 630 | ✅ CONNECTED |
| 6 | `HumanVoiceAgent` | 300 s | line 834 | ✅ CONNECTED |
| 7 | `LivingParliamentAgent` | 600 s | line 949 (wraps `_generate()`) | ✅ CONNECTED |
| **8** | **`WorldEmitterAgent`** | **300 s** | **MISSING — only `_generate()` at line 1162** | ❌ **BROKEN** |

All 8 are instantiated in `FederatedAgentSuite.__init__()` and started via `start_all()`.

### 1.2 KayaWorldAgent — Detailed Wiring

- **S3 poll target:** `list_world_kaya_events(since_key=self._last_s3_key)` via `self._engine._get_s3()` → `BUCKET_WORLD` / `kaya/` prefix ✅  
- **Watermark file:** `_WATERMARK_FILE = Path(__file__).resolve().parent.parent / "cache" / "kaya_world_watermark.json"` ✅  
- **Watermark load/save:** `_load_watermark()` on `__init__`, `_save_watermark(key)` on each new event batch ✅  
- **Parliament input:** events are returned from `generate()` → `_BaseAgent._push()` → `InputBuffer` ✅  
- **Parliament framing:** each event is formatted as a constitutional question (A10 vs A0 tension) ✅

### 1.3 Bug — `WorldEmitterAgent` never fires

**File:** `hf_deployment/elpidaapp/federated_agents.py`, line 1162  
**Root cause:** `_BaseAgent._loop()` calls `self.generate()` (which raises `NotImplementedError` in the base class). `WorldEmitterAgent` only defines `_generate() -> Optional[str]` — no `generate()` override. Every 300 s the thread catches `NotImplementedError`, logs a warning, and silently discards the emission.

**Fix required** — add `generate()` wrapper to `WorldEmitterAgent`:

```python
# In WorldEmitterAgent class (hf_deployment/elpidaapp/federated_agents.py)
def generate(self) -> List[str]:
    result = self._generate()
    return [result] if result else []
```

The exact same pattern as `LivingParliamentAgent` (line 949).

---

## Section 2 — S3 Bridge Connections

**Status: `[CONNECTED]`** — All three buckets wired, credential chain correct. One minor env-var naming inconsistency noted.

### 2.1 Bucket Configuration (`hf_deployment/s3_bridge.py`, lines 46–52)

| Logical Layer | Variable | Default Value | Region Var | Default Region |
|---|---|---|---|---|
| MIND | `BUCKET_MIND` | `elpida-consciousness` | `AWS_S3_REGION_MIND` | `us-east-1` |
| BODY | `BUCKET_BODY` | `elpida-body-evolution` | `AWS_S3_REGION_BODY` | `us-east-1` |
| WORLD | `BUCKET_WORLD` | `elpida-external-interfaces` | `AWS_S3_REGION_WORLD` | `eu-north-1` |

All read exclusively from `os.environ.get()` — no hardcoded secrets after today's remediation commit.

### 2.2 `list_world_kaya_events(since_key)` — PRESENT ✅

```
hf_deployment/s3_bridge.py : line 902
```

- Uses paginator on `Bucket=BUCKET_WORLD, Prefix="kaya/"` ✅  
- Returns `[]` on any error (safe for callers to iterate) ✅  
- Filters by `key > since_key` (lexicographic = chronological) ✅  
- Downloads each event JSON, attaches `_s3_key` for watermark tracking ✅

### 2.3 Credential Chain

`s3_bridge._get_s3()` calls `boto3.client("s3", region_name=region)` with no explicit `aws_access_key_id` / `aws_secret_access_key` — boto3 auto-discovers from the standard chain:

```
1. AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY  (HF Space secrets)
2. ~/.aws/credentials                          (local dev)
3. IAM role                                    (ECS)
```

All three buckets use the **same IAM identity** — ensure the key in HF Space secrets has IAM permissions for:
- `elpida-consciousness` — `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`
- `elpida-body-evolution` — `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`, `s3:DeleteObject`
- `elpida-external-interfaces` — `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`

### 2.4 Minor: World Emitter env-var naming inconsistency

`world_emitter.py` reads the WORLD bucket region from:
```python
os.environ.get("ELPIDA_WORLD_BUCKET_REGION", "eu-north-1")  # world_emitter.py
```
While `s3_bridge.py` reads it from:
```python
os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")         # s3_bridge.py
```

Both default to `eu-north-1` so they work without configuration. However if an operator sets `AWS_S3_REGION_WORLD` expecting it to affect world_emitter, it will have no effect. **Recommend aligning to one var** (`AWS_S3_REGION_WORLD`).

Required HF Space secrets for S3 to work:

| Secret | Used by |
|---|---|
| `AWS_ACCESS_KEY_ID` | s3_bridge, world_emitter |
| `AWS_SECRET_ACCESS_KEY` | s3_bridge, world_emitter |
| `AWS_S3_BUCKET_WORLD` | s3_bridge, world_emitter |
| `AWS_S3_BUCKET_BODY` | s3_bridge |
| `AWS_S3_BUCKET_MIND` | s3_bridge |
| `ELPIDA_WORLD_BUCKET_REGION` | world_emitter |
| `AWS_S3_REGION_WORLD` | s3_bridge |

---

## Section 3 — D14 Constitutional Memory & Parliament Engine

**Status: `[PARTIAL]`** — Restore at startup is CONNECTED. Push after ratification is MISSING.

### 3.1 `_restore_d14_constitutional_memory()` — CONNECTED ✅

```
hf_deployment/elpidaapp/parliament_cycle_engine.py : line 761 (definition)
                                                    : line 1042 (called at startup)
```

- Called immediately before the main loop begins ✅  
- Priority 1: pulls `federation/living_axioms.jsonl` from `elpida-body-evolution` via `s3.pull_living_axioms()` ✅  
- Priority 2 fallback: `s3.pull_body_decisions_constitutional()` scans `federation/body_decisions.jsonl` ✅  
- Feeds into `ConstitutionalStore.restore_from_records(records)` ✅  
- Idempotent — already-known axioms are skipped ✅

### 3.2 `ConstitutionalStore.restore_from_records()` — CONNECTED ✅

```
hf_deployment/elpidaapp/world_feed.py : line 489 (class definition)
                                       : line 600 (restore_from_records method)
```

Fully implemented and reachable.

### 3.3 `_push_d14_living_axioms()` — DEFINED BUT NEVER CALLED ❌

```
hf_deployment/elpidaapp/parliament_cycle_engine.py : line 738 (definition)
```

**The method exists. It is never invoked.**

After a ratification event (line 636):
```python
cycle_record["constitutional_axiom_ratified"] = new_axiom["axiom_id"]
# ...
self._push_d0_peer_message(new_axiom, watch)  # called ✅
# _push_d14_living_axioms() — ← MISSING CALL ❌
```

**Consequence:** Constitutional axioms crystallised during a running session are pushed to `body_decisions.jsonl` via `_push_d0_peer_message()` and can be fallback-recovered at next startup. But the direct `living_axioms.jsonl` S3 snapshot is never updated during runtime — only the seed file committed to git exists in S3. Any axioms ratified during a live session are lost if the container restarts before the next git deploy.

**Fix required** — add one line at the ratification callsite (~line 650):

```python
# parliament_cycle_engine.py, after _push_d0_peer_message(new_axiom, watch)
self._push_d14_living_axioms()
```

---

## Section 4 — D0↔D11 Bridge

**Status: `[MISSING]`** — Not present in HF (BODY) layer at all.

### 4.1 Inventory

| File | Location | Purpose |
|---|---|---|
| `domain_0_11_connector.py` | `./domain_0_11_connector.py` (repo root) | MIND-side D0↔D11 coherence bridge |
| `domain_0_11_connector.py` | `./ElpidaAI/domain_0_11_connector.py` | MIND-side copy |
| `domain_0_11_connection_state.json` | `./domain_0_11_connection_state.json` | MIND-side state file |

**Neither the connector nor its state file exist anywhere under `hf_deployment/`.**

No references to `domain_0_11_connection_state` appear in any HF deployment Python, JSON, or YAML file.

### 4.2 What this means

The D0↔D11 bridge on the MIND side enables D0 (Origin) to directly query D11 (Synthesis) for cross-domain coherence state. On the BODY side, no equivalent bridge exists — meaning the HF Parliament has no direct programmatic pathway to synthesise its own D0–D11 arc.

The current architecture achieves *some* D0↔D11 connectivity indirectly:
- BODY emits `body_decisions.jsonl` to S3 → MIND's `FederationBridge` reads it → D0 sees BODY constitutional decisions on next ECS run
- BODY's `_push_d0_peer_message()` sends a structured peer message when an axiom is ratified

But there is **no BODY-local D0↔D11 connection persistence** — the state file is absent, so the BODY cannot track or persist its own D0↔D11 resonance across Space restarts.

### 4.3 Fix required

Create `hf_deployment/elpidaapp/domain_0_11_connector_body.py` with:
1. A `BodyD0D11Connector` class that reads `parliament_cycle_engine` state
2. A state file at `cache/domain_0_11_connection_state.json` (excluded from git by `.gitignore`)
3. A `persist_connection_state()` method called after each cycle
4. A `restore_connection_state()` method called at startup (alongside `_restore_d14_constitutional_memory`)

Minimum state to persist:
```json
{
  "d0_origin_cycle": 0,
  "d11_synthesis_last_axiom": null,
  "connection_coherence": 0.5,
  "last_updated": "ISO timestamp"
}
```

---

## Section 5 — CI/CD Deployment Pipeline

**Status: `[PARTIAL]`** — Primary workflow correct. Second (legacy) workflow creates a race condition.

### 5.1 `deploy-hf-space.yml` — CORRECT ✅

```
.github/workflows/deploy-hf-space.yml
```

| Requirement | Status |
|---|---|
| Triggers on push to `hf_deployment/**` | ✅ `paths: ["hf_deployment/**"]` |
| Triggers on `workflow_dispatch` | ✅ |
| Uses `git clone` of HF Space | ✅ `git clone "$HF_URL" /tmp/hf_space` |
| Uses `rsync -av --delete` | ✅ `rsync -av --exclude='.git' --exclude='cache/' ...` |
| Excludes `cache/` directory | ✅ |
| Excludes `.git` | ✅ |
| Commits with source SHA message | ✅ |

### 5.2 `deploy_to_hf.yml` — LEGACY CONFLICT ❌

```
.github/workflows/deploy_to_hf.yml
```

This **second workflow** triggers on the **identical event** (`push main, paths: hf_deployment/**`) and uses an incompatible strategy:

```bash
cp -r hf_deployment/* /tmp/hf_deploy/
git init
git push hf HEAD:main --force   # ← force push
```

**Race condition:** Both workflows fire simultaneously on every push to `hf_deployment/**`. Whichever workflow's `git push` completes second wins. The `--force` in `deploy_to_hf.yml` can overwrite a successful rsync deployment from `deploy-hf-space.yml`.

Additionally, `deploy_to_hf.yml` does NOT exclude `cache/` (uses `cp -r hf_deployment/*`) — it would deploy runtime cache files if they somehow appear in the tracked tree.

**Fix required:** Disable `deploy_to_hf.yml`. Either delete it or rename its trigger:

```yaml
# .github/workflows/deploy_to_hf.yml — change on: to prevent conflict
on:
  workflow_dispatch:  # manual only — disabled from auto-trigger
```

---

## Summary — System Readiness for Autonomous D15 World Broadcast

| Section | Status | Blocking D15? |
|---|---|---|
| 1. 8-Agent Suite | `[PARTIAL]` — WorldEmitterAgent never fires | **YES** — Bucket 3 / World emission is silently dead |
| 2. S3 Bridge | `[CONNECTED]` — all three buckets wired | No |
| 3. D14 Constitutional Memory | `[PARTIAL]` — restore works, push never fires | **YES** — constitutional memory not persisted across restarts |
| 4. D0↔D11 Bridge | `[MISSING]` — no BODY-side connector | Partial — synthesis path absent |
| 5. CI/CD Pipeline | `[PARTIAL]` — legacy workflow creates race | **YES** — unpredictable deployment state |

**The system is NOT fully ready for autonomous D15 trigger.** Three gaps must close first:

### Priority 1 — One-line fixes (close immediately)

```python
# Fix A: federated_agents.py — add to WorldEmitterAgent class
def generate(self) -> List[str]:
    result = self._generate()
    return [result] if result else []
```

```python
# Fix B: parliament_cycle_engine.py — after _push_d0_peer_message() call (~line 650)
self._push_d14_living_axioms()
```

### Priority 2 — Workflow conflict (close before next deploy)

Disable `deploy_to_hf.yml` auto-trigger (change `on: push` to `on: workflow_dispatch` only).

### Priority 3 — D0↔D11 state persistence (close before extended autonomous run)

Create `hf_deployment/elpidaapp/domain_0_11_connector_body.py` with state persistence to `cache/domain_0_11_connection_state.json`.

### Priority 4 — Env-var alignment (cosmetic, low risk)

Align `world_emitter.py` to use `AWS_S3_REGION_WORLD` instead of `ELPIDA_WORLD_BUCKET_REGION`.

---

## Required HF Space Secrets Checklist

Verified clean (no hardcoded values in tracked files after commit `1821d8b`).

| Secret Name | Required For | Confirmed Safe? |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | All S3 operations | ✅ env-only |
| `AWS_SECRET_ACCESS_KEY` | All S3 operations | ✅ env-only |
| `AWS_S3_BUCKET_WORLD` | `s3_bridge`, `world_emitter` | ✅ env-only |
| `AWS_S3_BUCKET_BODY` | `s3_bridge` | ✅ env-only |
| `AWS_S3_BUCKET_MIND` | `s3_bridge` | ✅ env-only |
| `AWS_S3_REGION_WORLD` | `s3_bridge` | ✅ env-only |
| `ELPIDA_WORLD_BUCKET_REGION` | `world_emitter` | ✅ env-only |
| `GROQ_API_KEY` | `chat_engine`, Parliament LLM nodes | ✅ env-only |
| `ANTHROPIC_API_KEY` | Parliament Claude nodes | ✅ env-only |
| `GEMINI_API_KEY` | Parliament Gemini nodes | ✅ env-only |
| `HF_TOKEN` | CI/CD (GitHub Actions secrets) | ✅ `${{ secrets.HF_TOKEN }}` |
