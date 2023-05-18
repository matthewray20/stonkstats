#!/usr/bin/env python3

import unittest
from datetime import datetime
from stonkstats.common.events import Split


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


if __name__ == "__main__":
    unittest.main()