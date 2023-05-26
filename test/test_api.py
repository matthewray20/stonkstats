#!/usr/bin/env python3

import unittest
import json
import yaml
from common.asset import Asset
from backends.apis.twelve_data import MyTwelveDataAPI
from backends.apis.financial_modelling_prep import MyFinancialModellingPrepAPI
from backends.apis.alpha_vantage import MyAlphaVantageAPI


def build_api(api_name):
    with open('backends/apis/API_keys.yaml', 'rb') as f:
        api_keys = yaml.load(f, Loader=yaml.FullLoader)
    api_key = api_keys[api_name]
    if api_name == 'alphaVantage': return MyAlphaVantageAPI(api_key)
    elif api_name == 'twelveData': return MyTwelveDataAPI(api_key)
    elif api_name == 'financialModellingPrep': return MyFinancialModellingPrepAPI(api_key)



class BaseTestCases:
    class BaseTest(unittest.TestCase):
        def setUp(self):
            self.specific_set_up()
            self.api = build_api(self.api_name)
            self.asset1 = Asset('TSLA', 'security')
            self.asset1.asset_api_currency = 'USD'
            self.asset2 = Asset('BTC', 'crypto')
            self.asset2.asset_api_currency = 'AUD'

        def test_get_latest_price(self):
            price1 = self.api.get_latest_price(self.asset1, 'AUD')
            price2 = self.api.get_latest_price(self.asset2, 'AUD')
            self.assertTrue(isinstance(price1, float))
            self.assertTrue(isinstance(price2, float))

        def test_get_exchange_rate(self):
            rate1 = self.api.get_exchange_rate('AUD', 'USD')
            self.assertTrue(isinstance(rate1, float))
            self.assertGreater(1, rate1)

        def test_get_historical_prices(self):
            dates, prices = self.api.get_historical_prices(self.asset1, '2023-01-01', '2023-03-03', 'AUD', 'daily')
            self.assertTrue(isinstance(prices[0], float))

        def get_currency_info(self):
            currency = self.api.get_currency_info('TSLA')
            self.assertTrue(isinstance(currency, str))
            self.assertTrue(currency == 'USD')

        def test_which_rate(self):
            rate1 = self.api.which_rate('AUD', 'AUD')
            self.assertTrue(isinstance(rate1, int))
            self.assertTrue(rate1 == 1)
            rate2 = self.api.which_rate('AUD', 'USD')
            self.assertTrue(isinstance(rate2, float))
            self.assertGreater(1, rate2)
            

"""
class TestAlphaVantage(BaseTestCases.BaseTest):
    def specific_set_up(self):
        self.api_name = 'alphaVantage'
 

class TestTwelveData(BaseTestCases.BaseTest):
    def specific_set_up(self):
        self.api_name = 'twelveData'
    
"""
class TestFinancialModellingPrep(BaseTestCases.BaseTest):
    def specific_set_up(self):
        self.api_name = 'financialModellingPrep'


if __name__ == "__main__":
    unittest.main()