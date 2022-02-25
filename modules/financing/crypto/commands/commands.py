from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from modules.core.data.user import get_user_info
from modules.financing.data.trader import operatives
from modules.financing.model.trade import get_last_trade, save_current_price
from modules.financing.crypto.operations import get_stats, get_escential_data, current_stats
from bot.bot import bot
from modules.financing.data.user import Trade, trade_dict
from sqlalchemy.sql.expression import null
from decimal import Decimal
from datetime import datetime
import time
from bot.connect.communication import send_message


@bot.message_handler(commands=["operation"])
def command_operation(m):
    msg = bot.reply_to(
        m,
        "Simularemos una operación al precio actual. Escribe la cantidad a invertir en pesos mexicanos:",
    )
    bot.register_next_step_handler(msg, process_amount_step)


def process_amount_step(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        response = message.text
        if response.isdigit():
            send_message(cid, "Calculando para " + response)
            result = get_escential_data(0, response)
            bot.reply_to(message, result)
        else:
            send_message(
                cid,
                "Debe ser un valor númerico, intente otra vez ejecutando el comando",
            )
    except Exception as e:
        bot.reply_to(message, "Algo salio mal")


@bot.message_handler(commands=["simulation"])
def command_operation(m):
    msg = bot.reply_to(
        m,
        "Simularemos una operación a futuro. Escribe la cantidad a invertir en pesos mexicanos:",
    )
    bot.register_next_step_handler(msg, process_amount_future_step)


@bot.message_handler(commands=["trade_actual"])
def command_operation(message):
    cid = message.chat.id
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
        operatives['ETHUSDT'].monitor.start(cid)


@bot.message_handler(commands=["ver_analisis"])
def command_operation(message):
    cid = message.chat.id
    user = get_user_info(cid)
    if user.market in operatives:
        operatives[user.market].monitor.get_trades(cid, 1)


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


def trade_steps(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        response = message.text
        cid = message.chat.id
        user = get_user_info(cid)
        if user.market in operatives:
            operatives[user.market].monitor.make_simulation(cid)
    except Exception as e:
        bot.reply_to(message, "Algo salio mal")


@bot.message_handler(commands=["ver_resumen"])
def command_operation(message):
    cid = message.chat.id
    user = get_user_info(cid)
    if user.market in operatives:
        operatives[user.market].monitor.get_full_resumes(cid)


def process_amount_future_step(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        amount = message.text
        trade = Trade(amount)
        trade_dict[cid] = trade
        if amount.isdigit():
            msg = bot.reply_to(
                message, "¿Cuál es el precio del BTC con el que quieres simular?"
            )
            bot.register_next_step_handler(msg, process_price_future_step)
    except Exception as e:
        bot.reply_to(message, "Algo salio mal")


def process_price_future_step(message):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        price = message.text
        trade = trade_dict[cid]
        trade.price = price
        if trade.price.isdigit():
            result = get_escential_data(trade.price, trade.amount)
            send_message(cid, result)
    except Exception as e:
        bot.reply_to(message, "Algo salio mal")


@bot.message_handler(commands=["monitor"])
def command_start(m):
    msg = bot.reply_to(
        m,
        "Ingresa el monto en BTC a monitorear",
    )
    bot.register_next_step_handler(msg, process_btc_monitor_step)


def process_btc_monitor_step(message, market):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")
        starting_point = time.time()
        monitor_price = Decimal(message.text)

        elapsed_time = 0
        max_percent = 0

        while elapsed_time < 300:
            elapsed_time = int(time.time() - starting_point)
            message = get_stats()

            current_price = Decimal(current_stats(market)["ask"])
            percent = (current_price * 100 / monitor_price) - 100

            if percent > max_percent:
                max_percent = percent

            send_message(
                cid,
                str(current_price)
                + " |     "
                + f"{Decimal(percent):,.2f}"
                + "%"
                + "\nVariación: "
                + f"{Decimal(percent - max_percent):,.2f}",
            )

            time.sleep(5)
    except Exception as e:
        bot.reply_to(message, "Algo salio mal")


@bot.message_handler(commands=["smart_alerts"])
def command_start(message, market):
    try:
        cid = message.chat.id
        bot.send_chat_action(cid, "typing")

        current_price = Decimal(current_stats(market)["ask"])
        max_price = current_price
        min_price = current_price
        try:
            last_trade = get_last_trade()
            max_price = Decimal(last_trade[0])
            min_price = Decimal(last_trade[1])
        except:
            print("Query error")

        send_message(cid, "Te notificaré en cuanto algo interesante suceda")

        while 1:

            max_percent_diference = Decimal((max_price * 100 / current_price) - 100)
            min_percent_diference = Decimal((min_price * 100 / current_price) - 100)

            print(max_percent_diference, min_percent_diference)

            if current_price > max_price:
                max_price = current_price
                save_current_price(
                    datetime.now(),
                    "BTCMXN",
                    current_price,
                    max_price,
                    min_price,
                    datetime.now(),
                    null(),
                )
            else:
                if current_price < min_price:
                    min_price = current_price
                    save_current_price(
                        datetime.now(),
                        "BTCMXN",
                        current_price,
                        max_price,
                        min_price,
                        null(),
                        datetime.now(),
                    )
                else:
                    save_current_price(
                        datetime.now(),
                        "BTCMXN",
                        current_price,
                        max_price,
                        min_price,
                    )

            if max_percent_diference < -1:
                send_message(
                    cid,
                    "ATENCIÓN baja en el precio"
                    + " | "
                    + f"{Decimal(current_price):,.2f}"
                    + " | "
                    + f"{Decimal(max_percent_diference):,.2f}",
                )

            if min_percent_diference > 1:
                send_message(
                    cid,
                    "ATENCIÓN alta en el precio"
                    + " | "
                    + f"{Decimal(current_price):,.2f}"
                    + " | "
                    + f"{Decimal(max_percent_diference):,.2f}",
                )

            time.sleep(5)
            current_price = Decimal(current_stats(market)["ask"])
    except Exception as e:
        bot.reply_to(message, "Algo salio mal")
