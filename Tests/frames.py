import logging as log
import unittest

import array

from Codec.Steim import SteimFrame
from Codec.Steim.frames import SteimHeaderFrame
from buffer import IntBuffer, ByteOrder

log.basicConfig(level=log.ERROR)


class TestSteimFrames(unittest.TestCase):

    def test_steim_frame(self):
        buffer = SteimFrame()
        self.assertEqual(ByteOrder.BIG_ENDIAN, buffer.byte_order)
        buffer = SteimFrame(byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(ByteOrder.LITTLE_ENDIAN, buffer.byte_order)
        self.assertEqual(15, buffer.capacity)
        self.assertEqual(1, buffer.position)
        self.assertEqual(15, buffer.remaining)

    def test_steim_header_frame(self):
        buffer = SteimHeaderFrame()
        self.assertEqual(ByteOrder.BIG_ENDIAN, buffer.byte_order)
        buffer = SteimHeaderFrame(byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(ByteOrder.LITTLE_ENDIAN, buffer.byte_order)
        self.assertEqual(13, buffer.capacity)
        self.assertEqual(3, buffer.position)
        self.assertEqual(13, buffer.remaining)

        buffer.forward_integration_factor = 2
        buffer.reverse_integration_factor = 6
        self.assertEqual(6, buffer[2])
        print(buffer)

    def test_steim_header_frame_BigEndian(self):
        header = SteimHeaderFrame()
        self.assertEqual(ByteOrder.BIG_ENDIAN, header.byte_order)
        self.assertEqual(13, header.capacity)
        self.assertEqual(3, header.position)
        self.assertEqual(13, header.remaining)

        header.forward_integration_factor = 2
        self.assertEqual(2, header[1])
        self.assertEqual(2, header.forward_integration_factor)
        self.assertEqual(3, header.position)
        print(header)

    def test_steim_frame_index(self):
        ar = array.array("i", range(0, 150))
        frame = SteimFrame()
        for num in ar:
            if not frame.append(2, [num]):
                break
        print(len(frame.to_array()))
        print(frame)

    def test_raise_exception(self):
        frame = SteimFrame()
        with self.assertRaises(IndexError):
            frame[-1]
