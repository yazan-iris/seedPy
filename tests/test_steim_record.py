import unittest

import array
import math

from codec import SteimRecord, Steim1Bucket, EncodingFormat, SteimBucket, ControlSequence, Steim2Bucket
from buffer import ByteOrder


class TestSteimRecord(unittest.TestCase):

    def test_allocate_record_1(self):
        lis = [1, 2, 3, 4, 5, 6]
        print(' '.join(str(x) for x in lis[0:3]))

    def test_allocate_record(self):
        lis = [1, 2, 3, 4, 5, 6]
        ' '.join(str(x) for x in list(range(0, 3)))

        record = SteimRecord.allocate(10, encoding_format=EncodingFormat.STEIM_2, byte_order=ByteOrder.BIG_ENDIAN)
        self.assertEqual((10, 16), record.shape)

        arr = record.to_byte_array()
        self.assertEqual(160 * 4, len(arr))

        record = SteimRecord.wrap_bytes(arr, byte_order=ByteOrder.BIG_ENDIAN, encoding_format=EncodingFormat.STEIM_2)
        self.assertEqual((10, 16), record.shape)

        arr = record.to_byte_array()
        self.assertEqual(160 * 4, len(arr))

        arr = array.array("i", range(0, 1500))
        record = SteimRecord.allocate(10, encoding_format=EncodingFormat.STEIM_2, byte_order=ByteOrder.BIG_ENDIAN)
        row, column = record.shape
        self.assertEqual(10, row)
        self.assertEqual(16, column)

        reusable_bucket = Steim2Bucket()
        for num in arr:
            if record.is_full():
                break
            if not reusable_bucket.put(num):
                if not record.append(reusable_bucket):
                    raise RuntimeError
                if not reusable_bucket.put(num):
                    raise RuntimeError
        self.assertEqual(482, record.number_of_samples)
        self.assertEqual(0, record.forward_integration_factor)
        self.assertEqual(481, record.reverse_integration_factor)

        byte_array = record.to_byte_array()
        self.assertEqual(640, len(byte_array))

        record = SteimRecord.wrap_bytes(byte_array, encoding_format=record.encoding_format,
                                        byte_order=record.byte_order)
        self.assertTrue(record.is_full())
        # self.assertEqual(380, record.number_of_samples)
        self.assertEqual(0, record.forward_integration_factor)
        self.assertEqual(481, record.reverse_integration_factor)
        self.assertEqual(10, record.number_of_frames())

        samples = list()
        for i in range(0, record.number_of_frames()):
            frame = record.frame(i)
            cs = ControlSequence(frame[0])
            start: int = 1
            if i == 0:
                forward_integration_factor = frame[1]
                reverse_integration_factor = frame[2]
                start = 3
            for b_index in range(start, 16):
                control: int = cs[b_index]
                if control == 0:
                    continue
                bucket = SteimBucket.fill(encoding_format=record.encoding_format, control=control, value=frame[b_index])
                nums = bucket.unpack()
                samples.extend(nums)
        print(samples)
        arr = array.array("i", range(0, 482))
        self.assertSequenceEqual(arr, samples)

    def test_record_wrap_bytes(self):

        arr = array.array("i", range(0, 1500))
        byte_order: ByteOrder = ByteOrder.BIG_ENDIAN
        number_of_frames: int = math.floor((4096 / 64) - 2)
        encoding_format: EncodingFormat = EncodingFormat.STEIM_2
        record = SteimRecord(encoding_format=encoding_format, number_of_frames=number_of_frames, byte_order=byte_order)
        print(type(arr[0]))
        record.forward_integration_factor = arr[0]
        reusable_bucket = Steim1Bucket()
        for num in arr:
            if record.is_full():
                break
            if not reusable_bucket.put(num):
                if not record.append(reusable_bucket):
                    raise RuntimeError
                if not reusable_bucket.put(num):
                    raise RuntimeError
        record.append(reusable_bucket)
        self.assertEqual(48, record.size())
        for frame in record:
            print(frame)
        the_bytes = record.to_byte_array()

        record_from_bytes = SteimRecord.wrap_bytes(encoding_format=encoding_format, steim_bytes=the_bytes,
                                                   byte_order=byte_order)
        self.assertEqual(record, record_from_bytes)
        self.assertEqual(48, record.size())
        self.assertEqual(record.size(), record_from_bytes.size())

        self.assertEqual(0, record_from_bytes.forward_integration_factor)
        self.assertEqual(record.forward_integration_factor, record_from_bytes.forward_integration_factor)
        self.assertEqual(1499, record_from_bytes.reverse_integration_factor)
        self.assertEqual(record.reverse_integration_factor, record_from_bytes.reverse_integration_factor)

        nums = array.array('i')
        for frame in record:
            for control, value in frame:
                bucket = Steim1Bucket.fill(control=control, value=value)
                b = bucket.unpack()
                nums.extend(b)
        print(nums)
        print(arr)
        self.assertEqual(nums[0], record.forward_integration_factor)
        self.assertEqual(nums[-1], record.reverse_integration_factor)
        self.assertSequenceEqual(arr, nums)

    def test_record(self):
        record = SteimRecord(number_of_frames=1, byte_order=ByteOrder.BIG_ENDIAN)
        self.assertEqual(ByteOrder.BIG_ENDIAN, record.byte_order)
        self.assertIsNone(record.forward_integration_factor)
        self.assertIsNone(record.reverse_integration_factor)
        self.assertEqual(0, record.number_of_samples)
        self.assertFalse(record.is_full())
        self.assertTrue(record.is_empty())
        self.assertEqual(0, record.size())

        arr = array.array("i", range(0, 150))
        bucket = Steim1Bucket()
        for num in arr:
            if record.is_full():
                break
            if not bucket.put(num):
                record.append(bucket)
                if not bucket.put(num):
                    raise ValueError

        print(f'number_of_samples:{record.number_of_samples}')
        for f in record:
            print(f)
        # record.get_date()
        self.assertEqual(52, record.number_of_samples)
        self.assertEqual(0, record.forward_integration_factor)
        self.assertEqual(51, record.reverse_integration_factor)
