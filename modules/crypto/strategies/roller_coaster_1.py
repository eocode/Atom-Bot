def rc_1(trade, temporalities, strategy):
    # Long
    if (
            temporalities['micro']['1m']['trade']['RSI'] and
            temporalities['micro']['5m']['trade']['RSI'] and
            temporalities['short']['15m']['trade']['RSI'] and
            temporalities['short']['30m']['trade']['RSI'] and
            temporalities['medium']['1h']['trade']['RSI']):
        return 'long', True
    # Short
    if (
            not temporalities['micro']['1m']['trade']['RSI'] and
            not temporalities['micro']['5m']['trade']['RSI'] and
            not temporalities['short']['15m']['trade']['RSI'] and
            not temporalities['short']['30m']['trade']['RSI'] and
            not temporalities['medium']['1h']['trade']['RSI']):
        return 'short', True

    return None, False


def rc_1_evaluate(trade, temporalities, strategy):
    close = False

    # Long
    if trade['operative'] == 'long':
        if (not temporalities['micro']['1m']['trade']['RSI'] and
                not temporalities['micro']['5m']['trade']['RSI'] and
                not temporalities['short']['15m']['trade']['RSI']):
            close = True

    # Short
    else:
        if (temporalities['micro']['1m']['trade']['RSI'] and
                temporalities['micro']['5m']['trade']['RSI'] and
                temporalities['short']['15m']['trade']['RSI']):
            close = True

    return close


def set_risk(crypto, temporalities, trade):
    risk = round(
        (temporalities['micro']['1m']['trade']['RSI_value'] + temporalities['short']['15m']['trade']['RSI_value'] +
         temporalities['short']['15m']['trade']['RSI_value'] + temporalities['short']['30m']['trade'][
             'RSI_value']) / 4, 2)

    trade['risk'] = risk
