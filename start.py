from bot.connect.message_connector import send_messsage_by_rest
from modules.core.model import get_groups
from modules.financing.crypto.data.dictionary import binance_order_books
from modules.financing.crypto.data.operative import TraderOPS, operatives
from bot.constants import version
from modules.financing.crypto.trader import CryptoBot

for key, value in binance_order_books.items():
    trader = TraderOPS()
    trader.monitor = CryptoBot(crypto=value['crypto'], ref=value['pair'],
                               exchange='BINANCE')
    operatives[value['symbol']] = trader

chat_ids = []
for group in get_groups():
    chat_ids.append(group.id)
    msg = "Actualizando a la versión %s\n" % version
    send_messsage_by_rest(cid=group.id, text=msg)

for key, value in binance_order_books.items():
    operatives[value['crypto'] + value['pair']].monitor.start(chat_ids)
