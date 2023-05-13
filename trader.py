from collections import deque
from time import time
import asyncio

import ta
from exchange import client
from segment import Segment
from common import logger
from common.db import mongo_db


class RollingWindowDeque(deque):

    def __init__(self, iterable, condition, maxlen=None):
        super().__init__(iterable, maxlen)
        self.condition = condition

    def roll(self):
        if len(self) == 0:
            return
        while self.condition(self[0], self[-1]):
            self.popleft()

class PriceWindow:
    '''
        This is a kind of time window that allows only a single WHOLE time period of self.size milliseconds in it.
        For example, if size=1000 - 1 second, values can be:
        - [5.1, 5.45, 5.61, 5.999999]
        - [21.71, 21.9]

        But values cannot be [4.5, 4.7, 5.4, 5.5] or [21.71, 22, 22.71].
        That is, int(value[0]) must remain constant for each value[0] in self.values.
    '''

    def __init__(self, *values, size=1000):
        # values = [(t1, p1), (t2, p2), ..., (tn, pn)]
        self.values = list(values)
        self.size = size
        self.normalized_values = [(value[0] / self.size, value[1]) for value in self.values]
        self._validate_window()

    def _validate_window(self):
        if len(self.normalized_values) > 1:
            if len(set([int(value[0]) for value in self.normalized_values])) != 1:
                raise ValueError("All values must belong to the same time period")

    def add_or_return_difference(self, value):
        normalized_time = value[0] / self.size
        if len(self.normalized_values) == 0 or int(normalized_time) == int(self.normalized_values[0][0]):
            self.values.append(value)
            self.normalized_values.append((normalized_time, value[1]))
        else:
            return int(normalized_time) - int(self.normalized_values[0][0])
        
    def _get_window_start(self):
        return int(self.normalized_values[0][0]) * self.size / 1000
        
    def max(self):
        return self._get_window_start(), max([value[1] for value in self.values])
    
    def min(self):
        return self._get_window_start(), min([value[1] for value in self.values])
    
    def mean(self):
        return self._get_window_start(), sum([value[1] for value in self.values]) / len(self.values)

    def __str__(self):
        return str(self.values)


class Trader:

    def __init__(self, symbols, window_size=1000, debug=False):
        self.symbols = symbols
        self.window_size = window_size
        self.debug = debug

        self._semaphore = asyncio.Semaphore(128)

        self.ema = {}
        self.trades = {}
        condition = lambda first, last: last[0] - first[0] > 90
        for s in self.symbols:
            self.ema[s] = {
                'signal': RollingWindowDeque([], condition),
                'struct': RollingWindowDeque([], condition),
                'window': PriceWindow(size=self.window_size),
                'segment': None
            }

    def init(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._init_emas())

    async def _init_emas(self):
        prices = await client.futures_mark_price()
        for p in prices:
            if asset := self.ema.get(p['symbol']):
                p0 = (int(p['time'] / 1000), float(p['markPrice']))
                asset['signal'].append(p0)
                asset['struct'].append(p0)

        await logger.info('Trader initialized')

    def update_emas(self, symbol, current_max_price, current_mean_price):
        asset = self[symbol]
        previous_signal_ema = asset['signal'][-1]
        previous_struct_ema = asset['struct'][-1]
        current_signal_ema = (
            current_max_price[0],
            ta.ema(previous_signal_ema[1], current_max_price[1], 50)
        )
        current_struct_ema = (
            current_mean_price[0],
            ta.ema(previous_struct_ema[1], current_mean_price[1], 4)
        )
        asset['signal'].append(current_signal_ema)
        asset['struct'].append(current_struct_ema)

    async def update_segment(self, symbol, ping):
        asset = self[symbol]
        window = asset['window']

        if asset['segment']:
            if asset['signal'][-1][1] <= asset['struct'][-1][1]:
                segment = asset['segment']
                asset['segment'] = None
                if not self.trades.get(symbol):
                    segment.end = asset['struct'][-1][0]
                    should_buy, checks = await segment.should_buy()
                    if should_buy:
                        await logger.info(f'{symbol} has fallen by {checks["delta"]*100 :.2f}% - trying to buy it...')
                        await self.buy(symbol, ping)
            else:
                asset['segment'].update_extremums(minp=window.min()[1], maxp=window.max()[1])

        elif asset['signal'][-1][1] > asset['struct'][-1][1]:
            asset['segment'] = Segment(symbol, minp=window.min()[1], maxp=window.max()[1], start=asset['struct'][-1][0])

    async def update_trades(self, symbol, ping):
        trade = self.trades.get(symbol)
        if not trade:
            return
        
        asset = self[symbol]
        if asset['signal'][-1][1] > asset['struct'][-1][1]:
            # ejecting the trade before submitting it so a race condition won't occure
            trade = self.trades.pop(symbol)
            await logger.info(f'{symbol} SIGNAL crossed over STRUCT - trying to sell it...')
            await self.sell(symbol, trade, ping)

    async def _handle_message(self, message):
        symbol = message['s']
        asset = self[symbol]

        t0, p0 = message['T'], float(message['p'])
        difference = asset['window'].add_or_return_difference((t0, p0))
        # difference=1 means that we received order data for the next second,
        # so we just need to calculate ema once for the current complete window.
        # difference > 1 indicates that there were no orders for more than 1 second,
        # therefore we need to calculate additional (difference - 1) values for ema to ensure smoothness.
        # assuming that the price remained constant during the gap in order data.
        if difference:
            ping = time() * 1000 - t0
            current_max_price = asset['window'].max()
            current_mean_price = asset['window'].mean()
            for i in range(difference):
                next_max_price = (current_max_price[0] + i*self.window_size/1000, current_max_price[1])
                next_mean_price = (current_mean_price[0] + i*self.window_size/1000, current_mean_price[1])
                self.update_emas(symbol, next_max_price, next_mean_price)

            await self.update_segment(symbol, ping)
            await self.update_trades(symbol, ping)

            asset['window'] = PriceWindow((t0, p0), size=self.window_size)
            asset['signal'].roll()
            asset['struct'].roll()
        
    async def handle_message(self, message):
        async with self._semaphore:
            await self._handle_message(message)

    async def buy(self):
        pass

    async def sell(self):
        pass

    def __getitem__(self, symbol):
        return self.ema[symbol]
    

class BacktestTrader(Trader):

    async def buy(self, symbol):
        if self.trades.get(symbol):
            return
        
        time, price = self[symbol]['struct'][-1]
        self.trades[symbol] = {'buy': {'time': time, 'price': price}, 'sell': {}}

    async def sell(self, symbol, trade):
        time, price = self[symbol]['struct'][-1]
        self.trades[symbol]['sell'] = {'time': time, 'price': price}
        await mongo_db.testTrades.insert_one({'symbol': symbol, **self.trades.pop(symbol)})


class EmulatorTrader(Trader):

    async def _mark_price(self, symbol):
        mark_price = await client.futures_mark_price(symbol=symbol)
        return mark_price['time']/1000, float(mark_price['markPrice'])

    async def buy(self, symbol, ping):
        if self.trades.get(symbol):
            await logger.warning(symbol + ' has been already bought!')
            return
        if len(self.trades.keys()) > 5:
            await logger.warning('Won\'t buy ' + symbol + ' - too many coins.')
            return
        
        # setting dummy data for the symbol before submitting the trade so a race condition won't occure
        self.trades[symbol] = {
            'buy': {},
            'sell': {},
        }

        # emulating await submit trade
        sumbit_time = time()
        await self._mark_price(symbol)

        self.trades[symbol]['buy'] = {'time': time(), 'submitTime': sumbit_time, 'price': self[symbol]['struct'][-1][1], 'ping': ping}

        await logger.info(f'{symbol} BUY {self.trades[symbol]["buy"]}')

    async def sell(self, symbol, trade, ping):
        # emulating await submit trade
        sumbit_time = time()
        await self._mark_price(symbol)

        trade['sell'] = {'time': time(), 'submitTime': sumbit_time, 'price': self[symbol]['struct'][-1][1], 'ping': ping}

        await mongo_db.trades.insert_one({
            'symbol': symbol,
            **trade
        })

        await logger.info(f'{symbol} SELL {trade["sell"]}')