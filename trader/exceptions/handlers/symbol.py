from exceptions.handlers.handler import Handler
from exceptions.exceptions import (
    SaveTradeException,
    ChangeStatusTimeoutException,
    UnconfirmedBuyException,
    SubmissionTimeoutException,
    OrderSubmissionException
)

from binance.exceptions import BinanceAPIException


class SymbolHandler(Handler):

    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol

    async def handle(self, e: Exception):
        self.symbol.suspend()
        if isinstance(e, OrderSubmissionException):
            await self.handle_submission(e)
        elif isinstance(e, SaveTradeException):
            await self.handle_save_trade(e)
        elif isinstance(e, ChangeStatusTimeoutException):
            await self.handle_change_status_timeout(e)
        elif isinstance(e, UnconfirmedBuyException):
            await self.handle_unconfirmed_buy(e)
        elif isinstance(e, SubmissionTimeoutException):
            await self.handle_submission_timeout(e)
        else:
            await super().handle(f'{self.symbol.name} error! {e}')

    async def handle_submission(self, e: OrderSubmissionException):
        if isinstance(e.parent_exception, BinanceAPIException):
            await self.handle_api(e)
        else:
            await self._report(f'{self.symbol.name} {e.side} order submission error! {e}')

    async def handle_api(self, e: OrderSubmissionException):
        api_error = e.parent_exception
        if api_error.code == -4131:
            await self._report(f'No liquidity for {e.side} {self.symbol.name}')
        elif api_error.code == -1001:
            await self._warn(f'Failed to {e.side} {self.symbol.name} due to binance internal error!')
            if e.side == 'BUY':
                self.symbol.block_next_sell()
            else:
                self.symbol.sell_until_success()
        else:
            await self._report(f'{self.symbol.name} API error! {e}')

    async def handle_save_trade(self, e: SaveTradeException):
        await self._report(f'Failed to save a trade for {self.symbol.name}! {e}')

    async def handle_change_status_timeout(self, e: ChangeStatusTimeoutException):
        await self._report(f'{self.symbol.name} change status timeout! {e}')
    
    async def handle_unconfirmed_buy(self, e: UnconfirmedBuyException):
        await self._report(f'{self.symbol.name} unconfirmed buy! {e}')

    async def handle_submission_timeout(self, e: SubmissionTimeoutException):
        await self._report(f'{self.symbol.name} submission timeout! {e}')
