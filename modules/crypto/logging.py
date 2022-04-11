from connect.message_connector import logging_message, send_voice, send_messsage_by_rest
from connect.time_connector import convert_utc_to_local
from modules.crypto.extractor import get_type_trade
from modules.crypto.utilities import elapsed_time, profit, trade_variation
import time


def logging_changes(temporalities, available_sizes, crypto):
    logging_message(
        "-------------------------------------------------------------------> %s actualizado" % crypto)
    message = ''
    for size in available_sizes:
        length = get_type_trade(size, temporalities)
        rsi = temporalities[length][size]['trade']['RSI']
        t = temporalities[length][size]['analysis']['trend']
        vt = temporalities[length][size]['analysis']['volume_trend']
        s = temporalities[length][size]['analysis']['support']
        r = temporalities[length][size]['analysis']['resistance']
        b = temporalities[length][size]['analysis']['secure_buy']
        p = temporalities[length][size]['analysis']['profit']
        pv = temporalities[length][size]['analysis']['profit_value']
        v = temporalities[length][size]['analysis']['volume']
        sl = temporalities[length][size]['analysis']['stop_loss']
        m = temporalities[length][size]['analysis']['mean']
        message += "%s - RSI: %s | t: %s | vt: %s | b: %s | v: %s | s: %s | r: %s | p: %s | pv: %s | sl: %s | m: %s \n" % (
            size.ljust(3), ' 🟢 ' if rsi else ' 🔴 ', ' 🟢 ' if t else ' 🔴 ', ' 🟢 ' if vt else ' 🔴 ',
            ' 🟢 ' if b else ' 🔴 ', ' 🟢 ' if v else ' 🔴 ', s, r, p, pv, sl, m)
    logging_message(message)


def show_stats(effectivity, crypto, trade, chat_ids):
    total_operations = (
            (effectivity['earn']['long']['operations'] + effectivity['earn']['short']['operations']) +
            (effectivity['lose']['short']['operations'] + effectivity['lose']['long']['operations']))
    total_variation = (
            (effectivity['earn']['long']['difference'] + effectivity['earn']['short']['difference']) -
            (effectivity['lose']['short']['difference'] + effectivity['lose']['long']['difference']))
    earn_operations = (
            effectivity['earn']['long']['operations'] + effectivity['earn']['short']['operations'])
    earn_differences = (
            effectivity['earn']['long']['difference'] + effectivity['earn']['short']['difference'])
    lose_operations = (
            effectivity['lose']['long']['operations'] + effectivity['lose']['short']['operations'])
    lose_differences = (
            effectivity['lose']['long']['difference'] + effectivity['lose']['short']['difference'])
    message = "Eficiencia en %s\n\n" % crypto
    message += "Ganancias:\nTrades %s con %s\n" % (
        round(earn_operations, 2), round((earn_operations * 100) / total_operations, 2))
    message += "Variación: %s con %s\n\n" % (
        round(earn_differences, 2), round((earn_differences * 100) / total_variation, 2))
    message += "Perdidas:\nTrades %s con %s\n" % (
        round(lose_operations, 2), round((lose_operations * 100) / total_operations, 2))
    message += "Variación: %s con %s\n" % (
        round(lose_differences, 2), round((lose_differences * 100) / total_variation, 2))

    send_messages(trade=trade, chat_ids=chat_ids, message=message)


def show_operative(trade, process_is_started, symbol, operative, chat_ids, temporalities):
    if process_is_started:
        if operative:
            message = "%s\n" % symbol
            message += "Trend %s - %s\nRiesgo: %s - %s \n" % (
                trade['trend'],
                ' 🟢 ' if trade['operative'] == 'long' else ' 🔴 ',
                trade['risk'], trade['last_risk'])
            message += "Inicial: %s - Actual: %s \n" % (
                trade['value'], temporalities['micro']['1m']['trade']['close'])
            message += "Resultado: %s con %s\n\nStats\n" % (
                profit(trade=trade, temporalities=temporalities),
                trade_variation(current=temporalities['micro']['1m']['trade']['close'], trade=trade))

            message += "Tiempo: %s hrs\n" % (elapsed_time(trade=trade, current=True, temporalities=temporalities))
            message += "Máximo: %s con %s\n" % (
                round(trade['max']),
                trade_variation(trade=trade, current=round(trade['max'])))
            message += "Minimo: %s con %s\n\n" % (
                round(trade['min']),
                trade_variation(trade=trade, current=round(trade['min'])))
            message += "Longs %s - Shorts %s - %s Tendencia" % (
                trade['long'], trade['short'], temporalities['medium']['4h']['trade']['RSI'])
        else:
            message = "No hay ninguna operativa para %s actualmente" % symbol
    else:
        message = "Primero se debe iniciar el proceso de monitoreo para %s" % symbol
    send_messages(trade=trade, chat_ids=chat_ids, message=message)


def show_trade(chat_ids, trade, symbol):
    message = "%s en %s\n" % (symbol, ' 🟢 ' if trade['operative'] == 'long' else ' 🔴 ')
    message += "Soporte: %s \nResistencia: %s\n" % (trade['support'], trade['resistance'])
    message += "Profit: %s \nStopLoss: %s\n" % (trade['profit'], trade['stop_loss'])
    send_messages(trade=trade, chat_ids=chat_ids, message=message)


def notify(testing, message, action, trade, crypto, profit, save, chat_ids, effectivity, symbol, temporalities):
    if action == 'Abrir':
        diff = 0
        win = message
    else:
        diff = profit
        win = 'Ganado' if diff >= 0 else 'Perdido'

    if not testing:
        print(temporalities['micro']['1m']['analysis'])
        trade['action'] = action
        if action == 'Abrir':
            message = "Inicia %s %s en %s" % (
                ('COMPRA' if trade['operative'] == 'long' else 'VENTA'), crypto,
                temporalities['micro']['1m']['trade']['close'])
            show_trade(trade=trade, symbol=symbol, chat_ids=chat_ids)
        if action == 'Continua':
            message = "Continua %s %s en %s" % (
                crypto, trade['operative'],
                temporalities['micro']['1m']['trade']['close'])
        if action == 'Cerrar':
            message = "Cierra %s en %s\n" % (crypto, temporalities['micro']['1m']['trade']['close'])
            message += "Resultado: %s con %s" % (win, profit)
        send_messages(trade=trade, chat_ids=chat_ids, message=message, crypto=crypto, alert=True, runs=1)
    else:
        row = [temporalities['micro']['1m']['fingerprint'],
               convert_utc_to_local(temporalities['micro']['1m']['fingerprint'], '1m'), action,
               trade['temp'], trade['operative'],
               temporalities['micro']['1m']['trade']['close'], diff, win,
               trade['risk'],
               trade['last_time'], elapsed_time(trade=trade, current=False, temporalities=temporalities),
               round(temporalities['micro']['1m']['trade']['close'] - trade['min'], 2),
               round(temporalities['micro']['1m']['trade']['close'] - trade['max'], 2),
               trade['min'],
               trade['max']]
        save.append(row)
    if action == 'Cerrar':
        generate_stats(trade=trade, operative=trade['operative'], result=win, diff=diff, effectivity=effectivity)


def generate_stats(trade, operative, result, diff, effectivity):
    # Log Operations
    if operative == 'long':
        trade['long'] += 1
        trade['short'] = 0
    else:
        trade['short'] += 1
        trade['long'] = 0

    # Earn
    if result == 'Ganado':
        effectivity['earn'][operative]['operations'] += 1
        effectivity['earn'][operative]['difference'] += diff
    # Lose
    else:
        effectivity['lose'][operative]['operations'] += 1
        effectivity['lose'][operative]['difference'] += diff


def send_messages(trade, chat_ids, message, crypto='', alert=False, runs=1):
    print('ALERT')
    print(message)
    for i in range(runs):
        for cid in chat_ids:
            send_messsage_by_rest(cid=cid, text=message)
            time.sleep(runs)
        if alert:
            if trade['action'] == 'Abrir':
                send_voice(trade['operative'] + ' ' + crypto)
            if trade['action'] == 'Cerrar':
                send_voice(trade['action'] + ' ' + crypto)
