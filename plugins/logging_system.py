# plugins/logging_system.py

from models import log_event
from config import LOGGER_ID


async def log_bot_started(update, context):
    user = update.message.from_user
    log_event("bot_started", {"user_id": user.id})

    try:
        await context.bot.send_message(
            LOGGER_ID,
            f"🚀 Bot Started by {user.full_name} (`{user.id}`)",
            parse_mode="Markdown"
        )
    except:
        pass


async def log_bot_added_to_group(update, context):
    chat = update.effective_chat

    log_event("bot_added_group", {"chat_id": chat.id})

    try:
        await context.bot.send_message(
            LOGGER_ID,
            f"🤖 Bot Added to Group:\n"
            f"**{chat.title}**\n"
            f"ID: `{chat.id}`",
            parse_mode="Markdown"
        )
    except:
        pass


async def log_error_event(error):
    log_event("error", {"error_details": str(error)})
