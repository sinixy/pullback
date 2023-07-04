import exchange.Exchange;
import input.Market;

import java.io.IOException;

import output.Socket;
import config.Config;

public class App {
    public static void main(String[] args) {
        Config.load();

        try {
            Socket.init();
        } catch(IOException ex) {
            ex.printStackTrace();
        }
        Exchange exchange = new Exchange();
        Market market = new Market(Config.SYMBOLS, exchange);
        market.monitor();
    }
}
