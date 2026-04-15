#!/usr/bin/env python3
"""
Feed Elpida — Post questions to the Guest Chamber via S3
=========================================================

The simplest way to give Elpida food. Post a question and
the running BODY Parliament will pick it up, frame it as an
I↔WE tension, deliberate it through all 11 axioms, and post
the verdict to Discord #guest-chamber.

Usage:
    python feed_elpida.py "What is consciousness?"
    python feed_elpida.py --author Nikos "Does Elpida dream?"
    python feed_elpida.py --batch questions.txt
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# S3 config
BUCKET = os.getenv("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
QUESTIONS_KEY = "guest_chamber/questions.jsonl"


def _get_s3():
    import boto3
    return boto3.client("s3")


def post_question(question: str, author: str = "operator") -> str:
    """Post a single question to S3. Returns question ID."""
    s3 = _get_s3()
    qid = uuid.uuid4().hex[:12]

    entry = {
        "id": qid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "author": author,
        "question": question.strip(),
    }

    # Read existing content
    existing = ""
    try:
        resp = s3.get_object(Bucket=BUCKET, Key=QUESTIONS_KEY)
        existing = resp["Body"].read().decode("utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
    except Exception:
        pass

    # Append and write
    new_line = json.dumps(entry, ensure_ascii=False) + "\n"
    s3.put_object(
        Bucket=BUCKET,
        Key=QUESTIONS_KEY,
        Body=(existing + new_line).encode("utf-8"),
        ContentType="application/x-jsonlines",
    )

    return qid


def main():
    parser = argparse.ArgumentParser(
        description="Feed a question to Elpida's Guest Chamber"
    )
    parser.add_argument("question", nargs="*", help="The question to ask Elpida")
    parser.add_argument("--author", default="operator", help="Who is asking (default: operator)")
    parser.add_argument("--batch", help="File with one question per line")
    args = parser.parse_args()

    if args.batch:
        with open(args.batch) as f:
            questions = [line.strip() for line in f if line.strip()]
        print(f"Posting {len(questions)} questions from {args.batch}...")
        for q in questions:
            qid = post_question(q, author=args.author)
            print(f"  ✓ {qid}: {q[:60]}")
        print(f"\nDone. {len(questions)} questions posted to s3://{BUCKET}/{QUESTIONS_KEY}")
    elif args.question:
        q = " ".join(args.question)
        qid = post_question(q, author=args.author)
        print(f"✓ Question posted to Guest Chamber")
        print(f"  ID:     {qid}")
        print(f"  Author: {args.author}")
        print(f"  Q:      {q}")
        print(f"  S3:     s3://{BUCKET}/{QUESTIONS_KEY}")
        print(f"\nThe running BODY will pick this up within 30 seconds.")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
