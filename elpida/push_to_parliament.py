"""
push_to_parliament.py — Vercel Chat → Parliament Human Voice Bridge

Reads curated Vercel conversation entries (from public_memory.jsonl and
curated_log.jsonl) and uploads them to the BODY S3 bucket so the
HumanVoiceAgent can propose them for Parliament ratification.

Usage:
  python push_to_parliament.py                  # dry run (preview only)
  python push_to_parliament.py --push           # actually upload to S3
  python push_to_parliament.py --push --min=9   # only score >= 9

Requires: boto3, AWS credentials with BODY bucket write access.
  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION (us-east-1)
  or: AWS_S3_BUCKET_BODY env var to override bucket name
"""

import json
import os
import hashlib
import sys
from pathlib import Path
from datetime import datetime

HERE = Path(__file__).parent

BUCKET_BODY       = os.environ.get("AWS_S3_BUCKET_BODY", "elpida-body-evolution")
REGION_BODY       = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
PENDING_S3_KEY    = "federation/pending_human_votes.jsonl"

PUBLIC_MEMORY     = HERE / "public_memory.jsonl"
CURATED_LOG       = HERE / "curated_log.jsonl"
EVOLUTION_LOG     = HERE / "evolution_log.jsonl"


# ─────────────────────────────────────────────────────────────────────
# Load local curated data
# ─────────────────────────────────────────────────────────────────────

def _entry_hash(entry: dict) -> str:
    key = (entry.get("timestamp", "") + entry.get("user_message_preview", "")
           + entry.get("content", ""))
    return hashlib.md5(key.encode()).hexdigest()[:12]


def load_candidates(min_score: int = 8) -> list:
    """
    Collect all candidate entries that are worth proposing to Parliament.

    Three sources (merged + deduplicated):
    1. curated_log.jsonl   — scored conversation references (score + preview)
    2. public_memory.jsonl — already-curated semantic entries (AXIOM_TENSION,
                             CONVERSATION, GENESIS types)
    3. evolution_log.jsonl — raw exchanges (only if curate_log is thin)
    """
    seen = set()
    candidates = []

    # Source 1: curated_log (has score + preview)
    if CURATED_LOG.exists():
        for line in CURATED_LOG.read_text().splitlines():
            if not line.strip():
                continue
            try:
                e = json.loads(line)
                if e.get("score", 0) >= min_score:
                    e.setdefault("type", "CONVERSATION")
                    h = _entry_hash(e)
                    if h not in seen:
                        seen.add(h)
                        e["_hash"] = h
                        candidates.append(e)
            except Exception:
                pass

    # Source 2: public_memory (high-value semantic entries)
    if PUBLIC_MEMORY.exists():
        for line in PUBLIC_MEMORY.read_text().splitlines():
            if not line.strip():
                continue
            try:
                e = json.loads(line)
                etype = e.get("type", "")
                # AXIOM_TENSION entries carry resolved dilemmas — high value
                # CONVERSATION entries carry real human insight
                if etype in ("AXIOM_TENSION", "CONVERSATION"):
                    # Synthesise a preview for display
                    if "user_message_preview" not in e:
                        e["user_message_preview"] = (
                            e.get("dilemma", e.get("topic", e.get("content", "")))[:120]
                        )
                    if "score" not in e:
                        e["score"] = 10  # curated = already trusted
                    h = _entry_hash(e)
                    if h not in seen:
                        seen.add(h)
                        e["_hash"] = h
                        candidates.append(e)
            except Exception:
                pass

    return candidates


# ─────────────────────────────────────────────────────────────────────
# S3 operations
# ─────────────────────────────────────────────────────────────────────

def _get_s3():
    try:
        import boto3
        return boto3.client("s3", region_name=REGION_BODY)
    except ImportError:
        print("ERROR: boto3 not installed. Run: pip install boto3")
        sys.exit(1)


def fetch_existing_hashes(s3) -> set:
    """Return hashes already queued in S3 to avoid duplicates."""
    try:
        resp = s3.get_object(Bucket=BUCKET_BODY, Key=PENDING_S3_KEY)
        lines = resp["Body"].read().decode().splitlines()
        return {json.loads(l).get("_hash", "") for l in lines if l.strip()}
    except s3.exceptions.NoSuchKey:
        return set()
    except Exception as e:
        print(f"  Warning: could not read existing queue: {e}")
        return set()


def append_to_s3_queue(s3, new_entries: list, existing_hashes: set) -> int:
    """Append new entries to the S3 pending queue. Returns count added."""
    # Read current queue
    existing_lines = []
    try:
        resp = s3.get_object(Bucket=BUCKET_BODY, Key=PENDING_S3_KEY)
        existing_lines = resp["Body"].read().decode().splitlines()
    except Exception:
        pass

    added = 0
    for entry in new_entries:
        if entry.get("_hash") in existing_hashes:
            continue
        entry["_queued_at"] = datetime.utcnow().isoformat() + "Z"
        existing_lines.append(json.dumps(entry))
        added += 1

    payload = "\n".join(l for l in existing_lines if l.strip()) + "\n"
    s3.put_object(
        Bucket=BUCKET_BODY,
        Key=PENDING_S3_KEY,
        Body=payload.encode(),
        ContentType="application/x-ndjson",
    )
    return added


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main():
    do_push = "--push" in sys.argv
    min_score = 8
    for arg in sys.argv:
        if arg.startswith("--min="):
            min_score = int(arg.split("=")[1])

    print("=" * 60)
    print("ELPIDA — PUSH HUMAN VOICES TO PARLIAMENT")
    print("=" * 60)
    print(f"Min curation score: {min_score}")
    print(f"Target S3: s3://{BUCKET_BODY}/{PENDING_S3_KEY}")
    print(f"Mode: {'LIVE PUSH' if do_push else 'DRY RUN'}")
    print()

    candidates = load_candidates(min_score)
    print(f"Candidates found: {len(candidates)}")
    for c in candidates:
        preview = c.get("user_message_preview", c.get("content", ""))[:80]
        print(f"  [{c.get('score', '?'):>2}] [{c.get('type', '?'):<15}] {preview}…")

    if not candidates:
        print("\nNo qualifying entries to push.")
        return

    if not do_push:
        print("\nDry run — pass --push to actually upload to S3.")
        return

    print("\nConnecting to S3...")
    s3 = _get_s3()
    existing = fetch_existing_hashes(s3)
    print(f"Already queued: {len(existing)} entry/entries")

    added = append_to_s3_queue(s3, candidates, existing)
    print(f"\n✓ {added} new entry/entries pushed to Parliament vote queue.")
    print("  HumanVoiceAgent will propose them in the next 5-minute poll.")
    print("  Parliament ratification determines if they become constitutional.")


if __name__ == "__main__":
    main()
