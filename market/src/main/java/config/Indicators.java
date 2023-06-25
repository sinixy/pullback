package config;

public class Indicators {
    public static Integer signalEMALag;
    public static Integer structEMALag;
    public static Integer timeWindowSize;

    public Indicators(Integer signalEMALag, Integer structEMALag, Integer timeWindowSize) {
        Indicators.signalEMALag = signalEMALag;
        Indicators.structEMALag = structEMALag;
        Indicators.timeWindowSize = timeWindowSize;
    }
}
