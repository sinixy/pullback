from exceptions.handlers.handler import Handler
import trader.trader as trader


class TraderHandler(Handler):

    def __init__(self, trader: trader.Trader):
        super().__init__()
        self.trader = trader

    async def handle(self, e: Exception):
        self.trader.wallet.suspend_trading()
        await super().handle(e)
