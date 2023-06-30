import random
import json
import asyncio

from config import SYMBOLS, TESTNET_BINANCE_API_KEY, TESTNET_BINANCE_API_SECRET, UNIX_SOCKET_ADDRESS
from common import banana
from tests.client import TestClient


async def generate_trade(symbol, duration):
    mark_price = await banana.mark_price(symbol)
    time, price = mark_price['time'], float(mark_price['markPrice'])
    buy_request = {
        "message": "BUY_REQUEST",
        "time": time,
        "data": {
            "symbol": symbol,
            "buy": {
                "time": time,
                "price": price,
                "triggerPoint": {
                    "time": time - random.randint(0, 300),
                    "price": price
                }
            },
            "strategy": {
                "priceChange": 0.0,
                "relativeIncrease": 0.0,
                "segmentLength": 0,
                "latestPump": {
                    "time": 0,
                    "increase": 0.0
                }
            }
        }
    }

    sell_price = price * (1 + random.random() / 100)
    sell_request = {
        "message": "SELL_REQUEST",
        "time": time + duration,
        "data": {
            "symbol": symbol,
            "time": time + duration,
            "price": sell_price,
            "triggerPoint": {
                "time": time + duration - random.randint(0, 300),
                "price": sell_price
            }
        }
    }

    return buy_request, sell_request


async def test_single(client: TestClient, symbol: str, duration: int):
    buy, sell = await generate_trade(symbol, duration)

    await client.send(json.dumps(buy))
    await asyncio.sleep(duration / 1000)
    await client.send(json.dumps(sell))

async def test_single_short(client: TestClient, symbol: str):
    await test_single(client, symbol, 200)

async def test_multiple(client, loop, data):
    for symbol, duration in data:
        loop.create_task(test_single(client, symbol, duration))
        await asyncio.sleep(max(0.2, random.random()))

async def main(loop):
    await banana.init(TESTNET_BINANCE_API_KEY, TESTNET_BINANCE_API_SECRET, True)
    client = TestClient(UNIX_SOCKET_ADDRESS)
    await client.start()
    
    symbols = random.choices(SYMBOLS, k=8)
    data = []
    for s in symbols:
        if random.random() < 0.4:
            data.append((s, 200))
        else:
            data.append((s, 5000))
    print('Testing', data)
    await test_multiple(client, loop, data)

def run():
    loop = asyncio.get_event_loop()
    loop.create_task(main(loop))
    loop.run_forever()