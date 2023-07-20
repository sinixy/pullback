import asyncio
import json
import traceback
from typing import List, Tuple


class WebsocketServer:

    def __init__(self):
        self.host: str = ''
        self.port: str = ''

        self.connected: bool = False
        self.connections: List[Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = []

    def init(self, host, port):
        self.host = host
        self.port = port

    async def run(self):
        try:
            await asyncio.start_server(self._serve, self.host, self.port)
        except Exception as e:
            traceback.print_exc()

    async def _serve(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        print('Manasan connected!')
        self.connected = True
        self.connections.append((reader, writer))
        while self.connected:
            data = await reader.readline()
            message = data.decode().strip()
            if not message:
                print('Manasan disconnected!')
                self.connected = False

            print(message)
            if message == 'PING':
                await self.send_message('PONG')
                
    async def send_error(self, error: str):
        await self._send(json.dumps({'message': 'ERROR', 'error': error}))

    async def send_warning(self, warning: str):
        await self._send(json.dumps({'message': 'WARNING', 'warning': warning}))

    async def send_dict(self, d: dict):
        if not d.get('message'):
            d['message'] = 'UNDEFINED'
        if not d.get('data'):
            d['data'] = {}
        await self._send(json.dumps(d))

    async def send_message(self, message: str):
        await self._send(json.dumps({'message': message}))

    async def _send(self, message: str):
        if not self.connected:
            return
        
        if not message.endswith('\n'):
            message += '\n'

        for con in self.connections:
            con[1].write(message.encode())
            await con[1].drain()

    async def ping(self):
        while True:
            await self.send('Ping')
            await asyncio.sleep(2)

    async def close(self):
        await self.send_message('CLOSE')
        self.connected = False
        for con in self.connections:
            con[1].close()
            await con[1].wait_closed()
