#!/usr/bin/env python3

from events import Split

# TODO: add cash position
# TODO: implement deposists and selling

class Asset:
    def __init__(self, ticker, asset_type):
        self.ticker = ticker
        self.asset_type = asset_type
        self.asset_api_currency = None
        self.event_log = None
        self.current_price = None
        self.cash = 0
    
    def set_api_currency(self, currency):
        self.asset_api_currency = currency
    
    def set_current_price(self, new_price):
        self.current_price = new_price
    
    def __eq__(self, other):
        checks = [
            self.ticker == other.ticker,
            self.asset_type == other.asset_type]
        return all(checks)
        
    def merge_asset(self, other):
        if self.asset_api_currency is None and other.asset_api_currency is not None: self.asset_api_currency = other.asset_api_currency
        if self.current_price is None and other.current_price is not None: self.current_price = other.current_price
        if self.event_log is None and other.event_log is None: return
        if self.event_log is None and other.event_log is not None: self.event_log = other.event_log
        for other_event in other.event_log:
            self.add_event(other_event, allow_duplicates=False)

    #def add_event(self, date, quantity, currency, event_type, price, allow_duplicates=False):
    def add_event(self, new_event, allow_duplicates=True):
        # insert event
        if self.event_log is None:
            assert not isinstance(new_event, Split), f"First trade for ticker={self.ticker} can not be type=Split"
            self.event_log = [new_event]
        elif not allow_duplicates and new_event in self.event_log:
            return
        else:
            # Splits will always be put last -> their date is after market close so after trades that day
            for i, logged_event in enumerate(self.event_log):
                if (new_event.date < logged_event.date) or (new_event.date == logged_event.date and isinstance(logged_event, Split) and isinstance(new_event, Trade)):
                    self.event_log.insert(i, new_event)
                    return
            self.event_log.append(new_event)
    
    def is_crypto(self):
        return self.asset_type == 'crypto'
    
    def reset_cash_balance(self):
        self.cash = 0

    def quantity_held(self):
        total = 0
        for event in self.event_log:
            if isinstance(event, Trade) and event.trade_type == 'buy': total += event.quantity
            elif isinstance(event, Trade) and event.trade_type == 'sell': total -= event.quantity
            elif isinstance(event, Split): total *= event.ratio
            #elif isinstance(event, Cash) and event.cash_type == 'deposit': total += event.quantity
            #elif isinstance(event, Cash) and event.cash_type == 'withdrawl': total -= event.quantity
            else: raise TypeError(f"Unrecognised trade of type {type(event)} from {event.__repr__()}")
        return total
        
    def ammount_invested(self):
        total = 0
        for event in self.event_log:
            if isinstance(event, Trade) and event.trade_type == 'buy': total += (event.quantity * event.price) # + event.commision
        return total
    
    def __repr__(self):
        return f'Asset({self.ticker}): {len(self.event_log)} events, {self.quantity_held()} current shares'

