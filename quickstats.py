#!/usr/bin/env python3

import pandas as pd
from twelvedata import TDClient
from matplotlib import pyplot as plt

class Split:
    def __init__(self, ratio, date):
        self.ratio = ratio
        self.date = date
    
    def __str__(self):
        return f"""
        ===== Split =====
        Ratio: {self.ratio}
        Date: {self.date}
        ================="""
    
    def __repr__(self):
        return f'Split(ratio={self.ratio}, date={self.date})'


class Trade:
    def __init__(self, quantity, price, trade_type, date, currency):
        self.quantity = quantity
        self.price = price
        self.trade_type = trade_type
        self.date = date
        self.currency = currency

    def __str__(self):
        return f"""
        ===== Trade =====
        Type: {self.trade_type}
        Quantity: {self.quantity}
        Price: {self.price}
        Date: {self.date}
        Currency: {self.currency}
        ================="""
    
    def __repr__(self):
        return f'Trade(quantity={self.quantity}, price={self.price}, type={self.trade_type}, date={self.date}, currency={self.currency})'


class Ticker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.trade_log = None
        self.current_price = None

    def add_trade(self, trade):
        if self.trade_log is None:
            assert not isinstance(trade, Split), f"First trade for ticker={self.ticker} can NOT be type=Split"
            self.trade_log = [trade]
        else:
            # Insert trades in date order
            # Splits will always be put last -> their date is after market close so after trades that day
            for i, logged_trade in enumerte(self.trade_log):
                if (new_trade.date < logged_trade.date) or (new_trade.date == logged_trade.date and isinstance(logged_trade, Split) and isinstance(new_trade, Trade)):
                    self.trade_log.insert(i, new_trade)
                    return
            self.trade_log.append(new_trade)

    
    def quantity_held(self):
        total = 0
        for trade in self.trade_log:
            if not isinstance(trade, Split) and trade.trade_type == "Buy": total += trade.quantity
            else:
                raise TypeError(f"Unrecognised trade of type {type(trade)} from {trade}")
        return total
        
    def ammount_invested(self):
        total = 0
        for trade in self.trade_log:
            if not isinstance(trade, Split) and trade.trade_type == "Buy": total += (trade.quantity * trade.price)
        return total

    def total_value(self):
        total = 0
        for trade in self.trade_log:
            if not isinstance(trade, Split) and trade.trade_type == "Buy": total += (trade.quantity * self.current_price)
        return total

    def profit(self):
        return self.total_value() - self.ammount_invested()
    
    def avg_price_per_share(self):
        return self.ammount_invested() / self.quantity_held()
    
    def __repr__(self):
        return f'Ticker({self.ticker}): {len(self.trade_log)} trades, {self.quantity_held()} current shares'
    
    def __str__(self):
        return f"""
        ===== {self.ticker} =====
        {trade for trade in self.trade_log}
        ================"""



class Dashboard:
    def __init__(self):
        self.tickers = {}
        td = TDClient(apikey=open('API_key.txt', 'r').read().strip())
    
    def from_df(self, df):
        pass
    
    def add_ticker(self, tic):
        self.tickers[tick.ticker] = tick
    
    def update_recent_price(self):
        for ticker in self.tickers:
            p = self.td.price(symbol=ticker).as_json()
            self.tickers[ticker].current_price = float(p['price'])
    
    def historical(self, start, stop, num_points):
        pass
            
    
    def __repr__(self):
        return f'Dashboard(): {len(self.tickers)} tickers'
    
    def __str__(self):
        return f"""
        ===== Dashboard =====
        {self.tickers[ticker] for ticker in self.tickers.keys()}
        ====================="""
    
    def stats(self, currency='USD'):
        rates = {}
        if currency != "USD":
            rate = self.td.exchange_rate(symbol=f"{currency}/USD").as_json()['rate']

        print('======= Quickstats =======')
        print('Stock | Net Worth | Profit')
        print('--------------------------')
        for ticker in self.tickers:
            print(f'{ticker:6}{ticker.total_value():12.2f}{ticker.profit():6.2f}')
            print(print('--------------------------'))
    
    def render(self):
        pass
        # TODO: GUI
        # call it show()? 


if __name__ == "__main__":
    db = Dashboard()
    df = pd.read_csv('sharedata.csv')
    db.from_df(df)
    print(db)



df = pd.read_csv('sharedata.csv')
print(df)
ex = float(input('exchange rate: '))
worth_dict, net_dict = {}, {}

for ticker in set(df['ticker']):
    if type(ticker) != str:
        continue
    current_price = float(input(f"current price of {ticker}: "))
    trades = df[(df['ticker']==ticker) & (df['Type'] == 'Purchase')]
    investedTotal = trades['quantity'] * trades['share_price'] + trades['commission']
    avgPrice = investedTotal.sum()/trades["quantity"].sum()
    print(f'\tAvg Price {ticker}: {round(avgPrice, 2)} | no. shares: {trades["quantity"].sum()}')
    curTotal = trades['quantity'] * current_price
    worth_dict[ticker] = sum(curTotal)
    net_dict[ticker] = sum(curTotal - investedTotal)

totalWorth = sum(list(worth_dict.values()))
totalProfit = sum(list(net_dict.values()))
divStr = '-'* 56
tickStr = "|{:>7}|{:>11}|{:>11}|{:>11}|{:>11}"

print()
print(divStr)
print(tickStr.format("tick", "USD Value", "AUD Value", "USD Profit", "AUD Profit"))
for key in worth_dict:
    print(divStr)
    print(tickStr.format(key, round(worth_dict[key],2), round(worth_dict[key]/ex,2), round(net_dict[key],2), round(net_dict[key]/ex,2)))
print(divStr)
print(tickStr.format("TOTAL", round(totalWorth,2), round(totalWorth/ex,2), round(totalProfit,2), round(totalProfit/ex,2)))
print()


# TODO: refactor to single loop
