# from crynom.wrappers import timer
import pandas as pd
from stock import Stock, show
import matplotlib.pyplot as plt
from mean_var import optimal_portfolio, return_portfolios
import datetime as dt
import numpy as np
from scipy.stats import kurtosis, skew
import os


class Portfolio():

    def __init__(self, user):
        self.user = user
        self.stocks = []
        self.shares = []
        self.tix = []
        self.value = 0
        
    # @timer
    def add_stock(self, ticker, shares = 0, price = None, load = False, worth = 0):
            stock = Stock(ticker)
            if stock.valid:
                if ticker.upper() in self.tix:
                    i = self.tix.index(ticker.upper())
                    self.shares[i] += shares
                    stock.shares += shares
                    stock = self.stocks[i]
                else:
                    self.tix.append(ticker.upper())
                    self.shares.append(shares)
                    self.stocks.append(stock)
                i = self.tix.index(ticker.upper())
                stock.shares += shares
                if price == None:
                    stock.worth += stock.price * shares
                    stock.cb = stock.worth / stock.shares
                else:
                    stock.worth += price * shares
                    stock.cb = stock.worth / stock.shares
                if load == True:
                    stock.worth = worth
                    stock.cb = stock.worth / stock.shares
                    self.refresh()
                    return f"\nLoaded {shares:,} shares of ${stock} to {self.user}'s portfolio"
                self.refresh()
                return f"\nAdded {shares:,} shares of ${stock} to {self.user}'s portfolio"
            return 'Something went wrong, stock not added'

    # @timer
    def remove_stock(self, ticker, shares = None, price = None):
        if shares == None:
            if ticker.upper() in self.tix:
                i = self.tix.index(ticker.upper())
                del self.stocks[i]
                removed = self.shares.pop(i)
                self.refresh()
                return f"\nRemoved {removed} shares of {self.tix.pop(i)} from {self.user}'s portfolio"
        if ticker.upper() in self.tix:
            i = self.tix.index(ticker.upper())
            if shares >= self.shares[i]:
                del self.stocks[i]
                removed = self.shares.pop(i)
                self.refresh()
                return f"\nRemoved {removed} shares of {self.tix.pop(i)} from {self.user}'s portfolio"
            self.shares[i] -= shares
            self.stocks[i].shares -= shares
            if price == None:
                self.stocks[i].worth -= shares * self.stocks[i].price
            else:
                self.stocks[i].worth -= shares * price
            self.stocks[i].cb = self.stocks[i].worth / self.stocks[i].shares
            self.refresh()
            return f"\nRemoved {shares} shares of {self.tix[i]} from {self.user}'s portfolio"

    # @timer       
    def refresh(self):
        self.value = 0
        self.data = pd.DataFrame()
        for stock in self.stocks:
            self.data[stock.ticker] = stock.clos
        for stock in self.stocks:
            stock.value = stock.price * stock.shares
            self.value += stock.value
            self.weights = self.get_weights()
            if len(self.stocks) > 1:
                self.e_opt, self.v_opt, self.s_opt = self.optimal()
                self.returns = self.get_returns()
                self.expectation, self.variance, self. volatility = self.expect()
                self.volatility = np.sqrt(self.variance)
                self.returns_skew = skew(self.returns)
                self.returns_kurtosis = kurtosis(self.returns)

    # @timer
    def print_portfolio(self):
        user_format = ''
        while len(user_format) != len(self.user):
            user_format += '_'            
        print(f'''\n\n
Portfolio user: {self.user}
{user_format}_______________________

    Expected returns per period: {self.expectation:.5%} or ${self.expectation * self.value:.2f}
    
    Expected volatility: {self.volatility:.5f}
    
    Expected returns for 365 days: ${self.expectation * self.value * len(self.returns):,.2f} or {self.expectation * len(self.returns):,.2%}\n\n''')

        for stock in self.stocks:
            print(f'    Portfolio is {(stock.value/self.value):,.2%} ${stock} with {stock.shares:,} shares, worth ${stock.value:,.2f}')
            print(f'    Cost basis: ${stock.cb:,.2f}   Past year gain: ${stock.clos[-1] - stock.clos[0]:,.2f} | {sum(stock.log_returns):.2%}\n')
        print(f'''
        Total portfolio value: ${self.value:,.2f}
        
{user_format}_______________________\n''')
    
    # @timer
    def plot_stocks(self):
        for stock in self.stocks:
            stock.clos.plot()
            plt.title('Stock Price over Time')
            plt.ylabel('Price ($)')
            plt.grid(True)
            plt.legend(self.stocks)
        show()

    # @timer
    def optimal(self):
        period = np.log(self.data/self.data.shift(1)).dropna()
        weights, _, _, _ = optimal_portfolio(period[1:])
        for weight, stock in zip(weights, self.stocks):
            stock.optweight = weight
        expectation, variance, stddev = self.expect(weights = weights)
        return expectation, variance, stddev

    # @timer
    def generate_portfolio(self, vol = 50):
        if vol <= 100:
            selected = list(self.data)
            period = np.log(self.data[selected]/self.data[selected].shift(1)).dropna()
            weights, returns, risks, portw = optimal_portfolio(period[1:])
            v = int(len(portw) * vol / -100)
            if vol == 0:
                v = 0
            w = [portw[v][x][0] for x in range(len(portw[v]))]
            e, _, s = self.expect(weights = w)

            print(f'''\n\n
Portfolio on EF with {vol} percentile volatility:
_________________________________________________________

    Expected returns per period: {e:.5%}      ({returns[v]:.5%})

    Expected volatility: {s:.5f}               ({risks[v]:.5f})
    
    Expected return for 365 days: ${e * self.value * len(self.returns):,.2f} or {e * len(self.returns):,.2%}\n''')
            for stock, weight, optimal in zip(self.stocks, w, weights):
                print(f'''
    {weight:.2%} {stock}, or {(weight * self.value)/stock.price:,.5f} shares for ${(weight * self.value):,.2f} at ${stock.price:,.2f} per share

    Optimal Portfolio weight: {optimal:.2%}  shares: {(optimal * self.value)/stock.price:,.5f}   value: ${optimal * self.value:,.2f}
    Your Portfolio weight: {stock.weight:.2%}  shares: {stock.shares}   value: ${stock.value:,.2f}\n''')
    
            print('_________________________________________________________\n')
        else: print('\nInvalid Percentile.')

    # @timer
    def print_opt(self):
        print(f'''\n\n
Optimal Portfolio:
__________________________
        
    Expected returns per period: {self.e_opt:.5%}

    Expected volatility: {self.s_opt:.5f}

    Expected return for 365 days: ${len(self.returns) * self.e_opt * self.value:,.2f} or {self.e_opt * len(self.returns):.2%}\n\n''')
        for stock in self.stocks:
            print(f'    Portfolio is {stock.optweight:,.2%} ${stock} with {(stock.optweight * self.value)/stock.price:,.5f} shares, worth ${stock.optweight * self.value:,.2f}\n')
        print('__________________________\n')

    # @timer
    def EF(self):
        selected = list(self.data)
        period = np.log(self.data[selected]/self.data[selected].shift(1)).dropna()
        expected = period.mean()
        cov_matrix = period.cov()
        _, returns, risks, _ = optimal_portfolio(period[1:])
        df = return_portfolios(expected, cov_matrix)
        df.iloc[1:,:]
        df.plot.scatter(x = 'Volatility', y = 'Returns')
        plt.plot(risks,returns,"g--")
        plt.xlabel('Volatility (std. dev.)', fontsize = 14)
        plt.ylabel('Returns', fontsize = 14)
        plt.title('Efficient Frontier', fontsize = 16)
        plt.grid(True)
        show()

    # @timer
    def print_gains(self, delta = 365):
        print('\n')
        total = 0
        for stock in self.stocks:
            print(f'${stock} has gained ${stock.gain:,.2f} in the past {delta:,} days, or {sum(stock.log_returns):.2%}.\n')
            total += stock.gain
        print(f'    Total gain: ${total:,.2f}\n')
        self.year_gain = total

    # @timer
    def plot_logdist(self, delta = 365):
        rows = int(np.sqrt(len(self.stocks)))
        columns = int(np.ceil(len(self.stocks) / rows))
        if len(self.stocks) == 1:
            columns = 1
        elif len(self.stocks) == 2:
            columns = 2
        elif len(self.stocks) == 3:
            rows = 2
            columns = 2
        fig, ax = plt.subplots(rows, columns, constrained_layout = True)
        for index, stock in enumerate(self.stocks,1):
            plt.subplot(rows, columns, index)
            stock.dist_log(delta)
        fig.suptitle(f"Log distribution for stocks in {self.user}'s portfolio for {delta} days")
        show()
       
    # @timer
    def plot_portfolio_logdist(self):
        plt.hist(100 * self.returns, 35, density=True, facecolor='g')
        plt.title(f"{self.user}'s Portfolio Returns Dist\nμ={self.returns.mean():.4%}   med={np.median(self.returns):.4%}\nσ={self.returns.std():.4f}|S={skew(self.returns):.4f}|K={kurtosis(self.returns):.4f}")
        plt.ylabel('Frequency')
        plt.xlabel(f'Log Return %')
        plt.grid(True)
        show()

    # @timer
    def expect(self, weights = None):
        expectation = 0
        variance = 0
        if weights == None:
            weights = self.weights
            self.weights = self.get_weights()
        for stock, weight in zip(self.stocks, weights):
            expectation += weight * stock.log_mean    
            # variance = np.var(weights)
            # stddev = np.std(weights)
            # skewness = skew(weights)
            # kurt = kurtosis(weights)
        for index, stock in enumerate(self.stocks):
            for i in range(index, len(self.stocks)):
                variance += np.cov(stock.log_returns, self.stocks[i].log_returns)[0][0] * stock.weight * weights[i]
        stddev = np.sqrt(variance)
        return expectation, variance, stddev

    # @timer
    def get_weights(self):
        weights = []
        for stock in self.stocks:
            stock.weight = stock.value / self.value
            weights.append(stock.weight)
        return weights

    # @timer
    def get_returns(self):
        weighted_returns = []
        for stock in self.stocks:
            weighted_returns.append(stock.weight * stock.log_returns)
        for returns in weighted_returns:
            portfolio_return = [0*x for x in range(len(self.stocks[0].log_returns))]
            portfolio_return = np.add(portfolio_return, returns)
        return portfolio_return

    # @timer
    def saveas(self, saveas):
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'saves', f'{saveas.lower()}.csv'))
        with open(path, 'w') as file:
            for stock in self.stocks:
                file.write(f'{stock.ticker},{stock.shares},{stock.worth} ') # FIX THIS WRITE WITH STCK OBJECT VARIABLES
        print(f"Saved {self.user}'s portfolio to {saveas}.csv")
    
    # @timer
    def save(self):
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'saves', f'{self.user.lower()}.csv'))
        with open(path, 'w') as file:
            for stock in self.stocks:
                file.write(f'{stock.ticker},{stock.shares},{stock.worth} ')
        print(f"Saved {self.user}'s portfolio to {self.user}.csv")
    
    # @timer
    def load(self, loadfrom):
        self.stocks = []
        self.shares = []
        self.tix = []
        self.value = 0
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), 'saves', f'{loadfrom.lower()}.csv'))
        with open(path) as file:
            loaded = file.read()
            loaded = loaded.strip()
            split = loaded.split(' ')
            for item in split:
                stock = item.split(',')
                print(self.add_stock(stock[0], float(stock[1]), price = None, load = True, worth = float(stock[2])))
        print(f"\nLoaded {loadfrom}.csv to {self.user}'s portfolio")




    #express possible portfolios (r) as a combination of n assets -> group further into sets for rebalancing purposes 
    #organize modules into directories
    #add value at risk and portfolio sharpes
    #add brownian motion
    #something with neural nets?
    #beta weighting -> correlation with mkt returns (use SPY)
    #CAPM
    #optimize with beta maximize return for beta
    #options eventually
    #define the probability of a stock being at or above a certain weight and generate expected returns of an option or stock
    #scale distribution probabilites with skew and kurtosis
    #binomial prob models
    #add modeling


if __name__ == '__main__':


    p = Portfolio('Test')
    p.add_stock('AAPL', 10)
    p.add_stock('AMD', 5)
    print(p.data)
    pass
