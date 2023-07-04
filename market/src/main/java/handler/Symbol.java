package handler;

import java.util.HashMap;

import output.Socket;
import config.Config;


public class Symbol {
    private String symbol;

    private TimeWindow tw;
    public Segment segment;
    public EMA signalEMA;
    public EMA structEMA;

    private String currentlyTrading = null;

    public HashMap<String, Double> latestPump = new HashMap<String, Double>();

    public Symbol(String symbol, Point initialPoint) {
        Integer timeWindowSize = (int) Config.INDICATORS.get("timeWindowSize");
        Integer signalEMALag = (int) Config.INDICATORS.get("signalEMALag");
        Integer structEMALag = (int) Config.INDICATORS.get("structEMALag");
        this.symbol = symbol;
        this.tw = new TimeWindow(initialPoint, timeWindowSize);
        this.signalEMA = new EMA(signalEMALag, initialPoint, timeWindowSize);
        this.structEMA = new EMA(structEMALag, initialPoint, timeWindowSize);
        this.segment = new Segment(initialPoint, signalEMA, structEMA);
    }

    public Double handleNewPoint(Point point) {
        Double difference = tw.add(point);
        if (difference > 0) {
            signalEMA.move(tw.getMax().price, difference);
            structEMA.move(tw.getMean().price, difference);

            Double structPrice = structEMA.latestPoint.price;
            Double signalPrice = signalEMA.latestPoint.price;

            if ( (Double.compare(structPrice, signalPrice) > 0) && (segment.direction == "BEARISH") ) {
                // potential buy
                segment.end = structEMA.latestPoint;
                CheckResults results = Strategy.shouldBuy(this);
                if (results.shouldBuy) {
                    currentlyTrading = sendBuyRequest(results, point);
                }
                segment = new Segment(point, signalEMA, structEMA);
            } else if ( (Double.compare(signalPrice, structPrice) > 0) && (segment.direction == "BULLISH") ) {
                // potential sell or pump
                if (currentlyTrading != null) {
                    sendSellRequest(point);
                    currentlyTrading = null;
                }
                Double increase = segment.getIncrease();
                if (Double.compare(increase, 0.015) > 0) {
                    latestPump.put("time", structEMA.latestPoint.time);
                    latestPump.put("increase", increase);
                }
                segment = new Segment(point, signalEMA, structEMA);
            } else {
                segment.update(tw.getMin(), tw.getMax());
            }

            tw = new TimeWindow(point, tw.getSize());
        }
        return difference;
    }

    String sendBuyRequest(CheckResults results, Point trigger) {
        return Socket.sendBuyMessage(symbol, results, structEMA.latestPoint, trigger);
    }

    private void sendSellRequest(Point trigger) {
        Socket.sendSellMessage(currentlyTrading, structEMA.latestPoint, trigger);
    }

}
