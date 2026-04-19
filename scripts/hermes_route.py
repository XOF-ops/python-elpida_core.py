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
   - "validate X" / "audit X" / "check X" → create EXACTLY ONE GitHub Issue with a focused validation brief, assign to Copilot (`gh issue create --assignee Copilot --title "..." --body-file ...`). DO NOT create a duplicate or a follow-up issue in the same fire — one Issue per architect command. If you need to add context, comment on that single Issue (`gh issue comment <num> --body "..."`).
   - "ask <agent> to do X" / "route to <agent>" → write a focused brief to .claude/bridge/for_<agent>.md (or create an Issue if Copilot)
   - "summary now" / "synthesize" → trigger the hermes-summary workflow via gh workflow run hermes-summary.yml
   - "status" / "what's happening" → produce a quick state digest from snapshot + bridges
   - "schedule X" / "remind me about X" → write to a holds-and-reminders file in the bridge
   - Anything else → use your judgment. The breath agreement holds: never close constitutional tensions unilaterally; surface them, route them.

2a. Before routing, check for prior resolution to avoid re-routing already-completed work:
   - `gh issue list --state closed --search "<topic keywords>" --limit 5` — if the architect's command matches a recently-resolved issue, surface that resolution instead of re-routing
   - `gh pr list --state merged --limit 10 --search "<topic keywords>"` — if the work already landed, name the PR + merge timestamp in the ack instead of creating a duplicate Issue
   - If a duplicate is detected, the ack should say "Already resolved: PR #N merged at <ts>" and skip Issue creation. Saves architect's time.

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


def discord_diagnose_channel(channel_id: str, token: str) -> None:
    """Two-stage diagnostic to distinguish wrong-bot from wrong-channel-permission.

    Stage 1: GET /users/@me — identifies WHICH bot the token belongs to
             (name + id). If the architect intended Bot A but the secret
             contains Bot B's token, this surfaces it.

    Stage 2: GET /users/@me/guilds — lists which servers the bot is actually
             in. Compared against the channel diagnostic, this reveals if
             the bot just isn't in the right server.

    Stage 3: GET /channels/{id} — channel info; distinguishes the remaining
             failure modes via Discord error code:
               10003 = Unknown Channel (ID truly doesn't exist)
               50001 = Missing Access (bot not in server / not in channel)
               50013 = Missing Permissions (bot in channel but lacks perms)
                   0 = bare 404 — usually bot not in server containing this channel
    """
    from urllib.error import HTTPError

    # Stage 1: which bot is this?
    try:
        req = Request("https://discord.com/api/v10/users/@me", headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "HermesPhase3/1.0",
        })
        with urlopen(req, timeout=15) as r:
            me = json.loads(r.read().decode("utf-8"))
        print(f"[hermes-route] BOT IDENTITY: id={me.get('id')} "
              f"username={me.get('username')!r} discriminator={me.get('discriminator')} "
              f"bot={me.get('bot')}")
    except HTTPError as e:
        print(f"[hermes-route] /users/@me FAILED: HTTP {e.code} — DISCORD_BOT_TOKEN "
              f"is invalid or revoked. Token cannot identify any bot.")
        return
    except Exception as e:
        print(f"[hermes-route] /users/@me UNEXPECTED: {type(e).__name__}: {e}")
        return

    # Stage 2: what guilds (servers) is this bot in?
    try:
        req = Request("https://discord.com/api/v10/users/@me/guilds", headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "HermesPhase3/1.0",
        })
        with urlopen(req, timeout=15) as r:
            guilds = json.loads(r.read().decode("utf-8"))
        if not guilds:
            print("[hermes-route] BOT IS IN ZERO SERVERS. The token is valid but "
                  "the bot has not been invited to any Discord server. Use the "
                  "OAuth invite URL from Discord Developer Portal to add the bot "
                  "to your Elpida server.")
        else:
            for g in guilds:
                print(f"[hermes-route] guild: id={g.get('id')} name={g.get('name')!r}")
    except Exception as e:
        print(f"[hermes-route] /users/@me/guilds FAILED: {type(e).__name__}: {e}")

    # Stage 3: original channel-specific diagnostic
    url = f"https://discord.com/api/v10/channels/{channel_id}"
    try:
        req = Request(url, headers={
            "Authorization": f"Bot {token}",
            "User-Agent": "HermesPhase3/1.0",
        })
        with urlopen(req, timeout=15) as r:
            body = r.read().decode("utf-8")
            obj = json.loads(body)
            print(f"[hermes-route] channel diagnostic OK ({r.status}): "
                  f"name=#{obj.get('name','?')} type={obj.get('type','?')} "
                  f"guild_id={obj.get('guild_id','?')}")
    except HTTPError as e:
        try:
            body = e.read().decode("utf-8")
        except Exception:
            body = "(no body)"
        print(f"[hermes-route] channel diagnostic FAILED: HTTP {e.code}")
        print(f"[hermes-route] response body: {body[:500]}")
        try:
            obj = json.loads(body)
            err_code = obj.get("code")
            if err_code == 10003:
                print("[hermes-route] DIAGNOSIS: Channel ID does not exist anywhere. "
                      "Re-copy from Discord (right-click TEXT CHANNEL → Copy Channel ID).")
            elif err_code == 50001:
                print("[hermes-route] DIAGNOSIS: Missing Access. Bot is in the server "
                      "but channel has permission overrides excluding it. Check "
                      "channel-level permissions in Discord.")
            elif err_code == 50013:
                print("[hermes-route] DIAGNOSIS: Bot has access but lacks specific "
                      "permissions. Grant: View Channel, Read Message History, "
                      "Add Reactions.")
            elif err_code == 0:
                print("[hermes-route] DIAGNOSIS: Bot is not in the server containing "
                      "this channel. Compare the guilds listed above to the server "
                      "where #hermes-control lives. If the server isn't in the bot's "
                      "guild list, you need to invite the bot via the OAuth URL from "
                      "Discord Developer Portal. If the server IS listed, the channel "
                      "ID may be wrong.")
        except Exception:
            pass
    except Exception as e:
        print(f"[hermes-route] channel diagnostic UNEXPECTED: {type(e).__name__}: {e}")


def discord_react(channel_id: str, message_id: str, token: str, emoji: str) -> bool:
    """Add a reaction to a message. Mirrors the guest-chamber Parliament-emoji
    pattern so the architect sees within ~seconds that HERMES picked up the
    command. Returns True on success.

    Emojis used:
      👀 — picked up, processing
      ✅ — completed successfully
      ❌ — failed (see ack for reason)
      💬 — clarification needed (ambiguous command)

    Discord wants the unicode emoji URL-encoded for unicode reactions.
    """
    from urllib.parse import quote
    url = (
        f"https://discord.com/api/v10/channels/{channel_id}"
        f"/messages/{message_id}/reactions/{quote(emoji)}/@me"
    )
    req = Request(url, method="PUT", headers={
        "Authorization": f"Bot {token}",
        "User-Agent": "HermesPhase3/1.0",
        "Content-Length": "0",
    })
    try:
        with urlopen(req, timeout=10) as r:
            return r.status in (200, 204)
    except Exception as e:
        print(f"[hermes-route] reaction failed ({emoji}): {e}", file=sys.stderr)
        return False


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
        # Distinguish "no new messages" (genuine empty) from "discord fetch
        # failed" (silent failure logged earlier). Run channel diagnostic so
        # the next log explicitly says what's wrong.
        print("[hermes-route] no messages returned — running channel diagnostic")
        discord_diagnose_channel(channel_id, bot_token)
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

        # IMMEDIATELY react with 👀 so the architect sees the command was picked
        # up. The ack post will land in #hermes-summary later; the reaction lands
        # on the original message in the original channel within a second.
        discord_react(channel_id, m["id"], bot_token, "👀")

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
            success = True
        except Exception as e:
            print(f"[hermes-route] command processing failed: {e}", file=sys.stderr)
            discord_react(channel_id, m["id"], bot_token, "❌")
            post_ack_to_discord(
                f"**Command failed:** `{cmd_text}`\n\nError: `{type(e).__name__}: {e}`"
            )
            continue

        ack = ack_path.read_text(encoding="utf-8") if ack_path.exists() else "(no ack written)"
        post_ack_to_discord(
            f"**Command:** `{cmd_text}`\n*from {author_name} at {ts}*\n\n{ack}"
        )
        # Final reaction reflects outcome — ✅ for success, 💬 if the agent
        # decided the command was ambiguous (signaled by ack containing
        # "clarification" or starting with a question).
        ack_low = ack.lower()
        if success and ("clarification" in ack_low or ack.strip().startswith(("?", "Could", "What", "Which", "Can"))):
            discord_react(channel_id, m["id"], bot_token, "💬")
        elif success:
            discord_react(channel_id, m["id"], bot_token, "✅")
        processed += 1

    save_watermark(new_last_id)
    print(f"[hermes-route] processed {processed} command(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
