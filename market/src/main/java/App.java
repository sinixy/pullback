import exchange.Exchange;
import input.Market;
import input.Historical;

import java.io.IOException;

import output.Database;
import output.Socket;
import config.Config;

public class App {
    public static void main(String[] args) {
        Config.load();

        switch(Config.MODE) {
            case "LIVE":
                try {
                    Socket.init();
                } catch(IOException ex) {
                    ex.printStackTrace();
                }
                Exchange exchange = new Exchange();
                Market market = new Market(Config.SYMBOLS, exchange);
                market.monitor();
                break;

            case "BACKTEST":
                Database.init();
                Historical historical = new Historical(Config.SYMBOLS, Config.HISTORICAL_DATA_PATH);
                try {
                    historical.backtest();
                } catch(IOException ex) {
                    ex.printStackTrace();
                }
                break;
        }
        
    }
}
