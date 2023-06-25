import asyncio
import traceback
from time import time

from common import logger
from common.db import mongo_db
from exchange import client
from bot.bot import send_message


class Trader:

    def __init__(self):
        self.trades = {}

    async def handle(self, message: dict):
        try:
            await self._handle(message)
        except Exception as e:
            traceback.print_exc()
            await send_message(f'Handling error: {e}')
            await logger.critical(f'Handling error: {e}', exc_info=True)

    async def _handle(self, message: dict):
        message_type = message.get('message')
        message_data = message.get('data')
        timestamps = {
            'sent': message.get('time'),
            'received': time()
        }
        if message_type == 'BUY_REQUEST':
            await self.buy(message_data, timestamps)
        elif message_type == 'SELL_REQUEST':
            await self.sell(message_data, timestamps)

    async def buy(self, data: dict, timestamps: dict):
        pass

    async def sell(self, data: dict, timestamps: dict):
        pass


class EmulatorTrader(Trader):

    async def _mark_price(self, symbol):
        mark_price = await client.futures_mark_price(symbol=symbol)
        return mark_price['time']/1000, float(mark_price['markPrice'])

    async def buy(self, data: dict, timestamps: dict):
        symbol = data['symbol']
        if self.trades.get(symbol):
            await logger.warning(symbol + ' has been already bought!')
            return
        if len(self.trades.keys()) > 10:
            await logger.warning('Won\'t buy ' + symbol + ' - too many coins.')
            return

        trigger_point_time = data['buy']['triggerPoint']['time'] / 1000
        now = time()
        self.trades[symbol] = {
            'buy': {
                **data['buy'],
                'delay': {
                    'processing': timestamps['sent'] - trigger_point_time,
                    'transmitting': timestamps['received'] - timestamps['sent'],
                    'sending': now - timestamps['received'],
                    'full': now - trigger_point_time
                }
            },
            'sell': {},
            'strategy': data['strategy']
        }

        # emulating await submit trade
        sumbit_time = time()
        await self._mark_price(symbol)

        self.trades[symbol]['buy']['ping'] = time() - sumbit_time

        await logger.info(f'{symbol} BUY {self.trades[symbol]["buy"]}')

    async def sell(self, data: dict, timestamps: dict):
        symbol = data.pop('symbol')

        start = time()
        while not self.trades.get(symbol):
            await logger.info(f'Waiting for {symbol} to sell...')
            await asyncio.sleep(0.1)
            if time() - start > 5:
                await logger.info(f'{symbol} sell timeouted - no trade')
                return
        trade = self.trades[symbol]
        while not trade['buy'].get('ping'):
            await logger.info(f'Waiting for {symbol} confirmation to sell...')
            await asyncio.sleep(0.1)
            if time() - start > 10:
                await logger.info(f'{symbol} sell timeouted - no confirmation')
                del self.trades[symbol]
                return
            
        trigger_point_time = data['triggerPoint']['time'] / 1000
        now = time()
        trade['sell'] = {
            **data,
            'delay': {
                'processing': timestamps['sent'] - trigger_point_time,
                'transmitting': timestamps['received'] - timestamps['sent'],
                'sending': now - timestamps['received'],
                'full': now - trigger_point_time
            }
        }
            
        # emulating await submit trade
        sumbit_time = time()
        await self._mark_price(symbol)

        trade['sell']['ping'] = time() - sumbit_time

        await mongo_db.trades.insert_one({
            'symbol': symbol,
            **trade
        })

        del self.trades[symbol]
        await logger.info(f'{symbol} SELL {trade["sell"]}')