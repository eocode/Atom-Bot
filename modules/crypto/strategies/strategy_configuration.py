from modules.crypto.strategies.roller_coaster_0 import rc_0, rc_0_evaluate
from modules.crypto.strategies.roller_coaster_1 import rc_1, rc_1_evaluate

strategy_selector = {
    'rc_1': {
        'name': 'Roller Coaster 1',
        'size': '1m',
        'temp': 'micro',
        'base': 5,
        'update_size': 5,
        'execute': rc_1,
        'evaluate': rc_1_evaluate,
        'available_sizes': ['1m', '5m', '15m', '30m', '1h'],
        'reload_sizes': ['5m', '15m', '30m', '1h'],
        'period': {
            'BTC': 14,
            'ETH': 14
        },
    },
    'rc_0': {
        'name': 'Roller Coaster 0',
        'size': '1m',
        'temp': 'micro',
        'base': 1,
        'update_size': 1,
        'execute': rc_0,
        'evaluate': rc_0_evaluate,
        'available_sizes': ['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
        'reload_sizes': ['5m', '15m', '30m', '1h', '4h', '1d'],
        'period': {
            'BTC': 14,
            'ETH': 14
        }
    },
}
