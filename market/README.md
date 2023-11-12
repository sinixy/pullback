# Market module

## Releases

### 1.3.0
##### HTTP communication with the trader
Now the market sending HTTP requests to the trader instead of connecting via unix-sockets.

### 1.2.0
##### Centralized remote config
Now you can edit values and symbols on the remote mongodb and they will be loaded here on stratup.

##### Removed backtesting mechanism
I decided to create a dedicated application for backtesting.