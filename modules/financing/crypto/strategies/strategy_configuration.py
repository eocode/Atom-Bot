from modules.financing.crypto.strategies.roller_coaster_0 import rc_0, rc_0_evaluate
from modules.financing.crypto.strategies.roller_coaster_1 import rc_1, rc_1_evaluate
from modules.financing.crypto.strategies.roller_coaster_15 import rc_15, rc_15_evaluate
from modules.financing.crypto.strategies.roller_coaster_30 import rc_30, rc_30_evaluate
from modules.financing.crypto.strategies.roller_coaster_5 import rc_5, rc_5_evaluate

strategy_selector = {
    'rc_30': {
        'name': 'Roller Coaster 30',
        'size': '30m',
        'temp': 'short',
        'base': 30,
        'update_size': 15,
        'execute': rc_30,
        'evaluate': rc_30_evaluate,
        'available_sizes': ['1m', '5m', '15m', '30m'],
        'reload_sizes': ['15m', '30m', '1h', '4h', '1d', '1w'],
        'period': {
            'BTC': 9,
            'ETH': 48
        }
    },
    'rc_15': {
        'name': 'Roller Coaster 15',
        'size': '15m',
        'temp': 'short',
        'base': 15,
        'update_size': 5,
        'execute': rc_15,
        'evaluate': rc_15_evaluate,
        'available_sizes': ['1m', '5m', '15m'],
        'reload_sizes': ['15m', '30m', '1h', '4h', '1d', '1w'],
        'period': {
            'BTC': 24,
            'ETH': 48
        }
    },
    'rc_5': {
        'name': 'Roller Coaster 5',
        'size': '5m',
        'temp': 'micro',
        'base': 5,
        'update_size': 1,
        'execute': rc_5,
        'evaluate': rc_5_evaluate,
        'available_sizes': ['1m', '5m', '15m', '30m', '1h', '4h'],
        'reload_sizes': ['5m', '15m', '30m', '1h', '4h'],
        'period': {
            'BTC': 14,
            'ETH': 14
        }
    },
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
        'available_sizes': ['1m', '5m', '15m', '30m'],
        'reload_sizes': ['5m', '15m', '30m'],
        'period': {
            'BTC': 14,
            'ETH': 14
        }
    },
}
