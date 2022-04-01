import numpy as np
import pandas as pd
import matplotlib
from datetime import datetime
import pandas_ta as ta

from modules.financing.crypto.extractor import get_file_name, convert_columns_to_float, \
    get_binance_symbol_data, save_extracted_data, save_clean_result, get_type_trade
import math

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import markers


def simple_moving_average(num, df, column):
    df['mean_%s_%s' % (column, num)] = df[column].rolling(window=int(num), min_periods=1).mean()
    convert_columns_to_float(df, ['mean_%s_%s' % (column, num)])
    return df


def simple_standard_deviation(num, df, column):
    df['std_%s_%s' % (column, num)] = df[column].rolling(window=int(num), min_periods=1).std(ddof=0)
    convert_columns_to_float(df, ['mean_%s_%s' % (column, num)])
    return df


def my_round(x, base=5):
    return abs(int(round(math.floor(x / base)) * base))


def round_minutes(minutes, base=5):
    result = my_round(minutes, base)
    return 60 - base if result == 60 else result


def supres(ltp, n):
    from scipy.signal import savgol_filter as smooth

    if n % 2 != 0:
        n += 1

    n_ltp = ltp.shape[0]

    ltp_s = smooth(ltp, (n + 1), 3)  # the polynomial is 3 in this sample

    ltp_d = np.zeros(n_ltp)
    ltp_d[1:] = np.subtract(ltp_s[1:], ltp_s[:-1])

    resistance = []
    support = []

    for i in range(n_ltp - n):
        arr_sl = ltp_d[i:(i + n)]
        first = arr_sl[:int((n / 2))]
        last = arr_sl[int((n / 2)):]

        r_1 = np.sum(first > 0)
        r_2 = np.sum(last < 0)

        s_1 = np.sum(first < 0)
        s_2 = np.sum(last > 0)

        if (r_1 == (n / 2)) and (r_2 == (n / 2)):
            resistance.append(ltp[i + (int(n / 2) - 1)])

        if (s_1 == (n / 2)) and (s_2 == (n / 2)):
            support.append(ltp[i + (int(n / 2) - 1)])

    return support, resistance


def get_stats(df):
    df['time'] = df.index

    df['time'] = pd.to_datetime(df['time'])

    df['day_hour'] = df.apply(
        lambda r: datetime(r['time'].year, r['time'].month, r['time'].day, r['time'].hour,
                           round_minutes(r['time'].minute)),
        axis=1)

    data = pd.DataFrame(df, columns=['day_hour', 'close'])
    dfgrouped = data.groupby('day_hour')
    dfmax = dfgrouped.max()
    dfmin = dfgrouped.min()
    max_mins = dfmax.join(dfmin, lsuffix='_max', rsuffix='_min')
    df.drop(columns=['time', 'day_hour'],
            inplace=True)

    return max_mins


def analysis(df, ma_f, ma_s, period):
    df["ema_f"] = ta.ema(high=df.high, low=df.low, close=df.close, length=ma_f)
    df["ema_s"] = ta.ema(high=df.high, low=df.low, close=df.close, length=ma_s)

    df.fillna(0, inplace=True)

    df['s'] = (df['ema_s'] - df['ema_s'].shift(1)) >= 0
    df['f'] = (df['ema_f'] - df['ema_f'].shift(1)) >= 0

    df['buy_ema'] = df['ema_f'] > df['ema_s']
    df['sell_ema'] = df['ema_f'] <= df['ema_s']

    df['buy_change'] = (df['buy_ema'] != df['buy_ema'].shift(1)) & df['buy_ema']
    df['sell_change'] = (df['sell_ema'] != df['sell_ema'].shift(1)) & df['sell_ema']

    df["RSI"] = ta.rsi(high=df.high, low=df.low, close=df.close, length=period)
    df['RSIs'] = (df['RSI'] - df['RSI'].shift(1)) >= 0
    df['RSI_ups'] = df.groupby(
        (df['RSIs'] != df['RSIs'].shift(1)).cumsum()).cumcount() + 1
    df['adx'] = ta.adx(high=df.high, low=df.low, close=df.close, length=period)['ADX_%s' % period]
    df['adx_s'] = (df['adx'] - df['adx'].shift(1)) >= 0
    df['adx_ups'] = df.groupby(
        (df['adx_s'] != df['adx_s'].shift(1)).cumsum()).cumcount() + 1
    df['ATR'] = df.ta.atr()

    df['close_variation'] = df['close'] - df['close'].shift(1)
    #
    # df = ema(df, ma_f, ma_s)
    # df = rsi(df, period)
    df = momentum(df)

    df['trend'] = df['momentum_s'] & df['RSIs']

    return df


def adx(data: pd.DataFrame, period: int):
    df = data.copy()
    alpha = 1 / period

    # TR
    df['H-L'] = df['high'] - df['low']
    df['H-C'] = np.abs(df['high'] - df['close'].shift(1))
    df['L-C'] = np.abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
    del df['H-L'], df['H-C'], df['L-C']

    # ATR
    df['ATR'] = df['TR'].ewm(alpha=alpha, adjust=False).mean()

    # +-DX
    df['H-pH'] = df['high'] - df['high'].shift(1)
    df['pL-L'] = df['low'].shift(1) - df['low']
    df['+DX'] = np.where(
        (df['H-pH'] > df['pL-L']) & (df['H-pH'] > 0),
        df['H-pH'],
        0.0
    )
    df['-DX'] = np.where(
        (df['H-pH'] < df['pL-L']) & (df['pL-L'] > 0),
        df['pL-L'],
        0.0
    )
    del df['H-pH'], df['pL-L']

    # +- DMI
    df['S+DM'] = df['+DX'].ewm(alpha=alpha, adjust=False).mean()
    df['S-DM'] = df['-DX'].ewm(alpha=alpha, adjust=False).mean()
    df['+DMI'] = (df['S+DM'] / df['ATR']) * 100
    df['-DMI'] = (df['S-DM'] / df['ATR']) * 100
    del df['S+DM'], df['S-DM']

    # ADX
    df['DX'] = (np.abs(df['+DMI'] - df['-DMI']) / (df['+DMI'] + df['-DMI'])) * 100
    df['adx'] = df['DX'].ewm(alpha=alpha, adjust=False).mean()
    df['adxs'] = (df['RSI'] - df['RSI'].shift(1)) >= 0
    del df['DX'], df['ATR'], df['TR'], df['-DX'], df['+DX'], df['+DMI'], df['-DMI']

    return df


def ema(df, ma_f, ma_s):
    df = simple_moving_average(ma_f, df, 'close')
    df = simple_moving_average(ma_s, df, 'close')

    df['slow'] = (df['mean_close_%s' % ma_s] - df['mean_close_%s' % ma_s].shift(1)) >= 0
    df['fast'] = (df['mean_close_%s' % ma_f] - df['mean_close_%s' % ma_f].shift(1)) >= 0

    df['fast_ups'] = df.groupby((df['fast'] != df['fast'].shift(1)).cumsum()).cumcount() + 1

    df['buy_ema'] = df['mean_close_%s' % ma_f] > df['mean_close_%s' % ma_s]
    df['sell_ema'] = df['mean_close_%s' % ma_f] <= df['mean_close_%s' % ma_s]

    df['buy_ema_change'] = (df['buy_ema'] != df['buy_ema'].shift(1)) & df['buy_ema']
    df['sell_ema_change'] = (df['sell_ema'] != df['sell_ema'].shift(1)) & df['sell_ema']

    return df


def rsi(df, period):
    df['avg'] = df.close - df.open
    df['diffh'] = df.high - df.open
    df['diffl'] = df.low - df.open
    df['price_up'] = df['avg'] >= 0

    df['price_ups'] = df.groupby((df['price_up'] != df['price_up'].shift(1)).cumsum()).cumcount() + 1

    df['up'] = df['avg'][df['avg'] >= 0]
    df['down'] = abs(df['avg'][df['avg'] < 0])

    df.fillna(value=0, inplace=True)

    df = simple_moving_average(period, df, 'up')
    df = simple_moving_average(period, df, 'down')
    df['RSI'] = 100 - (100 / (1 + df['mean_up_%s' % period] / df['mean_down_%s' % period]))

    convert_columns_to_float(df, ['avg'])
    convert_columns_to_float(df, ['up'])
    convert_columns_to_float(df, ['down'])
    convert_columns_to_float(df, ['RSI'])

    df['RSI_avg'] = df['RSI'] - df['RSI'].shift(1)
    df['RSIs'] = df['RSI_avg'] >= 0
    df['RSI_ups'] = df.groupby(
        (df['RSIs'] != df['RSIs'].shift(1)).cumsum()).cumcount() + 1

    df.drop(columns=['mean_up_%s' % period, 'mean_down_%s' % period],
            inplace=True)
    return df


def momentum(df):
    length = 20
    length_KC = 20

    m_avg = df['close'].rolling(window=length).mean()

    highest = df['high'].rolling(window=length_KC).max()
    lowest = df['low'].rolling(window=length_KC).min()
    m1 = (highest + lowest) / 2
    df['momentum'] = (df['close'] - (m1 + m_avg) / 2)
    fit_y = np.array(range(0, length_KC))
    df['momentum'] = df['momentum'].rolling(window=length_KC).apply(lambda x:
                                                                    np.polyfit(fit_y, x, 1)[0] * (length_KC - 1) +
                                                                    np.polyfit(fit_y, x, 1)[1], raw=True)

    df['momentum_s'] = (df['momentum'] - df['momentum'].shift(1)) >= 0
    df['momentum_ups'] = df.groupby(
        (df['momentum_s'] != df['momentum_s'].shift(1)).cumsum()).cumcount() + 1

    df['momentum_t'] = df['momentum'] >= 0

    convert_columns_to_float(df, ['momentum'])
    return df


def mfi(df, period):
    df['typical_price'] = (df['close'] + df['high'] + df['low']) / 3
    df['money_flow'] = df['typical_price'] * df['volume']
    df['last_typical_price'] = df['typical_price'].shift(1)
    df['positive_typical_price'] = df['typical_price'] > df['last_typical_price']

    df['mfi_up'] = df['money_flow'].where(df['typical_price'] > df['last_typical_price'], 0)
    df['mfi_down'] = df['money_flow'].where(df['typical_price'] < df['last_typical_price'], 0)

    df = simple_moving_average(period, df, 'mfi_up')
    df = simple_moving_average(period, df, 'mfi_down')
    df['MFI'] = 100 * (
            df['mean_mfi_up_%s' % period] / (df['mean_mfi_up_%s' % period] + df['mean_mfi_down_%s' % period]))
    df['MFIs'] = df['MFI'] > df['MFI'].shift(1)

    df['MFI_ups'] = df.groupby(
        (df['MFIs'] != df['MFIs'].shift(1)).cumsum()).cumcount() + 1

    df.drop(
        columns=['mean_mfi_up_%s' % period, 'mean_mfi_down_%s' % period, 'typical_price', 'money_flow',
                 'last_typical_price',
                 'positive_typical_price', 'mfi_up', 'mfi_down'],
        inplace=True)
    return df


def plot_df(size, form, values, symbol, support, resistence):
    try:
        df = pd.read_csv(get_file_name(symbol=symbol, size=size, form=form))

        pre = df.loc[:, ('close', 'volume')]
        pre['close'] = pre['close'].astype(int)
        group = df.groupby('close', as_index=False).agg({'volume': 'sum'})

        plt.cla()
        plt.clf()

        df = df.tail(values)

        group = group[(group.close >= df['close'].min()) & (group.close <= df['close'].max())]

        fig = plt.figure(figsize=(24, 12))

        fig.suptitle(symbol, fontsize=24)

        grid = plt.GridSpec(4, 2, wspace=.25, hspace=.5)

        plt.subplot(grid[2, :])
        plt.plot(df.RSI)
        plt.plot(df.index, 70 * np.ones(df.shape[0]), 'r')
        plt.plot(df.index, 30 * np.ones(df.shape[0]), 'g')
        plt.title('RSI')

        plt.subplot(grid[1, 0])
        plt.bar(df.index.values, df['volume'], width=0.9, color=df.price_up.map({True: 'g', False: 'r'}))
        plt.title('Volume')

        plt.subplot(grid[0:2, 1])
        plt.hist(group['close'], weights=group['volume'], bins=values, orientation='horizontal')
        plt.title('VPVR')

        plt.subplot(grid[0, 0])
        plt.bar(df.index.values, df['momentum'], width=0.9, color=df.mom_t.map({True: 'g', False: 'r'}))
        plt.title('Momentum')

        plt.subplot(grid[3, :])
        plt.bar(df.index.values, df['diff'], width=0.9, bottom=df.open, color=df.price_up.map({True: 'y', False: 'y'}))
        plt.bar(df.index.values, df['diffh'], width=0.3, bottom=df.open, color=df.price_up.map({True: 'y', False: 'y'}))
        plt.bar(df.index.values, df['diffl'], width=0.3, bottom=df.open, color=df.price_up.map({True: 'y', False: 'y'}))
        plt.scatter(df[(df.buy_trend == True)].index.values,
                    df[(df.buy_trend == True)]['close'].tolist(),
                    marker=markers.TICKUP, color='g', s=22 ** 2)
        plt.scatter(df[(df.sell_trend == True)].index.values,
                    df[(df.sell_trend == True)]['close'].tolist(),
                    marker=markers.TICKDOWN, color='r', s=22 ** 2)

        for sup in support:
            plt.axhline(y=sup, linewidth='1.0', color='red')
        for res in resistence:
            plt.axhline(y=res, linewidth='1.0', color='blue')

        plt.title(symbol)
        plt.ylabel('Price')
        plt.grid(True)

        plt.savefig(get_file_name(symbol=symbol, form=form, size=size, data_type='png'))
    except Exception as e:
        print(e)


def download_test_data(symbol, items, indicators, period):
    try:
        for time, options in items:
            # Get Data
            data = get_binance_symbol_data(symbol=symbol, kline_size=time, auto_increment=False,
                                           save=True, sma=options['days_t'])
            # Analyse
            options['data'] = analysis(df=data, ma_f=options['sma_f'],
                                       ma_s=options['sma_s'], period=period)

            save_extracted_data(symbol=symbol, df=options['data'], form='sma-%s' % options['days_t'],
                                size=time)
            save_clean_result(symbol, time, options['days_t'], indicators)
    except Exception as e:
        print('Error: ', e)


def load_test_data(items, trades, symbol):
    for time, options in items:
        df = pd.read_csv(get_file_name(symbol, time, 'sma-%s' % options['days_t']))
        trades[get_type_trade(time, trades)][time]['data'] = df


def save_result(df, symbol, crypto):
    df = df[df['Result'] != 'Iniciado']
    df = df[df['Result'] != 'Actualización']
    df_new = df.groupby(['Operative', 'Result'])['Profit'].agg(['sum', 'count']).reset_index(drop=False)
    total = df_new['count'].sum()
    total_price = df_new['sum'].abs().sum()
    df_new['%_price'] = (df_new['count'] * 100) / total
    df_new['%_by_price'] = (df_new['sum'] * 100) / total_price
    df_new = df_new.round(2)
    df_new.to_csv('backtesting/result_%s.csv' % symbol, index=False)
