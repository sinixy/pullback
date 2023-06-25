import asyncio
import traceback
import json

from common import applogger
from bot.bot import send_message


class Server:

    def __init__(self, socket_address, trader, loop = None):
        self.socket_address = socket_address
        self.trader = trader
        self._loop = loop

        if not loop:
            self._loop = asyncio.get_event_loop()

        self.running = False

    async def run(self):
        applogger.info('Starting the server')
        self.running = True
        try:
            await asyncio.start_unix_server(self._listen, self.socket_address)
        except Exception as e:
            traceback.print_exc()
            await send_message(f'UNIX server error: {e}')
            applogger.critical(f'UNIX server error: {e}', exc_info=True)


    async def _listen(self, reader, writer):
        while True:
            data = await reader.readline()
            message = data.decode().strip()
            if message:
                self._loop.create_task(self.trader.handle(json.loads(message)))
