#!/usr/bin/env python3

import unittest
from datetime import datetime
from common.asset import Asset
from common.events import Trade, Split


class TestAsset(unittest.TestCase):
    def setUp(self):
        # creating assets
        self.asset1 = Asset(ticker='TSLA', asset_type='security')
        self.asset2 = Asset(ticker='TSLA', asset_type='security')
        self.asset3 = Asset(ticker='BTC', asset_type='crypto')
        # creating and adding events for asset1
        self.asset1.event_log = [
            Trade(1, 1.1, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Trade(2, 2.2, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Split(3, datetime(day=1, month=1, year=2023)),
            Trade(4, 4.4, datetime(day=2, month=1, year=2023), currency='AUD', trade_type='sell'),
            Trade(5, 5.5, datetime(day=2, month=1, year=2023), currency='AUD', trade_type='buy')
        ]
        # creating and adding events 
        self.asset2.event_log = [
            Trade(6, 6.6, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy'),
            Trade(7, 7.7, datetime(day=1, month=1, year=2023), currency='AUD', trade_type='buy')
        ]

    def test_add_event(self):
        # testing adding buy, sell, split, buy
        self.assertEqual(self.asset3.event_log, None)
        new_event1 = Trade(1, 12.34, datetime(day=1, month=2, year=2023), currency='AUD', trade_type='buy')
        self.asset3.add_event(new_event1)
        self.assertEqual(len(self.asset3.event_log), 1)
        # testing split added in correct order
        new_event2 = Split(2, datetime(day=2, month=2, year=2023))
        self.asset3.add_event(new_event2)
        self.assertEqual(len(self.asset3.event_log), 2)
        new_event3 = Trade(3, 23.45, datetime(day=2, month=2, year=2023), currency='AUD', trade_type='sell')
        self.asset3.add_event(new_event3)
        self.assertEqual(len(self.asset3.event_log), 3)
        new_event4 = Trade(4, 34.56, datetime(day=3, month=2, year=2023), currency='AUD', trade_type='buy')
        self.asset3.add_event(new_event4)
        self.assertEqual(len(self.asset3.event_log), 4)
        # testing with duplicates & allow_duplicates=False
        new_event5 = Trade(4, 34.56, datetime(day=3, month=2, year=2023), currency='AUD', trade_type='buy')
        self.asset3.add_event(new_event5, allow_duplicates=False)
        self.assertEqual(len(self.asset3.event_log), 4)
        # testing with duplicates & allow_duplicates=True
        new_event6 = Trade(4, 34.56, datetime(day=3, month=2, year=2023), currency='AUD', trade_type='buy')
        self.asset3.add_event(new_event6, allow_duplicates=True)
        self.assertEqual(len(self.asset3.event_log), 5)
        # testing added in correct order
        self.assertTrue(isinstance(self.asset3.event_log[0], Trade))
        self.assertEqual(self.asset3.event_log[0].quantity, 1)
        self.assertTrue(isinstance(self.asset3.event_log[1], Trade))
        self.assertEqual(self.asset3.event_log[1].quantity, 3)
        self.assertTrue(isinstance(self.asset3.event_log[2], Split))
        self.assertEqual(self.asset3.event_log[2].ratio, 2)
        self.assertTrue(isinstance(self.asset3.event_log[3], Trade))
        self.assertEqual(self.asset3.event_log[3].quantity, 4)
        self.assertTrue(isinstance(self.asset3.event_log[4], Trade))
        self.assertEqual(self.asset3.event_log[4].quantity, 4)
    
    def test_eq(self):
        asset4 = Asset('TSLA', 'security')
        asset4.set_api_currency('AUD')
        asset4.set_current_price(100)
        asset5 = Asset('TSLA', 'security')
        asset5.set_api_currency('USD')
        asset5.set_current_price(200)
        self.assertEqual(asset4, asset5)
        self.assertNotEqual(self.asset1, self.asset3)
    
    def test_remove_ith_event(self):
        event_i = 2
        remove_event = self.asset1.event_log[event_i] # Should be the Split
        self.assertEqual(len(self.asset1.event_log), 5)
        self.asset1.remove_ith_event(event_i)
        self.assertEqual(len(self.asset1.event_log), 4)
        self.assertTrue(remove_event not in self.asset1.event_log)
        event_i_2 = -15
        self.assertRaises(IndexError, self.asset1.remove_ith_event, event_i_2)
        event_i_3 = 7
        self.assertRaises(IndexError, self.asset1.remove_ith_event, event_i_3)

    def test_update_cash_balance(self):
        self.assertEqual(self.asset1.cash, 0)
        self.asset1.update_cash_balance()
        self.assertAlmostEqual(self.asset1.cash, -15.4)

    def test_set_api_currency(self):
        self.assertEqual(self.asset1.asset_api_currency, None)
        self.asset1.set_api_currency('AUD')
        self.assertEqual(self.asset1.asset_api_currency, 'AUD')
    
    def test_set_current_price(self):
        self.assertEqual(self.asset1.current_price, None)
        self.asset1.set_current_price(300.20)
        self.assertEqual(self.asset1.current_price, 300.20)

    def test_reset_cash_balance(self):
        self.asset1.cash = 45327.21
        self.assertEqual(self.asset1.cash, 45327.21)
        self.asset1.reset_cash_balance()
        self.assertEqual(self.asset1.cash, 0)
    
    def test_is_crypto(self):
        self.assertFalse(self.asset1.is_crypto())
        self.assertTrue(self.asset3.is_crypto())

    def test_quantity_held(self):
        self.assertEqual(self.asset1.quantity_held(), 10)

    def test_ammount_invested(self):
        self.assertAlmostEqual(self.asset1.ammount_invested(), 15.4)
    
    def test_merge_in(self):
        # update self.asset1 values to merge into self.asset2
        self.asset1.asset_api_currency = 'USD'
        self.asset1.current_price = 100
        # testing values in default configuration
        self.assertEqual(self.asset2.asset_api_currency, None)
        self.assertEqual(self.asset2.current_price, None)
        # merge assets
        self.asset2.merge_asset(self.asset1)
        # testing length
        self.assertEqual(len(self.asset2.event_log), 7)
        # testing merged in values
        self.assertEqual(self.asset2.asset_api_currency, 'USD')
        self.assertEqual(self.asset2.current_price, 100)
        # testing order
        self.assertTrue(isinstance(self.asset2.event_log[0], Trade))
        self.assertEqual(self.asset2.event_log[0].price, 6.6)
        self.assertTrue(isinstance(self.asset2.event_log[1], Trade))
        self.assertEqual(self.asset2.event_log[1].price, 7.7)
        self.assertTrue(isinstance(self.asset2.event_log[2], Trade))
        self.assertEqual(self.asset2.event_log[2].price, 1.1)
        self.assertTrue(isinstance(self.asset2.event_log[3], Trade))
        self.assertEqual(self.asset2.event_log[3].price, 2.2)
        
        self.assertTrue(isinstance(self.asset2.event_log[4], Split))
        self.assertEqual(self.asset2.event_log[4].ratio, 3)

        self.assertTrue(isinstance(self.asset2.event_log[5], Trade))
        self.assertEqual(self.asset2.event_log[5].price, 4.4)


        self.assertTrue(isinstance(self.asset2.event_log[6], Trade))
        self.assertEqual(self.asset2.event_log[6].price, 5.5)
        # testing ammounts
        self.assertAlmostEqual(self.asset2.ammount_invested(), 108.9)
        self.assertEqual(self.asset2.quantity_held(), 49.0)
    
    

if __name__ == "__main__":
    unittest.main()