from aiohttp import ClientSession
from asyncio import get_event_loop

from bot.bot import send_message
from config import SYMBOLS
from common import applogger
from market import MarketDataCollector
from trader import EmulatorTrader


def run(market: MarketDataCollector):
    market.start_monitoring()
    

if __name__ == '__main__':
    loop = get_event_loop()

    trader = EmulatorTrader(SYMBOLS)
    trader.init()
    market = MarketDataCollector(trader)

    try:
        run(market)
    except Exception as e:
        applogger.critical(f'WE\'RE FUCKED {e}', exc_info=True)
        loop.run_until_complete(send_message(f'WE\'RE FUCKED\n\n{e}'))
    finally:
        market.stop_monitoring()
        print('See ya!')