from aiohttp import ClientSession
import asyncio
import traceback

from bot.bot import send_message
from config import SYMBOLS
from common import applogger
from market import MarketDataCollector
from trader import EmulatorTrader


ERROR = False

def handle_exception(loop, context):
    global ERROR
    if not ERROR:
        ERROR = True
        try:
            market.stop_monitoring()
        except Exception as e:
            applogger.error(f'Couldn\'t correctly stop monitoring: {e}', exc_info=True)

        exception = context["exception"]
        loop.create_task(send_message(f'WE\'RE FUCKED\n\n{exception}'))
        traceback_str = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        applogger.critical(f'WE\'RE FUCKED - {exception}\n{traceback_str}', exc_info=True)

        loop.create_task(terminate(loop))

async def terminate(loop):
    await asyncio.sleep(3)
    loop.stop()

def run(market: MarketDataCollector, loop):
    market.start_monitoring()
    loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

    trader = EmulatorTrader(SYMBOLS)
    trader.init()
    market = MarketDataCollector(trader)

    try:
        run(market, loop)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        applogger.critical(f'WE\'RE FUCKED {e}', exc_info=True)
        loop.run_until_complete(send_message(f'WE\'RE FUCKED\n\n{e}'))
    finally:
        market.stop_monitoring()
        print('See ya!')