FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /build
COPY src ./src
COPY pom.xml .
RUN mvn clean package

FROM eclipse-temurin:17-jre
WORKDIR /market
COPY --from=build /build/target/market-1.2.0.jar /market/market.jar
COPY --from=build /build/target/lib /market/lib

CMD ["java", "-jar", "market.jar"]