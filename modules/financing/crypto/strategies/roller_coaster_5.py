from modules.financing.crypto.trades import trades


def rc_5(crypto):
    # Long
    if (
            trades[crypto]['micro']['1m']['trade']['mean_f'] and
            trades[crypto]['micro']['5m']['trade']['RSI'] and
            trades[crypto]['short']['15m']['trade']['RSI'] and
            trades[crypto]['short']['30m']['trade']['RSI'] and
            trades[crypto]['medium']['1h']['trade']['RSI'] and
            trades[crypto]['medium']['4h']['trade']['RSI']):
        return 'long', True
    # Short
    if (
            not trades[crypto]['micro']['1m']['trade']['mean_f'] and
            not trades[crypto]['micro']['5m']['trade']['RSI'] and
            not trades[crypto]['short']['15m']['trade']['RSI'] and
            not trades[crypto]['short']['30m']['trade']['RSI'] and
            not trades[crypto]['medium']['1h']['trade']['RSI'] and
            not trades[crypto]['medium']['4h']['trade']['RSI']):
        return 'short', True
    return None, False


def rc_5_evaluate(trade, crypto):
    close = False

    # Long
    if trade['operative'] == 'long':
        if (not trades[crypto]['micro']['1m']['trade']['mean_f'] and
                not trades[crypto]['micro']['5m']['trade']['RSI'] and
                not trades[crypto]['short']['15m']['trade']['RSI'] and
                not trades[crypto]['short']['30m']['trade']['RSI'] and
                not trades[crypto]['medium']['1h']['trade']['RSI']):
            close = True

    # Short
    else:
        if (trades[crypto]['micro']['1m']['trade']['mean_f'] and
                trades[crypto]['micro']['5m']['trade']['RSI'] and
                trades[crypto]['short']['15m']['trade']['RSI'] and
                trades[crypto]['short']['30m']['trade']['RSI'] and
                trades[crypto]['medium']['1h']['trade']['RSI']):
            close = True

    return close
