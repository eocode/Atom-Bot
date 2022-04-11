from modules.crypto.strategies.builders import check_rsi, not_check_rsi


def rc_0(trade, temporalities, strategy):
    # Long
    if (
            check_rsi(temporalities=temporalities, available_sizes=strategy['available_sizes']) and
            temporalities['micro']['1m']['analysis']['trend'] and
            temporalities['micro']['1m']['analysis']['volume_trend'] and
            temporalities['micro']['1m']['analysis']['secure_buy']
    ):
        return 'long', True
    # Short
    if (
            not_check_rsi(temporalities=temporalities, available_sizes=strategy['available_sizes']) and
            not temporalities['micro']['1m']['analysis']['trend'] and
            not temporalities['micro']['1m']['analysis']['volume_trend'] and
            temporalities['micro']['1m']['analysis']['secure_buy']
    ):
        return 'short', True

    return None, False


def rc_0_evaluate(trade, temporalities, strategy):
    close = False

    # Long
    if trade['operative'] == 'long':
        if (temporalities['micro']['1m']['trade']['close'] <= temporalities['micro']['1m']['analysis']['stop_loss'] or (
                temporalities['micro']['1m']['analysis']['volume_trend'] and
                temporalities['micro']['1m']['analysis']['trend']
        ) or (
                temporalities['micro']['1m']['trade']['close'] >= temporalities['micro']['1m']['analysis'][
            'profit']
        )):
            close = True

    # Short
    else:
        if (temporalities['micro']['1m']['trade']['close'] >= temporalities['micro']['1m']['analysis']['stop_loss'] or (
                temporalities['micro']['1m']['analysis']['volume_trend'] and
                temporalities['micro']['1m']['analysis']['trend']
        ) or (
                temporalities['micro']['1m']['trade']['close'] <= temporalities['micro']['1m']['analysis'][
            'profit']
        )):
            close = True

    return close
