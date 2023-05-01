import motor.motor_asyncio
import aioredis
from traceback import print_exc

from config import MONGODB_HOST, MONGODB_NAME, REDIS_HOST


mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_HOST)
mongo_db = mongo_client[MONGODB_NAME]

# redis_db = aioredis.from_url(REDIS_HOST)
