from typing import Dict, List
from time import time
import asyncio

from common import banana, logger
from models.request import Request, BuyRequest, SellRequest
from models.order import Order, BuyOrder, SellOrder
from models.enums import SymbolStatus
from db import trades_db
from servers import ws

from exceptions.handlers import SymbolHandler
from exceptions import (
    SaveTradeException,
    ChangeStatusTimeoutException,
    UnconfirmedBuyException,
    UnexpectedSymbolStatusException,
    SubmissionTimeoutException,
    OrderSubmissionException
)


class Symbol:
    
    def __init__(self, name: str, loop=None):
        self.name = name
        self.status = SymbolStatus.BUY_ALLOWED
        self.precision: int = None
        self.requests: Dict[str, Request] = {'buy': None, 'sell': None}
        self.orders: Dict[str, Order] = {'buy': None, 'sell': None}
        self.fills: Dict[str, List[Order]] = {'buy': [], 'sell': []}

        self._loop: asyncio.BaseEventLoop = loop
        if not self._loop:
            self._loop = asyncio.get_event_loop()

        self.exceptions_handler = SymbolHandler(self)

    async def buy(self, price: float):
        await logger.info(f'Buying {self.name} at ${price}')
        try:
            await self._buy(price)
        except Exception as e:
            await self.exceptions_handler.handle(OrderSubmissionException('BUY', e))

    async def _buy(self, price: float):
        self.status = SymbolStatus.SUBMITTING_BUY_ORDER
        self._loop.create_task(self.watch_buy_submission_timeout())

        await banana.submit_buy_market_order(self.name, price=price, precision=self.precision)
        
        await logger.info(f'{self.name} buy order submitted')
        self.status = SymbolStatus.WAITING_FOR_BUY_ORDER_FILL

    async def sell(self):
        await logger.info(f'Selling {self.name}')
        try:
            await self._sell()
        except Exception as e:
            await self.exceptions_handler.handle(OrderSubmissionException('SELL', e))
    
    async def _sell(self):
        self.status = SymbolStatus.SUBMITTING_SELL_ORDER
        self._loop.create_task(self.watch_sell_submission_timeout())

        await banana.submit_sell_market_order(self.name, quantity=self.orders['buy'].quantity, precision=self.precision)
        
        await logger.info(f'{self.name} sell order submitted')
        self.status = SymbolStatus.WAITING_FOR_SELL_ORDER_FILL
    
    async def confirm_buy(self) -> bool:
        await logger.info(f'Confirming {self.name} buy')
        try:
            await self._confirm_buy()
        except Exception as e:
            await self.exceptions_handler.handle(UnconfirmedBuyException(e))
            return False
        
        await logger.info(f'{self.name} buy confirmed')
        return True

    async def _confirm_buy(self):
        await self.wait_for_buy_submission()
        
        await self.wait_for_buy_fill()
        
        if self.status != SymbolStatus.SELL_ALLOWED:
            raise UnexpectedSymbolStatusException(self.status)
        
    def set_request_buy(self, request: BuyRequest):
        self.requests['buy'] = request

    def set_request_sell(self, request: SellRequest):
        self.requests['sell'] = request

    def add_fill(self, message):
        side = message['S']
        if side == 'BUY':
            self.fills['buy'].append(BuyOrder.from_dict(message))
        else:
            self.fills['sell'].append(SellOrder.from_dict(message))

    async def set_filled(self, message: dict):
        self.add_fill(message)
        side = message['S']
        if side == 'BUY':
            await self.set_filled_buy(BuyOrder.from_dict(message))
        else:
            await self.set_filled_sell(SellOrder.from_dict(message))
            await self.save_trade()
    
    async def set_filled_buy(self, order: BuyOrder):
        await logger.info(f'{self.name} buy order filled')
        self.orders['buy'] = order
        self.status = SymbolStatus.SELL_ALLOWED

    async def set_filled_sell(self, order: SellOrder):
        await logger.info(f'{self.name} sell order filled')
        self.orders['sell'] = order
        self.status = SymbolStatus.BUY_ALLOWED

    async def save_trade(self):
        await logger.info(f'Saving {self.name} trade')
        try:
            await trades_db.insert_trade(self.name, self.requests, self.orders, self.fills)
        except Exception as e:
            self.exceptions_handler.handle(SaveTradeException(e))
        await logger.info(f'{self.name} trade saved')
        self.reset()

    def reset(self):
        self.requests = {'buy': None, 'sell': None}
        self.orders = {'buy': None, 'sell': None}
        self.fills = {'buy': [], 'sell': []}

    def suspend(self):
        self.status = SymbolStatus.TRADING_SUSPENDED

    def is_suspended(self) -> bool:
        return self.status == SymbolStatus.TRADING_SUSPENDED
    
    def block_next_sell(self):
        self.status = SymbolStatus.BLOCK_NEXT_SELL

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

    def sell_until_success(self):
        self._loop.create_task(self._sell_until_success())

    async def _sell_until_success(self):
        retries = 1
        sold = False
        while not sold:
            if retries > 1000:
                await logger.error(f'Too many retries selling {self.name}!')
                await ws.send_error(f'Too many retries selling {self.name}!')
                break

            await logger.info(f'(#{retries}) Trying to sell {self.name}...')
            try:
                await self._sell()
                sold = True
            except Exception as e:
                await logger.info(f'(#{retries}) Failed to sell {self.name}: {e}')
                await asyncio.sleep(0.2)
                retries += 1

        if sold:
            self.status = SymbolStatus.BUY_ALLOWED
            await logger.info(f'Sold {self.name} after {retries} retries!')
            await ws.send_message(f'Sold {self.name} after {retries} retries!')