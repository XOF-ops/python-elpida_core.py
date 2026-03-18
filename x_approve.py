#!/usr/bin/env python3
"""
x_approve.py — Review and approve Elpida X (Twitter) candidate posts
=====================================================================

Lists pending tweet candidates from S3, shows the full text,
and lets you approve or reject them interactively.

Usage:
  python x_approve.py              # Interactive review mode
  python x_approve.py --list       # Just list pending candidates
  python x_approve.py --approve ID # Approve a specific candidate
  python x_approve.py --status     # Show X Bridge status
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hf_deployment" / "elpidaapp"))

# ── Auto-load .env ──────────────────────────────────────────────────────────
_env_file = ROOT / ".env"
if _env_file.exists():
    with open(_env_file) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and "=" in _line and not _line.startswith("#"):
                _k, _, _v = _line.partition("=")
                os.environ.setdefault(_k.strip(), _v.strip())

# ── S3 keys ─────────────────────────────────────────────────────────────────
BUCKET = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
REGION = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
CANDIDATE_PREFIX = "x/candidates/"
POSTED_PREFIX = "x/posted/"


def _s3():
    import boto3
    return boto3.client("s3", region_name=REGION)


def list_pending():
    """Return list of (candidate_id, candidate_data) tuples."""
    client = _s3()
    resp = client.list_objects_v2(Bucket=BUCKET, Prefix=CANDIDATE_PREFIX)
    candidates = []
    for obj in resp.get("Contents", []):
        key = obj["Key"]
        if not key.endswith(".json"):
            continue
        cid = key.replace(CANDIDATE_PREFIX, "").replace(".json", "")
        try:
            data = client.get_object(Bucket=BUCKET, Key=key)
            candidate = json.loads(data["Body"].read().decode())
            candidates.append((cid, candidate))
        except Exception as e:
            print(f"  ⚠ Error reading {key}: {e}")
    return candidates


def list_posted():
    """Return count of posted tweets."""
    client = _s3()
    resp = client.list_objects_v2(Bucket=BUCKET, Prefix=POSTED_PREFIX)
    return resp.get("KeyCount", 0)


def display_candidate(idx, total, cid, candidate):
    """Pretty-print a single candidate."""
    source = candidate.get("source", "?")
    axiom = candidate.get("axiom", "?")
    axiom_name = candidate.get("axiom_name", "")
    harvested = candidate.get("harvested_at", "?")[:19]
    consonance = candidate.get("consonance", "")
    body_approval = candidate.get("body_approval", "")
    tweet = candidate.get("tweet_text", "")

    print(f"\n{'─'*60}")
    print(f"  [{idx}/{total}]  ID: {cid}")
    print(f"  Source: {source}  |  Axiom: {axiom} {axiom_name}")
    print(f"  Harvested: {harvested}")
    if consonance:
        print(f"  Consonance: {consonance:.2f}", end="")
    if body_approval:
        print(f"  |  Body Approval: {body_approval}", end="")
    print()
    print(f"{'─'*60}")
    print(f"\n{tweet}\n")
    print(f"  ({len(tweet)}/280 chars)")
    print(f"{'─'*60}")


def approve_candidate(cid):
    """Approve and post a candidate via XBridge."""
    from x_bridge import XBridge
    bridge = XBridge()
    results = bridge.post_approved([cid])
    if results:
        r = results[0]
        print(f"\n  ✅ Posted! Tweet ID: {r.get('tweet_id', '?')}")
        print(f"     {r.get('posted_at', '')[:19]}")
    else:
        print(f"\n  ❌ Post failed for {cid}")
    return results


def reject_candidate(cid):
    """Move candidate to a rejected prefix (soft delete)."""
    client = _s3()
    src_key = f"{CANDIDATE_PREFIX}{cid}.json"
    try:
        # Read it first
        data = client.get_object(Bucket=BUCKET, Key=src_key)
        body = data["Body"].read()

        # Write to rejected/
        client.put_object(
            Bucket=BUCKET,
            Key=f"x/rejected/{cid}.json",
            Body=body,
            ContentType="application/json",
        )
        # Delete from candidates/
        client.delete_object(Bucket=BUCKET, Key=src_key)
        print(f"  🗑  Rejected and archived: {cid}")
    except Exception as e:
        print(f"  ⚠ Reject failed: {e}")


def interactive_review():
    """Interactive review mode — walk through each candidate."""
    candidates = list_pending()
    posted_count = list_posted()

    if not candidates:
        print("\n  No pending candidates. System is clean.")
        print(f"  Previously posted: {posted_count}")
        return

    print(f"\n  📋 {len(candidates)} pending candidate(s)  |  {posted_count} previously posted\n")

    for idx, (cid, candidate) in enumerate(candidates, 1):
        display_candidate(idx, len(candidates), cid, candidate)

        while True:
            choice = input("  [A]pprove  [R]eject  [S]kip  [Q]uit → ").strip().lower()
            if choice in ("a", "approve"):
                approve_candidate(cid)
                break
            elif choice in ("r", "reject"):
                reject_candidate(cid)
                break
            elif choice in ("s", "skip"):
                print("  ⏭  Skipped")
                break
            elif choice in ("q", "quit"):
                print("  Exiting.")
                return
            else:
                print("  Pick: A, R, S, or Q")


def show_status():
    """Show X Bridge status."""
    candidates = list_pending()
    posted_count = list_posted()
    tweepy_ready = bool(
        os.environ.get("TWITTER_API_KEY")
        and os.environ.get("TWITTER_API_SECRET")
        and os.environ.get("TWITTER_ACCESS_TOKEN")
        and os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")
    )

    print(f"\n  X Bridge — Phase 1 Status")
    print(f"  {'─'*40}")
    print(f"  Tweepy configured: {'✅' if tweepy_ready else '❌'}")
    print(f"  Pending candidates: {len(candidates)}")
    print(f"  Posted tweets: {posted_count}")
    print(f"  S3 bucket: {BUCKET}")
    print(f"  Candidate prefix: {CANDIDATE_PREFIX}")
    print()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Review and approve Elpida X posts")
    parser.add_argument("--list", action="store_true", help="List pending candidates")
    parser.add_argument("--approve", type=str, help="Approve a specific candidate ID")
    parser.add_argument("--status", action="store_true", help="Show X Bridge status")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.list:
        candidates = list_pending()
        if not candidates:
            print("\n  No pending candidates.")
            return
        print(f"\n  {len(candidates)} pending candidate(s):\n")
        for idx, (cid, c) in enumerate(candidates, 1):
            display_candidate(idx, len(candidates), cid, c)
    elif args.approve:
        approve_candidate(args.approve)
    else:
        interactive_review()


if __name__ == "__main__":
    main()
