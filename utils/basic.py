from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

import pandas as pd
sys.path.append('../libraries/backtrader')
sys.path.append('../')
import backtrader as bt
from utils.testers import TestStrategyComplete


def run_backtest_full(strategy=TestStrategyComplete,datapath='/home/fcelaya/quant/data/us/daily/aapl.csv',analyzers=None,custom_log_prefix=None,init_cash=100000.0,commission=0.00,margin=None):
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
            if "LOGGER" in analyzer.__name__.upper():
                cerebro.addanalyzer(analyzer,log_path=log_path,data_df=df)
            else:
                cerebro.addanalyzer(analyzer)

    # Set our desired cash start
    cerebro.broker.setcash(init_cash)
    cerebro.broker.setcommission(commission=commission,margin=margin)
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

    return log_path