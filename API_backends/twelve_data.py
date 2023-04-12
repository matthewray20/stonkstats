 #!/usr/bin/env python3

from API_backends.default_api import DefaultAPI
from twelvedata import TDClient

# TODO: move error handling to default API. Maybe use @error_capture to wrap methods
class MyTwelveDataAPI(DefaultAPI):
    def __init__(self, api_key):
        super().__init__()
        self.max_requests_per_min = 8
        self.td = TDClient(apikey=api_key)
    
    def get_latest_price(self, asset, desired_currency):
        try:
            if asset.asset_type == 'crypto': return float(self.td.price(symbol=f'{asset.ticker}/{desired_currency}').as_json()['price'])
            # detirmine what currency is returned in
            currency = self.td.eod(symbol=asset.ticker).as_json()['currency']
            rate = 1 if currency == desired_currency else self.get_exchange_rate(currency, desired_currency)
            return float(self.td.price(symbol=asset.ticker).as_json()['price']) * rate
        except Exception as e:
            print(f'###### ERROR getting latest price for {asset.ticker} (type {asset.asset_type})')
            print(e)
            return 0

    def get_exchange_rate(self, convert_from, convert_to):
        try:
            currencies = f'{convert_from}/{convert_to}'
            if currencies in self.exchange_rate_cache: return self.exchange_rate_cache[currencies]
            rate = self.td.exchange_rate(symbol=currencies).as_json()['rate']
            self.exchange_rate_cache[currencies] = rate
            return rate
        except Exception as e:
            print(f'###### ERROR getting exchange rate from {convert_from} to {convert_to}')
            print(e)
            return 1


    def get_historical_prices(self, start_date, end_date, desired_currency, interval='1d', *args):
        # TODO: add currency option here
        try:
            return self.td.time_series(
                symbol=','.join(args), 
                start_date=start, 
                end_date=end, 
                interval=interval).as_json()
        except Exception as e:
            print(f'###### ERROR getting historical prices for {len(assets)} assets(s)')
            print(e)
            return 0
    

        