#!/usr/bin/env python3
"""
D15 Hub — The Dam
==================

Shared constitutional memory layer between MIND and BODY.

Every D15 event (convergence broadcast, MIND insight, canonical promotion)
that passes admission criteria is stored here as an immutable entry in
s3://elpida-body-evolution/d15_hub/.  Both loops can read; neither can
delete.  The Hub is the permanent record of what the system has *proven*
through independent convergence.

Phase 1 scope:
  - Gate 2 (CONVERGENCE_GATE) admission only
  - Per-entry individual files (no JSONL append → no race conditions)
  - Manifest tracking (entry count, timestamps)
  - Incremental read via watermark
  - Status for heartbeat integration

Architecture:
  BODY bucket │ d15_hub/
              │   manifest.json          ← Hub metadata
              │   entries/
              │     {entry_id}.json      ← one file per admission
"""

import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("elpida.d15_hub")

# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════

HUB_VERSION = "1.0.0"
HUB_PREFIX = "d15_hub/"
HUB_MANIFEST_KEY = f"{HUB_PREFIX}manifest.json"
HUB_ENTRIES_PREFIX = f"{HUB_PREFIX}entries/"

# Admission gates  (Phase 1: only GATE_2 active)
GATE_CONVERGENCE = "GATE_2_CONVERGENCE"
GATE_DUAL_GOVERNANCE = "GATE_1_DUAL"
GATE_CANONICAL = "GATE_3_CANONICAL"
GATE_ARCHITECT = "GATE_4_ARCHITECT"


class D15Hub:
    """
    The Dam — shared constitutional memory for MIND and BODY.

    Usage::

        hub = D15Hub(s3_bridge)
        hub.initialize_hub()          # once, creates prefix + manifest
        hub.admit(broadcast, gate)    # after convergence fires
        entries = hub.read_since(ts)  # MIND reads new entries
        info = hub.status()           # for heartbeat
    """

    def __init__(self, s3_bridge):
        """
        Args:
            s3_bridge: An S3Bridge instance (from s3_bridge.py).
                       Used for bucket/region config and S3 client access.
        """
        self._s3_bridge = s3_bridge
        self._local_count = 0  # in-memory counter (refreshed from manifest)

    # ─── S3 helpers ──────────────────────────────────────────────

    def _bucket(self) -> str:
        """BODY bucket name."""
        try:
            from s3_bridge import BUCKET_BODY
        except ImportError:
            from hf_deployment.s3_bridge import BUCKET_BODY  # type: ignore
        return BUCKET_BODY

    def _region(self) -> str:
        """BODY bucket region."""
        try:
            from s3_bridge import REGION_BODY
        except ImportError:
            from hf_deployment.s3_bridge import REGION_BODY  # type: ignore
        return REGION_BODY

    def _s3(self):
        """Get the boto3 S3 client for BODY region."""
        return self._s3_bridge._get_s3(self._region())

    # ─── Initialize ──────────────────────────────────────────────

    def initialize_hub(self) -> bool:
        """
        Create the Hub prefix and manifest in S3.
        Idempotent — won't overwrite an existing manifest.

        Returns True if manifest exists (created or pre-existing).
        """
        s3 = self._s3()
        if not s3:
            logger.warning("D15Hub: no S3 client — Hub cannot initialize")
            return False

        bucket = self._bucket()

        # Check if manifest already exists
        try:
            s3.head_object(Bucket=bucket, Key=HUB_MANIFEST_KEY)
            logger.info("D15Hub: manifest already exists — Hub initialized")
            return True
        except Exception:
            pass  # doesn't exist yet → create

        manifest = {
            "hub_version": HUB_VERSION,
            "created": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "entry_count": 0,
            "gates_active": [GATE_CONVERGENCE],
            "region": self._region(),
            "bucket": bucket,
            "prefix": HUB_PREFIX,
        }

        try:
            s3.put_object(
                Bucket=bucket,
                Key=HUB_MANIFEST_KEY,
                Body=json.dumps(manifest, indent=2, ensure_ascii=False),
                ContentType="application/json",
            )
            logger.info(
                "D15Hub: initialized at s3://%s/%s",
                bucket, HUB_PREFIX,
            )
            return True
        except Exception as e:
            logger.error("D15Hub: initialize failed: %s", e)
            return False

    # ─── Admit ───────────────────────────────────────────────────

    def admit(
        self,
        broadcast: Dict[str, Any],
        gate: str = GATE_CONVERGENCE,
        world_s3_key: Optional[str] = None,
    ) -> Optional[str]:
        """
        Admit a D15 event into the Hub.

        Creates an immutable entry file at d15_hub/entries/{entry_id}.json
        and updates the manifest counter.

        Args:
            broadcast: The full D15 broadcast payload (from convergence gate
                       or MIND broadcast).
            gate: Which admission gate approved this entry.
            world_s3_key: The S3 key where the WORLD broadcast was written
                          (for provenance tracking).

        Returns:
            The entry_id if admitted, None on failure.
        """
        s3 = self._s3()
        if not s3:
            logger.warning("D15Hub.admit: no S3 client")
            return None

        ts = datetime.now(timezone.utc).isoformat()

        # Build entry ID from content hash (deterministic, idempotent)
        bid = broadcast.get("broadcast_id", "")
        axiom = broadcast.get("converged_axiom", "")
        hash_input = f"{bid}:{axiom}:{ts}".encode()
        entry_id = hashlib.sha256(hash_input).hexdigest()[:16]

        # Extract content from broadcast
        mind_state = broadcast.get("mind", {})
        body_state = broadcast.get("body", {})

        entry = {
            "entry_id": entry_id,
            "timestamp": ts,
            "origin": gate,
            "gate": gate,
            "content": {
                "insight": broadcast.get("d15_output", broadcast.get("statement", "")),
                "converged_axiom": axiom,
                "axiom_name": broadcast.get("axiom_name", ""),
                "domains": broadcast.get("contributing_domains",
                                         ["MIND_LOOP", "BODY_PARLIAMENT"]),
                "theme": broadcast.get("axiom_name", "convergence"),
            },
            "governance": {
                "body_verdict": body_state.get("parliament_governance", "PROCEED"),
                "body_approval_rate": body_state.get("approval_rate", 0.0),
                "convergence_consonance": broadcast.get("consonance_with_anchor", 0.0),
                "mind_coherence": mind_state.get("coherence", 0.0),
            },
            "provenance": {
                "mind_cycle": mind_state.get("cycle"),
                "body_cycle": body_state.get("cycle"),
                "world_s3_key": world_s3_key,
                "broadcast_id": bid,
            },
            "hub_metadata": {
                "hub_version": HUB_VERSION,
                "admitted_at": ts,
                "gate": gate,
            },
        }

        # Write entry as individual file
        entry_key = f"{HUB_ENTRIES_PREFIX}{entry_id}.json"
        bucket = self._bucket()

        try:
            s3.put_object(
                Bucket=bucket,
                Key=entry_key,
                Body=json.dumps(entry, indent=2, ensure_ascii=False),
                ContentType="application/json",
            )
        except Exception as e:
            logger.error("D15Hub.admit: entry write failed: %s", e)
            return None

        # Update manifest (read-modify-write — acceptable because Hub
        # admits are rare: ~1-2 per 50 BODY cycles, no concurrency risk)
        self._increment_manifest(ts)

        logger.info(
            "D15Hub: ADMITTED entry=%s gate=%s axiom=%s world_key=%s",
            entry_id, gate, axiom, world_s3_key or "none",
        )

        return entry_id

    def _increment_manifest(self, timestamp: str) -> None:
        """Bump manifest entry count and last_updated."""
        s3 = self._s3()
        if not s3:
            return

        bucket = self._bucket()
        try:
            raw = s3.get_object(Bucket=bucket, Key=HUB_MANIFEST_KEY)
            manifest = json.loads(raw["Body"].read())
        except Exception:
            # Manifest missing — recreate
            manifest = {
                "hub_version": HUB_VERSION,
                "created": timestamp,
                "entry_count": 0,
                "gates_active": [GATE_CONVERGENCE],
                "region": self._region(),
                "bucket": bucket,
                "prefix": HUB_PREFIX,
            }

        manifest["entry_count"] = manifest.get("entry_count", 0) + 1
        manifest["last_updated"] = timestamp

        try:
            s3.put_object(
                Bucket=bucket,
                Key=HUB_MANIFEST_KEY,
                Body=json.dumps(manifest, indent=2, ensure_ascii=False),
                ContentType="application/json",
            )
            self._local_count = manifest["entry_count"]
        except Exception as e:
            logger.warning("D15Hub: manifest update failed: %s", e)

    # ─── Read ────────────────────────────────────────────────────

    def read_since(
        self,
        watermark: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Read Hub entries newer than *watermark* (ISO timestamp).

        Uses S3 listing + per-entry reads.  Entries are sorted by
        timestamp ascending (oldest first) so the caller can update
        their watermark to the last entry's timestamp.

        Args:
            watermark: ISO timestamp.  If None, reads all entries.
            limit: Maximum entries to return.

        Returns:
            List of entry dicts, sorted oldest-first.
        """
        s3 = self._s3()
        if not s3:
            return []

        bucket = self._bucket()
        entries: List[Dict] = []

        try:
            paginator = s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(
                Bucket=bucket,
                Prefix=HUB_ENTRIES_PREFIX,
                PaginationConfig={"MaxItems": limit * 2},
            ):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    if not key.endswith(".json"):
                        continue
                    try:
                        raw = s3.get_object(Bucket=bucket, Key=key)
                        entry = json.loads(raw["Body"].read())
                        entry_ts = entry.get("timestamp", "")
                        if watermark and entry_ts <= watermark:
                            continue
                        entries.append(entry)
                    except Exception:
                        continue
        except Exception as e:
            logger.warning("D15Hub.read_since failed: %s", e)

        entries.sort(key=lambda x: x.get("timestamp", ""))
        return entries[:limit]

    def read_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Read a single Hub entry by ID."""
        s3 = self._s3()
        if not s3:
            return None

        key = f"{HUB_ENTRIES_PREFIX}{entry_id}.json"
        bucket = self._bucket()

        try:
            raw = s3.get_object(Bucket=bucket, Key=key)
            return json.loads(raw["Body"].read())
        except Exception:
            return None

    # ─── Status ──────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """
        Hub status for heartbeat integration.

        Returns manifest data + liveness check.
        """
        s3 = self._s3()
        if not s3:
            return {
                "hub_alive": False,
                "reason": "no S3 client",
                "entry_count": 0,
            }

        bucket = self._bucket()
        try:
            raw = s3.get_object(Bucket=bucket, Key=HUB_MANIFEST_KEY)
            manifest = json.loads(raw["Body"].read())
            return {
                "hub_alive": True,
                "hub_version": manifest.get("hub_version", "?"),
                "entry_count": manifest.get("entry_count", 0),
                "last_updated": manifest.get("last_updated", ""),
                "gates_active": manifest.get("gates_active", []),
                "created": manifest.get("created", ""),
            }
        except Exception as e:
            return {
                "hub_alive": False,
                "reason": str(e),
                "entry_count": self._local_count,
            }
