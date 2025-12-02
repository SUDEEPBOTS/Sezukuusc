import logging
import asyncio
from datetime import datetime, timedelta

from telegram import (
    Update, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ChatPermissions,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from models import (
    get_user,
    get_group,
    add_ban_record,
    get_pending_appeals,
    approve_appeal,
    reject_appeal,
    increment_ban,
    accept_appeal,
    set_verified,
    save_profile,
)

from plugins.welcome_verify import new_member, verify_button
from plugins.logging_system import log_bot_started, log_bot_added
from utils.auto_delete import auto_delete

from config import BOT_TOKEN

OWNER_ID = 6356015122
LOGGER_ID = -1003444664979
BOT_USERNAME = "@Sezukuusecuritybot"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =============== HELPER FUNCTIONS =============== #

async def is_admin(update: Update, user_id: int):
    try:
        member = await update.effective_chat.get_member(user_id)
        return member.status in ("administrator", "creator")
    except:
        return False


async def send_log(context, msg):
    try:
        await context.bot.send_message(LOGGER_ID, msg)
    except:
        pass# =================== BAN SYSTEM =================== #

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, update.message.from_user.id):
        return

    if len(context.args) < 2:
        return await update.message.reply_text("Usage: /ban @user reason")

    user = update.message.reply_to_message.from_user
    reason = " ".join(context.args[1:])
    chat_id = update.effective_chat.id

    # Add ban record
    increment_ban(user.id)
    add_ban_record(user.id, chat_id, reason)

    await context.bot.ban_chat_member(chat_id, user.id)

    # Send DM to user with reason
    try:
        await context.bot.send_message(
            user.id,
            f"🚫 You were banned from {update.effective_chat.title}\n\nReason: {reason}"
        )
    except:
        pass

    # Notify admin
    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve Appeal", callback_data=f"admin_approve_{user.id}_{chat_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{user.id}_{chat_id}")
        ]
    ])

    msg = await context.bot.send_message(
        LOGGER_ID,
        f"⚠️ Ban Appeal Request\nUser: {user.full_name}\nID: {user.id}\nGroup: {chat_id}\nReason: {reason}",
        reply_markup=btn
    )

    await auto_delete(msg)


# =================== USER APPEAL =================== #

async def appeal(update: Update, context):
    user_id = update.message.from_user.id
    appeals = get_pending_appeals(user_id)

    if not appeals:
        return await update.message.reply_text("❌ No pending appeals.")

    user = get_user(user_id)

    # If appeal accepted 3 times → no more appeals
    if user["total_appeals_accepted"] >= 3:
        return await update.message.reply_text("⚠️ You cannot appeal anymore.")

    for a in appeals:
        chat_id = a["chat_id"]
        reason = a["reason"]

        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔓 Approve", callback_data=f"admin_approve_{user_id}_{chat_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{user_id}_{chat_id}")
            ]
        ])

        msg = await context.bot.send_message(
            LOGGER_ID,
            f"🚨 Appeal Received\nUser: {update.message.from_user.full_name}\nChat: {chat_id}\nReason: {reason}",
            reply_markup=btn
        )
        await auto_delete(msg)

    await update.message.reply_text("📨 Your appeal has been sent to admins.")


# =================== ADMIN BUTTON HANDLERS =================== #

async def admin_buttons(update: Update, context):
    query = update.callback_query
    data = query.data.split("_")

    action = data[1]
    user_id = int(data[2])
    chat_id = int(data[3])

    if action == "approve":
        approve_appeal(user_id, chat_id)
        accept_appeal(user_id)

        # Unban
        try:
            await context.bot.unban_chat_member(chat_id, user_id)
        except:
            pass

        # Join button
        join_btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Join Group", url=f"https://t.me/{chat_id}")]
        ])

        await query.edit_message_text(
            f"✅ Appeal Approved for user {user_id}\nGroup: {chat_id}",
            reply_markup=join_btn
        )

    elif action == "reject":
        reject_appeal(user_id, chat_id)
        await query.edit_message_text(f"❌ Appeal Rejected for user {user_id}")

    await auto_delete(query.message)# =================== START COMMAND =================== #

async def start(update: Update, context):
    await log_bot_started(update, context)
    await update.message.reply_text("Hello! I'm your security bot.")


# =================== BOT ADDED TO GROUP =================== #

async def added_to_group(update: Update, context):
    await log_bot_added(update, context)


# =================== MAIN APP =================== #

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("appeal", appeal))

    # New Member
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))

    # Callbacks
    app.add_handler(CallbackQueryHandler(verify_button, pattern="verify_"))
    app.add_handler(CallbackQueryHandler(admin_buttons, pattern="admin_"))

    # Bot added
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, added_to_group))

    logging.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
