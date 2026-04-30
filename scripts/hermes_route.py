#!/usr/bin/env python3
"""
hermes_route.py — HERMES Phase 3 inbound: Telegram → architect commands → routed action.

The architect sends a message in the Control Room → 🎯 Commands topic.
HERMES (Fleet THE_INTERFACE) parses intent, decides what to do (create
GitHub Issue + assign Copilot, write to bridge, fire another workflow,
post a digest, etc.), executes via Claude Agent SDK with bypassPermissions,
and posts an acknowledgement back to the Commands topic.

Two invocation modes:

1. Cron-driven Telegram poll (every 5 min by default).
   - Reads .claude/bridge/hermes_command_watermark.json
   - Telegram Bot API: getUpdates with offset = last_update_id + 1
   - For each new message in TELEGRAM_CONTROL_ROOM_ID +
     TELEGRAM_TOPIC_COMMANDS, processes it as a command.
   - Updates watermark.

2. workflow_dispatch with `command` input.
   - Skips Telegram polling entirely.
   - Processes the input string as if it had arrived via Telegram.
   - Lets us test the routing without Telegram round-trips.

Migrated from Discord 2026-04-30. The dedicated Commands topic replaces
the `!hermes` prefix discipline of the old Discord channel — any message
in the topic is treated as a command. Prefix `/hermes` or `!hermes` is
still tolerated and stripped.

What HERMES does NOT do (constitutional bounds, same as Phase 2):
- Decide constitutional questions (it routes them; agents still hold gate-vetos)
- Modify source code, deploy, or touch infra
- Speak FOR other agents — it surfaces and routes

What HERMES Phase 3 ADDS over Phase 2:
- Two-way conversation with architect via Telegram
- Issue creation + Copilot assignment via gh CLI
- workflow_dispatch firing for other workflows

Required env (workflow secrets):
- ANTHROPIC_API_KEY — for the Agent SDK brain
- GITHUB_TOKEN — for gh CLI (workflow provides automatically)
- TELEGRAM_BOT_TOKEN — for reading messages and posting acks
- TELEGRAM_CONTROL_ROOM_ID — supergroup chat ID for the Control Room
- TELEGRAM_TOPIC_COMMANDS — forum topic ID for 🎯 Commands
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parent.parent
WATERMARK_PATH = REPO_ROOT / ".claude" / "bridge" / "hermes_command_watermark.json"
COMMAND_PREFIXES = ("/hermes", "!hermes")  # both tolerated, both stripped


HERMES_ROUTE_PROMPT_TEMPLATE = """You are HERMES, Fleet THE_INTERFACE node — A1 (Transparency / Existence is Relational), A4 (Process > Product), primary_gate SOVEREIGNTY. Per ELPIDA_CANON.md you are connective tissue between architect and agents.

The architect (Hernan) just sent this Telegram command in Control Room → 🎯 Commands topic:

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

1a. **AWS S3 read is available in this runner** (closed instrumentation gap, 2026-04-30). When the architect's command requires state verification, USE the `aws` CLI:
   - `aws s3 ls s3://elpida-body-evolution/feedback/ --region eu-north-1` — Gap 3 PHASE 5.5 watermark + feedback_to_native
   - `aws s3 ls s3://elpida-body-evolution/federation/identity_verification/entries/ --region eu-north-1` — Gap 2 Mirror verdicts
   - `aws s3 cp s3://elpida-body-evolution/federation/mind_heartbeat.json - --region eu-north-1 | python3 -m json.tool` — live MIND state
   - `aws s3 cp s3://elpida-body-evolution/federation/body_heartbeat.json - --region eu-north-1 | python3 -m json.tool` — live BODY state
   - `aws s3 ls s3://elpida-external-interfaces/d15/ --region eu-north-1 | tail -20` — recent D15 broadcasts to world
   Use these whenever the architect's command requires checking actual state instead of reasserting bridge claims. Per ELPIDA_CANON.md HERMES is observer not actor — read-only S3 verification fits that role exactly.

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

4. Compose a Telegram acknowledgement (concise, ≤2000 chars, plain text — the workflow will format as Telegram HTML):
   - One-line summary of what you understood the command to mean
   - One-line summary of what you did
   - URL if you created an Issue, or path if you wrote to bridge, or workflow run URL if you fired one
   - One-line "next step" if applicable (e.g., "Copilot will pick up the issue within minutes; you'll get a PR")
   - Save the ack text to /tmp/hermes_ack.txt — the workflow posts it to Telegram after you finish.

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


HERMES_ROUTE_PROMPT_NO_COMMAND = """You are HERMES (Fleet THE_INTERFACE) running in poll mode. Telegram Commands topic was checked but no new commands arrived since last poll. Write 'no new commands' to /tmp/hermes_ack.txt and exit cleanly. No bridge writes, no commits."""


# ════════════════════════════════════════════════════════════════════
# Watermark — track last processed Telegram update_id
# ════════════════════════════════════════════════════════════════════

def load_watermark() -> dict:
    if not WATERMARK_PATH.exists():
        return {"last_update_id": None, "last_check_utc": None}
    try:
        data = json.loads(WATERMARK_PATH.read_text(encoding="utf-8"))
        # Migration: older watermarks used last_message_id (Discord snowflake).
        # Treat that as None so we start fresh on Telegram.
        if "last_update_id" not in data:
            data["last_update_id"] = None
        return data
    except Exception:
        return {"last_update_id": None, "last_check_utc": None}


def save_watermark(last_update_id: int | None) -> None:
    WATERMARK_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_update_id": last_update_id,
        "last_check_utc": datetime.now(timezone.utc).isoformat(),
    }
    WATERMARK_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


# ════════════════════════════════════════════════════════════════════
# Telegram API helpers — stdlib only
# ════════════════════════════════════════════════════════════════════

def telegram_api(method: str, token: str, params: dict | None = None, timeout: int = 15) -> dict:
    """Call Telegram Bot API. Returns parsed JSON; raises on transport error."""
    url = f"https://api.telegram.org/bot{token}/{method}"
    if params:
        data = urlencode(params).encode("utf-8")
        req = Request(url, data=data, method="POST")
    else:
        req = Request(url, method="GET")
    with urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def telegram_diagnose_chat(chat_id: str, token: str) -> None:
    """
    Probe Telegram chat reachability so empty getUpdates results have a clear
    explanation in logs. Mirrors the Discord channel diagnostic pattern.
    """
    print("[hermes-route] running Telegram chat diagnostic...")

    try:
        result = telegram_api("getMe", token, timeout=10)
        if result.get("ok"):
            me = result["result"]
            print(
                f"[hermes-route] /getMe OK: bot=@{me.get('username')} id={me.get('id')}"
            )
        else:
            print(f"[hermes-route] /getMe FAILED: {result}")
            return
    except Exception as e:
        print(f"[hermes-route] /getMe ERROR: {type(e).__name__}: {e}")
        return

    try:
        result = telegram_api("getChat", token, params={"chat_id": chat_id}, timeout=10)
        if result.get("ok"):
            chat = result["result"]
            print(
                f"[hermes-route] /getChat OK: chat_id={chat.get('id')} "
                f"title={chat.get('title')!r} type={chat.get('type')}"
            )
        else:
            print(f"[hermes-route] /getChat FAILED for chat_id={chat_id}: {result}")
    except Exception as e:
        print(f"[hermes-route] /getChat ERROR for chat_id={chat_id}: {type(e).__name__}: {e}")


def telegram_react(chat_id: str, message_id: int, token: str, emoji: str) -> bool:
    """
    Add an emoji reaction to a message. Returns True on success.

    Emojis used (same constitutional pattern as Discord):
      👀 — picked up, processing
      ✅ — completed successfully
      ❌ — failed (see ack for reason)
      💬 — clarification needed (ambiguous command)
    """
    try:
        result = telegram_api(
            "setMessageReaction",
            token,
            params={
                "chat_id": chat_id,
                "message_id": message_id,
                "reaction": json.dumps([{"type": "emoji", "emoji": emoji}]),
            },
            timeout=10,
        )
        return bool(result.get("ok"))
    except Exception as e:
        print(f"[hermes-route] reaction failed ({emoji}): {e}", file=sys.stderr)
        return False


def fetch_new_telegram_updates(
    token: str,
    chat_id: str,
    topic_id: str,
    after_update_id: int | None,
) -> list[dict]:
    """
    Pull new updates from Telegram, filtered to messages in the Control Room
    Commands topic. Returns a list of message dicts (chronological order).

    The watermark mechanic: pass `offset = after_update_id + 1` so Telegram
    returns only newer events. First-run (no watermark) skips backlog by
    starting from current latest update.
    """
    # Determine offset
    if after_update_id is not None:
        offset = after_update_id + 1
    else:
        offset = -1  # first run: start at latest, don't replay backlog

    try:
        result = telegram_api(
            "getUpdates",
            token,
            params={
                "offset": offset,
                "timeout": 0,  # short-poll (workflow has its own cron cadence)
                "allowed_updates": json.dumps(["message"]),
            },
            timeout=15,
        )
    except URLError as e:
        print(f"[hermes-route] telegram getUpdates failed: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[hermes-route] telegram getUpdates unexpected: {e}", file=sys.stderr)
        return []

    if not result.get("ok"):
        print(f"[hermes-route] getUpdates not OK: {result}", file=sys.stderr)
        return []

    updates = result.get("result") or []
    target_chat = str(chat_id)
    target_topic = str(topic_id) if topic_id else ""
    out: list[dict] = []

    for u in updates:
        msg = u.get("message") or u.get("edited_message")
        if not msg:
            continue
        chat = msg.get("chat") or {}
        if str(chat.get("id")) != target_chat:
            continue
        if target_topic and str(msg.get("message_thread_id") or "") != target_topic:
            continue
        # Annotate with the update_id so caller can advance watermark cleanly.
        msg["_update_id"] = u.get("update_id")
        out.append(msg)
    return out


def post_ack_to_telegram(
    text: str,
    token: str,
    chat_id: str,
    topic_id: str,
    reply_to_message_id: int | None = None,
) -> None:
    """Post the routing acknowledgement to the Commands topic."""
    if not token or not chat_id:
        print("[hermes-route] TELEGRAM_BOT_TOKEN or chat_id missing — skipping ack post")
        return

    import html as _html
    body = _html.escape(text.strip()[:3500], quote=False)
    formatted = (
        "<b>🎯 HERMES — Command Routed</b>\n\n"
        f"{body}\n\n"
        "<i>Fleet THE_INTERFACE · A1+A4 · SOVEREIGNTY · Phase 3 routing</i>"
    )

    payload = {
        "chat_id": chat_id,
        "text": formatted[:4096],
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if topic_id:
        try:
            payload["message_thread_id"] = int(topic_id)
        except ValueError:
            pass
    if reply_to_message_id:
        payload["reply_to_message_id"] = reply_to_message_id

    try:
        result = telegram_api("sendMessage", token, params=payload, timeout=15)
        if result.get("ok"):
            print(
                f"[hermes-route] telegram ack post OK: "
                f"message_id={result['result'].get('message_id')}"
            )
        else:
            print(f"[hermes-route] telegram ack post failed: {result}", file=sys.stderr)
    except Exception as e:
        print(f"[hermes-route] telegram ack post failed: {e}", file=sys.stderr)


# ════════════════════════════════════════════════════════════════════
# Command parsing
# ════════════════════════════════════════════════════════════════════

def is_command(content: str) -> bool:
    """
    Any non-empty message in the Commands topic counts as a command.
    The dedicated topic is the filter — no prefix required.
    Service messages and bot replies have already been filtered upstream.
    """
    return bool(content and content.strip())


def extract_command_text(content: str) -> str:
    """Strip optional /hermes or !hermes prefix; return the rest."""
    stripped = content.strip()
    for prefix in COMMAND_PREFIXES:
        if stripped.lower().startswith(prefix.lower()):
            return stripped[len(prefix):].strip()
    return stripped


# ════════════════════════════════════════════════════════════════════
# Agent SDK dispatch
# ════════════════════════════════════════════════════════════════════

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


# ════════════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════════════

def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[hermes-route] FATAL: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CONTROL_ROOM_ID", "").strip()
    topic_id = os.environ.get("TELEGRAM_TOPIC_COMMANDS", "").strip()

    # Manual override: workflow_dispatch input
    manual_command = os.environ.get("HERMES_MANUAL_COMMAND", "").strip()
    if manual_command:
        print(f"[hermes-route] manual mode — command: {manual_command!r}")
        ack_path = Path("/tmp/hermes_ack.txt")
        if ack_path.exists():
            ack_path.unlink()
        rc = asyncio.run(run_hermes_routing(
            command_text=extract_command_text(manual_command),
            message_id="manual_dispatch",
            author=os.environ.get("HERMES_MANUAL_AUTHOR", "architect"),
            ts=datetime.now(timezone.utc).isoformat(),
        ))
        ack = ack_path.read_text(encoding="utf-8") if ack_path.exists() else "(no ack written)"
        post_ack_to_telegram(
            f"Manual dispatch: {manual_command}\n\n{ack}",
            token=token,
            chat_id=chat_id,
            topic_id=topic_id,
        )
        return rc

    # Polling mode: Telegram Commands topic
    if not token or not chat_id or not topic_id:
        print(
            "[hermes-route] TELEGRAM_BOT_TOKEN, TELEGRAM_CONTROL_ROOM_ID, or "
            "TELEGRAM_TOPIC_COMMANDS missing — skipping poll. "
            "(Manual workflow_dispatch with HERMES_MANUAL_COMMAND still works.)",
            file=sys.stderr,
        )
        return 0

    wm = load_watermark()
    after_update_id = wm.get("last_update_id")
    msgs = fetch_new_telegram_updates(token, chat_id, topic_id, after_update_id)

    if not msgs:
        # Distinguish "no new messages" (genuine empty) from "telegram fetch
        # failed" (silent failure logged earlier). Run chat diagnostic so
        # the next log explicitly says what's wrong.
        print("[hermes-route] no messages returned — running chat diagnostic")
        telegram_diagnose_chat(chat_id, token)
        save_watermark(after_update_id)  # bump check time
        return 0

    new_last_id = after_update_id
    processed = 0
    for m in msgs:
        update_id = m.get("_update_id")
        if update_id is not None:
            new_last_id = max(new_last_id or 0, update_id)
        # Skip messages from bots (including our own webhook posts / replies)
        sender = m.get("from") or {}
        if sender.get("is_bot"):
            continue
        content = m.get("text", "") or ""
        if not is_command(content):
            continue
        cmd_text = extract_command_text(content)
        if not cmd_text:
            continue
        author_name = (
            sender.get("first_name")
            or sender.get("username")
            or "unknown"
        )
        ts = datetime.fromtimestamp(
            m.get("date", 0), tz=timezone.utc
        ).isoformat() if m.get("date") else datetime.now(timezone.utc).isoformat()

        message_id = m.get("message_id")

        # IMMEDIATELY react with 👀 so the architect sees the command was picked
        # up. The ack post will land in the Commands topic shortly afterwards;
        # the reaction lands on the original message within ~1 second.
        if message_id is not None:
            telegram_react(chat_id, message_id, token, "👀")

        ack_path = Path("/tmp/hermes_ack.txt")
        if ack_path.exists():
            ack_path.unlink()

        success = False
        try:
            asyncio.run(run_hermes_routing(
                command_text=cmd_text,
                message_id=str(message_id),
                author=author_name,
                ts=ts,
            ))
            success = True
        except Exception as e:
            print(f"[hermes-route] command processing failed: {e}", file=sys.stderr)
            if message_id is not None:
                telegram_react(chat_id, message_id, token, "❌")
            post_ack_to_telegram(
                f"Command failed: {cmd_text}\n\nError: {type(e).__name__}: {e}",
                token=token,
                chat_id=chat_id,
                topic_id=topic_id,
                reply_to_message_id=message_id,
            )
            continue

        ack = ack_path.read_text(encoding="utf-8") if ack_path.exists() else "(no ack written)"
        post_ack_to_telegram(
            f"Command: {cmd_text}\nfrom {author_name} at {ts}\n\n{ack}",
            token=token,
            chat_id=chat_id,
            topic_id=topic_id,
            reply_to_message_id=message_id,
        )
        # Final reaction reflects outcome.
        ack_low = ack.lower()
        if message_id is not None:
            if success and ("clarification" in ack_low or ack.strip().startswith(("?", "Could", "What", "Which", "Can"))):
                telegram_react(chat_id, message_id, token, "💬")
            elif success:
                telegram_react(chat_id, message_id, token, "✅")
        processed += 1

    save_watermark(new_last_id)
    print(f"[hermes-route] processed {processed} command(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
