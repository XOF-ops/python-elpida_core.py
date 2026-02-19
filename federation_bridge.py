"""
Elpida Federation Bridge — MIND ↔ BODY Governance Protocol
═══════════════════════════════════════════════════════════

The Federated architecture: Both MIND and BODY keep sovereignty.
FederationBridge mediates governance metadata exchange via the BODY S3 bucket.

Architecture Decision: FEDERATED (Feb 19, 2026)
"Seed contains genome, not the full organism. Growth, not stasis."

This module handles:
1. CurationVerdict schema — shared metadata format for pattern curation
2. Federation state — unified cycle counter, governance sync
3. MIND→BODY curation writes — push curation metadata to BODY bucket
4. BODY→MIND governance reads — pull governance decisions from BODY bucket
5. Conflict mediation — when MIND and BODY disagree

The BODY bucket (elpida-body-evolution) is the federation channel.
Both sides write to it. Both sides read from it.
"""

import json
import os
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
from pathlib import Path

logger = logging.getLogger("elpida.federation")

# ════════════════════════════════════════════════════════════════════
# SHARED SCHEMAS — identical on MIND and BODY
# ════════════════════════════════════════════════════════════════════

class CurationTier(str, Enum):
    """Pattern curation tier — determines persistence."""
    CANONICAL = "CANONICAL"           # Never decay — passed dual-gate
    PENDING_CANONICAL = "PENDING"     # Awaiting generativity proof — 200 cycle TTL
    STANDARD = "STANDARD"             # Default — 200 cycle persistence
    EPHEMERAL = "EPHEMERAL"           # Short-lived — 50 cycle persistence


class GovernanceVerdict(str, Enum):
    """Federation governance decision."""
    APPROVED = "APPROVED"             # Both sides agree
    HARD_BLOCK = "HARD_BLOCK"         # Kernel violation
    VETOED = "VETOED"                 # Parliament VETO (score ≤ -7)
    PENDING = "PENDING"               # Awaiting other side's decision
    CONFLICT = "CONFLICT"             # MIND and BODY disagree


@dataclass
class CurationMetadata:
    """
    Shared curation verdict format.
    
    Written by MIND (Ark Curator), read by BODY (Parliament).
    Both sides must respect TTL and tier.
    """
    pattern_hash: str                           # Unique pattern identifier
    tier: str = CurationTier.STANDARD.value     # CANONICAL / PENDING / STANDARD / EPHEMERAL
    ttl_cycles: int = 200                       # Cycles until decay (0 = never)
    cross_domain_count: int = 0                 # Gate A: domains where theme appeared
    generativity_score: float = 0.0             # Gate B: downstream new insights
    source_domain: int = 0                      # Domain that originated pattern
    originating_cycle: int = 0                  # Cycle when first seen
    recursion_detected: bool = False            # Whether Ark Curator flagged recursion
    friction_boost_active: bool = False         # Whether A0 friction safeguard is active
    timestamp: str = ""                         # ISO timestamp

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CurationMetadata":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class FederationHeartbeat:
    """
    Unified cycle counter and federation state.
    
    Written by MIND every F(7)=13 cycles.
    Read by BODY to correlate its decisions with MIND cycles.
    """
    mind_cycle: int = 0                         # MIND's current cycle count
    mind_epoch: str = ""                        # ISO timestamp of MIND's current cycle
    coherence: float = 1.0                      # MIND's coherence score
    current_rhythm: str = "CONTEMPLATION"       # MIND's current rhythm
    current_domain: int = 0                     # MIND's current domain
    ark_mood: str = "serene"                    # Ark Curator's cadence mood
    canonical_count: int = 0                    # Number of CANONICAL patterns
    pending_canonical_count: int = 0            # Number of PENDING CANONICAL
    recursion_warning: bool = False             # Ark recursion alert
    friction_boost: Dict[int, float] = field(default_factory=dict)  # Active friction domain boosts
    kernel_version: str = "1.0.0"              # MIND kernel version
    kernel_rules: int = 7                       # Number of kernel rules active
    kernel_blocks_total: int = 0                # Total kernel blocks since boot
    dominant_axiom: str = ""                    # Primary axiom of current domain (for D15 convergence)
    federation_version: str = "1.0.0"          # This protocol version
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "FederationHeartbeat":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class GovernanceExchange:
    """
    A governance decision record — written by either side, read by both.
    
    This is how MIND and BODY communicate governance decisions.
    """
    exchange_id: str = ""                       # Unique exchange ID
    source: str = "MIND"                        # Who wrote this: "MIND" or "BODY"
    verdict: str = GovernanceVerdict.APPROVED.value
    pattern_hash: str = ""                      # Pattern this decision applies to
    cycle: int = 0                              # Cycle number (MIND or BODY)
    domain: int = 0                             # Domain context
    kernel_rule: Optional[str] = None           # If HARD_BLOCK: which kernel rule
    parliament_score: Optional[float] = None    # If Parliament voted: score
    parliament_approval: Optional[float] = None # Approval rate (0.0-1.0)
    veto_node: Optional[str] = None             # If VETOED: which node
    curation: Optional[Dict] = None             # CurationMetadata if applicable
    reasoning: str = ""                         # Human-readable explanation
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.exchange_id:
            import hashlib
            raw = f"{self.source}:{self.cycle}:{self.pattern_hash}:{self.timestamp}"
            self.exchange_id = hashlib.sha256(raw.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Remove None values for cleaner JSON
        return {k: v for k, v in d.items() if v is not None}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "GovernanceExchange":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ════════════════════════════════════════════════════════════════════
# FEDERATION BRIDGE — MIND SIDE
# ════════════════════════════════════════════════════════════════════

# Local federation state directory
FEDERATION_DIR = Path("ElpidaAI/federation")
FEDERATION_HEARTBEAT_FILE = FEDERATION_DIR / "heartbeat.json"
FEDERATION_EXCHANGE_LOG = FEDERATION_DIR / "governance_exchanges.jsonl"
FEDERATION_CURATION_LOG = FEDERATION_DIR / "curation_metadata.jsonl"

# S3 keys in BODY bucket
S3_FEDERATION_PREFIX = "federation/"
S3_HEARTBEAT_KEY = f"{S3_FEDERATION_PREFIX}mind_heartbeat.json"
S3_CURATION_KEY = f"{S3_FEDERATION_PREFIX}mind_curation.jsonl"
S3_EXCHANGE_KEY = f"{S3_FEDERATION_PREFIX}governance_exchanges.jsonl"
S3_BODY_DECISIONS_KEY = f"{S3_FEDERATION_PREFIX}body_decisions.jsonl"


class FederationBridge:
    """
    The MIND side of the Federated governance bridge.
    
    Responsibilities:
    - Write heartbeat (cycle counter, coherence, ark state) to BODY bucket
    - Write curation metadata per insight to BODY bucket
    - Read governance decisions from BODY's Parliament
    - Detect and log governance conflicts
    - Maintain local federation state
    """

    def __init__(self, ark_curator=None):
        self.ark_curator = ark_curator
        self.kernel_blocks = 0
        self.exchanges: List[GovernanceExchange] = []
        self.curations: List[CurationMetadata] = []
        self._s3_client = None
        self._body_bucket = os.environ.get(
            "AWS_S3_BUCKET_BODY", "elpida-body-evolution"
        )

        # Ensure local federation directory
        FEDERATION_DIR.mkdir(parents=True, exist_ok=True)

        # Load last heartbeat if exists
        self.last_heartbeat: Optional[FederationHeartbeat] = None
        if FEDERATION_HEARTBEAT_FILE.exists():
            try:
                with open(FEDERATION_HEARTBEAT_FILE) as f:
                    self.last_heartbeat = FederationHeartbeat.from_dict(json.load(f))
            except Exception:
                pass

        logger.info("FederationBridge initialized (MIND side)")

    def _get_s3(self):
        """Lazy-init S3 client."""
        if self._s3_client is None:
            try:
                import boto3
                self._s3_client = boto3.client(
                    "s3",
                    region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
                )
            except Exception as e:
                logger.warning("S3 client init failed: %s", e)
        return self._s3_client

    # ────────────────────────────────────────────────────────────
    # HEARTBEAT: Unified Cycle Counter
    # ────────────────────────────────────────────────────────────

    def emit_heartbeat(
        self,
        cycle: int,
        coherence: float,
        rhythm: str,
        domain: int,
        dominant_axiom: str = "",
    ) -> FederationHeartbeat:
        """
        Emit a federation heartbeat.
        
        Called every F(7)=13 cycles from the native engine.
        Writes to local state + pushes to BODY bucket.
        """
        # Build heartbeat from current state
        friction = {}
        ark_mood = "serene"
        canonical = 0
        pending = 0
        recursion = False

        if self.ark_curator:
            friction = self.ark_curator.get_friction_boost() or {}
            ark_mood = self.ark_curator.cadence.cadence_mood
            canonical = self.ark_curator.cadence.canonical_count
            pending = self.ark_curator.get_pending_canonical_count()
            ark_state = self.ark_curator.query()
            recursion = ark_state.recursion_warning

        hb = FederationHeartbeat(
            mind_cycle=cycle,
            mind_epoch=datetime.now(timezone.utc).isoformat(),
            coherence=coherence,
            current_rhythm=rhythm,
            current_domain=domain,
            ark_mood=ark_mood,
            canonical_count=canonical,
            pending_canonical_count=pending,
            recursion_warning=recursion,
            friction_boost={str(k): v for k, v in friction.items()},
            kernel_blocks_total=self.kernel_blocks,
            dominant_axiom=dominant_axiom or "",
        )

        # Save locally
        self.last_heartbeat = hb
        with open(FEDERATION_HEARTBEAT_FILE, "w") as f:
            json.dump(hb.to_dict(), f, indent=2)

        # Push to BODY bucket
        self._push_to_body(S3_HEARTBEAT_KEY, json.dumps(hb.to_dict(), indent=2))

        logger.info(
            "Federation heartbeat: cycle=%d coherence=%.2f mood=%s canonical=%d",
            cycle, coherence, ark_mood, canonical,
        )
        return hb

    # ────────────────────────────────────────────────────────────
    # CURATION: Pattern Metadata
    # ────────────────────────────────────────────────────────────

    def emit_curation(
        self,
        pattern_hash: str,
        tier: str,
        ttl_cycles: int,
        cross_domain_count: int,
        generativity_score: float,
        source_domain: int,
        originating_cycle: int,
        recursion_detected: bool = False,
        friction_boost_active: bool = False,
    ) -> CurationMetadata:
        """
        Emit curation metadata for a pattern.
        
        Called by Ark Curator when it evaluates a pattern.
        Written to local log + appended to BODY bucket.
        """
        cm = CurationMetadata(
            pattern_hash=pattern_hash,
            tier=tier,
            ttl_cycles=ttl_cycles,
            cross_domain_count=cross_domain_count,
            generativity_score=generativity_score,
            source_domain=source_domain,
            originating_cycle=originating_cycle,
            recursion_detected=recursion_detected,
            friction_boost_active=friction_boost_active,
        )

        self.curations.append(cm)

        # Append to local log
        with open(FEDERATION_CURATION_LOG, "a") as f:
            f.write(json.dumps(cm.to_dict()) + "\n")

        # Push incremental to BODY bucket
        self._append_to_body(S3_CURATION_KEY, json.dumps(cm.to_dict()))

        return cm

    # ────────────────────────────────────────────────────────────
    # GOVERNANCE EXCHANGE: Record decisions
    # ────────────────────────────────────────────────────────────

    def record_kernel_block(
        self,
        kernel_result: Dict[str, Any],
        cycle: int,
        domain: int,
    ) -> GovernanceExchange:
        """Record a kernel HARD_BLOCK as a governance exchange."""
        self.kernel_blocks += 1

        ex = GovernanceExchange(
            source="MIND",
            verdict=GovernanceVerdict.HARD_BLOCK.value,
            pattern_hash=kernel_result.get("kernel_rule", "unknown"),
            cycle=cycle,
            domain=domain,
            kernel_rule=kernel_result.get("kernel_rule"),
            reasoning=kernel_result.get("reasoning", ""),
        )

        self._record_exchange(ex)
        return ex

    def record_approval(
        self,
        pattern_hash: str,
        cycle: int,
        domain: int,
        curation: Optional[CurationMetadata] = None,
    ) -> GovernanceExchange:
        """Record MIND-side approval of a pattern."""
        ex = GovernanceExchange(
            source="MIND",
            verdict=GovernanceVerdict.APPROVED.value,
            pattern_hash=pattern_hash,
            cycle=cycle,
            domain=domain,
            curation=curation.to_dict() if curation else None,
            reasoning="Kernel passed, Ark Curator evaluated",
        )

        self._record_exchange(ex)
        return ex

    def _record_exchange(self, exchange: GovernanceExchange):
        """Write exchange to local log and BODY bucket."""
        self.exchanges.append(exchange)

        # Local append
        with open(FEDERATION_EXCHANGE_LOG, "a") as f:
            f.write(json.dumps(exchange.to_dict()) + "\n")

        # Push to BODY bucket
        self._append_to_body(S3_EXCHANGE_KEY, json.dumps(exchange.to_dict()))

    # ────────────────────────────────────────────────────────────
    # BODY→MIND: Read governance decisions from BODY
    # ────────────────────────────────────────────────────────────

    def pull_body_decisions(self) -> List[GovernanceExchange]:
        """
        Pull governance decisions written by BODY (Parliament).
        
        Returns list of new GovernanceExchange records from BODY side.
        """
        s3 = self._get_s3()
        if not s3:
            return []

        try:
            response = s3.get_object(
                Bucket=self._body_bucket,
                Key=S3_BODY_DECISIONS_KEY,
            )
            body = response["Body"].read().decode("utf-8")
            decisions = []
            for line in body.strip().split("\n"):
                if line.strip():
                    try:
                        decisions.append(
                            GovernanceExchange.from_dict(json.loads(line))
                        )
                    except Exception:
                        continue
            logger.info("Pulled %d BODY decisions", len(decisions))
            return decisions
        except s3.exceptions.NoSuchKey:
            return []
        except Exception as e:
            logger.warning("Failed to pull BODY decisions: %s", e)
            return []

    # ────────────────────────────────────────────────────────────
    # CONFLICT DETECTION
    # ────────────────────────────────────────────────────────────

    def detect_conflicts(
        self, body_decisions: List[GovernanceExchange]
    ) -> List[Dict[str, Any]]:
        """
        Detect governance conflicts between MIND and BODY.
        
        A conflict occurs when:
        - MIND approved but BODY vetoed (or vice versa)
        - MIND HARD_BLOCK but BODY approved
        - Different curation tiers for same pattern
        
        Returns list of conflict records.
        """
        conflicts = []

        # Index MIND decisions by pattern_hash
        mind_by_hash = {}
        for ex in self.exchanges:
            mind_by_hash[ex.pattern_hash] = ex

        for body_ex in body_decisions:
            mind_ex = mind_by_hash.get(body_ex.pattern_hash)
            if not mind_ex:
                continue

            # Check for contradictions
            if mind_ex.verdict != body_ex.verdict:
                conflict = {
                    "type": "VERDICT_CONFLICT",
                    "pattern_hash": body_ex.pattern_hash,
                    "mind_verdict": mind_ex.verdict,
                    "body_verdict": body_ex.verdict,
                    "mind_cycle": mind_ex.cycle,
                    "body_cycle": body_ex.cycle,
                    "resolution": self._resolve_conflict(mind_ex, body_ex),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                conflicts.append(conflict)
                logger.warning(
                    "GOVERNANCE CONFLICT: pattern=%s MIND=%s BODY=%s → %s",
                    body_ex.pattern_hash,
                    mind_ex.verdict,
                    body_ex.verdict,
                    conflict["resolution"],
                )

        return conflicts

    def _resolve_conflict(
        self, mind: GovernanceExchange, body: GovernanceExchange
    ) -> str:
        """
        Resolve a governance conflict.
        
        Resolution rules (Federated model):
        1. HARD_BLOCK always wins (either side) — kernel is absolute
        2. VETO wins over APPROVED (dissent preservation — CASSANDRA principle)
        3. If both APPROVED but different curation tiers: use stricter tier
        4. Otherwise: flag for human review
        """
        # Rule 1: Kernel HARD_BLOCK is absolute
        if mind.verdict == GovernanceVerdict.HARD_BLOCK.value:
            return "MIND_KERNEL_PREVAILS"
        if body.verdict == GovernanceVerdict.HARD_BLOCK.value:
            return "BODY_KERNEL_PREVAILS"

        # Rule 2: VETO wins (CASSANDRA principle — dissent preserved)
        if mind.verdict == GovernanceVerdict.VETOED.value:
            return "MIND_VETO_PREVAILS"
        if body.verdict == GovernanceVerdict.VETOED.value:
            return "BODY_VETO_PREVAILS"

        # Rule 3: Both approved but different details
        if (
            mind.verdict == GovernanceVerdict.APPROVED.value
            and body.verdict == GovernanceVerdict.APPROVED.value
        ):
            return "BOTH_APPROVED_USE_STRICTER_CURATION"

        # Rule 4: Unresolvable
        return "FLAGGED_FOR_REVIEW"

    # ────────────────────────────────────────────────────────────
    # S3 HELPERS
    # ────────────────────────────────────────────────────────────

    def _push_to_body(self, key: str, body: str):
        """Write a full object to the BODY bucket."""
        s3 = self._get_s3()
        if not s3:
            logger.debug("S3 not available — skipping push to %s", key)
            return
        try:
            s3.put_object(
                Bucket=self._body_bucket,
                Key=key,
                Body=body.encode("utf-8"),
                ContentType="application/json",
            )
            logger.debug("Pushed to s3://%s/%s", self._body_bucket, key)
        except Exception as e:
            logger.warning("Failed to push to BODY bucket: %s", e)

    def _append_to_body(self, key: str, line: str):
        """Append a line to a JSONL file in the BODY bucket."""
        s3 = self._get_s3()
        if not s3:
            return
        try:
            # Read existing content
            try:
                response = s3.get_object(Bucket=self._body_bucket, Key=key)
                existing = response["Body"].read().decode("utf-8")
            except Exception:
                existing = ""

            # Append new line
            updated = existing.rstrip("\n") + "\n" + line + "\n" if existing else line + "\n"

            s3.put_object(
                Bucket=self._body_bucket,
                Key=key,
                Body=updated.encode("utf-8"),
                ContentType="application/json",
            )
        except Exception as e:
            logger.warning("Failed to append to BODY bucket: %s", e)

    # ────────────────────────────────────────────────────────────
    # STATUS
    # ────────────────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Return federation bridge status."""
        return {
            "federation_version": "1.0.0",
            "architecture": "FEDERATED",
            "side": "MIND",
            "last_heartbeat_cycle": (
                self.last_heartbeat.mind_cycle if self.last_heartbeat else 0
            ),
            "kernel_blocks_total": self.kernel_blocks,
            "exchanges_recorded": len(self.exchanges),
            "curations_emitted": len(self.curations),
            "body_bucket": self._body_bucket,
            "s3_available": self._get_s3() is not None,
            "local_state_dir": str(FEDERATION_DIR),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ════════════════════════════════════════════════════════════════════
# SELF-TEST
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════╗")
    print("║  ELPIDA FEDERATION BRIDGE — MIND SIDE v1.0.0    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    bridge = FederationBridge()
    status = bridge.status()

    print(f"Architecture:    {status['architecture']}")
    print(f"Side:            {status['side']}")
    print(f"Body bucket:     {status['body_bucket']}")
    print(f"S3 available:    {status['s3_available']}")
    print(f"Local state:     {status['local_state_dir']}")
    print()

    # Test schemas
    cm = CurationMetadata(
        pattern_hash="test_abc123",
        tier=CurationTier.PENDING_CANONICAL.value,
        ttl_cycles=200,
        cross_domain_count=1,
        generativity_score=0.0,
        source_domain=3,
        originating_cycle=42,
    )
    print(f"CurationMetadata test: {json.dumps(cm.to_dict(), indent=2)[:200]}...")
    print()

    hb = FederationHeartbeat(
        mind_cycle=78508,
        coherence=0.95,
        current_rhythm="CONTEMPLATION",
        current_domain=0,
    )
    print(f"Heartbeat test: cycle={hb.mind_cycle} coherence={hb.coherence}")
    print()

    ex = GovernanceExchange(
        source="MIND",
        verdict=GovernanceVerdict.APPROVED.value,
        pattern_hash="test_abc123",
        cycle=78508,
        domain=3,
    )
    print(f"Exchange test: {ex.exchange_id} verdict={ex.verdict}")
    print()
    print("✅ All schemas valid")
