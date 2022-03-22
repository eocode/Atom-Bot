from dotenv import load_dotenv
from binance.client import Client
import os

load_dotenv()


class BinanceConnector:
    client = None
    sizes = None

    def __init__(self):
        self.client = Client(api_key=os.environ['binance_api_key'], api_secret=os.environ['binance_api_secret'])
        self.sizes = {"1m": 1, "3m": 3, "5m": 5, "1h": 60, "4h": 240, "1d": 1440}
