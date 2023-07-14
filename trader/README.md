# Trader module

## Notes
- Modes: EMULATOR, REAL
- DO NOT LET THE ```_serve``` STUCK INSIDE AN INFINITE LOOP

## Releases

### 1.2.5
##### Bug fix
- removed resetting the symbol inside ```suspend()``` as it caused ```sell_until_success()``` added in 1.2.3 not being able to access the quantity needed to sell the symbol; also it's just kinda useless to do it anyway
- removed allowing buy inside the sell_until_success method as it's supposed to happen in case of successful sell fill

### 1.2.4
##### Bug fix
When I got an UnconfirmedBuyException and checked the logs I saw this:
```bash
[INFO] [PULLBACK] 2023-07-10 17:50:53.690 :: Received BUY_REQUEST for ANKRUSDT
[INFO] [PULLBACK] 2023-07-10 17:50:53.694 :: Buying ANKRUSDT at $0.02379
[INFO] [PULLBACK] 2023-07-10 17:50:53.721 :: ANKRUSDT buy order filled
[INFO] [PULLBACK] 2023-07-10 17:50:53.723 :: ANKRUSDT buy order submitted
[INFO] [PULLBACK] 2023-07-10 17:50:59.373 :: Received SELL_REQUEST for ANKRUSDT
[INFO] [PULLBACK] 2023-07-10 17:50:59.375 :: Confirming ANKRUSDT buy
[ERROR] [PULLBACK] 2023-07-10 17:51:04.391 :: ANKRUSDT unconfirmed buy! UnconfirmedBuyException: ChangeStatusTimeoutException(status=5, duration=5)
```
So basically the order got filled before the trader confirmed its submission. It might've been caused by await logging.info before setting the status to waiting, so here's what I think happened:
1. ```await logger.info``` returned control to the event loop before setting the status to ```WAITING_FOR_BUY_ORDER_FILL```.
2. The order got filled really quickly and the status became ```SELL_ALLOWED```.
3. After this, ```await logger.info``` finished executing and status has been set to ```WAITING_FOR_BUY_ORDER_FILL```, which means that now any sell request will fail to confirm the buy order fill.
I moved every logging operation to the end of a method and also added a guard statement to not set the status to ```WAITING``` if it's already has been filled. I might as well consider rethinking the whole status system or/and make the logger sync to be sure.

### 1.2.3
##### Handling the binance' internal error
During high volatility periods binance might fail to process buy/sell requests:  ```APIError(code=-1001): Internal error; unable to process your request. Please try again.```
Trader is going to handle it like this:
- BUY fail: just block the next sell request from executing
- SELL fail: keep trying to sell the symbol until success or max (1000) retries exceeded
###### Sending warns and info messages
Added ability to safely send warnings and simple info messages to manasan.

### 1.2.2
##### Partial fills support
Now trader is saving data about ```PARTIALLY_FILLED``` events. For now I just need it to calculate full profit of the trade, but it actually might be useful during backtesting too.
###### Code quality improvement
- moved the whole fills setting logic inside the Symbol class

### 1.2.1
##### Logging extended
This version should be ready for real trading, so logging has been extended to include important events besides exceptions.
##### Bugs
- fixed OrderDataStream unsuspending a symbol
- fixed a symbol with the ```BLOCK_NEXT_SELL``` status being counted as an active symbol 
###### Code quality improvement
- introduced the with_quantity decorator, which calculates the quantity for submitting buy/sell orders.
- modified the buy and sell methods of a symbol to only accept relatable values, with request-related tasks handled by trader.
- added the ```is_suspended()``` method to the Symbol class; although similar methods could be created for all statuses, it is currently considered redundant.


### 1.2.0
##### Centralized remote config
Now you can edit values and symbols on the remote mongodb and they will be loaded here on startup.
###### Code quality improvement
- created the config class as a result of transitioning to a new config system;
- created the database package for the same reason;
- moved trade saving logic to the TradesDatabase class;
- refactored a few modules so they don't need to import any config values – everything must be initialized on startup.

### 1.1.0
##### Dedicated exception handling package
```bash
exceptions/
├─ handlers/
│  ├─ __init__.py
├─ __init__.py
├─ exceptions.py
├─ utils.py
```
The ```handlers``` directory should contain all the modules (classes) for handling different parts of the application. The ```exceptions.py``` module defines each custom exception.
##### Code quality improvement
- moved logging to a separate module
- moved buy confirming logic to the Symbol class