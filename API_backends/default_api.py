#!/usr/bin/env python3

class DefaultAPI:
    def __init__(self):
        self.exchange_rate_cache = {}

    def get_latest_price(self, asset, desired_currency):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_latest_price()')
    
    def get_exchange_rate(self, convert_from, convert_to):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_exchange_rate()')
    
    def get_historical_prices(self, start_date, end_date, *args):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_hsitorical_prices()')