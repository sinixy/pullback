class Order:

    def __init__(self, id: int, symbol: str, time: int, status: str, side: str, price: float, quantity: float):
        self.id = id
        self.symbol = symbol
        self.time = time
        self.status = status
        self.side = side
        self.price = price
        self.quantity = quantity

    @classmethod
    def from_dict(cls, d: dict):
        pass
    
    def to_dict(self):
        pass


class BuyOrder(Order):

    def __init__(self, id: int, symbol: str, time: int, status: str, side: str, price: float, quantity: float):
        super().__init__(id, symbol, time, status, side, price, quantity)

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d['t'],
            d['s'],
            d['T'],
            d['X'],
            d['S'],
            float(d['ap']),
            float(d['q'])
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'time': self.time,
            'status': self.status,
            'side': self.side,
            'price': self.price,
            'quantity': self.quantity
        }


class SellOrder(Order):

    def __init__(self, id: int, symbol: str, time: int, status: str, side: str, price: float, quantity: float, profit: float):
        super().__init__(id, symbol, time, status, side, price, quantity)
        self.profit = profit

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            d['t'],
            d['s'],
            d['T'],
            d['X'],
            d['S'],
            float(d['ap']),
            float(d['q']),
            float(d['rp'])
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'time': self.time,
            'status': self.status,
            'side': self.side,
            'price': self.price,
            'quantity': self.quantity,
            'profit': self.profit
        }