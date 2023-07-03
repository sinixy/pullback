import asyncio

from config import MODE, UNIX_SOCKET_ADDRESS, SYMBOLS, BINANCE_API_KEY, BINANCE_API_SECRET, TESTNET_BINANCE_API_KEY, TESTNET_BINANCE_API_SECRET
from servers import ws
from common import banana
from exceptions import ExchangeInitializationException, WalletInitializationException
from exceptions.handlers import ControllerHanlder


def run(loop: asyncio.BaseEventLoop):
    api_key, api_secret, testnet = TESTNET_BINANCE_API_KEY, TESTNET_BINANCE_API_SECRET, True
    if MODE == 'REAL':
        api_key, api_secret, testnet = BINANCE_API_KEY, BINANCE_API_SECRET, False

    try:
        loop.run_until_complete(banana.init(api_key, api_secret, testnet))
    except Exception as e:
        raise ExchangeInitializationException(e)

    from models import Wallet
    wallet = Wallet(SYMBOLS)
    try:
        loop.run_until_complete(wallet.init())
    except Exception as e:
        raise WalletInitializationException(e)

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
    exceptions_handler = ControllerHanlder()

    try:
        run(loop)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        loop.run_until_complete(exceptions_handler.handle(e))
    finally:
        loop.run_until_complete(banana.close())
        loop.run_until_complete(ws.close())
        print('See ya!')