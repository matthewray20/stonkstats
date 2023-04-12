 #!/usr/bin/env python3

from API_backends.default_api import DefaultAPI
import requests
import json

# This uses the alphavantage API
# https://www.alphavantage.co/documentation/

class MyAlphaVantageAPI(DefaultAPI):
    def __init__(self, api_key):
        super().__init__()
        self.max_requests_per_min = 5
        self.base_url = 'https://www.alphavantage.co/query?'
        self.api_key = api_key

    def get_latest_price(self, asset, desired_currency):
        # if crypto use same api call as exchange rate
        if asset.asset_type == 'crypto': return self.get_exchange_rate(asset.ticker, desired_currency)
        # get request price and currency info
        price_resp = requests.get(self.base_url + f'function=GLOBAL_QUOTE&symbol={asset.ticker}&apikey={self.api_key}')
        currency_resp = requests.get(self.base_url + f'function=OVERVIEW&symbol={asset.ticker}&apikey={self.api_key}')
        # error check responses
        if self.check_for_error(price_resp, 'price', asset.ticker) or self.check_for_error(currency_resp, 'currency_info', asset.ticker): return 0
        # get price and currency data, 
        price = float(json.loads(price_resp.text)['Global Quote']['05. price'])
        currency = json.loads(currency_resp.text)['Currency']
        rate = 1 if currency == desired_currency else self.get_exchange_rate(currency, desired_currency)
        return price * rate


    def get_exchange_rate(self, convert_from, convert_to):
        # TODO: add crypto argument? allow to return 0 to match securities
        # TODO: should be if error getting data, show 'n/a' or 'error' in table
        exchange_string = f'{convert_from}/{convert_to}'
        # return cached rate if possible
        if exchange_string in self.exchange_rate_cache: return self.exchange_rate_cache[exchange_string]
        # API call and error check
        resp = requests.get(self.base_url + f'function=CURRENCY_EXCHANGE_RATE&from_currency={convert_from}&to_currency={convert_to}&apikey={self.api_key}')
        if self.check_for_error(resp, 'exchange_rate', convert_from, convert_to): return 1
        # get to exchange rate and return it
        data = json.loads(resp.text)
        rate = float(data['Realtime Currency Exchange Rate']['5. Exchange Rate'])
        self.exchange_rate_cache[exchange_string] = rate
        return rate
    
    def get_historical_prices(self, start_date, end_date, interval='1d', *args):
        return 0
    
    def check_for_error(self, resp, action, *args):
        error = False
        if resp.status_code != requests.codes.ok:
            error = True
        data = json.loads(resp.text)
        if 'Error Message' in data.keys() or 'Note' in data.keys():
            error = True
        if error: 
            self.print_error_message(action, *args)
            print(f'got status code:{resp.status_code} - \n{resp.text}')
        return error

    
    
    
    