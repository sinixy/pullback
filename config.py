from dotenv import load_dotenv
import os
import json

load_dotenv()


MONGODB_HOST = os.environ['MONGODB_HOST']
MONGODB_NAME = os.environ['MONGODB_NAME']
REDIS_HOST = os.environ['REDIS_HOST']

TG_BOT_TOKEN = os.environ['TG_BOT_TOKEN']
TG_RECEIVER_ID = os.environ['TG_RECEIVER_ID']

BINANCE_API_KEY = os.environ['BINANCE_API_KEY']
BINANCE_SECRET_KEY = os.environ['BINANCE_SECRET_KEY']

WINDOW_SIZE = 200
SYMBOLS = []
with open('symbols.json') as file:
    SYMBOLS = json.load(file)