from modules.financing.crypto.trades import trades


def rc_1(trade, crypto):
    risk = 0
    result = ''
    # Long
    if (
            trades[crypto]['micro']['1m']['trade']['mean_f'] and
            trades[crypto]['micro']['5m']['trade']['RSI'] and
            trades[crypto]['short']['15m']['trade']['RSI'] and
            trades[crypto]['short']['30m']['trade']['RSI'] and
            trades[crypto]['medium']['1h']['trade']['RSI']):
        result = 'long'
    # Short
    if (
            not trades[crypto]['micro']['1m']['trade']['mean_f'] and
            not trades[crypto]['micro']['5m']['trade']['RSI'] and
            not trades[crypto]['short']['15m']['trade']['RSI'] and
            not trades[crypto]['short']['30m']['trade']['RSI'] and
            not trades[crypto]['medium']['1h']['trade']['RSI']):
        result = 'short'

    if result != '':
        if trades[crypto]['micro']['1m']['trade']['ema']:
            risk += 10
        if trades[crypto]['short']['15m']['trade']['ema']:
            risk += 30
        if trades[crypto]['short']['15m']['trade']['ema']:
            risk += 30
        if trades[crypto]['short']['30m']['trade']['ema']:
            risk += 30

        trade['risk'] = risk
        return result, True
    else:
        return None, False


def rc_1_evaluate(trade, crypto):
    close = False

    risk = 0

    # Long
    if trade['operative'] == 'long':
        if (not trades[crypto]['micro']['1m']['trade']['mean_f'] and
                not trades[crypto]['micro']['5m']['trade']['RSI'] and
                not trades[crypto]['short']['15m']['trade']['RSI'] and
                not trades[crypto]['short']['30m']['trade']['RSI']):
            close = True

    # Short
    else:
        if (trades[crypto]['micro']['1m']['trade']['mean_f'] and
                trades[crypto]['micro']['5m']['trade']['RSI'] and
                trades[crypto]['short']['15m']['trade']['RSI'] and
                trades[crypto]['short']['30m']['trade']['RSI']):
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
