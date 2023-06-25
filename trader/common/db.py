import motor.motor_asyncio

from config import MONGODB_HOST, MONGODB_NAME


mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_HOST)
mongo_db = mongo_client[MONGODB_NAME]
