package output;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;


public class Output {
    private File file;
    private FileWriter writer;

    public Output() {
        File dir = new File("D:/trade/code/pullback/market/src/main/java/output/data");
        dir.mkdirs();

        file = new File(dir, "preprocessedAggTrades.csv");
        if (file.exists()) {
            file.delete();
        }

        try {
            file.createNewFile();
            writer = new FileWriter(file, true);
        } catch (IOException e) {
            e.printStackTrace();
        }

        write("symbol,time,signal,struct,min_window_price,max_window_price");
    }

    public void write(String entry) {
        // System.out.println("4. " + entry);
        try {
            writer.write(entry + "\n");
            // writer.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
