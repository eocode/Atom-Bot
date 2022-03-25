from modules.financing.crypto.trades import trades


def rc_15(crypto):
    # Long
    if ((
            trades[crypto]['micro']['1m']['trade']['RSI'] and
            trades[crypto]['micro']['5m']['trade']['RSI'] and
            trades[crypto]['short']['15m']['trade']['RSI'] and
            trades[crypto]['short']['30m']['trade']['RSI'] and
            trades[crypto]['medium']['1h']['trade']['RSI'] and
            trades[crypto]['medium']['4h']['trade']['RSI']) and (
            trades[crypto]['short']['15m']['trade']['Momentum']) and (
            trades[crypto]['micro']['5m']['trade']['Momentum']) or (
            trades[crypto]['micro']['5m']['trade']['RSI'] and
            trades[crypto]['micro']['1m']['trade']['RSI'] and
            trades[crypto]['short']['15m']['trade']['RSI'] and
            trades[crypto]['short']['30m']['trade']['RSI'] and
            trades[crypto]['medium']['1h']['trade']['RSI'] and
            trades[crypto]['medium']['4h']['trade']['RSI']) and
            (trades[crypto]['short']['30m']['trade']['Momentum'])):
        return 'long', True
    # Short
    if ((
            not trades[crypto]['micro']['1m']['trade']['RSI'] and
            not trades[crypto]['micro']['5m']['trade']['RSI'] and
            not trades[crypto]['short']['15m']['trade']['RSI'] and
            not trades[crypto]['short']['30m']['trade']['RSI'] and
            not trades[crypto]['medium']['1h']['trade']['RSI'] and
            not trades[crypto]['medium']['4h']['trade']['RSI']) and (
            not trades[crypto]['short']['15m']['trade']['Momentum']) and (
            not trades[crypto]['micro']['5m']['trade']['Momentum']) or (
            (not trades[crypto]['micro']['5m']['trade']['RSI'] and
             not trades[crypto]['micro']['1m']['trade']['RSI'] and
             not trades[crypto]['short']['15m']['trade']['RSI'] and
             not trades[crypto]['short']['30m']['trade']['RSI'] and
             not trades[crypto]['medium']['1h']['trade']['RSI'] and
             not trades[crypto]['medium']['4h']['trade']['RSI']) and (
                    not trades[crypto]['short']['30m']['trade']['Momentum']))):
        return 'short', True
    return None, False


def rc_15_evaluate(trade, crypto):
    close = False

    # Long
    if trade['operative'] == 'long':
        if (not trades[crypto]['micro']['5m']['trade']['RSI'] and
            not trades[crypto]['micro']['1m']['trade']['RSI'] and
            not trades[crypto]['micro']['5m']['trade']['mean_f']) or (
                not trades[crypto]['short']['15m']['trade']['Momentum']):
            close = True

    # Short
    else:
        if ((trades[crypto]['micro']['5m']['trade']['RSI'] and
             trades[crypto]['micro']['1m']['trade']['RSI'] and
             trades[crypto]['micro']['1m']['trade']['Momentum'] and
             trades[crypto]['micro']['5m']['trade']['mean_f']) or (
                trades[crypto]['short']['15m']['trade']['Momentum'])):
            close = True

    return close
