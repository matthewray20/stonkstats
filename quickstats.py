#!/usr/bin/env python3

import pandas as pd
from twelvedata import TDClient
from matplotlib import pyplot as plt



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
