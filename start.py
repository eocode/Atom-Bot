from connect.message_connector import send_messsage_by_rest
from modules.core.model import get_groups
from bot.constants import version
from modules.crypto.data.structure import order_books, TraderOPS, operatives
from modules.crypto.trader import CryptoBot
import sys

if __name__ == "__main__":
    args = sys.argv
    args.pop(0)

    for key, value in order_books.items():
        trader = TraderOPS()
        trader.monitor = CryptoBot(crypto=value['crypto'], ref=value['pair'],
                                   exchange='BINANCE', configuration=trader.configuration,
                                   temporalities=trader.temporalities, trade=trader.trade, indicators=trader.indicators,
                                   effectivity=trader.effectivity, result_indicators=trader.result_indicators)
        operatives[value['symbol']] = trader

    chat_ids = []
    for group in get_groups():
        chat_ids.append(group.id)

        if len(args) > 0:
            msg = "Ejecutando Backtesting"
        else:
            msg = "Versión %s\n" % version
        send_messsage_by_rest(cid=group.id, text=msg)

    if len(args) > 0:
        print('BACKTESTING')
        for key, value in order_books.items():
            operatives[value['crypto'] + value['pair']].monitor.backtesting(chat_ids)
    else:
        for key, value in order_books.items():
            operatives[value['crypto'] + value['pair']].monitor.start(chat_ids)
