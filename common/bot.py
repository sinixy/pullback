from aiogram import Bot, types

from config import BOT_TOKEN, RECIEVER_ID


bot = Bot(token=BOT_TOKEN)

async def send_message(text, disable_preview=False):
    await bot.send_message(
        RECIEVER_ID,
        text,
        parse_mode=types.ParseMode.HTML,
        disable_web_page_preview=disable_preview
    )