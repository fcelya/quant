import sys,os,re
sys.path.append('../libraries/backtrader')
import backtrader as bt

class PairTrading(bt.Strategy):

    params = (
        ('timeperiod', 20), 
        ('nbdevup', 1), 
        ('nbdevdn', 1),
        ('matype', 0),
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.stock[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self) -> None:
        # Keep a reference to the "close" line in the data[0] dataseries
        self.stock1close = self.stock1[0].close
        self.stock2close = self.stock2[0].close
        self.cointclose = self.coint[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Name of file where results will be stored
        #self.log_strategy = re.search("^(.*)\.py$",os.path.basename(__file__)).group(1)
        #self.log_data = list(self.dnames.keys())[0]

        # Add a Bollinger-Bands indicator to the Cointegration Feed
        self.upper, self.middle, self.lower = bt.talib.BBANDS(self.coint, timeperiod=self.params.timeperiod, nbdevup=self.params.nbdevup, nbdevdn=self.params.nbdevdn, matype=self.params.matype)


    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.cointclose[0] > self.boll[0]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy(data=stock1, )
                self.order = self.buy(data=stock2, )

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()