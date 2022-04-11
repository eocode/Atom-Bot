from modules.crypto.extractor import get_type_trade


def check_rsi(temporalities, available_sizes):
    for size in available_sizes:
        length = get_type_trade(size, temporalities)
        if temporalities[length][size]['trade']['RSI']:
            continue
        else:
            return False
    return True


def not_check_rsi(temporalities, available_sizes):
    for size in available_sizes:
        length = get_type_trade(size, temporalities)
        if not temporalities[length][size]['trade']['RSI']:
            continue
        else:
            return False
    return True
