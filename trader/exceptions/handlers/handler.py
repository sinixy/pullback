import traceback
from common import logger


class Handler:

    async def handle(self, e: Exception):
        traceback.print_exc()
        await self._report(str(e))

    async def _report(self, msg: str):
        await logger.error(msg, exc_info=True)

    async def _warn(self, msg):
        await logger.warn(msg)