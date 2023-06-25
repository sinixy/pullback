package input;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.FileNotFoundException;

import handler.HistoricalHandler;
import me.tongfei.progressbar.ProgressBar;

public class Historical {
    
    private HistoricalHandler handler;
    private BufferedReader reader;

    private Long dataBytesSize;

    public Historical(String[] symbols, String historicalDataPath) {
        this.handler = new HistoricalHandler();

        File file = new File(historicalDataPath);
        this.dataBytesSize = file.length();

        FileReader fileReader = null;
        try {
            fileReader = new FileReader(file);
        } catch(FileNotFoundException ex) {
            ex.printStackTrace();
        }

        this.reader = new BufferedReader(fileReader);
    }

    public void backtest() throws IOException {
        try (ProgressBar pbar = new ProgressBar("Processing", dataBytesSize)) {
            String line = reader.readLine();
            pbar.stepBy(line.getBytes("UTF-8").length);

            line = reader.readLine();
            while (line != null) {
                AggTrade a = AggTrade.fromLine(line);
                handler.handle(a);
                pbar.stepBy(line.getBytes("UTF-8").length);
                line = reader.readLine();
            }
        }
    }

}
