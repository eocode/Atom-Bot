from binance.enums import SIDE_BUY, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC, SIDE_SELL
from binance.exceptions import BinanceAPIException

from bot.brain import binance_client


def create_order(symbol, quantity, price, operation='BUY'):
    order = None
    side = None
    if operation == 'BUY':
        side = SIDE_BUY
    if operation == 'SELL':
        side = SIDE_SELL
    try:
        order = binance_client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_LIMIT,
            timeInForce=TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=price)
    except BinanceAPIException as e:
        print(e)
    return order, order.get('orderId')


def cancel_order(symbol, order):
    order_id = order.get('orderId')
    cancel = binance_client.cancel_order(symbol=symbol, orderId=order_id)
    return cancel
