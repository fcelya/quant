from __future__ import absolute_import, division, print_function, unicode_literals

import operator
import pandas as pd
import sys, os
from copy import deepcopy as dc
from datetime import datetime
import multiprocessing as mp

sys.path.append("../libraries/backtrader")
from backtrader.utils.py3 import map
from backtrader import Analyzer, TimeFrame
from backtrader.mathsupport import average, standarddev
from backtrader.analyzers import AnnualReturn


class Logger01(Analyzer):

    params = (("log_path", None), ("data_df", None))

    def __init__(self):
        self.order_dict = dict()
        self.order_list = list()
        self.trade_dict = dict()
        self.trade_list = list()
        self.fund_dict = dict()
        self.fund_list = list()
        self.data_df = self.params.data_df
        if self.params.log_path is None:
            self.log_path = f"../backtests/automatically-set_{self.strategy.__name__}_{list(self.dnames.keys())[0]}_{datetime.now().isoformat()}"
            print("[Warning] - No log path provided")
        else:
            self.log_path = self.params.log_path
        self.i = 1

        pass

    def start(self):
        pass

    def next(self):
        pass

    def stop(self):
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        df = pd.DataFrame.from_dict(self.fund_list, orient="columns")
        df.to_csv(os.path.join(self.log_path, "funds.csv"))
        summary_df = df[["date", "value"]]
        self.fund_list = list()
        print("[LOG] - Funds logged")

        df = pd.DataFrame.from_dict(self.order_list, orient="columns")
        df.to_csv(os.path.join(self.log_path, "orders.csv"))
        self.order_list = list()
        print("[LOG] - Orders logged")

        trades = list()
        for k1 in self.strategy._trades.keys():
            for k2 in self.strategy._trades[k1].keys():
                for trade in self.strategy._trades[k1][k2]:
                    if self.i % 10 == 0:
                        print(self.i)
                        self.i += 1
                    if trade not in trades:
                        trades.append(trade)
                        self.append_trade(trade)
        df = pd.DataFrame.from_dict(self.trade_list, orient="columns")
        df.to_csv(os.path.join(self.log_path, "trades.csv"))
        trades = list()
        self.trade_list = list()
        print("[LOG] - Trades logged")

        if self.data_df is not None:
            self.data_df = self.data_df[
                ["date", "open", "high", "low", "close", "volume"]
            ]
            self.data_df.loc[:, "date"] = pd.to_datetime(
                pd.DatetimeIndex(self.data_df.loc[:, "date"]).normalize()
            )
            self.data_df.set_index("date")
            summary_df.loc[:, "date"] = pd.to_datetime(
                pd.DatetimeIndex(summary_df.loc[:, "date"]).normalize()
            )
            summary_df.set_index("date")
            summary_df = pd.concat(
                [summary_df, self.data_df], join="outer", ignore_index=False, axis=1
            )
            summary_df = summary_df[
                ["open", "high", "low", "close", "volume", "value", "date"]
            ]
            summary_df.fillna(0, inplace=True)
            # summary_df = summary_df.reset_index(drop=True)
        else:
            print(
                "[WARNING] - No data DataFrame provided. Summary log will have reduced data"
            )

        summary_df["close_returns"] = summary_df["close"].pct_change()
        summary_df["value_returns"] = summary_df["value"].pct_change()
        summary_df.to_csv(os.path.join(self.log_path, "summary.csv"))
        pass

    def notify_cashvalue(self, cash, value):
        """Receives the cash/value notification before each next cycle"""
        pass

    def notify_fund(self, cash, value, fundvalue, shares):
        """Receives the current cash, value, fundvalue and fund shares"""
        self.fund_dict["date"] = self.datas[0].datetime.date(0).isoformat()
        self.fund_dict["cash"] = cash
        self.fund_dict["value"] = value
        self.fund_dict["fundValue"] = fundvalue
        self.fund_dict["shares"] = shares
        self.fund_list.append(dc(self.fund_dict))
        pass

    def notify_order(self, order):
        """Receives order notifications before each next cycle"""
        self.order_dict["date"] = self.datas[0].datetime.date(0).isoformat()
        self.order_dict["reference"] = order.ref
        self.order_dict["orderType"] = order.ordtypename()
        self.order_dict["status"] = order.getstatusname()
        self.order_dict["size"] = order.size
        self.order_dict["price"] = order.price
        self.order_dict["priceLimit"] = order.pricelimit
        self.order_dict["trialAmount"] = order.trailamount
        self.order_dict["tiralPercent"] = order.trailpercent
        self.order_dict["executionType"] = order.getordername()
        if order.comminfo is not None:
            self.order_dict["commisionPercentage"] = order.comminfo.p.commission
            self.order_dict["commisionMargin"] = order.comminfo.p.margin
            self.order_dict["commisionType"] = order.comminfo._commtype
        else:
            self.order_dict["commisionPercentage"] = None
            self.order_dict["commisionMargin"] = None
            self.order_dict["commisionType"] = None
        self.order_dict["endOfSession"] = order.dteos
        self.order_dict["broker"] = order.broker
        self.order_dict["alive"] = order.alive()
        self.order_list.append(dc(self.order_dict))
        pass

    def notify_trade(self, trade):
        """Receives trade notifications before each next cycle"""
        # self.append_trade(trade)
        pass

    def append_trade(self, trade):
        self.trade_dict["date"] = self.datas[0].datetime.date(0).isoformat()
        self.trade_dict["reference"] = trade.ref
        # self.trade_dict["status"] = ['Created', 'Open', 'Closed'][trade.status]
        # self.trade_dict['data'] = trade.data
        # self.trade_dict["tradeId"] = trade.tradeid
        # self.trade_dict["size"] = trade.size
        self.trade_dict["price"] = trade.price
        # self.trade_dict["value"] = trade.value
        self.trade_dict["commission"] = trade.commission
        self.trade_dict["pnl"] = trade.pnl
        self.trade_dict["pnlNet"] = trade.pnlcomm
        self.trade_dict["justOpened"] = trade.justopened
        self.trade_dict["isOpen"] = trade.isopen
        self.trade_dict["isClosed"] = trade.isclosed
        # self.trade_dict["barOpen"] = trade.baropen
        self.trade_dict["dateOpen"] = trade.dtopen
        # self.trade_dict["barClose"] = trade.barclose
        self.trade_dict["dateClose"] = trade.dtclose
        self.trade_dict["barDuration"] = trade.barlen
        self.trade_list.append(dc(self.trade_dict))
        pass

    def get_analysis(self):
        print("No analysis")
        pass


class LoggerMicro(Analyzer):
    """
    WIP
    """

    params = (("log_path", None), ("data_df", None))

    def __init__(self):
        self.order_dict = dict()
        self.order_list = list()
        self.trade_dict = dict()
        self.trade_list = list()
        self.fund_dict = dict()
        self.fund_list = list()
        self.data_df = self.params.data_df
        if self.params.log_path is None:
            self.log_path = f"../backtests/automatically-set_{self.strategy.__name__}_{list(self.dnames.keys())[0]}_{datetime.now().isoformat()}"
            print("[Warning] - No log path provided")
        else:
            self.log_path = self.params.log_path
        self.i = 1

        pass

    def start(self):
        pass

    def next(self):
        pass

    def stop(self):
        if not os.path.exists(self.log_path):
            os.makedirs(self.log_path)

        df = pd.DataFrame.from_dict(self.fund_list, orient="columns")
        # df.to_csv(os.path.join(self.log_path, "funds.csv"))
        summary_df = df[["date", "value"]]
        # self.fund_list = list()
        # print("[LOG] - Funds logged")

        # df = pd.DataFrame.from_dict(self.order_list, orient="columns")
        # df.to_csv(os.path.join(self.log_path, "orders.csv"))
        # self.order_list = list()
        # print("[LOG] - Orders logged")

        # trades = list()
        # for k1 in self.strategy._trades.keys():
        #     for k2 in self.strategy._trades[k1].keys():
        #         for trade in self.strategy._trades[k1][k2]:
        #             if self.i % 10 == 0:
        #                 print(self.i)
        #                 self.i += 1
        #             if trade not in trades:
        #                 trades.append(trade)
        #                 self.append_trade(trade)
        # df = pd.DataFrame.from_dict(self.trade_list, orient="columns")
        # df.to_csv(os.path.join(self.log_path, "trades.csv"))
        # trades = list()
        # self.trade_list = list()
        # print("[LOG] - Trades logged")

        if self.data_df is not None:
            self.data_df = self.data_df[
                ["date", "open", "high", "low", "close", "volume"]
            ]
            self.data_df.loc[:, "date"] = pd.to_datetime(
                pd.DatetimeIndex(self.data_df.loc[:, "date"]).normalize()
            )
            self.data_df.set_index("date")
            summary_df.loc[:, "date"] = pd.to_datetime(
                pd.DatetimeIndex(summary_df.loc[:, "date"]).normalize()
            )
            summary_df.set_index("date")
            summary_df = pd.concat(
                [summary_df, self.data_df], join="outer", ignore_index=False, axis=1
            )
            summary_df = summary_df[
                ["open", "high", "low", "close", "volume", "value", "date"]
            ]
            summary_df.fillna(0, inplace=True)
            # summary_df = summary_df.reset_index(drop=True)
        else:
            print(
                "[WARNING] - No data DataFrame provided. Summary log will have reduced data"
            )

        summary_df["close_returns"] = summary_df["close"].pct_change()
        summary_df["value_returns"] = summary_df["value"].pct_change()
        summary_df.to_csv(os.path.join(self.log_path, "summary.csv"))
        pass

    def notify_cashvalue(self, cash, value):
        """Receives the cash/value notification before each next cycle"""
        pass

    def notify_fund(self, cash, value, fundvalue, shares):
        """Receives the current cash, value, fundvalue and fund shares"""
        self.fund_dict["date"] = self.datas[0].datetime.date(0).isoformat()
        self.fund_dict["cash"] = cash
        self.fund_dict["value"] = value
        self.fund_dict["fundValue"] = fundvalue
        self.fund_dict["shares"] = shares
        self.fund_list.append(dc(self.fund_dict))
        pass

    def notify_order(self, order):
        """Receives order notifications before each next cycle"""
        # self.order_dict["date"] = self.datas[0].datetime.date(0).isoformat()
        # self.order_dict["reference"] = order.ref
        # self.order_dict["orderType"] = order.ordtypename()
        # self.order_dict["status"] = order.getstatusname()
        # self.order_dict["size"] = order.size
        # self.order_dict["price"] = order.price
        # self.order_dict["priceLimit"] = order.pricelimit
        # self.order_dict["trialAmount"] = order.trailamount
        # self.order_dict["tiralPercent"] = order.trailpercent
        # self.order_dict["executionType"] = order.getordername()
        # if order.comminfo is not None:
        #     self.order_dict["commisionPercentage"] = order.comminfo.p.commission
        #     self.order_dict["commisionMargin"] = order.comminfo.p.margin
        #     self.order_dict["commisionType"] = order.comminfo._commtype
        # else:
        #     self.order_dict["commisionPercentage"] = None
        #     self.order_dict["commisionMargin"] = None
        #     self.order_dict["commisionType"] = None
        # self.order_dict["endOfSession"] = order.dteos
        # self.order_dict["broker"] = order.broker
        # self.order_dict["alive"] = order.alive()
        # self.order_list.append(dc(self.order_dict))
        pass

    def notify_trade(self, trade):
        """Receives trade notifications before each next cycle"""
        # self.append_trade(trade)
        pass

    def append_trade(self, trade):
        # self.trade_dict["date"] = self.datas[0].datetime.date(0).isoformat()
        # self.trade_dict["reference"] = trade.ref
        # # self.trade_dict["status"] = ['Created', 'Open', 'Closed'][trade.status]
        # # self.trade_dict['data'] = trade.data
        # # self.trade_dict["tradeId"] = trade.tradeid
        # # self.trade_dict["size"] = trade.size
        # self.trade_dict["price"] = trade.price
        # # self.trade_dict["value"] = trade.value
        # self.trade_dict["commission"] = trade.commission
        # self.trade_dict["pnl"] = trade.pnl
        # self.trade_dict["pnlNet"] = trade.pnlcomm
        # self.trade_dict["justOpened"] = trade.justopened
        # self.trade_dict["isOpen"] = trade.isopen
        # self.trade_dict["isClosed"] = trade.isclosed
        # # self.trade_dict["barOpen"] = trade.baropen
        # self.trade_dict["dateOpen"] = trade.dtopen
        # # self.trade_dict["barClose"] = trade.barclose
        # self.trade_dict["dateClose"] = trade.dtclose
        # self.trade_dict["barDuration"] = trade.barlen
        # self.trade_list.append(dc(self.trade_dict))
        pass

    def get_analysis(self):
        print("No analysis")
        pass
