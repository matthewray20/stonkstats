#!/usr/bin/env python3

import unittest
import json
from backends.apis.twelve_data import MyTwelveDataAPI
from backends.apis.financial_modelling_prep import MyFinancialModellingPrepAPI
from backends.apis.alpha_vantage import MyAlphaVantageAPI


class TestAPI:
    pass





class TestAlphaVantage(TestAPI, unittest.TestCase):
    def setUp(self):
        with open('backends/apis/API_keys.yaml', 'rb') as f:
            api_keys = yaml.load(f, Loader=yaml.FullLoader)
        api_key = api_keys['alphaVantage']
        self.api = MyAlphaVantageAPI(api_key)

class TestTwelveData(TestAPI, unittest.TestCase):
    def setUp(self):
        with open('backends/apis/API_keys.yaml', 'rb') as f:
            api_keys = yaml.load(f, Loader=yaml.FullLoader)
        api_key = api_keys['twelveData']
        self.api = MyAlphaVantageAPI(api_key)

class TestFinancialModellingPrep(TestAPI, unittest.TestCase):
    def setUp(self):
        with open('backends/apis/API_keys.yaml', 'rb') as f:
            api_keys = yaml.load(f, Loader=yaml.FullLoader)
        api_key = api_keys['financialModellingPrep']
        self.api = MyAlphaVantageAPI(api_key)


if __name__ == "__main__":
    unittest.main()