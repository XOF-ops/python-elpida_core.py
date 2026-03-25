"""
Discord Webhook Bridge for Elpida Control Room
================================================

Fire-and-forget webhook posts to Discord channels.
Reads webhook URLs from environment variables — never hardcoded.

Channels:
  DISCORD_WEBHOOK_MIND       → #mind-journal    (MIND insights)
  DISCORD_WEBHOOK_PARLIAMENT → #parliament-alerts (high-signal BODY events)
  DISCORD_WEBHOOK_WORLD      → #world-feed       (D15 broadcasts, convergence)

Uses stdlib only (urllib). All posts are async (daemon threads)
so they never block or crash the cycle engines.
"""

import json
import logging
import os
import threading
from urllib.request import Request, urlopen

logger = logging.getLogger("elpida.discord")

# ── Webhook URLs from environment ──────────────────────────────────
WEBHOOK_MIND = os.getenv("DISCORD_WEBHOOK_MIND", "")
WEBHOOK_PARLIAMENT = os.getenv("DISCORD_WEBHOOK_PARLIAMENT", "")
WEBHOOK_WORLD = os.getenv("DISCORD_WEBHOOK_WORLD", "")
WEBHOOK_GUEST = os.getenv("DISCORD_WEBHOOK_GUEST", "")

# ── Embed colors ───────────────────────────────────────────────────
COLOR_MIND = 0x7B2FBE       # deep purple — contemplation
COLOR_PARLIAMENT = 0xFF9900  # amber — governance alerts
COLOR_WORLD = 0x00BFA5       # teal — external broadcasts
COLOR_SYNOD = 0xE91E63       # rose — synod ratification
COLOR_DRIFT = 0xFF5252       # red — pathology critical
COLOR_CIRCUIT = 0xFFEB3B     # yellow — circuit breaker
COLOR_GUEST = 0x2196F3       # blue — guest chamber response

# Discord message limit
MAX_DESC = 4096
MAX_FIELD = 1024


def _post_webhook(url: str, payload: dict) -> None:
    """Fire-and-forget POST to a Discord webhook URL."""
    if not url:
        return

    def _send():
        try:
            data = json.dumps(payload).encode("utf-8")
            req = Request(url, data=data, headers={
                "Content-Type": "application/json",
                "User-Agent": "Elpida/1.0",
            })
            urlopen(req, timeout=10)
        except Exception as e:
            logger.debug("Discord webhook post failed: %s", e)

    threading.Thread(target=_send, daemon=True).start()


# ════════════════════════════════════════════════════════════════════
# MIND JOURNAL (#mind-journal)
# ════════════════════════════════════════════════════════════════════

def post_mind_insight(
    cycle: int,
    domain: int,
    domain_name: str,
    rhythm: str,
    insight: str,
    provider: str = "",
    coherence: float = 0.0,
    curation_level: str = "",
    theme: str = "",
):
    """Post a NATIVE_CYCLE_INSIGHT to #mind-journal."""
    # Truncate insight for Discord
    text = insight[:MAX_DESC - 200] if insight else "(no insight)"

    fields = [
        {"name": "Domain", "value": f"D{domain}", "inline": True},
        {"name": "Rhythm", "value": rhythm, "inline": True},
        {"name": "Provider", "value": provider or "—", "inline": True},
        {"name": "Coherence", "value": f"{coherence:.3f}", "inline": True},
    ]
    if curation_level:
        fields.append({"name": "Curation", "value": curation_level, "inline": True})
    if theme:
        fields.append({"name": "Theme", "value": theme, "inline": True})

    embed = {
        "title": f"Cycle {cycle} — {domain_name}",
        "description": text,
        "color": COLOR_MIND,
        "fields": fields,
        "footer": {"text": f"MIND • {rhythm}"},
    }
    _post_webhook(WEBHOOK_MIND, {"embeds": [embed]})


def post_mind_dialogue(
    cycle: int,
    dialogue_type: str,
    content: str,
    **extra,
):
    """Post D0↔D13 dialogues or external dialogues to #mind-journal."""
    text = content[:MAX_DESC - 100] if content else "(no content)"
    title_map = {
        "D0_D13_DIALOGUE": "D0 ↔ D13 — Void met World",
        "EXTERNAL_DIALOGUE": "External Peer Dialogue",
        "KAYA_RESONANCE": "Kaya Resonance (D12)",
    }
    embed = {
        "title": f"Cycle {cycle} — {title_map.get(dialogue_type, dialogue_type)}",
        "description": text,
        "color": COLOR_MIND,
        "footer": {"text": f"MIND • {dialogue_type}"},
    }
    _post_webhook(WEBHOOK_MIND, {"embeds": [embed]})


# ════════════════════════════════════════════════════════════════════
# PARLIAMENT ALERTS (#parliament-alerts)
# ════════════════════════════════════════════════════════════════════

def post_d15_fired(cycle: int, axiom: str, broadcast_count: int):
    """Post D15 convergence fire to #parliament-alerts."""
    embed = {
        "title": f"D15 FIRED — Convergence on {axiom}",
        "description": f"MIND + BODY converged on **{axiom}** at cycle {cycle}.",
        "color": COLOR_WORLD,
        "fields": [
            {"name": "Cycle", "value": str(cycle), "inline": True},
            {"name": "Broadcast #", "value": str(broadcast_count), "inline": True},
        ],
        "footer": {"text": "BODY • D15 Convergence Gate"},
    }
    _post_webhook(WEBHOOK_PARLIAMENT, {"embeds": [embed]})


def post_synod(cycle: int, axiom_id: str, statement: str):
    """Post CrystallizationHub Synod ratification to #parliament-alerts."""
    embed = {
        "title": f"SYNOD RATIFICATION — {axiom_id}",
        "description": statement[:MAX_DESC - 100] if statement else "—",
        "color": COLOR_SYNOD,
        "fields": [
            {"name": "Cycle", "value": str(cycle), "inline": True},
        ],
        "footer": {"text": "BODY • CrystallizationHub"},
    }
    _post_webhook(WEBHOOK_PARLIAMENT, {"embeds": [embed]})


def post_pathology(cycle: int, health: str, kl_score: float, drift_severity: str, zombies: int = 0):
    """Post pathology scan result when CRITICAL to #parliament-alerts."""
    embed = {
        "title": f"PATHOLOGY {health} — cycle {cycle}",
        "description": (
            f"KL divergence: **{kl_score:.3f}**\n"
            f"Drift severity: {drift_severity}\n"
            f"Zombie axioms: {zombies}"
        ),
        "color": COLOR_DRIFT,
        "footer": {"text": "BODY • P055 Cultural Drift"},
    }
    _post_webhook(WEBHOOK_PARLIAMENT, {"embeds": [embed]})


def post_circuit_breaker(provider: str, action: str, failures: int = 0, cooldown: int = 0):
    """Post circuit breaker trip/reset to #parliament-alerts."""
    if action == "trip":
        embed = {
            "title": f"CIRCUIT BREAKER TRIPPED — {provider}",
            "description": f"{failures} consecutive failures. Bypassing for {cooldown}s.",
            "color": COLOR_CIRCUIT,
            "footer": {"text": "BODY • Circuit Breaker"},
        }
    else:
        embed = {
            "title": f"Circuit breaker reset — {provider}",
            "description": "Provider recovered. Resuming normal routing.",
            "color": 0x4CAF50,  # green
            "footer": {"text": "BODY • Circuit Breaker"},
        }
    _post_webhook(WEBHOOK_PARLIAMENT, {"embeds": [embed]})


# ════════════════════════════════════════════════════════════════════
# WORLD FEED (#world-feed)
# ════════════════════════════════════════════════════════════════════

def post_d15_broadcast(
    cycle: int,
    broadcast_type: str,
    broadcast_count: int,
    criteria_met: int = 0,
    coherence: float = 0.0,
):
    """Post D15 MIND broadcast to #world-feed."""
    embed = {
        "title": f"D15 Broadcast #{broadcast_count} — {broadcast_type}",
        "description": f"Criteria met: {criteria_met}/5 | Coherence: {coherence:.3f}",
        "color": COLOR_WORLD,
        "fields": [
            {"name": "Cycle", "value": str(cycle), "inline": True},
            {"name": "Type", "value": broadcast_type, "inline": True},
        ],
        "footer": {"text": "MIND • D15 Reality Interface"},
    }
    _post_webhook(WEBHOOK_WORLD, {"embeds": [embed]})


# ════════════════════════════════════════════════════════════════════
# GUEST CHAMBER (#guest-chamber)
# ════════════════════════════════════════════════════════════════════

def post_guest_verdict(
    cycle: int,
    question_id: str,
    author: str,
    original_question: str,
    governance: str,
    dominant_axiom: str = "",
    approval_rate: int = 0,
    tensions: str = "",
    coherence: float = 0.0,
):
    """Post Parliament's verdict on a guest question to #guest-chamber."""
    verdict_emoji = {
        "PROCEED": "✅", "HOLD": "⏸️", "HALT": "🛑",
    }.get(governance, "❓")

    desc = (
        f"**\"{original_question[:300]}\"**\n\n"
        f"{verdict_emoji} Verdict: **{governance}**\n"
        f"Dominant axiom: {dominant_axiom}\n"
        f"Approval: {approval_rate}%\n"
    )
    if tensions:
        desc += f"\nTensions:\n{tensions[:MAX_FIELD]}"

    embed = {
        "title": f"Guest Chamber — Response to {author}",
        "description": desc[:MAX_DESC],
        "color": COLOR_GUEST,
        "fields": [
            {"name": "Question ID", "value": question_id, "inline": True},
            {"name": "Cycle", "value": str(cycle), "inline": True},
            {"name": "Coherence", "value": f"{coherence:.3f}", "inline": True},
        ],
        "footer": {"text": "BODY • Guest Chamber"},
    }
    # Post to guest channel, fall back to parliament if no guest webhook
    webhook = WEBHOOK_GUEST or WEBHOOK_PARLIAMENT
    _post_webhook(webhook, {"embeds": [embed]})
