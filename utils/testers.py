from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

import pandas as pd
sys.path.append('../libraries/backtrader')
sys.path.append('../')
import backtrader as bt


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])
        pass

# Create a Stratey
class TestStrategyComplete(bt.Strategy):
    params = (
        ('maperiod', 15),
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] > self.sma[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

def test_run(strategy=TestStrategyComplete,datapath='/home/fcelaya/quant3/data/us/daily/aapl.csv',analyzers=None,custom_log_prefix=None):
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(strategy)

    df = pd.read_csv(datapath)
    df['date'] = pd.to_datetime(df['date'])

    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=df,datetime=0,open=1,high=2,low=3,close=4,volume=5)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    cerebro.resampledata(data,name=datapath.replace("/","-").replace("\\","-"))

    if custom_log_prefix is not None:
        # chr(92) is the backslash
        log_path = f'../backtests/{custom_log_prefix}_{strategy.__name__}_{datapath.replace("/","-").replace(chr(92),"-")}_{datetime.now().isoformat()}'
    else:
        log_path = f'../backtests/{strategy.__name__}_{datapath.replace("/","-").replace(chr(92),"-")}_{datetime.now().isoformat()}'

    if analyzers is not None:
        for analyzer in analyzers:
            if analyzer.__name__=="Logger01":
                cerebro.addanalyzer(analyzer,log_path=log_path)
            else:
                cerebro.addanalyzer(analyzer)

    # Set our desired cash start
    
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    writer_path = os.path.join(log_path,'writer.csv')
    cerebro.addwriter(bt.WriterFile, csv=True, out=writer_path)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run(exactbars=1)

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())