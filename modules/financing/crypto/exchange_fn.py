from decimal import Decimal
import requests
import os

# Comisión
mxn_btc = Decimal("0.3")
btc_mxn = Decimal("0.0750")


def calculate_mxn_btc_comission(amount):
    return 0.500


def show_help_message(message, value):
    return "\n------------\n" + message + " " + value


def clear_console():
    clear = lambda: os.system("cls")
    clear()


def current_btc_orders():
    response = requests.get("https://api.bitso.com/v3/order_book/?book=btc_mxn")
    json_response = response.json()
    return json_response["payload"]


def current_btc_trades():
    response = requests.get("https://api.bitso.com/v3/trades/?book=btc_mxn")
    json_response = response.json()
    return json_response["payload"]


def current_stats(market):
    response = requests.get("https://api.bitso.com/v3/ticker/?book=" + market)
    json_response = response.json()
    return json_response["payload"]


def print_values(trade):
    return (
        "\nCompra: "
        + str(f"{Decimal(trade[0]):,}")
        + "\nComisión: "
        + str(f"{Decimal(trade[1]):,}")
        + "\nValor real: "
        + str(f"{Decimal(trade[2]):,}")
        + "\nDiferencia: "
        + str(f"{Decimal(trade[3]):,}")
    )


def trade_btc(mxn, price):
    trade = round(Decimal(mxn) * 1 / Decimal(price), 8)
    commission = round(
        (Decimal(trade) * Decimal(calculate_mxn_btc_comission(mxn))) / 100, 8
    )
    buyed = trade - commission
    return (trade, commission, buyed, commission)


def trade_mxn(mxn, btc, price):
    trade = round(btc * Decimal(price), 2)
    commission = round(
        (Decimal(trade) * Decimal(calculate_mxn_btc_comission(mxn))) / 100, 2
    )
    sale = round(trade - commission, 2)
    diference = sale - mxn
    return (trade, commission, sale, diference)


def trade_mxn_btc(btc, price):
    trade = round(btc * Decimal(price), 2)
    commission = round(
        (Decimal(trade) * Decimal(calculate_mxn_btc_comission(0))) / 100, 2
    )
    sale = round(trade - commission, 2)
    diference = trade - sale
    return (trade, commission, sale, diference)