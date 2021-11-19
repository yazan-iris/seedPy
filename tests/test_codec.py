import unittest

import array

from codec import EncodingFormat, get_encoder, get_decoder

from buffer import ByteOrder


class TestCodec(unittest.TestCase):

    def test_byte_order(self):
        encoder = get_encoder(EncodingFormat.STEIM_1, ByteOrder.BIG_ENDIAN)
        self.assertEqual(ByteOrder.BIG_ENDIAN, encoder.byte_order)

        encoder = get_encoder(EncodingFormat.STEIM_1, ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(ByteOrder.LITTLE_ENDIAN, encoder.byte_order)

    def test_encoding_format(self):
        encoder = get_encoder(EncodingFormat.STEIM_1, byte_order=ByteOrder.BIG_ENDIAN)
        self.assertEqual(EncodingFormat.STEIM_1, encoder.encoding_format)

        encoder = get_encoder(EncodingFormat.STEIM_2, byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(EncodingFormat.STEIM_2, encoder.encoding_format)

        encoder = get_encoder(EncodingFormat.STEIM_3, byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(EncodingFormat.STEIM_3, encoder.encoding_format)

    def test_encode(self):
        encoder = get_encoder(EncodingFormat.STEIM_1, byte_order=ByteOrder.BIG_ENDIAN)

        offset = 0
        ar = array.array("i", range(0, 150))
        steim_record = encoder.encode(ar, offset, number_of_frames=10)
        decoder = get_decoder(EncodingFormat.STEIM_1, byte_order=ByteOrder.BIG_ENDIAN)
        decoded_arr = decoder.decode(steim_record.to_byte_array())

        self.assertEqual(ar, decoded_arr)
