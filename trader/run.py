import asyncio
import traceback

from bot.bot import send_message
from config import UNIX_SOCKET_ADDRESS
from common import applogger



def run(loop):
    from trader import EmulatorTrader
    trader = EmulatorTrader()

    from server import Server
    unix_socket_server = Server(UNIX_SOCKET_ADDRESS, trader, loop=loop)

    loop.create_task(unix_socket_server.run())
    loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    try:
        run(loop)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        traceback.print_exc()
        applogger.critical(f'WE\'RE FUCKED {e}', exc_info=True)
        loop.run_until_complete(send_message(f'WE\'RE FUCKED\n\n{e}'))
    finally:
        print('See ya!')