from decimal import Decimal
from utils.bitso_fn import trade_btc, trade_mxn, print_values, show_help_message, current_btc

def show_btc_stats():
    current_btc_price = current_btc()
    result = ""
    result = result + "Valor actual: "+f"{Decimal(current_btc_price['ask']):,}"+'\n'
    result = result + "Min: "+f"{Decimal(current_btc_price['low']):,}"+ '\n'
    result = result + "Max: "+f"{Decimal(current_btc_price['high']):,}"+'\n'
    result = result + "Soporte: "+ f"{Decimal(current_btc_price['vwap']):,.2f}" + "\n"
    return result

def btc_escentials(current_btc_price, amount):
    amount = Decimal(amount)

    if current_btc_price == 0:
        current_btc_price = Decimal(current_btc()['ask'])
    else:
        print(current_btc_price)

    result = show_help_message("Entrada con "+f"{Decimal(amount):,}"," a "+f"{Decimal(current_btc_price):,}")
    a = trade_btc(amount,current_btc_price)
    result = result + print_values(a)
    result = result + show_help_message("Salida a ese momento","")
    b = trade_mxn(amount, a[2], current_btc_price)
    result = result + print_values(b)

    c = b
    price = current_btc_price
    while (c[3] < 0):
        price = Decimal(price) + Decimal(100)
        c = trade_mxn(amount, a[2], price)
    result = result + show_help_message("Salida optima a ",str(price))
    result = result + print_values(c)

    stop_lost = round(Decimal(amount) * Decimal(.01), 2) * -1
    d = b
    price = current_btc_price

    while (d[3] > stop_lost):
        price = Decimal(price) - Decimal(100)
        d = trade_mxn(amount, a[2], price)

    result = result + show_help_message("Stop Loss -1%: "+str(price)+" con un Stop Lost de $",str(stop_lost))
    result = result + print_values(d)

    stop_lost = round(Decimal(amount) * Decimal(.02), 2) * -1
    d = b
    price = current_btc_price

    while (d[3] > stop_lost):
        price = Decimal(price) - Decimal(100)
        d = trade_mxn(amount, a[2], price)

    result = result + show_help_message("Stop Loss -2%: "+str(price)+" con un Stop Lost de $",str(stop_lost))
    result = result + print_values(d)

    result = result + show_help_message("Escenarios positivos","")

    e = b
    price = current_btc_price

    for n in range(1,35,5):
        gain = round(Decimal(amount) * Decimal(n/100), 2)
        result = result + show_help_message("Ganancia: "+str(gain) + " al "+str(n)+"%","")

        while (e[3] < gain):
            price = Decimal(price) + Decimal(100)
            e = trade_mxn(amount, a[2], price)

        result = result + show_help_message("Vender al precio: "+str(price),"")
        result = result + print_values(e)

    return result