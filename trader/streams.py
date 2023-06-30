from common import banana
from models import Wallet, BuyOrder, SellOrder
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
                
                status = msg['o']['X']
                if status != OrderStatus.FILLED:
                    continue

                symbol = msg['o']['s']
                side = msg['o']['S']
                if side == 'BUY':
                    await self.wallet[symbol].set_filled_buy(BuyOrder.from_dict(msg['o']))
                else:
                    await self.wallet[symbol].set_filled_sell(SellOrder.from_dict(msg['o']))
                    
