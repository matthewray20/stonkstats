 #!/usr/bin/env python3

from API_backends.default_api import DefaultAPI

class MyAlphaVantageAPI(DefaultAPI):
    def __init__(self, api_key_file):
        super().__init__()

    def get_latest_price(self, asset):
        pass
    
    def get_exchange_rate(self, convert_from, convert_to):
        pass
    
    def get_historical_prices(self, start_date, end_date, interval='1d', *args):
        pass