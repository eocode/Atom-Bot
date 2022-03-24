from bot.connect.message_connector import logging_message, send_message, send_voice
from bot.connect.time_connector import convert_utc_to_local
from modules.financing.crypto.trades import trades
from modules.financing.crypto.utilities import elapsed_time, profit
import time


def logging_changes(size, crypto):
    if size == '1m':
        message = "-------------------------------------------------------------------\n" \
                  "%s actualizado:" % crypto
        message += "\n1m %s " % convert_utc_to_local(str(trades[crypto]['micro']['1m']['fingerprint']), size)
        message += "\n3m %s " % convert_utc_to_local(str(trades[crypto]['micro']['3m']['fingerprint']), size)
        message += "\n5m %s " % convert_utc_to_local(str(trades[crypto]['micro']['5m']['fingerprint']), size)
        message += "\n15m %s " % convert_utc_to_local(str(trades[crypto]['short']['15m']['fingerprint']), size)
        message += "\n30m %s " % convert_utc_to_local(str(trades[crypto]['short']['30m']['fingerprint']), size)
        message += "\n1h %s " % convert_utc_to_local(str(trades[crypto]['medium']['1h']['fingerprint']), size)
        message += "\n4h %s \n" % convert_utc_to_local(str(trades[crypto]['medium']['4h']['fingerprint']), size)
        logging_message(message)
    message = "1m   - RSI %s  | " % trades[crypto]['micro']['1m']['trade']['RSI']
    message += "3m  - RSI %s | " % trades[crypto]['micro']['3m']['trade']['RSI']
    message += "5m  - RSI %s | " % trades[crypto]['micro']['5m']['trade']['RSI']
    message += "15m - RSI %s | \n" % trades[crypto]['short']['15m']['trade']['RSI']
    message += "30m - RSI %s Momentum %s | " % (
        trades[crypto]['short']['30m']['trade']['RSI'],
        trades[crypto]['short']['30m']['trade']['Momentum'])
    message += "1h  - RSI %s | " % trades[crypto]['medium']['1h']['trade']['RSI']
    message += "4h  - RSI %s\n" % trades[crypto]['medium']['4h']['trade']['RSI']
    logging_message(message)
    logging_message("-------------------------------------------------------------------> %s actualizado en %s" % (crypto, size))


def notify(testing, message, action, trade, crypto, profit, save, chat_ids, effectivity):
    if action == 'Abrir':
        diff = 0
        win = message
    else:
        diff = profit
        win = 'Ganado' if diff >= 0 else 'Perdido'

    if not testing:
        trade['action'] = action
        if action == 'Abrir':
            message = "Inicia %s %s en %s" % (
                ('COMPRA' if trade['operative'] == 'long' else 'VENTA'), crypto,
                trades[crypto]['micro']['1m']['trade']['close'])
        if action == 'Continua':
            message = "Continua %s %s en %s" % (
                crypto, trade['operative'],
                trades[crypto]['micro']['1m']['trade']['close'])
        if action == 'Cerrar':
            message = "Cierra %s en %s\n" % (crypto, trades[crypto]['micro']['1m']['trade']['close'])
            message += "Resultado: %s con %s" % (win, profit)
        send_messages(trade=trade, chat_ids=chat_ids, message=message, play=False, alert=True, runs=3)
    else:
        row = [trades[crypto]['micro']['1m']['fingerprint'],
               convert_utc_to_local(trades[crypto]['micro']['1m']['fingerprint'], '1m'), action,
               trade['temp'], trade['operative'],
               trades[crypto]['micro']['1m']['trade']['close'], diff, win,
               trade['risk'],
               trade['last_time'], elapsed_time(trade=trade, crypto=crypto, current=False),
               round(trades[crypto]['micro']['1m']['trade']['close'] - trade['min'], 2),
               round(trades[crypto]['micro']['1m']['trade']['close'] - trade['max'], 2),
               trade['min'],
               trade['max']]
        save.append(row)
    if action == 'Cerrar':
        generate_stats(operative=trade['operative'], result=win, diff=diff, effectivity=effectivity)


def generate_stats(operative, result, diff, effectivity):
    # Earn
    if result == 'Ganado':
        effectivity['earn'][operative]['operations'] += 1
        effectivity['earn'][operative]['difference'] += diff
    # Lose
    else:
        effectivity['lose'][operative]['operations'] += 1
        effectivity['lose'][operative]['difference'] += diff


def send_messages(trade, chat_ids, message, play=False, alert=False, runs=1):
    print('ALERT')
    print(message)
    for i in range(runs):
        for cid in chat_ids:
            send_message(cid=cid, text=message, play=play)
            time.sleep(runs)
        if alert:
            send_voice(trade['action'])
