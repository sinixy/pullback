package handler;

import java.util.HashMap;

import output.Database;
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
        // System.out.println("3. difference=" + difference.toString());
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

    private String sendBuyRequest(CheckResults results, Point trigger) {
        // gotta save the aggTradeId too
        String resp = null;
        switch (Config.MODE) {
            case "LIVE":
                resp = Socket.sendBuyMessage(symbol, results, structEMA.latestPoint, trigger);
                break;
            case "BACKTEST":
                resp = Database.insertTrade(symbol, results, structEMA.latestPoint).toString();
                break;
        }
        return resp;
    }

    private void sendSellRequest(Point trigger) {
        switch (Config.MODE) {
            case "LIVE":
                Socket.sendSellMessage(currentlyTrading, structEMA.latestPoint, trigger);
                break;
            case "BACKTEST":
                Database.sellTrade(currentlyTrading, structEMA.latestPoint);
                break;
        }
    }

}
