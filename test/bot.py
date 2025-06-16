import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN, REQUIRED_CHANNELS, ADMIN_ID, CHANNEL_ID, VIDEO_LINKS
from utils.check_subs import check_subs
from baza.save_users import init_db, save_user, get_all_users
from baza.send_bulk_message import send_bulk_message, send_bulk_photo, send_bulk_video
from states import AdminStates

# Bot va dispatcher
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id

    # Foydalanuvchini saqlaymiz (agar sync funksiya bo‘lsa await kerak emas)
    save_user(user_id)

    # Har doim obuna tugmalari chiqsin
    btn = types.InlineKeyboardMarkup(
        inline_keyboard=[
            # [types.InlineKeyboardButton(text=f"📢 Obuna bo‘lish #{i+1}", url=ch["link"])]
            [types.InlineKeyboardButton(text=f"📢 {i+1}. {ch['name']}", url=ch["link"])]
            for i, ch in enumerate(REQUIRED_CHANNELS)
        ] + [[types.InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subs")]]
    )
    await message.answer(
        "🔒 Botdan foydalanish uchun quyidagi kanal(lar)ga obuna bo‘ling, so‘ngra botga kod yuboring:",
        reply_markup=btn
    )
@dp.callback_query(lambda c: c.data == "check_subs")
async def check_subs_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    not_joined = await check_subs(bot, user_id, REQUIRED_CHANNELS)

    if not_joined:
        btn = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=f"➕ {ch['name']}", url=ch["link"])]
                for ch in not_joined
            ] + [[types.InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subs")]]
        )
        await callback.message.edit_text(
            "❗️ Siz hali quyidagi kanal(lar)ga obuna bo‘lmagansiz:",
            reply_markup=btn
        )
        await callback.answer()
    else:
        await callback.message.edit_text("✅ Obuna tasdiqlandi!\n🎬 Endi kino kodini yuboring (masalan: <code>1</code>, <code>2</code>)")
        await callback.answer()


# @dp.message(Command("start"))
# async def start_handler(message: types.Message):
#     save_user(message.from_user.id)
#     if not await check_subs(bot, message.from_user.id):
#         btn = types.InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [types.InlineKeyboardButton(text=f"➕ Obuna bo‘lish #{i+1}", url=ch["link"])]
#                 for i, ch in enumerate(REQUIRED_CHANNELS)
#             ]
#         )
#         await message.answer("🔒 Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:", reply_markup=btn)
#         return
#     await message.answer("🎬 Maxsus kodni yuboring (masalan: <code>1, 2, 3</code>):")

# Admin_panel
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    btn = types.ReplyKeyboardMarkup(
        keyboard=[
            [   # Bir qator
                types.KeyboardButton(text="📊 Statistika"),
                types.KeyboardButton(text="📢 Reklama yuborish")
            ]
        ],
        resize_keyboard=True
    )
    await message.answer("🔧 Admin panelga xush kelibsiz:", reply_markup=btn)

@dp.message(lambda msg: msg.from_user.id == ADMIN_ID and msg.text == "📊 Statistika")
async def show_stats(message: types.Message):
    count = len(get_all_users())
    await message.answer(f"👥 Umumiy foydalanuvchilar soni: <b>{count}</b>")

# fayl bilan birga reklama tarqatish /////////////////////////////////////////////////////////////////////////////////////////
@dp.message(lambda msg: msg.from_user.id == ADMIN_ID and msg.text == "📢 Reklama yuborish")
async def ask_ad_text(message: types.Message, state: FSMContext):
    await message.answer("📨 Reklama matnini yuboring:")
    await state.set_state(AdminStates.waiting_for_ad_text)

# //////////////////////////////////////////////////////////////////////////////
@dp.message(AdminStates.waiting_for_ad_text)
async def handle_ad_text(message: types.Message, state: FSMContext):
    caption = message.caption or message.text or ""

    # Agar foydalanuvchi rasm yuborsa
    if message.photo:
        photo_id = message.photo[-1].file_id
        ok, total = await send_bulk_photo(bot, photo_id, caption)
        await message.answer(f"🖼 Rasm yuborildi:\n✅ {ok} ta\n❌ {total - ok} ta")

    # Agar foydalanuvchi video yuborsa
    elif message.video:
        video_id = message.video.file_id
        ok, total = await send_bulk_video(bot, video_id, caption)
        await message.answer(f"🎥 Video yuborildi:\n✅ {ok} ta\n❌ {total - ok} ta")

    # Faqat matn yuborsa
    elif message.text:
        ok, total = await send_bulk_message(bot, message.text)
        await message.answer(f"✉️ Matn yuborildi:\n✅ {ok} ta\n❌ {total - ok} ta")
    else:
        await message.answer("❗️ Iltimos, matn, rasm yoki video yuboring.")
        return

    await state.clear()
# ////////////////////////ADMIN PANEL//////////////////////////////////////////////////////
@dp.message()
async def handle_code(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

# ❗️ Obuna bo‘lmagan foydalanuvchiga tugmali xabar yuborish # Obuna holatini tekshiramiz
    not_joined = await check_subs(bot, user_id, REQUIRED_CHANNELS)
    if not_joined:
        btn = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=f"➕ {ch['name']}", url=ch["link"])]
                for ch in not_joined
            ] + [[types.InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subs")]]
        )
        await message.answer(
            "🔒 Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling, so‘ngra «✅ Obunani tekshirish» tugmasini bosing:",
            reply_markup=btn
        )
        return
# obuna holati
    if text in VIDEO_LINKS:
        msg_id = VIDEO_LINKS[text]
        await bot.copy_message(chat_id=user_id, from_chat_id=CHANNEL_ID, message_id=msg_id)
    else:
        
      await message.answer(
    "📭 Kechirasiz, bu kodga mos kino topilmadi.\nBoshqa kod yuboring!",
    reply_markup=types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🎬 Kino kodlari", url="https://t.me/smediauz")],
        ]
    )
)
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())