from binance import enums
from typing import Dict
import traceback

from common import banana
from models.request import Request, BuyRequest, SellRequest
from models.order import Order, BuyOrder, SellOrder
from models.enums import SymbolStatus
from common.db import mongo_db
from config import MARGIN_SIZE, LEVERAGE


class Symbol:
    
    def __init__(self, name: str):
        self.name = name
        self.status = SymbolStatus.BUY_ALLOWED
        self.precision: int = None
        self.requests: Dict[str, Request] = {'buy': None, 'sell': None}
        self.orders: Dict[str, Order] = {'buy': None, 'sell': None}

    async def buy(self, request: BuyRequest) -> str:
        self.status = SymbolStatus.SUBMITTING_BUY_ORDER

        try:
            await banana.submit_buy_market_order(self.name, price=request.trigger.price, precision=self.precision)
        except Exception as e:
            traceback.print_exc()
            return str(e)
        
        self.requests['buy'] = request
        self.status = SymbolStatus.WAITING_FOR_BUY_ORDER_FILL

        return 'OK'
    
    async def sell(self, request: SellRequest) -> str:
        self.status = SymbolStatus.SUBMITTING_SELL_ORDER

        try:
            await banana.submit_sell_market_order(self.name, quantity=self.orders['buy'].quantity, precision=self.precision)
        except Exception as e:
            traceback.print_exc()
            return str(e)
        
        self.requests['sell'] = request
        self.status = SymbolStatus.WAITING_FOR_SELL_ORDER_FILL

        return 'OK'
    
    async def set_filled_buy(self, order: BuyOrder):
        # it doesn't needs to be async (for now) but im doing it for consistency with set_filled_sell
        self.orders['buy'] = order
        self.status = SymbolStatus.SELL_ALLOWED

    async def set_filled_sell(self, order: SellOrder):
        self.orders['sell'] = order
        self.status = SymbolStatus.BUY_ALLOWED
        await self._save_trade()
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