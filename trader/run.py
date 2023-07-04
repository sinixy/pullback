import asyncio

from config import Config
from servers import ws
from common import banana
from exceptions import ExchangeInitializationException, WalletInitializationException
from exceptions.handlers import ControllerHanlder


def run(loop: asyncio.BaseEventLoop):
    from db import config_db, trades_db
    config_db.init(Config.MONGODB_HOST, Config.MONGODB_NAME)
    trades_db.init(Config.MONGODB_HOST, Config.MONGODB_NAME)

    Config.init()

    api_key, api_secret, testnet = Config.TESTNET_BINANCE_API_KEY, Config.TESTNET_BINANCE_API_SECRET, True
    if Config.MODE == 'REAL':
        api_key, api_secret, testnet = Config.BINANCE_API_KEY, Config.BINANCE_API_SECRET, False

    try:
        loop.run_until_complete(
            banana.init(
                api_key,
                api_secret,
                testnet=testnet,
                init_symbols=Config.SYMBOLS_EXCHANGE_INITIALIZATION,
                symbols=Config.SYMBOLS,
                margin_size=Config.MARGIN_SIZE,
                leverage=Config.LEVERAGE
            )
        )
    except Exception as e:
        raise ExchangeInitializationException(e)

    from models import Wallet
    wallet = Wallet(Config.SYMBOLS, Config.MAX_ACTIVE_TRADES)
    try:
        loop.run_until_complete(wallet.init())
    except Exception as e:
        raise WalletInitializationException(e)

    from trader import LiveTrader
    from servers import UnixServer
    trader = LiveTrader(wallet)
    unix_server = UnixServer(Config.UNIX_SOCKET_ADDRESS, trader, loop=loop)
    loop.create_task(unix_server.run())

    ws.init(Config.WEBSOCKET_HOST, Config.WEBSOCKET_PORT)
    loop.create_task(ws.run())

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