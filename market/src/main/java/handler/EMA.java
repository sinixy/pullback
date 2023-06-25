package handler;


public class EMA {
    private Integer lag;

    private Double k;
    private Integer stepSize;
    public Point latestPoint;

    public EMA(Integer lag, Point initialPoint, Integer timeWindowSize) {
        this.lag = lag;
        this.k = 2.0 / (lag + 1);
        this.stepSize = timeWindowSize;
        this.latestPoint = initialPoint;
    }

    public void move(Double newPrice, Double steps) {
        for (int i = 0; i < steps; i++) {
            latestPoint = new Point(latestPoint.time + stepSize, newPrice * k + latestPoint.price * (1 - k));
        }
    }

    public Integer getLag() {
        return lag;
    }
}
