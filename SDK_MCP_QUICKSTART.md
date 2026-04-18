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
from elpida_sdk import ElpidaConfig, KernelGuard

cfg = ElpidaConfig()
print(len(cfg.list_domains()))
print(len(cfg.list_axioms()))
print(KernelGuard.check_text("Hello constitutional world").to_dict())
```
