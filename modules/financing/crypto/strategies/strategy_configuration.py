from modules.financing.crypto.strategies.roller_coaster_30 import rc_30, rc_30_evaluate

strategy_selector = {
    'rc_30': {
        'name': 'Roller Coaster 30',
        'size': '30m',
        'temp': 'short',
        'base': 30,
        'execute': rc_30,
        'evaluate': rc_30_evaluate,
        'available_sizes': ['1m', '5m', '15m', '30m'],
        'reload_with_sizes': ['1h', '30m']
    }
}
