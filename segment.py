from common.db import redis_db
import ta


class Segment:

    def __init__(self, symbol: str, start: int, end: int = None):
        self.symbol = symbol
        self.start = start
        self.end = end

    async def _get_orders(self):
        return await redis_db.xrange(self.symbol, f'{self.start*1000}-0', f'{self.end*1000}-0')

    async def should_buy(self, struct_ema):
        if self.end == None:
            raise AssertionError(f'Undefined end of {self}')
        length = self.end - self.start
        if length < 20 or length > 80:
            return False, {}
        
        ema = [e for e in struct_ema if self.start <= e[0] <= self.end]
        if ema[0][0] != self.start or ema[-1][0] != self.end:
            raise AssertionError(f'Cannot fully retreive EMA for {self}. Current values: {ema[0]} - {ema[-1]}')
        
        orders = [(int(order[b't'])/1000, float(order[b'p'])) for _, order in await self._get_orders()]
        # X = [o[0] for o in orders if self.start <= o[0] <= self.end]
        Y = [o[1] for o in orders if self.start <= o[0] <= self.end]
        if len(Y) == 0:
            msg = f'No order data for {self}.'
            all_orders = await redis_db.xrange(self.symbol)
            if len(all_orders) > 0:
                msg += f' Oldest order: {all_orders[0]}; Latest order: {all_orders[-1]}.'
            else:
                msg += f' No order data in the database for {self.symbol}.'

            raise AssertionError(msg)
        
        price_delta = 1 - min(Y) / Y[0]
        if price_delta < 0.015:
            return False, {'delta': price_delta}
        
        # spikes = await ta.find_spikes(X, Y, ema)
        # if len(spikes['spikesIndx']) > 8:
        #     return False
        # if spikes['biggest'] > 0.008:
        #     return False
        
        return True, {'delta': price_delta}

    def __str__(self):
        return f'<Segment symbol={self.symbol} start={self.start}, end={self.end}>'