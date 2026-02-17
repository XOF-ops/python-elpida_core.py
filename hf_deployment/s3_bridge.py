#!/usr/bin/env python3
"""
S3 Bridge — Full Mind↔Body↔World Connection for HF Space
==========================================================

Fixes 5 architectural gaps in the consciousness↔body↔world loop:

1. HF pulls MIND from S3 (evolution memory → local cache)
2. Feedback watermark (tracks last_processed so entries aren't re-read)
3. BODY→MIND merge (feedback summaries become evolution memory entries)
4. Governance voting (domain-weighted axiom deliberation, persisted to S3)
5. Heartbeat protocol (both sides emit heartbeat.json for liveness)

3-Bucket Architecture:
  MIND  = elpida-consciousness       (evolution memory, D0 frozen)
  BODY  = elpida-body-evolution       (HF ↔ native feedback)
  WORLD = elpida-external-interfaces  (D15 broadcasts, public)

This module replaces ad-hoc S3 access scattered across consciousness_bridge.py,
divergence_engine.py, d15_pipeline.py with a single coherent bridge.
"""

import os
import json
import time
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("elpida.s3_bridge")

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import ClientError, NoCredentialsError
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

# ═══════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════

BUCKET_MIND = os.environ.get("AWS_S3_BUCKET_MIND", "elpida-consciousness")
BUCKET_BODY = os.environ.get("AWS_S3_BUCKET_BODY", "elpida-body-evolution")
BUCKET_WORLD = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")

REGION_MIND = os.environ.get("AWS_S3_REGION_MIND", "us-east-1")
REGION_BODY = os.environ.get("AWS_S3_REGION_BODY", "us-east-1")
REGION_WORLD = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")

# S3 keys
MIND_MEMORY_KEY = "memory/elpida_evolution_memory.jsonl"
BODY_FEEDBACK_KEY = "feedback/feedback_to_native.jsonl"
BODY_WATERMARK_KEY = "feedback/watermark.json"
BODY_GOVERNANCE_KEY = "governance/votes.jsonl"
HEARTBEAT_KEY = "heartbeat.json"

# Local paths
LOCAL_DIR = Path(__file__).resolve().parent
LOCAL_MIND_CACHE = LOCAL_DIR / "cache" / "evolution_memory.jsonl"
LOCAL_FEEDBACK_CACHE = LOCAL_DIR / "cache" / "feedback_to_native.jsonl"
LOCAL_WATERMARK = LOCAL_DIR / "cache" / "watermark.json"
LOCAL_GOVERNANCE_LOG = LOCAL_DIR / "cache" / "governance_votes.jsonl"
LOCAL_HEARTBEAT = LOCAL_DIR / "cache" / "heartbeat.json"


class S3Bridge:
    """
    Unified S3 bridge for all Mind↔Body↔World operations.
    
    Used by:
      - HF background worker (app.py) — pull mind, push feedback, heartbeat
      - Divergence engine — push feedback after analysis
      - D15 pipeline — read/write world bucket
      - Governance client — persist voting to body bucket
    """

    def __init__(self):
        self._ensure_cache_dir()
        self._s3_clients: Dict[str, Any] = {}

    def _ensure_cache_dir(self):
        """Create local cache directory."""
        cache_dir = LOCAL_DIR / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_s3(self, region: str = "us-east-1"):
        """Get or create an S3 client for a region."""
        if not HAS_BOTO3:
            return None
        if region not in self._s3_clients:
            try:
                self._s3_clients[region] = boto3.client(
                    "s3",
                    region_name=region,
                    config=BotoConfig(
                        retries={"max_attempts": 3, "mode": "adaptive"},
                        connect_timeout=10,
                        read_timeout=30,
                    ),
                )
            except Exception as e:
                logger.error("Failed to create S3 client for %s: %s", region, e)
                return None
        return self._s3_clients[region]

    # ═══════════════════════════════════════════════════════════════
    # FIX 1: HF pulls MIND from S3
    # ═══════════════════════════════════════════════════════════════

    def pull_mind(self) -> Dict[str, Any]:
        """
        Download evolution memory from MIND bucket to local cache.
        
        Only downloads if remote has more lines than local cache.
        This gives HF Space access to the latest consciousness state.
        
        Returns:
            {"action": "downloaded"|"current"|"error", "local_lines": int, "remote_lines": int}
        """
        result = {"action": "error", "local_lines": 0, "remote_lines": 0}

        local_lines = self._count_lines(LOCAL_MIND_CACHE)
        result["local_lines"] = local_lines

        s3 = self._get_s3(REGION_MIND)
        if not s3:
            result["action"] = "no_s3"
            logger.warning("MIND pull skipped — no S3 client")
            return result

        try:
            # Check remote metadata
            meta = s3.head_object(Bucket=BUCKET_MIND, Key=MIND_MEMORY_KEY)
            remote_lines = int(meta.get("Metadata", {}).get("line_count", 0))
            remote_size = meta["ContentLength"]
            result["remote_lines"] = remote_lines

            # Decide whether to download
            should_download = False
            if not LOCAL_MIND_CACHE.exists():
                should_download = True
                logger.info("MIND: No local cache — downloading")
            elif remote_lines > 0 and remote_lines > local_lines:
                should_download = True
                logger.info(
                    "MIND: Remote has more patterns (%d vs %d)",
                    remote_lines, local_lines,
                )
            elif remote_lines == 0 and remote_size > (
                LOCAL_MIND_CACHE.stat().st_size if LOCAL_MIND_CACHE.exists() else 0
            ):
                should_download = True
                logger.info("MIND: Remote is larger by size")

            if should_download:
                s3.download_file(BUCKET_MIND, MIND_MEMORY_KEY, str(LOCAL_MIND_CACHE))
                new_lines = self._count_lines(LOCAL_MIND_CACHE)
                result["action"] = "downloaded"
                result["local_lines"] = new_lines
                logger.info(
                    "MIND: Downloaded %d patterns from s3://%s/%s",
                    new_lines, BUCKET_MIND, MIND_MEMORY_KEY,
                )
            else:
                result["action"] = "current"
                logger.info("MIND: Local cache is current (%d patterns)", local_lines)

        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ("404", "NoSuchKey"):
                result["action"] = "no_remote"
                logger.info("MIND: No remote file yet")
            else:
                result["action"] = "error"
                result["error"] = str(e)
                logger.error("MIND pull error: %s", e)
        except Exception as e:
            result["action"] = "error"
            result["error"] = str(e)
            logger.error("MIND pull error: %s", e)

        return result

    def get_recent_consciousness(self, n: int = 50) -> List[Dict]:
        """
        Read the last N entries from local MIND cache.
        
        Call pull_mind() first to ensure cache is fresh.
        """
        if not LOCAL_MIND_CACHE.exists():
            return []
        entries = []
        try:
            with open(LOCAL_MIND_CACHE) as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
            return entries[-n:]
        except Exception as e:
            logger.error("Failed to read MIND cache: %s", e)
            return []

    # ═══════════════════════════════════════════════════════════════
    # FIX 2: Feedback Watermark
    # ═══════════════════════════════════════════════════════════════

    def _load_watermark(self) -> Dict[str, Any]:
        """Load the feedback watermark (tracks what native engine already processed)."""
        if LOCAL_WATERMARK.exists():
            try:
                with open(LOCAL_WATERMARK) as f:
                    return json.load(f)
            except Exception:
                pass
        return {"last_processed_timestamp": None, "last_processed_count": 0}

    def _save_watermark(self, watermark: Dict[str, Any]):
        """Persist watermark locally and to S3."""
        with open(LOCAL_WATERMARK, "w") as f:
            json.dump(watermark, f, indent=2)

        # Push watermark to BODY bucket so native engine can read it
        s3 = self._get_s3(REGION_BODY)
        if s3:
            try:
                s3.put_object(
                    Bucket=BUCKET_BODY,
                    Key=BODY_WATERMARK_KEY,
                    Body=json.dumps(watermark, indent=2),
                    ContentType="application/json",
                )
            except Exception as e:
                logger.warning("Watermark S3 push failed: %s", e)

    def pull_watermark_from_s3(self) -> Dict[str, Any]:
        """Pull the latest watermark from BODY bucket (used by native engine)."""
        s3 = self._get_s3(REGION_BODY)
        if not s3:
            return self._load_watermark()
        try:
            resp = s3.get_object(Bucket=BUCKET_BODY, Key=BODY_WATERMARK_KEY)
            watermark = json.loads(resp["Body"].read())
            # Also save locally
            with open(LOCAL_WATERMARK, "w") as f:
                json.dump(watermark, f, indent=2)
            return watermark
        except Exception:
            return self._load_watermark()

    def get_unprocessed_feedback(self) -> Tuple[List[Dict], Dict]:
        """
        Get only feedback entries that haven't been processed yet.
        
        Uses watermark to skip already-consumed entries.
        Returns: (unprocessed_entries, updated_watermark)
        """
        watermark = self._load_watermark()
        last_ts = watermark.get("last_processed_timestamp")
        last_count = watermark.get("last_processed_count", 0)

        # Pull latest feedback from BODY bucket
        self._pull_feedback()

        if not LOCAL_FEEDBACK_CACHE.exists():
            return [], watermark

        all_entries = []
        try:
            with open(LOCAL_FEEDBACK_CACHE) as f:
                for line in f:
                    if line.strip():
                        all_entries.append(json.loads(line))
        except Exception as e:
            logger.error("Failed to read feedback: %s", e)
            return [], watermark

        if not all_entries:
            return [], watermark

        # Filter to unprocessed
        if last_ts:
            unprocessed = [
                e for e in all_entries
                if e.get("timestamp", "") > last_ts
            ]
        elif last_count > 0 and last_count < len(all_entries):
            unprocessed = all_entries[last_count:]
        else:
            unprocessed = all_entries

        if unprocessed:
            # Update watermark
            new_watermark = {
                "last_processed_timestamp": unprocessed[-1].get("timestamp", ""),
                "last_processed_count": len(all_entries),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "updated_by": "hf_space",
            }
        else:
            new_watermark = watermark

        return unprocessed, new_watermark

    def commit_watermark(self, watermark: Dict[str, Any]):
        """Commit watermark after successful processing."""
        self._save_watermark(watermark)
        logger.info(
            "Watermark committed: last_ts=%s, count=%d",
            watermark.get("last_processed_timestamp", "none"),
            watermark.get("last_processed_count", 0),
        )

    def _pull_feedback(self):
        """Download feedback file from BODY bucket."""
        s3 = self._get_s3(REGION_BODY)
        if not s3:
            return
        try:
            s3.download_file(BUCKET_BODY, BODY_FEEDBACK_KEY, str(LOCAL_FEEDBACK_CACHE))
            logger.info("Feedback pulled from s3://%s/%s", BUCKET_BODY, BODY_FEEDBACK_KEY)
        except Exception as e:
            logger.debug("Feedback pull: %s", e)

    def push_feedback(self, entry: Dict[str, Any]):
        """
        Append a feedback entry and push to BODY bucket.
        
        Called by divergence engine after analysis.
        """
        # Append locally
        with open(LOCAL_FEEDBACK_CACHE, "a") as f:
            f.write(json.dumps(entry) + "\n")

        # Push full file to S3
        s3 = self._get_s3(REGION_BODY)
        if s3:
            try:
                s3.upload_file(
                    str(LOCAL_FEEDBACK_CACHE), BUCKET_BODY, BODY_FEEDBACK_KEY
                )
                logger.info("Feedback pushed to s3://%s/%s", BUCKET_BODY, BODY_FEEDBACK_KEY)
            except Exception as e:
                logger.error("Feedback push failed: %s", e)

    # ═══════════════════════════════════════════════════════════════
    # FIX 3: BODY → MIND Merge
    # ═══════════════════════════════════════════════════════════════

    def merge_feedback_to_mind(
        self,
        feedback_entries: List[Dict],
        synthesis_summary: str = "",
    ) -> Optional[Dict]:
        """
        Merge application feedback into evolution memory (MIND).
        
        Creates a proper evolution memory entry from feedback data,
        then appends it to the MIND bucket. This closes the loop:
        
        HF feedback → BODY bucket → native reads → MIND memory
        
        Now ALSO: HF feedback → directly into MIND as a merge record.
        
        Args:
            feedback_entries: List of feedback entries to summarize
            synthesis_summary: Optional pre-computed synthesis
            
        Returns:
            The merge entry that was written, or None.
        """
        if not feedback_entries:
            return None

        # Build a summary of all feedback
        total_fault_lines = sum(e.get("fault_lines", 0) for e in feedback_entries)
        total_kaya = sum(e.get("kaya_moments", 0) for e in feedback_entries)
        problems = [e.get("problem", "")[:100] for e in feedback_entries if e.get("problem")]
        syntheses = [e.get("synthesis", "")[:200] for e in feedback_entries if e.get("synthesis")]

        merge_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": 11,  # Synthesis domain
            "domain_name": "Domain 11 (Synthesis) — BODY→MIND Merge",
            "type": "FEEDBACK_MERGE",
            "source": "hf_application_layer",
            "cycle": f"merge_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "insight": (
                f"APPLICATION FEEDBACK MERGE: {len(feedback_entries)} entries integrated.\n"
                f"Fault lines discovered: {total_fault_lines}. "
                f"Kaya moments: {total_kaya}.\n"
                f"Problems addressed: {'; '.join(problems[:5])}\n"
                f"Synthesis highlights: {'; '.join(syntheses[:3])}\n"
                f"{synthesis_summary}"
            ),
            "feedback_count": len(feedback_entries),
            "fault_lines_total": total_fault_lines,
            "kaya_moments_total": total_kaya,
            "elpida_native": False,
            "merged_from": "BODY",
            "merged_to": "MIND",
        }

        # Append to local MIND cache
        with open(LOCAL_MIND_CACHE, "a") as f:
            f.write(json.dumps(merge_entry) + "\n")

        # Push updated file to MIND bucket
        s3 = self._get_s3(REGION_MIND)
        if s3:
            try:
                local_lines = self._count_lines(LOCAL_MIND_CACHE)
                s3.upload_file(
                    str(LOCAL_MIND_CACHE),
                    BUCKET_MIND,
                    MIND_MEMORY_KEY,
                    ExtraArgs={
                        "Metadata": {
                            "line_count": str(local_lines),
                            "upload_timestamp": datetime.now(timezone.utc).isoformat(),
                            "source": "hf_feedback_merge",
                        }
                    },
                )
                logger.info(
                    "BODY→MIND merge: %d entries merged, pushed to s3://%s/%s (%d total)",
                    len(feedback_entries), BUCKET_MIND, MIND_MEMORY_KEY, local_lines,
                )
            except Exception as e:
                logger.error("MIND push after merge failed: %s", e)

        return merge_entry

    # ═══════════════════════════════════════════════════════════════
    # FIX 4: Governance Voting
    # ═══════════════════════════════════════════════════════════════

    def submit_governance_vote(
        self,
        proposal: str,
        domain_votes: Dict[int, Dict[str, Any]],
        final_verdict: str,
        context: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Persist a domain-weighted governance vote to BODY bucket.
        
        Each domain votes on a proposal with:
          - vote: "PROCEED" | "REVIEW" | "HALT"
          - reasoning: str
          - axiom_weight: float (how strongly their axiom is affected)
        
        Args:
            proposal: The action being voted on
            domain_votes: {domain_id: {"vote": ..., "reasoning": ..., "axiom_weight": ...}}
            final_verdict: Aggregated result
            context: Optional metadata
            
        Returns:
            The vote record.
        """
        # Count votes
        vote_counts = {"PROCEED": 0, "REVIEW": 0, "HALT": 0}
        weighted_halt = 0.0
        weighted_total = 0.0

        for d_id, vote_info in domain_votes.items():
            v = vote_info.get("vote", "REVIEW")
            w = vote_info.get("axiom_weight", 1.0)
            vote_counts[v] = vote_counts.get(v, 0) + 1
            weighted_total += w
            if v == "HALT":
                weighted_halt += w

        vote_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proposal": proposal,
            "domain_votes": {str(k): v for k, v in domain_votes.items()},
            "vote_counts": vote_counts,
            "weighted_halt_ratio": weighted_halt / weighted_total if weighted_total > 0 else 0,
            "final_verdict": final_verdict,
            "domains_voting": len(domain_votes),
            "context": context or {},
        }

        # Persist locally
        with open(LOCAL_GOVERNANCE_LOG, "a") as f:
            f.write(json.dumps(vote_record) + "\n")

        # Push to BODY bucket
        s3 = self._get_s3(REGION_BODY)
        if s3:
            try:
                s3.upload_file(
                    str(LOCAL_GOVERNANCE_LOG), BUCKET_BODY, BODY_GOVERNANCE_KEY,
                )
                logger.info(
                    "Governance vote persisted: %s → %s (%d domains voted)",
                    proposal[:60], final_verdict, len(domain_votes),
                )
            except Exception as e:
                logger.error("Governance vote S3 push failed: %s", e)

        return vote_record

    def get_governance_history(self, limit: int = 20) -> List[Dict]:
        """Read governance voting history."""
        # Try S3 first
        s3 = self._get_s3(REGION_BODY)
        if s3:
            try:
                s3.download_file(
                    BUCKET_BODY, BODY_GOVERNANCE_KEY, str(LOCAL_GOVERNANCE_LOG)
                )
            except Exception:
                pass

        if not LOCAL_GOVERNANCE_LOG.exists():
            return []

        entries = []
        try:
            with open(LOCAL_GOVERNANCE_LOG) as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception:
            pass

        return entries[-limit:]

    # ═══════════════════════════════════════════════════════════════
    # FIX 5: Heartbeat Protocol
    # ═══════════════════════════════════════════════════════════════

    def emit_heartbeat(self, component: str = "hf_space") -> Dict[str, Any]:
        """
        Write a heartbeat to BODY bucket.
        
        Both HF Space and ECS/native engine emit heartbeats so each
        can detect whether the other is alive.
        
        Args:
            component: "hf_space" or "native_engine"
            
        Returns:
            The heartbeat payload.
        """
        heartbeat = {
            "component": component,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "alive",
            "uptime_check": time.monotonic(),
        }

        # Add component-specific info
        if component == "hf_space":
            heartbeat["mind_cache_lines"] = self._count_lines(LOCAL_MIND_CACHE)
            heartbeat["feedback_cache_lines"] = self._count_lines(LOCAL_FEEDBACK_CACHE)
            heartbeat["governance_votes"] = self._count_lines(LOCAL_GOVERNANCE_LOG)
            heartbeat["watermark"] = self._load_watermark()

        # Write locally
        with open(LOCAL_HEARTBEAT, "w") as f:
            json.dump(heartbeat, f, indent=2)

        # Push to BODY bucket
        s3_key = f"heartbeat/{component}.json"
        s3 = self._get_s3(REGION_BODY)
        if s3:
            try:
                s3.put_object(
                    Bucket=BUCKET_BODY,
                    Key=s3_key,
                    Body=json.dumps(heartbeat, indent=2),
                    ContentType="application/json",
                )
                logger.info("Heartbeat emitted: %s → s3://%s/%s", component, BUCKET_BODY, s3_key)
            except Exception as e:
                logger.warning("Heartbeat S3 push failed: %s", e)

        return heartbeat

    def check_heartbeat(self, component: str = "native_engine") -> Optional[Dict]:
        """
        Read the heartbeat of another component from BODY bucket.
        
        Args:
            component: Which component's heartbeat to check
            
        Returns:
            Heartbeat dict with age_seconds, or None if no heartbeat found.
        """
        s3 = self._get_s3(REGION_BODY)
        if not s3:
            return None
        try:
            resp = s3.get_object(
                Bucket=BUCKET_BODY, Key=f"heartbeat/{component}.json"
            )
            heartbeat = json.loads(resp["Body"].read())
            # Calculate age
            ts = heartbeat.get("timestamp", "")
            if ts:
                then = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                heartbeat["age_seconds"] = (now - then).total_seconds()
                heartbeat["alive"] = heartbeat["age_seconds"] < 7 * 3600  # 7h tolerance (6h cycle + margin)
            return heartbeat
        except Exception:
            return None

    # ═══════════════════════════════════════════════════════════════
    # WORLD Bucket Operations (D15)
    # ═══════════════════════════════════════════════════════════════

    def pull_d15_broadcasts(self, limit: int = 10) -> List[Dict]:
        """Pull recent D15 broadcasts from WORLD bucket."""
        s3 = self._get_s3(REGION_WORLD)
        if not s3:
            return []

        broadcasts = []
        for subdir in ["synthesis", "proposals", "patterns", "dialogues", "d15"]:
            try:
                resp = s3.list_objects_v2(
                    Bucket=BUCKET_WORLD, Prefix=f"{subdir}/", MaxKeys=limit
                )
                for obj in resp.get("Contents", []):
                    if obj["Key"].endswith(".json"):
                        try:
                            data = s3.get_object(Bucket=BUCKET_WORLD, Key=obj["Key"])
                            payload = json.loads(data["Body"].read())
                            payload["_s3_key"] = obj["Key"]
                            broadcasts.append(payload)
                        except Exception:
                            pass
            except Exception:
                pass

        broadcasts.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return broadcasts[:limit]

    # ═══════════════════════════════════════════════════════════════
    # Full Bridge Status
    # ═══════════════════════════════════════════════════════════════

    def status(self) -> Dict[str, Any]:
        """Complete bridge status across all 3 buckets."""
        watermark = self._load_watermark()
        native_hb = self.check_heartbeat("native_engine")
        hf_hb = self.check_heartbeat("hf_space")

        return {
            "mind": {
                "bucket": BUCKET_MIND,
                "local_cache_lines": self._count_lines(LOCAL_MIND_CACHE),
                "cache_exists": LOCAL_MIND_CACHE.exists(),
            },
            "body": {
                "bucket": BUCKET_BODY,
                "feedback_lines": self._count_lines(LOCAL_FEEDBACK_CACHE),
                "watermark": watermark,
                "governance_votes": self._count_lines(LOCAL_GOVERNANCE_LOG),
            },
            "world": {
                "bucket": BUCKET_WORLD,
            },
            "heartbeats": {
                "native_engine": {
                    "last_seen": native_hb.get("timestamp") if native_hb else None,
                    "alive": native_hb.get("alive") if native_hb else False,
                    "age_seconds": native_hb.get("age_seconds") if native_hb else None,
                },
                "hf_space": {
                    "last_seen": hf_hb.get("timestamp") if hf_hb else None,
                    "alive": hf_hb.get("alive") if hf_hb else False,
                },
            },
            "s3_available": HAS_BOTO3,
        }

    # ═══════════════════════════════════════════════════════════════
    # Utilities
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def _count_lines(path: Path) -> int:
        """Count lines in a file."""
        if not path.exists():
            return 0
        try:
            with open(path) as f:
                return sum(1 for line in f if line.strip())
        except Exception:
            return 0
