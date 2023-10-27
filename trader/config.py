from typing import List
import os


class Config:
    MONGODB_HOST = os.environ['MONGODB_HOST']
    MONGODB_NAME = os.environ['MONGODB_NAME']

    LOCAL_SERVER_PORT = os.environ['LOCAL_SERVER_PORT']

    BINANCE_API_KEY = os.environ['BINANCE_API_KEY']
    BINANCE_API_SECRET = os.environ['BINANCE_API_SECRET']
    TESTNET_BINANCE_API_KEY = os.environ['TESTNET_BINANCE_API_KEY']
    TESTNET_BINANCE_API_SECRET = os.environ['TESTNET_BINANCE_API_SECRET']

    MODE: str = ''
    SYMBOLS_EXCHANGE_INITIALIZATION: bool = False
    MARGIN_SIZE: int = 0
    LEVERAGE: int = 0
    MAX_ACTIVE_TRADES: int = 0

    SYMBOLS: List[str] = []

    @classmethod
    def init(cls):
        from db import config_db
        
        common_cofig_doc = config_db.get_common()
        trader_config_doc = config_db.get_trader()

        cls.MODE = trader_config_doc['mode']
        cls.SYMBOLS_EXCHANGE_INITIALIZATION = trader_config_doc['symbolsExchangeInitialization']
        cls.MARGIN_SIZE = trader_config_doc['marginSize']
        cls.LEVERAGE = trader_config_doc['leverage']
        cls.MAX_ACTIVE_TRADES = trader_config_doc['maxActiveTrades']

        cls.SYMBOLS = common_cofig_doc['symbols']