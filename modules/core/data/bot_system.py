from connect.binance_connector import BinanceConnector
from connect.sql_connector import SQLConnector

system_connectors = {}


def init_system():
    system_connectors['sql'] = SQLConnector()
    system_connectors['algorithms'] = BinanceConnector()


def system(value):
    if value not in system_connectors:
        init_system()
    return system_connectors[value]
