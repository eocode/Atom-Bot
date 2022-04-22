import time

import pandas as pd

from connect.message_connector import send_messsage_by_rest
from connect.thread_connector import limit, async_fn
from modules.core.data.bot_system import system
from modules.crypto.extractor import get_binance_symbol_data, save_extracted_data, \
    get_file_name, get_type_trade, get_last_row_dataframe_by_time
from modules.crypto.logging import show_operative, logging_changes, notify, show_stats
from modules.crypto.processing import analysis, plot_df, supres, download_test_data, load_test_data, \
    save_result, get_volume_profile, get_volume_analisys
import datetime
from modules.crypto.strategies.strategy_configuration import strategy_selector
from modules.crypto.utilities import profit
import os
from dotenv import load_dotenv

load_dotenv()


class CryptoBot:

    def __init__(self, crypto, ref, configuration, temporalities, indicators, trade, effectivity,
                 result_indicators, exchange='BINANCE'):
        self.client = system('algorithms').client
        self.symbol = crypto + ref
        self.crypto = crypto
        self.ref = ref
        self.exchange = exchange

        # Default Values
        self.max_min = None
        self.order_status = None
        self.order = None
        self.process_is_started = False
        self.first_iteration = False
        self.trade_type = 'micro'
        self.operative = False

        # Settings
        self.strategy = strategy_selector[os.environ["strategy"]]
        self.configuration = configuration
        self.indicators = indicators
        self.result_indicators = result_indicators
        self.trade = trade
        self.effectivity = effectivity
        self.temporalities = temporalities

        self.testing = []
        self.chat_ids = []

    @limit(1)
    @async_fn
    def start(self, chat_ids=None):
        if not self.process_is_started:
            self.chat_ids = chat_ids
            self.process_is_started = True
            while True:
                for size, options in self.configuration.items():
                    if size in self.strategy['available_sizes']:
                        data = get_binance_symbol_data(symbol=self.symbol, kline_size=size, auto_increment=False,
                                                       save=False, sma=options['days_s'])
                        options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'],
                                                   period=self.strategy['period'][self.crypto])
                        df = options['data']
                        last_row = df.iloc[-1, :]
                        self.update_indicators(last_row=last_row, size=size)
                        length = get_type_trade(size, self.temporalities)
                        time.sleep(2)
                        vp = get_volume_profile(df)
                        self.temporalities[length][size]['analysis'] = get_volume_analisys(vp,
                                                                                           self.temporalities[length][
                                                                                               size]['trade'][
                                                                                               'close'])
                        # set_risk(self.crypto, trades, self.trade)
                        # self.evaluate_trend()
                        if self.first_iteration:
                            self.decide(testing=False)
                        time.sleep(2)
                logging_changes(temporalities=self.temporalities,
                                strategy=self.strategy, crypto=self.crypto)
                self.trade['last_risk'] = self.trade['risk']
                self.trade['last_trend'] = self.trade['trend']
                time.sleep(2)
                self.first_iteration = True
        else:
            # send_messages(trade=self.trade, chat_ids=self.chat_ids, message="Monitoreando %s " % self.crypto)
            print('Ya se ha iniciado el monitoreo de %s' % self.symbol)

    def evaluate_trend(self):
        if self.trade['risk'] > self.trade['last_risk']:
            self.trade['trend_positive'] += 1
        else:
            self.trade['trend_negative'] += 1

        self.trade['trend'] = self.trade['risk'] > self.trade['last_risk']

        if self.trade['trend'] != self.trade['last_trend']:
            self.trade['count_trend'] = 0
        else:
            self.trade['count_trend'] += 1

    @limit(1)
    @async_fn
    def backtesting(self, chat_ids, download=True):
        self.chat_ids = chat_ids

        print('Obteniendo Datos de %s' % self.crypto)

        if download:
            download_test_data(self.symbol, self.configuration.items(), self.indicators,
                               period=self.strategy['period'][self.crypto])

        print('Cargando datos de %s' % self.crypto)

        # Get Test Data
        load_test_data(self.configuration.items(), self.temporalities, self.symbol)
        main = self.temporalities[get_type_trade('1m', self.temporalities)]['1m']['data']

        tod = datetime.datetime.now()
        d = datetime.timedelta(days=15)
        timestamp = tod - d

        print("Initial Analysis: ", timestamp, self.crypto)

        main = main[main['timestamp'] >= str(timestamp)]
        self.process_is_started = True
        self.first_iteration = True

        for index, row in main.iterrows():
            print(self.temporalities['micro']['1m']['fingerprint'])
            self.update_indicators(last_row=row, size='1m')
            self.temporalities['micro']['1m']['analysis'] = get_volume_analisys(
                self.temporalities['micro']['1m']['data_vp'],
                self.temporalities['micro']['1m']['trade']['close'])
            self.update_indicators(
                last_row=get_last_row_dataframe_by_time(self.temporalities, '5m', row['timestamp']),
                size='5m')
            self.temporalities['micro']['5m']['analysis'] = get_volume_analisys(
                self.temporalities['micro']['5m']['data_vp'],
                self.temporalities['micro']['5m']['trade']['close'])
            self.update_indicators(
                last_row=get_last_row_dataframe_by_time(self.temporalities, '15m', row['timestamp']),
                size='15m')
            self.temporalities['short']['15m']['analysis'] = get_volume_analisys(
                self.temporalities['short']['15m']['data_vp'],
                self.temporalities['short']['15m']['trade']['close'])
            self.update_indicators(
                last_row=get_last_row_dataframe_by_time(self.temporalities, '30m', row['timestamp']),
                size='30m')
            self.temporalities['short']['30m']['analysis'] = get_volume_analisys(
                self.temporalities['short']['30m']['data_vp'],
                self.temporalities['short']['30m']['trade']['close'])
            self.update_indicators(
                last_row=get_last_row_dataframe_by_time(self.temporalities, '1h', row['timestamp']),
                size='1h')
            self.temporalities['medium']['1h']['analysis'] = get_volume_analisys(
                self.temporalities['medium']['1h']['data_vp'],
                self.temporalities['medium']['1h']['trade']['close'])
            self.update_indicators(
                last_row=get_last_row_dataframe_by_time(self.temporalities, '4h', row['timestamp']),
                size='4h')
            self.temporalities['medium']['4h']['analysis'] = get_volume_analisys(
                self.temporalities['medium']['4h']['data_vp'],
                self.temporalities['medium']['4h']['trade']['close'])
            self.update_indicators(
                last_row=get_last_row_dataframe_by_time(self.temporalities, '1d', row['timestamp']),
                size='1d')
            self.temporalities['large']['1d']['analysis'] = get_volume_analisys(
                self.temporalities['large']['1d']['data_vp'],
                self.temporalities['large']['1d']['trade']['close'])
            self.update_indicators(
                last_row=get_last_row_dataframe_by_time(self.temporalities, '1w', row['timestamp']),
                size='1w')
            self.temporalities['large']['1w']['analysis'] = get_volume_analisys(
                self.temporalities['large']['1w']['data_vp'],
                self.temporalities['large']['1w']['trade']['close'])
            self.decide(testing=True)
        df = pd.DataFrame(self.testing, columns=self.result_indicators)
        print('Saved results')
        df.to_csv('backtesting/trades_%s.csv' % self.symbol, index=False)
        save_result(df=df, symbol=self.symbol, crypto=self.crypto)
        show_stats(effectivity=self.effectivity, crypto=self.crypto, trade=self.trade, chat_ids=self.chat_ids)
        show_operative(trade=self.trade, process_is_started=self.process_is_started, symbol=self.symbol,
                       operative=self.operative, chat_ids=self.chat_ids, temporalities=self.temporalities)
        self.operative = False

    def decide(self, testing=False):
        if not self.operative:
            trade_operative, start = self.strategy['execute'](trade=self.trade, temporalities=self.temporalities,
                                                              strategy=self.strategy)
            if start:
                self.operative = True
                self.trade['trend_negative'] = 0
                self.trade['trend_positive'] = 0
                self.save_trade(self.temporalities['micro']['1m']['trade']['close'],
                                trade_operative)
                notify(testing=testing, message='Iniciado', action='Abrir', trade=self.trade, crypto=self.crypto,
                       profit=profit(trade=self.trade, temporalities=self.temporalities), save=self.testing,
                       chat_ids=self.chat_ids,
                       effectivity=self.effectivity, symbol=self.symbol, temporalities=self.temporalities)
        else:
            if self.temporalities['micro']['1m']['trade']['close'] > self.trade['max']:
                self.trade['max'] = self.temporalities['micro']['1m']['trade']['close']

            if self.temporalities['micro']['1m']['trade']['close'] < self.trade['min']:
                self.trade['min'] = self.temporalities['micro']['1m']['trade']['close']

            close = self.strategy['evaluate'](trade=self.trade, temporalities=self.temporalities,
                                              strategy=self.strategy)
            if close:
                self.trade['trend_negative'] = 0
                self.trade['trend_positive'] = 0
                self.operative = False
                if not testing:
                    print('notify')
                notify(testing=testing, message='Cierre', action='Cerrar', trade=self.trade, crypto=self.crypto,
                       profit=profit(trade=self.trade, temporalities=self.temporalities), save=self.testing,
                       chat_ids=self.chat_ids,
                       effectivity=self.effectivity, symbol=self.symbol, temporalities=self.temporalities)

    def update_indicators(self, size, last_row):
        length = get_type_trade(size, self.temporalities)
        self.temporalities[length][size]['fingerprint'] = last_row['time']
        self.temporalities[length][size]['last_minute'] = datetime.datetime.strptime(
            str(self.temporalities['micro']['1m']['fingerprint']), '%Y-%m-%d %H:%M:%S').minute
        self.temporalities[length][size]['trend'] = last_row['trend']
        self.temporalities[length][size]['trade']['high'] = last_row['high']
        self.temporalities[length][size]['trade']['low'] = last_row['low']
        self.temporalities[length][size]['trade']['close'] = last_row['close']
        self.temporalities[length][size]['trade']['RSI'] = last_row['RSIs']
        self.temporalities[length][size]['trade']['RSIs'] = last_row['RSI_ups']
        self.temporalities[length][size]['trade']['RSI_value'] = last_row['RSI']
        self.temporalities[length][size]['trade']['bbm'] = last_row['bb_bbm']
        self.temporalities[length][size]['trade']['bm_trend'] = last_row['b_m']
        self.temporalities[length][size]['trade']['bbh'] = last_row['bb_bbh']
        self.temporalities[length][size]['trade']['bbl'] = last_row['bb_bbl']
        self.temporalities[length][size]['trade']['pvt'] = last_row['pvt']
        self.temporalities[length][size]['trade']['pvt_t'] = last_row['pvt_t']
        self.temporalities[length][size]['trade']['mean_f'] = last_row['f']
        self.temporalities[length][size]['trade']['Momentum'] = last_row['momentum_s']
        self.temporalities[length][size]['trade']['Momentums'] = last_row['momentum_ups']
        self.temporalities[length][size]['trade']['Momentum_value'] = last_row['momentum']
        self.temporalities[length][size]['trade']['variation'] = last_row['close_variation']
        self.temporalities[length][size]['trade']['time'] = last_row['momentum_t']
        self.temporalities[length][size]['trade']['ema'] = last_row['buy_ema']

    def save_trade(self, close, operative):
        self.trade['operative'] = operative
        self.trade['value'] = close
        self.trade['support'] = self.temporalities[self.trade['last_temp']][self.trade['last_size']]['analysis']['mid'][
            'support']
        self.trade['resistance'] = \
            self.temporalities[self.trade['last_temp']][self.trade['last_size']]['analysis']['mid']['resistance']
        self.trade['profit'] = self.temporalities[self.trade['last_temp']][self.trade['last_size']]['analysis']['mid'][
            'profit']
        self.trade['trend'] = self.temporalities[self.trade['last_temp']][self.trade['last_size']]['analysis']['mid'][
            'trend']
        self.trade['volume_trend'] = \
            self.temporalities[self.trade['last_temp']][self.trade['last_size']]['analysis']['mid']['volume_trend']
        self.trade['volume'] = self.temporalities[self.trade['last_temp']][self.trade['last_size']]['analysis']['mid'][
            'volume']
        self.trade['secure_buy'] = \
            self.temporalities[self.trade['last_temp']][self.trade['last_size']]['analysis']['mid']['secure_buy']
        self.trade['stop_loss'] = \
            self.temporalities[self.trade['last_temp']][self.trade['last_size']]['analysis']['mid']['stop_loss']
        date_time_obj = datetime.datetime.strptime(str(self.temporalities['micro']['1m']['fingerprint']),
                                                   '%Y-%m-%d %H:%M:%S')
        self.trade['fingerprint'] = date_time_obj
        self.trade['max'] = close
        self.trade['min'] = close

    def get_market_graphs(self, bot=None, cid=None):

        for size, options in self.configuration.items():
            try:
                # Get Data
                data = get_binance_symbol_data(symbol=self.symbol, kline_size=size, auto_increment=False,
                                               save=True, sma=options['days'])
                # Analyse
                options['data'] = analysis(df=data, ma_f=options['sma_f'], ma_s=options['sma_s'],
                                           period=self.strategy['period'][self.crypto])
                save_extracted_data(symbol=self.symbol, df=options['data'], form='sma-%s' % options['days'],
                                    size=size)
                # options['min_max'] = get_stats(df=self.data)
                df = options['data'].tail(120)
                if len(df.index) > options['plot']:
                    options['support'], options['resistance'] = supres(df['close'].to_numpy(), options['plot'])
                    # Visualize data
                    plot_df(values=options['plot'], size=size, form='sma-%s' % options['days'],
                            symbol=self.symbol, support=options['support'], resistence=options['resistance'])

                    # Send results
                    photo = open(get_file_name(self.symbol, size, 'sma-%s' % options['days'], 'png'), 'rb')
                    if bot is not None:
                        send_messsage_by_rest(cid=cid, text=size)
                        bot.send_photo(cid, photo)
            except Exception as e:
                print('Error PLOT: ', e)
