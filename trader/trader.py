from common import logger
from models import BuyRequest, SellRequest, Wallet
from models.enums import SymbolStatus
from exceptions import HandleRequestException
from exceptions.handlers import TraderHandler


class Trader:

    def __init__(self, wallet: Wallet):
        self.wallet = wallet
        self.exceptions_handler = TraderHandler(self)

    async def handle_request(self, message: dict):
        try:
            await self._handle_request(message)
        except Exception as e:
            await self.exceptions_handler.handle(HandleRequestException(message, e))

    async def _handle_request(self, message: dict):
        message_type = message.get('message')
        message_symbol = message.get("data", {}).get("symbol")
        await logger.info(f'Received {message_type} for {message_symbol}')
        if message_type == 'BUY_REQUEST':
            await self.handle_buy_request(BuyRequest.from_dict(message))
        elif message_type == 'SELL_REQUEST':
            await self.handle_sell_request(SellRequest.from_dict(message))

    async def handle_buy_request(self, request: BuyRequest):
        pass

    async def handle_sell_request(self, request: SellRequest):
        pass


class LiveTrader(Trader):

    async def handle_buy_request(self, request: BuyRequest):
        symbol = self.wallet[request.symbol]
        if symbol.is_suspended():
            await logger.info(f'{symbol.name} buy refused: suspended from trading')
            return
        if symbol.status != SymbolStatus.BUY_ALLOWED:
            await logger.info(f'{symbol.name} buy refused: buy is not allowed')
            symbol.status = SymbolStatus.BLOCK_NEXT_SELL
            return
        if self.wallet.is_full():
            await logger.info(f'{symbol.name} buy refused: wallet is full')
            symbol.status = SymbolStatus.BLOCK_NEXT_SELL
            return
        
        symbol.set_request_buy(request)
        await symbol.buy(request.trigger.price)

    async def handle_sell_request(self, request: SellRequest):
        symbol = self.wallet[request.symbol]
        if symbol.is_suspended():
            await logger.info(f'{symbol.name} sell refused: suspended from trading')
            return
        if symbol.status == SymbolStatus.BLOCK_NEXT_SELL:
            await logger.info(f'{symbol.name} sell refused: blocked')
            symbol.status = SymbolStatus.BUY_ALLOWED
            return
        
        symbol.set_request_sell(request)
        confirmed = await symbol.confirm_buy()
        if confirmed:
            await symbol.sell()
