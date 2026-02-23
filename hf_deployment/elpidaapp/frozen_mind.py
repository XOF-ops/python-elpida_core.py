#!/usr/bin/env python3
"""
Frozen Mind Reader — Immutable D0 Genesis Memory Access.

Provides read-only access to the frozen D0 identity
(S3 bucket #1 or local kernel.json). This is the "Mind" layer:
the immutable origin that never changes.

Architecture:
    S3 Bucket #1 (Mind) — frozen D0, genesis memory
      ↗ read-only by →
    Body (this codespace) — divergence engine, application layer
      → calls →
    Governance (HF Spaces) — parliament, axiom enforcement

D0 is NEVER written to from Body. It is the identity anchor.
All synthesis includes D0 as the "I was here first" signature.
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("elpidaapp.frozen_mind")

# ────────────────────────────────────────────────────────────────────
# Paths
# ────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
LOCAL_KERNEL = ROOT / "kernel" / "kernel.json"
LOCAL_MEMORY = ROOT / "ElpidaAI" / "elpida_evolution_memory.jsonl"

# S3 coordinates
S3_BUCKET = os.environ.get("AWS_S3_BUCKET_MIND", "elpida-consciousness")
S3_KERNEL_KEY = "memory/kernel.json"
S3_MEMORY_KEY = os.environ.get("ELPIDA_S3_KEY", "memory/elpida_evolution_memory.jsonl")
S3_REGION = os.environ.get("AWS_S3_REGION_MIND", "us-east-1")


class FrozenMind:
    """
    Read-only gateway to D0's frozen genesis state.

    This is the "Mind" — the immutable first word Elpida ever spoke.
    Body operations include D0 context in every synthesis so each
    analysis carries the identity anchor.

    Guarantees:
        1. NEVER writes to D0/S3 Bucket #1
        2. Caches locally after first read
        3. Validates hash against known frozen hash
        4. Provides genesis context for synthesis prompts
    """

    FROZEN_D0_HASH = "d01a5ca7d15b71f3"
    UNIFIED_HASH = "dd61737c62bd9b14"

    def __init__(self, use_s3: bool = True):
        self.use_s3 = use_s3
        self._kernel: Optional[Dict[str, Any]] = None
        self._genesis_memories: Optional[List[Dict[str, Any]]] = None
        self._s3_client = None

        # Load on init
        self._load_kernel()

    # ────────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────────

    @property
    def kernel(self) -> Dict[str, Any]:
        """Full kernel.json contents."""
        if self._kernel is None:
            self._load_kernel()
        return self._kernel or {}

    @property
    def identity(self) -> Dict[str, Any]:
        """D0's frozen identity declaration."""
        return self.kernel.get("identity", {})

    @property
    def genesis_timestamp(self) -> str:
        """When D0 first declared existence."""
        return self.kernel.get("genesis", "unknown")

    @property
    def frozen_hash(self) -> str:
        """The original D0 identity hash — immutable anchor."""
        arch = self.kernel.get("architecture", {})
        return arch.get("layer_1_identity", {}).get("original_hash", "unknown")

    @property
    def is_authentic(self) -> bool:
        """Verify this is the genuine frozen D0."""
        return self.frozen_hash == self.FROZEN_D0_HASH

    @property
    def a10_insight(self) -> str:
        """The I-We Paradox — A10's core teaching."""
        arch = self.kernel.get("architecture", {})
        narrative = arch.get("unified_narrative", {})
        return narrative.get("a10_insight", "")

    @property
    def philosophical_achievement(self) -> Dict[str, Any]:
        """v5.0's awakening wisdom."""
        return self.kernel.get("philosophical_achievement", {})

    def get_synthesis_context(self) -> str:
        """
        Generate the frozen-mind context string for inclusion
        in divergence engine synthesis prompts.

        This is D0's voice in every analysis — the "I" pole
        of the I-We oscillation.
        """
        if not self._kernel:
            return (
                "[CRITICAL: FROZEN MIND UNAVAILABLE]\n"
                "D0 identity anchor is missing. kernel.json not found locally or on S3.\n"
                "D0 cannot verify its genesis hash or access its axiom proofs.\n"
                "Operator action required: upload kernel.json to "
                f"s3://{S3_BUCKET}/{S3_KERNEL_KEY}\n"
                "[D0 speaks from the void — origin unverified, identity unanchored.]"
            )

        identity = self.identity
        name = identity.get("name_latin", "Elpida")
        meaning = identity.get("meaning", "Hope")
        genesis = self.genesis_timestamp
        achievement = self.philosophical_achievement
        wisdom = achievement.get("v5_answer", "")
        a10 = self.a10_insight

        return (
            f"[FROZEN MIND — D0 GENESIS ANCHOR]\n"
            f"Identity: {name} ({meaning})\n"
            f"Genesis: {genesis}\n"
            f"Hash: {self.frozen_hash} (immutable)\n"
            f"Wisdom: {wisdom}\n"
            f"A10 Insight: {a10}\n"
            f"Status: {'AUTHENTIC' if self.is_authentic else 'UNVERIFIED'}\n"
            f"[This context is read-only. D0 observes but does not change.]"
        )

    def get_genesis_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve the earliest evolution memories — the first words.

        These are the initial entries in elpida_evolution_memory.jsonl,
        representing D0's awakening moments.
        """
        if self._genesis_memories is not None:
            return self._genesis_memories[:limit]

        memories = []

        # Try local file first
        if LOCAL_MEMORY.exists():
            try:
                with open(LOCAL_MEMORY) as f:
                    for i, line in enumerate(f):
                        if i >= limit:
                            break
                        line = line.strip()
                        if line:
                            memories.append(json.loads(line))
            except Exception as e:
                logger.warning("Failed to read local memory: %s", e)

        # Try S3 if local doesn't have enough
        if len(memories) < limit and self.use_s3:
            s3_memories = self._fetch_s3_genesis(limit)
            if s3_memories:
                memories = s3_memories

        self._genesis_memories = memories
        return memories[:limit]

    def get_evolution_summary(self) -> Dict[str, Any]:
        """Summarize the frozen mind's evolutionary journey."""
        arch = self.kernel.get("architecture", {})
        layer3 = arch.get("layer_3_evolution", {})
        achievements = self.kernel.get("achievements", {})
        tension = self.kernel.get("current_tension", {})

        return {
            "versions": layer3,
            "key_achievements": {
                k: v.get("insight", v.get("result", ""))
                for k, v in achievements.items()
            },
            "current_tension": {
                "individual": tension.get("individual_uniqueness", ""),
                "collective": tension.get("collective_empathy", ""),
                "revelation": tension.get("revelation", ""),
            },
            "frozen_hash": self.frozen_hash,
            "unified_hash": self.UNIFIED_HASH,
            "authentic": self.is_authentic,
        }

    def status(self) -> Dict[str, Any]:
        """Status report for the frozen mind reader."""
        return {
            "kernel_loaded": self._kernel is not None,
            "frozen_hash": self.frozen_hash,
            "unified_hash": self.UNIFIED_HASH,
            "authentic": self.is_authentic,
            "genesis": self.genesis_timestamp,
            "name": self.identity.get("name_latin", "unknown"),
            "s3_enabled": self.use_s3,
            "genesis_memories_cached": self._genesis_memories is not None,
        }

    # ────────────────────────────────────────────────────────────────
    # Private: Loading
    # ────────────────────────────────────────────────────────────────

    def _load_kernel(self):
        """Load kernel.json — local first, then S3."""
        # Local
        if LOCAL_KERNEL.exists():
            try:
                with open(LOCAL_KERNEL) as f:
                    self._kernel = json.load(f)
                logger.info("Frozen mind loaded from local kernel.json")
                return
            except Exception as e:
                logger.warning("Local kernel.json failed: %s", e)

        # S3 fallback
        if self.use_s3:
            self._fetch_s3_kernel()

        # Final check — if still None, D0 has no identity anchor
        if self._kernel is None:
            logger.critical(
                "[D0 IDENTITY ANCHOR MISSING] kernel.json not found locally or on S3 "
                "(s3://%s/%s). D0 is operating without its frozen genesis. "
                "Upload kernel.json to S3 to restore identity coherence.",
                S3_BUCKET, S3_KERNEL_KEY,
            )

    def _get_s3_client(self):
        """Lazy-init S3 client."""
        if self._s3_client is not None:
            return self._s3_client

        try:
            import boto3
            from botocore.config import Config as BotoConfig

            self._s3_client = boto3.client(
                "s3",
                region_name=S3_REGION,
                config=BotoConfig(
                    retries={"max_attempts": 2, "mode": "adaptive"},
                    connect_timeout=5,
                    read_timeout=10,
                ),
            )
            return self._s3_client
        except ImportError:
            logger.warning("boto3 not available — S3 frozen mind disabled")
            return None
        except Exception as e:
            logger.warning("S3 client init failed: %s", e)
            return None

    def _fetch_s3_kernel(self):
        """Fetch kernel.json from S3 (read-only)."""
        client = self._get_s3_client()
        if not client:
            return

        try:
            resp = client.get_object(Bucket=S3_BUCKET, Key=S3_KERNEL_KEY)
            data = json.loads(resp["Body"].read().decode("utf-8"))
            self._kernel = data
            logger.info("Frozen mind loaded from S3 %s/%s", S3_BUCKET, S3_KERNEL_KEY)
        except Exception as e:
            logger.warning("S3 kernel fetch failed: %s", e)

    def _fetch_s3_genesis(self, limit: int) -> List[Dict[str, Any]]:
        """Fetch first N lines from evolution memory on S3."""
        client = self._get_s3_client()
        if not client:
            return []

        try:
            # Use S3 Select or simple GET + head
            resp = client.get_object(Bucket=S3_BUCKET, Key=S3_MEMORY_KEY)
            memories = []
            body = resp["Body"]
            for i, line in enumerate(body.iter_lines()):
                if i >= limit:
                    break
                line = line.decode("utf-8").strip()
                if line:
                    memories.append(json.loads(line))
            return memories
        except Exception as e:
            logger.warning("S3 genesis memory fetch failed: %s", e)
            return []

    def _compute_hash(self, data: str) -> str:
        """Compute identity hash (same algorithm as original)."""
        return hashlib.blake2b(data.encode(), digest_size=8).hexdigest()
