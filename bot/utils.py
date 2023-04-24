import asyncio
from functools import wraps, partial


def async_wrap(func):
	@wraps(func)
	async def run(*args, loop=None, executor=None, **kwargs):
		if loop is None:
			loop = asyncio.get_event_loop()
		pfunc = partial(func, *args, **kwargs)
		return await loop.run_in_executor(executor, pfunc)
	return run 

def stringify_price(price):
	if price >= 0.0001:
		return str(round(price, 5))
	else:
		# 0 . 000 000 000 987654345678909876 => 0.0[9]9877
		zeros_cnt = int(str(price)[-2:])
		return f'0.0[{zeros_cnt-1}]' + str(round(price * 10**(zeros_cnt-1), 4))[2:]

def stringify_duration(secs):
	if secs >= 3600 * 24:
		return str(round(secs / (3600*24), 1)) + 'd'
	elif secs >= 3600:
		return str(round(secs / 3600, 1)) + 'h'
	elif secs >= 60:
		return str(round(secs / 60, 1)) + 'm'
	else:
		return str(secs) + 's'

def stringify_raised_info(info):
	res = '{} / {} {}'
	caps = info['soft_cap']
	if hard_cap := info.get('hard_cap'):
		caps = f'({caps} - {hard_cap})'
	return res.format(info['raised'], caps, info['currency']['symbol'])

def get_pool_buttons(pool):
	buttons = [('Presale', pool['presale_url'])]
	if tglink := pool['socials'].get('telegram'):
		buttons.append(('Chat', tglink))
	if pair := pool.get('pair'):
		buttons.append(('DEXTools', f'https://www.dextools.io/app/bnb/pair-explorer/{pair}'))
	return buttons