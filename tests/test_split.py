#!/usr/bin/env python3

import unittest
from common.events import Split
from datetime import datetime


class TestSplit(unittest.TestCase):
    def setUp(self):
        self.split1 = Split(
            ratio=3,
            date = datetime(day=22, month=11, year=2023))
        
        self.split2 = Split(
            ratio=3,
            date = datetime(day=22, month=11, year=2023))

        self.split3 = Split(
            ratio=5,
            date = datetime(day=22, month=11, year=2023))


    def test_eq(self):
        self.assertEqual(self.split1, self.split2)
        self.assertNotEqual(self.split1, self.split3)

    def test_repr(self):
        self.assertEqual(str(self.split1), 'Split(ratio=3, date=date=2023-11-22 00:00:00)')
        self.assertEqual(str(self.split3), 'Split(ratio=5, date=date=2023-11-22 00:00:00)')




if __name__ == "__main__":
    unittest.main()