#!/usr/bin/env python3
"""
Calibrated D16 probe for Option 1 verification.

Modes:
  level1: Schema-only preview (no S3 writes)
  level2: Forced emit through ParliamentCycleEngine._emit_d16_execution
          and S3 verification (requires --execute)

Examples:
  /workspaces/python-elpida_core.py/.venv/bin/python codespace_tools/d16_level2_probe.py --mode level1

  /workspaces/python-elpida_core.py/.venv/bin/python codespace_tools/d16_level2_probe.py \
    --mode level2 --execute --source test-level2
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
HF_ROOT = REPO_ROOT / "hf_deployment"
if str(HF_ROOT) not in sys.path:
    sys.path.insert(0, str(HF_ROOT))

from elpidaapp.parliament_cycle_engine import ParliamentCycleEngine  # type: ignore
from s3_bridge import (  # type: ignore
    BUCKET_BODY,
    FED_BODY_DECISIONS_KEY,
    FED_D16_EXECUTIONS_KEY,
    REGION_BODY,
    S3Bridge,
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_action(source: str, action: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    marker = " [TEST ONLY - DO NOT ACT]" if source.lower().startswith("test") else ""
    return f"[{source}]{marker} {action} :: {stamp}"


def _build_result(approval: float) -> Dict[str, Any]:
    return {
        "governance": "PROCEED",
        "parliament": {
            "veto_exercised": False,
            "approval_rate": approval,
        },
    }


def _build_watch(name: str) -> Dict[str, Any]:
    return {
        "name": name,
        "symbol": "P",
    }


def _build_meta(source: str) -> Dict[str, Any]:
    return {
        "source": source,
        "systems": [source],
        "rhythm": "ACTION",
        "event_provenance": [{"system": source, "source": source}],
    }


def _preview_schema(cycle: int, action: str, dominant_axiom: str, watch_name: str) -> Dict[str, Any]:
    content_hash = hashlib.sha256(action.encode("utf-8", errors="replace")).hexdigest()[:16]
    return {
        "body_cycle": cycle,
        "proposal": action[:500],
        "action_type": "constitutional_agency",
        "scope": "global",
        "consent_level": "witnessed",
        "witness_domain": 3,
        "witness_axiom": "A3",
        "content_hash": content_hash,
        "governing_conditions": [
            f"Dominant Axiom: {dominant_axiom}",
            f"Watch: {watch_name}",
        ],
        "stage": 2,
        "status": "attested",
        "timestamp": _iso_now(),
    }


def _read_jsonl_all(s3, bucket: str, key: str) -> List[Dict[str, Any]]:
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
    except Exception:
        return []
    raw = obj["Body"].read().decode("utf-8", errors="replace")
    rows: List[Dict[str, Any]] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _tail_jsonl(s3, bucket: str, key: str, tail_bytes: int) -> List[Dict[str, Any]]:
    try:
        head = s3.head_object(Bucket=bucket, Key=key)
    except Exception:
        return []

    size = int(head.get("ContentLength", 0))
    start = max(size - tail_bytes, 0)
    kwargs = {"Bucket": bucket, "Key": key}
    if start > 0:
        kwargs["Range"] = f"bytes={start}-{size - 1}"

    obj = s3.get_object(**kwargs)
    raw = obj["Body"].read().decode("utf-8", errors="replace")
    lines = raw.splitlines()

    # Range reads can begin mid-line, so drop the first fragment.
    if start > 0 and lines:
        lines = lines[1:]

    rows: List[Dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def run_level1(args: argparse.Namespace) -> int:
    action = _build_action(args.source, args.action)
    preview = _preview_schema(
        cycle=args.cycle,
        action=action,
        dominant_axiom=args.dominant_axiom,
        watch_name=args.watch,
    )

    required = {
        "body_cycle",
        "proposal",
        "action_type",
        "scope",
        "consent_level",
        "witness_domain",
        "witness_axiom",
        "content_hash",
        "governing_conditions",
        "stage",
        "status",
        "timestamp",
    }
    ok = required.issubset(set(preview.keys()))
    out = {
        "mode": "level1",
        "schema_valid": ok,
        "entry": preview,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if ok else 3


def run_level2(args: argparse.Namespace) -> int:
    if not args.execute:
        print(
            "Refusing Level 2 without --execute. This mode writes to production federation S3.",
            file=sys.stderr,
        )
        return 2

    engine = ParliamentCycleEngine()
    engine.cycle_count = args.cycle

    action = _build_action(args.source, args.action)
    content_hash = hashlib.sha256(action.encode("utf-8", errors="replace")).hexdigest()[:16]
    result = _build_result(args.approval)
    watch = _build_watch(args.watch)
    meta = _build_meta(args.source)

    bridge = S3Bridge()
    s3 = bridge._get_s3(REGION_BODY)
    if s3 is None:
        print("No S3 client available. Check credentials/environment.", file=sys.stderr)
        return 2

    before_d16_rows = _read_jsonl_all(s3, BUCKET_BODY, FED_D16_EXECUTIONS_KEY)
    before_d16_count = len(before_d16_rows)

    engine._emit_d16_execution(action, result, args.dominant_axiom, watch, meta)

    after_d16_rows = _read_jsonl_all(s3, BUCKET_BODY, FED_D16_EXECUTIONS_KEY)
    after_d16_count = len(after_d16_rows)

    d16_tail = _tail_jsonl(s3, BUCKET_BODY, FED_D16_EXECUTIONS_KEY, tail_bytes=256 * 1024)
    body_tail = _tail_jsonl(s3, BUCKET_BODY, FED_BODY_DECISIONS_KEY, tail_bytes=2 * 1024 * 1024)

    found_d16 = None
    for row in reversed(d16_tail):
        if row.get("content_hash") == content_hash:
            found_d16 = row
            break

    found_mirror = None
    for row in reversed(body_tail):
        if (
            row.get("pattern_hash") == content_hash
            and (row.get("type") == "D16_EXECUTION" or row.get("verdict") == "D16_EXECUTION")
            and row.get("input_source") == args.source
        ):
            found_mirror = row
            break

    success = (
        after_d16_count >= before_d16_count + 1
        and found_d16 is not None
        and found_mirror is not None
    )

    out = {
        "mode": "level2",
        "success": success,
        "source": args.source,
        "content_hash": content_hash,
        "d16_count_before": before_d16_count,
        "d16_count_after": after_d16_count,
        "mirror_found": found_mirror is not None,
        "d16_entry_found": found_d16 is not None,
        "bridge_note": (
            f"d16_executions_count={after_d16_count} at {_iso_now()} (source={args.source}, hash={content_hash})"
        ),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if success else 3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Level-1/Level-2 D16 probe")
    parser.add_argument("--mode", choices=["level1", "level2"], default="level1")
    parser.add_argument("--execute", action="store_true", help="Required for level2 write mode")
    parser.add_argument("--source", default="test-level2", help="Tag written into mirrored body_decisions input_source")
    parser.add_argument("--action", default="D16 emit-chain verification probe", help="Action/proposal text seed")
    parser.add_argument("--cycle", type=int, default=999, help="Synthetic cycle id for the probe")
    parser.add_argument("--watch", default="Parliament", help="Watch name carried in payload")
    parser.add_argument("--dominant-axiom", default="A16", help="Dominant axiom tag for governing_conditions")
    parser.add_argument("--approval", type=float, default=0.91, help="Synthetic parliament approval for mirror payload")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.mode == "level1":
        return run_level1(args)
    return run_level2(args)


if __name__ == "__main__":
    raise SystemExit(main())
