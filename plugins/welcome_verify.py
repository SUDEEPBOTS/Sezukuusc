# plugins/welcome_verify.py

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
)
from telegram.ext import ContextTypes
from models import set_verified, save_profile
from utils.auto_delete import auto_delete
from config import LOGGER_ID


async def handle_new_member(update, context: ContextTypes.DEFAULT_TYPE):
    """Handles new users joining with auto mute + verification system."""
    for user in update.message.new_chat_members:
        chat = update.effective_chat
        user_id = user.id

        # Auto Mute
        await context.bot.restrict_chat_member(
            chat.id,
            user_id,
            ChatPermissions(can_send_messages=False),
        )

        # Verify Button
        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("✔ Verify", callback_data=f"verify_{user_id}")]
        ])

        msg = await update.message.reply_text(
            f"👋 Welcome **{user.first_name}**!\n"
            "Please complete verification.",
            parse_mode="Markdown",
            reply_markup=btn
        )

        # Auto delete verify message
        await auto_delete(msg)


async def verify_button(update, context: ContextTypes.DEFAULT_TYPE):
    """User clicks verify → DM message + profile create + unmute."""
    query = update.callback_query
    data = query.data.split("_")
    target_id = int(data[1])

    user = query.from_user

    # Delete the verify button message
    try:
        await query.message.delete()
    except:
        pass

    # Send DM
    try:
        await context.bot.send_message(
            user.id,
            "🔐 **Verification Successful!**\nYour identity has been confirmed.",
            parse_mode="Markdown",
        )
    except:
        pass

    # Save profile
    save_profile(user.id, {"verified": True})
    set_verified(user.id, True)

    # Unmute the user
    chat_id = query.message.chat.id
    try:
        await context.bot.restrict_chat_member(
            chat_id,
            user.id,
            ChatPermissions(can_send_messages=True)
        )
    except:
        pass
