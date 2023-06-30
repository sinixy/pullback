import asyncio
import traceback
import json

from common import applogger


class UnixServer:

    def __init__(self, socket_address, trader, loop = None):
        self.socket_address = socket_address
        self.trader = trader
        self._loop = loop

        if not loop:
            self._loop = asyncio.get_event_loop()

        self.connected = False

    async def run(self):
        applogger.info('Starting the server')
        try:
            await asyncio.start_unix_server(self._serve, self.socket_address)
        except Exception as e:
            traceback.print_exc()
            applogger.critical(f'UNIX server error: {e}', exc_info=True)


    async def _serve(self, reader, writer):
        print('Market connected!')
        self.connected = True
        while self.connected:
            data = await reader.readline()
            message = data.decode().strip()
            if message:
                self._loop.create_task(self.trader.handle_request(json.loads(message)))
            else:
                print('Market disconnected!')
                self.connected = False
