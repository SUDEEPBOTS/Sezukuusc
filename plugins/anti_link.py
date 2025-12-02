# plugins/anti_link.py

import re
from utils.auto_delete import auto_delete

LINK_REGEX = r"(https?://\S+)"

async def handle_links(update, context):
    """Auto delete links and warn users."""
    text = update.message.text

    if re.search(LINK_REGEX, text):
        msg = await update.message.reply_text(
            "🚫 Links are not allowed without context."
        )
        await auto_delete(msg)

        try:
            await update.message.delete()
        except:
            pass
