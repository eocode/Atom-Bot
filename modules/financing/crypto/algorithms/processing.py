import numpy as np
import pandas as pd
import matplotlib
from datetime import datetime
from modules.financing.crypto.algorithms.extractor import get_file_name, convert_columns_to_float, \
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
    """
    This function takes a numpy array of last traded price
    and returns a list of support and resistance levels
    respectively. n is the number of entries to be scanned.
    """
    from scipy.signal import savgol_filter as smooth

    # converting n to a nearest even number
    if n % 2 != 0:
        n += 1

    n_ltp = ltp.shape[0]  # length of ltp

    # smoothening the curve
    # scipy.signal.savgol_filter(x, window_length, polyorder, deriv=0, delta=1.0, axis=- 1, mode='interp', cval=0.0)
    # window_lengthint
    #   The length of the filter window (i.e., the number of coefficients).
    # polyorderint
    #   The order of the polynomial used to fit the samples.
    ltp_s = smooth(ltp, (n + 1), 3)  # the polynomial is 3 in this sample
    # print('length of ltp_s: {}'.format(len(ltp_s)))

    # taking a simple derivative
    ltp_d = np.zeros(n_ltp)
    ltp_d[1:] = np.subtract(ltp_s[1:], ltp_s[:-1])
    # print('length of ltp_d: {}'.format(len(ltp_d)))

    resistance = []
    support = []

    for i in range(n_ltp - n):
        arr_sl = ltp_d[i:(i + n)]
        first = arr_sl[:int((n / 2))]  # first half
        last = arr_sl[int((n / 2)):]  # second half

        r_1 = np.sum(first > 0)
        r_2 = np.sum(last < 0)

        s_1 = np.sum(first < 0)
        s_2 = np.sum(last > 0)

        # local maxima detection
        if (r_1 == (n / 2)) and (r_2 == (n / 2)):
            resistance.append(ltp[i + (int(n / 2) - 1)])

        # local minima detection
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


def analysis(df, ma_f, ma_s, mas, time):
    df['last_close'] = df['close'].shift(1)
    df['close_variation'] = df['close'] - df['last_close']

    for ma in mas:
        df = simple_moving_average(ma, df, 'close')

    df['mean_close_%s_rv' % ma_f] = df['mean_close_%s' % ma_f].shift(1)
    df['mean_close_%s_rv' % ma_s] = df['mean_close_%s' % ma_s].shift(1)

    df['mean_f_diff'] = df['mean_close_%s' % ma_f] - df['mean_close_%s_rv' % ma_f]
    df['mean_s_diff'] = df['mean_close_%s' % ma_s] - df['mean_close_%s_rv' % ma_s]

    df['mean_s_diff_res'] = df['mean_s_diff'] >= 0
    df['mean_f_diff_res'] = df['mean_f_diff'] >= 0

    df['ema_f_ups'] = df.groupby((df['mean_f_diff_res'] != df['mean_f_diff_res'].shift(1)).cumsum()).cumcount() + 1

    df['buy_ema'] = df['mean_close_%s' % ma_f] > df['mean_close_%s' % ma_s]
    df['sell_ema'] = df['mean_close_%s' % ma_f] <= df['mean_close_%s' % ma_s]

    df['last_buy_ema'] = df['buy_ema'].shift(1)
    df['last_sell_ema'] = df['sell_ema'].shift(1)

    df['buy_ema_change'] = (df['buy_ema'] != df['last_buy_ema']) & df['buy_ema']
    df['sell_ema_change'] = (df['sell_ema'] != df['last_sell_ema']) & df['sell_ema']

    df['prev_buy_ema_change'] = df['buy_ema_change'].shift(1)
    df['prev_sell_ema_change'] = df['sell_ema_change'].shift(1)

    df['ema_s_ups'] = df.groupby((df['mean_s_diff_res'] != df['mean_s_diff_res'].shift(1)).cumsum()).cumcount() + 1
    df['ema_f_ups'] = df.groupby((df['mean_f_diff_res'] != df['mean_f_diff_res'].shift(1)).cumsum()).cumcount() + 1

    df = simple_moving_average(5, df, 'close')
    df['mean_close_5_rv'] = df['mean_close_5'].shift(1)
    df['mean_5_diff'] = df['mean_close_5'] - df['mean_close_5_rv']
    df['mean_5_diff_res'] = df['mean_5_diff'] >= 0

    df['ema_5_ups'] = df.groupby((df['mean_5_diff_res'] != df['mean_5_diff_res'].shift(1)).cumsum()).cumcount() + 1

    df['diff'] = df.close - df.open
    df['diffh'] = df.high - df.open
    df['diffl'] = df.low - df.open
    df['DIFF'] = df['diff'] >= 0

    df['ups'] = df.groupby((df['DIFF'] != df['DIFF'].shift(1)).cumsum()).cumcount() + 1

    df['up'] = df['diff'][df['diff'] >= 0]
    df['down'] = abs(df['diff'][df['diff'] < 0])

    df.fillna(value=0, inplace=True)

    df = simple_moving_average(14, df, 'up')
    df = simple_moving_average(5, df, 'down')
    df['RSI'] = 100 - (100 / (1 + df['mean_up_%s' % 14] / df['mean_down_%s' % 5]))

    convert_columns_to_float(df, ['diff'])
    convert_columns_to_float(df, ['diffh'])
    convert_columns_to_float(df, ['diffl'])
    convert_columns_to_float(df, ['up'])
    convert_columns_to_float(df, ['down'])
    convert_columns_to_float(df, ['RSI'])

    df['RSI_rv'] = df['RSI'].shift(1)
    df['RSI_diff'] = df['RSI'] - df['RSI_rv']
    df['positive_RSI'] = df['RSI_diff'] >= 0
    df['RSI_ups'] = df.groupby(
        (df['positive_RSI'] != df['positive_RSI'].shift(1)).cumsum()).cumcount() + 1

    length = 20
    # mult = 2
    length_KC = 20
    # mult_KC = 1.5

    # # calculate BB
    m_avg = df['close'].rolling(window=length).mean()

    # calculate bar value
    highest = df['high'].rolling(window=length_KC).max()
    lowest = df['low'].rolling(window=length_KC).min()
    m1 = (highest + lowest) / 2
    df['momentum'] = (df['close'] - (m1 + m_avg) / 2)
    fit_y = np.array(range(0, length_KC))
    df['momentum'] = df['momentum'].rolling(window=length_KC).apply(lambda x:
                                                                    np.polyfit(fit_y, x, 1)[0] * (length_KC - 1) +
                                                                    np.polyfit(fit_y, x, 1)[1], raw=True)

    df['momentum_rv'] = df['momentum'].shift(1)
    df['momentum_diff'] = df['momentum'] - df['momentum_rv']
    df['positive_momentum'] = df['momentum_diff'] >= 0
    df['momentum_ups'] = df.groupby(
        (df['positive_momentum'] != df['positive_momentum'].shift(1)).cumsum()).cumcount() + 1

    df['mom_t'] = df['momentum'] >= 0

    df['trend'] = df['positive_momentum'] & df['positive_RSI']

    if time in ('1w'):
        df['buy_trend'] = df['positive_momentum']
        df['sell_trend'] = (df['positive_momentum'] == False)

    if time in ('1d', '4h'):
        df['buy_trend'] = (df['positive_momentum'] & df['mean_5_diff_res'])
        df['sell_trend'] = (df['positive_momentum'] == False) & (df['mean_5_diff_res'] == False)

    if time in ('1h'):
        df['buy_trend'] = (df['positive_momentum'] & df['mean_f_diff_res'])
        df['sell_trend'] = (df['positive_momentum'] == False) & (df['mean_f_diff_res'] == False)

    if time in ('30m', '15m', '5m', '1m'):
        df['buy_trend'] = (df['mean_f_diff_res'] & df['sell_ema']) | (df['mean_f_diff_res'] & df['buy_ema'])
        df['sell_trend'] = (df['mean_f_diff_res'] == False & df['buy_ema']) | (
                df['mean_f_diff_res'] == False & df['sell_ema'])

    df['buy_confirmation'] = (df['buy_ema'])
    df['sell_confirmation'] = (df['sell_ema'])

    # df['buy_trade'] = (df['buy_ema'] == True) & (df['mean_f_diff_res'] == True) & (df['mean_s_diff_res'] == True) & (df['positive_momentum'] == True)
    # df['sell_trade'] = (df['sell_ema'] == True) & (df['mean_f_diff_res'] == False) & (df['mean_s_diff_res'] == False) & (df['positive_momentum'] == False)

    df.drop(columns=['mean_up_%s' % 14, 'mean_down_%s' % 5],
            inplace=True)

    df.dropna(inplace=True)

    return df


def plot_df(size, form, values, symbol, support, resistence, smas):
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
        plt.bar(df.index.values, df['volume'], width=0.9, color=df.DIFF.map({True: 'g', False: 'r'}))
        plt.title('Volume')

        plt.subplot(grid[0:2, 1])
        plt.hist(group['close'], weights=group['volume'], bins=values, orientation='horizontal')
        plt.title('VPVR')

        plt.subplot(grid[0, 0])
        plt.bar(df.index.values, df['momentum'], width=0.9, color=df.mom_t.map({True: 'g', False: 'r'}))
        plt.title('Momentum')

        plt.subplot(grid[3, :])
        plt.bar(df.index.values, df['diff'], width=0.9, bottom=df.open, color=df.DIFF.map({True: 'y', False: 'y'}))
        plt.bar(df.index.values, df['diffh'], width=0.3, bottom=df.open, color=df.DIFF.map({True: 'y', False: 'y'}))
        plt.bar(df.index.values, df['diffl'], width=0.3, bottom=df.open, color=df.DIFF.map({True: 'y', False: 'y'}))
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

        colors = ['b', 'm', 'c']

        legends = []
        for idx, sma in enumerate(smas):
            plt.plot(df['mean_close_%s' % sma], colors[idx])
            legends.append('SMA %s' % sma)

        plt.title(symbol)
        plt.ylabel('Price')
        plt.legend(legends)
        plt.grid(True)

        plt.savefig(get_file_name(symbol=symbol, form=form, size=size, data_type='png'))
    except Exception as e:
        print(e)


def download_test_data(symbol, items):
    try:
        for time, options in items:
            # Get Data
            data = get_binance_symbol_data(symbol=symbol, kline_size=time, auto_increment=False,
                                           save=True, sma=options['days_t'])
            # Analyse
            options['data'] = analysis(df=data, ma_f=options['sma_f'],
                                       ma_s=options['sma_s'],
                                       mas=options['smas'], time=time)
            save_extracted_data(symbol=symbol, df=options['data'], form='sma-%s' % options['days_t'],
                                size=time)
            save_clean_result(symbol, time, options['days_t'])
    except Exception as e:
        print('Error: ', e)


def load_test_data(items, trades, symbol):
    for time, options in items:
        trades[get_type_trade(time, trades)][time]['data'] = pd.read_csv(get_file_name(symbol, time,
                                                                                       'sma-%s' % options[
                                                                                           'days_t']))
