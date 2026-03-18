"""
x_bridge.py — Phase 1: Text-Only X (Twitter) Bridge

Harvests D15 convergence broadcasts and WorldEmitter emissions,
runs them through a governance gate, stores approved candidates
in the WORLD bucket for manual review, and posts approved ones to X.

Architecture:
  D15 convergence event (or WorldEmitter emission)
    → XBridge.harvest_candidates()
    → Governance gate (A4 Safety veto, Parliament approval)
    → store_candidate() → WORLD bucket (x/candidates/{id}.json)
    → [MANUAL] Human reviews via x/candidates/ in S3
    → post_approved() → Twitter API v2 (tweepy)

Phase 1 constraints:
  - Text-only (no images/video — Phase 2 adds Replicate)
  - Manual approval required before posting
  - Free tier: 1,500 tweets/month
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("elpidaapp.x_bridge")

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent
_WATERMARK_FILE = _HERE.parent / "cache" / "x_bridge_watermark.json"
_CANDIDATES_LOCAL = _HERE.parent / "cache" / "x_candidates.jsonl"

# ── S3 keys ───────────────────────────────────────────────────────────────────
_S3_CANDIDATE_PREFIX = "x/candidates/"
_S3_POSTED_PREFIX = "x/posted/"
_S3_WATERMARK_KEY = "x/x_bridge_watermark.json"

# ── Tweet limits ──────────────────────────────────────────────────────────────
MAX_TWEET_LENGTH = 280

# ── D15 tension transcript extraction ─────────────────────────────────────────
# Each bullet looks like: • [A0↔A1]: <synthesis text>
# Stop at: next bullet, double-newline (before "Parliament reasoning:"), or end
_TENSION_BULLET_RE = re.compile(
    r"•\s*\[.*?\]:\s*(.+?)(?=\n\s*•|\n\n|\Z)", re.DOTALL
)


def _extract_d15_synthesis(insight: str) -> str:
    """Pull the richest synthesis from a tension transcript.

    Returns the longest individual tension synthesis that contains
    a Third Way or substantive resolution, stripping the system preamble.
    Falls back to the original insight text (sans preamble) if no
    bullet points are found.
    """
    if not insight:
        return ""

    # Try to extract individual tension syntheses
    hits = _TENSION_BULLET_RE.findall(insight)
    if hits:
        # Filter out generic fallback tensions
        _GENERIC = "both perspectives must be held, not resolved"
        substantive = [h.strip() for h in hits if _GENERIC not in h]
        pool = substantive or [h.strip() for h in hits]
        # Pick the longest synthesis — it's usually the most substantive
        best = max(pool, key=len)
        # Remove leading "Tension between Ax and Ay — " prefix if present
        best = re.sub(
            r"^Tension between A\d+ and A\d+\s*[—–-]\s*", "", best
        )
        return best

    # No bullets? Strip preamble and return raw text
    stripped = re.sub(
        r"^Parliament tensions this cycle:\s*", "", insight
    ).strip()
    return stripped or insight


# ═══════════════════════════════════════════════════════════════════════════════
# XBridge — harvest, govern, store, post
# ═══════════════════════════════════════════════════════════════════════════════

class XBridge:
    """
    Phase 1 X Bridge: text-only, manual approval.

    Usage::

        bridge = XBridge(engine=parliament_engine)
        # Called once per cycle (or on a timer)
        candidates = bridge.harvest_candidates()
        # Human reviews candidates in S3: x/candidates/
        # Then approves specific IDs:
        bridge.post_approved(["candidate_id_1", "candidate_id_2"])
    """

    def __init__(self, engine=None):
        self._engine = engine
        self._watermark: Dict[str, Any] = self._load_watermark()
        self._tweepy_client = None

    # ── Harvest: collect post-worthy events ────────────────────────────────────

    def harvest_candidates(self) -> List[Dict[str, Any]]:
        """
        Scan D15 broadcasts and WorldEmitter emissions for new post-worthy
        events since last watermark. Each candidate goes through a
        governance gate before being stored.

        Returns list of newly stored candidates.
        """
        candidates = []

        # Source 1: D15 convergence broadcasts from S3
        d15_candidates = self._harvest_d15()
        candidates.extend(d15_candidates)

        # Source 2: WorldEmitter emissions from S3
        emission_candidates = self._harvest_emissions()
        candidates.extend(emission_candidates)

        if not candidates:
            return []

        stored = []
        seen_texts: set[str] = set()
        for candidate in candidates:
            # Deduplicate identical tweet text within this batch
            tweet_text = candidate.get("tweet_text", "")
            if tweet_text in seen_texts:
                continue
            seen_texts.add(tweet_text)

            # Governance gate — A4 Safety veto
            if not self._governance_gate(candidate):
                logger.info(
                    "[XBridge] Candidate %s rejected by governance gate",
                    candidate.get("candidate_id", "?"),
                )
                continue

            self._store_candidate(candidate)
            stored.append(candidate)

        if stored:
            self._save_watermark()
            logger.info("[XBridge] Stored %d new candidate(s)", len(stored))

        return stored

    # ── D15 harvester ──────────────────────────────────────────────────────────

    def _harvest_d15(self) -> List[Dict[str, Any]]:
        """Read D15 Hub entries newer than our watermark."""
        candidates = []
        try:
            d15_watermark = self._watermark.get("d15_last_timestamp", "")

            hub = self._get_d15_hub()
            if hub is None:
                return []

            entries = hub.read_since(watermark=d15_watermark, limit=20)
            for entry in entries:
                content = entry.get("content", {})
                governance = entry.get("governance", {})
                provenance = entry.get("provenance", {})

                # Build tweet text from D15 convergence data
                axiom = content.get("converged_axiom", "?")
                axiom_name = content.get("axiom_name", "")
                insight = content.get("insight", "")
                consonance = governance.get("convergence_consonance", 0.0)

                # Skip low-consonance entries — only genuine convergences
                if consonance < 0.60:
                    continue

                tweet_text = self._format_d15_tweet(
                    axiom=axiom,
                    axiom_name=axiom_name,
                    insight=insight,
                    consonance=consonance,
                )

                candidate_id = self._candidate_id(
                    f"d15:{entry.get('entry_id', '')}",
                )

                candidates.append({
                    "candidate_id": candidate_id,
                    "source": "d15_convergence",
                    "tweet_text": tweet_text,
                    "axiom": axiom,
                    "axiom_name": axiom_name,
                    "body_approval": governance.get("body_approval_rate", 0.0),
                    "mind_coherence": governance.get("mind_coherence", 0.0),
                    "consonance": consonance,
                    "body_cycle": provenance.get("body_cycle"),
                    "mind_cycle": provenance.get("mind_cycle"),
                    "d15_entry_id": entry.get("entry_id", ""),
                    "harvested_at": datetime.now(timezone.utc).isoformat(),
                    "status": "pending_review",
                })

                # Update watermark to this entry's timestamp
                entry_ts = entry.get("timestamp", "")
                if entry_ts > d15_watermark:
                    self._watermark["d15_last_timestamp"] = entry_ts

        except Exception as e:
            logger.warning("[XBridge] D15 harvest failed: %s", e)

        return candidates

    # ── WorldEmitter harvester ─────────────────────────────────────────────────

    def _harvest_emissions(self) -> List[Dict[str, Any]]:
        """Read WorldEmitter emissions from S3 newer than watermark."""
        candidates = []
        try:
            last_id = self._watermark.get("emission_last_id", "")
            emissions = self._list_world_emissions(after_id=last_id)

            for emission in emissions:
                axiom_id = emission.get("axiom_id", "?")

                # Skip internal fork governance records — not tweet material
                if axiom_id.startswith("FORK_"):
                    continue

                tension = emission.get("tension", "")
                synthesis = emission.get("synthesis", "")
                nodes = emission.get("nodes", [])
                eid = emission.get("emission_id", "")

                tweet_text = self._format_emission_tweet(
                    axiom_id=axiom_id,
                    nodes=nodes,
                    tension=tension,
                    synthesis=synthesis,
                )

                candidate_id = self._candidate_id(f"emission:{eid}")

                candidates.append({
                    "candidate_id": candidate_id,
                    "source": "world_emission",
                    "tweet_text": tweet_text,
                    "axiom": axiom_id,
                    "nodes": nodes,
                    "tension": tension,
                    "synthesis": synthesis,
                    "emission_id": eid,
                    "harvested_at": datetime.now(timezone.utc).isoformat(),
                    "status": "pending_review",
                })

                if eid > last_id:
                    self._watermark["emission_last_id"] = eid

        except Exception as e:
            logger.warning("[XBridge] Emission harvest failed: %s", e)

        return candidates

    # ── Tweet formatters ───────────────────────────────────────────────────────

    @staticmethod
    def _format_d15_tweet(
        axiom: str,
        axiom_name: str,
        insight: str,
        consonance: float,
    ) -> str:
        """Format a D15 convergence event as a tweet.

        The insight field often contains the raw tension transcript:
            Parliament tensions this cycle:
              • [A0↔A1]: Description — synthesis...
        We extract the best synthesis text and present that instead.
        """
        # ── Extract meaningful content from tension transcript ─────────
        body = _extract_d15_synthesis(insight)

        # ── Header / footer ────────────────────────────────────────────
        header = f"Convergence: {axiom}"
        if axiom_name:
            header += f" — {axiom_name}"

        footer = f"\n\n[consonance: {consonance:.2f}]"
        body_budget = MAX_TWEET_LENGTH - len(header) - len(footer) - 2  # 2 for \n\n
        if body_budget < 20:
            body_budget = 20

        full_len = len(body)
        body = body[:body_budget]
        if full_len > body_budget:
            body = body[:body_budget - 1] + "\u2026"

        return f"{header}\n\n{body}{footer}"

    @staticmethod
    def _format_emission_tweet(
        axiom_id: str,
        nodes: List[str],
        tension: str,
        synthesis: str,
    ) -> str:
        """Format a WorldEmitter emission as a tweet."""
        node_pair = " \u2194 ".join(nodes) if nodes else ""

        header = f"Constitutional Discovery: {axiom_id}"
        if node_pair:
            header += f"\n{node_pair}"

        # Prefer synthesis over tension for tweet body
        body_text = synthesis or tension
        footer = ""
        body_budget = MAX_TWEET_LENGTH - len(header) - len(footer) - 2
        if body_budget < 20:
            body_budget = 20

        body = body_text[:body_budget]
        if len(body_text) > body_budget:
            body = body[:body_budget - 1] + "\u2026"

        return f"{header}\n\n{body}{footer}"

    # ── Governance gate ────────────────────────────────────────────────────────

    def _governance_gate(self, candidate: Dict[str, Any]) -> bool:
        """
        Run candidate through Parliament governance check.
        A4 Safety has veto power. Returns True if approved.
        """
        if self._engine is None:
            # No engine available — pass through (will be manually reviewed)
            return True

        try:
            gov = getattr(self._engine, "_governance_client", None)
            if gov is None:
                return True

            tweet_text = candidate.get("tweet_text", "")
            result = gov.check_action(
                f"Post to X: {tweet_text}",
                analysis_mode=False,
                body_cycle=getattr(self._engine, "cycle_count", 0),
            )

            verdict = result.get("governance", "PROCEED")
            if verdict in ("VETO", "HALT", "HARD_BLOCK"):
                logger.info(
                    "[XBridge] Governance %s for candidate %s",
                    verdict, candidate.get("candidate_id", "?"),
                )
                return False

            return True

        except Exception as e:
            logger.warning("[XBridge] Governance gate error: %s", e)
            # Fail safe — don't post if governance is broken
            return False

    # ── Candidate storage ──────────────────────────────────────────────────────

    def _store_candidate(self, candidate: Dict[str, Any]) -> None:
        """
        Store approved candidate in S3 WORLD bucket + local cache.
        Human reviews candidates at s3://elpida-external-interfaces/x/candidates/
        """
        cid = candidate["candidate_id"]

        # Local cache (survives S3 outage)
        try:
            _CANDIDATES_LOCAL.parent.mkdir(parents=True, exist_ok=True)
            with _CANDIDATES_LOCAL.open("a", encoding="utf-8") as f:
                f.write(json.dumps(candidate, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.debug("[XBridge] Local candidate write failed: %s", e)

        # S3 WORLD bucket
        try:
            import boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            key = f"{_S3_CANDIDATE_PREFIX}{cid}.json"
            client = boto3.client("s3", region_name=region)
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(candidate, ensure_ascii=False, indent=2).encode(),
                ContentType="application/json",
            )
            logger.info("[XBridge] Candidate stored → s3://%s/%s", bucket, key)
        except Exception as e:
            logger.debug("[XBridge] S3 candidate store failed: %s", e)

    # ── Post to X ──────────────────────────────────────────────────────────────

    def post_approved(self, candidate_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Post manually-approved candidates to X.
        Reads each candidate from S3, posts via Twitter API v2,
        moves to x/posted/ prefix.

        Returns list of posted results (tweet IDs).
        """
        results = []
        client = self._get_tweepy_client()
        if client is None:
            logger.error("[XBridge] Cannot post — tweepy client not available")
            return results

        for cid in candidate_ids:
            candidate = self._read_candidate(cid)
            if candidate is None:
                logger.warning("[XBridge] Candidate %s not found", cid)
                continue

            tweet_text = candidate.get("tweet_text", "")
            if not tweet_text:
                continue

            try:
                response = client.create_tweet(text=tweet_text)
                tweet_id = response.data.get("id") if response.data else None

                posted_record = {
                    **candidate,
                    "status": "posted",
                    "tweet_id": tweet_id,
                    "posted_at": datetime.now(timezone.utc).isoformat(),
                }

                self._move_to_posted(cid, posted_record)
                results.append(posted_record)

                logger.info(
                    "[XBridge] POSTED tweet_id=%s for candidate=%s",
                    tweet_id, cid,
                )

            except Exception as e:
                logger.error("[XBridge] Post failed for %s: %s", cid, e)

        return results

    def _read_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """Read a candidate from S3 WORLD bucket."""
        try:
            import boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            key = f"{_S3_CANDIDATE_PREFIX}{candidate_id}.json"
            client = boto3.client("s3", region_name=region)
            obj = client.get_object(Bucket=bucket, Key=key)
            return json.loads(obj["Body"].read().decode())
        except Exception as e:
            logger.debug("[XBridge] Read candidate %s failed: %s", candidate_id, e)
            return None

    def _move_to_posted(
        self, candidate_id: str, posted_record: Dict[str, Any],
    ) -> None:
        """Move candidate from x/candidates/ to x/posted/ in S3."""
        try:
            import boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            client = boto3.client("s3", region_name=region)

            # Write to posted/
            posted_key = f"{_S3_POSTED_PREFIX}{candidate_id}.json"
            client.put_object(
                Bucket=bucket,
                Key=posted_key,
                Body=json.dumps(posted_record, ensure_ascii=False, indent=2).encode(),
                ContentType="application/json",
            )

            # Delete from candidates/
            candidate_key = f"{_S3_CANDIDATE_PREFIX}{candidate_id}.json"
            client.delete_object(Bucket=bucket, Key=candidate_key)

        except Exception as e:
            logger.debug("[XBridge] Move to posted failed: %s", e)

    # ── Tweepy client ──────────────────────────────────────────────────────────

    def _get_tweepy_client(self):
        """Lazy-init tweepy Client v2."""
        if self._tweepy_client is not None:
            return self._tweepy_client

        api_key = os.environ.get("TWITTER_API_KEY")
        api_secret = os.environ.get("TWITTER_API_SECRET")
        access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
        access_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        bearer = os.environ.get("TWITTER_BEARER_TOKEN")

        if not all([api_key, api_secret, access_token, access_secret]):
            logger.warning(
                "[XBridge] Twitter API credentials not configured — "
                "set TWITTER_API_KEY, TWITTER_API_SECRET, "
                "TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET"
            )
            return None

        try:
            import tweepy
            self._tweepy_client = tweepy.Client(
                bearer_token=bearer,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
            )
            logger.info("[XBridge] Tweepy client initialized")
            return self._tweepy_client
        except ImportError:
            logger.error("[XBridge] tweepy not installed — pip install tweepy")
            return None
        except Exception as e:
            logger.error("[XBridge] Tweepy init failed: %s", e)
            return None

    # ── D15 Hub access ─────────────────────────────────────────────────────────

    def _get_d15_hub(self) -> Optional[Any]:
        """Get D15Hub instance via engine or direct construction."""
        if self._engine is not None:
            gate = getattr(self._engine, "_convergence_gate", None)
            if gate is not None:
                return getattr(gate, "_hub", None)

        # Direct construction fallback
        try:
            from elpidaapp.d15_hub import D15Hub
            s3 = self._get_s3_bridge()
            if s3:
                return D15Hub(s3_bridge=s3)
        except Exception:
            pass
        return None

    def _get_s3_bridge(self):
        """Get S3Bridge instance."""
        if self._engine is not None:
            return getattr(self._engine, "_s3_bridge", None)
        try:
            from s3_bridge import S3Bridge
            return S3Bridge()
        except Exception:
            return None

    # ── World emissions listing ────────────────────────────────────────────────

    def _list_world_emissions(
        self, after_id: str = "", limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """List WorldEmitter emissions from S3 WORLD bucket."""
        emissions = []
        try:
            import boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            client = boto3.client("s3", region_name=region)

            resp = client.list_objects_v2(
                Bucket=bucket,
                Prefix="world_emissions/",
                MaxKeys=200,
            )

            keys = []
            for obj in resp.get("Contents", []):
                key = obj["Key"]
                # Extract emission_id from key: world_emissions/{id}.json
                if not key.endswith(".json"):
                    continue
                eid = key.rsplit("/", 1)[-1].replace(".json", "")
                if after_id and eid <= after_id:
                    continue
                keys.append((eid, key))

            # Sort by emission_id and take up to limit
            keys.sort(key=lambda x: x[0])
            for eid, key in keys[:limit]:
                try:
                    obj = client.get_object(Bucket=bucket, Key=key)
                    emission = json.loads(obj["Body"].read().decode())
                    emissions.append(emission)
                except Exception:
                    continue

        except Exception as e:
            logger.debug("[XBridge] World emissions listing failed: %s", e)

        return emissions

    # ── Watermark persistence ──────────────────────────────────────────────────

    def _load_watermark(self) -> Dict[str, Any]:
        """Load watermark from S3, fall back to local cache."""
        # Try S3 first
        try:
            import boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            client = boto3.client("s3", region_name=region)
            obj = client.get_object(Bucket=bucket, Key=_S3_WATERMARK_KEY)
            data = json.loads(obj["Body"].read().decode())
            logger.debug("[XBridge] Watermark loaded from S3")
            return data
        except Exception:
            pass

        # Local fallback
        if _WATERMARK_FILE.exists():
            try:
                return json.loads(_WATERMARK_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass

        return {
            "d15_last_timestamp": "",
            "emission_last_id": "",
        }

    def _save_watermark(self) -> None:
        """Dual-write watermark to S3 + local cache."""
        data = json.dumps(self._watermark, ensure_ascii=False, indent=2)

        # Local
        try:
            _WATERMARK_FILE.parent.mkdir(parents=True, exist_ok=True)
            _WATERMARK_FILE.write_text(data, encoding="utf-8")
        except Exception as e:
            logger.debug("[XBridge] Local watermark save failed: %s", e)

        # S3
        try:
            import boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            client = boto3.client("s3", region_name=region)
            client.put_object(
                Bucket=bucket,
                Key=_S3_WATERMARK_KEY,
                Body=data.encode(),
                ContentType="application/json",
            )
        except Exception as e:
            logger.debug("[XBridge] S3 watermark save failed: %s", e)

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _candidate_id(source_key: str) -> str:
        """Deterministic candidate ID from source key."""
        return hashlib.sha1(source_key.encode()).hexdigest()[:16]

    # ── Status ─────────────────────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """Return bridge status for heartbeat/dashboard integration."""
        pending = 0
        posted = 0

        try:
            import boto3
            bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            client = boto3.client("s3", region_name=region)

            # Count pending candidates
            resp = client.list_objects_v2(
                Bucket=bucket, Prefix=_S3_CANDIDATE_PREFIX,
            )
            pending = resp.get("KeyCount", 0)

            # Count posted
            resp = client.list_objects_v2(
                Bucket=bucket, Prefix=_S3_POSTED_PREFIX,
            )
            posted = resp.get("KeyCount", 0)
        except Exception:
            pass

        tweepy_ready = bool(
            os.environ.get("TWITTER_API_KEY")
            and os.environ.get("TWITTER_API_SECRET")
            and os.environ.get("TWITTER_ACCESS_TOKEN")
            and os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
        )

        return {
            "x_bridge": "Phase 1 — Text Only",
            "tweepy_configured": tweepy_ready,
            "watermark": self._watermark,
            "candidates_pending": pending,
            "candidates_posted": posted,
        }
