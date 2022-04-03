import datetime
from datetime import timedelta

from modules.financing.crypto.extractor import get_type_trade
from modules.financing.crypto.trades import trades


def check_if_update(size, crypto, strategy):
    if size not in strategy['available_sizes']:
        return False
    else:
        try:

            if size in strategy['reload_sizes']:
                size = '1m'

            current_time = datetime.datetime.utcnow()
            period = size[-1]
            t = int(size[:-1])
            delta = None
            full = True
            if period == 'm':
                full = True
                delta = timedelta(minutes=t)
            if period == 'h':
                full = True
                delta = timedelta(hours=t)
            if period == 'd':
                full = False
                delta = timedelta(days=t)
            if period == 'w':
                full = False
                delta = timedelta(weeks=t)
            lt = str(trades[crypto][get_type_trade(size, trades[crypto])][size]['fingerprint'])
            if full:
                last_time = datetime.datetime.strptime(lt, '%Y-%m-%d %H:%M:%S')
            else:
                last_time = datetime.datetime.strptime(lt, '%Y-%m-%d')
                current_time = datetime.datetime(current_time.year, current_time.month, current_time.day)
            updatable = current_time - delta
            return True if updatable >= last_time else False
        except Exception as e:
            print("Error al revisar actualizaciones")
            print(e)
            return False


def elapsed_time(crypto, trade, current=True):
    return round(elapsed_minutes(crypto=crypto, current=current, trade=trade) / 60, 2)


def elapsed_minutes(crypto, trade, current=True):
    if current:
        diff = (datetime.datetime.utcnow() - trade['fingerprint'])
    else:
        date_time_obj = datetime.datetime.strptime(str(trades[crypto]['micro']['1m']['fingerprint']),
                                                   '%Y-%m-%d %H:%M:%S')
        diff = (date_time_obj - trade['fingerprint'])
    return round(diff.total_seconds() / 60, 2)


def trade_variation(current, trade):
    return abs(round((1 - (current / trade['value'])) * 100, 2))


def profit(trade, crypto):
    if trade['operative'] == 'long':
        diff = float(trades[crypto]['micro']['1m']['trade']['close']) - (
            float(trade['value']))
    else:
        diff = (float(trade['value'])) - float(
            trades[crypto]['micro']['1m']['trade']['close'])
    return round(diff, 2)
