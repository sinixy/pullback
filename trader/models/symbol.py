from typing import Dict
from time import time
import traceback
import asyncio

from common import banana, logger
from models.request import Request, BuyRequest, SellRequest
from models.order import Order, BuyOrder, SellOrder
from models.enums import SymbolStatus
from common.db import mongo_db
from servers import ws


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

    async def buy(self, request: BuyRequest) -> str:
        self.requests['buy'] = request
        self.status = SymbolStatus.SUBMITTING_BUY_ORDER
        self._loop.create_task(self.watch_buy_submission_timeout())

        try:
            await banana.submit_buy_market_order(self.name, price=request.trigger.price, precision=self.precision)
        except Exception as e:
            traceback.print_exc()
            return str(e)
        
        self.status = SymbolStatus.WAITING_FOR_BUY_ORDER_FILL

        return 'OK'
    
    async def sell(self, request: SellRequest) -> str:
        self.requests['sell'] = request
        self.status = SymbolStatus.SUBMITTING_SELL_ORDER
        self._loop.create_task(self.watch_sell_submission_timeout())

        try:
            await banana.submit_sell_market_order(self.name, quantity=self.orders['buy'].quantity, precision=self.precision)
        except Exception as e:
            traceback.print_exc()
            return str(e)
        
        self.status = SymbolStatus.WAITING_FOR_SELL_ORDER_FILL

        return 'OK'
    
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
            await logger.error(f'Save trade error: {e}')
            await ws.send_error(f'Save trade error: {e}')
            self.suspend()
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

    async def _wait_for_symbol_status_change(self, status, timeout=5, raise_error=False) -> bool:
        start = time()
        while self.status == status:
            await asyncio.sleep(0.1)
            if time() - start > timeout:
                return True
        if raise_error:
            raise Exception(f'Waiting for symbol status-{status} change timeouted')
        else:
            return False
    
    async def wait_for_buy_submission(self, raise_error=False) -> bool:
        return await self._wait_for_symbol_status_change(SymbolStatus.SUBMITTING_BUY_ORDER, raise_error)
    
    async def wait_for_buy_fill(self, raise_error=False) -> bool:
        return await self._wait_for_symbol_status_change(SymbolStatus.WAITING_FOR_BUY_ORDER_FILL, raise_error)
    
    async def wait_for_sell_submission(self, raise_error=False) -> bool:
        return await self._wait_for_symbol_status_change(SymbolStatus.SUBMITTING_SELL_ORDER, raise_error)
    
    async def wait_for_sell_fill(self, raise_error=False) -> bool:
        return await self._wait_for_symbol_status_change(SymbolStatus.WAITING_FOR_SELL_ORDER_FILL, raise_error)
    
    async def watch_buy_submission_timeout(self):
        await logger.info(f'Watching {self.name} buy submission') 
        try:
            await self.wait_for_buy_submission(True)
        except Exception as e:
            await logger.error(f'{self.name} BUY SUBMISSION TIMEOUTED')
            await ws.send_error(f'{self.name} BUY SUBMISSION TIMEOUTED')
            self.suspend()

    async def watch_sell_submission_timeout(self):
        await logger.info(f'Watching {self.name} sell submission') 
        try:
            await self.wait_for_sell_submission(True)
        except Exception as e:
            await logger.error(f'{self.name} SELL SUBMISSION TIMEOUTED')
            await ws.send_error(f'{self.name} SELL SUBMISSION TIMEOUTED')
            self.suspend()