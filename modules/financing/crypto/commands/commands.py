from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from modules.core.data.user import get_user_info
from modules.financing.data.dictionary import binance_order_books
from modules.financing.data.operative import operatives
from bot.bot import bot
from bot.connect.message_connector import send_message, get_chat_info


@bot.message_handler(commands=["alertas"])
def command_operation(m):
    cid, verified, chat_name, group, admin, active = get_chat_info(m)
    if group['group']:
        for key, value in binance_order_books.items():
            status = operatives[value['crypto'] + value['pair']].monitor.show_operative(cid, False)
            if not status:
                break
    else:
        user = get_user_info(cid)
        if user.market in operatives:
            operatives[user.market].monitor.show_operative(cid, False)
        else:
            send_message(cid, 'Necesita preparar la operativa antes')


@bot.message_handler(commands=["ver_graficos"])
def command_operation(message):
    cid = message.chat.id
    user = get_user_info(cid)
    if user.market in operatives:
        operatives[user.market].monitor.get_market_graphs(bot, cid)
    else:
        send_message(cid, 'Necesita preparar la operativa antes')


@bot.message_handler(commands=["trade"])
def command_operation(message):
    cid = message.chat.id
    user = get_user_info(cid)
    if user.market in operatives:
        operatives[user.market].monitor.start(cid)


@bot.message_handler(func=lambda message: True, commands=["simular_trades"])
def message_handler(message):
    cid = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton("Si", callback_data="yes"),
               InlineKeyboardButton("No", callback_data="no"))
    bot.send_message(cid, "¿Quieres descargar nuevos datos de prueba?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    cid = call.message.chat.id
    print(cid)
    download = False
    if call.data == "yes":
        bot.answer_callback_query(call.id, "Descargando datos de prueba")
        download = True
    elif call.data == "no":
        bot.answer_callback_query(call.id, "Se usara la base de datos existente")
        download = False

    bot.send_chat_action(cid, "typing")
    user = get_user_info(cid)
    if user.market in operatives:
        operatives[user.market].monitor.make_simulation(cid=cid, download=download)
