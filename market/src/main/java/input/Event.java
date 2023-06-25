package input;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;


@JsonIgnoreProperties(ignoreUnknown = true)
public class Event {

    private static ObjectMapper mapper = new ObjectMapper();

    @JsonProperty("stream")
    private String stream;

    @JsonProperty("data")
    private AggTrade data;

    public Event() {
        // empty constructor needed for Jackson
    }

    public Event(String stream, AggTrade data) {
        this.stream = stream;
        this.data = data;
    }

    public String getStream() {
        return stream;
    }

    public AggTrade getData() {
        return data;
    }

    public static Event fromJSON(String message) {
        Event atradeWrapper = null;
        try {
            atradeWrapper = mapper.readValue(message, Event.class);
        } catch(JsonProcessingException ex) {
            ex.printStackTrace();
        }
        return atradeWrapper;
    }
}
