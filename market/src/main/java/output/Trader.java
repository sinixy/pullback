package output;

import java.net.URI;
import java.net.http.HttpRequest;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import handler.CheckResults;
import handler.Point;


public class Trader {
    
    private static ObjectMapper mapper = new ObjectMapper();
    private static HttpClient httpClient = HttpClient.newHttpClient();

    private static void sendMessage(ObjectNode message) {
        try {
            String jsonString = message.toString();

            HttpRequest request = HttpRequest.newBuilder()
                    .uri(new URI("http://trader:8888/trade"))
                    .POST(HttpRequest.BodyPublishers.ofString(jsonString, StandardCharsets.UTF_8))
                    .header("Content-Type", "application/json")
                    .build();

            httpClient.send(request, HttpResponse.BodyHandlers.ofString());

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    public static void sendBuyMessage(String symbol, CheckResults results, Point buyPoint, Point trigger) {
        ObjectNode message = mapper.createObjectNode();

        ObjectNode trade = mapper.createObjectNode();
        ObjectNode buy = mapper.createObjectNode();
        ObjectNode triggerPoint = mapper.createObjectNode();
        ObjectNode strategy = mapper.createObjectNode();
        ObjectNode latestPump = mapper.createObjectNode();

        buy.put("time", buyPoint.time);
        buy.put("price", buyPoint.price);

        triggerPoint.put("time", trigger.time);
        triggerPoint.put("price", trigger.price);
        buy.set("triggerPoint", triggerPoint);

        strategy.put("priceChange", results.priceChange);
        strategy.put("relativeIncrease", results.relativeIncrease);
        strategy.put("segmentLength", results.segmentLength);
        latestPump.put("time", results.latestPump.get("time"));
        latestPump.put("increase", results.latestPump.get("increase"));
        strategy.set("latestPump", latestPump);

        trade.put("symbol", symbol);
        trade.set("buy", buy);
        trade.set("strategy", strategy);

        message.put("message", "BUY_REQUEST");
        message.put("time", System.currentTimeMillis() / 1000.0);
        message.set("data", trade);

        sendMessage(message);
    }

    public static void sendSellMessage(String symbol, Point sellPoint, Point trigger) {
        ObjectNode message = mapper.createObjectNode();
        ObjectNode sell = mapper.createObjectNode();
        ObjectNode triggerPoint = mapper.createObjectNode();

        triggerPoint.put("time", trigger.time);
        triggerPoint.put("price", trigger.price);

        sell.put("symbol", symbol);
        sell.put("time", sellPoint.time);
        sell.put("price", sellPoint.price);
        sell.set("triggerPoint", triggerPoint);

        message.put("message", "SELL_REQUEST");
        message.put("time", System.currentTimeMillis() / 1000.0);
        message.set("data", sell);

        sendMessage(message);
    }
}
