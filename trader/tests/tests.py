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


async def test_single(client: TestClient):
    duration = 5000
    buy, sell = await generate_trade('ADAUSDT', duration)

    await client.send(json.dumps(buy))
    await asyncio.sleep(duration / 1000)
    await client.send(json.dumps(sell))



async def main():
    await banana.init(TESTNET_BINANCE_API_KEY, TESTNET_BINANCE_API_SECRET, True)
    client = TestClient(UNIX_SOCKET_ADDRESS)
    await client.start()
    
    await test_single(client)

def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())