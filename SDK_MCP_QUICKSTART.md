# Elpida SDK + MCP (Phase 1, Read-only)

## What was added

- `elpida_sdk/` read-only SDK modules
- `mcp_server/server.py` lightweight stdio MCP-style server stub

## Quick smoke test

```bash
cd /workspaces/python-elpida_core.py
python -m mcp_server.server <<'EOF'
{"method":"list_tools"}
{"method":"call_tool","params":{"name":"list_domains","arguments":{}}}
{"method":"call_tool","params":{"name":"kernel_check_text","arguments":{"text":"Test proposal for constitutional review."}}}
EOF
```

## Live federation/world read test

Requires AWS credentials in env.

```bash
cd /workspaces/python-elpida_core.py
source .env
export AWS_EC2_METADATA_DISABLED=true
python -m mcp_server.server <<'EOF'
{"method":"call_tool","params":{"name":"get_mind_heartbeat","arguments":{}}}
{"method":"call_tool","params":{"name":"get_body_heartbeat","arguments":{}}}
{"method":"call_tool","params":{"name":"get_d15_broadcasts","arguments":{"limit":2}}}
{"method":"call_tool","params":{"name":"get_system_status","arguments":{"d15_limit":2}}}
{"method":"call_tool","params":{"name":"summarize_system_status","arguments":{"d15_limit":2}}}
{"method":"call_tool","params":{"name":"summarize_system_health_alerts","arguments":{"d15_limit":2}}}
{"method":"call_tool","params":{"name":"summarize_system_health_alerts","arguments":{"profile":"lenient","d15_limit":2}}}
{"method":"call_tool","params":{"name":"summarize_system_health_alerts","arguments":{"profile":"default","d15_limit":2,"alerts_only":true}}}
{"method":"call_tool","params":{"name":"summarize_system_health_alerts","arguments":{"profile":"default","alerts_only":true,"min_level":"CRITICAL","max_alerts":1}}}
EOF
```

`summarize_system_health_alerts` supports profiles: `strict`, `default`, `lenient`.
Any explicit threshold argument still overrides the selected profile.
Set `alerts_only=true` for a compact webhook/paging payload.
Use `min_level` (`WARNING` or `CRITICAL`) and `max_alerts` to bound payload size.

## Checkpoint read test

Requires AWS credentials in env and executable script present.

```bash
cd /workspaces/python-elpida_core.py
source .env
export AWS_EC2_METADATA_DISABLED=true
python -m mcp_server.server <<'EOF'
{"method":"call_tool","params":{"name":"list_checkpoints","arguments":{"layers":["mind"],"latest_n":3,"since_hours":72}}}
EOF
```

## SDK usage example

```python
from elpida_sdk import ElpidaConfig, KernelGuard, S3Client

cfg = ElpidaConfig()
print(len(cfg.list_domains()))
print(len(cfg.list_axioms()))
print(KernelGuard.check_text("Hello constitutional world").to_dict())

s3 = S3Client()
print(s3.read_json(s3.buckets.federation, "federation/mind_heartbeat.json"))
```
