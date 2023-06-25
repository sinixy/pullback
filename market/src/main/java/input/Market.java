package input;

import exchange.Exchange;
import handler.MarketHandler;


public class Market {

    private String[] symbols;
    private Exchange exchange;
    private MarketHandler handler;

    public Market(String[] symbols, Exchange exchange) {
        this.symbols = symbols;
        this.handler = new MarketHandler(symbols, exchange);
        this.exchange = exchange;
    }

    public void monitor() {
        exchange.wsClient.combineStreams(Exchange.getAggTradeStreams(symbols), ((e) -> {
            AggTrade a = Event.fromJSON(e).getData();
            handler.handle(a);
            // System.out.println(a.symbol);
        }));
    }
}