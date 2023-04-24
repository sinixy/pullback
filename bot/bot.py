from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# import plotly.graph_objects as go

from config import TG_BOT_TOKEN, TG_RECEIVER_ID
from .utils import async_wrap
import bot.keyboards as kb


bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def admin(func):
	async def wrapper(message, state):
		if message.from_user.id != int(TG_RECEIVER_ID):
			return
		return await func(message, state)
	return wrapper

@dp.message_handler(commands=['admin'], state='*')
@admin
async def enter_admin_panel(msg: types.Message, state: FSMContext):
	await msg.reply('Pullback Admin 😎', reply=False, reply_markup=kb.admin_kb)

async def send_message(text, buttons=[], disable_preview=False):
	await bot.send_message(
		TG_RECEIVER_ID,
		text,
		reply_markup=kb.urls_kb(buttons),
		parse_mode=types.ParseMode.HTML,
		disable_web_page_preview=disable_preview
	)

async def send_signal(symbol, price_feed):
	segment = [p for p in price_feed if price_feed[-1]['time'] - p['time'] <= 3600]

	fig = go.Figure(data=[go.Scatter(x=[s['time'] for s in segment], y=[s['price'] for s in segment])])
	photo = await async_wrap(fig.to_image)(format='png')
	await bot.send_photo(
		TG_RECEIVER_ID,
		photo=photo,
		caption=f'❗️ <b>{symbol} attention!</b>',
		parse_mode=types.ParseMode.HTML
	)