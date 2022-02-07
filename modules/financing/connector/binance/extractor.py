import os
import pandas as pd
from dateutil import parser
from datetime import datetime, timedelta
import dateparser
import pytz

from bot.brain import binance_client, binsizes
import math


def symbol_info(crypto, ref, exchange='BINANCE'):
    data = {}
    if exchange == 'BINANCE':
        info = binance_client.get_symbol_info(crypto + ref)
        data['min_quantity'] = float(info['filters'][2]['minQty'])
        data['max_quantity'] = float(info['filters'][2]['maxQty'])
        data['min_notional'] = float(info['filters'][3]['minNotional'])
        data['crypto_quantity'] = binance_client.get_asset_balance(asset=crypto).get('free')
        data['ref_quantity'] = binance_client.get_asset_balance(asset=ref).get('free')
    return data


def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds
    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"
    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/
    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)


def minutes_of_new_data(symbol, kline_size, data, source):
    global old, new
    if len(data) > 0:
        old = parser.parse(data["timestamp"].iloc[-1])
    elif source == "binance":
        old = datetime.strptime('1 Jan 2021', '%d %b %Y')
    if source == "binance":
        new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0],
                             unit='ms')
    return old, new


folder_path = 'datasets'
image_path = 'images'


def get_file_name(symbol, size, form='all', data_type='csv'):
    if data_type == 'csv':
        if not os.path.exists(image_path):
            os.mkdir(image_path)
        return folder_path + '/' + '%s-%s-%s.csv' % (symbol, size, form)
    if data_type == 'png':
        if not os.path.exists(image_path):
            os.mkdir(image_path)
        return image_path + '/' + '%s-%s-%s.png' % (symbol, size, form)
    else:
        return ''


def save_extracted_data(symbol, size, df, form='all'):
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    df.to_csv(get_file_name(symbol, size, form))


def merge_df(df_first, df_second, auto_increment=True):
    if len(df_first) > 0 and auto_increment:
        temp_df = pd.DataFrame(df_second)
        if len(df_second.index) > 0:
            data_df = df_first.append(temp_df).iloc[1:, :]
        else:
            data_df = df_first.append(temp_df)
    else:
        data_df = df_second
    data_df.set_index('timestamp', inplace=True)
    data_df.index.name = 'timestamp'
    return data_df


def get_data_frame(symbol, kline_size, form='all'):
    file_name = get_file_name(symbol, kline_size, form)
    if os.path.isfile(file_name):
        data_df = pd.read_csv(file_name)
    else:
        data_df = pd.DataFrame()
    return data_df


def convert_columns_to_float(df, columns):
    for column in columns:
        df[column] = df[column].astype(float)
        # df[column] = df[column].round(2)
    return df


def get_klines(symbol, kline_size, data_df):
    oldest_point, newest_point = minutes_of_new_data(symbol, kline_size, data_df, source="binance")
    delta_min = (newest_point - oldest_point).total_seconds() / 60
    available_data = math.ceil(delta_min / binsizes[kline_size])
    print(oldest_point, newest_point, available_data)
    return binance_client.get_historical_klines(symbol=symbol, interval=kline_size,
                                                start_str=oldest_point.strftime("%d %b %Y %H:%M:%S"),
                                                end_str=newest_point.strftime("%d %b %Y %H:%M:%S"))


def get_klines_times(symbol, kline_size, data, old_date=None, new_date=None):
    if old_date is None or new_date is None:
        old_date = (pd.to_datetime(data.iloc[-1:].timestamp.item()) + timedelta(minutes=1)).strftime(
            "%d %b %Y %H:%M:%S")
        new_date = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0],
                                  unit='ms').strftime("%d %b %Y %H:%M:%S")

    print(old_date, new_date)

    return binance_client.get_historical_klines(symbol=symbol, interval=kline_size,
                                                start_str=old_date,
                                                end_str=new_date)


def get_binance_symbol_data(symbol, kline_size, save=False, sma=None, auto_increment=True):
    if sma is None:
        form = 'all'
        data_df = get_data_frame(symbol, kline_size, form='all')
        klines = get_klines_times(symbol, kline_size, data_df)
    else:
        form = 'sma-%s' % sma
        data_df = get_data_frame(symbol, kline_size, form=form)
        if data_df.shape[0] < sma or auto_increment is False:
            oldest_point = (datetime.now() - timedelta(days=sma)).strftime("%d %b %Y %H:%M:%S")
            newest_point = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0],
                                          unit='ms').strftime("%d %b %Y %H:%M:%S")
            print(oldest_point, newest_point)
            klines = binance_client.get_historical_klines(symbol=symbol, interval=kline_size,
                                                          start_str=oldest_point,
                                                          end_str=newest_point)
        else:
            klines = get_klines_times(symbol, kline_size, data_df)

    data = pd.DataFrame(klines,
                        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    print(len(data.index))

    data.drop(['close_time', 'ignore', 'tb_base_av', 'quote_av', 'tb_quote_av'], axis='columns', inplace=True)

    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
    data['time'] = data['timestamp']
    data.set_index('timestamp', inplace=True, drop=False)

    convert_columns_to_float(data, ['open', 'high', 'low', 'close', 'volume',
                                    'trades'])

    data_df = merge_df(data_df, data, auto_increment)

    if save:
        save_extracted_data(symbol, kline_size, data_df, form=form)
    # print(data_df.shape)
    return data_df
