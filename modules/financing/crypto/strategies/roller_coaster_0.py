from modules.financing.crypto.trades import trades


def rc_0(trade, crypto):
    risk = 0

    # Long
    if (
            trades[crypto]['micro']['1m']['trade']['RSI'] and
            trades[crypto]['micro']['5m']['trade']['RSI'] and
            trades[crypto]['short']['15m']['trade']['RSI'] and
            trades[crypto]['short']['30m']['trade']['RSI'] and
            trades[crypto]['medium']['4h']['trade']['RSI']):
        set_risk(crypto, trades, trade)
        return 'long', True
    # Short
    if (
            not trades[crypto]['micro']['1m']['trade']['RSI'] and
            not trades[crypto]['micro']['5m']['trade']['RSI'] and
            not trades[crypto]['short']['15m']['trade']['RSI'] and
            not trades[crypto]['short']['30m']['trade']['RSI'] and
            not trades[crypto]['medium']['4h']['trade']['RSI']):
        set_risk(crypto, trades, trade)
        return 'short', True

    return None, False


def rc_0_evaluate(trade, crypto):
    close = False

    risk = 0

    # Long
    if trade['operative'] == 'long':
        if (not trades[crypto]['micro']['1m']['trade']['RSI'] and
                not trades[crypto]['micro']['5m']['trade']['RSI'] and
                not trades[crypto]['short']['15m']['trade']['RSI'] and
                not trades[crypto]['short']['30m']['trade']['RSI'] and
                not trades[crypto]['medium']['1h']['trade']['RSI']):
            close = True

    # Short
    else:
        if (trades[crypto]['micro']['1m']['trade']['RSI'] and
                trades[crypto]['micro']['5m']['trade']['RSI'] and
                trades[crypto]['short']['15m']['trade']['RSI'] and
                trades[crypto]['short']['30m']['trade']['RSI'] and
                trades[crypto]['medium']['1h']['trade']['RSI']):
            close = True

    set_risk(crypto, trades, trade)

    return close


def set_risk(crypto, trades, trade):
    risk = round(
        (trades[crypto]['micro']['1m']['trade']['RSI_value'] + trades[crypto]['short']['15m']['trade']['RSI_value'] +
         trades[crypto]['short']['15m']['trade']['RSI_value'] + trades[crypto]['short']['30m']['trade'][
             'RSI_value']) / 4, 2)

    trade['risk'] = risk
