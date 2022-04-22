def rc_0(trade, temporalities, strategy):
    # Long
    if temporalities['medium']['4h']['trade']['RSI'] and temporalities['large']['1d']['trade']['RSI']:
        trade['temp'] = '4h'
        trade['last_temp'] = 'medium'
        trade['last_size'] = '4h'
        return 'long', True
    # Short
    if not temporalities['medium']['4h']['trade']['RSI'] and temporalities['large']['1d']['trade']['RSI']:
        trade['temp'] = '4h'
        trade['last_temp'] = 'medium'
        trade['last_size'] = '4h'
        return 'short', True

    return None, False


def rc_0_evaluate(trade, temporalities, strategy):
    close = False

    if trade['temp'] == '4h':
        # Long
        if trade['operative'] == 'long':
            if ((
                    not temporalities['medium']['4h']['trade']['RSI']
            )):
                close = True

        # Short
        else:
            if ((
                    temporalities['medium']['4h']['trade']['RSI']
            )):
                close = True

    return close
