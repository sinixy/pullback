import json
import asyncio
from binance import AsyncClient, BinanceSocketManager
from time import time


loop = asyncio.get_event_loop()
client = loop.run_until_complete(AsyncClient.create())
bm = BinanceSocketManager(client)

conf = {}
with open('config.json') as file:
	conf = json.load(file)


class MarketDataCollector:

    def __init__(self, loop=None):
        self._loop = loop

        if not loop:
            self._loop = asyncio.get_event_loop()

        self.running = False
        self.socket_connection = bm.futures_multiplex_socket([f'{s.lower()}@aggTrade' for s in conf['symbols']])

    def start_monitoring(self):
        self.running = True
        self._loop.create_task(self._listen_for_messages())

    async def _listen_for_messages(self):
        async with self.socket_connection as stream:
            while self.running:
                msg = await stream.recv()
                if msg['data']['s'] == 'MASKUSDT':
                	print('Ping:', time()*1000 - msg['data']['T'])

    def stop_monitoring(self):
        if not self.running:
            return
        self.running = False
        self._loop.create_task(self._close_connection())

    async def _close_connection(self):
        await client.close_connection()


if __name__ == '__main__':
    market = MarketDataCollector(loop)
    try:
        market.start_monitoring()
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        print_exc()
    finally:
        print('Bye')
        market.stop_monitoring()
        loop.stop()