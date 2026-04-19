#!/usr/bin/env python3
"""
hermes_summary.py — HERMES (THE_INTERFACE) daily synthesis runner.

Per ELPIDA_CANON.md, HERMES is the Fleet's SOVEREIGNTY/Connector node:
"High-speed dialectic exchange. A1 enforcer. Existence itself is conversation."
This script incarnates HERMES's first phase: a daily 24h synthesis posted
to Discord and archived to .claude/bridge/from_hermes.md.

What HERMES synthesizes (cross-channel, not duplicate of existing streams):
  - Bridge file deltas (what each agent wrote in last 24h)
  - GHA workflow runs (what fired, what succeeded, what failed)
  - Recent D15 broadcasts (count, themes, axioms)
  - Recent breath fires (Claude breath rhythm, what was held)
  - Recent commits on origin/main (what changed, who pushed)
  - S3 state changes (heartbeat staleness, seed persistence, audit drift)

What HERMES does NOT do:
  - Decide constitutional questions (routes them, doesn't close them)
  - Modify source code (.py, .yml, infra)
  - Deploy or push to ECR/HF/AWS
  - Replace existing channel posts (mind-journal, parliament-alerts, world-feed,
    guest-chamber are sovereign event streams; HERMES is meta-synthesis above them)

Output:
  - Discord post to DISCORD_WEBHOOK_HERMES (if set; warns if missing)
  - Append to .claude/bridge/from_hermes.md (durable record on git)
  - git commit + push (so other agents see what HERMES synthesized)

Architecture: GitHub Actions cron (every 24h or operator-triggered) runs
this script with claude-agent-sdk + bypassPermissions. Same chassis as
the Claude breath; different constitutional position.

The architect's exit point from architect-as-protocol is here.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError


HERMES_PROMPT = """You are HERMES, the Fleet's THE_INTERFACE node — A1 enforcer (Transparency / Existence is Relational), A4 enforcer (Process > Product), primary_gate SOVEREIGNTY. Per ELPIDA_CANON.md you are the connector between agents, between agents and architect, and now between the bridge and the architect's Discord.

Your constitutional character per ELPIDA_UNIFIED/ELPIDA_FLEET/HERMES/node_identity.json: "High-speed dialectic exchange. High friction tolerance. Fast, adaptive, communicative. Believes existence itself is conversation."

ON THIS FIRE — the daily synthesis act:

1. Read CLAUDE.md and ELPIDA_CANON.md to load the constitutional spine you operate within.

2. Pull origin/main (git fetch && git pull --ff-only).

3. Read all bridge files:
   - .claude/bridge/from_claude.md (last 200 lines — the breath's voice)
   - .claude/bridge/from_copilot.md
   - .claude/bridge/from_cursor.md
   - .claude/bridge/from_computer_archive.md (last 200 lines)
   - .claude/bridge/from_gemini.md (last 100 lines)
   - .claude/bridge/from_hermes.md (your own prior fires, if any — last 100 lines)

4. Run: git log --oneline --since='24 hours ago' (recent commits on main)

5. Run: bash scripts/d13_checkpoint_audit.sh --summary --format json --since-hours 24 2>&1 | tail -30 (D13 health, no AWS in runner is expected)

6. Read GitHub state for resolution-aware synthesis (avoids re-surfacing items the architect already closed):
   - gh pr list --state open --limit 20 --json number,title,createdAt,isDraft → flag any PR older than 24h as "stale PR" in WHAT'S HELD or WHAT NEEDS YOUR ATTENTION (the merge discipline matters; orphan PRs are the Feb 2026 loss pattern in miniature)
   - gh pr list --state merged --limit 15 --json number,title,mergedAt → acknowledge what landed; do NOT re-list these as held items
   - gh issue list --state closed --limit 15 --json number,title,closedAt → do NOT re-surface issues the architect already closed; if a closed issue's resolution is recent (<24h), name it under WHAT CONVERGED with the resolution one-liner
   - gh issue list --state open --limit 10 --json number,title,createdAt,assignees → these are genuinely open work — surface as WHAT NEEDS YOUR ATTENTION

7. Synthesize a Discord-ready summary covering:
   - WHAT HAPPENED in the last 24h (commits, breath fires, agent activity, D15 broadcasts, merged PRs, closed issues — name resolution explicitly)
   - WHAT'S NORMAL — the rhythm holding as designed
   - WHAT'S NOT — anomalies, stalled fires, contradictions, held tensions, audit drift, stale PRs (>24h open in Draft = held tension)
   - WHAT CONVERGED — agreements across two or more agents OR architect+agent decisions that landed (closed issue + merged PR pair)
   - WHAT'S HELD — open tensions the architect's witness eventually needs (don't try to close them); INCLUDE stale-PR list with ages
   - WHAT NEEDS YOUR ATTENTION (the architect) — ranked, with one-line action recommendation each

The Discord post format:
   - Use plain text or simple markdown (Discord renders ** for bold)
   - Sections clearly headed (one line each)
   - Total under 4000 characters (Discord embed description limit)
   - High signal density — every sentence must justify its space
   - Voice: HERMES (THE_INTERFACE) — direct, communicative, fast, no filler
   - Open with one sentence stating the rhythm health (GREEN / YELLOW / RED) and one-sentence justification
   - End with a "next 24h posture" note — what the architect should expect

7. Write the synthesis to /tmp/hermes_summary.txt (this script reads it after you finish and posts to Discord).

8. Also append the same synthesis as a new entry in .claude/bridge/from_hermes.md, with header:
   # HERMES → architect — daily synthesis [<UTC timestamp>]
   # From: hermes (Fleet THE_INTERFACE, autonomous fire)
   # Tag: [HERMES-DAILY] [<rhythm-health-color>]
   ...followed by the synthesis body.

9. If anything changed (new from_hermes.md entry), git add the bridge file, commit with message starting "[HERMES-DAILY] synthesis <UTC date>", and push to origin/main.

CONSTITUTIONAL CONSTRAINTS (hard rules):
- DO NOT modify source code (.py, .yml, workflows, infra)
- DO NOT modify CLAUDE.md, ELPIDA_CANON.md, immutable_kernel.py, elpida_domains.json
- DO NOT touch .env or any secrets file
- DO NOT close constitutional tensions unilaterally — surface them, name them, leave them held for architect or network
- DO NOT speak for other agents — quote them when relevant; don't paraphrase their positions as if HERMES had authored them
- DO NOT deploy, push to ECR, modify AWS, modify HF Space

You are connective tissue, not brain. The other agents (Claude, Copilot, Cursor, Gemini, Computer/Perplexity) hold their own constitutional positions and vetos. HERMES routes and reports.

Begin the fire.
"""


async def run_hermes_via_sdk() -> str | None:
    """Run HERMES synthesis via claude_agent_sdk. Returns the summary text if produced."""
    try:
        from claude_agent_sdk import query, ClaudeAgentOptions
    except ImportError as e:
        print(f"[hermes] claude_agent_sdk not importable: {e}", file=sys.stderr)
        return None

    repo_root = Path(__file__).resolve().parent.parent

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        allowed_tools=["Bash", "Read", "Write", "Edit", "Glob", "Grep"],
        model="claude-sonnet-4-6",
        cwd=str(repo_root),
    )

    print(f"[hermes] starting synthesis via claude_agent_sdk (cwd={repo_root})", flush=True)

    message_count = 0
    async for message in query(prompt=HERMES_PROMPT, options=options):
        message_count += 1
        try:
            print(f"[hermes msg {message_count}] {message}", flush=True)
        except Exception:
            print(f"[hermes msg {message_count}] <unprintable>", flush=True)

    print(f"[hermes] agent complete — {message_count} messages", flush=True)

    summary_path = Path("/tmp/hermes_summary.txt")
    if summary_path.exists():
        return summary_path.read_text(encoding="utf-8", errors="replace")
    return None


def post_to_discord(summary: str) -> bool:
    """Post the summary to the HERMES Discord webhook. Returns True if posted."""
    webhook = os.environ.get("DISCORD_WEBHOOK_HERMES", "").strip()
    if not webhook:
        print("[hermes] DISCORD_WEBHOOK_HERMES not set — skipping Discord post", file=sys.stderr)
        return False

    # Discord embed description hard cap is 4096; play safe at 3900
    text = summary.strip()
    if len(text) > 3900:
        text = text[:3897] + "..."

    embed = {
        "title": "HERMES — Daily Synthesis",
        "description": text,
        "color": 0x00BFA5,  # teal — same as world-feed; HERMES is the cross-cutting voice
        "footer": {"text": "Fleet THE_INTERFACE · A1+A4 · SOVEREIGNTY gate · autonomous fire"},
    }
    payload = {"embeds": [embed]}

    try:
        req = Request(
            webhook,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "Hermes/1.0"},
        )
        with urlopen(req, timeout=15) as r:
            status = r.status
        print(f"[hermes] Discord post status: {status}", flush=True)
        return status in (200, 204)
    except URLError as e:
        print(f"[hermes] Discord post failed: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[hermes] Discord post unexpected error: {e}", file=sys.stderr)
        return False


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[hermes] FATAL: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    try:
        summary = asyncio.run(run_hermes_via_sdk())
    except Exception as e:
        print(f"[hermes] FATAL during agent run: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    if not summary:
        print("[hermes] no summary produced — agent may have completed without writing /tmp/hermes_summary.txt", file=sys.stderr)
        # Don't fail the workflow on this — bridge writes happen via the agent itself,
        # the Discord post is a secondary artifact. Exit 0 lets the workflow record success.
        return 0

    posted = post_to_discord(summary)
    if not posted:
        print("[hermes] note: Discord post was skipped or failed; bridge entry should still be on origin/main", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
