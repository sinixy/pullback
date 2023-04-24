from traceback import print_exc
import asyncio

from exchange import client, bm
from common import applogger
from common.bot import send_message
from common.db import redis_db


class MarketDataCollector:

    def __init__(self, trader, loop=None):
        self.trader = trader
        self._loop = loop

        self._semaphore = asyncio.Semaphore(128)
        if not loop:
            self._loop = asyncio.get_event_loop()

        self.running = False
        self.socket_connection = bm.futures_multiplex_socket([f'{s.lower()}@aggTrade' for s in self.trader.symbols])

    def start_monitoring(self):
        applogger.info('Starting the monitoring process')
        self.running = True
        self._loop.create_task(self._listen_for_messages())
        if not self._loop.is_running():
            self._loop.run_forever()

    async def _save_message(self, message):
        async with self._semaphore:
            time = message['T']
            await redis_db.xadd(message['s'], {'t': time, 'p': message['p']}, id=f'{time}-*')

    async def _listen_for_messages(self):
        applogger.info('Listeting to incoming orders')
        async with self.socket_connection as stream:
            while self.running:
                msg = await stream.recv()
                self._loop.create_task(self.trader.handle_message(msg['data']))
                self._loop.create_task(self._save_message(msg['data']))

    def stop_monitoring(self):
        applogger.info('Stoping the monitoring process')
        self._loop.create_task(self._stop_monitoring())

    async def _stop_monitoring(self):
        self.running = False
        await client.close_connection()
        applogger.info('Monitoring process stopped')
    

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    market = MarketDataCollector(loop)
    try:
        market.start_monitoring()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        print_exc()
        loop.run_until_complete(send_message(f'⚠️ ERROR: {e}'))
    finally:
        print('Bye')
        market.stop_monitoring()
        loop.stop()