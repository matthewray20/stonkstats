#!/usr/bin/env python3

import unittest
from portfolio import Portfolio
from common.asset import Asset
from common.events import Trade, Split
from backends.apis.twelve_data import MyTwelveDataAPI
from backends.apis.alpha_vantage import MyAlphaVantageAPI
from backends.apis.financial_modelling_prep import MyFinancialModellingPrepAPI
from datetime import datetime
import os

class DummyAPI:
    def get_latest_price(self, ticker, desired_currency):
        return 100
    
    def get_exchange_rate(self, convert_from, convert_to):
        return 0.75

    def get_currency_info(self, ticker):
        return 'AUD'
    
    def which_rate(option1, option2):
        return 1.0
    
    def get_historical_prices(self, ticker, start, stop, interval):
        datetimes = [
            datetime(day=1, month=1, year=2023),
            datetime(day=2, month=1, year=2023),
            datetime(day=3, month=1, year=2023),
            datetime(day=4, month=1, year=2023),
            datetime(day=5, month=1, year=2023)]
        prices = [1.5, 2.5, 3.5, 4.5, 5.5]
        return datetimes, prices
    

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        self.save_name = 'test_save_as_pickle.pkl'
        # creating assets
        asset1 = Asset(ticker='TSLA', asset_type='security')
        asset2 = Asset(ticker='AAPL', asset_type='security')
        asset3 = Asset(ticker='BTC', asset_type='crypto')
        # creating and adding events for asset1
        asset1.event_log = [
            Trade(1, 1.1, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Trade(2, 2.2, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Split(3, datetime(day=1, month=1, year=2023)),
            Trade(4, 4.4, datetime(day=2, month=1, year=2023), currency='AUD', trade_type='sell'),
            Trade(5, 5.5, datetime(day=2, month=1, year=2023), currency='AUD', trade_type='buy')
        ]
        # creating and adding events 
        asset2.event_log = [
            Trade(6, 6.6, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Trade(7, 7.7, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy')
        ]
        asset3.event_log = [
            Trade(1, 1.1, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Trade(2, 2.2, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Split(3, datetime(day=1, month=1, year=2023)),
            Trade(6, 6.6, datetime(day=2, month=1, year=2023), currency='AUD', trade_type='buy'),
            Trade(7, 7.7, datetime(day=2, month=1, year=2023), currency='AUD', trade_type='buy')
        ]
        self.portfolio1 = Portfolio()
        self.portfolio1.assets['TSLA'] = asset1
        self.portfolio1.assets['AAPL'] = asset2
        self.portfolio1.assets['BTC'] = asset3
        self.portfolio1.api = DummyAPI()
    
    def tearDown(self):
        if os.path.exists(self.save_name):
            os.remove(self.save_name)
    
    def test_eq(self):
        new_portfolio1 = Portfolio()
        new_portfolio2 = Portfolio()
        self.assertEqual(new_portfolio1, new_portfolio2)
        self.assertNotEqual(new_portfolio1, self.portfolio1)
        new_portfolio3 = Portfolio()
        asset1 = Asset(ticker='TSLA', asset_type='security')
        asset1.event_log = [
            Trade(1, 1.1, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Trade(2, 2.2, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Split(3, datetime(day=1, month=1, year=2023)),
            Trade(4, 4.4, datetime(day=2, month=1, year=2023), currency='AUD', trade_type='sell'),
            Trade(5, 5.5, datetime(day=2, month=1, year=2023), currency='AUD', trade_type='buy')
        ]
        new_portfolio3.assets['TSLA'] = asset1
        self.assertNotEqual(self.portfolio1, new_portfolio3)

    def test_set_default_currency(self):
        self.assertEqual(self.portfolio1.default_currency, 'AUD')
        self.portfolio1.set_default_currency('USD')
        self.assertEqual(self.portfolio1.default_currency, 'USD')

    def test_set_data_date_format(self):
        self.assertEqual(self.portfolio1.date_format, None)
        self.portfolio1.set_data_date_format('%d-%m-%Y')
        self.assertEqual(self.portfolio1.date_format, '%d-%m-%Y')

    def test_set_backend(self):
        api_key_file = 'backends/apis/API_keys.yaml'
        self.assertTrue(isinstance(self.portfolio1.api, DummyAPI))
        self.portfolio1.set_backend(api_key_file, 'financialModellingPrep')
        self.assertTrue(isinstance(self.portfolio1.api, MyFinancialModellingPrepAPI))
        self.portfolio1.set_backend(api_key_file, 'alphaVantage')
        self.assertTrue(isinstance(self.portfolio1.api, MyAlphaVantageAPI))
        self.portfolio1.set_backend(api_key_file, 'twelveData')
        self.assertTrue(isinstance(self.portfolio1.api, MyTwelveDataAPI))
    
    def test_setup_from_config(self):
        self.assertEqual(self.portfolio1.default_currency, 'AUD')
        self.assertEqual(self.portfolio1.date_format, None)
        self.assertTrue(isinstance(self.portfolio1.api, DummyAPI))
        config1 = {'dataConversions': {'dateFormat': '%Y-%m-%d', 'defaultCurrency': 'USD'}, 'api': {'apiBackend': 'twelveData', 'apiKeysFile': 'backends/apis/API_keys.yaml'}}
        self.portfolio1.setup_from_config(config1)
        self.assertEqual(self.portfolio1.default_currency, 'USD')
        self.assertEqual(self.portfolio1.date_format, '%Y-%m-%d')
        self.assertTrue(isinstance(self.portfolio1.api, MyTwelveDataAPI))
        config2 = {'dataConversions': {'defaultCurrency': 'AUD'}, 'api': {'apiBackend': 'alphaVantage', 'apiKeysFile': 'backends/apis/API_keys.yaml'}}
        self.portfolio1.setup_from_config(config2)
        self.assertEqual(self.portfolio1.default_currency, 'AUD')
        self.assertEqual(self.portfolio1.date_format, '%Y-%m-%d')
        self.assertTrue(isinstance(self.portfolio1.api, MyAlphaVantageAPI))

    def test_num_assets(self):
        self.assertEqual(self.portfolio1.num_assets(), 3)

    def test_merge_portfolio(self):
        pass

    def test_save_as_pickle(self):
        self.assertFalse(os.path.exists(self.save_name))
        self.portfolio1.save_as_pickle(self.save_name)
        self.assertTrue(os.path.exists(self.save_name))

    def test_add_from_pickle(self):
        self.portfolio1.save_as_pickle(self.save_name)
        self.assertTrue(os.path.exists(self.save_name))
        new_portfolio = Portfolio()
        new_portfolio.add_from_pickle(self.save_name)
        self.assertTrue(self.portfolio1 == new_portfolio)
        self.portfolio1.merge_portfolio(new_portfolio)
        self.assertTrue(self.portfolio1 == new_portfolio)
    
    def test_remove_asset(self):
        self.assertTrue('AAPL' in self.portfolio1.assets)
        self.portfolio1.remove_asset('AAPL')
        self.assertFalse('AAPL' in self.portfolio1.assets)
        self.assertRaises(KeyError, self.portfolio1.remove_asset, ticker='MSFT')

    def test_remove_asset_ith_event(self):
        event_to_remove = self.portfolio1.assets['TSLA'].event_log[2]
        self.assertTrue(event_to_remove in self.portfolio1.assets['TSLA'].event_log)
        self.portfolio1.remove_asset_ith_event('TSLA', 2)
        self.assertFalse(event_to_remove in self.portfolio1.assets['TSLA'].event_log)
        self.assertRaises(IndexError, self.portfolio1.remove_asset_ith_event, ticker='TSLA', i=-10)
        self.assertRaises(IndexError, self.portfolio1.remove_asset_ith_event, ticker='TSLA', i=12)

    def test_add_new_asset(self):
        self.portfolio1.add_new_asset('MSFT', 'security')
        self.assertTrue('MSFT' in self.portfolio1.assets.keys())

    def test_add_existing_asset(self):
        new_asset1 = Asset('MSFT', 'security')
        self.assertFalse(new_asset1 in self.portfolio1.assets.values())
        self.portfolio1.add_existing_asset(new_asset1)
        self.assertTrue(new_asset1 in self.portfolio1.assets.values())

    def test_add_asset_event(self):
        pass

    def test_add_from_csv(self):
        pass

    def test_get_latest_prices(self):
        self.assertEqual(self.portfolio1.assets['TSLA'].current_price, None)
        self.assertEqual(self.portfolio1.assets['AAPL'].current_price, None)
        self.assertEqual(self.portfolio1.assets['BTC'].current_price, None)
        self.portfolio1.get_latest_prices('AUD')
        self.assertEqual(self.portfolio1.assets['TSLA'].current_price, 100)
        self.assertEqual(self.portfolio1.assets['AAPL'].current_price, 100)
        self.assertEqual(self.portfolio1.assets['BTC'].current_price, 100)

    def test_get_historical_prices(self):
        pass

    def test_plot_historical(self):
        pass


    def test_as_table(self):
        pass

    def test_quickstats(self):
        pass

    def test_show_dashboard(self):
        self.assertRaises(NotImplementedError, self.portfolio1.show_dashboard)




if __name__ == "__main__":
    unittest.main()