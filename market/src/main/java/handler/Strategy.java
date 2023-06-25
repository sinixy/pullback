package handler;

import config.Config;


public class Strategy {
    
    public static CheckResults shouldBuy(Symbol symbol) {
        CheckResults results = new CheckResults();

        Double minSegmentPrice = symbol.segment.min.price;
        Double maxSegmentPrice = symbol.segment.max.price;

        results.priceChange = 1 - minSegmentPrice / symbol.segment.start.price;
        results.latestPump = symbol.latestPump;
        results.relativeIncrease = (symbol.structEMA.latestPoint.price - minSegmentPrice) / (maxSegmentPrice - minSegmentPrice);
        results.segmentLength = symbol.segment.end.time - symbol.segment.start.time;

        if (hasFallenEnough(results.priceChange) && isShortEnough(results.segmentLength) && isEarlyEnough(results.relativeIncrease)) {
            results.shouldBuy = true;
        }

        return results;
    }

    private static Boolean hasFallenEnough(Double priceChange) {
        return Double.compare(priceChange, Config.MIN_PRICE_CHANGE) > 0;
    }

    private static Boolean isShortEnough(Double segmentLength) {
        return Double.compare(Config.MAX_SEGMENT_LENGTH, segmentLength) > 0;
    }

    private static Boolean isEarlyEnough(Double relativeIncrease) {
        return Double.compare(Config.MAX_RELATIVE_INCREASE, relativeIncrease) > 0;
    }
}
