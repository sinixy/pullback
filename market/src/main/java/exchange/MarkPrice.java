package exchange;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonCreator; 
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;


@JsonIgnoreProperties(ignoreUnknown = true)
public class MarkPrice {
    private static ObjectMapper mapper = new ObjectMapper();

    public final String symbol;
    public final Long time;
    public final Double price;

    @JsonCreator(mode = JsonCreator.Mode.PROPERTIES)
    public MarkPrice(
        @JsonProperty("symbol") String symbol,
        @JsonProperty("time") Long time,
        @JsonProperty("markPrice") String price
    ) {
            this.symbol = symbol;
            this.time = time;
            this.price = Double.parseDouble(price);
    }

    public static MarkPrice load(String message) {
        MarkPrice mp = null;
        try {
            mp = mapper.readValue(message, MarkPrice.class);
        } catch(JsonProcessingException ex) {
            ex.printStackTrace();
        }
        return mp;
    }
}