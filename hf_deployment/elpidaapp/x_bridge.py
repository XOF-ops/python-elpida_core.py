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
        """Read D15 broadcast files from S3 WORLD bucket.

        These broadcasts contain LLM-synthesized d15_output text —
        the rich, tweet-worthy content written by Claude during the
        D15 convergence gate pipeline.
        """
        candidates = []
        try:
            d15_watermark = self._watermark.get("d15_last_timestamp", "")

            import boto3
            bucket = os.environ.get(
                "AWS_S3_BUCKET_WORLD", "elpida-external-interfaces",
            )
            region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
            client = boto3.client("s3", region_name=region)

            resp = client.list_objects_v2(
                Bucket=bucket,
                Prefix="d15/broadcast_",
                MaxKeys=200,
            )

            # Sort by key (timestamp-ordered filenames)
            keys = sorted(
                (o["Key"] for o in resp.get("Contents", [])),
                reverse=False,
            )

            for key in keys:
                obj = client.get_object(Bucket=bucket, Key=key)
                broadcast = json.loads(obj["Body"].read().decode())

                ts = broadcast.get("timestamp", "")
                if ts and ts <= d15_watermark:
                    continue

                d15_output = broadcast.get("d15_output", "")
                if not d15_output:
                    continue

                # Skip raw tension transcripts (LLM synthesis failed)
                if d15_output.startswith("Parliament tensions"):
                    continue

                axioms = broadcast.get("axioms_in_tension", [])
                axiom = axioms[0] if axioms else "?"
                governance = broadcast.get("governance", {})
                parliament = governance.get("parliament", {})
                bid = broadcast.get("broadcast_id", "")

                tweet_text = self._format_d15_tweet(
                    axiom=axiom,
                    d15_output=d15_output,
                )

                candidate_id = self._candidate_id(f"d15:{bid}")

                candidates.append({
                    "candidate_id": candidate_id,
                    "source": "d15_broadcast",
                    "tweet_text": tweet_text,
                    "axiom": axiom,
                    "body_approval": parliament.get("approval_rate", 0.0),
                    "broadcast_id": bid,
                    "harvested_at": datetime.now(timezone.utc).isoformat(),
                    "status": "pending_review",
                })

                # Update watermark
                if ts > d15_watermark:
                    self._watermark["d15_last_timestamp"] = ts

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
        d15_output: str,
    ) -> str:
        """Format a D15 broadcast as a tweet.

        The d15_output is LLM-synthesized text from the convergence gate
        pipeline — already polished, human-readable prose. We just need
        to trim it to 280 chars.
        """
        # Strip the "**D15 WORLD BROADCAST**" header if present
        body = re.sub(
            r"^\*{0,2}D15 WORLD BROADCAST\*{0,2}\s*", "", d15_output,
        ).strip()

        if len(body) <= MAX_TWEET_LENGTH:
            return body

        # Truncate at the last sentence boundary that fits
        truncated = body[:MAX_TWEET_LENGTH - 1]
        # Try to break at a sentence ending
        for sep in (". ", ".\n", "? ", "! "):
            last = truncated.rfind(sep)
            if last > MAX_TWEET_LENGTH // 2:
                return truncated[: last + 1].strip()
        return truncated.rstrip() + "\u2026"

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
            "read_enabled": os.environ.get("X_READ_ENABLED", "false").lower() == "true",
        }

    # ── Mention reader (Phase 1.5 — off by default) ───────────────────────────

    def read_mentions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Read recent mentions/replies and route them as human voice input.

        Requires X Basic tier ($200/month) and X_READ_ENABLED=true.
        Reads mentions since last watermark, scores governance relevance,
        and writes qualifying replies to pending_human_votes.jsonl in S3
        for HumanVoiceAgent to pick up.

        Returns list of processed mentions.
        """
        if os.environ.get("X_READ_ENABLED", "false").lower() != "true":
            return []

        client = self._get_tweepy_client()
        if not client:
            return []

        username = os.environ.get("TWITTER_USERNAME", "")
        if not username:
            logger.info("[XBridge] TWITTER_USERNAME not set — skipping mention read")
            return []

        since_id = self._watermark.get("mention_since_id")
        processed = []

        try:
            # Get authenticated user ID
            me = client.get_me()
            if not me or not me.data:
                return []
            user_id = me.data.id

            kwargs = {"max_results": min(limit, 100)}
            if since_id:
                kwargs["since_id"] = since_id

            resp = client.get_users_mentions(user_id, **kwargs)
            if not resp or not resp.data:
                return []

            for tweet in resp.data:
                text = tweet.text or ""
                # Strip @mention prefix
                clean = re.sub(r"@\w+\s*", "", text).strip()
                if len(clean) < 10:
                    continue

                # Score governance relevance (simple keyword match)
                score = self._score_governance_relevance(clean)
                if score < 0.3:
                    continue

                entry = {
                    "source": "x_mention",
                    "tweet_id": str(tweet.id),
                    "text": clean[:500],
                    "relevance_score": score,
                    "received_at": datetime.now(timezone.utc).isoformat(),
                }
                processed.append(entry)

                # Update since_id watermark
                if not since_id or tweet.id > int(since_id):
                    since_id = str(tweet.id)

            # Write to S3 for HumanVoiceAgent pickup
            if processed:
                self._write_human_votes(processed)
                self._watermark["mention_since_id"] = since_id
                self._save_watermark()
                logger.info(
                    "[XBridge] Processed %d mentions (since_id=%s)",
                    len(processed), since_id,
                )

        except Exception as e:
            logger.warning("[XBridge] read_mentions failed: %s", e)

        return processed

    @staticmethod
    def _score_governance_relevance(text: str) -> float:
        """Score how governance-relevant a mention is (0.0-1.0)."""
        low = text.lower()
        _GOV_KEYWORDS = [
            "governance", "axiom", "tension", "parliament", "ethics",
            "privacy", "autonomy", "collective", "individual", "rights",
            "freedom", "justice", "safety", "transparency", "ai",
            "dilemma", "trade-off", "tradeoff", "balance",
        ]
        hits = sum(1 for kw in _GOV_KEYWORDS if kw in low)
        return min(1.0, hits * 0.2)

    def _write_human_votes(self, entries: List[Dict[str, Any]]) -> None:
        """Append mention entries to pending_human_votes.jsonl in S3."""
        try:
            import boto3
            bucket = os.environ.get(
                "AWS_S3_BUCKET_BODY", "elpida-body-evolution",
            )
            region = os.environ.get("AWS_S3_REGION_BODY", "eu-north-1")
            client = boto3.client("s3", region_name=region)

            key = "pending_human_votes.jsonl"

            # Read existing content
            existing = ""
            try:
                obj = client.get_object(Bucket=bucket, Key=key)
                existing = obj["Body"].read().decode()
            except client.exceptions.NoSuchKey:
                pass
            except Exception:
                pass

            # Append new entries
            lines = existing.rstrip("\n")
            for entry in entries:
                lines += "\n" + json.dumps(entry, ensure_ascii=False)
            lines = lines.lstrip("\n")

            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=lines.encode(),
                ContentType="application/json",
            )
        except Exception as e:
            logger.warning("[XBridge] Write human votes failed: %s", e)
