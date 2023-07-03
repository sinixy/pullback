from exceptions.handlers.handler import Handler
from exceptions.exceptions import ExchangeInitializationException, WalletInitializationException

import traceback


class ControllerHanlder(Handler):

    async def handle(self, e):
        if isinstance(e, ExchangeInitializationException):
            self.handle_exchange_init(e)
        elif isinstance(e, WalletInitializationException):
            self.handle_wallet_init(e)
        else:
            await super().handle(f'OOPSEE {e}')

    def handle_exchange_init(self, e):
        traceback.print_exc()

    def handle_wallet_init(self, e):
        traceback.print_exc()