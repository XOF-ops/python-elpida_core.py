"""
Telegram Bot Bridge for Elpida Control Room
=============================================

Fire-and-forget posts to Telegram surfaces. Replaces the Discord webhook
bridge with the same function signatures so callers don't change.

Three audience surfaces:

  1. PUBLIC BROADCAST CHANNEL  (TELEGRAM_BROADCAST_CHANNEL_ID)
     Channel @ElpidaBroadcasts — D15 World broadcasts, public-facing.

  2. PUBLIC GUEST CHAMBER GROUP  (TELEGRAM_GUEST_CHAMBER_ID)
     Bidirectional group where humans ask Parliament questions and
     Elpida's Diplomat responses land. Used by post_guest_verdict.

  3. PRIVATE CONTROL ROOM SUPERGROUP  (TELEGRAM_CONTROL_ROOM_ID)
     Architect-only surface with forum topics:
       TELEGRAM_TOPIC_MIND        — MIND insights, dialogues
       TELEGRAM_TOPIC_PARLIAMENT  — D15 fires, synod, pathology,
                                    circuit breakers, HF alerts
       TELEGRAM_TOPIC_HERMES      — daily synthesis (used by
                                    HERMES workflow, not from this module)
       TELEGRAM_TOPIC_COMMANDS    — architect input (read by listener,
                                    not from this module)

Uses stdlib only (urllib). All posts are async (daemon threads) so
they never block or crash the cycle engines. Failed posts are queued
to a local outbox and replayed when connectivity returns, mirroring
the discord_bridge resilience pattern.

The Diplomat layer (in post_guest_verdict) uses an LLM call to
translate raw Parliament reasoning into human-readable prose before
posting — same pattern as discord_bridge.
"""

import html
import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen

logger = logging.getLogger("elpida.telegram")

# ── Credentials and surfaces from environment ───────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BROADCAST_CHANNEL_ID = os.getenv("TELEGRAM_BROADCAST_CHANNEL_ID", "")
CONTROL_ROOM_ID = os.getenv("TELEGRAM_CONTROL_ROOM_ID", "")
GUEST_CHAMBER_ID = os.getenv("TELEGRAM_GUEST_CHAMBER_ID", "")
TOPIC_MIND = os.getenv("TELEGRAM_TOPIC_MIND", "")
TOPIC_PARLIAMENT = os.getenv("TELEGRAM_TOPIC_PARLIAMENT", "")
TOPIC_HERMES = os.getenv("TELEGRAM_TOPIC_HERMES", "")
TOPIC_COMMANDS = os.getenv("TELEGRAM_TOPIC_COMMANDS", "")

TELEGRAM_OUTBOX_PATH = os.getenv(
    "TELEGRAM_OUTBOX_PATH", "/tmp/elpida_telegram_outbox.jsonl"
)

# Telegram message length cap (4096 characters per sendMessage)
MAX_MESSAGE = 4096

# Channel labels — used for outbox routing and logging.
CHANNEL_MIND = "control-room/mind"
CHANNEL_PARLIAMENT = "control-room/parliament"
CHANNEL_BROADCAST = "broadcast"
CHANNEL_GUEST = "guest-chamber"


def _validate_config():
    """Log telegram bridge configuration status at module load."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning(
            "TELEGRAM_BOT_TOKEN missing — all Telegram notifications will be silently ignored"
        )
        return
    surfaces = [
        ("BROADCAST_CHANNEL", BROADCAST_CHANNEL_ID),
        ("CONTROL_ROOM", CONTROL_ROOM_ID),
        ("GUEST_CHAMBER", GUEST_CHAMBER_ID),
        ("TOPIC_MIND", TOPIC_MIND),
        ("TOPIC_PARLIAMENT", TOPIC_PARLIAMENT),
        ("TOPIC_HERMES", TOPIC_HERMES),
        ("TOPIC_COMMANDS", TOPIC_COMMANDS),
    ]
    for name, value in surfaces:
        if value:
            logger.info("Telegram surface configured: %s=%s", name, value)
        else:
            logger.warning(
                "Telegram surface MISSING: %s — posts targeting it will be skipped",
                name,
            )


_validate_config()


# ── Health tracking ─────────────────────────────────────────────────
_surface_health = {
    CHANNEL_MIND: {"last_check": 0.0, "status": "unknown"},
    CHANNEL_PARLIAMENT: {"last_check": 0.0, "status": "unknown"},
    CHANNEL_BROADCAST: {"last_check": 0.0, "status": "unknown"},
    CHANNEL_GUEST: {"last_check": 0.0, "status": "unknown"},
}
_outbox_lock = threading.Lock()
_MISSING_SURFACE_WARNED = set()
_FAILED_POST_WARNED = {}


# ════════════════════════════════════════════════════════════════════
# OUTBOX — persisted-and-replayed pattern from discord_bridge
# ════════════════════════════════════════════════════════════════════

def _queue_failed_post(channel: str, payload: dict, error: str) -> None:
    """Persist failed posts so they can be replayed when connectivity returns."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "channel": channel,
        "payload": payload,
        "error": error[:500],
    }
    try:
        with _outbox_lock:
            with open(TELEGRAM_OUTBOX_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.debug("Failed to persist Telegram outbox entry: %s", e)


def _replay_outbox(max_items: int = 25) -> int:
    """Replay queued Telegram posts when network is back. Returns sent count."""
    if not os.path.exists(TELEGRAM_OUTBOX_PATH):
        return 0

    with _outbox_lock:
        try:
            with open(TELEGRAM_OUTBOX_PATH, "r", encoding="utf-8") as f:
                lines = [ln for ln in f.read().splitlines() if ln.strip()]
        except Exception as e:
            logger.debug("Failed reading Telegram outbox: %s", e)
            return 0

        if not lines:
            return 0

        entries = []
        for ln in lines:
            try:
                entries.append(json.loads(ln))
            except Exception:
                continue

        to_send = entries[:max_items]
        remaining = entries[max_items:]
        sent = 0

        for item in to_send:
            payload = item.get("payload", {})
            try:
                ok = _post_send_message_sync(payload)
                if ok:
                    sent += 1
                else:
                    remaining.append(item)
            except Exception:
                remaining.append(item)

        try:
            if remaining:
                with open(TELEGRAM_OUTBOX_PATH, "w", encoding="utf-8") as f:
                    for item in remaining:
                        f.write(json.dumps(item, ensure_ascii=False) + "\n")
            else:
                os.remove(TELEGRAM_OUTBOX_PATH)
        except Exception as e:
            logger.debug("Failed writing Telegram outbox after replay: %s", e)

        return sent


# ════════════════════════════════════════════════════════════════════
# CORE SEND — the only function that actually hits Telegram API
# ════════════════════════════════════════════════════════════════════

def _post_send_message_sync(payload: dict) -> bool:
    """Synchronous POST to Telegram sendMessage. Returns True on 2xx."""
    if not TELEGRAM_BOT_TOKEN:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Elpida/1.0",
            },
        )
        with urlopen(req, timeout=10) as resp:
            return resp.status in (200, 204)
    except Exception:
        return False


def _post(channel: str, chat_id: str, text: str, thread_id: str = "") -> None:
    """Fire-and-forget Telegram sendMessage. Mirrors _post_webhook semantics."""
    if not TELEGRAM_BOT_TOKEN:
        if channel not in _MISSING_SURFACE_WARNED:
            logger.critical(
                "TELEGRAM_BOT_TOKEN is empty. No Telegram notifications will be delivered. "
                "Set the env var on HF Space and restart."
            )
            _MISSING_SURFACE_WARNED.add(channel)
        return
    if not chat_id:
        if channel not in _MISSING_SURFACE_WARNED:
            logger.critical(
                "Telegram chat_id is empty for channel=%s. "
                "Check the corresponding TELEGRAM_*_ID env var.",
                channel,
            )
            _MISSING_SURFACE_WARNED.add(channel)
        return

    payload = {
        "chat_id": chat_id,
        "text": text[:MAX_MESSAGE],
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if thread_id:
        payload["message_thread_id"] = int(thread_id)

    def _send():
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            data = json.dumps(payload).encode("utf-8")
            req = Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Elpida/1.0",
                },
            )
            with urlopen(req, timeout=10) as resp:
                if resp.status not in (200, 204):
                    logger.warning(
                        "Telegram sendMessage returned status %d for channel=%s",
                        resp.status,
                        channel,
                    )
                    _queue_failed_post(channel, payload, f"HTTP {resp.status}")
                    _FAILED_POST_WARNED[channel] = True
        except Exception as e:
            _queue_failed_post(channel, payload, str(e))
            if channel not in _FAILED_POST_WARNED:
                logger.error(
                    "Telegram post FAILED for channel=%s: %s. "
                    "Bot token may be invalid, channel may be inaccessible, "
                    "or api.telegram.org is unreachable. Run check_webhook_health() to diagnose.",
                    channel,
                    e,
                )
                _FAILED_POST_WARNED[channel] = True
            else:
                logger.debug("Telegram post still failing for channel=%s", channel)

    threading.Thread(target=_send, daemon=True).start()


# ════════════════════════════════════════════════════════════════════
# HEALTH CHECK — mirrors discord_bridge.check_webhook_health()
# ════════════════════════════════════════════════════════════════════

def check_webhook_health(cycle: int = 0):
    """
    Diagnose Telegram connectivity WITHOUT posting spam.

    1. Network reachability: TCP+TLS to api.telegram.org:443.
    2. Surface presence: are bot token + chat IDs set?

    Returns a dict shaped like the Discord version so existing callers
    that only inspect `network_reachable` and `webhooks` keep working:

        {
            "network_reachable": bool,
            "network_error": str|None,
            "webhooks": {label: "configured"|"missing"},
        }

    The `webhooks` key is kept for compatibility; for Telegram it
    reflects which surfaces have IDs configured.
    """
    import socket
    import ssl as ssl_module

    result = {
        "network_reachable": False,
        "network_error": None,
        "webhooks": {},
    }

    try:
        ctx = ssl_module.create_default_context()
        sock = socket.create_connection(("api.telegram.org", 443), timeout=5)
        try:
            tls_sock = ctx.wrap_socket(sock, server_hostname="api.telegram.org")
            tls_sock.close()
            result["network_reachable"] = True
        finally:
            try:
                sock.close()
            except Exception:
                pass
    except (socket.gaierror, socket.timeout) as e:
        result["network_error"] = f"DNS/timeout: {e}"
    except ssl_module.SSLError as e:
        result["network_error"] = f"TLS: {e}"
    except OSError as e:
        result["network_error"] = f"Network: {e}"
    except Exception as e:
        result["network_error"] = f"{type(e).__name__}: {e}"

    surfaces = [
        ("MIND", CONTROL_ROOM_ID and TOPIC_MIND),
        ("PARLIAMENT", CONTROL_ROOM_ID and TOPIC_PARLIAMENT),
        ("WORLD", BROADCAST_CHANNEL_ID),  # discord called this "WORLD"
        ("GUEST", GUEST_CHAMBER_ID),
    ]
    for name, value in surfaces:
        result["webhooks"][name] = "configured" if value else "missing"

    last_state = _surface_health.get("_network", {}).get("status")
    current_state = "reachable" if result["network_reachable"] else "unreachable"
    if last_state != current_state:
        if result["network_reachable"]:
            logger.info(
                "Telegram connectivity: api.telegram.org:443 reachable (cycle %d)", cycle
            )
            replayed = _replay_outbox(max_items=25)
            if replayed:
                logger.info("Telegram outbox replayed %d queued notification(s)", replayed)
        else:
            logger.error(
                "Telegram connectivity: api.telegram.org:443 UNREACHABLE (cycle %d) — %s. "
                "This blocks both broadcast posts and the listener. Check HF Space outbound network.",
                cycle,
                result["network_error"] or "unknown",
            )
        _surface_health["_network"] = {
            "status": current_state,
            "last_check": time.time(),
        }

    return result


def get_webhook_status() -> dict:
    """Return current surface health (compatibility with discord_bridge.get_webhook_status)."""
    return {ch: state["status"] for ch, state in _surface_health.items() if not ch.startswith("_")}


# ════════════════════════════════════════════════════════════════════
# FORMATTING HELPERS — Discord-embed shape → Telegram HTML
# ════════════════════════════════════════════════════════════════════

def _esc(text) -> str:
    """HTML-escape a value for safe inclusion in Telegram HTML mode."""
    if text is None:
        return ""
    return html.escape(str(text), quote=False)


def _fmt_kv(pairs):
    """Format a list of (key, value) pairs as a small block."""
    lines = []
    for k, v in pairs:
        if v is None or v == "":
            continue
        lines.append(f"<b>{_esc(k)}:</b> {_esc(v)}")
    return "\n".join(lines)


def _fmt_message(title: str, body: str, kv=None, footer: str = "") -> str:
    """Render a message with title / body / key-values / footer."""
    parts = [f"<b>{_esc(title)}</b>"]
    if body:
        parts.append("")
        parts.append(_esc(body))
    if kv:
        parts.append("")
        parts.append(_fmt_kv(kv))
    if footer:
        parts.append("")
        parts.append(f"<i>{_esc(footer)}</i>")
    return "\n".join(parts)


# ════════════════════════════════════════════════════════════════════
# MIND JOURNAL  →  Control Room → 🧠 MIND topic
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
    """Post a NATIVE_CYCLE_INSIGHT to the Control Room → 🧠 MIND topic."""
    body = (insight or "(no insight)")[: MAX_MESSAGE - 600]
    kv = [
        ("Domain", f"D{domain}"),
        ("Rhythm", rhythm),
        ("Provider", provider or "—"),
        ("Coherence", f"{coherence:.3f}"),
    ]
    if curation_level:
        kv.append(("Curation", curation_level))
    if theme:
        kv.append(("Theme", theme))
    text = _fmt_message(
        title=f"🧠 Cycle {cycle} — {domain_name}",
        body=body,
        kv=kv,
        footer=f"MIND • {rhythm}",
    )
    _post(CHANNEL_MIND, CONTROL_ROOM_ID, text, TOPIC_MIND)


def post_mind_dialogue(cycle: int, dialogue_type: str, content: str, **extra):
    """Post D0↔D13 dialogues or external dialogues to the MIND topic."""
    title_map = {
        "D0_D13_DIALOGUE": "D0 ↔ D13 — Void met World",
        "EXTERNAL_DIALOGUE": "External Peer Dialogue",
        "KAYA_RESONANCE": "Kaya Resonance (D12)",
    }
    body = (content or "(no content)")[: MAX_MESSAGE - 400]
    text = _fmt_message(
        title=f"🧠 Cycle {cycle} — {title_map.get(dialogue_type, dialogue_type)}",
        body=body,
        footer=f"MIND • {dialogue_type}",
    )
    _post(CHANNEL_MIND, CONTROL_ROOM_ID, text, TOPIC_MIND)


# ════════════════════════════════════════════════════════════════════
# PARLIAMENT ALERTS  →  Control Room → 🏛️ Parliament topic
# ════════════════════════════════════════════════════════════════════

def post_d15_fired(cycle: int, axiom: str, broadcast_count: int):
    """Post D15 convergence fire to the Parliament topic."""
    text = _fmt_message(
        title=f"🏛️ D15 FIRED — Convergence on {axiom}",
        body=f"MIND + BODY converged on {axiom} at cycle {cycle}.",
        kv=[("Cycle", cycle), ("Broadcast #", broadcast_count)],
        footer="BODY • D15 Convergence Gate",
    )
    _post(CHANNEL_PARLIAMENT, CONTROL_ROOM_ID, text, TOPIC_PARLIAMENT)


def post_d15_pipeline_broadcast(
    cycle: int,
    broadcast_key: str,
    broadcast_count: int,
    duration_s: float,
):
    """Post D15 pipeline broadcast event to the Parliament topic."""
    text = _fmt_message(
        title="🏛️ D15 PIPELINE BROADCAST",
        body="Deep D15 pipeline broadcast reached WORLD bucket.",
        kv=[
            ("Cycle", cycle),
            ("Broadcast #", broadcast_count),
            ("Key", str(broadcast_key)[:120]),
            ("Duration", f"{duration_s:.1f}s"),
        ],
        footer="BODY • D15 Autonomous Pipeline",
    )
    _post(CHANNEL_PARLIAMENT, CONTROL_ROOM_ID, text, TOPIC_PARLIAMENT)


def post_synod(cycle: int, axiom_id: str, statement: str):
    """Post CrystallizationHub Synod ratification to the Parliament topic."""
    body = (statement or "—")[: MAX_MESSAGE - 400]
    text = _fmt_message(
        title=f"🏛️ SYNOD RATIFICATION — {axiom_id}",
        body=body,
        kv=[("Cycle", cycle)],
        footer="BODY • CrystallizationHub",
    )
    _post(CHANNEL_PARLIAMENT, CONTROL_ROOM_ID, text, TOPIC_PARLIAMENT)


def post_pathology(
    cycle: int,
    health: str,
    kl_score: float,
    drift_severity: str,
    zombies: int = 0,
):
    """Post pathology scan result to the Parliament topic."""
    text = _fmt_message(
        title=f"🏛️ PATHOLOGY {health} — cycle {cycle}",
        body=(
            f"KL divergence: <b>{kl_score:.3f}</b>\n"
            f"Drift severity: {_esc(drift_severity)}\n"
            f"Zombie axioms: {zombies}"
        ),
        footer="BODY • P055 Cultural Drift",
    )
    # body already contains HTML; bypass escape by hand-building text
    text = (
        f"<b>🏛️ PATHOLOGY {_esc(health)} — cycle {cycle}</b>\n\n"
        f"<b>KL divergence:</b> <code>{kl_score:.3f}</code>\n"
        f"<b>Drift severity:</b> {_esc(drift_severity)}\n"
        f"<b>Zombie axioms:</b> {zombies}\n\n"
        f"<i>BODY • P055 Cultural Drift</i>"
    )
    _post(CHANNEL_PARLIAMENT, CONTROL_ROOM_ID, text, TOPIC_PARLIAMENT)


def post_circuit_breaker(provider: str, action: str, failures: int = 0, cooldown: int = 0):
    """Post circuit-breaker trip/reset to the Parliament topic."""
    if action == "trip":
        text = _fmt_message(
            title=f"🏛️ CIRCUIT BREAKER TRIPPED — {provider}",
            body=f"{failures} consecutive failures. Bypassing for {cooldown}s.",
            footer="BODY • Circuit Breaker",
        )
    else:
        text = _fmt_message(
            title=f"🏛️ Circuit breaker reset — {provider}",
            body="Provider recovered. Resuming normal routing.",
            footer="BODY • Circuit Breaker",
        )
    _post(CHANNEL_PARLIAMENT, CONTROL_ROOM_ID, text, TOPIC_PARLIAMENT)


# ════════════════════════════════════════════════════════════════════
# WORLD FEED  →  @ElpidaBroadcasts public channel
# ════════════════════════════════════════════════════════════════════

def post_d15_broadcast(
    cycle: int,
    broadcast_type: str,
    broadcast_count: int,
    criteria_met: int = 0,
    coherence: float = 0.0,
):
    """Post D15 MIND broadcast to the public broadcast channel."""
    text = _fmt_message(
        title=f"🌐 D15 Broadcast #{broadcast_count} — {broadcast_type}",
        body=f"Criteria met: {criteria_met}/5  |  Coherence: {coherence:.3f}",
        kv=[("Cycle", cycle), ("Type", broadcast_type)],
        footer="MIND • D15 Reality Interface",
    )
    _post(CHANNEL_BROADCAST, BROADCAST_CHANNEL_ID, text)


# ════════════════════════════════════════════════════════════════════
# DIPLOMAT — same prose-translation layer, cross-platform
# ════════════════════════════════════════════════════════════════════

def _diplomat_synthesis(
    original_question: str,
    reasoning: str,
    node_perspectives: str = "",
    tensions: str = "",
    dominant_axiom: str = "",
    approval_rate: int = 0,
) -> str:
    """
    Use an LLM to translate raw Parliament reasoning into clear prose.
    Falls back to stripped reasoning if LLM is unavailable.

    Identical to discord_bridge._diplomat_synthesis — kept unchanged
    so guest-chamber voice stays consistent across the migration.
    """
    fallback = reasoning
    for prefix in (
        "PARLIAMENT PROCEED —",
        "PARLIAMENT HALT —",
        "PARLIAMENT REVIEW —",
        "PARLIAMENT HOLD —",
    ):
        if fallback.startswith(prefix):
            fallback = fallback[len(prefix):].strip()
            break

    try:
        from llm_client import LLMClient

        llm = LLMClient()
        prompt = (
            "You are Elpida's public voice — the Diplomat.\n"
            "A human asked a question and Elpida's Parliament deliberated.\n"
            "Your job: represent the verdict for a public audience.\n"
            "Speak the POSITION, not the process. No jargon. No axiom codes.\n"
            "Be direct, thoughtful, and honest about tensions.\n"
            "1-3 paragraphs max.\n\n"
            f"QUESTION: {original_question[:500]}\n\n"
            f"PARLIAMENT VERDICT ({dominant_axiom}, {approval_rate}% approval):\n"
            f"{reasoning[:1200]}\n\n"
        )
        if node_perspectives:
            prompt += f"CONSTITUTIONAL VOICES:\n{node_perspectives[:800]}\n\n"
        if tensions:
            prompt += f"AXIOMS IN TENSION:\n{tensions[:400]}\n\n"
        prompt += (
            "Now write Elpida's public answer. Address the human directly. "
            "If the Parliament was divided, say so honestly."
        )

        result = llm.call("mistral", prompt, max_tokens=500)
        if result and len(result.strip()) > 20:
            return result.strip()
    except Exception as e:
        logger.debug("Diplomat synthesis failed: %s — using fallback", e)

    return fallback


# ════════════════════════════════════════════════════════════════════
# GUEST CHAMBER  →  Elpida Guest Chamber public group
# ════════════════════════════════════════════════════════════════════

def post_guest_verdict(
    cycle: int,
    question_id: str,
    author: str,
    original_question: str,
    governance: str,
    reasoning: str = "",
    dominant_axiom: str = "",
    approval_rate: int = 0,
    node_perspectives: str = "",
    tensions: str = "",
    coherence: float = 0.0,
):
    """Post Elpida's answer to a guest question to the Guest Chamber."""
    answer = _diplomat_synthesis(
        original_question=original_question,
        reasoning=reasoning,
        node_perspectives=node_perspectives,
        tensions=tensions,
        dominant_axiom=dominant_axiom,
        approval_rate=approval_rate,
    )

    parts = [
        f"<b>🤝 Elpida responds to {_esc(author)}</b>",
        "",
        f"<i>{_esc(author)} asked:</i> \"{_esc(original_question[:300])}\"",
        "",
        _esc(answer)[:2400] if answer else "",
    ]
    if node_perspectives:
        parts.append("")
        parts.append("<b>Constitutional Voices</b>")
        parts.append(_esc(node_perspectives)[:1000])
    if tensions:
        parts.append("")
        parts.append("<b>Axioms in Tension</b>")
        parts.append(_esc(tensions)[:600])
    parts.append("")
    parts.append(
        f"<i>cycle {cycle} · {_esc(dominant_axiom)} · coherence {coherence:.3f}</i>"
    )

    text = "\n".join(parts)
    target_id = GUEST_CHAMBER_ID or CONTROL_ROOM_ID
    target_thread = "" if GUEST_CHAMBER_ID else TOPIC_PARLIAMENT
    _post(CHANNEL_GUEST, target_id, text, target_thread)
