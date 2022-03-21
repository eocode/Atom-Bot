from modules.financing.data.operative import initialize_operatives, operatives, start_operatives


def show_operatives(symbol):
    operatives[symbol].monitor.show_operative()


def get_monitor(symbol):
    return operatives[symbol].monitor


def init_operatives():
    initialize_operatives()


def prepare_trading(cid):
    start_operatives(cid)
