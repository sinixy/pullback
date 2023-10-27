import exchange.Exchange;
import input.Market;
import config.Config;


public class App {
    public static void main(String[] args) {
        Config.load();

        Exchange exchange = new Exchange();
        Market market = new Market(Config.SYMBOLS, exchange);
        market.monitor();
    }
}
