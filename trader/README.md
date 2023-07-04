# Trader module

## Notes
- Modes: EMULATOR, REAL
- ```SYMBOLS_EXCHANGE_INITIALIZATION = True``` to set margin type and leverage for each symbol
- DO NOT LET THE ```_serve``` STUCK INSIDE AN INFINITE LOOP

## Releases

### 1.2.0
##### Centralized remote config
Now you can edit values and symbols on the remote mongodb and they will be loaded here on stratup.

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
The ```handlers``` directory should contain all the modules (classes) for handling different parts of the application. The ```exceptions.py``` module must define every custom exception.
##### Code quality improvement
- moved logging to a separate module
- moved buy confirming logic to the Symbol class