import struct
import unittest

import array

from buffer import ByteOrder, ByteBuffer


class TestByteBuffer(unittest.TestCase):

    def test_byte_order(self):
        bb = ByteBuffer.allocate(capacity=4, byte_order=ByteOrder.BIG_ENDIAN)
        self.assertEqual(ByteOrder.BIG_ENDIAN, bb.byte_order)

        bb = ByteBuffer.allocate(capacity=4, byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(ByteOrder.LITTLE_ENDIAN, bb.byte_order)

    def test_allocate_zero(self):
        with self.assertRaises(ValueError):
            ByteBuffer.allocate(capacity=0, byte_order=ByteOrder.BIG_ENDIAN)

    def test_allocate_neg(self):
        with self.assertRaises(ValueError):
            ByteBuffer.allocate(capacity=-1, byte_order=ByteOrder.BIG_ENDIAN)

    def test_allocate(self):
        with self.assertRaises(ValueError):
            ByteBuffer.allocate(capacity=0, byte_order=ByteOrder.BIG_ENDIAN)

        bb = ByteBuffer.allocate(capacity=4, byte_order=ByteOrder.BIG_ENDIAN)
        self.assertEqual(ByteOrder.BIG_ENDIAN, bb.byte_order)
        self.assertEqual(0, bb.position)
        self.assertEqual(4, bb.capacity)
        self.assertEqual(4, bb.remaining)
        self.assertEqual(4, len(bb))

        index: int = 0
        bb[index] = 1
        self.assertEqual(index + 1, bb.position)
        self.assertEqual(4, bb.capacity)
        self.assertEqual(3, bb.remaining)
        self.assertEqual(4, len(bb))

        bb.put(2)
        self.assertEqual(2, bb.position)
        self.assertEqual(4, bb.capacity)
        self.assertEqual(2, bb.remaining)
        self.assertEqual(4, len(bb))
        self.assertSequenceEqual(b'\x01\x02\x00\x00', bb.to_byte_array())
        self.assertSequenceEqual([16908288], bb.to_int_array())
        self.assertEqual(2, bb.position)
        self.assertEqual(4, bb.capacity)
        self.assertEqual(2, bb.remaining)
        self.assertEqual(4, len(bb))

        bb[3] = 5
        self.assertSequenceEqual(b'\x01\x02\x00\x05', bb.to_byte_array())
        self.assertEqual(4, bb.position)
        self.assertEqual(4, bb.capacity)
        self.assertEqual(0, bb.remaining)
        self.assertEqual(4, len(bb))
        self.assertSequenceEqual([16908293], bb.to_int_array())

        self.assertEqual(5, bb[-1])
        self.assertEqual(0, bb[-2])

        with self.assertRaises(IndexError):
            bb.put(3)

        with self.assertRaises(IndexError):
            bb.put_int(3)

    def test_get_ints_1(self):
        int_list = [32799, 1, 258, 32770, 747474747]
        fmt = ">i"
        st_big_signed = struct.Struct(fmt)
        data = bytearray()
        index: int = 0
        buffer = bytearray(b'\x00') * 20
        print(int_list)
        for value in int_list:
            st_big_signed.pack_into(buffer, index, value)
            index += 4

        print(f'packed:{buffer}')
        print(f"packed:{array.array('i').frombytes(buffer)}")
        a2 = array.array('i')
        a2.frombytes(buffer)
        print(f"frombytes: {a2}")
        a2.byteswap()
        print(f"frombytes: {a2}")

        new_list = list(struct.unpack('>5i', buffer))
        print(new_list)


    def test_get_ints(self):
        int_list = [0, 1, 258, 32768]
        fmt = "<%dI" % len(int_list)
        fmt = ">%di" % len(int_list)
        data = struct.pack(fmt, *int_list)
        bb = ByteBuffer.wrap_bytes(values=data, byte_order=ByteOrder.BIG_ENDIAN)

        st_big_signed = struct.Struct(fmt)

        nums = list(st_big_signed.unpack(data))
        result = bb.to_int_array()
        print(bb._buffer)
        print(f'nums: {nums}')
        print('0000000000000')
        print(result)
        self.assertSequenceEqual(int_list, result)
