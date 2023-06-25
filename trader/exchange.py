import asyncio
from binance import AsyncClient, BinanceSocketManager


loop = asyncio.get_event_loop()
client = loop.run_until_complete(AsyncClient.create())
bm = BinanceSocketManager(client)
