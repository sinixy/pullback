package handler;

public class TimeWindow {
    private Integer size;
    private Integer count;

    private Double floor;
    private Double minPrice;
    private Double maxPrice;
    private Double priceSum;

    public TimeWindow(Point initialPoint, Integer size) {
        this.size = size;
        this.count = 1;

        this.floor = Math.floor(initialPoint.time / size);
        this.minPrice = initialPoint.price;
        this.maxPrice = initialPoint.price;
        this.priceSum = initialPoint.price;
    }

    public Double add(Point p) {
        Double currentPointFloor = Math.floor(p.time / size);
        // System.out.println("2. " + "tw_floor=" + floor.toString() + " point_floor=" + currentPointFloor.toString());

        if ( currentPointFloor.equals(floor) ) {
            count += 1;
            priceSum += p.price;
            if (Double.compare(p.price, maxPrice) > 0) {
                maxPrice = p.price;
            }
            if (Double.compare(p.price, minPrice) < 0) {
                minPrice = p.price;
            }
        }

        return currentPointFloor - floor;
    }

    public Integer getSize() {
        return size;
    }

    public Long getStartingMS() {
        return Math.round(floor * size);
    }

    public Point getMax() {
        return new Point(getStartingMS().doubleValue(), maxPrice);
    }

    public Point getMin() {
        return new Point(getStartingMS().doubleValue(), minPrice);
    }

    public Point getMean() {
        return new Point(getStartingMS().doubleValue(), priceSum / count);
    }
}
