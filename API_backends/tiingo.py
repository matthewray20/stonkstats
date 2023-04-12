#!/usr/bin/env python3

from API_backends.default_api import DefaultAPI
import requests 

class MyTiingoAPI:
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.base_url = 'https://api.tiingo.com/tiingo/'
        self.headers = {'Content-Type': 'application/json'}

    def get_latest_price(self, asset):
        if asset.asset_type == 'crypto': extra_url = f'crypto/prices?tickers={asset.ticker}{desired_currency}'
        else: extra_url = f'daily/{asset.ticker}/prices'
        response = requests.get(self.base_url + extra_url + f'?token={self.api_key}', headers=self.headers)
        if response.status_code != requests.codes.ok:
            print(f'###### ERROR getting latest price for {asset.ticker} (type {asset.asset_type})')
            print(f'got status code:{response.status_code} - {response.text}')
            return 1
        return float(response[0]['adjClose'])

    def get_exchange_rate(self, convert_from, convert_to):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_exchange_rate()')
    
    def get_historical_prices(self, start_date, end_date, *args):
        raise NotImplementedError(f'Class <{self.__class__.__name__}> has not implemented get_hsitorical_prices()')