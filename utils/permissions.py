# utils/permissions.py

async def is_admin(chat, user_id):
    try:
        member = await chat.get_member(user_id)
        return member.status in ("administrator", "creator")
    except:
        return False
