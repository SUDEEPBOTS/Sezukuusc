import asyncio

async def auto_delete(message):
    await asyncio.sleep(180)
    try:
        await message.delete()
    except:
        pass
