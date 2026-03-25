"""
Discord Guest Listener — Reads #guest-chamber Messages into S3
================================================================

Lightweight Discord bot that watches the #guest-chamber channel
for human questions, posts them to S3 via guest_chamber.post_question(),
and replies with a confirmation. The BODY's GuestChamberFeed picks
them up within 30 seconds and deliberates.

Runs as a background thread inside the HF Space process.
Requires DISCORD_BOT_TOKEN environment variable.
Channel name is configurable via DISCORD_GUEST_CHANNEL (default: guest-chamber).

The bot ignores:
  - Its own messages
  - Other bots' messages (including webhook posts from Elpida)
  - Messages in channels other than #guest-chamber
"""

import logging
import os
import threading
from typing import Optional

logger = logging.getLogger("elpida.discord_listener")

GUEST_CHANNEL_NAME = os.getenv("DISCORD_GUEST_CHANNEL", "guest-chamber")
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")

# Extract Elpida's own webhook ID from the guest webhook URL to prevent loops.
# Webhook URLs look like: https://discord.com/api/webhooks/{ID}/{TOKEN}
_guest_webhook_url = os.getenv("DISCORD_WEBHOOK_GUEST", "")
ELPIDA_WEBHOOK_ID = None
if _guest_webhook_url:
    try:
        ELPIDA_WEBHOOK_ID = int(_guest_webhook_url.split("/webhooks/")[1].split("/")[0])
    except (IndexError, ValueError):
        pass


def _run_bot():
    """Start the Discord bot in an asyncio event loop (blocking)."""
    try:
        import discord
    except ImportError:
        logger.warning(
            "discord.py not installed — Guest Listener disabled. "
            "Install with: pip install discord.py"
        )
        return

    import asyncio

    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(
            "Discord Guest Listener connected as %s (guilds: %d)",
            client.user, len(client.guilds),
        )
        # Find and log the guest chamber channel
        for guild in client.guilds:
            for ch in guild.text_channels:
                if ch.name == GUEST_CHANNEL_NAME:
                    logger.info(
                        "  Listening on #%s in %s (id=%s)",
                        ch.name, guild.name, ch.id,
                    )

    @client.event
    async def on_message(message):
        logger.info(
            "on_message: author=%s bot=%s webhook_id=%s channel=%s content=%s",
            message.author, message.author.bot,
            message.webhook_id,
            getattr(message.channel, 'name', '?'),
            (message.content or '')[:60],
        )
        # Ignore our own messages
        if message.author == client.user:
            return
        # Only block Elpida's own webhook (replies) to prevent loops.
        # Other webhooks (e.g. Pipedream, Zapier) are allowed through.
        if message.webhook_id and ELPIDA_WEBHOOK_ID and message.webhook_id == ELPIDA_WEBHOOK_ID:
            return

        # Only listen in #guest-chamber
        if not hasattr(message.channel, 'name'):
            return
        if message.channel.name != GUEST_CHANNEL_NAME:
            return

        # Ignore empty messages or attachment-only
        question = message.content.strip()
        if not question:
            return

        author = message.author.display_name or message.author.name

        # Post to S3 via guest_chamber module
        try:
            from elpidaapp.guest_chamber import post_question
            qid = post_question(question, author=author)
            logger.info(
                "Guest question captured: id=%s author=%s q='%s'",
                qid, author, question[:80],
            )
            # React to confirm receipt
            await message.add_reaction("🏛️")
        except Exception as e:
            logger.error("Failed to post guest question to S3: %s", e)
            try:
                await message.add_reaction("❌")
            except Exception:
                pass

    # Run the bot
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(client.start(BOT_TOKEN))
    except Exception as e:
        logger.error("Discord bot stopped: %s", e)
    finally:
        loop.close()


_listener_thread: Optional[threading.Thread] = None


def start_listener():
    """
    Start the Discord guest listener as a daemon thread.

    Safe to call multiple times — only starts once.
    Requires DISCORD_BOT_TOKEN environment variable.
    """
    global _listener_thread

    if _listener_thread and _listener_thread.is_alive():
        logger.debug("Discord listener already running")
        return

    if not BOT_TOKEN:
        logger.info(
            "DISCORD_BOT_TOKEN not set — Guest Listener disabled. "
            "Questions can still be posted via feed_elpida.py CLI."
        )
        return

    _listener_thread = threading.Thread(
        target=_run_bot,
        daemon=True,
        name="DiscordGuestListener",
    )
    _listener_thread.start()
    logger.info("Discord Guest Listener thread started")


def is_running() -> bool:
    """Check if the listener thread is alive."""
    return _listener_thread is not None and _listener_thread.is_alive()
