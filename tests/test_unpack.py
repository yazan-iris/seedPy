import ctypes
import pathlib
import struct
import unittest

import numpy
from codec import unpack_steim_2, SteimBucket, EncodingFormat, SteimError, Steim2Bucket, unpack_1, unpack_4, unpack_5
from ctypes import *



class TestUnpack(unittest.TestCase):

    def test_num(self):
        print(type(unpack_1(22)))
        print(type(unpack_4(22)))
        print(unpack_5(22))

    def test_unpack_11(self):
        print(1 << 1)
        print(1 << 2)
        print(1 << 3)
        print(bin(-1))
        print(int('01100000000000000000000000000001', 2))
        max_value = 2 ** (30 - 1)
        num = (1610612737 >> 0) & 1073741823

        # 536870913
        print(f'num:{num}')
        print(f'max:{max_value}')
        print(f'minus:{(1 << 29)}')
        if num >= max_value:
            num = (1 << 29) - num
        print(f'num:{num}')
        # 01 1000000000 0000000000 0000000001
        print(bin(1610612737))
        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=2, value=1610612737)
        self.assertSequenceEqual([-1], bucket.unpack())

    def unpack_steim_221(self, value: int, mask: int, shift_from: int, width: int, expected_list_size: int):
        shift: int = shift_from
        nums = list()
        max_value = 2 ** (width - 1)
        for i in range(0, expected_list_size):
            num = (value >> shift) & mask
            if num >= max_value:
                print(f'{num} > {max_value}  ::  {(1 << width - 1)}')
                num = (1 << width - 1) - num
            nums.append(num)
            shift -= width
        return nums

    def unpack_steim_22(self, value: int, mask: int, shift_from: int, width: int, expected_list_size: int):
        shift: int = shift_from
        nums = list()
        max_value = 2 ** (width - 1)
        for i in range(0, expected_list_size):
            num = (value >> shift) & mask
            print(f'max_value:{max_value}  num:{num}')
            if num == max_value:
                num = -num
            elif num > max_value:
                num = (1 << (width - 1)) - num
            nums.append(num)
            shift -= width
        return nums

    def test_unpack_1(self):
        nums = self.unpack_steim_22(value=1610612736, mask=1073741823, shift_from=0, width=30, expected_list_size=1)
        self.assertEqual(-536870912, nums[0])
        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=2, value=1610612735)
        self.assertSequenceEqual([536870911], bucket.unpack())
        nums = self.unpack_steim_22(value=1073741824, mask=1073741823, shift_from=0, width=30, expected_list_size=1)
        self.assertEqual(0, nums[0])
        nums = self.unpack_steim_22(value=1610612737, mask=1073741823, shift_from=0, width=30, expected_list_size=1)
        self.assertEqual(-1, nums[0])
        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=2, value=1073741825)
        nums = bucket.unpack()
        self.assertEqual(1, nums[0])

    def twosComplement(self, value, bitLength):
        return bin(value & (2 ** bitLength - 1))

    def test_uu(self):
        control = 1
        value = int('10100000000000001100000000000001', 2)
        print(f'2s: {self.twosComplement(value, 32)}')
        original: list[int] = [0, -67, -63, -63]

        bucket = Steim2Bucket()
        bucket.put_list(original)
        control, value, length = bucket.pack()
        self.assertEqual(12435905, value[0])
        self.assertEqual(1, control)
        bucket = Steim2Bucket.fill(control, 12435905)
        result = bucket.unpack()
        self.assertSequenceEqual(original, result)

    def test_unpack_2(self):
        original: list[int] = [-1, -1]
        nums = self.unpack_steim_22(value=2684403713, mask=32767, shift_from=15, width=15, expected_list_size=2)
        self.assertSequenceEqual(original, nums)
        print(nums)
        self.assertEqual(-1, nums[0])

        control = 2
        value = int('10000000000000000000000000000001', 2)
        original: list[int] = [0, 1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('10100000000000001100000000000001', 2)
        print(value)
        print(bin(value))
        original: list[int] = [-1, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())
        unpack_steim_2(value=2684403713, mask=32767, shift_from=15, width=15, expected_list_size=2)

        value = int('10000000000000000100000000000001', 2)

        original: list[int] = [0, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('10100000000000000100000000000001', 2)
        original: list[int] = [-16384, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

    def test_unpack_3(self):
        control = 2
        value = int('11000000000000000000000000000001', 2)
        original: list[int] = [0, 0, 1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('11000000000000000000001000000001', 2)
        original: list[int] = [0, 0, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('11000000000000000000001100000001', 2)
        original: list[int] = [0, 0, -257]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('11000000000000000000000100000001', 2)
        original: list[int] = [0, 0, 257]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('11010000000101000000010100000001', 2)
        original: list[int] = [257, 257, 257]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('11011111111101111111110111111111', 2)
        original: list[int] = [511, 511, 511]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('11111111111111111111111111111111', 2)
        original: list[int] = [-511, -511, -511]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

    def test_unpack_4(self):
        control = 1
        value = int('00000000000000000000000000000001', 2)
        original: list[int] = [0, 0, 0, 1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('00000000000000000000000010000001', 2)
        original: list[int] = [0, 0, 0, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('10000000100000001000000010000001', 2)
        original: list[int] = [-128, -128, -128, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('00000000000000000000000010000001', 2)
        original: list[int] = [0, 0, 0, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('10000001100000011000000110000001', 2)
        original: list[int] = [-1, -1, -1, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('10000001100000011000000110000001', 2)
        original: list[int] = [0, -61, -65, -65]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=12435905)
        self.assertSequenceEqual(original, bucket.unpack())
        # 00000000 10111101 11000001 11000001

        # 00000000 10111101 11000001 11000001

    def test_unpack_5(self):
        control = 3
        value = int('11000000000000000000000000000001', 2)
        with self.assertRaises(SteimError):
            SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)

        value = int('00000000000000000000000000000001', 2)
        original: list[int] = [0, 0, 0, 0, 1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

    def test_unpack_6(self):
        control = 3
        value = int('11000000000000000000000000000001', 2)
        with self.assertRaises(SteimError):
            SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)

        value = int('01000000000000000000000000000001', 2)
        original: list[int] = [0, 0, 0, 0, 0, 1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

    def test_unpack_7(self):
        control = 3
        value = int('11000000000000000000000000000001', 2)
        with self.assertRaises(SteimError):
            SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)

        value = int('10000000000000000000000000000001', 2)
        original: list[int] = [0, 0, 0, 0, 0, 0, 1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('10000001000100010001000100010001', 2)
        original: list[int] = [1, 1, 1, 1, 1, 1, 1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())

        value = int('10001001100110011001100110011001', 2)
        original: list[int] = [-1, -1, -1, -1, -1, -1, -1]

        bucket = SteimBucket.fill(encoding_format=EncodingFormat.STEIM_2, control=control, value=value)
        self.assertSequenceEqual(original, bucket.unpack())
