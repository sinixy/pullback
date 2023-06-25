package output;

import java.io.IOException;
import java.net.StandardProtocolFamily;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.net.UnixDomainSocketAddress;
import java.nio.file.Path;
import java.util.concurrent.TimeUnit;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import handler.CheckResults;
import handler.Point;

// apt install openjdk-17-jdk openjdk-17-jre

public class Socket {

    private static UnixDomainSocketAddress address;
    private static SocketChannel channel;
    private static ByteBuffer buffer;
    
    private static ObjectMapper mapper;

    public static void init() throws IOException {
        address = UnixDomainSocketAddress.of(Path.of("/tmp/socket"));
        channel = SocketChannel.open(StandardProtocolFamily.UNIX);
        buffer = ByteBuffer.allocate(1024);
        mapper = new ObjectMapper();
        channel.connect(address);
    }

    private static void sendMessage(ObjectNode message) {
        String json = null;
        try {
            json = mapper.writeValueAsString(message) + "\n";
        } catch (JsonProcessingException ex) {
            ex.printStackTrace();
        }
        buffer.clear();
        buffer.put(json.getBytes());
        buffer.flip();
        while (buffer.hasRemaining()) {
            try {
                channel.write(buffer);
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
    }
    
    public static String sendBuyMessage(String symbol, CheckResults results, Point buyPoint, Point trigger) {
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

        return symbol;
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
