import asyncio
import traceback
from time import time

from common import logger
from common.db import mongo_db
from models import BuyRequest, SellRequest, Wallet, Symbol
from models.enums import SymbolStatus
from servers import ws


class Trader:

    def __init__(self, wallet: Wallet):
        self.wallet = wallet

    async def handle_request(self, message: dict):
        try:
            await self._handle_request(message)
        except Exception as e:
            traceback.print_exc()
            await ws.send_error(f'handle_request error: {e}')
            await logger.critical(f'handle_request error: {e}', exc_info=True)
            self.wallet.suspend_trading()

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

        if symbol.status != SymbolStatus.BUY_ALLOWED:
            symbol.status = SymbolStatus.BLOCK_NEXT_SELL
            await logger.warning(symbol.name + ' buy not allowed!')
            return
        if self.wallet.is_full():
            symbol.status = SymbolStatus.BLOCK_NEXT_SELL
            await logger.warning('Won\'t buy ' + symbol.name + ' - wallet is full.')
            return

        response = await symbol.buy(request)
        if response == 'OK':
            await logger.info(f'{symbol.name} BUY')
        elif response == 'NO_LIQUIDITY':
            await ws.send_error(f'No liquidity for buy in {symbol.name}')
            await logger.info(f'No liquidity for buy in {symbol.name}')
            symbol.suspend()
        else:
            await ws.send_error(f'FAILED TO BUY {symbol.name}: {response}')
            await logger.info(f'FAILED TO BUY {symbol.name}: {response}')
            symbol.suspend()

    async def handle_sell_request(self, request: SellRequest):
        symbol = self.wallet[request.symbol]
        if symbol.status == SymbolStatus.TRADING_SUSPENDED:
            return
        if symbol.status == SymbolStatus.BLOCK_NEXT_SELL:
            symbol.status = SymbolStatus.BUY_ALLOWED
            return

        buy_status = await self._confirm_buy(symbol)
        if buy_status != 'OK':
            await logger.info(f'CANNOT CONFIRM BUY FOR {symbol.name}: {buy_status}')
            await ws.send_error(f'CANNOT CONFIRM BUY FOR {symbol.name}: {buy_status}')
            symbol.suspend()
            return

        response = await symbol.sell(request)
        if response == 'OK':
            await logger.info(f'{symbol.name} SELL')
        elif response == 'NO_LIQUIDITY':
            await ws.send_error(f'No liquidity for sell in {symbol.name}')
            await logger.info(f'No liquidity for sell in {symbol.name}')
            symbol.suspend()
        else:
            await logger.info(f'FAILED TO SELL {symbol.name}: {response}')
            await ws.send_error(f'FAILED TO SELL {symbol.name}: {response}')

    async def _confirm_buy(self, symbol: Symbol) -> bool:
        submission_timeouted = await symbol.wait_for_buy_submission(symbol)
        if submission_timeouted:
            return 'SUBMISSION_TIMEOUT'
        
        fill_timeouted = await symbol.wait_for_buy_fill(symbol)
        if fill_timeouted:
            return 'FILL_TIMEOUT'
        
        if symbol.status == SymbolStatus.SELL_ALLOWED:
            return 'OK'
        else:
            return f'UNEXPECTED_SYMBOL_STATUS_{symbol.status}'
