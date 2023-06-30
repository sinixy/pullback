import asyncio
import traceback

from config import MODE, UNIX_SOCKET_ADDRESS, SYMBOLS, BINANCE_API_KEY, BINANCE_API_SECRET, TESTNET_BINANCE_API_KEY, TESTNET_BINANCE_API_SECRET
from servers import ws
from common import applogger, banana


def run(loop: asyncio.BaseEventLoop):
    api_key, api_secret, testnet = TESTNET_BINANCE_API_KEY, TESTNET_BINANCE_API_SECRET, True
    if MODE == 'REAL':
        api_key, api_secret, testnet = BINANCE_API_KEY, BINANCE_API_SECRET, False
    loop.run_until_complete(banana.init(api_key, api_secret, testnet))

    from models import Wallet
    wallet = Wallet(SYMBOLS)
    loop.run_until_complete(wallet.init())

    loop.create_task(ws.run())

    from trader import LiveTrader
    trader = LiveTrader(wallet)

    from servers import UnixServer
    unix_server = UnixServer(UNIX_SOCKET_ADDRESS, trader, loop=loop)
    loop.create_task(unix_server.run())

    from streams import OrderDataStream
    stream = OrderDataStream(wallet)
    loop.create_task(stream.start())

    loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        run(loop)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        traceback.print_exc()
        applogger.critical(f'WE\'RE FUCKED {e}', exc_info=True)
        loop.run_until_complete(ws.send_error(f'WE\'RE FUCKED: {e}'))
    finally:
        loop.run_until_complete(banana.close())
        loop.run_until_complete(ws.close())
        print('See ya!')