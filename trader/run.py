import asyncio
from aiohttp import web

from config import Config
from common import banana
from exceptions import ExchangeInitializationException, WalletInitializationException
from exceptions.handlers import ControllerHanlder

    
async def stop(app):
    print('Stopping the application...')
    await banana.close()

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

    from streams import OrderDataStream
    stream = OrderDataStream(wallet)
    loop.create_task(stream.start())

    from trader import LiveTrader
    trader = LiveTrader(wallet)

    from server.routes import routes
    app = web.Application()
    app['trader'] = trader
    app.add_routes(routes)
    app.on_shutdown.append(stop)
    
    web.run_app(app, port=Config.LOCAL_SERVER_PORT, loop=loop)


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
        print('See ya!')