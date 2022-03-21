from modules.financing.crypto.trader import CryptoBot
from modules.financing.crypto.data.dictionary import binance_order_books

operatives = {}


class TraderOPS:
    def __init__(self):
        self.monitor = None


def initialize_operatives():
    print('Preparing')
    for key, value in binance_order_books.items():
        trader = TraderOPS()
        trader.monitor = CryptoBot(crypto=value['crypto'], ref=value['pair'],
                                   exchange='BINANCE')
        operatives[value['symbol']] = trader
    print('All prepared')


def start_operatives(chat_ids):
    print('Monitoring')
    for key, value in binance_order_books.items():
        operatives[value['crypto'] + value['pair']].monitor.start(chat_ids)
