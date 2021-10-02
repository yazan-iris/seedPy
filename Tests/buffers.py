import unittest

from Codec.Steim import SteimFrame
from buffer import IntBuffer, ByteOrder


class TestIntBuffer(unittest.TestCase):

    def test_int_buffer(self):
        buffer = IntBuffer.allocate(10)
        self.assertEqual(10, buffer.capacity)
        self.assertEqual(0, buffer.position)
        self.assertEqual(10, buffer.remaining)
        buffer.put(2)
        self.assertEqual(10, buffer.capacity)
        self.assertEqual(1, buffer.position)
        self.assertEqual(9, buffer.remaining)

        print(buffer)

        # buffer.position()
        # buffer.remaining()

    def test_int_buffer_byte_order(self):
        buffer = IntBuffer.allocate(10)
        self.assertEqual(ByteOrder.BIG_ENDIAN, buffer.byte_order)
        buffer = IntBuffer.allocate(10, byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(ByteOrder.LITTLE_ENDIAN, buffer.byte_order)
        self.assertEqual(10, buffer.capacity)
        self.assertEqual(0, buffer.position)
        self.assertEqual(10, buffer.remaining)
        buffer.put(2)
        self.assertEqual(10, buffer.capacity)
        self.assertEqual(1, buffer.position)
        self.assertEqual(9, buffer.remaining)
        self.assertEqual(2, buffer[0])


