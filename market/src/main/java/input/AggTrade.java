package input;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator; 
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;


@JsonIgnoreProperties(ignoreUnknown = true)
public class AggTrade {
    private static ObjectMapper mapper = new ObjectMapper();

    public final String symbol;
    public final Long time;
    public final Double price;

    @JsonCreator(mode = JsonCreator.Mode.PROPERTIES)
    public AggTrade(
        @JsonProperty("s") String symbol,
        @JsonProperty("T") Long time,
        @JsonProperty("p") String price
    ) {
            this.symbol = symbol;
            this.time = time;
            this.price = Double.parseDouble(price);
    }

    public AggTrade(String[] entry) {
        this.symbol = entry[0];
        this.time = Long.parseLong(entry[1]);
        this.price = Double.parseDouble(entry[2]);
    }

    public static AggTrade fromJSON(String message) {
        AggTrade atrade = null;
        try {
            atrade = mapper.readValue(message, AggTrade.class);
        } catch(JsonProcessingException ex) {
            ex.printStackTrace();
        }
        return atrade;
    }

    public static AggTrade fromLine(String line) {
        return new AggTrade(line.trim().split(","));
    }
}