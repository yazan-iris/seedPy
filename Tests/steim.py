import unittest

import array

from Codec.Steim import SteimRecord, SteimBucket
from Codec.Steim.buckets import Steim1Bucket


class TestSteim(unittest.TestCase):

    def test_steim_record_is_full(self):
        record = SteimRecord(number_of_frames=10)
        self.assertFalse(record.is_full())
        self.assertEqual(0, record.size())
        bucket = Steim1Bucket()
        bucket.put(1)
        record.append(bucket)
        self.assertEqual(1, record.size())
        self.assertFalse(record.is_full())

        bucket.put(1)
        record.append(bucket)
        self.assertEqual(1, record.size())
        self.assertFalse(record.is_full())

    def test_steim_record(self):
        record = SteimRecord(number_of_frames=1)
        arr = array.array("i", range(0, 150))
        bucket = Steim1Bucket()
        for num in arr:
            if record.is_full():
                break
            if not bucket.put(num):
                print(f'added {record.append(bucket)}')
                print(f'full: {record.is_full()}')
                bucket.reset()
                bucket.put(num)

