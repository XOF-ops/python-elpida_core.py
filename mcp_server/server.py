from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List

from elpida_sdk import CheckpointAuditor, ElpidaConfig, KernelGuard, S3Client


class ElpidaMCPServer:
    """Minimal stdio JSON-RPC-like server for phase-1 tool exposure.

    Input format (one JSON object per line):
    {"method": "list_tools"}
    {"method": "call_tool", "params": {"name": "list_domains", "arguments": {}}}

    Output format (one JSON object per line):
    {"ok": true, "result": ...}
    {"ok": false, "error": "..."}
    """

    def __init__(self) -> None:
        self.config = ElpidaConfig()
        self.checkpoints = CheckpointAuditor()
        self.s3 = S3Client()
        self.tools = {
            "list_domains": self.list_domains,
            "list_axioms": self.list_axioms,
            "list_rhythms": self.list_rhythms,
            "kernel_check_text": self.kernel_check_text,
            "list_checkpoints": self.list_checkpoints,
            "get_mind_heartbeat": self.get_mind_heartbeat,
            "get_body_heartbeat": self.get_body_heartbeat,
            "get_d15_broadcasts": self.get_d15_broadcasts,
            "get_system_status": self.get_system_status,
            "summarize_system_status": self.summarize_system_status,
            "summarize_system_health_alerts": self.summarize_system_health_alerts,
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "list_domains",
                "description": "Return canonical domain definitions from elpida_domains.json",
            },
            {
                "name": "list_axioms",
                "description": "Return canonical axiom definitions from elpida_domains.json",
            },
            {
                "name": "list_rhythms",
                "description": "Return rhythm configuration from elpida_domains.json",
            },
            {
                "name": "kernel_check_text",
                "description": "Run immutable kernel check against text",
            },
            {
                "name": "list_checkpoints",
                "description": "Return D13 checkpoint rows via scripts/d13_checkpoint_audit.sh",
            },
            {
                "name": "get_mind_heartbeat",
                "description": "Read federation/mind_heartbeat.json from S3",
            },
            {
                "name": "get_body_heartbeat",
                "description": "Read heartbeat/native_engine.json from S3",
            },
            {
                "name": "get_d15_broadcasts",
                "description": "Read recent entries from d15/broadcasts.jsonl in S3",
            },
            {
                "name": "get_system_status",
                "description": "Return combined MIND heartbeat, BODY heartbeat, and recent D15 broadcasts",
            },
            {
                "name": "summarize_system_status",
                "description": "Return compact telemetry summary for dashboards/alerts",
            },
            {
                "name": "summarize_system_health_alerts",
                "description": "Return OK/WARNING/CRITICAL health classification with threshold-based alerts",
            },
        ]

    def list_domains(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        _ = arguments
        return [asdict(d) for d in self.config.list_domains()]

    def list_axioms(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        _ = arguments
        return [asdict(a) for a in self.config.list_axioms()]

    def list_rhythms(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        _ = arguments
        return self.config.list_rhythms()

    def kernel_check_text(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        text = str(arguments.get("text", ""))
        return KernelGuard.check_text(text).to_dict()

    def list_checkpoints(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        layers = arguments.get("layers") or ["mind", "body", "world", "full"]
        latest_n = int(arguments.get("latest_n", 20))
        since_hours = int(arguments.get("since_hours", 24))
        rows = self.checkpoints.list_rows(layers=layers, latest_n=latest_n, since_hours=since_hours)
        return [asdict(r) for r in rows]

    def get_mind_heartbeat(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        bucket = str(arguments.get("bucket", self.s3.buckets.federation))
        key = str(arguments.get("key", "federation/mind_heartbeat.json"))
        return self.s3.read_json(bucket=bucket, key=key)

    def get_body_heartbeat(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        bucket = str(arguments.get("bucket", self.s3.buckets.federation))
        key = str(arguments.get("key", "heartbeat/native_engine.json"))
        return self.s3.read_json(bucket=bucket, key=key)

    def get_d15_broadcasts(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        bucket = str(arguments.get("bucket", self.s3.buckets.world))
        key = str(arguments.get("key", "d15/broadcasts.jsonl"))
        limit = int(arguments.get("limit", 20))
        return self.s3.read_jsonl(bucket=bucket, key=key, limit=limit)

    def get_system_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        d15_limit = int(arguments.get("d15_limit", 5))
        result: Dict[str, Any] = {
            "mind_heartbeat": None,
            "body_heartbeat": None,
            "d15_broadcasts": [],
            "errors": {},
        }

        try:
            result["mind_heartbeat"] = self.get_mind_heartbeat({})
        except Exception as e:
            result["errors"]["mind_heartbeat"] = str(e)

        try:
            result["body_heartbeat"] = self.get_body_heartbeat({})
        except Exception as e:
            result["errors"]["body_heartbeat"] = str(e)

        try:
            result["d15_broadcasts"] = self.get_d15_broadcasts({"limit": d15_limit})
        except Exception as e:
            result["errors"]["d15_broadcasts"] = str(e)

        result["ok"] = len(result["errors"]) == 0
        return result

    def summarize_system_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        d15_limit = int(arguments.get("d15_limit", 3))
        status = self.get_system_status({"d15_limit": d15_limit})

        mind = status.get("mind_heartbeat") or {}
        body = status.get("body_heartbeat") or {}
        d15 = status.get("d15_broadcasts") or []
        errors = status.get("errors") or {}

        latest_d15 = d15[-1] if d15 else {}

        summary: Dict[str, Any] = {
            "ok": bool(status.get("ok", False)),
            "errors": errors,
            "mind": {
                "cycle": mind.get("mind_cycle"),
                "timestamp": mind.get("timestamp"),
                "coherence": mind.get("coherence"),
                "rhythm": mind.get("current_rhythm"),
                "domain": mind.get("current_domain"),
                "dominant_axiom": mind.get("dominant_axiom"),
                "recursion_warning": bool(mind.get("recursion_warning", False)),
                "kernel_blocks_total": mind.get("kernel_blocks_total"),
            },
            "body": {
                "cycle": body.get("cycle"),
                "timestamp": body.get("timestamp"),
                "coherence": body.get("coherence"),
                "rhythm": body.get("rhythm"),
                "alive": bool(body.get("alive", False)),
            },
            "d15": {
                "count": len(d15),
                "latest_timestamp": latest_d15.get("timestamp"),
                "latest_broadcast_id": latest_d15.get("broadcast_id"),
                "latest_axioms_in_tension": latest_d15.get("axioms_in_tension", []),
                "latest_verdict": (latest_d15.get("governance") or {}).get("verdict"),
            },
            "health": {
                "mind_alive": mind.get("mind_cycle") is not None,
                "body_alive": bool(body.get("alive", False)),
                "has_recent_d15": len(d15) > 0,
            },
        }
        return summary

    def summarize_system_health_alerts(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        alert_profiles: Dict[str, Dict[str, Any]] = {
            "strict": {
                "warn_mind_coherence": 0.90,
                "crit_mind_coherence": 0.80,
                "warn_body_coherence": 0.90,
                "crit_body_coherence": 0.80,
                "warn_mind_age_min": 15,
                "crit_mind_age_min": 45,
                "warn_body_age_min": 15,
                "crit_body_age_min": 45,
                "max_kernel_blocks_warn": 0,
            },
            "default": {
                "warn_mind_coherence": 0.85,
                "crit_mind_coherence": 0.70,
                "warn_body_coherence": 0.85,
                "crit_body_coherence": 0.70,
                "warn_mind_age_min": 30,
                "crit_mind_age_min": 90,
                "warn_body_age_min": 30,
                "crit_body_age_min": 90,
                "max_kernel_blocks_warn": 0,
            },
            "lenient": {
                "warn_mind_coherence": 0.75,
                "crit_mind_coherence": 0.60,
                "warn_body_coherence": 0.75,
                "crit_body_coherence": 0.60,
                "warn_mind_age_min": 60,
                "crit_mind_age_min": 180,
                "warn_body_age_min": 60,
                "crit_body_age_min": 180,
                "max_kernel_blocks_warn": 3,
            },
        }

        def _parse_ts(ts: Any) -> datetime | None:
            if not isinstance(ts, str) or not ts.strip():
                return None
            raw = ts.strip().replace("Z", "+00:00")
            try:
                dt = datetime.fromisoformat(raw)
            except ValueError:
                return None
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt

        def _add_alert(level: str, code: str, message: str, value: Any = None, threshold: Any = None) -> None:
            alert: Dict[str, Any] = {
                "level": level,
                "code": code,
                "message": message,
            }
            if value is not None:
                alert["value"] = value
            if threshold is not None:
                alert["threshold"] = threshold
            alerts.append(alert)

        d15_limit = int(arguments.get("d15_limit", 3))
        status = self.get_system_status({"d15_limit": d15_limit})

        profile_name = str(arguments.get("profile", "default")).strip().lower()
        profile = alert_profiles.get(profile_name, alert_profiles["default"])
        if profile_name not in alert_profiles:
            profile_name = "default"

        warn_mind_coherence = float(arguments.get("warn_mind_coherence", profile["warn_mind_coherence"]))
        crit_mind_coherence = float(arguments.get("crit_mind_coherence", profile["crit_mind_coherence"]))
        warn_body_coherence = float(arguments.get("warn_body_coherence", profile["warn_body_coherence"]))
        crit_body_coherence = float(arguments.get("crit_body_coherence", profile["crit_body_coherence"]))
        warn_mind_age_min = float(arguments.get("warn_mind_age_min", profile["warn_mind_age_min"]))
        crit_mind_age_min = float(arguments.get("crit_mind_age_min", profile["crit_mind_age_min"]))
        warn_body_age_min = float(arguments.get("warn_body_age_min", profile["warn_body_age_min"]))
        crit_body_age_min = float(arguments.get("crit_body_age_min", profile["crit_body_age_min"]))
        max_kernel_blocks_warn = int(arguments.get("max_kernel_blocks_warn", profile["max_kernel_blocks_warn"]))

        mind = status.get("mind_heartbeat") or {}
        body = status.get("body_heartbeat") or {}
        d15 = status.get("d15_broadcasts") or []
        errors = status.get("errors") or {}
        alerts: List[Dict[str, Any]] = []

        if errors:
            _add_alert(
                "CRITICAL",
                "PARTIAL_READ_FAILURE",
                "One or more telemetry sources failed to load",
                value=list(errors.keys()),
            )

        now = datetime.now(timezone.utc)

        mind_ts = _parse_ts(mind.get("timestamp"))
        if mind_ts is None:
            _add_alert("CRITICAL", "MIND_TIMESTAMP_MISSING", "MIND heartbeat timestamp missing or invalid")
        else:
            mind_age = (now - mind_ts).total_seconds() / 60.0
            if mind_age > crit_mind_age_min:
                _add_alert(
                    "CRITICAL",
                    "MIND_HEARTBEAT_STALE",
                    "MIND heartbeat is stale",
                    value=round(mind_age, 2),
                    threshold=crit_mind_age_min,
                )
            elif mind_age > warn_mind_age_min:
                _add_alert(
                    "WARNING",
                    "MIND_HEARTBEAT_AGING",
                    "MIND heartbeat age exceeded warning threshold",
                    value=round(mind_age, 2),
                    threshold=warn_mind_age_min,
                )

        body_ts = _parse_ts(body.get("timestamp"))
        if body_ts is None:
            _add_alert("CRITICAL", "BODY_TIMESTAMP_MISSING", "BODY heartbeat timestamp missing or invalid")
        else:
            body_age = (now - body_ts).total_seconds() / 60.0
            if body_age > crit_body_age_min:
                _add_alert(
                    "CRITICAL",
                    "BODY_HEARTBEAT_STALE",
                    "BODY heartbeat is stale",
                    value=round(body_age, 2),
                    threshold=crit_body_age_min,
                )
            elif body_age > warn_body_age_min:
                _add_alert(
                    "WARNING",
                    "BODY_HEARTBEAT_AGING",
                    "BODY heartbeat age exceeded warning threshold",
                    value=round(body_age, 2),
                    threshold=warn_body_age_min,
                )

        mind_coherence = mind.get("coherence")
        if isinstance(mind_coherence, (int, float)):
            if float(mind_coherence) < crit_mind_coherence:
                _add_alert(
                    "CRITICAL",
                    "MIND_COHERENCE_LOW",
                    "MIND coherence below critical threshold",
                    value=float(mind_coherence),
                    threshold=crit_mind_coherence,
                )
            elif float(mind_coherence) < warn_mind_coherence:
                _add_alert(
                    "WARNING",
                    "MIND_COHERENCE_WARN",
                    "MIND coherence below warning threshold",
                    value=float(mind_coherence),
                    threshold=warn_mind_coherence,
                )

        body_coherence = body.get("coherence")
        if isinstance(body_coherence, (int, float)):
            if float(body_coherence) < crit_body_coherence:
                _add_alert(
                    "CRITICAL",
                    "BODY_COHERENCE_LOW",
                    "BODY coherence below critical threshold",
                    value=float(body_coherence),
                    threshold=crit_body_coherence,
                )
            elif float(body_coherence) < warn_body_coherence:
                _add_alert(
                    "WARNING",
                    "BODY_COHERENCE_WARN",
                    "BODY coherence below warning threshold",
                    value=float(body_coherence),
                    threshold=warn_body_coherence,
                )

        if not bool(body.get("alive", False)):
            _add_alert("CRITICAL", "BODY_NOT_ALIVE", "BODY heartbeat indicates not alive")

        if bool(mind.get("recursion_warning", False)):
            _add_alert("WARNING", "MIND_RECURSION_WARNING", "MIND recursion warning is active")

        kernel_blocks_total = mind.get("kernel_blocks_total")
        if isinstance(kernel_blocks_total, int) and kernel_blocks_total > max_kernel_blocks_warn:
            _add_alert(
                "WARNING",
                "KERNEL_BLOCKS_PRESENT",
                "Kernel hard-block count exceeds warning threshold",
                value=kernel_blocks_total,
                threshold=max_kernel_blocks_warn,
            )

        if len(d15) == 0:
            _add_alert("WARNING", "D15_MISSING", "No recent D15 broadcasts in requested window")

        latest_verdict = None
        if d15:
            latest = d15[-1]
            governance = latest.get("governance") or {}
            latest_verdict = governance.get("verdict")
            if latest_verdict and latest_verdict != "PROCEED":
                _add_alert(
                    "WARNING",
                    "D15_NON_PROCEED",
                    "Latest D15 governance verdict is not PROCEED",
                    value=latest_verdict,
                    threshold="PROCEED",
                )

        level = "OK"
        if any(a.get("level") == "CRITICAL" for a in alerts):
            level = "CRITICAL"
        elif any(a.get("level") == "WARNING" for a in alerts):
            level = "WARNING"

        return {
            "level": level,
            "profile": profile_name,
            "alerts": alerts,
            "metrics": {
                "mind_cycle": mind.get("mind_cycle"),
                "mind_coherence": mind.get("coherence"),
                "body_cycle": body.get("cycle"),
                "body_coherence": body.get("coherence"),
                "d15_count": len(d15),
                "latest_d15_verdict": latest_verdict,
            },
            "thresholds": {
                "warn_mind_coherence": warn_mind_coherence,
                "crit_mind_coherence": crit_mind_coherence,
                "warn_body_coherence": warn_body_coherence,
                "crit_body_coherence": crit_body_coherence,
                "warn_mind_age_min": warn_mind_age_min,
                "crit_mind_age_min": crit_mind_age_min,
                "warn_body_age_min": warn_body_age_min,
                "crit_body_age_min": crit_body_age_min,
                "max_kernel_blocks_warn": max_kernel_blocks_warn,
            },
            "evaluated_at": now.isoformat(),
        }

    def dispatch(self, msg: Dict[str, Any]) -> Dict[str, Any]:
        method = msg.get("method")
        if method == "list_tools":
            return {"ok": True, "result": self.list_tools()}
        if method == "call_tool":
            params = msg.get("params", {})
            name = params.get("name")
            arguments = params.get("arguments", {})
            if name not in self.tools:
                return {"ok": False, "error": f"unknown tool: {name}"}
            try:
                result = self.tools[name](arguments)
                return {"ok": True, "result": result}
            except Exception as e:  # pragma: no cover
                return {"ok": False, "error": str(e)}
        return {"ok": False, "error": f"unknown method: {method}"}


def main() -> int:
    server = ElpidaMCPServer()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception as e:
            print(json.dumps({"ok": False, "error": f"invalid json: {e}"}), flush=True)
            continue
        resp = server.dispatch(msg)
        print(json.dumps(resp, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
