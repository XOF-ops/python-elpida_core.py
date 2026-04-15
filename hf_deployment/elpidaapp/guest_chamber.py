"""
Guest Chamber — Human Voices Enter the Parliament
===================================================

Routes external human questions through S3 into the BODY's
InputBuffer. The Parliament deliberates on human tensions
with the same constitutional rigour it applies to world events.

S3 Layout:
  s3://elpida-external-interfaces/guest_chamber/questions.jsonl
  s3://elpida-external-interfaces/guest_chamber/watermark.json

Each question is framed as an I↔WE tension before it enters
Parliament. The framing preserves the human's original words
while exposing the structural conflict the question contains.

Usage (BODY side — HF Space):
    from elpidaapp.guest_chamber import GuestChamberFeed
    feed = GuestChamberFeed(engine.input_buffer)
    feed.start()   # background poll thread

Usage (operator side — CLI):
    python feed_elpida.py "What is consciousness?"
    python feed_elpida.py --author "Nikos" "Does Elpida dream?"
"""

import json
import logging
import os
import random
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("elpida.guest_chamber")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BUCKET = os.getenv("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
QUESTIONS_KEY = "guest_chamber/questions.jsonl"
WATERMARK_KEY = "guest_chamber/watermark.json"
LOCAL_CACHE = Path("guest_chamber_cache.jsonl")
LOCAL_WATERMARK = Path("guest_chamber_watermark.json")

POLL_INTERVAL_S = 30           # Check for new questions every 30 seconds
MAX_QUESTIONS_PER_POLL = 3     # Don't flood Parliament — 3 at a time

# ---------------------------------------------------------------------------
# I↔WE tension framing for human questions
# ---------------------------------------------------------------------------

TENSION_FRAMES = [
    (
        "A human guest asks: \"{question}\"\n"
        "The I-position: individual curiosity — one person's need to understand.\n"
        "The WE-position: collective wisdom — how the Parliament's answer "
        "serves all future questioners, not just this one.\n"
        "Tension: an answer precise enough for this person may be too narrow "
        "for the collective; an answer universal enough for all may fail "
        "to honour this specific question."
    ),
    (
        "Guest Chamber question from {author}: \"{question}\"\n"
        "The I-position: the questioner's unique context — their life, "
        "their moment of wondering.\n"
        "The WE-position: the system's constitutional integrity — "
        "answering without compromising the axioms.\n"
        "Tension: responsiveness to a single voice risks privileging "
        "one perspective; constitutional purity risks ignoring "
        "the human who knocked."
    ),
    (
        "A voice from outside enters: \"{question}\"\n"
        "The I-position: this question deserves a direct, personal answer.\n"
        "The WE-position: every answer becomes precedent — "
        "what we say to one, we say to the constitution.\n"
        "Tension: hospitality toward the guest versus fidelity "
        "to the collective's hard-won coherence."
    ),
]


def _frame_question(question: str, author: str = "anonymous") -> str:
    """Convert a human question into an I↔WE tension for Parliament."""
    template = random.choice(TENSION_FRAMES)
    return template.format(question=question[:500], author=author)


# ---------------------------------------------------------------------------
# S3 helpers
# ---------------------------------------------------------------------------

_boto3 = None

def _get_s3():
    global _boto3
    if _boto3 is None:
        try:
            import boto3
            _boto3 = boto3
        except ImportError:
            return None
    try:
        return _boto3.client("s3")
    except Exception:
        return None


def _read_jsonl_from_s3(bucket: str, key: str) -> List[Dict]:
    """Read a JSONL file from S3. Returns empty list on failure."""
    s3 = _get_s3()
    if not s3:
        return []
    try:
        resp = s3.get_object(Bucket=bucket, Key=key)
        lines = resp["Body"].read().decode("utf-8").strip().split("\n")
        return [json.loads(line) for line in lines if line.strip()]
    except Exception as e:
        if "NoSuchKey" in str(e):
            return []
        logger.warning("S3 read failed (%s/%s): %s", bucket, key, e)
        return []


def _append_jsonl_to_s3(bucket: str, key: str, entry: Dict):
    """Append a single JSONL entry to an S3 file (read-append-write)."""
    s3 = _get_s3()
    if not s3:
        raise RuntimeError("boto3 not available")

    # Read existing
    existing = ""
    try:
        resp = s3.get_object(Bucket=bucket, Key=key)
        existing = resp["Body"].read().decode("utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    except s3.exceptions.NoSuchKey:
        pass
    except Exception as e:
        if "NoSuchKey" not in str(e):
            logger.warning("S3 read for append failed: %s", e)

    # Append and write back
    new_line = json.dumps(entry, ensure_ascii=False) + "\n"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=(existing + new_line).encode("utf-8"),
        ContentType="application/x-jsonlines",
    )


def _read_watermark() -> Dict:
    """Read the watermark (last processed state)."""
    s3 = _get_s3()
    if s3:
        try:
            resp = s3.get_object(Bucket=BUCKET, Key=WATERMARK_KEY)
            return json.loads(resp["Body"].read())
        except Exception:
            pass
    if LOCAL_WATERMARK.exists():
        try:
            return json.loads(LOCAL_WATERMARK.read_text())
        except Exception:
            pass
    return {}


def _write_watermark(watermark: Dict):
    """Write the watermark to S3 and local cache."""
    LOCAL_WATERMARK.write_text(json.dumps(watermark, indent=2))
    s3 = _get_s3()
    if s3:
        try:
            s3.put_object(
                Bucket=BUCKET,
                Key=WATERMARK_KEY,
                Body=json.dumps(watermark, indent=2).encode("utf-8"),
                ContentType="application/json",
            )
        except Exception as e:
            logger.warning("Watermark S3 write failed: %s", e)


# ---------------------------------------------------------------------------
# Public API: post a question
# ---------------------------------------------------------------------------

def post_question(question: str, author: str = "anonymous") -> str:
    """
    Post a human question to the Guest Chamber via S3.

    Returns the question ID (UUID).
    """
    qid = uuid.uuid4().hex[:12]
    entry = {
        "id": qid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "author": author,
        "question": question.strip(),
    }

    _append_jsonl_to_s3(BUCKET, QUESTIONS_KEY, entry)
    logger.info("Guest question posted: id=%s author=%s", qid, author)
    return qid


# ---------------------------------------------------------------------------
# GuestChamberFeed — background poller for BODY integration
# ---------------------------------------------------------------------------

class GuestChamberFeed:
    """
    Polls S3 for new guest questions and pushes framed tensions
    into the Parliament's InputBuffer.

    Same contract as WorldFeed: .start() / .stop() background thread.
    """

    def __init__(self, input_buffer, poll_interval_s: int = POLL_INTERVAL_S):
        self.buffer = input_buffer
        self.interval = poll_interval_s
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._stats = {
            "questions_processed": 0,
            "last_poll_at": None,
            "last_question_id": None,
        }

    def poll_once(self) -> int:
        """
        Check S3 for new questions, frame them, push to InputBuffer.
        Returns the number of questions pushed.
        """
        from elpidaapp.parliament_cycle_engine import InputEvent

        watermark = _read_watermark()
        last_id = watermark.get("last_processed_id", "")
        last_ts = watermark.get("last_processed_timestamp", "")

        all_questions = _read_jsonl_from_s3(BUCKET, QUESTIONS_KEY)
        if not all_questions:
            return 0

        # Filter to unprocessed
        if last_ts:
            new_questions = [
                q for q in all_questions
                if q.get("timestamp", "") > last_ts
            ]
        elif last_id:
            # Find position of last processed, take everything after
            ids = [q.get("id", "") for q in all_questions]
            try:
                idx = ids.index(last_id)
                new_questions = all_questions[idx + 1:]
            except ValueError:
                new_questions = all_questions
        else:
            new_questions = all_questions

        if not new_questions:
            return 0

        # Process up to MAX_QUESTIONS_PER_POLL
        batch = new_questions[:MAX_QUESTIONS_PER_POLL]
        pushed = 0

        for q in batch:
            question_text = q.get("question", "")
            author = q.get("author", "anonymous")
            qid = q.get("id", "?")

            if not question_text:
                continue

            # Frame as I↔WE tension
            tension = _frame_question(question_text, author)

            event = InputEvent(
                system="guest",
                content=tension,
                timestamp=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "source": "guest_chamber",
                    "question_id": qid,
                    "author": author,
                    "original_question": question_text,
                },
            )
            self.buffer.push(event)
            pushed += 1
            logger.info(
                "Guest question pushed to InputBuffer: id=%s author=%s q='%s'",
                qid, author, question_text[:80],
            )

        # Advance watermark
        last_processed = batch[-1]
        _write_watermark({
            "last_processed_id": last_processed.get("id", ""),
            "last_processed_timestamp": last_processed.get("timestamp", ""),
            "last_processed_count": len(all_questions),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

        self._stats["questions_processed"] += pushed
        self._stats["last_poll_at"] = datetime.now(timezone.utc).isoformat()
        self._stats["last_question_id"] = last_processed.get("id", "")

        return pushed

    def _loop(self):
        """Background: poll → sleep → poll → ..."""
        logger.info("GuestChamberFeed started (interval=%ds)", self.interval)
        self.poll_once()
        while not self._stop.wait(self.interval):
            self.poll_once()
        logger.info("GuestChamberFeed stopped.")

    def start(self):
        """Start background polling thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="GuestChamber",
        )
        self._thread.start()

    def stop(self):
        """Stop background polling thread."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def status(self) -> Dict[str, Any]:
        """Current feed statistics."""
        stats = dict(self._stats)
        stats["running"] = self._thread is not None and self._thread.is_alive()
        return stats
