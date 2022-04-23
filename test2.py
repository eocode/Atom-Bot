import pandas_ta as ta
import pandas as pd
import os
import numpy as np

from attr import define
from dotenv import load_dotenv
from ta.volatility import BollingerBands

from modules.crypto.extractor import get_data_frame, get_klines_times
from modules.crypto.processing import get_volume_analisys, get_volume_profile

form = 'sma-%s' % 15
data_df = get_data_frame('ETHUSDT', '1m', form=form)
print(data_df)
klines = get_klines_times('ETHUSDT', '1m', data_df)
