from models.point import Point


class Request:

    def __init__(
            self,
            request_time: int,
            symbol: str,
            ema_time: int,
            ema_price: float,
            trigger_time: int,
            trigger_price: float
        ):
        '''
        request_time: int - час, коли з market був відправлений реквест
        symbol: str - символ, який потрібно купити/продати
        ema_time: int - час (x) точки структурної EMA, на якій відправився реквест
        ema_price: float - значення (y; ціна) точки структурної EMA, на якій відправився реквест
        trigger_time: int - час точки агрегованого трейду, який спричинив відправлення реквесту, завершивши обчислення EMA для вікна
        trigger_price: float - ціна точки агрегованого трейду, який спричинив відправлення реквесту, завершивши обчислення EMA для вікна
        '''
        self.request_time = request_time
        self.symbol = symbol
        self.ema = Point(ema_time, ema_price)
        self.trigger = Point(trigger_time, trigger_price)

    @classmethod
    def from_dict(cls, d):
        pass

    def to_dict(self):
        pass


class BuyRequest(Request):
    '''
    {
        "message": "BUY_REQUEST",
        "time": 160143824859248,
        "data": {
            "symbol": "...",
            "buy": {
                "time": 1687656784567,
                "price": 0.0,
                "triggerPoint": {
                    "time": 160987654678,
                    "price": 0.0
                }
            },
            "strategy": {
                "priceChange": 0.0,
                "relativeIncrease": 0.0,
                "segmentLength": 0,
                "latestPump": {
                    "time": 160987654567,
                    "increase": 0.0
                }
            }
        }
    }
    '''
    def __init__(
            self,
            request_time: int,
            symbol: str,
            ema_time: int,
            ema_price: float,
            trigger_time: int,
            trigger_price: float,
            strategy_info: dict
        ):
        super().__init__(request_time, symbol, ema_time, ema_price, trigger_time, trigger_price)
        self.strategy_info = strategy_info

    @classmethod
    def from_dict(cls, d):
        data = d['data']
        return cls(
            d['time'],
            data['symbol'],
            data['buy']['time'],
            data['buy']['price'],
            data['buy']['triggerPoint']['time'],
            data['buy']['triggerPoint']['price'],
            data['strategy']
        )
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'time': self.request_time,
            'emaPoint': {
                'time': self.ema.time,
                'price': self.ema.price
            },
            'triggerPoint': {
                'time': self.trigger.time,
                'price': self.trigger.price
            },
            'strategy': self.strategy_info
        }
    
    def __str__(self):
        return f'BuyRequest(symbol={self.symbol}, time={self.request_time})'


class SellRequest(Request):
    '''
    {
        "message": "SELL_REQUEST",
        "time": 160143824859248,
        "data": {
            "symbol": "...",
            "time": 1687656784567,
            "price": 0.0,
            "triggerPoint": {
                "time": 160987654678,
                "price": 0.0
            }
        }
    }
    '''
    def __init__(
            self,
            request_time: int,
            symbol: str,
            ema_time: int,
            ema_price: float,
            trigger_time: int,
            trigger_price: float
        ):
        super().__init__(request_time, symbol, ema_time, ema_price, trigger_time, trigger_price)

    @classmethod
    def from_dict(cls, d):
        data = d['data']
        return cls(
            d['time'],
            data['symbol'],
            data['time'],
            data['price'],
            data['triggerPoint']['time'],
            data['triggerPoint']['price']
        )
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'time': self.request_time,
            'emaPoint': {
                'time': self.ema.time,
                'price': self.ema.price
            },
            'triggerPoint': {
                'time': self.trigger.time,
                'price': self.trigger.price
            }
        }
    
    def __str__(self):
        return f'SellRequest(symbol={self.symbol}, time={self.request_time})'