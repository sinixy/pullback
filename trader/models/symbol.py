from typing import Dict
from time import time
import asyncio

from common import banana
from models.request import Request, BuyRequest, SellRequest
from models.order import Order, BuyOrder, SellOrder
from models.enums import SymbolStatus
from common.db import mongo_db
from exceptions.handlers import SymbolHandler
from exceptions import (
    SaveTradeException,
    ChangeStatusTimeoutException,
    UnconfirmedBuyException,
    UnexpectedSymbolStatusException,
    SubmissionTimeoutException
)


class Symbol:
    
    def __init__(self, name: str, loop=None):
        self.name = name
        self.status = SymbolStatus.BUY_ALLOWED
        self.precision: int = None
        self.requests: Dict[str, Request] = {'buy': None, 'sell': None}
        self.orders: Dict[str, Order] = {'buy': None, 'sell': None}

        self._loop: asyncio.BaseEventLoop = loop
        if not self._loop:
            self._loop = asyncio.get_event_loop()

        self.exceptions_handler = SymbolHandler(self)

    async def buy(self, request: BuyRequest):
        try:
            await self._buy(request)
        except Exception as e:
            await self.exceptions_handler.handle(e)

    async def _buy(self, request: BuyRequest):
        self.requests['buy'] = request
        self.status = SymbolStatus.SUBMITTING_BUY_ORDER
        self._loop.create_task(self.watch_buy_submission_timeout())

        await banana.submit_buy_market_order(self.name, price=request.trigger.price, precision=self.precision)
        
        self.status = SymbolStatus.WAITING_FOR_BUY_ORDER_FILL

    async def sell(self, request: SellRequest):
        try:
            await self._sell(request)
        except Exception as e:
            await self.exceptions_handler.handle(e)
    
    async def _sell(self, request: SellRequest) -> str:
        self.requests['sell'] = request
        self.status = SymbolStatus.SUBMITTING_SELL_ORDER
        self._loop.create_task(self.watch_sell_submission_timeout())

        await banana.submit_sell_market_order(self.name, quantity=self.orders['buy'].quantity, precision=self.precision)
        
        self.status = SymbolStatus.WAITING_FOR_SELL_ORDER_FILL
    
    async def confirm_buy(self) -> bool:
        try:
            await self._confirm_buy()
        except Exception as e:
            await self.exceptions_handler.handle(UnconfirmedBuyException(e))
            return False
        return True

    async def _confirm_buy(self):
        await self.wait_for_buy_submission()
        
        await self.wait_for_buy_fill()
        
        if self.status != SymbolStatus.SELL_ALLOWED:
            raise UnexpectedSymbolStatusException(self.status)
    
    async def set_filled_buy(self, order: BuyOrder):
        # it doesn't needs to be async (for now) but im doing it for consistency with set_filled_sell
        self.orders['buy'] = order
        self.status = SymbolStatus.SELL_ALLOWED

    async def set_filled_sell(self, order: SellOrder):
        self.orders['sell'] = order
        self.status = SymbolStatus.BUY_ALLOWED
        try:
            await self._save_trade()
        except Exception as e:
            self.exceptions_handler.handle(SaveTradeException(e))
        self._reset()

    async def _save_trade(self):
        await mongo_db.trades.insert_one({
            'symbol': self.name,
            'time': self.requests['buy'].trigger.time,
            'requests': {
                'buy': self.requests['buy'].to_dict(),
                'sell': self.requests['sell'].to_dict()
            },
            'orders': {
                'buy': self.orders['buy'].to_dict(),
                'sell': self.orders['sell'].to_dict()
            }
        })

    def _reset(self):
        self.requests = {'buy': None, 'sell': None}
        self.orders = {'buy': None, 'sell': None}

    def suspend(self):
        self.status = SymbolStatus.TRADING_SUSPENDED
        self._reset()

    async def _wait_for_symbol_status_change(self, status, timeout=5):
        start = time()
        while self.status == status:
            await asyncio.sleep(0.1)
            if time() - start > timeout:
                raise ChangeStatusTimeoutException(status, timeout)
    
    async def wait_for_buy_submission(self):
        return await self._wait_for_symbol_status_change(SymbolStatus.SUBMITTING_BUY_ORDER)
    
    async def wait_for_buy_fill(self):
        return await self._wait_for_symbol_status_change(SymbolStatus.WAITING_FOR_BUY_ORDER_FILL)
    
    async def wait_for_sell_submission(self):
        return await self._wait_for_symbol_status_change(SymbolStatus.SUBMITTING_SELL_ORDER)
    
    async def wait_for_sell_fill(self):
        return await self._wait_for_symbol_status_change(SymbolStatus.WAITING_FOR_SELL_ORDER_FILL)
    
    async def watch_buy_submission_timeout(self):
        # "watches" are supposed to be run as tasks unlike the "waits"
        try:
            await self.wait_for_buy_submission()
        except Exception as e:
            await self.exceptions_handler.handle(SubmissionTimeoutException('BUY', e))

    async def watch_sell_submission_timeout(self):
        try:
            await self.wait_for_sell_submission()
        except Exception as e:
            await self.exceptions_handler.handle(SubmissionTimeoutException('SELL', e))