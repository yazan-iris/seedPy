import importlib.resources
import unittest

from codec import get_decoder
from seedio import iterate


class TestRecord(unittest.TestCase):

    def test_record(self):
        foo = {42: 'aaa', 2.78: 'bbb', True: 'ccc'}
        print(foo[42])

        foo = dict()
        foo[42] = 'aaa'
        print(foo[42])

        arr = list()
        with importlib.resources.open_text('tests',
                                           'fdsnws-dataselect_2021-10-16t19_00_21z.csv') as file:
            i:int = 0
            for line in file:
                if i % 1000 == 0:
                    line = line.split(",")
                    arr.append((i, line[1]))
                i += 1

        with importlib.resources.path('tests',
                                      'fdsnws-dataselect_2021-10-16t19_00_21z.mseed') as file, \
                iterate(file, decompress=False) as iterator:
            r: int = 0
            carry_over = None
            samples = list()
            for record in iterator:
                print(record.b1000)
                print(record.sample_rate)
                print(record)
                print(record.to_int_array())
                samples.extend(get_decoder(encoding_format=record.encoding_format, byte_order=record.byte_order). \
                               decode(data=record.data, carry_over=carry_over,
                                      expected_number_of_samples=record.number_of_samples))
                carry_over = samples[-1]
                r += 1
                print(r)

        self.assertSamplesEqual(arr, samples)

    def assertSamplesEqual(self, arr, samples):
        j: int = 0
        for i in range(0, len(samples)):
            sample = samples[i]
            if i == arr[j]:
                if arr[j][1] != sample[i]:
                    raise AssertionError(i)
