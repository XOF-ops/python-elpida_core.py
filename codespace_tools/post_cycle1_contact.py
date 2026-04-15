#!/usr/bin/env python3
"""
Post a cycle-1 external contact message for MIND D0 ingestion.

Writes a JSONL entry to:
  s3://<AWS_S3_BUCKET_BODY>/feedback/feedback_to_native.jsonl

NativeCycleEngine always starts at D0 on cycle 1 and checks this file during
the D0 branch via _pull_application_feedback().
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _s3_client():
    try:
        import boto3
    except ImportError as exc:
        raise RuntimeError("boto3 is required. Install with: pip install boto3") from exc
    region = os.getenv("AWS_S3_REGION_BODY", "eu-north-1")
    return boto3.client("s3", region_name=region)


def _append_jsonl_entry(bucket: str, key: str, entry: dict) -> None:
    s3 = _s3_client()

    existing = ""
    try:
        resp = s3.get_object(Bucket=bucket, Key=key)
        existing = resp["Body"].read().decode("utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    except Exception as exc:
        # First write is expected to miss.
        if "NoSuchKey" not in str(exc):
            raise

    line = json.dumps(entry, ensure_ascii=False) + "\n"
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=(existing + line).encode("utf-8"),
        ContentType="application/x-jsonlines",
    )


def build_entry(message: str, author: str, source: str) -> dict:
    return {
        "id": f"cycle1-{uuid.uuid4().hex[:12]}",
        "type": "APPLICATION_FEEDBACK",
        "timestamp": _now_iso(),
        "problem": "D13 external contact to D0 at cycle 1",
        "synthesis": message.strip(),
        "fault_lines": 0,
        "consensus_points": 1,
        "kaya_moments": 0,
        "author": author,
        "source": source,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Post a cycle-1 D13->D0 external contact message"
    )
    parser.add_argument(
        "message",
        help="The message that D0 should ingest on cycle 1",
    )
    parser.add_argument(
        "--author",
        default="computer-d13",
        help="Author label written into the JSON entry",
    )
    parser.add_argument(
        "--source",
        default="computer_bridge",
        help="Source label written into the JSON entry",
    )
    parser.add_argument(
        "--bucket",
        default=os.getenv("AWS_S3_BUCKET_BODY", "elpida-body-evolution"),
        help="BODY bucket (default: AWS_S3_BUCKET_BODY or elpida-body-evolution)",
    )
    parser.add_argument(
        "--key",
        default="feedback/feedback_to_native.jsonl",
        help="Feedback key consumed by MIND D0",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.message.strip():
        print("Message cannot be empty", file=sys.stderr)
        return 2

    entry = build_entry(args.message, args.author, args.source)
    _append_jsonl_entry(args.bucket, args.key, entry)

    print("Posted cycle-1 external contact entry")
    print(f"  bucket: s3://{args.bucket}")
    print(f"  key:    {args.key}")
    print(f"  id:     {entry['id']}")
    print(f"  ts:     {entry['timestamp']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
