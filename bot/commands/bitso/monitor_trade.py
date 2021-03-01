from utils.bitso_fn import current_stats
from bot.bot import bot, send_voice
from decimal import Decimal
import time


@bot.message_handler(commands=["monitor_trade"])
def monitor_trade(m):
    msg = bot.reply_to(
        m,
        "Indica el monto a notificar",
    )
    bot.register_next_step_handler(msg, monitor_trade_process)


def monitor_trade_process(message, market):
    try:
        # User chat
        cid = message.chat.id
        # Get price values
        monitor_price = Decimal(message.text)
        price = Decimal(current_stats(market)["ask"])
        bot.send_message(cid, "Ok. Te notificaré en cuanto algo suceda")
        # Indicators
        max_price = price
        max_price_percent = (price * 100 / max_price) - 100
        min_price = price
        min_price_percent = (price * 100 / min_price) - 100
        distance = max_price - min_price
        mid_distance = distance / 2

        # Start app
        while 1:
            # Update data
            bot.send_chat_action(cid, "typing")
            price = Decimal(current_stats(market)["ask"])
            percent = (price * 100 / monitor_price) - 100

            # Get stats
            if max_price < price:
                max_price = price
            if min_price > price:
                min_price = price

            max_price_percent = (price * 100 / max_price) - 100
            min_price_percent = (price * 100 / min_price) - 100
            if min_price_percent > 0.50:
                min_price = price
            if max_price_percent < -0.50:
                max_price = price
            distance = max_price - min_price
            mid_distance = distance / 2
            distance_max = max_price - mid_distance
            distance_min = min_price + mid_distance

            # Print info
            if price < monitor_price:

                if price > distance_max:
                    send_voice("Vela superior")

                if price < distance_min:
                    send_voice("Vela inferior")

                text = "ATENCIÓN al precio " + f"{Decimal(price):,.0f}"
                if min_price_percent == 0:
                    text2 = (
                        "Tendencia a la baja "
                        + f"{Decimal(percent):,.2f}"
                        + " por ciento"
                    )
                if min_price_percent > 0 and max_price_percent < 0:
                    text2 = (
                        "Recuperación del "
                        + f"{Decimal(min_price_percent):,.2f}"
                        + " por ciento"
                    )
                if max_price_percent == 0:
                    text2 = "Tendencia a la alza, nuevo máximo"
                text3 = (
                    "Máximo: "
                    + f"{Decimal(max_price_percent):,.2f}"
                    + " | "
                    + f"{Decimal(max_price):,.0f}"
                    + "\nMínimo: "
                    + f"{Decimal(min_price_percent):,.2f}"
                    + " | "
                    + f"{Decimal(min_price):,.0f}"
                    + "\nDistancia: "
                    + f"{Decimal(distance):,.0f}"
                    + "\n"
                )
                send_voice(text)
                send_voice(text2)
                bot.send_message(
                    cid,
                    text + "\n" + text2 + "\n" + text3,
                )

            if price == monitor_price:
                text = "Valor de compra " + f"{Decimal(price):,.0f}"
                bot.send_message(
                    cid,
                    text,
                )

            if price > monitor_price and abs(percent) == percent:
                text = "Por encima del valor de compra " + f"{Decimal(price):,.0f}"
                text2 = "Subiendo " + f"{Decimal(percent):,.2f}" + " por ciento"
                text3 = (
                    "Máximo: "
                    + f"{Decimal(max_price_percent):,.2f}"
                    + " | "
                    + f"{Decimal(max_price):,.0f}"
                    + "\nMínimo: "
                    + f"{Decimal(min_price_percent):,.2f}"
                    + " | "
                    + f"{Decimal(min_price):,.0f}"
                    + "\nDistancia: "
                    + f"{Decimal(distance):,.0f}"
                    + "\n"
                )
                bot.send_message(
                    cid,
                    text + "\n" + text2 + "\n" + text3,
                )

            time.sleep(5)
    except Exception as e:
        print(e)
        bot.reply_to(message, "Algo salio mal")