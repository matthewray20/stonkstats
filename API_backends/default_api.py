#!/usr/bin/env python3

import yaml

class DefaultAPI:
    def __init__(self, api_key_file):
        with open(api_key_file) as f:
            keys = yaml.load(f, Loader=yaml.FullLoader)
            self.api_key = keys[f'{self.__class__.__name__}']

    def get_latest_price(self, ticker, asset_type):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_latest_price()')
    
    def get_exchange_rate(self, convert_from, covert_to):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_exchange_rate()')
    
    def get_historical_prices(self, start_date, end_date, *args):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_hsitorical_prices()')