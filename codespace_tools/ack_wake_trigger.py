#!/usr/bin/env python3
"""
Acknowledge wake-boundary triggers with a state-anchored bridge message.

Purpose:
- Turn the operator's wake signal into a deterministic status artifact.
- Read current git + heartbeat state.
- Emit a GREEN/YELLOW/RED token with a reason token.
- Optionally write to a bridge file (overwrite mode) for immediate relay.

Default behavior is dry-run: print the generated message to stdout.
Use --write to overwrite the selected bridge file.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = ROOT / ".claude" / "bridge"

TARGET_MAP = {
	"for_claude": BRIDGE_DIR / "for_claude.md",
	"for_copilot": BRIDGE_DIR / "for_copilot.md",
	"for_computer": BRIDGE_DIR / "for_computer.md",
	"for_gemini": BRIDGE_DIR / "for_gemini.md",
}


def _utc_now() -> datetime:
	return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
	return _utc_now().isoformat().replace("+00:00", "Z")


def _run_cmd(cmd: list[str], timeout: int = 20) -> Tuple[int, str, str]:
	try:
		p = subprocess.run(
			cmd,
			cwd=str(ROOT),
			capture_output=True,
			text=True,
			timeout=timeout,
		)
		return p.returncode, p.stdout.strip(), p.stderr.strip()
	except Exception as e:
		return 1, "", str(e)


def _git_state_anchor() -> Dict[str, str]:
	head_rc, head_out, _ = _run_cmd(["git", "rev-parse", "--short", "HEAD"])
	origin_rc, origin_out, _ = _run_cmd(["git", "rev-parse", "--short", "origin/main"])
	dirty_rc, dirty_out, _ = _run_cmd(["git", "status", "--short"])

	return {
		"head": head_out if head_rc == 0 and head_out else "unknown",
		"origin_main": origin_out if origin_rc == 0 and origin_out else "unknown",
		"checked_at": _utc_now_iso(),
		"dirty": "yes" if dirty_rc == 0 and dirty_out else "no",
	}


def _parse_iso(ts: str) -> Optional[datetime]:
	if not ts:
		return None
	try:
		# Accept both Z and +00:00 styles.
		normalized = ts.replace("Z", "+00:00")
		return datetime.fromisoformat(normalized)
	except Exception:
		return None


def _pull_mind_heartbeat(bucket: str, key: str, region: str) -> Dict[str, Any]:
	try:
		import boto3
	except ImportError as e:
		return {"_error": f"boto3 unavailable: {e}"}

	try:
		s3 = boto3.client("s3", region_name=region)
		resp = s3.get_object(Bucket=bucket, Key=key)
		return json.loads(resp["Body"].read())
	except Exception as e:
		return {"_error": str(e)}


def _classify(
	heartbeat: Dict[str, Any],
	max_epoch_age_minutes: int,
) -> Tuple[str, str, Optional[float]]:
	if heartbeat.get("_error"):
		return "RED", "heartbeat_unavailable", None

	mind_epoch = str(heartbeat.get("mind_epoch", ""))
	parsed_epoch = _parse_iso(mind_epoch)
	if not parsed_epoch:
		return "YELLOW", "mind_epoch_missing_or_invalid", None

	age_seconds = (_utc_now() - parsed_epoch).total_seconds()
	age_minutes = age_seconds / 60.0

	if age_minutes > max_epoch_age_minutes:
		return "YELLOW", "stale_heartbeat_no_new_cycle", age_minutes

	if bool(heartbeat.get("recursion_warning", False)):
		return "YELLOW", "recursion_warning_active", age_minutes

	return "GREEN", "fresh_heartbeat_and_no_recursion_warning", age_minutes


def _render_message(
	token: str,
	reason_token: str,
	trigger: str,
	reason: str,
	anchor: Dict[str, str],
	heartbeat: Dict[str, Any],
	age_minutes: Optional[float],
) -> str:
	epoch = str(heartbeat.get("mind_epoch", "unknown"))
	cycle = heartbeat.get("mind_cycle", "unknown")
	recursion = heartbeat.get("recursion_warning", "unknown")
	pattern = heartbeat.get("recursion_pattern_type", "unknown")
	rhythm = heartbeat.get("current_rhythm", "unknown")

	age_line = "unknown"
	if age_minutes is not None:
		age_line = f"{age_minutes:.1f}"

	reason_text = reason.strip() if reason.strip() else "none"

	return f"""# From: ack_wake_trigger
# Session: {anchor['checked_at']}
# Trigger: {trigger}
# Tag: [WAKE-ACK] [AUTO-MONITOR]

## State Anchor
HEAD:                   {anchor['head']}
origin/main:            {anchor['origin_main']}
git status checked at:  {anchor['checked_at']}
working tree dirty:     {anchor['dirty']}

## Wake ACK
token: {token}
reason_token: {reason_token}
operator_reason: {reason_text}

## Heartbeat Snapshot
mind_cycle:             {cycle}
mind_epoch:             {epoch}
heartbeat_age_minutes:  {age_line}
current_rhythm:         {rhythm}
recursion_warning:      {recursion}
recursion_pattern_type: {pattern}

## Next Action
- If token is GREEN: proceed with watch boundary handoff.
- If token is YELLOW: keep monitor posture and wait for next mind_epoch.
- If token is RED: escalate immediately and verify AWS credentials/S3 path.
"""


def parse_args() -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Acknowledge a wake-boundary trigger")
	p.add_argument(
		"--target",
		choices=sorted(TARGET_MAP.keys()),
		default="for_claude",
		help="Bridge file target (overwrite on --write)",
	)
	p.add_argument(
		"--trigger",
		default="manual_wake",
		help="Trigger label for header",
	)
	p.add_argument(
		"--reason",
		default="",
		help="Operator reason/context to include in message",
	)
	p.add_argument(
		"--max-epoch-age-minutes",
		type=int,
		default=300,
		help="Heartbeat staleness threshold in minutes",
	)
	p.add_argument(
		"--bucket",
		default="elpida-body-evolution",
		help="S3 bucket containing federation heartbeat",
	)
	p.add_argument(
		"--key",
		default="federation/mind_heartbeat.json",
		help="S3 key for MIND heartbeat",
	)
	p.add_argument(
		"--region",
		default="eu-north-1",
		help="AWS region for heartbeat bucket",
	)
	p.add_argument(
		"--write",
		action="store_true",
		help="Overwrite target bridge file instead of printing",
	)
	return p.parse_args()


def main() -> int:
	args = parse_args()

	anchor = _git_state_anchor()
	heartbeat = _pull_mind_heartbeat(args.bucket, args.key, args.region)
	token, reason_token, age_minutes = _classify(heartbeat, args.max_epoch_age_minutes)

	message = _render_message(
		token=token,
		reason_token=reason_token,
		trigger=args.trigger,
		reason=args.reason,
		anchor=anchor,
		heartbeat=heartbeat,
		age_minutes=age_minutes,
	)

	if args.write:
		target = TARGET_MAP[args.target]
		target.write_text(message, encoding="utf-8")
		print(f"Wrote wake ACK to {target}")
		print(f"token={token} reason_token={reason_token}")
		return 0

	print(message)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

