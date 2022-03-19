import pandas as pd
import datetime

df = pd.read_csv('backtesting/ETHUSDT-1m-result.csv')
current_minute = datetime.datetime.now().minute
df_minute = pd.to_datetime(df.tail(1)['timestamp'])

print(current_minute, df_minute, current_minute)
