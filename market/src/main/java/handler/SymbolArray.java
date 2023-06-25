package handler;

import java.util.HashMap;

import exchange.MarkPrice;


public class SymbolArray {
    private HashMap<String, Symbol> symbols;

    public SymbolArray() {
        this.symbols = new HashMap<String, Symbol>();
    }

    public SymbolArray(MarkPrice[] prices) {
        this();
        for (MarkPrice mp : prices) {
            symbols.put(mp.symbol, new Symbol(mp.symbol, new Point(mp.time.doubleValue(), mp.price)));
        }
    }

    public Symbol get(String symbol) {
        return symbols.get(symbol);
    }

    public void initSymbol(String symbol, Point initialPoint) {
        symbols.put(symbol, new Symbol(symbol, initialPoint));
    }
}
