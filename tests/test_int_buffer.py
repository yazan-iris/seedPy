import ctypes
from typing import List

import math
import struct
import sys
import unittest
import array
import numpy

from buffer import ByteOrder, IntBuffer, IntArray




class TestIntBuffer(unittest.TestCase):

    def test_zero_int_array(self):

        tup = (1,2,3,4,5,6,7)
        print(tup[0:3])
        arr = IntArray.zeros(2, 3)
        print(arr)

    def test_int_array(self):
        b = struct.pack('>8i', 1, 2, 3, 4, 5, 6, 7, 8000)
        print(len(b))
        ar = struct.unpack('>8i', b[0:32])
        print(ar)
        ar = IntArray.wrap_bytes(b, ByteOrder.BIG_ENDIAN, rows=2, columns=4)
        print('row[0] {}'.format(ar[0]))



    def test_numpy(self):
        arr = numpy.zeros((1, 16))
        print(type(arr))
        print(arr)
        print(arr[0])

        print(arr[0][1])
        arr[0][4] = 3

        arr = IntArray.allocate(1, 16, ByteOrder.BIG_ENDIAN)

        print(arr[0])

        print(arr[0][1])
        print(arr.to_bytes())

        arr = IntArray.wrap_bytes(arr.to_bytes(), byte_order=ByteOrder.BIG_ENDIAN)
        print(arr[0])
        pair = arr.shape
        print(f'pair:{pair}')
        print(f'columns:{pair[0]}')
        print(f'len:{len(pair)}')
        print(f'rows:{pair[1]}')
        print(arr.shape)
        print(arr[1])
        arr.reshape(4, 4)
        print(arr[1])
        print(arr[1])

        print(arr[1][1])

        print(arr.shape)

    def test_list(self):
        buffer = IntBuffer(capacity=10, byte_order=ByteOrder.BIG_ENDIAN)
        self.assertIsNotNone(buffer)
        self.assertEqual(10, len(buffer))
        self.assertEqual(ByteOrder.BIG_ENDIAN, buffer.byte_order)
        self.assertEqual(0, buffer.position)
        self.assertEqual(10, buffer.remaining)

        print(ByteOrder.BIG_ENDIAN.value)
        print(buffer.byte_order)

        buffer[0] = -2
        self.assertEqual(-2, buffer[0])
        # self.assertEqual(1, buffer.position)
        # self.assertEqual(9, buffer.remaining)

        print(sys.byteorder)
        print(buffer.to_byte_array())
        ba = buffer.to_byte_array()
        self.assertEqual(40, len(ba))
