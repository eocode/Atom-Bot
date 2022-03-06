from bot.connect.binance_connector import BinanceConnector
from bot.connect.sql_connector import SQLConnector

system_connectors = {}


def init_system():
    print("Initializing")
    system_connectors['sql'] = SQLConnector()
    system_connectors['algorithms'] = BinanceConnector()
    print("initialized")


def system(value):
    if value not in system_connectors:
        init_system()
    return system_connectors[value]
