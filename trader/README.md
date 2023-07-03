# Trader module

## Notes
- Modes: EMULATOR, REAL
- ```SYMBOLS_EXCHANGE_INITIALIZATION = True``` to set margin type and leverage for each symbol
- DO NOT LET THE ```_serve``` STUCK INSIDE AN INFINITE LOOP

## TO-DO
- Proper (unified?) configuration

## Releases

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