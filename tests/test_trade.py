#!/usr/bin/env python3

import unittest
from common.events import Trade
from datetime import datetime


class TestTrade(unittest.TestCase):
    def setUp(self):
        self.trade1 = Trade(
            quantity=12, 
            price=123.45, 
            date=datetime(day=22, month=11, year=2023), 
            currency='AUD', 
            trade_type='buy')
        
        self.trade2 = Trade(
            quantity=12, 
            price=123.45, 
            date=datetime(day=22, month=11, year=2023), 
            currency='AUD', 
            trade_type='buy')
        
        self.trade3 = Trade(
            quantity=12, 
            price=123.45, 
            date=datetime(day=22, month=11, year=2023), 
            currency='AUD', 
            trade_type='sell')

    def test_eq(self):
        self.assertEqual(self.trade1, self.trade2)
        self.assertNotEqual(self.trade1, self.trade3)


if __name__ == "__main__":
    unittest.main()