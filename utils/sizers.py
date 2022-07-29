from __future__ import absolute_import, division, print_function, unicode_literals

import operator
import pandas as pd
import sys, os
from copy import deepcopy as dc
from datetime import datetime

sys.path.append("../libraries/backtrader")
import backtrader as bt


class Ludopata(bt.Sizer):
    params = (("percent", 1),)

    def __init__(self):
        self.multiplier = self.params.multiplier
        print("[WARNING] - Sizer not configured. Buying fixed amount of shares")
        pass

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy = True and self.

        if isbuy=False and self.position

        size = cash  * (self.multiplier - comminfo.commission)
        return size
