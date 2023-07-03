from exceptions.handlers.handler import Handler
from trader.trader import Trader


class TraderHandler(Handler):

    def __init__(self, trader: Trader):
        super().__init__()
        self.trader = trader

    async def handle(self, e: Exception):
        self.trader.wallet.suspend_trading()
        await super().handle(e)
