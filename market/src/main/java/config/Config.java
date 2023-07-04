package config;

import output.Database;
import org.bson.Document;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;


public class Config {
    private static ObjectMapper mapper = new ObjectMapper();

    public static String DB_URI;
    public static String DB_NAME;

    public static String[] SYMBOLS;
    public static HashMap<String, Object> INDICATORS = new HashMap<String, Object>();

    public static Double MIN_PRICE_CHANGE;
    public static Double MAX_RELATIVE_INCREASE;
    public static Double MAX_SEGMENT_LENGTH;

    public static void load() {
        HashMap<?, ?> config = null;

        try {
            config = mapper.readValue(new File(System.getProperty("user.dir"), "config.json"), HashMap.class);
        } catch (IOException e) {
            e.printStackTrace();
        }

        DB_URI = (String) config.get("DB_URI");
        DB_NAME = (String) config.get("DB_NAME");

        Database db = new Database(DB_URI, DB_NAME, "config");
        Document commonConfigDocument = db.collection.find(new Document("_id", "common")).first();
        Document marketConfigDocument = db.collection.find(new Document("_id", "market")).first();

        SYMBOLS = commonConfigDocument.getList("symbols", String.class).toArray(new String[0]);

        MIN_PRICE_CHANGE = marketConfigDocument.getDouble("minPriceChange");
        MAX_RELATIVE_INCREASE = marketConfigDocument.getDouble("maxRelativeIncrease");
        MAX_SEGMENT_LENGTH = marketConfigDocument.getDouble("maxSegmentLength");
        INDICATORS.put("timeWindowSize", marketConfigDocument.getInteger("timeWindowSize"));
        INDICATORS.put("signalEMALag", marketConfigDocument.getInteger("signalEMALag"));
        INDICATORS.put("structEMALag", marketConfigDocument.getInteger("structEMALag"));
    }
}