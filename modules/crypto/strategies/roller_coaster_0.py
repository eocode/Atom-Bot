from modules.crypto.strategies.builders import check_rsi, not_check_rsi


def rc_0(trade, temporalities, strategy):
    # Long
    if (
            (
                    check_rsi(temporalities=temporalities, available_sizes=strategy['available_sizes'])
            ) and temporalities['micro']['1m']['analysis']['secure_buy']
    ):
        return 'long', True
    # Short
    if (
            (
                    not_check_rsi(temporalities=temporalities, available_sizes=strategy['available_sizes'])
            ) and temporalities['micro']['1m']['analysis']['secure_buy']
    ):
        return 'short', True

    return None, False


def rc_0_evaluate(trade, temporalities, strategy):
    close = False

    # Long
    if trade['operative'] == 'long':
        if ((
                not temporalities['micro']['1m']['trade']['RSI'] and
                not temporalities['micro']['5m']['trade']['RSI'] and
                not temporalities['short']['15m']['trade']['RSI'] and
                not temporalities['short']['30m']['trade']['RSI'] and
                not temporalities['medium']['1h']['trade']['RSI'] and
                not temporalities['medium']['4h']['trade']['RSI']
        )):
            close = True

    # Short
    else:
        if ((
                temporalities['micro']['1m']['trade']['RSI'] and
                temporalities['micro']['5m']['trade']['RSI'] and
                temporalities['short']['15m']['trade']['RSI'] and
                temporalities['short']['30m']['trade']['RSI'] and
                temporalities['short']['30m']['trade']['RSI'] and
                temporalities['medium']['1h']['trade']['RSI'] and
                temporalities['medium']['4h']['trade']['RSI']
        )):
            close = True

    return close
