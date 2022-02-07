from modules.financing.connector.binance.trader import CryptoBot
from modules.financing.data.dictionary import binance_order_books

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
