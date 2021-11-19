import unittest

import array

from codec import SteimFrame, SteimHeader, Steim1Bucket, SteimError, EncodingFormat
from buffer import ByteOrder, IntBuffer


class TestSteimFrame(unittest.TestCase):

    def test_iter(self):

        class Iterator:
            def __init__(self):
                self._my_list = list()

            def append(self, value: int):
                self._my_list.append(value)

            def __iter__(self):
                self._index = 0
                return self

            def __next__(self):
                if self._index >= len(self._my_list):
                    raise StopIteration
                value = self._my_list[self._index]
                self._index += 1
                return value

        frame = Iterator()
        frame.append(0)
        frame.append(1)
        frame.append(2)
        frame.append(3)
        frame.append(4)

        for bucket_idx, item in enumerate(frame, start=1):
            print(f':::{bucket_idx}   {item}')

    def test_steimFrame(self):
        original = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
                    52, 53, 54, 55, 56, 57, 58, 59]
        arr = [357913941, 66051, 67438087, 134810123, 202182159, 269554195,
               336926231, 404298267, 471670303, 539042339, 606414375, 673786411, 741158447,
               808530483, 875902519, 943274555]

        steim = [(0, 357913941), (1, 66051), (1, 67438087), (1, 134810123), (1, 202182159), (1, 269554195),
                 (1, 336926231), (1, 404298267), (1, 471670303), (1, 539042339), (1, 606414375),
                 (1, 673786411), (1, 741158447), (1, 808530483), (1, 875902519), (1, 943274555)]
        ib = IntBuffer.wrap_ints(values=arr, byte_order=ByteOrder.BIG_ENDIAN)
        frame = SteimFrame.wrap_ints(values=arr, byte_order=ByteOrder.BIG_ENDIAN)
        print(frame)
        print(frame.remaining)
        self.assertSequenceEqual(steim, frame)

        numbers = list()
        for control, value in frame:
            numbers.extend(Steim1Bucket.fill(control, value).unpack())
        self.assertSequenceEqual(original, numbers)

    def test_steimFrame_to_bytes(self):
        original = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
                    52, 53, 54, 55, 56, 57, 58, 59]
        arr = [357913941, 66051, 67438087, 134810123, 202182159, 269554195,
               336926231, 404298267, 471670303, 539042339, 606414375, 673786411, 741158447,
               808530483, 875902519, 943274555]

        steim = [(0, 357913941), (1, 66051), (1, 67438087), (1, 134810123), (1, 202182159), (1, 269554195),
                 (1, 336926231), (1, 404298267), (1, 471670303), (1, 539042339), (1, 606414375),
                 (1, 673786411), (1, 741158447), (1, 808530483), (1, 875902519), (1, 943274555)]
        frame = SteimFrame.wrap_ints(values=arr, byte_order=ByteOrder.BIG_ENDIAN)
        self.assertSequenceEqual(steim, frame)

        print(frame.to_byte_array())

    def test_steim_frame(self):
        result = [357913941, 66051, 67438087, 134810123, 202182159, 269554195,
                  336926231, 404298267, 471670303, 539042339, 606414375, 673786411, 741158447,
                  808530483, 875902519, 943274555]

        result = [(0, 22369621), (0, 0), (0, 52), (1, 66051), (1, 67438087), (1, 134810123), (1, 202182159),
                  (1, 269554195),
                  (1, 336926231),
                  (1, 404298267), (1, 471670303), (1, 539042339), (1, 606414375), (1, 673786411), (1, 741158447),
                  (1, 808530483)]

        arr = array.array("i", range(0, 150))
        idx: int = 0
        frame = SteimHeader(encoding_format=EncodingFormat.STEIM_1)
        frame.forward_integration_factor = arr[idx]
        bucket = Steim1Bucket()
        num = 0
        while frame.remaining() > 0 and idx < len(arr):
            if not bucket.put(arr[idx]):
                control, values, number_of_samples = bucket.pack()
                num += number_of_samples
                frame.append(control, values)
                # what to do with leftovers in the bucket, sample_idx is ahead now
                # 1   |    2   |1292821
                # pack will pack 1  |   2 leaving   1292821 in the bucket, 1292821 already accounted for in
                # sample_idx
                # use num instead, to figure out index of last sample in arr for next frame run
                if not bucket.put(arr[idx]):
                    raise ValueError
            idx += 1

        frame.reverse_integration_factor = arr[num]
        self.assertEqual(52, num)
        self.assertEqual(22369621, int(frame.control_sequence))
        self.assertSequenceEqual(result, frame)

        seed_bytes = frame.to_byte_array()
        frame_from_bytes = SteimHeader.wrap_bytes(encoding_format=frame.encoding_format, values=seed_bytes,
                                                  byte_order=ByteOrder.BIG_ENDIAN)
        self.assertEqual(22369621, int(frame.control_sequence))

        self.assertEqual(frame, frame_from_bytes)



    def test_steim_short(self):
        result = [(0, 16777216), (0, 0), (0, 0), (1, 66051), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),
                  (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        arr = array.array("i", range(0, 4))
        header = SteimHeader()
        bucket = Steim1Bucket()
        num = 0
        for sample in arr:
            if header.is_full():
                break
            if not bucket.put(sample):
                control, values, number_of_samples = bucket.pack()
                num += number_of_samples
                if not header.append(control, values):
                    raise ValueError
                if not bucket.put(sample):
                    raise ValueError
        if not bucket.is_empty():
            control, values, number_of_samples = bucket.pack()
            num += number_of_samples
            if not header.append(control, values):
                raise ValueError

        self.assertFalse(header.is_empty())
        self.assertFalse(header.is_full())
        self.assertEqual(4, num)
        print(header.control_sequence)
        self.assertSequenceEqual(result, header)
        self.assertEqual(4, header.position)

        header.forward_integration_factor = 0
        header.reverse_integration_factor = 4
        self.assertEqual(4, header.position)
        self.assertSequenceEqual(
            [(0, 16777216), (0, 0), (0, 4), (1, 66051), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),
             (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], header)

        header[4] = (1, 5)

        self.assertSequenceEqual(
            [(0, 20971520), (0, 0), (0, 4), (1, 66051), (1, 5), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0),
             (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)], header)
        self.assertEqual(4, header.position)

    def test_steim_header(self):
        result = [(0, 22369621), (0, 0), (0, 0), (1, 66051), (1, 67438087), (1, 134810123), (1, 202182159),
                  (1, 269554195), (1, 336926231), (1, 404298267), (1, 471670303), (1, 539042339), (1, 606414375),
                  (1, 673786411), (1, 741158447), (1, 808530483)]

        header = SteimHeader()
        self.assertEqual(ByteOrder.BIG_ENDIAN, header.byte_order)
        header = SteimHeader(byte_order=ByteOrder.LITTLE_ENDIAN)
        self.assertEqual(ByteOrder.LITTLE_ENDIAN, header.byte_order)
        self.assertEqual(13, header.capacity)
        self.assertEqual(3, header.position)
        self.assertEqual(13, header.remaining)
        cs = header.control_sequence
        self.assertIsNotNone(cs)
        self.assertEqual(0, int(cs))

        with self.assertRaises(IndexError):
            header[0] = (0, 4)
        with self.assertRaises(IndexError):
            header[1] = (0, 4)
        with self.assertRaises(IndexError):
            header[2] = (0, 4)

        header.forward_integration_factor = 0
        self.assertEqual(3, header.position)

        arr = array.array("i", range(0, 150))
        bucket = Steim1Bucket()
        num = 0
        for sample in arr:
            if header.is_full():
                break
            if not bucket.put(sample):
                control, values, number_of_samples = bucket.pack()
                num += number_of_samples
                if not header.append(control, values):
                    raise ValueError
                if not bucket.put(sample):
                    raise ValueError

        self.assertFalse(header.is_empty())
        self.assertTrue(header.is_full())
        self.assertEqual(52, num)
        print(header)
        self.assertSequenceEqual(result, header)
        header.forward_integration_factor = 3
        header.forward_integration_factor = 5

        # self.assertEqual(16, len(header))
        for num in header:
            print(num)

        for control, num in header:
            print(f'control: {control}, num: {num}')
            bucket = Steim1Bucket.fill(control, num)
            values = bucket.unpack()
            print(values)

        print(cs)
        # header.is_full()
        # header.to_array()
