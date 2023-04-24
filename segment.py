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
        if self.end - self.start < 20:
            return False
        
        ema = [e for e in struct_ema if self.start <= e[0] <= self.end]
        if ema[0][0] != self.start or ema[-1][0] != self.end:
            raise AssertionError(f'Cannot fully retreive EMA for {self}')
        
        orders = [(int(order[b't'])/1000, float(order[b'p'])) for _, order in await self._get_orders()]
        # X = [o[0] for o in orders if self.start <= o[0] <= self.end]
        Y = [o[1] for o in orders if self.start <= o[0] <= self.end]
        price_delta = 1 - min(Y) / Y[0]
        if price_delta < 0.015:
            return False
        
        # spikes = await ta.find_spikes(X, Y, ema)
        # if len(spikes['spikesIndx']) > 8:
        #     return False
        # if spikes['biggest'] > 0.008:
        #     return False
        
        return True, {'delta': price_delta}

    def __str__(self):
        return f'<Segment start={self.start}, end={self.end}>'