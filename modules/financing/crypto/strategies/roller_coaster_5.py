from modules.financing.crypto.trades import trades


def rc_5(crypto):
    # Long
    if (
            trades[crypto]['micro']['5m']['trade']['RSI'] and
            trades[crypto]['micro']['1m']['trade']['RSI'] and
            trades[crypto]['micro']['1m']['trade']['mean_f'] and
            trades[crypto]['medium']['1h']['trade']['Momentum']):
        return 'long', True
    # Short
    if (
            not trades[crypto]['micro']['1m']['trade']['RSI'] and
            not trades[crypto]['micro']['5m']['trade']['RSI'] and
            not trades[crypto]['micro']['5m']['trade']['mean_f'] and
            not trades[crypto]['medium']['1h']['trade']['Momentum']):
        return 'short', True
    return None, False


def rc_5_evaluate(trade, crypto):
    close = False

    # Long
    if trade['operative'] == 'long':
        if (not trades[crypto]['micro']['5m']['trade']['RSI'] and
                not trades[crypto]['micro']['1m']['trade']['RSI'] or
                not trades[crypto]['micro']['5m']['trade']['Momentum']):
            close = True

    # Short
    else:
        if (trades[crypto]['micro']['5m']['trade']['RSI'] and
                trades[crypto]['micro']['1m']['trade']['RSI'] or
                trades[crypto]['micro']['5m']['trade']['Momentum']):
            close = True

    return close
