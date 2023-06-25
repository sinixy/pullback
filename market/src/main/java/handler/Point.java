package handler;

public class Point {
    public Double time;
    public Double price;

    public Point(Double time, Double price) {
        this.time = time;
        this.price = price;
    }

    public String toString() {
        return "Point<time=" + time.toString() + ", price=" + price.toString() + ">";
    }
}
