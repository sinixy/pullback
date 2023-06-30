from typing import Dict

from config import MAX_ACTIVE_TRADES
from models.symbol import Symbol
from models.enums import SymbolStatus
from common import banana


class Wallet:

    def __init__(self, symbols: list):
        self.symbols: Dict[str, Symbol] = {s: Symbol(s) for s in symbols}

    async def init(self):
        info = await banana.exchange_info()
        for symbol in self.symbols.values():
            found = False
            for s in info['symbols']:
                if s['symbol'] == symbol.name:
                    symbol.precision = s['quantityPrecision']
                    found = True
                    break
            if not found:
                raise Exception(f'{symbol.name} not found on the exchange!')

    def is_full(self) -> bool:
        currently_active = 0
        for symbol in self.symbols.values():
            if symbol.status in [SymbolStatus.TRADING_SUSPENDED, SymbolStatus.BUY_ALLOWED]:
                continue
            currently_active += 1
        return currently_active > MAX_ACTIVE_TRADES
    
    def suspend_trading(self):
        for symbol in self.symbols.values():
            symbol.suspend()
    
    def __getitem__(self, key) -> Symbol:
        return self.symbols[key]