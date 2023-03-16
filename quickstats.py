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
        self.event_log = None
        self.current_price = None

    def add_event(self, event):
        if self.event_log is None:
            assert not isinstance(event, Split), f"First event for ticker={self.ticker} can NOT be type=Split"
            self.event_log = [event]
        else:
            # Insert events in date order
            # Splits will always be put last -> their date is after market close so after trades that day
            for i, logged_event in enumerte(self.event_log):
                if (new_event.date < logged_event.date) or (new_event.date == logged_event.date and isinstance(logged_event, Split) and isinstance(new_event, Trade)):
                    self.event_log.insert(i, new_event)
                    return
            self.event_log.append(new_event)

    
    def quantity_held(self):
        total = 0
        for trade in self.event_log:
            if isinstance(trade, Buy):
                total += trade.quantity
            elif isinstance(trade, Sell):
                total -= trade.quantity
            elif isinstance(trade, Split):
                total *= trade.ratio
            else:
                raise TypeError(f"Unrecognised trade of type {type(trade)} from {trade}")
        
    def ammount_invested(self):
        total = 0
        

    
    def __repr__(self):
        return f'Ticker({self.ticker}): {len(self.event_log)} events, {self.quantity_held()} current shares'
    
    def __str__(self):
        return f"""
        ===== {self.ticker} =====
        {event for event in self.event_log}
        ================"""



class Dashboard:
    def __init__(self):
        self.tickers = {}
        self.apikey = open('apikey.txt', 'r').read().strip()
    
    def from_df(self, df):
        pass
    
    def add_ticker(self, tic):
        self.tickers[tick.ticker] = tick
    
    def update_recent_price(self):
        for ticker in self.tickers:

    
    def __repr__(self):
        return f'Dashboard(): {len(self.tickers)} tickers'
    
    def __str__(self):
        return f"""
        ===== Dashboard =====
        {self.tickers[ticker] for ticker in self.tickers.keys()}
        ====================="""
    
    def stats(self):
        pass # print out relevant info
    
    def render(self):
        pass
        # TODO: GUI
        # call it show()? 



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
