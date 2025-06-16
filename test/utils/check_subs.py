# from config import REQUIRED_CHANNELS
# from aiogram import Bot

# async def check_subs(bot: Bot, user_id: int) -> bool:
#     for channel in REQUIRED_CHANNELS:
#         try:
#             member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
#             if member.status in ["left", "kicked"]:
#                 return False
#         except:
#             return False
#     return True
from aiogram import Bot

async def check_subs(bot: Bot, user_id: int, channels: list):
    not_joined = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                not_joined.append(ch)
        except:
            not_joined.append(ch)
    return not_joined  # Endi ro‘yxat qaytaradi
