order_books = {
    "Bitcoin": {
        'crypto': 'BTC',
        'pair': 'USDT',
        'symbol': 'BTCUSDT'
    },
    "Etherium": {
        'crypto': 'ETH',
        'pair': 'USDT',
        'symbol': 'ETHUSDT'
    },
}

operatives = {}


class TraderOPS:
    def __init__(self):
        self.monitor = None
        self.configuration = {
            "1w": {
                'sma_s': 55,
                'sma_f': 10,
                'days': 1095,
                'days_s': 2000,
                'days_t': 2000,
                'plot': 90
            },
            '1d': {
                'sma_s': 55,
                'sma_f': 10,
                'days': 270,
                'days_s': 45,
                'days_t': 45,
                'plot': 90
            },
            '4h': {
                'sma_s': 55,
                'sma_f': 10,
                'days': 60,
                'days_s': 14,
                'days_t': 14,
                'plot': 90
            },
            '1h': {
                'sma_s': 55,
                'sma_f': 10,
                'days': 30,
                'days_s': 14,
                'days_t': 14,
                'plot': 90
            },
            '30m': {
                'sma_s': 55,
                'sma_f': 10,
                'days': 3,
                'days_s': 14,
                'days_t': 14,
                'plot': 90
            },
            '15m': {
                'sma_s': 55,
                'sma_f': 10,
                'days': 3,
                'days_s': 14,
                'days_t': 14,
                'plot': 90
            },
            '5m': {
                'sma_s': 55,
                'sma_f': 10,
                'days': 3,
                'days_s': 14,
                'days_t': 14,
                'plot': 90
            },
            '1m': {
                'sma_s': 55,
                'sma_f': 10,
                'days': 3,
                'days_s': 7,
                'days_t': 7,
                'plot': 90
            }
        }
        self.temporalities = {
            'large': {
                '1w': {
                    'trade': {
                        'close': 0,
                    },
                    'fingerprint': '2022-03-25 17:39:06',
                },
                '1d': {
                    'trade': {
                        'close': 0,
                    },
                    'fingerprint': '2022-03-25 17:39:06',
                },
            },
            'medium': {
                '4h': {
                    'trade': {
                        'close': 0,
                    },
                    'fingerprint': '2022-03-25 17:39:06',
                },
                '1h': {
                    'trade': {
                        'close': 0,
                    },
                    'fingerprint': '2022-03-25 17:39:06',
                },
            },
            'short': {
                '30m': {
                    'trade': {
                        'close': 0,
                    },
                    'fingerprint': '2022-03-25 17:39:06',
                },
                '15m': {
                    'trade': {
                        'close': 0,
                    },
                    'fingerprint': '2022-03-25 17:39:06',
                },
            },
            'micro': {
                '5m': {
                    'trade': {
                        'close': 0,
                    },
                    'fingerprint': '2022-03-25 17:39:06',
                },
                '1m': {
                    'trade': {
                        'close': 0,
                    },
                    'fingerprint': '2022-03-25 17:39:06',
                },
            }
        }
        self.indicators = [
            'timestamp', 'high', 'low', 'open', 'close', 'volume', 'ema_f', 'ema_s', 'f', 's', 'buy_ema', 'sell_ema',
            'buy_change', 'sell_change', 'RSI', 'RSIs', 'RSI_ups', 'momentum',
            'momentum_s',
            'momentum_ups', 'momentum_t', 'bb_bbm', 'b_m', 'bb_bbh', 'bb_bbl', 'bb_bbhi', 'bb_bbli', 'pvt', 'pvt_t'
        ]
        self.trade = {
            'temp': '',
            'operative': '',
            'value': 0,
            'last_temp': '',
            'last_time': '',
            'risk': 0,
            'last_risk': 0,
            'count_trend': 0,
            'trend': False,
            'last_trend': False,
            'trend_positive': 0,
            'trend_negative': 0,
            'action': '',
            'max': 0,
            'min': 0,
            'long': 0,
            'short': 0
        }
        self.effectivity = {
            'earn': {
                'long': {
                    'operations': 0,
                    'difference': 0,
                },
                'short': {
                    'operations': 0,
                    'difference': 0,
                }
            },
            'lose': {
                'long': {
                    'operations': 0,
                    'difference': 0,
                },
                'short': {
                    'operations': 0,
                    'difference': 0,
                }
            }
        }
        self.result_indicators = ['time', 'Local', 'Action', 'Temp', 'Operative', 'Value', 'Profit', 'Result',
                                  'Risk', 'Support', 'Resistance', 'Stop_Loss', 'profit', 'trend', 'volume_trend',
                                  'volume',
                                  'Time', 'Elapsed', 'MinDif', 'MaxDif',
                                  'Min', 'Max']
