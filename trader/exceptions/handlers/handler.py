import traceback
from common import logger
from servers import ws


class Handler:

    async def handle(self, e: Exception):
        traceback.print_exc()
        await self._report(str(e))

    async def _report(self, msg: str):
        await ws.send_error(msg)
        await logger.error(msg, exc_info=True)

    async def _warn(self, msg):
        await ws.send_warning(msg)
        await logger.warn(msg)