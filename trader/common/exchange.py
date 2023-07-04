from binance import AsyncClient, BinanceSocketManager, enums
from binance.exceptions import BinanceAPIException
from typing import List


class Exchange:

    def __init__(self):
        self.symbols: List[str] = []
        self.margin_size: float = 20
        self.leverage: int = 20

        self.client: AsyncClient = None
        self.bm: BinanceSocketManager = None

    async def init(
            self,
            api_key,
            api_secret,
            testnet=False,
            init_symbols=False,
            symbols=[],
            margin_size=20,
            leverage=20
    ):
        self.symbols = symbols
        self.margin_size = margin_size
        self.leverage = leverage

        self.client = await AsyncClient.create(api_key, api_secret, testnet=testnet)
        self.bm = BinanceSocketManager(self.client)
        
        if init_symbols:
            await self._init_symbols()

    async def _init_symbols(self):
        from tqdm import tqdm

        for s in tqdm(self.symbols, desc='Initializing symbols'):
            await self.set_leverage(s, self.leverage)
            await self.set_margin_type(s, 'ISOLATED')

    async def exchange_info(self):
        return await self.client.futures_exchange_info()

    async def mark_price(self, symbol) -> dict:
        return await self.client.futures_mark_price(symbol=symbol)

    async def close(self):
        await self.client.close_connection()

    async def set_leverage(self, symbol, leverage=20):
        await self.client.futures_change_leverage(symbol=symbol, leverage=leverage)

    async def set_margin_type(self, symbol, margin_type='ISOLATED'):
        try:
            await self.client.futures_change_margin_type(symbol=symbol, marginType=margin_type)
        except BinanceAPIException as e:
            if e.code == -4046:
                return
            raise e

    async def submit_buy_market_order(self, symbol, quantity=None, price=None, precision=0):
        if quantity is None:
            if price is None:
                raise Exception('Both quantity and price cannot be undefined at the same time')
            quantity = self.margin_size * self.leverage / price
        quantity = int(quantity) if precision == 0 else round(quantity, precision)

        await self.client.futures_create_order(
            symbol=symbol,
            side=enums.SIDE_BUY,
            type=enums.FUTURE_ORDER_TYPE_MARKET,
            quantity=quantity
        )

    async def submit_sell_market_order(self, symbol, quantity=None, price=None, precision=0):
        if quantity is None:
            if price is None:
                raise Exception('Both quantity and price cannot be undefined at the same time')
            quantity = self.margin_size * self.leverage / price
        quantity = int(quantity) if precision == 0 else round(quantity, precision)

        await self.client.futures_create_order(
            symbol=symbol,
            side=enums.SIDE_SELL,
            type=enums.FUTURE_ORDER_TYPE_MARKET,
            quantity=quantity
        )
