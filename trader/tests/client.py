import asyncio


class TestClient:

    def __init__(self, socket_address):
        self.socket_address = socket_address
        self.opened = False
        self.reader: asyncio.StreamReader = None
        self.writer: asyncio.StreamWriter = None

    async def start(self):
        self.reader, self.writer = await asyncio.open_unix_connection(self.socket_address)
        print('Connection opened!')
        self.opened = True

    async def _send(self, message: str):
        if not message.endswith('\n'):
            message += '\n'

        self.writer.write(message.encode())
        await self.writer.drain()

    async def send(self, message):
        await self._send(message)

    async def close(self):
        self.opened = False
        self.writer.close()
        await self.writer.wait_closed()
