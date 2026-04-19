#!/usr/bin/env python3
"""
Post-MIND-run verifier for the Gap 3 handshake + D13 MIND seed artifacts.

Reads the three new outputs a completed MIND run should have produced and
prints a single GO/NO-GO readout. Intended to be run after cloud_runner.py
completes on ECS (or any local/test invocation).

Checks:
  1. feedback_to_native.jsonl (S3 or local) has a recent cross_session_seed
     entry with source in {d0_self, d9_self}, a deterministic full_result_id,
     and recursion_warning_at_write set. Reports which voice carried the
     handshake (D0 normal, D9 counter-voice when session ended fixated).

  2. seeds/mind/ in WORLD bucket has a recent tarball from this run.

  3. federation/seed_anchors/ in BODY bucket has the corresponding anchor
     JSON, and its canonical_json_sha256 matches the seed's manifest.

Exit code is 0 on full GO, non-zero on any NO-GO so this can be wired into
workflows as a gate. Intentionally read-only — makes no S3 writes.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import boto3
except ImportError:
    boto3 = None


WORLD_BUCKET = os.environ.get("AWS_S3_BUCKET_WORLD", "elpida-external-interfaces")
BODY_BUCKET = os.environ.get("AWS_S3_BUCKET_BODY", "elpida-body-evolution")
WORLD_REGION = os.environ.get("AWS_S3_REGION_WORLD", "eu-north-1")
BODY_REGION = os.environ.get("AWS_S3_REGION_BODY", "eu-north-1")


def _fmt(ok: bool) -> str:
    return "GO " if ok else "NO-GO"


def _latest_self_handshake(max_scan: int = 200) -> Optional[dict[str, Any]]:
    """Find the latest entry with source in {d0_self, d9_self}, or the
    legacy MIND_D0_FINAL_INSIGHT for backward compatibility."""
    sources_ok = {"d0_self", "d9_self", "MIND_D0_FINAL_INSIGHT"}
    content = b""

    if boto3 is not None:
        try:
            s3 = boto3.client("s3", region_name=BODY_REGION)
            obj = s3.get_object(Bucket=BODY_BUCKET, Key="feedback/feedback_to_native.jsonl")
            content = obj["Body"].read()
        except Exception:
            pass

    if not content:
        local = Path("application_feedback_cache.jsonl")
        if local.exists():
            content = local.read_bytes()

    if not content:
        return None

    latest: Optional[dict[str, Any]] = None
    scanned = 0
    for line in reversed(content.splitlines()):
        scanned += 1
        if scanned > max_scan:
            break
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue
        if entry.get("source") in sources_ok:
            latest = entry
            break
    return latest


def _latest_mind_seed() -> Optional[dict[str, Any]]:
    """Return metadata for the most recent object in seeds/mind/ or None."""
    if boto3 is None:
        return None
    s3 = boto3.client("s3", region_name=WORLD_REGION)
    try:
        resp = s3.list_objects_v2(Bucket=WORLD_BUCKET, Prefix="seeds/mind/")
    except Exception as e:
        return {"error": f"list seeds/mind/ failed: {e}"}
    contents = resp.get("Contents") or []
    if not contents:
        return None
    latest = max(contents, key=lambda o: o["LastModified"])
    return {
        "key": latest["Key"],
        "size": latest["Size"],
        "last_modified": latest["LastModified"].isoformat(),
    }


def _read_seed_manifest(key: str) -> Optional[dict[str, Any]]:
    """Download tarball and extract its manifest.json in-memory."""
    if boto3 is None:
        return None
    s3 = boto3.client("s3", region_name=WORLD_REGION)
    try:
        obj = s3.get_object(Bucket=WORLD_BUCKET, Key=key)
        buf = io.BytesIO(obj["Body"].read())
        with tarfile.open(fileobj=buf, mode="r:gz") as tar:
            mf = tar.extractfile("manifest.json")
            if mf is None:
                return None
            return json.loads(mf.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"read manifest failed: {e}"}


def _read_anchor(checkpoint_id: str) -> Optional[dict[str, Any]]:
    if boto3 is None or not checkpoint_id:
        return None
    s3 = boto3.client("s3", region_name=BODY_REGION)
    try:
        obj = s3.get_object(
            Bucket=BODY_BUCKET,
            Key=f"federation/seed_anchors/{checkpoint_id}.json",
        )
        return json.loads(obj["Body"].read())
    except Exception as e:
        return {"error": f"read anchor failed: {e}"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--max-age-hours",
        type=float,
        default=24.0,
        help="Warn if artifacts are older than this (default 24h)",
    )
    args = ap.parse_args()

    print("=" * 70)
    print(f"MIND run artifact verifier — {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    all_ok = True
    now = datetime.now(timezone.utc)

    # 1. Handshake entry
    print()
    print("[1/3] Gap 3 handshake entry (feedback_to_native.jsonl)")
    handshake = _latest_self_handshake()
    if not handshake:
        print(f"      {_fmt(False)}: no self-handshake entry found")
        all_ok = False
    else:
        src = handshake.get("source", "?")
        typ = handshake.get("type", "?")
        frid = handshake.get("full_result_id", "?")
        ts = handshake.get("timestamp", "?")
        cycle = handshake.get("cycle", "?")
        rec_flag = handshake.get("recursion_warning_at_write")
        try:
            age = now - datetime.fromisoformat(ts.replace("Z", "+00:00"))
            age_h = age.total_seconds() / 3600
        except Exception:
            age_h = None

        schema_ok = src in ("d0_self", "d9_self") and typ == "cross_session_seed"
        id_ok = isinstance(frid, str) and (
            frid.startswith("mind_d0_handshake_") or frid.startswith("mind_d9_handshake_")
        )
        age_ok = age_h is None or age_h <= args.max_age_hours

        entry_ok = schema_ok and id_ok and age_ok
        all_ok = all_ok and entry_ok

        voice = "D9 (counter-voice, prior session fixated)" if src == "d9_self" else "D0 (clean handshake)" if src == "d0_self" else f"legacy ({src})"
        print(f"      {_fmt(entry_ok)}: voice={voice}")
        print(f"             source={src} type={typ}")
        print(f"             id={frid}")
        print(f"             cycle={cycle} recursion_warning_at_write={rec_flag}")
        if age_h is not None:
            print(f"             age={age_h:.2f}h (threshold {args.max_age_hours}h)")
        if not schema_ok:
            print("             ⚠ schema mismatch — expected source∈{d0_self,d9_self}, type=cross_session_seed")
        if not id_ok:
            print("             ⚠ id not in mind_d0/d9_handshake_... form (dedup guard may be broken)")
        if not age_ok:
            print("             ⚠ handshake is stale relative to --max-age-hours")

    # 2. MIND seed tarball
    print()
    print("[2/3] MIND seed tarball (s3://elpida-external-interfaces/seeds/mind/)")
    seed_meta = _latest_mind_seed()
    seed_manifest: Optional[dict[str, Any]] = None
    if not seed_meta:
        print(f"      {_fmt(False)}: no seeds found")
        all_ok = False
    elif isinstance(seed_meta, dict) and "error" in seed_meta:
        print(f"      {_fmt(False)}: {seed_meta['error']}")
        all_ok = False
    else:
        try:
            lm = datetime.fromisoformat(seed_meta["last_modified"].replace("Z", "+00:00"))
            age_h = (now - lm).total_seconds() / 3600
        except Exception:
            age_h = None
        age_ok = age_h is None or age_h <= args.max_age_hours
        all_ok = all_ok and age_ok
        print(f"      {_fmt(age_ok)}: {seed_meta['key']}")
        print(f"             size={seed_meta['size']}B last_modified={seed_meta['last_modified']}")
        if age_h is not None:
            print(f"             age={age_h:.2f}h (threshold {args.max_age_hours}h)")
        seed_manifest = _read_seed_manifest(seed_meta["key"])

    # 3. Anchor + hash consistency
    print()
    print("[3/3] Federation anchor (s3://elpida-body-evolution/federation/seed_anchors/)")
    if not seed_manifest or "error" in seed_manifest:
        print(f"      {_fmt(False)}: no seed manifest to cross-check")
        all_ok = False
    else:
        checkpoint_id = seed_manifest.get("checkpoint_id", "")
        seed_hash = seed_manifest.get("canonical_json_sha256", "")
        anchor = _read_anchor(checkpoint_id)
        if not anchor or "error" in (anchor or {}):
            err = (anchor or {}).get("error", "missing")
            print(f"      {_fmt(False)}: anchor for {checkpoint_id} — {err}")
            all_ok = False
        else:
            anchor_hash = anchor.get("canonical_json_sha256", "")
            hash_ok = bool(seed_hash) and seed_hash == anchor_hash
            all_ok = all_ok and hash_ok
            print(f"      {_fmt(hash_ok)}: checkpoint_id={checkpoint_id}")
            print(f"             seed   sha256={seed_hash}")
            print(f"             anchor sha256={anchor_hash}")
            if not hash_ok:
                print("             ⚠ hash mismatch — anchor does not attest this seed")

    # Summary
    print()
    print("=" * 70)
    print(f"OVERALL: {_fmt(all_ok)}")
    print("=" * 70)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
