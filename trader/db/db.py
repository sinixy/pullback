class Database:

    COLLECTION_NAME = ''

    def __init__(self):
        self.db_uri: str = None
        self.db_name: str = None
        
        self.client = None
        self.db = None
        self.collection = None

    def init(self, db_uri, db_name):
        pass