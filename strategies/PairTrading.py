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
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))
    
    def __init__(self) -> None:
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Name of file where results will be stored
        #self.log_strategy = re.search("^(.*)\.py$",os.path.basename(__file__)).group(1)
        #self.log_data = list(self.dnames.keys())[0]

        # Add a MovingAverageSimple indicator
        self.boll = bt.talib.BBANDS(self.dataSEÑAL, timeperiod=self.params.timeperiod, nbdevup=self.params.nbdevup, nbdevdn=self.params.nbdevdn, matype=self.params.matype)


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
                self.order = self.buy(data=1, SIZE_1)
                self.order = self.buy(data=2, SIZE_2)

        else:

            if self.dataclose[0] < self.sma[0]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()