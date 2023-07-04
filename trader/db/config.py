from db.db import Database
from pymongo import MongoClient, database, collection


class ConfigDatabase(Database):

    COLLECTION_NAME = 'config'

    def init(self, db_uri, db_name):
        self.db_uri = db_uri
        self.db_name = db_name

        self.client: MongoClient = MongoClient(self.db_uri)
        self.db: database.Database = self.client.get_database(self.db_name)
        self.collection: collection.Collection = self.db.get_collection(ConfigDatabase.COLLECTION_NAME)

    def get_common(self):
        return self.collection.find_one({'_id': 'common'})
    
    def get_trader(self):
        return self.collection.find_one({'_id': 'trader'})