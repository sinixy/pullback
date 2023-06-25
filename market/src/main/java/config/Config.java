package config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator; 

import java.io.File;
import java.io.IOException;
import java.util.HashMap;


public class Config {
    private static ObjectMapper mapper = new ObjectMapper();

    public static String MODE;
    public static String HISTORICAL_DATA_PATH;
    public static String[] SYMBOLS;
    public static HashMap<String, Object> INDICATORS = new HashMap<String, Object>();

    public static Double MIN_PRICE_CHANGE;
    public static Double MAX_RELATIVE_INCREASE;
    public static Double MAX_SEGMENT_LENGTH;

    @JsonCreator(mode = JsonCreator.Mode.PROPERTIES)
    public Config(
        @JsonProperty("mode") String mode,
        @JsonProperty("historicalDataPath") String historicalDataPath,
        @JsonProperty("timeWindowSize") Integer timeWindowSize,
        @JsonProperty("signalEMALag") Integer signalEMALag,
        @JsonProperty("structEMALag") Integer structEMALag,
        @JsonProperty("minPriceChange") Double minPriceChange,
        @JsonProperty("maxRelativeIncrease") Double maxRelativeIncrease,
        @JsonProperty("maxSegmentLength") Double maxSegmentLength,
        @JsonProperty("symbols") String[] symbols
    ) {
        MODE = mode;
        HISTORICAL_DATA_PATH = historicalDataPath;
        SYMBOLS = symbols;
        MIN_PRICE_CHANGE = minPriceChange;
        MAX_RELATIVE_INCREASE = maxRelativeIncrease;
        MAX_SEGMENT_LENGTH = maxSegmentLength;
        INDICATORS.put("timeWindowSize", timeWindowSize);
        INDICATORS.put("signalEMALag", signalEMALag);
        INDICATORS.put("structEMALag", structEMALag);
    }

    public static Config load() {
        Config config = null;

        try {
            config = mapper.readValue(new File(System.getProperty("user.dir"), "config.json"), Config.class);
        } catch (IOException e) {
            e.printStackTrace();
        }

        return config;
    }
}