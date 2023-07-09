from common import banana
from models import Wallet
from models.enums import UserDataEvent, OrderStatus


class OrderDataStream:

    def __init__(self, wallet: Wallet):
        self.wallet = wallet

    async def start(self):
        async with banana.bm.futures_user_socket() as stream:
            while True:
                msg = await stream.recv()
                if msg['e'] != UserDataEvent.ORDER_TRADE_UPDATE:
                    continue

                symbol = self.wallet[msg['o']['s']]
                if symbol.is_suspended():
                    continue

                status = msg['o']['X']
                if status == OrderStatus.FILLED:
                    await symbol.set_filled(msg['o'])
                elif status == OrderStatus.PARTIALLY_FILLED:
                    symbol.add_fill(msg['o'])
                else:
                    continue
                    
