import datetime
from datetime import timedelta

from modules.crypto.extractor import get_type_trade


def check_time(time):
    current_time = datetime.datetime.utcnow()
    return current_time.minute % time == 0


def set_risk(crypto, trades, trade):
    risk = round(
        (trades[crypto]['micro']['1m']['trade']['RSI_value'] + trades[crypto]['micro']['5m']['trade']['RSI_value'] +
         trades[crypto]['short']['15m']['trade']['RSI_value']) / 3, 2)

    trade['risk'] = risk


def check_if_update(size, crypto, strategy, temporalities):
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
            lt = str(temporalities[get_type_trade(size, temporalities)][size]['fingerprint'])
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


def elapsed_time(trade, temporalities, current=True):
    return round(elapsed_minutes(current=current, temporalities=temporalities, trade=trade) / 60, 2)


def elapsed_minutes(trade, temporalities, current=True):
    if current:
        diff = (datetime.datetime.utcnow() - trade['fingerprint'])
    else:
        date_time_obj = datetime.datetime.strptime(str(temporalities['micro']['1m']['fingerprint']),
                                                   '%Y-%m-%d %H:%M:%S')
        diff = (date_time_obj - trade['fingerprint'])
    return round(diff.total_seconds() / 60, 2)


def trade_variation(current, trade):
    return abs(round((1 - (current / trade['value'])) * 100, 2))


def profit(trade, temporalities):
    if trade['operative'] == 'long':
        diff = float(temporalities['micro']['1m']['trade']['close']) - (
            float(trade['value']))
    else:
        diff = (float(trade['value'])) - float(
            temporalities['micro']['1m']['trade']['close'])
    return round(diff, 2)
