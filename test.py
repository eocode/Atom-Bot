import pandas_ta as ta
import pandas as pd
import os
import numpy as np

from attr import define
from dotenv import load_dotenv
from ta.volatility import BollingerBands

from modules.crypto.processing import get_volume_analisys, get_volume_profile

load_dotenv()
bot = os.environ["telegram_token_bot"]

df = pd.read_csv('datasets/ETHUSDT-1m-sma-15.csv')

print(df)

df["EMA12"] = ta.ema(high=df.high, low=df.low, close=df.close, length=12)
df["RSI2"] = ta.rsi(high=df.high, low=df.low, close=df.close, length=14)
df['ATR2'] = df.ta.atr()
df['Momentum'] = df.ta.mom()
df['adx'] = ta.adx(high=df.high, low=df.low, close=df.close, length=14)['ADX_14']

print('---------------------')
df['pvt'] = ta.pvt(close=df.close, volume=df.volume)

indicator_bb = BollingerBands(close=df.close, window=14, window_dev=2)
df['bb_bbm'] = indicator_bb.bollinger_mavg()
df['bb_bbh'] = indicator_bb.bollinger_hband()
df['bb_bbl'] = indicator_bb.bollinger_lband()
df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()
df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()

macd = ta.macd(close=df.close, fast=12, slow=26, signal_indicators=True, signal=9)

df['macd_osc'] = macd['MACD_12_26_9']
df['macd_h'] = macd['MACDh_12_26_9']
df['macd_s'] = macd['MACDs_12_26_9']
df['macd_xa'] = macd['MACDh_12_26_9_XA_0']
df['macd_xb'] = macd['MACDh_12_26_9_XB_0']
df['macd_a'] = macd['MACD_12_26_9_A_0']

df.to_csv('test.csv')

vp = get_volume_profile(df)
ref_value = 3020
vp['mean_close'] = round(vp['mean_close'], 2)
vp['vp_trend'] = vp.pos_volume > vp.neg_volume
vp['total_trend'] = (vp.total_volume - vp.total_volume.shift(1)) >= 0
vp['dist_high'] = abs(ref_value - vp.high_close)
vp['dist_low'] = abs(ref_value - vp.low_close)
vp['dir'] = vp.dist_high > vp.dist_low
vp['profit'] = np.where(vp['dir'], ref_value + ((vp.dist_high * 90) / 100), ref_value - (vp.dist_low * 90) / 100)
vp['profit_value'] = np.where(vp['dir'], vp.dist_high, vp.dist_low)
vp['min_position'] = np.where(vp['dir'], (vp.mean_close - (vp.mean_close * .2 / 100)),
                              (vp.mean_close + (vp.mean_close * .2 / 100)))
vp['secure_position'] = np.where(vp['dir'], (vp.min_position >= ref_value) & (ref_value >= vp.low_close),
                                 (ref_value >= vp.min_position) & (ref_value <= vp.high_close))
print(vp)
res = get_volume_analisys(vp, ref_value=3000)
print(res)
