 #!/usr/bin/env python3

from API_backends.default_api import DefaultAPI
from twelvedata import TDClient


class MyTwelveDataAPI(DefaultAPI):
    def __init__(self, api_key_file):
        super().__init__(api_key_file)
        self.td = TDClient(apikey=self.api_key)
    
    def get_latest_price(self, asset):
        # TODO: somehow have this auto convert to default currency since no way to specify currency
        if asset.asset_type == 'crypto':
            pass
        return float(self.td.price(symbol=ticker).as_json()['price'])

    def get_exchange_rate(self, convert_from, covert_to):
        return self.td.exchange_rate(symbol=f'{convert_from}/{convert_to}').as_json()['rate']

    def get_historical_prices(self, start_date, end_date, interval='1d', *args):
        # TODO: add currency option here
        return self.td.time_series(
            symbol=','.join(args), 
            start_date=start, 
            end_date=end, 
            interval=interval).as_json()
    

        