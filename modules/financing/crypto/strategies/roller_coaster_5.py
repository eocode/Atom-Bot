from modules.financing.crypto.trades import trades


def rc_5(crypto):
    # Long
    if (
            trades[crypto]['micro']['1m']['trade']['RSI'] and
            trades[crypto]['micro']['3m']['trade']['RSI'] and
            trades[crypto]['micro']['5m']['trade']['RSI'] and
            trades[crypto]['short']['15m']['trade']['RSI'] and
            trades[crypto]['short']['30m']['trade']['RSI'] and
            trades[crypto]['short']['30m']['trade']['Momentum'] and
            trades[crypto]['micro']['5m']['trade']['ema']):
        return 'long', True
    # Short
    if (
            not trades[crypto]['micro']['1m']['trade']['RSI'] and
            not trades[crypto]['micro']['3m']['trade']['RSI'] and
            not trades[crypto]['micro']['5m']['trade']['RSI'] and
            not trades[crypto]['short']['15m']['trade']['RSI'] and
            not trades[crypto]['short']['30m']['trade']['RSI'] and
            not trades[crypto]['short']['30m']['trade']['Momentum'] and
            not trades[crypto]['micro']['5m']['trade']['ema']):
        return 'short', True
    return None, False


def rc_5_evaluate(trade, crypto):
    close = False

    # Long
    if trade['operative'] == 'long':
        if (not trades[crypto]['micro']['3m']['trade']['RSI'] and
            not trades[crypto]['micro']['5m']['trade']['RSI'] or
            not trades[crypto]['micro']['5m']['trade']['mean_f']) or (
                not trades[crypto]['micro']['5m']['trade']['ema']) or (
                not trades[crypto]['micro']['5m']['trade']['Momentum']
        ):
            close = True

    # Short
    else:
        if ((trades[crypto]['micro']['3m']['trade']['RSI'] and
             trades[crypto]['micro']['5m']['trade']['RSI'] or
             trades[crypto]['micro']['5m']['trade']['mean_f']) or (
                    trades[crypto]['micro']['5m']['trade']['ema'])) or (
                trades[crypto]['micro']['5m']['trade']['Momentum']
        ):
            close = True

    return close
