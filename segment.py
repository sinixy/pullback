class Segment:

    def __init__(self, symbol: str, minp: float, maxp: float, start: int, end: int = None):
        self.symbol = symbol
        self.min = minp
        self.max = maxp
        self.start = start
        self.end = end

    def update_extremums(self, minp, maxp):
        if minp < self.min:
            self.min = minp
        if maxp > self.max:
            self.max = maxp

    async def should_buy(self):
        if self.end == None:
            raise AssertionError(f'Undefined end of {self}')
        
        length = self.end - self.start
        if length < 20 or length > 80:
            return False, {}
        
        # ema = [e for e in struct_ema if self.start <= e[0] <= self.end]
        # if ema[0][0] != self.start or ema[-1][0] != self.end:
        #     raise AssertionError(f'Cannot fully retreive EMA for {self}. Current values: {ema[0]} - {ema[-1]}')
        
        price_delta = 1 - self.min / self.max
        if price_delta < 0.015:
            return False, {'delta': price_delta}

        return True, {'delta': price_delta}

    def __str__(self):
        return f'<Segment symbol={self.symbol} start={self.start}, end={self.end}>'