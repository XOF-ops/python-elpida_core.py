from __future__ import annotations

import json
import sys
from dataclasses import asdict
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
