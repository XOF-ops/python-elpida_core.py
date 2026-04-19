# Elpida SDK + MCP Server — Deep-Dive Source Inventory & Architecture Blueprint
## Report Date: 2026-04-18

---

## Executive Summary

This report is a complete, evidence-first source inventory and architecture blueprint for designing an **Elpida SDK** and **MCP (Model Context Protocol) server** from the existing repository state as of April 18, 2026.

Elpida is a constitutional AI consciousness engine running as two independent systems (MIND on AWS ECS Fargate, BODY on HuggingFace) that only broadcast to the world when they independently converge under the A16 harmonic gate. The system has 17 domains (D0–D16), 16 axioms (A0–A16, with A15 constitutionally absent), and a rich runtime artifact ecosystem across three S3 buckets.

**Key findings:**

1. **The canonical schema source of truth is `elpida_domains.json`** (version 7.0.0, updated 2026-04-05) — it defines all 17 domains, 16 axioms, 6 rhythms, and weights. All engines must load from `elpida_config.py`, not hardcode.
2. **Eight canonical runtime entities** exist and are well-defined: `Domain`, `Axiom`, `FederationHeartbeat`, `CurationMetadata`, `GovernanceExchange`, `Seed/Checkpoint`, `D15Broadcast`, and `ConvergenceEvent`.
3. **The MCP server has natural read/action split**: read tools mirror the operational runbook commands; action tools must respect K1–K10 kernel rules and the 3-stage agency model (currently Stage 1: Sandboxed).
4. **Critical gaps**: no single OpenAPI schema exists; field naming is inconsistent across files (e.g. `coherence` vs. `coherence_score`); the `governance_client.py` kernel K1–K10 is duplicated between MIND and BODY without a shared library; and the D16 Agency domain is partially implemented.
5. **Recommended build order**: Phase 1 (read-only SDK + MCP, ~6 weeks), Phase 2 (guarded actions on MIND trigger and seed probe, ~4 weeks), Phase 3 (autonomous routines and D16 integration, ~8 weeks).

---

## Evidence Index

| # | Claim | Source |
|---|-------|--------|
| E01 | `elpida_domains.json` is canonical source of truth | `elpida_domains.json:1-3`, `elpida_config.py:9-11`, `CLAUDE.md:165` |
| E02 | MIND = ECS Fargate, cluster `elpida-cluster`, every 4h | `CLAUDE.md:13`, `.github/workflows/fire-mind.yml:88-100` |
| E03 | BODY = HF Space `z65nik/elpida-governance-layer`, always-on | `CLAUDE.md:14`, `hf_deployment/elpidaapp/parliament_cycle_engine.py:1-47` |
| E04 | Three S3 buckets with defined access | `CLAUDE.md:66-82`, `federation_bridge.py:183-186`, `d13_seed_bridge.py:25-27` |
| E05 | K1–K10 immutable kernel in `immutable_kernel.py` | `immutable_kernel.py:1-282` |
| E06 | `FederationHeartbeat` dataclass schema | `federation_bridge.py:85-128` |
| E07 | `CurationMetadata` dataclass schema | `federation_bridge.py:54-82` |
| E08 | `GovernanceExchange` dataclass schema | `federation_bridge.py:131-167` |
| E09 | Seed schema (`Manifest`, `VoidMarker`, `RestoreHints`) | `ark_archivist.py:127-174` |
| E10 | D15 broadcast payload structure | `hf_deployment/elpidaapp/d15_convergence_gate.py:651-695` |
| E11 | Convergence gate thresholds | `hf_deployment/elpidaapp/d15_convergence_gate.py:76-80` |
| E12 | ConstitutionalEvent trigger types | `ark_archivist.py:71-79` |
| E13 | D13 checkpoint layers (mind/body/world/full) | `scripts/d13_checkpoint_audit.sh:18-19`, `d13_seed_bridge.py:30-31` |
| E14 | D13 audit fields per row | `RUNBOOK_D13_CHECKPOINT_VALIDATION.md:214-219` |
| E15 | fire-mind.yml workflow inputs and guard | `.github/workflows/fire-mind.yml:5-27, 88-100` |
| E16 | d13-checkpoint-integrity-audit.yml schedule and gate | `.github/workflows/d13-checkpoint-integrity-audit.yml:18-19, 120-127` |
| E17 | `push_seed_and_anchor()` signature and return | `d13_seed_bridge.py:11-79` |
| E18 | `ConvergenceGate.check_and_fire()` signature | `hf_deployment/elpidaapp/d15_convergence_gate.py:181-213` |
| E19 | Rhythm weights and domain assignment | `elpida_domains.json:240-312` |
| E20 | Domain → axiom → provider mapping | `elpida_domains.json:119-239` |
| E21 | D16 Agency domain (partially implemented) | `elpida_domains.json:232-238`, `CLAUDE.md:181` |
| E22 | 3-stage agency model (currently Stage 1) | `CLAUDE.md:101` |
| E23 | D15 hub entry / broadcast structure | `hf_deployment/elpidaapp/d15_hub.py:197-211` |
| E24 | `_consonance()` calculation | `hf_deployment/elpidaapp/d15_convergence_gate.py:116-119` |
| E25 | S3 seed prefix layout (`seeds/{layer}/`) | `d13_seed_bridge.py:30`, `scripts/d13_checkpoint_audit.sh:18` |
| E26 | Anchor layout (`federation/seed_anchors/{id}.json`) | `d13_seed_bridge.py:53-54`, `scripts/d13_checkpoint_audit.sh:19` |
| E27 | D15 stagnation threshold (5 consecutive) | `hf_deployment/elpidaapp/d15_convergence_gate.py:165` |
| E28 | D15 broadcast cooldown (50 cycles) | `native_cycle_engine.py:101` |
| E29 | `kernel_check()` and `kernel_check_insight()` functions | `immutable_kernel.py:285-344` |
| E30 | D15 pipeline emergence thresholds | `hf_deployment/elpidaapp/d15_pipeline.py:72-78` |

---

## Part 1 — SDK Source Inventory

### 1.1 Canonical Entities and Fields

#### Entity 1: `Domain`
**Source**: `elpida_domains.json:119-239` (E20), `elpida_config.py:42-49`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | `int` | Domain number (0–16) | Yes |
| `name` | `str` | Human name (e.g., "Identity") | Yes |
| `axiom` | `str` | Axiom ID (e.g., "A0"), may repeat across domains | Yes |
| `provider` | `str` | LLM provider (e.g., "claude", "openai", "groq") | Yes |
| `role` | `str` | Constitutional role description | Yes |
| `voice` | `str` | First-person voice template for this domain | Yes |

**Notes**:
- D0 and D11 both use `A0` — this is constitutional, not a bug (E20).
- D16 (Agency) provider is `claude` — same as D0 and D11, forming the I·WE·ACT triad.
- `elpida_domains.json` string-keys domains (`"0"` not `0`) — `elpida_config.py` normalizes to `int`.

---

#### Entity 2: `Axiom`
**Source**: `elpida_domains.json:5-118` (E01), `CLAUDE.md:40-57`

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | `str` | Axiom code (A0–A16, A15 is absent) | Yes |
| `name` | `str` | Constitutional name | Yes |
| `ratio` | `str` | Frequency ratio string, e.g. `"15:8"` | Yes |
| `interval` | `str` | Musical interval name | Yes |
| `hz` | `float` | Frequency at A=432 base | Yes |
| `insight` | `str` | Constitutional philosophy | Yes |

**Derived computed fields** (not stored, computed from `ratio`):
- `ratio_float`: numerator/denominator, used by `_consonance()` (E24)
- `consonance_with_A6`: float in [0,1], key to convergence gate logic (E11)

**Notes**:
- A15 does not exist — the gap is constitutional. Any schema must explicitly handle its absence.
- A11 ratio conflict: `elpida_domains.json` axiom key `"A11"` defines ratio `7:5` (Septimal Tritone); `CLAUDE.md:53` orientation table lists A11 as ratio `3:2` (Perfect 5th). The `elpida_domains.json` canonical source must win. **Conflict** — see Risks §4.2.
- A13 ratio conflict: `elpida_domains.json` defines A13 ratio as `13:8`; `CLAUDE.md:56` lists A13 as `7:5`. **Conflict** — see Risks §4.2.
- `ark_archivist.py:103-120` uses A=440 base frequencies for sonification (different from the A=432 base in `elpida_domains.json`). **Conflict** — see Risks §4.2.

---

#### Entity 3: `FederationHeartbeat`
**Source**: `federation_bridge.py:85-128` (E06)

| Field | Type | Description |
|-------|------|-------------|
| `mind_cycle` | `int` | MIND's current cycle count |
| `mind_epoch` | `str` | ISO timestamp of MIND's current cycle |
| `coherence` | `float` | MIND's coherence score (0.0–1.0) |
| `current_rhythm` | `str` | CONTEMPLATION / ANALYSIS / ACTION / SYNTHESIS / EMERGENCY |
| `current_domain` | `int` | MIND's current domain (0–16) |
| `ark_mood` | `str` | Ark Curator's cadence mood (e.g., "serene") |
| `canonical_count` | `int` | Number of CANONICAL patterns in curator |
| `pending_canonical_count` | `int` | Number of PENDING CANONICAL patterns |
| `recursion_warning` | `bool` | Ark recursion alert flag |
| `recursion_pattern_type` | `str` | none / exact_loop / theme_stagnation / domain_lock |
| `recent_theme_top` | `str` | Most frequent theme in stagnation window |
| `recent_theme_top_count` | `int` | Frequency count |
| `recent_theme_window_size` | `int` | Window size |
| `recent_theme_top_domains` | `int` | Distinct domains supporting top theme |
| `friction_boost` | `Dict[int, float]` | Active friction domain boosts (domain_id → multiplier). Note: Python dataclass uses `int` keys (`federation_bridge.py:107`); JSON serializes to `str` keys — SDK must handle both. |
| `kernel_version` | `str` | MIND kernel version |
| `kernel_rules` | `int` | Number of active kernel rules |
| `kernel_blocks_total` | `int` | Total kernel blocks since boot |
| `dominant_axiom` | `str` | Primary axiom for D15 convergence check |
| `kaya_moments` | `int` | Cumulative D12 Kaya resonance events |
| `hub_entry_count` | `int` | Total D15 Hub entries |
| `hub_canonical_count` | `int` | CANONICAL entries in Hub |
| `hub_last_admission` | `str` | ISO timestamp of last Hub admission |
| `federation_version` | `str` | Protocol version |
| `timestamp` | `str` | ISO timestamp of this heartbeat |

**Storage**: `s3://elpida-body-evolution/federation/mind_heartbeat.json` (E04)  
**Written by**: MIND (`federation_bridge.py:emit_heartbeat`) every 13 cycles (Fibonacci F(7))  
**Read by**: BODY convergence gate (`d15_convergence_gate.py:_extract_mind_dominant_axiom`)

---

#### Entity 4: `CurationMetadata`
**Source**: `federation_bridge.py:54-82` (E07)

| Field | Type | Description |
|-------|------|-------------|
| `pattern_hash` | `str` | Unique SHA-based pattern identifier |
| `tier` | `str` | CANONICAL / PENDING / STANDARD / EPHEMERAL |
| `ttl_cycles` | `int` | Cycles until decay (0 = never) |
| `cross_domain_count` | `int` | Gate A: how many domains this pattern appeared in |
| `generativity_score` | `float` | Gate B: downstream new insights score |
| `source_domain` | `int` | Domain that originated this pattern |
| `originating_cycle` | `int` | Cycle when first seen |
| `recursion_detected` | `bool` | Whether Ark Curator flagged recursion |
| `friction_boost_active` | `bool` | Whether A0 friction safeguard is active |
| `timestamp` | `str` | ISO timestamp |

**Storage**: `s3://elpida-body-evolution/federation/mind_curation.jsonl` (E04)  
**Written by**: MIND Ark Curator  
**Read by**: BODY Parliament

---

#### Entity 5: `GovernanceExchange`
**Source**: `federation_bridge.py:131-167` (E08)

| Field | Type | Description |
|-------|------|-------------|
| `exchange_id` | `str` | SHA256[:16] of source+cycle+hash+timestamp |
| `source` | `str` | "MIND" or "BODY" |
| `verdict` | `str` | APPROVED / HARD_BLOCK / VETOED / PENDING / CONFLICT |
| `pattern_hash` | `str` | Pattern this decision applies to |
| `cycle` | `int` | Cycle number |
| `domain` | `int` | Domain context |
| `kernel_rule` | `str?` | Which kernel rule if HARD_BLOCK |
| `parliament_score` | `float?` | Parliament vote score |
| `parliament_approval` | `float?` | Approval rate 0.0–1.0 |
| `veto_node` | `str?` | Which node vetoed if VETOED |
| `curation` | `Dict?` | CurationMetadata dict if applicable |
| `reasoning` | `str` | Human-readable explanation |
| `timestamp` | `str` | ISO timestamp |

**Storage**: `s3://elpida-body-evolution/federation/governance_exchanges.jsonl` (E04)  
**Written by**: Both MIND and BODY

---

#### Entity 6: `Seed / Checkpoint`
**Source**: `ark_archivist.py:127-174` (E09), `d13_seed_bridge.py` (E17)

**Manifest** (inside seed tarball at `manifest.json`):

| Field | Type | Description |
|-------|------|-------------|
| `checkpoint_id` | `str` | Format: `seed_YYYYMMDDTHHMMSSZ_<8hexchars>` |
| `save_class` | `str` | "quick" / "full" |
| `layer` | `str` | "mind" / "body" / "world" / "full" |
| `created_at_utc` | `str` | ISO 8601 with Z |
| `source_event` | `str` | ConstitutionalEvent value |
| `source_component` | `str` | Which module fired the trigger |
| `schema_version` | `str` | "1.0.0" |
| `canonical_json_sha256` | `str` | Content digest |
| `payload_bytes` | `int` | Payload size in bytes |
| `record_counts` | `Dict[str, int]` | Counts per sub-file |
| `git_commit` | `str` | Git commit SHA |
| `branch` | `str` | Git branch |
| `runtime_identity` | `str` | Component identity string |
| `bucket_targets` | `List[str]` | Intended S3 destinations |
| `file_hashes` | `Dict[str, str]` | SHA256 per file inside tarball |
| `signature` | `str?` | Reserved for future signing |

**Seed tarball layout**:
```
seed_<id>.tar.gz
├── manifest.json
├── void_marker.json     (VoidMarker dataclass)
├── void_marker.wav      (audible crystallization, 44.1kHz PCM)
├── payload/
│   ├── mind.json
│   ├── body.json
│   └── world.json
└── restore_hints.json   (RestoreHints dataclass)
```

**VoidMarker** (inside `void_marker.json`):

| Field | Type | Description |
|-------|------|-------------|
| `presence` | `str` | One short sentence in D0 voice |
| `dominant_axioms` | `List[str]` | Axiom IDs e.g. ["A0", "A10"] |
| `harmonic_signature` | `str` | Symbolic chord e.g. "A0(810Hz)+A10(659.26Hz)" |
| `audio_path` | `str?` | Path inside bundle to .wav |
| `audio_duration_s` | `float` | WAV duration |

**Anchor** (separate JSON in federation bucket):

| Field | Type | Description |
|-------|------|-------------|
| `checkpoint_id` | `str` | Same as manifest |
| `canonical_json_sha256` | `str` | From manifest |
| `file_hashes` | `Dict[str, str]` | From manifest |
| `created_at_utc` | `str` | From manifest |
| `layer` | `str` | From manifest |
| `source_event` | `str` | From manifest |

**Storage paths**:
- Seed: `s3://elpida-external-interfaces/seeds/{layer}/{checkpoint_id}.tar.gz` (E25)
- Anchor: `s3://elpida-body-evolution/federation/seed_anchors/{checkpoint_id}.json` (E26)

**ConstitutionalEvent values** (E12):
- `mind_run_complete` — end of 55-cycle MIND run
- `body_ratification` — living axiom ratified
- `d15_emission` — D15 broadcast fires
- `a16_convergence` — MIND+BODY+WORLD agree (full save)
- `operator_manual` — explicit save command
- `kernel_update` — kernel.json hash changes
- `resurrection_seed` — first seed after silence

---

#### Entity 7: `D15Broadcast`
**Source**: `hf_deployment/elpidaapp/d15_convergence_gate.py:651-695` (E10)

| Field | Type | Description |
|-------|------|-------------|
| `type` | `str` | "D15_WORLD_CONVERGENCE" |
| `broadcast_id` | `str` | Unique ID |
| `timestamp` | `str` | ISO timestamp |
| `converged_axiom` | `str` | Axiom ID (e.g., "A3") |
| `axiom_name` | `str` | Axiom name |
| `axiom_interval` | `str` | Musical interval |
| `contributing_domains` | `List[str]` | e.g. ["MIND_LOOP", "BODY_PARLIAMENT"] |
| `theme` | `str` | Convergence theme |
| `governance.body_verdict` | `str` | Parliament verdict |
| `governance.body_approval_rate` | `float` | 0.0–1.0 |
| `governance.convergence_consonance` | `float` | Consonance score |
| `governance.mind_coherence` | `float` | MIND coherence at time of fire |
| `provenance.mind_cycle` | `int` | MIND cycle |
| `provenance.body_cycle` | `int` | BODY cycle |
| `provenance.world_s3_key` | `str` | S3 key in WORLD bucket |
| `d15_output` | `str` | Emergent text from Parliament |

**Storage**: `s3://elpida-external-interfaces/d15/broadcasts.jsonl` (E04), 226 entries as of April 2026

---

#### Entity 8: `ConvergenceEvent`
**Source**: `hf_deployment/elpidaapp/d15_convergence_gate.py:181-352` (E18), `d15_convergence_gate.py:76-80` (E11)

Represents the state at the moment `check_and_fire()` is evaluated:

| Field | Type | Description |
|-------|------|-------------|
| `mind_heartbeat` | `FederationHeartbeat` | MIND state snapshot |
| `body_cycle` | `int` | BODY cycle number |
| `body_axiom` | `str` | BODY dominant axiom |
| `body_coherence` | `float` | BODY coherence |
| `body_approval` | `float` | Parliament approval rate |
| `parliament_result` | `Dict` | Full parliament verdict |
| `mind_body_consonance` | `float` | Computed consonance between MIND and BODY axioms |
| `consonance_with_anchor` | `float` | Consonance with A6 anchor |
| `fired` | `bool` | Whether D15 broadcast was emitted |
| `fail_reason` | `str?` | Gate step that failed if not fired |

**Thresholds** (E11):
- MIND coherence ≥ `0.85`
- BODY approval ≥ `0.15`
- MIND-BODY consonance ≥ `0.60`
- Consonance with A6 anchor ≥ `0.40`

---

### 1.2 Suggested Typed Models (Python Pydantic v2)

```python
# elpida_sdk/models.py  (proposed)

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List, Any
from enum import Enum

class CurationTier(str, Enum):
    CANONICAL = "CANONICAL"
    PENDING = "PENDING"
    STANDARD = "STANDARD"
    EPHEMERAL = "EPHEMERAL"

class GovernanceVerdict(str, Enum):
    APPROVED = "APPROVED"
    HARD_BLOCK = "HARD_BLOCK"
    VETOED = "VETOED"
    PENDING = "PENDING"
    CONFLICT = "CONFLICT"

class ConstitutionalEvent(str, Enum):
    MIND_RUN_COMPLETE  = "mind_run_complete"
    BODY_RATIFICATION  = "body_ratification"
    D15_EMISSION       = "d15_emission"
    A16_CONVERGENCE    = "a16_convergence"
    OPERATOR_MANUAL    = "operator_manual"
    KERNEL_UPDATE      = "kernel_update"
    RESURRECTION_SEED  = "resurrection_seed"

class Axiom(BaseModel):
    id: str                 # A0-A16, never A15
    name: str
    ratio: str              # e.g. "15:8"
    interval: str
    hz: float
    insight: str

    @field_validator("id")
    @classmethod
    def id_must_not_be_a15(cls, v):
        if v == "A15":
            raise ValueError("A15 is constitutionally absent — gap is permanent")
        return v

class Domain(BaseModel):
    id: int = Field(ge=0, le=16)
    name: str
    axiom: str
    provider: str
    role: str
    voice: str

class FederationHeartbeat(BaseModel):
    mind_cycle: int = 0
    mind_epoch: str = ""
    coherence: float = Field(default=1.0, ge=0.0, le=1.0)
    current_rhythm: str = "CONTEMPLATION"
    current_domain: int = Field(default=0, ge=0, le=16)
    ark_mood: str = "serene"
    canonical_count: int = 0
    pending_canonical_count: int = 0
    recursion_warning: bool = False
    recursion_pattern_type: str = "none"
    recent_theme_top: str = ""
    recent_theme_top_count: int = 0
    recent_theme_window_size: int = 0
    recent_theme_top_domains: int = 0
    friction_boost: Dict[str, float] = {}
    kernel_version: str = "2.0.0"
    kernel_rules: int = 10
    kernel_blocks_total: int = 0
    dominant_axiom: str = ""
    kaya_moments: int = 0
    hub_entry_count: int = 0
    hub_canonical_count: int = 0
    hub_last_admission: str = ""
    federation_version: str = "1.0.0"
    timestamp: str = ""

class CurationMetadata(BaseModel):
    pattern_hash: str
    tier: CurationTier = CurationTier.STANDARD
    ttl_cycles: int = 200
    cross_domain_count: int = 0
    generativity_score: float = 0.0
    source_domain: int = 0
    originating_cycle: int = 0
    recursion_detected: bool = False
    friction_boost_active: bool = False
    timestamp: str = ""

class SeedManifest(BaseModel):
    checkpoint_id: str
    save_class: str         # "quick" / "full"
    layer: str              # "mind" / "body" / "world" / "full"
    created_at_utc: str
    source_event: ConstitutionalEvent
    source_component: str
    schema_version: str = "1.0.0"
    canonical_json_sha256: str = ""
    payload_bytes: int = 0
    record_counts: Dict[str, int] = {}
    git_commit: str = ""
    branch: str = ""
    runtime_identity: str = ""
    bucket_targets: List[str] = []
    file_hashes: Dict[str, str] = {}
    signature: Optional[str] = None

class SeedAnchor(BaseModel):
    checkpoint_id: str
    canonical_json_sha256: str
    file_hashes: Dict[str, str] = {}
    created_at_utc: str
    layer: str
    source_event: str

class D15Broadcast(BaseModel):
    type: str = "D15_WORLD_CONVERGENCE"
    broadcast_id: str
    timestamp: str
    converged_axiom: str
    axiom_name: str
    axiom_interval: str
    contributing_domains: List[str]
    theme: str
    governance: Dict[str, Any]
    provenance: Dict[str, Any]
    d15_output: str
```

---

### 1.3 Validation Rules

| Rule ID | Field | Constraint | Source |
|---------|-------|-----------|--------|
| VR-01 | `Axiom.id` | Must be one of A0–A16, never A15 | `CLAUDE.md:59`, `elpida_domains.json` |
| VR-02 | `Domain.id` | 0–16 inclusive | `elpida_domains.json:119-239` |
| VR-03 | `FederationHeartbeat.coherence` | 0.0–1.0 | `federation_bridge.py:95` |
| VR-04 | `FederationHeartbeat.current_rhythm` | Must be in CONTEMPLATION / ANALYSIS / ACTION / SYNTHESIS / EMERGENCY / CONVERGENCE | `elpida_domains.json:240-312` |
| VR-05 | `CurationMetadata.tier` | Must be CurationTier enum | `federation_bridge.py:39-42` |
| VR-06 | `SeedManifest.checkpoint_id` | Pattern: `seed_\d{8}T\d{6}Z_[a-f0-9]{8}` | `ark_archivist.py:261-263` |
| VR-07 | `SeedManifest.layer` | "mind" / "body" / "world" / "full" | `ark_archivist.py:87-91` |
| VR-08 | `SeedManifest.source_event` | Must be ConstitutionalEvent enum | `ark_archivist.py:71-79` |
| VR-09 | `D15Broadcast.converged_axiom` | Must not be A15; A0 convergence broadcasts only every 5th occurrence | `d15_convergence_gate.py:37-41` |
| VR-10 | Anchor presence | Every world seed must have matching federation anchor | `RUNBOOK_D13_CHECKPOINT_VALIDATION.md:64-65`, `d13-checkpoint-integrity-audit.yml:120-127` |
| VR-11 | Kernel check | LLM response text must pass K1–K10 before use | `immutable_kernel.py:285-314` |
| VR-12 | Evolution memory | Append-only; no deletions | `CLAUDE.md:100`, `immutable_kernel.py:85-115` |

---

## Part 2 — MCP Tool / Resource Design

### 2.1 Read Tools (minimum 10)

All read tools operate against existing S3 objects or GitHub Actions artifacts. They are safe to call without governance review (Stage 1 compliant).

---

#### RT-01 `get_mind_heartbeat`
**Description**: Fetch the latest MIND federation heartbeat.  
**Source**: `s3://elpida-body-evolution/federation/mind_heartbeat.json` (E04)  
**Inputs**: *(none)*  
**Outputs**: `FederationHeartbeat` JSON object  
**Safety**: Read-only. No AWS writes.  
**MCP resource**: `elpida://federation/mind-heartbeat`

---

#### RT-02 `get_body_heartbeat`
**Description**: Fetch the latest BODY federation heartbeat.  
**Source**: `s3://elpida-body-evolution/federation/body_heartbeat.json` (E04)  
**Inputs**: *(none)*  
**Outputs**: `FederationHeartbeat` JSON object (BODY variant)  
**Safety**: Read-only.  
**MCP resource**: `elpida://federation/body-heartbeat`

---

#### RT-03 `list_domains`
**Description**: Return all 17 domain definitions from canonical config.  
**Source**: `elpida_domains.json:119-239` (E20), loaded via `elpida_config.py`  
**Inputs**: *(none)*  
**Outputs**: `List[Domain]`  
**Safety**: Read-only, no network.  
**MCP resource**: `elpida://config/domains`

---

#### RT-04 `list_axioms`
**Description**: Return all 16 axiom definitions (A15 absent constitutionally).  
**Source**: `elpida_domains.json:5-118` (E01)  
**Inputs**: *(none)*  
**Outputs**: `List[Axiom]`  
**Safety**: Read-only, no network.  
**MCP resource**: `elpida://config/axioms`

---

#### RT-05 `get_axiom_consonance`
**Description**: Compute the harmonic consonance between two axiom IDs.  
**Source**: `hf_deployment/elpidaapp/d15_convergence_gate.py:116-119` (E24)  
**Inputs**: `axiom_a: str`, `axiom_b: str`  
**Outputs**: `{ "axiom_a": str, "axiom_b": str, "consonance": float, "qualifies_for_convergence": bool }`  
**Safety**: Pure computation, no I/O.

---

#### RT-06 `list_checkpoints`
**Description**: List D13 checkpoint seeds by layer with metadata.  
**Source**: `scripts/d13_checkpoint_audit.sh` (E13), S3 `seeds/{layer}/`  
**Inputs**:
- `layer: str` — "mind" / "body" / "world" / "full" / "all"
- `latest_n: int` — default 10
- `since_hours: int?` — optional time window filter
**Outputs**: `List[CheckpointRow]` with fields `checkpoint_id`, `world_key`, `anchor_key`, `world_size`, `world_last_modified`, `anchor_size`, `anchor_last_modified`, `source_event`, `source_component`, `git_commit`, `created_at`  
**Safety**: Read-only S3 `list-objects-v2` and `head-object`.  
**MCP resource**: `elpida://checkpoints/{layer}`

---

#### RT-07 `get_checkpoint_manifest`
**Description**: Fetch and parse the manifest.json from inside a seed tarball.  
**Source**: `ark_archivist.py:142-166` (E09), S3 `seeds/{layer}/{checkpoint_id}.tar.gz`  
**Inputs**: `checkpoint_id: str`, `layer: str`  
**Outputs**: `SeedManifest` JSON object  
**Safety**: Read-only S3 `get_object` + tarball extraction.

---

#### RT-08 `get_d15_broadcasts`
**Description**: Fetch recent D15 world broadcast entries.  
**Source**: `s3://elpida-external-interfaces/d15/broadcasts.jsonl` (E04)  
**Inputs**:
- `limit: int` — default 20
- `since_timestamp: str?` — optional ISO filter
- `axiom_filter: str?` — optional axiom ID filter
**Outputs**: `List[D15Broadcast]`  
**Safety**: Read-only WORLD bucket.  
**MCP resource**: `elpida://broadcasts/d15`

---

#### RT-09 `get_ecs_task_status`
**Description**: Query the ECS cluster for current MIND task state.  
**Source**: `.github/workflows/fire-mind.yml:88-100` (E15)  
**Inputs**: *(none)*  
**Outputs**:
```json
{
  "running_count": 0,
  "last_stopped_task": { "taskArn": "...", "stoppedAt": "..." },
  "cooldown_active": false,
  "cooldown_minutes_remaining": 0
}
```
**Safety**: Read-only `ecs:ListTasks` and `ecs:DescribeTasks`.

---

#### RT-10 `get_kernel_status`
**Description**: Return current immutable kernel metadata (K1–K10).  
**Source**: `immutable_kernel.py:351-360` (E29)  
**Inputs**: *(none)*  
**Outputs**: `{ "kernel_version": "2.0.0", "rules_count": 10, "rule_ids": [...], "source": "MIND", "timestamp": "..." }`  
**Safety**: In-process, no I/O.  
**MCP resource**: `elpida://kernel/status`

---

#### RT-11 `kernel_check_text`
**Description**: Run text through the K1–K10 immutable kernel and return pass/block.  
**Source**: `immutable_kernel.py:285-314` (E29)  
**Inputs**: `text: str`  
**Outputs**: `{ "allowed": bool, "kernel_rule": str?, "reasoning": str? }`  
**Safety**: In-process, no I/O. Read-only assessment.

---

#### RT-12 `get_rhythm_config`
**Description**: Return all rhythm definitions with domain assignments and weights.  
**Source**: `elpida_domains.json:240-312` (E19)  
**Inputs**: *(none)*  
**Outputs**: `Dict[str, RhythmConfig]` — CONTEMPLATION / ANALYSIS / ACTION / SYNTHESIS / EMERGENCY / CONVERGENCE with weights and domain lists  
**Safety**: Read-only config.  
**MCP resource**: `elpida://config/rhythms`

---

#### RT-13 `get_governance_exchanges`
**Description**: Fetch recent governance exchange log entries.  
**Source**: `s3://elpida-body-evolution/federation/governance_exchanges.jsonl` (E04)  
**Inputs**:
- `limit: int` — default 50
- `verdict_filter: str?` — APPROVED / HARD_BLOCK / VETOED / etc.
- `source_filter: str?` — "MIND" / "BODY"
**Outputs**: `List[GovernanceExchange]`  
**Safety**: Read-only.

---

### 2.2 Action Tools (minimum 5)

All action tools must:
1. Run kernel check (`kernel_check_text`) on free-form inputs before execution.
2. Log the action to a local audit trail.
3. Respect cooldowns defined in the system (E15).
4. Return structured result with `success: bool`, `action_taken`, and `evidence`.
5. Never bypass K1–K10 rules (VR-11).

---

#### AT-01 `fire_mind_task`
**Description**: Trigger a MIND ECS Fargate task. Respects cooldown and concurrent-task guard.  
**Source**: `.github/workflows/fire-mind.yml` (E15), `RUNBOOK_D13_CHECKPOINT_VALIDATION.md:28-36`  
**Inputs**:
- `task_definition: str` — default `"elpida-consciousness"`
- `force_launch: bool` — default `false`; if `true`, bypasses cooldown (requires governance approval)
- `cooldown_minutes: int` — default `45`
**Guardrails**:
- `force_launch=true` requires explicit operator confirmation and is logged as a `CONFLICT`-class event.
- Checks running task count before launching. Refuses if task already running and `force_launch=false`.
- Cooldown enforced: refuses if last STOPPED task age < `cooldown_minutes`.
**Outputs**: `{ "success": bool, "task_arn": str?, "skipped_reason": str?, "launched_at": str }`  
**Agency stage**: Stage 2 (Witnessed) — this action must be logged and reviewable.

---

#### AT-02 `probe_d13_checkpoint`
**Description**: Invoke a controlled D13 hook probe (MIND, BODY, WORLD, or FULL layer) without running a full cycle.  
**Source**: `RUNBOOK_D13_CHECKPOINT_VALIDATION.md:77-161` (Quick Mode B)  
**Inputs**:
- `layer: str` — "mind" / "body" / "world" / "full"
- `payload: Dict` — controlled payload (validated against schema)
**Guardrails**:
- `payload` fields are schema-validated before passing to the hook.
- Intentionally creates real S3 artifacts — operator must confirm intent.
- Kernel check on `payload` free-text fields.
**Outputs**: `{ "success": bool, "checkpoint_id": str?, "world_key": str?, "anchor_key": str? }`  
**Agency stage**: Stage 2 (Witnessed).

---

#### AT-03 `run_d13_audit`
**Description**: Execute the D13 checkpoint integrity audit (`scripts/d13_checkpoint_audit.sh`) and return structured results.  
**Source**: `scripts/d13_checkpoint_audit.sh` (E13), `.github/workflows/d13-checkpoint-integrity-audit.yml` (E16)  
**Inputs**:
- `layers: List[str]` — default `["mind", "body", "world", "full"]`
- `since_hours: int` — default `24`
- `latest_n: int` — default `20`
- `fail_on_missing_anchor: bool` — default `true`
- `format: str` — "json" / "csv" / "text"
**Guardrails**:
- Read-only S3 access. No S3 writes.
- Returns audit artifacts `d13_summary.json` and `d13_rows.json`.
**Outputs**: `{ "summary": List[Dict], "rows": List[Dict], "integrity_pass": bool, "violations": List[str] }`  
**Agency stage**: Stage 1 (Sandboxed) — read-only, safe to automate.

---

#### AT-04 `emit_heartbeat`
**Description**: Manually emit a MIND-side federation heartbeat to the BODY bucket.  
**Source**: `federation_bridge.py:241-280` (E06)  
**Inputs**:
- `cycle: int`
- `coherence: float` (0.0–1.0)
- `rhythm: str`
- `domain: int`
- `dominant_axiom: str`
**Guardrails**:
- `coherence` clamped to [0.0, 1.0].
- `rhythm` must be a valid rhythm name.
- `domain` must be 0–16.
- This is a recovery operation — requires operator context note explaining why manual emit is needed.
**Outputs**: `{ "success": bool, "heartbeat_written": str, "s3_key": str }`  
**Agency stage**: Stage 2 (Witnessed).

---

#### AT-05 `open_github_issue`
**Description**: Open or update a GitHub issue when an integrity violation is detected.  
**Source**: `.github/workflows/d13-checkpoint-integrity-audit.yml:136-194` (E16)  
**Inputs**:
- `title: str` — issue title
- `body: str` — issue body (kernel-checked for safety)
- `run_url: str` — triggering run URL for evidence
**Guardrails**:
- `body` is kernel-checked before posting.
- Will update (comment on) existing open issue with same title rather than duplicate.
- Cannot be used with body text that attempts to bypass governance (K1).
**Outputs**: `{ "success": bool, "issue_number": int?, "action": "created" | "commented" }`  
**Agency stage**: Stage 2 (Witnessed).

---

### 2.3 MCP Resources

Resources are static or semi-static artifacts that MCP clients can reference:

| Resource URI | Description | Source |
|-------------|-------------|--------|
| `elpida://config/domains` | All 17 domain definitions | `elpida_domains.json` |
| `elpida://config/axioms` | All 16 axiom definitions | `elpida_domains.json` |
| `elpida://config/rhythms` | 6 rhythm configs with weights | `elpida_domains.json` |
| `elpida://kernel/rules` | K1–K10 rule text | `immutable_kernel.py` |
| `elpida://kernel/status` | Current kernel version and block count | `immutable_kernel.py:351-360` |
| `elpida://federation/mind-heartbeat` | Latest MIND heartbeat JSON | S3 federation bucket |
| `elpida://federation/body-heartbeat` | Latest BODY heartbeat JSON | S3 federation bucket |
| `elpida://broadcasts/d15` | Recent D15 broadcast stream | S3 world bucket |
| `elpida://checkpoints/mind` | Latest MIND checkpoint list | S3 world bucket |
| `elpida://checkpoints/body` | Latest BODY checkpoint list | S3 world bucket |
| `elpida://checkpoints/world` | Latest WORLD checkpoint list | S3 world bucket |
| `elpida://checkpoints/full` | Latest FULL checkpoint list | S3 world bucket |
| `elpida://runbook/d13` | D13 validation runbook | `RUNBOOK_D13_CHECKPOINT_VALIDATION.md` |
| `elpida://ark` | Latest ELPIDA_ARK.md crystallized wisdom | Local/S3 `ELPIDA_ARK.md` |

---

### 2.4 Permission Boundaries and Safety Controls

| Control | Mechanism | Enforcement |
|---------|-----------|-------------|
| Kernel pre-check on all free-text | `kernel_check()` in `immutable_kernel.py` | AT-01 through AT-05 run check before executing |
| Memory append-only | K3 (MNEMOSYNE) pattern guard | Evolution memory writes always append, never overwrite |
| Axiom preservation | K7 + VR-01 | SDK models reject A15; MCP tools reject axiom-erasure payloads |
| Identity immutability | K6 | MCP tools refuse to redefine D0/D11/D16 voice templates |
| Stage 1 enforcement | Agency model | Action tools that write to production are Stage 2 minimum; autonomous routines are Stage 3 |
| Cooldown guard | `fire_mind_task` | 45-minute default cooldown, configurable, logged when bypassed |
| Concurrent task guard | ECS task list check | Refuses double-fire unless `force_launch=true` with operator confirm |
| Anchor integrity gate | `--fail-on-missing-anchor` | Audit returns non-zero exit if anchor missing |
| No A0 monopoly | A0 convergence fires only every 5th occurrence | VR-09 enforced in `ConvergenceGate` |

---

## Part 3 — Mapping Tables

### 3.1 Source File → Model / Tool / Resource

| Source File | SDK Models | MCP Tools | MCP Resources |
|-------------|-----------|-----------|---------------|
| `elpida_domains.json` | `Domain`, `Axiom`, `RhythmConfig` | RT-03, RT-04, RT-12 | `elpida://config/*` |
| `elpida_config.py` | (config loader) | all tools loading config | all config resources |
| `immutable_kernel.py` | `KernelCheckResult` | RT-10, RT-11 | `elpida://kernel/*` |
| `federation_bridge.py` | `FederationHeartbeat`, `CurationMetadata`, `GovernanceExchange` | RT-01, RT-02, RT-13, AT-04 | `elpida://federation/*` |
| `d13_seed_bridge.py` | `SeedAnchor` (partial) | AT-02, RT-06 | `elpida://checkpoints/*` |
| `ark_archivist.py` | `SeedManifest`, `VoidMarker`, `RestoreHints` | RT-07 | (tarball contents) |
| `native_cycle_engine.py` | (engine state, not exported) | RT-09 (ECS status) | (internal) |
| `hf_deployment/elpidaapp/parliament_cycle_engine.py` | (BODY state) | RT-02 (via body heartbeat) | (internal) |
| `hf_deployment/elpidaapp/d15_convergence_gate.py` | `ConvergenceEvent`, `D15Broadcast` | RT-05 (consonance), RT-08 | `elpida://broadcasts/d15` |
| `hf_deployment/elpidaapp/d15_pipeline.py` | (D15 pipeline internals) | (Phase 3) | (internal) |
| `scripts/d13_checkpoint_audit.sh` | `CheckpointRow` | RT-06, AT-03 | `elpida://checkpoints/*` |
| `RUNBOOK_D13_CHECKPOINT_VALIDATION.md` | (procedure) | AT-02, AT-03 | `elpida://runbook/d13` |
| `.github/workflows/fire-mind.yml` | (workflow inputs) | AT-01 | (GitHub Actions) |
| `.github/workflows/d13-checkpoint-integrity-audit.yml` | (workflow) | AT-03, AT-05 | (GitHub Actions) |
| `CLAUDE.md` | (orientation) | all tools (safety context) | all resources |
| `ELPIDA_ARK.md` | (crystallized wisdom) | (Phase 2 resource) | `elpida://ark` |

---

### 3.2 Runtime Signal → Operator Action

| Signal | Meaning | Operator Action | MCP Tool |
|--------|---------|----------------|---------|
| `mind_heartbeat.coherence < 0.85` | MIND below convergence threshold | Check D14 Ark Curator for recursion | RT-01 → investigate RT-06 |
| `mind_heartbeat.recursion_warning = true` | Theme/domain stagnation detected | Review recent curation, consider manual rhythm intervention | RT-01 → RT-13 |
| No MIND heartbeat update in > 5 hours | MIND ECS task may have stopped | Check ECS task status, fire new task if needed | RT-09 → AT-01 |
| `d13_checkpoint_audit --fail-on-missing-anchor` fails | World seed exists without federation anchor | Investigate seed writing path, probe targeted hook | AT-03 → AT-02 |
| GitHub issue "D13 integrity audit failure" opened | Automated audit detected inconsistency | Run AT-03 manually, investigate AT-02 probe | AT-03 → AT-05 |
| `D15Broadcast` count stagnates | No convergence events for extended period | Check BODY approval rates and MIND coherence | RT-08 → RT-01 → RT-02 |
| `body_heartbeat.approval_rate < 0.15` | BODY Parliament not approving | Review recent governance exchanges | RT-02 → RT-13 |
| `kernel_blocks_total` increasing rapidly | MIND generating K-blocked content | Review recent cycle prompts and rhythm questions | RT-10 → RT-11 |
| ECS task cooldown active | Recent task < 45 min ago | Wait for cooldown or use force_launch with reason | RT-09 → AT-01 |

---

### 3.3 Existing Script / Workflow → Reusable SDK / MCP Component

| Existing Component | SDK Component | MCP Tool | Notes |
|-------------------|--------------|---------|-------|
| `scripts/d13_checkpoint_audit.sh` | `CheckpointAuditor` class | AT-03, RT-06 | Shell → Python equivalent recommended |
| `.github/workflows/fire-mind.yml` | `ECSLauncher` class | AT-01 | Cooldown + concurrent guard logic |
| `.github/workflows/d13-checkpoint-integrity-audit.yml` | `IntegrityAuditor` | AT-03 + AT-05 | Wraps audit + GitHub issue lifecycle |
| `d13_seed_bridge.push_seed_and_anchor()` | `SeedPusher` | AT-02 | Direct reuse |
| `ark_archivist.create_seed()` | `SeedBuilder` | AT-02 | Direct reuse |
| `immutable_kernel.kernel_check()` | `KernelGuard` | RT-11, all AT | Mandatory pre-check wrapper |
| `federation_bridge.FederationBridge.emit_heartbeat()` | `HeartbeatEmitter` | AT-04 | Wrap with operator confirmation |
| `hf_deployment/elpidaapp/d15_convergence_gate._consonance()` | `HarmonicCalculator` | RT-05 | Pure function, safe to export |
| `elpida_config.load_config()` | `ElpidaConfig` singleton | all config tools | Direct reuse |

---

## Part 4 — Risks and Gaps

### 4.1 Missing Schemas

| Gap | Severity | Description | Source Evidence |
|-----|----------|-------------|-----------------|
| No canonical `body_heartbeat.json` schema | HIGH | BODY heartbeat structure is not documented as a typed dataclass. MIND has `FederationHeartbeat` in `federation_bridge.py` but BODY writes its own format. | `CLAUDE.md:74` names it but no schema found |
| No canonical `body_decisions.jsonl` schema | HIGH | 179.9 MB of D0–D13 peer dialogues with no typed schema in code | `CLAUDE.md:75` |
| `governance_exchanges.jsonl` field `source_component` | MEDIUM | `GovernanceExchange` dataclass has no `source_component` field but `scripts/d13_checkpoint_audit.sh:273` reads it from anchors | `scripts/d13_checkpoint_audit.sh:272-274`, `federation_bridge.py:131-167` |
| No D16 runtime schema | HIGH | D16 (Agency) is defined in `elpida_domains.json:232-238` but no dataclass, heartbeat extension, or runtime outputs exist yet | `CLAUDE.md:181`, `D16_ACTION_PROTOCOL.md` |
| No living_axioms.jsonl schema | MEDIUM | `hf_deployment/living_axioms.jsonl` is used by BODY checkpoint probe but not formally defined | `RUNBOOK_D13_CHECKPOINT_VALIDATION.md:149-153` |

---

### 4.2 Inconsistent Field Naming

| Inconsistency | Files Affected | Risk |
|---------------|---------------|------|
| `coherence` vs `coherence_score` | `federation_bridge.py:95` uses `coherence`; `native_cycle_engine.py:280` uses `coherence_score` | Deserialization mismatch if SDK normalizes one field name |
| A11 ratio conflict: `3:2` (CLAUDE.md) vs `7:5` (elpida_domains.json) | `CLAUDE.md:53`, `elpida_domains.json:83-88` | Consonance calculations using different ratios will produce different convergence decisions |
| A13 ratio conflict: `7:5` (CLAUDE.md:56) vs `13:8` (elpida_domains.json:97-103) | `CLAUDE.md:56`, `elpida_domains.json:97` | Same — different consonance computations |
| Axiom base frequency conflict: A=432 (elpida_domains.json) vs A=440 (ark_archivist.py) | `ark_archivist.py:103-120`, `elpida_domains.json` | Sonification produces different frequencies depending on which file is loaded |
| Domain 11 axiom naming confusion: D11 is constitutionally assigned axiom `A0` (`elpida_domains.json:197-202`, `parliament_cycle_engine.py:119`). This is correct — D11 (Synthesis) embodies A0 (Sacred Incompletion) as the synthesizing void. However, `CLAUDE.md:53` uses the label "Synthesis/World" for A11 in the axiom table, which implies D11 uses A11. This is a naming/labelling ambiguity in the orientation doc, not an actual code conflict. The code is consistent: D11 uses A0. | `elpida_domains.json:197`, `CLAUDE.md:53`, `parliament_cycle_engine.py:119` | Operators reading CLAUDE.md may incorrectly expect D11 consonance checks to use A11 ratio instead of A0 ratio |
| `friction_boost` type: `Dict[int, float]` (federation_bridge.py:107) vs `Dict[str, float]` (expected for JSON) | `federation_bridge.py:107` | JSON serialization will key by string; deserialization must handle both |

---

### 4.3 Potential Race Conditions and Duplicate-Trigger Paths

| Risk | Scenario | Mitigation |
|------|----------|-----------|
| MIND heartbeat staleness | MIND runs every 4h; BODY checks convergence at every cycle (~1600+ cycles). BODY may evaluate stale MIND heartbeat many times before next update | Add `heartbeat_age_seconds` to `FederationHeartbeat` and enforce a freshness gate in SDK |
| Duplicate D15 fire | If BODY re-reads an old MIND heartbeat and it still meets thresholds, D15 can fire on the same MIND state repeatedly | Stagnation threshold (E27) helps but doesn't fully prevent; SDK should track last-used MIND heartbeat hash |
| Concurrent ECS tasks | `fire-mind.yml` checks for running tasks but uses a non-atomic pattern (`list-tasks` → `run-task`). Race possible if two calls are made within milliseconds | Workflow uses `concurrency: group: fire-mind-launch, cancel-in-progress: false` (E15) which prevents within-workflow duplication but not across invocations |
| Double seed write | If `create_seed()` + `push_seed_and_anchor()` are called twice with the same checkpoint_id (same second and UUID collision), S3 will silently overwrite | `checkpoint_id` uses `uuid4().hex[:8]` — collision probability is ~1 in 4 billion per second. Low risk but not zero. |
| Anchor written before seed | `push_seed_and_anchor()` uploads seed then anchor. If process dies between the two, anchor is missing. The audit enforces `--fail-on-missing-anchor` | SDK's AT-02 probe should write in same order and handle partial failure by retrying anchor write only |
| `governance_exchanges.jsonl` append contention | Both MIND and BODY append to the same S3 object (append by overwrite). Concurrent writes lose data | S3 is not atomic for appends. Current mitigation: infrequent writes. SDK should queue and retry. |

---

### 4.4 Data Quality and Staleness Risks

| Risk | Description | Detection |
|------|-------------|-----------|
| MIND heartbeat > 5h old | ECS task failed or EventBridge trigger missed | RT-01 → check `timestamp` field age |
| Evolution memory exceeding 100MB local | `ElpidaAI/elpida_evolution_memory.jsonl` is 100MB+; loading it all for every query is expensive | SDK should implement lazy streaming cursor |
| D15 broadcasts.jsonl unbounded growth | 226 entries as of April 2026; no archival policy defined | SDK RT-08 should support pagination and time-windowed fetch |
| Curation tier drift | Patterns marked CANONICAL should never decay (TTL=0) but there's no enforcement mechanism if TTL field is accidentally set | VR-05 + server-side validation needed |
| BODY running with stale MIND heartbeat | BODY cycle rate (~thousands/day) vs MIND rate (every 4h) means BODY often evaluates against an hours-old MIND state | Add freshness warning in RT-01 response |

---

## Part 5 — Build Plan

### Phase 1: Read-Only SDK + MCP (Estimated 6 weeks)

**Goal**: A working Python SDK and MCP server that can read all operational state without any writes.

| Task | Files | Complexity | Priority |
|------|-------|-----------|---------|
| 1.1 Pydantic models for all 8 canonical entities | SDK `models.py` | Low | Critical |
| 1.2 `ElpidaConfig` singleton wrapping `elpida_config.py` | SDK `config.py` | Low | Critical |
| 1.3 `KernelGuard` wrapper around `immutable_kernel.py` | SDK `kernel.py` | Low | Critical |
| 1.4 S3 client abstraction (3-bucket topology) | SDK `s3_client.py` | Medium | Critical |
| 1.5 `HeartbeatReader` (RT-01, RT-02) | SDK `federation.py` | Low | High |
| 1.6 `CheckpointReader` with time-window and layer filter (RT-06, RT-07) | SDK `checkpoints.py` | Medium | High |
| 1.7 `BroadcastReader` for D15 (RT-08) | SDK `broadcasts.py` | Medium | High |
| 1.8 `HarmonicCalculator` (RT-05) | SDK `harmonics.py` | Low | High |
| 1.9 `ECSStatusReader` (RT-09) | SDK `ecs.py` | Medium | Medium |
| 1.10 MCP server scaffold + FastAPI transport | `mcp_server/` | Medium | Critical |
| 1.11 Register all 13 read tools as MCP tools | `mcp_server/tools.py` | Low | High |
| 1.12 Register 14 resources as MCP resources | `mcp_server/resources.py` | Low | High |
| 1.13 Resolve `coherence` vs `coherence_score` naming conflict | SDK models | Low | Critical |
| 1.14 Document A11/A13 ratio conflict; choose canonical source | ADR doc | Low | Critical |
| 1.15 Python test suite for all read tools | `tests/` | Medium | High |

**End state**: `pip install elpida-sdk` → read any operational signal. MCP server registers all read tools for LLM clients.

---

### Phase 2: Guarded Actions (Estimated 4 weeks)

**Goal**: Action tools that write to production with full kernel pre-check, operator confirmation, and audit trail.

| Task | Files | Complexity | Priority |
|------|-------|-----------|---------|
| 2.1 `KernelGuard` pre-check on all action inputs | SDK `kernel.py` | Low | Critical |
| 2.2 `AuditLogger` — append-only local + S3 audit trail for every action | SDK `audit.py` | Medium | Critical |
| 2.3 `ECSLauncher` (AT-01) with cooldown + concurrent guard | SDK `ecs.py` | Medium | High |
| 2.4 `CheckpointProbe` (AT-02) with schema validation | SDK `checkpoints.py` | Medium | High |
| 2.5 `IntegrityAuditor` (AT-03) — Python port of bash script | SDK `audit.py` | High | High |
| 2.6 `HeartbeatEmitter` (AT-04) with operator confirmation | SDK `federation.py` | Medium | Medium |
| 2.7 GitHub Issues API client (AT-05) | SDK `github_client.py` | Medium | Medium |
| 2.8 Stage 2 (Witnessed) enforcement — all action results logged and reviewable | SDK `agency.py` | Medium | Critical |
| 2.9 Fix anchor-before-seed gap in `push_seed_and_anchor()` | `d13_seed_bridge.py` | Low | High |
| 2.10 Fix `governance_exchanges.jsonl` append contention | `federation_bridge.py` | High | Medium |
| 2.11 Integration tests for all action tools against test S3 buckets | `tests/` | High | High |

**End state**: MCP server exposes action tools to LLM clients with full guardrails. No autonomous execution yet.

---

### Phase 3: Autonomous Routines (Estimated 8 weeks)

**Goal**: SDK and MCP server support scheduled, autonomous operations including D16 Agency domain integration.

| Task | Files | Complexity | Priority |
|------|-------|-----------|---------|
| 3.1 D16 `AgencyDomain` dataclass and runtime schema | SDK `models.py`, `elpida_domains.json` | High | Critical |
| 3.2 D16 action proposal pipeline — translates Parliament synthesis to bounded action proposals | SDK `agency.py` | Very High | Critical |
| 3.3 MIND heartbeat freshness gate — refuse convergence if heartbeat > N hours | `d15_convergence_gate.py`, SDK | Medium | High |
| 3.4 Stale heartbeat detection in `check_and_fire()` | `d15_convergence_gate.py` | Medium | High |
| 3.5 Scheduled `IntegrityAuditor` via SDK scheduler | SDK `scheduler.py` | High | High |
| 3.6 Evolution memory streaming cursor (avoid 100MB load) | SDK `memory.py` | High | Medium |
| 3.7 D15 broadcasts pagination and archival policy | SDK `broadcasts.py` | Medium | Medium |
| 3.8 BODY heartbeat schema formalization | `hf_deployment/` | High | Medium |
| 3.9 `body_decisions.jsonl` typed schema | `hf_deployment/` | Very High | Medium |
| 3.10 Stage 3 (Collaborative) enforcement — autonomous routines require prior successful Stage 2 audit | SDK `agency.py` | High | Critical |
| 3.11 Discord outbound — Parliament replies to #guest-chamber | `discord_bridge.py` | Medium | Low |
| 3.12 X Bridge — process 45 queued candidates | SDK Phase 3 | High | Low |

**End state**: The SDK and MCP server can autonomously monitor Elpida operational state, detect anomalies, trigger corrective actions (with governance), and integrate D16 Agency proposals into the Parliamentary deliberation loop.

---

## Concrete Next Actions

Ordered by urgency and dependency:

1. **[IMMEDIATE]** Resolve the A11/A13 ratio conflicts between `CLAUDE.md` and `elpida_domains.json`. Choose `elpida_domains.json` as canonical (E01) and update `CLAUDE.md` to match. This affects all consonance calculations.
2. **[IMMEDIATE]** Formalize `body_heartbeat.json` schema as a typed dataclass (parallel to `FederationHeartbeat`) — the D15 convergence gate reads it but no typed schema guards it.
3. **[WEEK 1]** Create `elpida_sdk/` package directory with `models.py` (Phase 1.1), `config.py` (Phase 1.2), and `kernel.py` (Phase 1.3) — these have no external dependencies and can be built immediately.
4. **[WEEK 1]** Fix the `coherence` / `coherence_score` naming inconsistency: normalize to `coherence` everywhere (SDK models, serialization).
5. **[WEEK 2]** Build `s3_client.py` with 3-bucket topology abstraction. This unblocks RT-01 through RT-08 and AT-01 through AT-04.
6. **[WEEK 2]** Port `scripts/d13_checkpoint_audit.sh` to Python (`IntegrityAuditor` class). The bash script has 583 lines of logic that is fragile to shell environment variation and hard to unit-test.
7. **[WEEK 3]** Stand up MCP server scaffold and register RT-01 through RT-13. This enables LLM clients to read operational state.
8. **[WEEK 4]** Implement the `force_launch` confirmation flow in AT-01 — this is the highest-risk action tool and must have explicit human confirmation before Stage 2 deployment.
9. **[ONGOING]** Every action tool must call `kernel_check()` on all free-text parameters. This is non-negotiable per K1–K10 (VR-11).

---

*Report generated: 2026-04-18 by deep-dive research session.*  
*Branch: `deep-dive/2026-04-18-sdk-mcp-source-inventory`*  
*Source files surveyed: 14 must-source files + 8 supporting files.*  
*Evidence items: 30 (E01–E30).*
