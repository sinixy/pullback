from binance import AsyncClient, BinanceSocketManager, exceptions, enums

from config import MARGIN_SIZE, LEVERAGE, SYMBOLS_EXCHANGE_INITIALIZATION


class Exchange:

    async def init(self, api_key, api_secret, testnet=False):
        self.client: AsyncClient = await AsyncClient.create(api_key, api_secret, testnet=testnet)
        self.bm: BinanceSocketManager = BinanceSocketManager(self.client)
        if SYMBOLS_EXCHANGE_INITIALIZATION:
            await self._init_symbols()

    async def _init_symbols(self):
        from tqdm import tqdm
        from config import SYMBOLS

        for s in tqdm(SYMBOLS, desc='Initializing symbols'):
            await self.set_leverage(s, LEVERAGE)
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
        except exceptions.BinanceAPIException as e:
            if e.code == -4046:
                return
            raise e

    async def submit_buy_market_order(self, symbol, quantity=None, price=None, precision=0):
        if quantity is None:
            if price is None:
                raise Exception('Both quantity and price cannot be undefined at the same time')
            quantity = MARGIN_SIZE * LEVERAGE / price
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
            quantity = MARGIN_SIZE * LEVERAGE / price
        quantity = int(quantity) if precision == 0 else round(quantity, precision)

        await self.client.futures_create_order(
            symbol=symbol,
            side=enums.SIDE_SELL,
            type=enums.FUTURE_ORDER_TYPE_MARKET,
            quantity=quantity
        )
