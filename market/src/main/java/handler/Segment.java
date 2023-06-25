package handler;

public class Segment {
    public Point start;
    public Point end;
    public Point min;
    public Point max;

    public String direction;

    public Segment(Point initialPoint, EMA signal, EMA struct) {
        this.start = struct.latestPoint;
        this.min = initialPoint;
        this.max = initialPoint;

        this.direction = (struct.latestPoint.price > signal.latestPoint.price) ? "BULLISH" : "BEARISH";
    }

    public Double getIncrease() {
        return max.price / min.price - 1;
    }

    public void update(Point newMin, Point newMax) {
        if (Double.compare(min.price, newMin.price) > 0) {
            min = newMin;
        }
        if (Double.compare(newMax.price, max.price) > 0) {
            max = newMax;
        }
    }

}
