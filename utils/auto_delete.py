# utils/auto_delete.py

import asyncio

async def auto_delete(message):
    """Deletes any bot message after 3 minutes."""
    await asyncio.sleep(180)

    try:
        await message.delete()
    except:
        pass
