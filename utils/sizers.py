from __future__ import absolute_import, division, print_function, unicode_literals

import operator
import pandas as pd
import sys, os
from copy import deepcopy as dc
from datetime import datetime

sys.path.append("../libraries/backtrader")
import backtrader as bt


class Ludopata(bt.Sizer):
    params = (("percent", 0.5),)

    def __init__(self):
        self.percent = self.params.percent

        # print("[WARNING] - Sizer not configured. Buying fixed amount of shares")
        pass

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.strategy.getposition(data)
        if isbuy == True and not position:
            # size = cash * (self.percent - comminfo.commission)
            size = self.percent * cash / data[0]
        elif isbuy == False and position:
            # size = self.position
            size = position.size
        else:
            size = 0

        return size


class FixedSize(bt.Sizer):
    params = (("stake", 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        return self.params.stake


class FixedRerverser(FixedSize):
    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        size = self.p.stake * (1 + (position.size != 0))
        return size


class PairTrading(bt.Sizer):
    params = (('ponderacion', 0.5),)



    return 