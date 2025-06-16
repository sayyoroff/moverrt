# from aiogram import Bot
# from baza.save_users import get_all_users

# async def send_bulk_message(bot: Bot, text: str):
#     users = get_all_users()
#     success = 0
#     for user_id in users:
#         try:
#             await bot.send_message(chat_id=user_id, text=text)
#             success += 1
#         except:
#             continue
#     return success, len(users)
from aiogram import Bot, types
from baza.save_users import get_all_users

# Matn yuborish
async def send_bulk_message(bot: Bot, text: str):
    users = get_all_users()
    success = 0
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            success += 1
        except:
            continue
    return success, len(users)

# Rasm yuborish
async def send_bulk_photo(bot: Bot, photo_file_id: str, caption: str = ""):
    users = get_all_users()
    success = 0
    for user_id in users:
        try:
            await bot.send_photo(chat_id=user_id, photo=photo_file_id, caption=caption)
            success += 1
        except:
            continue
    return success, len(users)

# Video yuborish
async def send_bulk_video(bot: Bot, video_file_id: str, caption: str = ""):
    users = get_all_users()
    success = 0
    for user_id in users:
        try:
            await bot.send_video(chat_id=user_id, video=video_file_id, caption=caption)
            success += 1
        except:
            continue
    return success, len(users)
