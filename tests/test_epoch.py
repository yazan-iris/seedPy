import unittest
from datetime import datetime

from timeseries import Epoch


class TestEpoch(unittest.TestCase):

    def test_epoch(self):

        e1 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=11),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=12))

        e2 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=13),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=14))
        self.assertTrue(e1 < e2)

        e2 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=12),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=13))
        self.assertTrue(e1 < e2)
        self.assertTrue(e1 <= e2)

        e2 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=10),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=13))
        self.assertFalse(e1 < e2)
        self.assertFalse(e1 <= e2)

        e2 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=8),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=9))
        self.assertTrue(e1 > e2)
        self.assertTrue(e1 >= e2)

        e1 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=11),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=14))
        e2 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=8),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=13))
        self.assertTrue(e1.overlap(e2))

        e1 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=11),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=14))
        e2 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=14),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=16))
        self.assertTrue(e1.overlap(e2))

        e1 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=11),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=14))
        e2 = Epoch(start_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=15),
                   end_time=datetime(year=2010, month=7, day=12, hour=11, minute=11, second=16))
        self.assertFalse(e1.overlap(e2))

