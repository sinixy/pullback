package output;

import org.bson.BsonValue;
import org.bson.Document;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.result.InsertOneResult;

import handler.CheckResults;
import handler.Point;

import com.mongodb.client.MongoCollection;


public class Database {
    public static MongoClient client;
    public static MongoDatabase db;
    public static MongoCollection<Document> collection;

    public static void init() {
        client = MongoClients.create("mongodb://localhost:27017");
        db = client.getDatabase("pullback");
        collection = db.getCollection("testTrades");
    }

    public static BsonValue insertTrade(String symbol, CheckResults results, Point buyPoint) {
        Document trade = new Document();
        Document buyDoc = new Document();
        Document strategyDoc = new Document();

        buyDoc.put("time", buyPoint.time);
        buyDoc.put("price", buyPoint.price);
        strategyDoc.put("priceChange", results.priceChange);
        strategyDoc.put("relativeIncrease", results.relativeIncrease);
        strategyDoc.put("segmentLength", results.segmentLength);
        strategyDoc.put("latestPump", new Document(results.latestPump));

        trade.put("symbol", symbol);
        trade.put("buy", buyDoc);
        trade.put("strategy", strategyDoc);

        InsertOneResult insertResult = collection.insertOne(trade);
        return insertResult.getInsertedId();
    }

    public static void sellTrade(String id, Point sellPoint) {
        Document query = new Document("_id", Document.parse(id));
        Document sellDoc = new Document();
        sellDoc.put("time", sellPoint.time);
        sellDoc.put("price", sellPoint.price);
        collection.updateOne(
            query,
            new Document("$set", new Document("sell", sellDoc))
        );
    }
}
