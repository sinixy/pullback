from time import time

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
        timestamps = {
            'sent': message.get('time'),
            'received': time()
        }
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
        if symbol.status == SymbolStatus.TRADING_SUSPENDED:
            return
        if symbol.status != SymbolStatus.BUY_ALLOWED or self.wallet.is_full():
            symbol.status = SymbolStatus.BLOCK_NEXT_SELL
            return
        
        await symbol.buy(request)

    async def handle_sell_request(self, request: SellRequest):
        symbol = self.wallet[request.symbol]
        if symbol.status == SymbolStatus.TRADING_SUSPENDED:
            return
        if symbol.status == SymbolStatus.BLOCK_NEXT_SELL:
            symbol.status = SymbolStatus.BUY_ALLOWED
            return
        
        confirmed = await symbol.confirm_buy()
        if confirmed:
            await symbol.sell(request)
