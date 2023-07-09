from db.db import Database
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection


class TradesDatabase(Database):

    COLLECTION_NAME = 'trades'

    def init(self, db_uri, db_name):
        self.db_uri = db_uri
        self.db_name = db_name

        self.client: AsyncIOMotorClient = AsyncIOMotorClient(self.db_uri)
        self.db: AsyncIOMotorDatabase = self.client.get_database(self.db_name)
        self.collection: AsyncIOMotorCollection = self.db.get_collection(TradesDatabase.COLLECTION_NAME)

    async def insert_trade(self, symbol: str, requests, orders, fills):
        await self.collection.insert_one({
            'symbol': symbol,
            'time': requests['buy'].trigger.time,
            'requests': {
                'buy': requests['buy'].to_dict(),
                'sell': requests['sell'].to_dict()
            },
            'orders': {
                'buy': orders['buy'].to_dict(),
                'sell': orders['sell'].to_dict()
            },
            'fills': {
                'buy': [buy.to_dict() for buy in fills['buy']],
                'sell': [sell.to_dict() for sell in fills['sell']]
            }
        })