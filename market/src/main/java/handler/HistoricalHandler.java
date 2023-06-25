package handler;

import input.AggTrade;

public class HistoricalHandler implements Handler {
    private SymbolArray symbols;

    public HistoricalHandler() {
        this.symbols = new SymbolArray();
    }

    public void handle(AggTrade atrade) {
        Symbol symbol = symbols.get(atrade.symbol);
        Point point = new Point(atrade.time.doubleValue(), atrade.price);
        if (symbol == null) {
            symbols.initSymbol(atrade.symbol, point);
            return;
        }

        symbol.handleNewPoint(point);
    }
}
