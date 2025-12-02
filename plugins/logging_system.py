from models import log_event

LOGGER_CHAT = -1001234567890  # <-- your logger GC ID

async def log_bot_started(update, context):
    user = update.message.from_user
    log_event("bot_started", {"user_id": user.id})

    await context.bot.send_message(
        LOGGER_CHAT,
        f"🚀 Bot Started by {user.full_name} (ID: {user.id})"
    )


async def log_bot_added(update, context):
    chat = update.effective_chat
    log_event("bot_added", {"chat_id": chat.id})

    await context.bot.send_message(
        LOGGER_CHAT,
        f"🤖 Bot Added to Group:\n"
        f"Name: {chat.title}\n"
        f"ID: {chat.id}"
    )
