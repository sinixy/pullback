# Trader module

## Notes
- Modes: EMULATOR, REAL
- ```SYMBOLS_EXCHANGE_INITIALIZATION = True``` to set margin type and leverage for each symbol
- DO NOT LET THE ```_serve``` STUCK INSIDE AN INFINITE LOOP

## Releases

### 1.2.1
##### Logging extended
This version should be ready for real trading, so logging has been extended to include important events besides exceptions.
##### Bugs
- fixed OrderDataStream unsuspending a symbol
- fixed a symbol with the ```BLOCK_NEXT_SELL``` status being counted as an active symbol 
###### Code quality improvement
- introduced the with_quantity decorator, which calculates the quantity for submitting buy/sell orders.
- modified the buy and sell methods of a symbol to only accept relatable values, with request-related tasks handled by the trader.
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