import pandas_ta as ta
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()
bot = os.environ["telegram_token_bot"]

df = pd.read_csv('datasets/ETHUSDT-1m-sma-15.csv')

print(df)

df["EMA12"] = ta.ema(high=df.high, low=df.low, close=df.close, length=12)
df["RSI2"] = ta.rsi(high=df.high, low=df.low, close=df.close, length=14)
df['ATR2'] = df.ta.atr()
df['Momentum'] = df.ta.mom()
df['adx'] = ta.adx(high=df.high, low=df.low, close=df.close, length=14)['ADX_14']
vp = ta.vp(close=df.close, volume=df.volume, width=24, sort_close=True)
print(vp)
vp['mean_close'] = round(vp['mean_close'], 2)
vp.to_csv('vp.csv')
df.to_csv('test.csv')


def send_messsage_by_rest(token, chat_id, text):
    message = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (token, chat_id, text)
    res = requests.get(message)
    print(res.text)
    print(res.status_code)

send_messsage_by_rest(bot, -64481497, "Hola")
send_messsage_by_rest(bot, -644814972, "Hola")
