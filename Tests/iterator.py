import unittest
import importlib.resources

import RecordIO


class TestVolume(unittest.TestCase):

    def test_open(self):
        with importlib.resources.path('Tests', 'fdsnws-dataselect_2020-03-28t21_11_14z.mseed') as file, \
                RecordIO.iterate(file) as iterator:
            for record in iterator:
                print(record)
                print(len(record.data))
                blockettes = record.blockettes
                for blockette in blockettes:
                    print(blockette)

