import unittest

from codec import Steim1Bucket, Steim2Bucket


class TestBucket(unittest.TestCase):

    def test_steim_capacity(self):
        bucket = Steim1Bucket()
        self.assertEqual(4, bucket.capacity)
        bucket = Steim2Bucket()
        self.assertEqual(7, bucket.capacity)

    def test_steim1_len(self):
        bucket = Steim1Bucket()
        self.assertEqual(4, bucket.capacity)
        self.assertEqual(0, len(bucket))
        bucket.put(1)
        self.assertEqual(4, bucket.capacity)
        self.assertEqual(1, len(bucket))
        bucket.put(1)
        self.assertEqual(4, bucket.capacity)
        self.assertEqual(2, len(bucket))
        bucket.put(1)
        self.assertEqual(4, bucket.capacity)
        self.assertEqual(3, len(bucket))
        bucket.put(1)
        self.assertEqual(4, bucket.capacity)
        self.assertEqual(4, len(bucket))
        self.assertFalse(bucket.put(0))
        self.assertEqual(4, bucket.capacity)
        self.assertEqual(4, len(bucket))

    def test_steim1_put_1(self):
        pass

    def test_steim1_put_2(self):
        pass

    def test_steim1_put_3(self):
        pass

    def test_steim1_put_4(self):
        pass

    def test_steim1_put(self):
        """A simple bucket data structure to pack numbers according
    to Steim 1 algorithm.  The bucket has no use outside of Steim.
    buckets have control values describing how to unpack the numbers
    in accordance with the table below:
    control = 00 -> no data.
    control = 01 -> four ints that fits in 1 bytes each: -127 <= num <= 128
              ex: 1, 1, 1, 1 [00000001 00000001 00000001 00000001]
    control = 10 -> two ints that fits in 2 bytes each: -32768 <= num <= 32767
              ex: 1, 1 [00000000 00000001 00000000 00000001]
    control = 11 -> one int, 4 bytes -2,147,483,648 <= num <= 2,147,483,647
              ex: 1 [00000000 00000000 00000000 00000001]
    """

        bucket = Steim1Bucket()
        bucket.put(0)
        bucket.put(0)
        bucket.put(0)
        bucket.put(0)
        self.assertFalse(bucket.put(0))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual(values, [0])
        self.assertEqual(4, number_of_samples)

        bucket = Steim1Bucket()
        bucket.put(-128)
        bucket.put(-128)
        bucket.put(-128)
        bucket.put(-128)
        self.assertFalse(bucket.put(0))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual(values, [2155905152])
        self.assertEqual(4, number_of_samples)

        bucket = Steim1Bucket()
        bucket.put(-128)
        bucket.put(-128)
        bucket.put(-128)
        self.assertFalse(bucket.put(-129))
        self.assertTrue(bucket.put(-128))
        self.assertFalse(bucket.put(0))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual(values, [2155905152])
        self.assertEqual(4, number_of_samples)
        self.assertEqual(2155905152, values[0])
        arr = Steim1Bucket.fill(control=control, value=values[0]).unpack()
        self.assertEqual(4, len(arr))
        self.assertSequenceEqual([-128, -128, -128, -128], arr)

        bucket = Steim1Bucket()
        bucket.put(127)
        bucket.put(127)
        bucket.put(127)
        self.assertFalse(bucket.put(128))
        self.assertTrue(bucket.put(127))
        self.assertFalse(bucket.put(0))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual(values, [2139062143])
        self.assertEqual(4, number_of_samples)

        arr = Steim1Bucket.fill(control=control, value=values[0]).unpack()
        self.assertEqual(4, len(arr))
        self.assertSequenceEqual([127, 127, 127, 127], arr)

        bucket = Steim1Bucket()
        bucket.put(3)
        bucket.put(1)
        bucket.put(2)
        bucket.put(1)
        self.assertFalse(bucket.put(1))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual(values, [50397697])
        self.assertEqual(4, number_of_samples)

        arr = Steim1Bucket.fill(control=control, value=values[0]).unpack()
        self.assertEqual(4, len(arr))
        self.assertSequenceEqual([3, 1, 2, 1], arr)

        bucket.clear()
        self.assertTrue(bucket.is_empty())

        bucket.put(1)
        bucket.put(1)
        bucket.put(1)
        self.assertFalse(bucket.put(200))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(2, control)
        self.assertEqual(65537, values[0])
        self.assertEqual(2, number_of_samples)

        self.assertFalse(bucket.is_empty())
        self.assertFalse(bucket._is_full())
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(3, control)
        self.assertEqual(1, values[0])
        self.assertEqual(1, number_of_samples)

        # bucket.index()
        # bucket.put()
        # bucket.size()
        # bucket.reset()
        # bucket.is_full()
        # bucket.is_empty()
        # bucket.pack()
        # bucket.unpack()
        # bucket.clear()
        # bucket.index(EncodingFormat.STEIM_1, )

    def test_steim2_put_1(self):
        pass

    def test_steim2_put_2(self):
        pass

    def test_steim2_put_3(self):
        pass

    def test_steim2_put_4(self):
        bucket = Steim2Bucket()
        bucket.put(0)
        bucket.put(0)
        bucket.put(0)
        bucket.put(0)
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual(values, [0])
        self.assertEqual(4, number_of_samples)
        self.assertSequenceEqual([0], values)
        bucket = Steim2Bucket.fill(control, values[0])
        arr = bucket.unpack()
        self.assertSequenceEqual([0, 0, 0, 0], arr)
        self.assertFalse(bucket.is_empty())
        bucket.clear()
        self.assertTrue(bucket.is_empty())

        bucket = Steim2Bucket()
        bucket.put(-128)
        bucket.put(-128)
        bucket.put(-128)
        bucket.put(-128)
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual([2155905152], values)
        self.assertEqual(4, number_of_samples)
        bucket = Steim2Bucket.fill(control, values[0])
        arr = bucket.unpack()
        self.assertSequenceEqual([-128, -128, -128, -128], arr)
        self.assertFalse(bucket.is_empty())
        bucket.clear()
        self.assertTrue(bucket.is_empty())

        bucket = Steim2Bucket()
        bucket.put(127)
        bucket.put(127)
        bucket.put(127)
        self.assertTrue(bucket.put(127))
        self.assertFalse(bucket.put(0))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual(values, [2139062143])
        self.assertEqual(4, number_of_samples)

        arr = Steim1Bucket.fill(control=control, value=values[0]).unpack()
        self.assertEqual(4, len(arr))
        self.assertSequenceEqual([127, 127, 127, 127], arr)

        bucket = Steim2Bucket()
        bucket.put(3)
        bucket.put(1)
        bucket.put(2)
        bucket.put(1)
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, control)
        self.assertSequenceEqual(values, [50397697])
        self.assertEqual(4, number_of_samples)

        arr = Steim2Bucket.fill(control=control, value=values[0]).unpack()
        self.assertEqual(4, len(arr))
        self.assertSequenceEqual([3, 1, 2, 1], arr)

        bucket.clear()
        self.assertTrue(bucket.is_empty())

        self.assertTrue(bucket.put(1))
        self.assertTrue(bucket.put(1))
        self.assertTrue(bucket.put(1))
        self.assertFalse(bucket.put(200))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(2, control)
        self.assertEqual(3222275073, values[0])
        self.assertEqual(3, number_of_samples)

        self.assertTrue(bucket.is_empty())
        self.assertFalse(bucket._is_full())
        self.assertTrue(bucket.put(200))
        control, values, number_of_samples = bucket.pack()
        self.assertEqual(1, number_of_samples)
        self.assertEqual(1073742024, values[0])
        self.assertEqual(2, control)

        arr = Steim2Bucket.fill(control=control, value=values[0]).unpack()
        self.assertEqual(1, len(arr))
        self.assertSequenceEqual([200], arr)

    def binary(self, x: int, n: int):
        return format(x, 'b').zfill(n)

    def test_with_width(self):
        # print(f'====={self.left_right_shift(956064398, 6, 2, 26, 5)}')

        print(bin(956064398))
        num = 956064398 >> 24
        # print(bin(956064398 | 63))
        print(bin(num))
        print(bin(63))
        print(bin(num & 63))
        print(bin(num & 0x3F))

        num = 956064398 >> 18
        # print(bin(956064398 | 63))
        print(bin(num))
        print(bin(63))
        print(bin(num & 63))
        print(bin(num & 0x3F))

        num = 956064398 >> 12
        # print(bin(956064398 | 63))
        print(bin(num))
        print(bin(63))
        print(bin(num & 63))
        print(bin(num & 0x3F))

        num = 956064398 >> 6
        # print(bin(956064398 | 63))
        print(bin(num))
        print(bin(63))
        print(bin(num & 63))
        print(bin(num & 0x3F))

        num = 956064398
        # print(bin(956064398 | 63))
        print(bin(num))
        print(bin(63))
        print(bin(num & 63))
        print(bin(num & 0x3F))

        print(self.unpack_5(num, 63))

    def test_unpack_2_15(self):
        #nums = unpack_2_15(value=-1388683805, mask=32767)
        #print(nums)

        #b = Steim2Bucket()
        #res = b.put_list(nums)
        #print(res)

        #b = Steim2Bucket.fill(2, -108113011)
        #print(b)

        #print(2147483517 >> 30)
        #b = Steim2Bucket.fill(2, 2147483517)
        #print(b)
        pass

    def test_unpack_compare(self):
        num = 143798419
        n = num >> 20
        print(bin(n))
        print(bin(1023))
        print(bin(n & 1023))

        num = -143798419
        b = Steim2Bucket.fill(2, num)
        print(bin(num))
        print(b)

        num = 2147483535
        b = Steim2Bucket.fill(2, num)
        print(bin(num))
        print(b)


    def unpack_5(self, value: int, mask: int):
        shift: int = 24
        nums = list()
        max_value = 2 ** (6 - 1)
        for i in range(0, 5):
            num = (value >> shift) & mask
            num = -(num - max_value) if num >= max_value else num
            nums.append(num)
            shift -= 6
        return nums

    def left_right_shift(self, value: int, width: int, left_start: int, right: int, expected_size: int) -> list[int]:
        left = left_start + 32
        right += 32
        nums = list()
        max_value = 2 ** (width - 1)
        for i in range(0, expected_size):
            print(f'shifting left {left} then shifting right {right}')
            num = value << left
            print(f'left<< {num}   {bin(num)}')
            num = num >> right
            # value = (value << left) >> right
            print(f'right {right}>> {num}   {bin(num)}')
            nums.append(-(num - max_value) if num >= max_value else num)
            left += width
        return nums

    def fix_sign(self, value: int, width: int):
        max = 2 ** (width - 1)
        print(f'max:{max}    value:{value}')
        print(f'pow:{2 ** width}')
        if value >= max:
            value = value - max
            return -value
        return value

    def test_steim2_put_5(self):
        pass

    def test_steim2_put_6(self):
        pass

    def test_steim2_put_7(self):
        pass
