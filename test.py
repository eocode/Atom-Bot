from binance.client import Client
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
binance_client = Client(api_key=os.environ['binance_api_key'], api_secret=os.environ['binance_api_secret'])
klines = binance_client.get_historical_klines(symbol='ADAUSDT', interval='1m',
                                              start_str="04 Feb 2022 00:23:47",
                                              end_str="07 Feb 2022 06:23:00")
data = pd.DataFrame(klines,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                             'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
print(data)
