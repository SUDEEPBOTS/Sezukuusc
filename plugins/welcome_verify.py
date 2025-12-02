from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from telegram.ext import ContextTypes
from models import set_verified, save_profile
from utils.auto_delete import auto_delete

async def new_member(update, context: ContextTypes.DEFAULT_TYPE):

    for user in update.message.new_chat_members:
        chat_id = update.effective_chat.id
        user_id = user.id

        # Mute
        await context.bot.restrict_chat_member(
            chat_id,
            user_id,
            ChatPermissions(can_send_messages=False)
        )

        # Verify button
        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("✔ Verify", callback_data=f"verify_{user_id}")
        ]])

        msg = await update.message.reply_text(
            f"👋 Welcome {user.first_name}!\n\nPlease verify yourself.",
            reply_markup=btn
        )

        context.chat_data["verify_message"] = msg.message_id
        await auto_delete(msg)


async def verify_button(update, context):
    query = update.callback_query
    user_id = query.from_user.id

    # Delete button message
    chat_id = query.message.chat.id
    try:
        await context.bot.delete_message(chat_id, query.message.message_id)
    except:
        pass

    # Send DM
    await context.bot.send_message(
        user_id,
        "🔐 Verification successful!\nYour profile is created."
    )

    set_verified(user_id)
    save_profile(user_id, {"verified": True})

    # Unmute in GC
    await context.bot.restrict_chat_member(
        chat_id,
        user_id,
        ChatPermissions(can_send_messages=True)
    )
