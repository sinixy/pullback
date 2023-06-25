package handler;

import exchange.Exchange;
import input.AggTrade;


public class MarketHandler implements Handler {
    private SymbolArray symbols;
    private Exchange exchange;

    public MarketHandler(String[] symbols, Exchange exchange) {
        this.exchange = exchange;
        this.symbols = new SymbolArray(this.exchange.markPrice());
    }

    public void handle(AggTrade atrade) {
        Symbol symbol = symbols.get(atrade.symbol);
        Point point = new Point(atrade.time.doubleValue(), atrade.price);
        symbol.handleNewPoint(point);
    }
}
