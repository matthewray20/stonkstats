#!/usr/bin/env python3

class Split:
    def __init__(self, ratio, date):
        self.ratio = ratio
        self.date = date
    
    def __eq__(self, other):
        if not isinstance(other, Split): return False
        checks = [
            self.ratio == other.ratio,
            self.date == other.date]
        return all(checks)
    
    def __repr__(self):
        return f'Split(ratio={self.ratio}, date={self.date})'


class Trade:
    def __init__(self, quantity, price, date, currency, trade_type):
        self.quantity = quantity
        self.price = price
        self.date = date
        self.currency = currency
        self.trade_type = trade_type
    
    def __eq__(self, other):
        if not isinstance(other, Trade): return False
        checks = [
            self.quantity == other.quantity,
            self.price == other.price,
            self.date == other.date,
            self.currency == other.currency,
            self.trade_type == other.trade_type]
        return all(checks)

    def __repr__(self):
        name = self.trade_type
        new_name = name[0].upper() + name[1:]
        return f'{new_name}(quantity={self.quantity}, price={self.price}, date={self.date}, currency={self.currency})'

