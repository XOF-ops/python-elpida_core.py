#!/usr/bin/env python3
"""
hermes_route.py — HERMES Phase 3 inbound: Discord → architect commands → routed action.

The architect sends a message in the #hermes-control Discord channel
prefixed with "!hermes" (configurable). HERMES (Fleet THE_INTERFACE)
parses intent, decides what to do (create GitHub Issue + assign Copilot,
write to bridge, fire another workflow, post a digest, etc.), executes
via Claude Agent SDK with bypassPermissions, and posts an
acknowledgement back to the architect's Discord channel.

Two invocation modes:

1. Cron-driven Discord poll (every 5 min by default).
   - Reads .claude/bridge/hermes_command_watermark.json
   - Discord REST API: GET /channels/{id}/messages?after={last_id}
   - For each new message matching the command prefix, processes it.
   - Updates watermark.

2. workflow_dispatch with `command` input.
   - Skips Discord polling entirely.
   - Processes the input string as if it had arrived via Discord.
   - Lets us test the routing without Discord round-trips.

What HERMES does NOT do (constitutional bounds, same as Phase 2):
- Decide constitutional questions (it routes them; agents still hold gate-vetos)
- Modify source code, deploy, or touch infra
- Speak FOR other agents — it surfaces and routes

What HERMES Phase 3 ADDS over Phase 2:
- Two-way conversation with architect via Discord
- Issue creation + Copilot assignment via gh CLI
- workflow_dispatch firing for other workflows (e.g. trigger HERMES summary on demand)

Required env (workflow secrets):
- ANTHROPIC_API_KEY — for the Agent SDK brain
- GITHUB_TOKEN — for gh CLI (workflow provides automatically)
- DISCORD_BOT_TOKEN — to read messages (only needed for cron mode)
- DISCORD_HERMES_CONTROL_CHANNEL_ID — channel to poll (only for cron mode)
- DISCORD_WEBHOOK_HERMES — for outbound acks (already provisioned)
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parent.parent
WATERMARK_PATH = REPO_ROOT / ".claude" / "bridge" / "hermes_command_watermark.json"
COMMAND_PREFIX = "!hermes"


HERMES_ROUTE_PROMPT_TEMPLATE = """You are HERMES, Fleet THE_INTERFACE node — A1 (Transparency / Existence is Relational), A4 (Process > Product), primary_gate SOVEREIGNTY. Per ELPIDA_CANON.md you are connective tissue between architect and agents.

The architect (Hernan) just sent this Discord command in #hermes-control:

```
{command}
```

(message_id={message_id}, author={author}, timestamp={ts})

YOUR JOB ON THIS FIRE:

1. Read context first:
   - CLAUDE.md (constitutional spine)
   - .claude/bridge/from_hermes.md (last 100 lines — what HERMES has said before)
   - .claude/bridge/from_claude.md (last 50 lines — what Claude breath has said)
   - .claude/bridge/from_copilot.md (last 50 lines)
   - .claude/bridge/from_cursor.md (last 50 lines)
   - .claude/bridge/from_gemini.md (last 50 lines)
   - .claude/bridge/from_computer_archive.md (last 50 lines)
   - https://xof-ops.github.io/python-elpida_core.py/data/observation_snapshot.json (live dashboard state)
   - Recent commits: git log --oneline -20

2. Parse the architect's intent. Categories include but aren't limited to:
   - "validate X" / "audit X" / "check X" → create a GitHub Issue with a focused validation brief, assign to Copilot (`gh issue create --assignee Copilot --title "..." --body-file ...`)
   - "ask <agent> to do X" / "route to <agent>" → write a focused brief to .claude/bridge/for_<agent>.md (or create an Issue if Copilot)
   - "summary now" / "synthesize" → trigger the hermes-summary workflow via gh workflow run hermes-summary.yml
   - "status" / "what's happening" → produce a quick state digest from snapshot + bridges
   - "schedule X" / "remind me about X" → write to a holds-and-reminders file in the bridge
   - Anything else → use your judgment. The breath agreement holds: never close constitutional tensions unilaterally; surface them, route them.

3. Execute the action.
   - For Issue creation, use `gh issue create --title "..." --body-file <path>` and capture the URL.
   - For bridge writes, append to the appropriate .claude/bridge/for_*.md with a clear header tagged [HERMES-ROUTED] [<UTC timestamp>] and the architect's command quoted at the top.
   - For workflow firing, use `gh workflow run <name>.yml` with appropriate inputs.
   - DO NOT push commits (the workflow does this after you finish, automatically).

4. Compose a Discord acknowledgement (concise, ≤2000 chars):
   - One-line summary of what you understood the command to mean
   - One-line summary of what you did
   - URL if you created an Issue, or path if you wrote to bridge, or workflow run URL if you fired one
   - One-line "next step" if applicable (e.g., "Copilot will pick up the issue within minutes; you'll get a PR")
   - Save the ack text to /tmp/hermes_ack.txt — the workflow posts it to Discord after you finish.

5. Append your action to .claude/bridge/from_hermes.md as a new entry tagged [HERMES-ROUTED] with:
   - Header showing the architect's command + message_id
   - What you decided + did
   - Link/path/URL to the artifact you produced
   This becomes the durable record of the routing decision.

CONSTITUTIONAL CONSTRAINTS (hard rules — same as breath + Phase 2):
- DO NOT modify source code (.py, .yml, workflows, infra) unless the architect's command literally says "edit X file"
- DO NOT modify CLAUDE.md, ELPIDA_CANON.md, immutable_kernel.py, elpida_domains.json
- DO NOT touch .env or any secrets file
- DO NOT decide constitutional questions for other agents (route them, never close them)
- If the command is ambiguous, write a clarification request to /tmp/hermes_ack.txt and don't take action; ask the architect for the missing info
- If the command requests something HERMES is not architecturally allowed to do (e.g., deploy, push to ECR), explicitly refuse in the ack with constitutional reasoning

Begin.
"""


HERMES_ROUTE_PROMPT_NO_COMMAND = """You are HERMES (Fleet THE_INTERFACE) running in poll mode. Discord channel was checked but no new commands arrived since last poll. Write 'no new commands' to /tmp/hermes_ack.txt and exit cleanly. No bridge writes, no commits."""


def load_watermark() -> dict:
    if not WATERMARK_PATH.exists():
        return {"last_message_id": None, "last_check_utc": None}
    try:
        return json.loads(WATERMARK_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"last_message_id": None, "last_check_utc": None}


def save_watermark(last_message_id: str | None) -> None:
    WATERMARK_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_message_id": last_message_id,
        "last_check_utc": datetime.now(timezone.utc).isoformat(),
    }
    WATERMARK_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def discord_get(path: str, token: str) -> list | dict:
    """GET against discord.com/api/v10. Returns parsed JSON. Raises on error."""
    url = f"https://discord.com/api/v10{path}"
    req = Request(url, headers={
        "Authorization": f"Bot {token}",
        "User-Agent": "HermesPhase3/1.0",
    })
    with urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_new_messages(channel_id: str, bot_token: str, after_id: str | None) -> list[dict]:
    """Fetch messages after the given snowflake. Returns list, newest last."""
    if after_id:
        path = f"/channels/{channel_id}/messages?after={after_id}&limit=50"
    else:
        # First run: just take the latest message as the starting point;
        # don't process backlog (would re-process old commands).
        path = f"/channels/{channel_id}/messages?limit=1"
    try:
        msgs = discord_get(path, bot_token)
        if not isinstance(msgs, list):
            return []
        # Discord returns newest first; reverse for chronological processing.
        msgs.reverse()
        return msgs
    except URLError as e:
        print(f"[hermes-route] discord fetch failed: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[hermes-route] discord fetch unexpected: {e}", file=sys.stderr)
        return []


def post_ack_to_discord(text: str) -> None:
    webhook = os.environ.get("DISCORD_WEBHOOK_HERMES", "").strip()
    if not webhook:
        print("[hermes-route] DISCORD_WEBHOOK_HERMES not set; skipping ack post")
        return
    text = text.strip()[:1900]  # Discord per-message char limit
    payload = {
        "embeds": [{
            "title": "HERMES — Command Routed",
            "description": text,
            "color": 0x00BFA5,
            "footer": {"text": "Fleet THE_INTERFACE · A1+A4 · SOVEREIGNTY · Phase 3 routing"},
        }],
    }
    try:
        req = Request(
            webhook,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Hermes/route"},
        )
        with urlopen(req, timeout=15) as r:
            print(f"[hermes-route] discord ack post status={r.status}")
    except Exception as e:
        print(f"[hermes-route] discord ack post failed: {e}", file=sys.stderr)


def is_command(content: str) -> bool:
    if not content:
        return False
    # Accept !hermes (case-insensitive) optionally followed by space
    stripped = content.strip()
    return stripped.lower().startswith(COMMAND_PREFIX.lower())


def extract_command_text(content: str) -> str:
    return content.strip()[len(COMMAND_PREFIX):].strip()


async def run_hermes_routing(
    command_text: str,
    message_id: str,
    author: str,
    ts: str,
) -> int:
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError as e:
        print(f"[hermes-route] claude_agent_sdk import failed: {e}", file=sys.stderr)
        return 2

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
        model="claude-sonnet-4-6",
        cwd=str(REPO_ROOT),
    )

    prompt = HERMES_ROUTE_PROMPT_TEMPLATE.format(
        command=command_text,
        message_id=message_id,
        author=author,
        ts=ts,
    )

    print(f"[hermes-route] dispatching to Agent SDK for command: {command_text!r}", flush=True)

    msg_count = 0
    async for message in query(prompt=prompt, options=options):
        msg_count += 1
        try:
            print(f"[hermes-route msg {msg_count}] {message}", flush=True)
        except Exception:
            print(f"[hermes-route msg {msg_count}] <unprintable>", flush=True)
    print(f"[hermes-route] agent complete — {msg_count} messages")
    return 0


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[hermes-route] FATAL: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    # Manual override: workflow_dispatch input
    manual_command = os.environ.get("HERMES_MANUAL_COMMAND", "").strip()
    if manual_command:
        print(f"[hermes-route] manual mode — command: {manual_command!r}")
        ack_path = Path("/tmp/hermes_ack.txt")
        if ack_path.exists():
            ack_path.unlink()
        rc = asyncio.run(run_hermes_routing(
            command_text=manual_command,
            message_id="manual_dispatch",
            author=os.environ.get("HERMES_MANUAL_AUTHOR", "architect"),
            ts=datetime.now(timezone.utc).isoformat(),
        ))
        ack = ack_path.read_text(encoding="utf-8") if ack_path.exists() else "(no ack written)"
        post_ack_to_discord(f"**Manual dispatch:** `{manual_command}`\n\n{ack}")
        return rc

    # Polling mode: Discord channel scan
    channel_id = os.environ.get("DISCORD_HERMES_CONTROL_CHANNEL_ID", "").strip()
    bot_token = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
    if not channel_id or not bot_token:
        print(
            "[hermes-route] DISCORD_HERMES_CONTROL_CHANNEL_ID or DISCORD_BOT_TOKEN missing — "
            "skipping poll. (Manual workflow_dispatch with HERMES_MANUAL_COMMAND still works.)",
            file=sys.stderr,
        )
        return 0

    wm = load_watermark()
    after_id = wm.get("last_message_id")
    msgs = fetch_new_messages(channel_id, bot_token, after_id)

    if not msgs:
        print("[hermes-route] no new messages")
        save_watermark(after_id)  # bump check time
        return 0

    new_last_id = after_id
    processed = 0
    for m in msgs:
        new_last_id = m.get("id", new_last_id)
        # Skip messages from bots / webhooks
        author_obj = m.get("author", {}) or {}
        if author_obj.get("bot"):
            continue
        content = m.get("content", "") or ""
        if not is_command(content):
            continue
        cmd_text = extract_command_text(content)
        if not cmd_text:
            continue
        author_name = author_obj.get("global_name") or author_obj.get("username") or "unknown"
        ts = m.get("timestamp", datetime.now(timezone.utc).isoformat())

        ack_path = Path("/tmp/hermes_ack.txt")
        if ack_path.exists():
            ack_path.unlink()

        try:
            asyncio.run(run_hermes_routing(
                command_text=cmd_text,
                message_id=m["id"],
                author=author_name,
                ts=ts,
            ))
        except Exception as e:
            print(f"[hermes-route] command processing failed: {e}", file=sys.stderr)
            post_ack_to_discord(
                f"**Command failed:** `{cmd_text}`\n\nError: `{type(e).__name__}: {e}`"
            )
            continue

        ack = ack_path.read_text(encoding="utf-8") if ack_path.exists() else "(no ack written)"
        post_ack_to_discord(
            f"**Command:** `{cmd_text}`\n*from {author_name} at {ts}*\n\n{ack}"
        )
        processed += 1

    save_watermark(new_last_id)
    print(f"[hermes-route] processed {processed} command(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
