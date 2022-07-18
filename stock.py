import pandas_datareader as web
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew

class Stock:

    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.valid = True
        self.price, self.clos = self.get_price()
        if self.valid:
            self.simple_returns, self.simple_mean = self.get_returns_simple()
            self.log_returns, self.log_mean = self.get_returns_log()
            self.worth = 0
            self.value = 0
            self.gain = self.gains()
            self.weight = 0
            self.optweight = 0
            self.shares = 0
            self.cb = 0

    def __repr__(self):
        return str(self.ticker)

    def get_price(self, delta = 365):
        end = dt.datetime.today()
        start = end - dt.timedelta(days=delta)
        try:
            clos = web.get_data_yahoo(self.ticker,start,end)['Close']
            price = clos[-1]
            return price, clos
        except:
            print('\nInvalid ticker')
            self.valid = False
            return 0, 0

    def get_returns_simple(self, delta = 365):
        _, clos = self.get_price(delta)
        simple_returns = clos.pct_change().dropna()
        return simple_returns, simple_returns.mean()

    def get_returns_log(self, delta = 365):
        _, adjclos = self.get_price(delta)
        log_returns = np.log(adjclos/adjclos.shift(1)).dropna()
        return log_returns, log_returns.mean()
    
    def gains(self, delta = 365):
        _, close = self.get_price(delta)
        return close[-1]-close[0]

    def dist_log(self, delta = 365):
        if delta != 365:
            returns, mean = self.get_returns_log(delta)
        else:
            returns, mean = self.log_returns, self.log_mean
        plot = plt.hist(100*returns, 35, density=True, facecolor='g')
        plt.title(f"${self.ticker}\nμ={mean:.4%}   med={np.median(returns):.4%}\nσ={returns.std():.4f}|S={skew(returns):.4f}|K={kurtosis(returns):.4f}")
        plt.ylabel('Frequency')
        plt.xlabel(f'Log Return %')
        plt.grid(True)
 
        if __name__ == '__main__':
            show()
        return plot

        
def show():
    plt.show()
    plt.clf()
                
if __name__ == '__main__':
    pass
