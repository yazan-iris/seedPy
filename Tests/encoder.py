import logging as log
import codecs
import itertools
import unittest

import array

from Codec import EncodingFormat, encoders
from Codec.Steim import SteimEncoder
from buffer import ByteOrder

log.basicConfig(level=log.ERROR)

class TestEncoder(unittest.TestCase):

    def test_byte_order(self):
        encoder = encoders.get(EncodingFormat.STEIM_1, ByteOrder.BIG_ENDIAN)
        self.assertEqual(ByteOrder.BIG_ENDIAN, encoder.byte_order)

        encoder = encoders.get(EncodingFormat.STEIM_1, ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(ByteOrder.LITTLE_ENDIAN, encoder.byte_order)

    def test_encoding_format(self):
        encoder = encoders.get(EncodingFormat.STEIM_1, byte_order=ByteOrder.BIG_ENDIAN)
        self.assertEqual(EncodingFormat.STEIM_1, encoder.encoding_format)

        encoder = encoders.get(EncodingFormat.STEIM_2, byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(EncodingFormat.STEIM_2, encoder.encoding_format)

        encoder = encoders.get(EncodingFormat.STEIM_3, byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(EncodingFormat.STEIM_3, encoder.encoding_format)

    def test_steim(self):
        encoder = encoders.get(EncodingFormat.STEIM_1, byte_order=ByteOrder.BIG_ENDIAN)

        offset = 0
        ar = array.array("i", range(0, 150))

        print(ar)
        steim_record = encoder.encode(ar, offset, number_of_frames=10)
        for frame in steim_record:
            print(f'frame={frame}')
        print(f'forward_integration_factor = {steim_record.forward_integration_factor}')
        print(f'reverse_integration_factor = {steim_record.reverse_integration_factor}')
        print(steim_record)
        offset += steim_record.number_of_samples


