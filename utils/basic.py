from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import requests

import pandas as pd

sys.path.append("../libraries/backtrader")
import backtrader as bt

sys.path.append("../libraries/quantstats")
import quantstats as qs

sys.path.append("../")
from utils.testers import TestStrategyComplete

import yfinance as yf


def run_backtest_full(
    strategy=TestStrategyComplete,
    datapath="../data/us/daily/aapl.csv",
    analyzers=None,
    custom_log_prefix=None,
    init_cash=100000.0,
    commission=0.00,
    margin=None,
    writer=False,
    mult=1.0,
):
    """
    Runs a backtest on an asset
    INPUT
    strategy: [Optional, default = TestStrategyComplete] the strategy to test
    datapath: [Optional, defalut = "../data/us/daily/aapl.csv"] path of the csv where the backtest data is. Must contain datetime, open, high, low, close, volume
    analyzers: [Optional, default = None] The backtest analyzer, usually where the logger that records the results is chosen
    custom_log_prefix: [Optional, default = None] a prefix for the folder where the logger will save the results
    init_cash: [Optional, default = 100000.0] the initial money the trategy starts with
    comission: [Optional, default = 0.00] the comission. It will be a percentage of the operation value if margin == None, and a set value if margin != None (margin is a parameter used when backtesting futures-like contracts)
    mult: [Optional, default = 1.0] the multiplier applied to value of stocks, simulates leverage.
    """
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(strategy)

    df = pd.read_csv(datapath)
    df["date"] = pd.to_datetime(df["date"])
    # Create a Data Feed
    data = bt.feeds.PandasData(
        dataname=df, datetime=0, open=1, high=2, low=3, close=4, volume=5
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    cerebro.resampledata(data, name=datapath.replace("/", "-").replace("\\", "-"))

    if custom_log_prefix is not None:
        # chr(92) is the backslash
        log_path = f'../backtests/{custom_log_prefix}_{strategy.__name__}_{datapath.replace("/","-").replace(chr(92),"-")}_{datetime.now().isoformat()}'
    else:
        log_path = f'../backtests/{strategy.__name__}_{datapath.replace("/","-").replace(chr(92),"-")}_{datetime.now().isoformat()}'

    if analyzers is not None:
        for analyzer in analyzers:
            if "LOGGER" in analyzer.__name__.upper():
                cerebro.addanalyzer(analyzer, log_path=log_path, data_df=df)
            else:
                cerebro.addanalyzer(analyzer)

    # Set our desired cash start
    cerebro.broker.setcash(init_cash)
    cerebro.broker.setcommission(commission=commission, mult=mult)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    if writer:
        writer_path = os.path.join(log_path, "writer.csv")
        cerebro.addwriter(bt.WriterFile, csv=True, out=writer_path)

    # Print out the starting conditions
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run(exactbars=1)

    # Print out the final result
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

    return log_path


def get_report_complete(log_path, html=True, console=False):
    """
    Creates the quantstats report of a backtrader backtrade
    INPUTS
    log_path: [Obligatory] the path to the folder where the summary.csv is contained
    html: [Optional, default = True] Whether to create and store in the log_path a .html report
    console: [Optional, default = False] Whether to show the report as output

    """
    summary_path = os.path.join(log_path, "summary.csv")
    df = pd.read_csv(summary_path, index_col=0)
    df = df.fillna(0).set_index(pd.to_datetime(df["date"])).drop("date", axis=1)
    if html:
        html_path = os.path.join(log_path, "full_report.html")
        qs.reports.html(
            df.loc[:, "value_returns"],
            benchmark=df.loc[:, "close_returns"],
            download_filename=html_path,
        )
    if console:
        qs.reports.full(
            df.loc[:, "value_returns"], benchmark=df.loc[:, "close_returns"]
        )


def get_stock_data(
    tickers, path, date_start=None, date_end=None, period=None, in_conflict_keep="old"
):
    """
    Save a .csv with a stock ohlcv values
    INPUTS
    tickers: [Obligatory] arrray of tickers for which you want the csv downloaded
    path: [Obligatory] folder path where the csvs should be saved, existing or not
    date_start: [Optional, default = None] first data date as 'YYYY-MM-DD'. If None the maximum will be chosen
    date_end: [Optional, default = None] last data date as 'YYYY-MM-DD'. If None the maximum will be chosen
    period: [Optional, default = None] dates range, alternative to date_start and date_end. valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max. Alternative to data
    in_conflict_keep: [Optional, default = "old"] "old" or "new". If data already exists por a same date point, whether to keep the old or new data, as the file will be overwritten
    """

    if not os.path.exists(path):
        os.makedirs(path)

    if date_start is not None and date_end is not None:
        for ticker in tickers:
            data = yf.download(tickers=ticker, start=date_start, end=date_end)
            data_path = os.path.join(path, ticker.upper() + ".csv")
            data.columns = [c.lower() for c in data.columns]
            if os.path.exists(data_path):
                old_df = pd.read_csv(data_path, index_col=0)
                old_df.index = pd.to_datetime(old_df.index)
                if in_conflict_keep == "old":
                    final = old_df.combine_first(data)
                elif in_conflict_keep == "new":
                    final = data.combine_first(old_df)
                else:
                    raise ValueError(
                        'Parameter in_conflict_keep can only have two values: "old" or "new"'
                    )
            final.to_csv(data_path, index_label="date")
    elif period is not None:
        for ticker in tickers:
            data = yf.download(tickers=ticker, period=period)
            data_path = os.path.join(path, ticker.upper() + ".csv")
            data.columns = [c.lower() for c in data.columns]
            if os.path.exists(data_path):
                old_df = pd.read_csv(data_path, index_col=0)
                old_df.index = pd.to_datetime(old_df.index)
                if in_conflict_keep == "old":
                    final = old_df.combine_first(data)
                elif in_conflict_keep == "new":
                    final = data.combine_first(old_df)
                else:
                    raise ValueError(
                        'Parameter in_conflict_keep can only have two values: "old" or "new"'
                    )
            final.to_csv(data_path, index_label="date")
    else:
        print("[WARNING] - Either start and end date or period must be specified")


def save_download_file(path, url, name):
    """
    Downloads the file in a given URL and saves it
    INPUTS
    path: [Obligatory] the path where the file is to be saved
    url: [Obligatory] the URL where the file is located
    name: [Obligatory] name to be given to the file
    """
    if not os.path.exists(path):
        os.makedirs(path)
    req = requests.get(url)
    url_content = req.content
    file_path = os.path.join(path, name)
    with open(file_path, "wb") as f:
        f.write(url_content)
        f.close()


def get_files(path):
    """
    Returns the path to all the files in a given folder
    INPUTS
    path: [Obligatory] the folder path to inspect
    """
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
