package exchange;

import java.util.ArrayList;

import com.binance.connector.futures.client.impl.UMFuturesClientImpl;
import com.binance.connector.futures.client.impl.um_futures.UMMarket;
import com.binance.connector.futures.client.impl.UMWebsocketClientImpl;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;


public class Exchange {
    private UMFuturesClientImpl client = new UMFuturesClientImpl();
    private UMMarket market = client.market();
    public UMWebsocketClientImpl wsClient = new UMWebsocketClientImpl();

    private static ObjectMapper mapper = new ObjectMapper();

    public MarkPrice[] markPrice() {
        MarkPrice[] prices = null;
        try {
            prices = mapper.readValue(market.markPrice(null), MarkPrice[].class);
        } catch(JsonProcessingException ex) {
            ex.printStackTrace();
        }
        return prices;
    }

    public static ArrayList<String> getAggTradeStreams(String[] symbols) {
        ArrayList<String> streams = new ArrayList<>();
        for (String s : symbols) {
            streams.add(s.toLowerCase() + "@aggTrade");
        }
        return streams;
    }
}
