from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


def paginated_chats_kb(chats, page=0, count=3):
	res = InlineKeyboardMarkup()
	start = page * count
	end = start + count
	page_items = chats[start:end]
	for i in page_items:
		id = i['_id']
		chat_name = i['name']
		res.add(InlineKeyboardButton(chat_name, callback_data='[c]' + str(id)))
	if len(chats) > count:
		control_buttons = []
		if page > 0:
			control_buttons.append(InlineKeyboardButton('⬅️', callback_data='prev'))
		if end < len(chats):
			control_buttons.append(InlineKeyboardButton('➡️', callback_data='next'))
		res.row(*control_buttons)
	res.add(InlineKeyboardButton('Cancel', callback_data='cancel'))
	return res

def urls_kb(buttons):
	res = InlineKeyboardMarkup()
	for b in buttons:
		res.add(InlineKeyboardButton(b[0], url=b[1]))
	return res

def presale_details_db(buttons=[]):
	res = InlineKeyboardMarkup()
	if buttons:
		res = urls_kb(buttons)
	res.add(InlineKeyboardButton('Back', callback_data='back'))
	return res


confirmation_kb = InlineKeyboardMarkup()
confirmation_kb.row(
	InlineKeyboardButton('Yes', callback_data='y'),
	InlineKeyboardButton('No', callback_data='n')
)

admin_kb = ReplyKeyboardMarkup(keyboard=[
	[KeyboardButton('Add')],
	[KeyboardButton('Remove')]
])
