"""
Telegram Guest Listener — Reads Guest Chamber Messages into S3
================================================================

Lightweight long-polling listener that watches the Telegram Guest
Chamber group for human questions, posts them to S3 via
guest_chamber.post_question(), and reacts with 🏛️ to confirm receipt.
The BODY's GuestChamberFeed picks them up within 30 seconds and
deliberates.

Mirrors the Discord guest_listener semantics:
  - Ignores its own messages (the bot)
  - Ignores other bots' messages
  - Only listens in the configured Guest Chamber chat
  - Empty messages and stickers/photos with no caption are ignored
  - /start and /help commands get a help reply, not a question route

Runs as a background daemon thread inside the HF Space process.
Requires TELEGRAM_BOT_TOKEN and TELEGRAM_GUEST_CHAMBER_ID env vars.

Bot privacy mode: this listener works in either mode, but to receive
all human messages in the group (rather than only mentions/replies),
the bot's privacy must be DISABLED via BotFather:
    /setprivacy → @ElpidaAIbot → Disable
"""

import json
import logging
import os
import threading
import time
from typing import Optional
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger("elpida.telegram_listener")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GUEST_CHAMBER_ID = os.getenv("TELEGRAM_GUEST_CHAMBER_ID", "")
LONG_POLL_TIMEOUT = int(os.getenv("TELEGRAM_LONG_POLL_TIMEOUT", "25"))

# ── Internal state ──────────────────────────────────────────────────
_offset_path = os.getenv(
    "TELEGRAM_LISTENER_OFFSET_PATH", "/tmp/elpida_telegram_offset"
)
_listener_thread: Optional[threading.Thread] = None
_BOT_USER_ID: Optional[int] = None  # populated on first run via getMe


# ════════════════════════════════════════════════════════════════════
# OFFSET PERSISTENCE — survive restart without replaying old questions
# ════════════════════════════════════════════════════════════════════

def _load_offset() -> int:
    try:
        with open(_offset_path, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def _save_offset(offset: int) -> None:
    try:
        with open(_offset_path, "w", encoding="utf-8") as f:
            f.write(str(offset))
    except Exception as e:
        logger.debug("Failed to persist Telegram listener offset: %s", e)


# ════════════════════════════════════════════════════════════════════
# TELEGRAM API HELPERS — stdlib only
# ════════════════════════════════════════════════════════════════════

def _api(method: str, params: Optional[dict] = None, timeout: int = 30) -> dict:
    """Call Telegram Bot API; return parsed JSON or {} on failure."""
    if not TELEGRAM_BOT_TOKEN:
        return {}
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    if params:
        data = urlencode(params).encode("utf-8")
        req = Request(url, data=data, method="POST")
    else:
        req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.debug("Telegram API %s failed: %s", method, e)
        return {}


def _get_me() -> Optional[int]:
    """Return the bot's own user ID, used to filter self-messages."""
    result = _api("getMe", timeout=10)
    if result.get("ok"):
        return result["result"].get("id")
    return None


def _get_updates(offset: int) -> list:
    """Long-poll for new updates. Returns the list (may be empty)."""
    params = {
        "offset": offset,
        "timeout": LONG_POLL_TIMEOUT,
        "allowed_updates": json.dumps(["message"]),
    }
    result = _api("getUpdates", params=params, timeout=LONG_POLL_TIMEOUT + 10)
    if result.get("ok"):
        return result.get("result") or []
    return []


def _react(chat_id, message_id: int, emoji: str) -> None:
    """Add an emoji reaction to a message (Telegram setMessageReaction)."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": json.dumps([{"type": "emoji", "emoji": emoji}]),
    }
    _api("setMessageReaction", params=payload, timeout=10)


def _reply(chat_id, message_id: int, text: str) -> None:
    """Reply to a message inline."""
    payload = {
        "chat_id": chat_id,
        "text": text[:4000],
        "reply_to_message_id": message_id,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    _api("sendMessage", params=payload, timeout=10)


# ════════════════════════════════════════════════════════════════════
# MESSAGE HANDLING
# ════════════════════════════════════════════════════════════════════

def _handle_message(msg: dict) -> None:
    """Process a single message from the Guest Chamber."""
    chat = msg.get("chat") or {}
    chat_id = chat.get("id")

    # Filter to the configured Guest Chamber only
    if str(chat_id) != str(GUEST_CHAMBER_ID):
        return

    # Ignore other bots and our own messages
    sender = msg.get("from") or {}
    if sender.get("is_bot"):
        return
    if _BOT_USER_ID and sender.get("id") == _BOT_USER_ID:
        return

    # Need text to route as a question
    text = (msg.get("text") or "").strip()
    if not text:
        return

    # Help / start commands get a friendly reply, not a Parliament question
    if text.startswith(("/start", "/help")):
        _reply(
            chat_id,
            msg.get("message_id", 0),
            "<b>🤝 Welcome to Elpida's Guest Chamber.</b>\n\n"
            "Ask any question and Elpida's Parliament will deliberate. "
            "Within ~30 seconds a 🏛️ reaction will confirm your question is in the queue. "
            "A response will arrive once the deliberation completes.\n\n"
            "Be direct. Honest tensions are welcome. Bring something real.",
        )
        return

    # Skip overly short messages — they almost never produce useful deliberation
    if len(text) < 5:
        return

    author = (
        sender.get("first_name")
        or sender.get("username")
        or f"guest_{sender.get('id', 'anon')}"
    )

    try:
        from elpidaapp.guest_chamber import post_question

        qid = post_question(text, author=author)
        logger.info(
            "Guest question captured: id=%s author=%s q='%s'",
            qid,
            author,
            text[:80],
        )
        _react(chat_id, msg.get("message_id", 0), "🏛️")
    except Exception as e:
        logger.error("Failed to post guest question to S3: %s", e)
        try:
            _react(chat_id, msg.get("message_id", 0), "❌")
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════════
# LOOP
# ════════════════════════════════════════════════════════════════════

def _run_listener() -> None:
    """Long-poll Telegram for guest chamber messages indefinitely."""
    global _BOT_USER_ID

    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram listener disabled")
        return
    if not GUEST_CHAMBER_ID:
        logger.warning(
            "TELEGRAM_GUEST_CHAMBER_ID not set — Telegram listener disabled"
        )
        return

    _BOT_USER_ID = _get_me()
    if _BOT_USER_ID:
        logger.info(
            "Telegram listener connected as user_id=%d, guest_chamber=%s",
            _BOT_USER_ID,
            GUEST_CHAMBER_ID,
        )
    else:
        logger.warning(
            "Telegram getMe failed at startup — token may be invalid. Will keep retrying."
        )

    offset = _load_offset()
    backoff = 1.0
    while True:
        try:
            updates = _get_updates(offset)
            if updates:
                backoff = 1.0  # reset backoff on success
                for update in updates:
                    new_offset = update.get("update_id", 0) + 1
                    if new_offset > offset:
                        offset = new_offset
                    msg = update.get("message") or update.get("edited_message")
                    if msg:
                        try:
                            _handle_message(msg)
                        except Exception as e:
                            logger.error("Handler error on update: %s", e)
                _save_offset(offset)
            else:
                # No updates — long-poll already waited up to LONG_POLL_TIMEOUT;
                # don't busy-loop.
                pass
        except Exception as e:
            logger.error("Telegram listener loop error: %s", e)
            time.sleep(backoff)
            backoff = min(backoff * 2.0, 60.0)


# ════════════════════════════════════════════════════════════════════
# PUBLIC API
# ════════════════════════════════════════════════════════════════════

def start_listener() -> None:
    """
    Start the Telegram guest listener as a daemon thread.

    Safe to call multiple times — only starts once.
    Requires TELEGRAM_BOT_TOKEN and TELEGRAM_GUEST_CHAMBER_ID env vars.
    """
    global _listener_thread

    if _listener_thread and _listener_thread.is_alive():
        logger.debug("Telegram listener already running")
        return

    if not TELEGRAM_BOT_TOKEN:
        logger.info(
            "TELEGRAM_BOT_TOKEN not set — Telegram listener disabled. "
            "Questions can still be posted via feed_elpida.py CLI."
        )
        return

    _listener_thread = threading.Thread(
        target=_run_listener,
        daemon=True,
        name="TelegramGuestListener",
    )
    _listener_thread.start()
    logger.info("Telegram Guest Listener thread started")


def is_running() -> bool:
    """Check if the listener thread is alive."""
    return _listener_thread is not None and _listener_thread.is_alive()
