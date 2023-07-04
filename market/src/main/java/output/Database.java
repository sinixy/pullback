package output;

import org.bson.Document;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;

import com.mongodb.client.MongoCollection;


public class Database {
    public MongoClient client;
    public MongoDatabase db;
    public MongoCollection<Document> collection;

    public Database(String db_uri, String db_name, String collection_name) {
        this.client = MongoClients.create(db_uri);
        this.db = client.getDatabase(db_name);
        this.collection = this.db.getCollection(collection_name);
    }
}
