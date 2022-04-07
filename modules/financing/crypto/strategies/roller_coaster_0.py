from modules.financing.crypto.trades import trades


def rc_0(trade, crypto):
    risk = 0

    # Long
    if (
            trades[crypto]['micro']['1m']['trade']['mean_f'] and
            trades[crypto]['micro']['5m']['trade']['RSI'] and
            trades[crypto]['short']['15m']['trade']['RSI'] and
            trades[crypto]['short']['30m']['trade']['RSI']):
        return 'long', True
    # Short
    if (
            not trades[crypto]['micro']['1m']['trade']['mean_f'] and
            not trades[crypto]['micro']['5m']['trade']['RSI'] and
            not trades[crypto]['short']['15m']['trade']['RSI'] and
            not trades[crypto]['short']['30m']['trade']['RSI']):
        return 'short', True

    if trades[crypto]['micro']['1m']['trade']['ema']:
        risk += 10
    if trades[crypto]['short']['15m']['trade']['ema']:
        risk += 30
    if trades[crypto]['short']['15m']['trade']['ema']:
        risk += 30
    if trades[crypto]['short']['30m']['trade']['ema']:
        risk += 30

    trade['risk'] = risk

    return None, False


def rc_0_evaluate(trade, crypto):
    close = False

    risk = 0

    # Long
    if trade['operative'] == 'long':
        if (not trades[crypto]['micro']['1m']['trade']['mean_f'] and
                not trades[crypto]['micro']['5m']['trade']['RSI'] and
                not trades[crypto]['short']['15m']['trade']['RSI']):
            close = True

    # Short
    else:
        if (trades[crypto]['micro']['1m']['trade']['mean_f'] and
                trades[crypto]['micro']['5m']['trade']['RSI'] and
                trades[crypto]['short']['15m']['trade']['RSI']):
            close = True

    if trades[crypto]['micro']['1m']['trade']['ema']:
        risk += 10
    if trades[crypto]['short']['15m']['trade']['ema']:
        risk += 30
    if trades[crypto]['short']['15m']['trade']['ema']:
        risk += 30
    if trades[crypto]['short']['30m']['trade']['ema']:
        risk += 30

    trade['risk'] = risk

    return close
