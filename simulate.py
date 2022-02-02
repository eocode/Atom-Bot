from datetime import datetime, timedelta

import pandas as pd
from backtrader import BacktraderError

from bot.brain import binance_client
from modules.financing.connector.binance.trader import CryptoBot

import numpy as np

bot = CryptoBot(binance_client=binance_client, crypto='ETH', ref='USDT',
                exchange='BINANCE')
bot.start()

# support, resistence = supres(bot.configuration['1m']['data']['close'].to_numpy(), 30)

# print(support)
# print(resistence)

# supres_plot(bot.configuration['1m']['data'], support, resistence)
