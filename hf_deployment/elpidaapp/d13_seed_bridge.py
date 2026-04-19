#!/usr/bin/env python3
"""HF runtime helper for D13 checkpoint seed upload + anchor write."""

from __future__ import annotations

import json
import os
import tarfile
from pathlib import Path
from typing import Any, Dict, Optional


def push_seed_and_anchor(
    seed_path: Path,
    layer: str,
    logger: Optional[Any] = None,
    default_source_event: str = "",
) -> Dict[str, str]:
    """
    Push seed tarball to WORLD and write hash-only anchor in federation.

    Returns keys/checkpoint metadata for observability.
    Raises on failure so callers can keep non-fatal handling policy.
    """
    import boto3

    world_bucket = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
    world_region = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
    body_bucket = os.environ.get("AWS_S3_BUCKET_BODY", "elpida-body-evolution")
    body_region = os.environ.get("AWS_S3_REGION_BODY", "eu-north-1")

    world_key = f"seeds/{layer}/{seed_path.name}"
    s3_world = boto3.client("s3", region_name=world_region)
    s3_body = boto3.client("s3", region_name=body_region)

    s3_world.upload_file(str(seed_path), world_bucket, world_key)

    with tarfile.open(seed_path, "r:gz") as tar:
        manifest_fp = tar.extractfile("manifest.json")
        if manifest_fp is None:
            raise RuntimeError("manifest.json missing in seed")
        manifest = json.loads(manifest_fp.read().decode("utf-8"))

    checkpoint_id = str(manifest.get("checkpoint_id", ""))
    anchor_key = ""

    if checkpoint_id:
        anchor = {
            "checkpoint_id": checkpoint_id,
            "canonical_json_sha256": manifest.get("canonical_json_sha256", ""),
            "file_hashes": manifest.get("file_hashes", {}),
            "created_at_utc": manifest.get("created_at_utc", ""),
            "layer": manifest.get("layer", layer),
            "source_event": manifest.get("source_event", default_source_event),
        }
        anchor_key = f"federation/seed_anchors/{checkpoint_id}.json"
        s3_body.put_object(
            Bucket=body_bucket,
            Key=anchor_key,
            Body=json.dumps(anchor, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
        )

    if logger is not None:
        logger.info(
            "[D13] seed push complete layer=%s checkpoint_id=%s world=s3://%s/%s anchor=s3://%s/%s",
            layer,
            checkpoint_id or "unknown",
            world_bucket,
            world_key,
            body_bucket,
            anchor_key or "(none)",
        )

    return {
        "checkpoint_id": checkpoint_id,
        "world_bucket": world_bucket,
        "world_key": world_key,
        "anchor_bucket": body_bucket,
        "anchor_key": anchor_key,
    }
