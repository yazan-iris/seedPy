import ctypes
import pathlib
from abc import ABC, abstractmethod
from collections import Sequence
from enum import Enum
from typing import Optional
import ctypes as _ctypes
import array
import math

from buffer import ByteOrder, IntArray


class CodecError(SyntaxError):
    """An error when parsing an XML document.

    In addition to its exception value, a ParseError contains
    two extra attributes:
        'code'     - the specific exception code
        'position' - the line and column of the error

    """

    def __init__(self, message: str):
        super().__init__(message)

    pass


class SteimError(CodecError):
    def __init__(self, fmt: str, *args, **kwargs):
        super().__init__(fmt.format(*args, **kwargs))


class EncodingFormat(int, Enum):
    ASCII = 0
    SIXTEEN_BIT = 1
    TWENTY_FOUR_BIT = 2
    THIRTY_TOW_BIT = 3
    IEEE_FLOATING_POINT = 4
    IEEE_DOUBLE = 5
    STEIM_1 = 10
    STEIM_2 = 11
    GEOSCOPE_24 = 12
    GEOSCOPE_16_3 = 13
    GEOSCOPE_16_4 = 14
    US_NATIONAL_NETWORK = 15
    CDSN = 16
    GRAEFENBERG = 17
    IPG = 18
    STEIM_3 = 19
    SRO = 30
    HGLP = 31
    DWWSSN = 32
    RSTN = 33


class InvalidControlSequenceError(SteimError):
    def __init__(self, control_sequence: ('ControlSequence', int, Sequence), message=None):
        self.control_sequence = control_sequence
        self.message = f"Invalid control sequence {control_sequence}" if message is None else message
        super().__init__(self.message)


class ControlSequence(Sequence):
    def __init__(self, value: (int, list) = 0):
        self._length = 16
        self._value = 0
        if value is not None:
            if isinstance(value, int):
                ControlSequence.validate(value)
                self._value = value
            # elif isinstance(value, numpy.int32):
            # self._value = value.item()
            # ControlSequence.validate(self._value)
            elif isinstance(value, Sequence):
                if len(value) > 16:
                    raise ValueError
                for idx, val in enumerate(value):
                    if idx == 0 and val != 0:
                        raise InvalidControlSequenceError(value,
                                                          f'Invalid control sequence, index:{idx}.  Expected  0 but '
                                                          f'received {val}')
                    self[idx] = val
            else:
                raise ValueError(type(value))
        self[0] = 0

    def __on(self, shift: int):
        self._value |= 1 << shift

    def __off(self, shift: int):
        self._value &= ~(1 << shift)

    def reset(self):
        self._value = 0

    def __getitem__(self, subscript: int) -> int:
        if subscript is None:
            raise ValueError
        if isinstance(subscript, slice):
            result = []
            if subscript.stop is not None and subscript.stop > len(self):
                raise IndexError
            for i in range(subscript.start if subscript.start is not None else 0,
                           subscript.stop if not None else len(self),
                           subscript.step if subscript.step is not None else 1):
                result.append((self._value >> (30 - i * 2)) & 0x03)
            return result
        else:
            if subscript >= 16:
                raise IndexError(subscript)
            return (self._value >> (30 - subscript * 2)) & 0x03

    def __setitem__(self, key, value):
        if key is None:
            raise ValueError
        if value is None:
            raise ValueError
        if key == 0 and value > 0:
            raise InvalidControlSequenceError(self, message=f"Value at index=0 is always 0, received {value}")

        if key < 0 or key > 15:
            raise IndexError(key)
        i = 31 - (2 * key)
        if value == 0:
            self.__off(i)
            self.__off(i - 1)
        elif value == 1:
            self.__off(i)
            self.__on(i - 1)
        elif value == 2:
            self.__on(i)
            self.__off(i - 1)
        elif value == 3:
            self.__on(i)
            self.__on(i - 1)
        else:
            raise SteimError(f"Invalid control value, expected [0, 1, 2, 3] but received {value}")

    def __len__(self) -> int:
        return self._length

    def __int__(self):
        # if isinstance(self._value, numpy.int32):
        # return self._value.value()
        return self._value

    def __str__(self) -> str:
        text = ''
        for i in range(0, len(self)):
            if i > 0:
                text += ' '
            control = self[i]
            if control == 0:
                text += '00'
            elif control == 1:
                text += '01'
            elif control == 2:
                text += '10'
            elif control == 3:
                text += '11'
            else:
                raise SteimError
        return text

    @staticmethod
    def validate(num: int = None):
        if num < 0:
            raise InvalidControlSequenceError(control_sequence=num)
        for idx in range(16):
            val = (num >> (30 - idx * 2)) & 0x03
            if idx == 0 and val > 0:
                raise InvalidControlSequenceError(control_sequence=num,
                                                  message=f'Invalid control sequence, index:{idx}.  Expected  0 but '
                                                          f'received {val}')
            if val > 3:
                raise InvalidControlSequenceError(control_sequence=num,
                                                  message=f'Invalid control sequence, index:{idx}.  Expected  1|2|3 '
                                                          f'but received {val}')


def size(num: int) -> int:
    if num is None:
        raise ValueError
    if -8 <= num <= 7:
        return 4
    elif -16 <= num <= 15:
        return 5
    elif -32 <= num <= 31:
        return 6
    elif -128 <= num <= 127:
        return 8
    elif -512 <= num <= 511:
        return 10
    elif -16384 <= num <= 16383:
        return 15
    elif -536870912 <= num <= 536870911:
        return 30
    else:
        return 32


def _pack_1(b1: int) -> int:
    if b1 is None:
        raise ValueError
    return b1


def _pack_2(b1: int, b2: int) -> int:
    if b1 is None or b2 is None:
        raise ValueError
    return (b1 << 16) | (b2 & 0xFFFF)


def _pack_4(b1: int, b2: int, b3: int, b4: int) -> int:
    if b1 is None or b2 is None or b3 is None or b4 is None:
        raise ValueError
    return (b1 & 0xff) << 24 | (b2 & 0xff) << 16 | (b3 & 0xff) << 8 | (b4 & 0xff)


def fix_sign_1(value: int, width: int):
    max = 2 ** (width - 1)
    if value >= max:
        value = value - 2 ** width
        return value
    return value


def fix_sign(value: int, width: int):
    max_value = 2 ** (width - 1)
    return -(value - max_value) if value >= max_value else value


def left_right_shift(value: int, width: int, left_start: int, right: int, expected_size: int) -> list[int]:
    left = left_start
    nums = list()
    max_value = 2 ** (width - 1)
    for i in range(0, expected_size):
        value = (value << left) >> right
        nums.append(-(value - max_value) if value >= max_value else value)
        left += width
    return nums


def fix_sign_1(self, value: int, width: int):
    max_value = 2 ** (width - 1)
    return -(value - max_value) if value >= max_value else value


def unpack_34(value: int):
    return [fix_sign((value >> 24) & 0xff, 8), fix_sign((value >> 16) & 0xff, 8), fix_sign((value >> 8) & 0xff, 8),
            fix_sign(value & 0xff, 8)]


def _pack_2_1(b1: int) -> int:
    return (b1 & 0x3fffffff) | (0x01 << 30)


def _pack_2_2(b1: int, b2: int) -> int:
    return ((b1 & 0x00007fff) << 15) | (b2 & 0x00007fff) | (0x02 << 30)


def _pack_2_3(b1: int, b2: int, b3: int) -> int:
    return ((b1 & 0x000003ff) << 20) | ((b2 & 0x000003ff) << 10) | (b3 & 0x000003ff) | (0x03 << 30)


def _pack_2_4(b1: int, b2: int, b3: int, b4: int) -> int:
    return (b1 & 0xff) << 24 | (b2 & 0xff) << 16 | (b3 & 0xff) << 8 | (b4 & 0xff)


def _pack_2_5(b1: int, b2: int, b3: int, b4: int, b5: int):
    return ((b1 & 0x0000003f) << 24) | ((b2 & 0x0000003f) << 18) | ((b3 & 0x0000003f) << 12) | \
           ((b4 & 0x0000003f) << 6) | (b5 & 0x0000003f) | (0x00 << 30)


def _pack_2_6(b1: int, b2: int, b3: int, b4: int, b5: int, b6: int) -> int:
    return ((b1 & 0x0000001f) << 25) | ((b2 & 0x0000001f) << 20) | ((b3 & 0x0000001f) << 15) | \
           ((b4 & 0x0000001f) << 10) | ((b5 & 0x0000001f) << 5) | (b6 & 0x0000001f) | (0x01 << 30)


def _pack_2_7(b1: int, b2: int, b3: int, b4: int, b5: int, b6: int, b7: int) -> int:
    return ((b1 & 0x0000000f) << 24) | ((b2 & 0x0000000f) << 20) | ((b3 & 0x0000000f) << 16) | \
           ((b4 & 0x0000000f) << 12) | ((b5 & 0x0000000f) << 8) | ((b6 & 0x0000000f) << 4) | \
           (b7 & 0x0000000f) | (0x02 << 30)


thirty_left_shift = 2 ** 30
Eight_left_shift = 2 ** 8
Six_left_shift = 2 ** 6

Five_left_shift = 2 ** 5

Four_left_shift = 2 ** 4

Ten_left_shift = 2 ** 10

Fifteen_left_shift = 2 ** 15


class SteimBucket(ABC):
    def __init__(self, capacity: int):
        self._array = [0] * capacity
        self._index = 0
        self._span = 0
        self.__totalSize = 0

    @property
    def index(self):
        return self._index

    @property
    def capacity(self):
        return len(self._array)

    def __len__(self):
        return self._index

    def __getitem__(self, item):
        if item is None:
            raise ValueError
        if item < 0:
            item = self._index + item
        if item < 0 or item >= self._index:
            raise IndexError(item)
        return self._array[item]

    def __str__(self):
        return ' '.join(str(x) for x in self._array[0:self._index])

    def is_empty(self) -> bool:
        return self._index == 0

    def reset(self):
        self._index = 0
        self.__totalSize = 0

    def clear(self):
        self.reset()
        self._array = [0] * self.capacity

    @abstractmethod
    def _is_full(self):
        raise NotImplemented

    @abstractmethod
    def put(self, num: int):
        pass

    @abstractmethod
    def pack(self, reset: bool = True) -> (int, [], int):
        raise NotImplemented

    def unpack(self):
        return self._array[0:self._index]

    @staticmethod
    def instance(encoding_format: EncodingFormat):
        if EncodingFormat.STEIM_1 == encoding_format:
            return Steim1Bucket()
        elif EncodingFormat.STEIM_2 == encoding_format:
            return Steim2Bucket()
        else:
            raise ValueError

    @staticmethod
    def fill(encoding_format: EncodingFormat, control: int, value: int) -> 'SteimBucket':
        if EncodingFormat.STEIM_1 == encoding_format:
            return Steim1Bucket.fill(control=control, value=value)
        elif EncodingFormat.STEIM_2 == encoding_format:
            return Steim2Bucket.fill(control=control, value=value)
        else:
            raise ValueError

    @staticmethod
    def unpack_by_control(encoding_format: EncodingFormat, control: int, value: int):
        if EncodingFormat.STEIM_1 == encoding_format:
            return Steim1Bucket.fill(control=control, value=value)
        elif EncodingFormat.STEIM_2 == encoding_format:
            if control == 1:
                return unpack_4(value)
            elif control == 2:
                c = get_control(value)
                if c == 1:
                    return unpack_1(value)
                elif c == 2:
                    return unpack_2(value)
                elif c == 3:
                    return unpack_3(value)
                else:
                    raise SteimError("Invalid control value, expected 2:1|2|3 but received 2:{}, value:{}", c, value)
            elif control == 3:
                c = get_control(value)
                if c == 0:
                    return unpack_5(value)
                elif c == 1:
                    return unpack_6(value)
                elif c == 2:
                    return unpack_7(value)
                else:
                    raise SteimError("Invalid control value, expected 0|1|2 but received {}", c)
            else:
                raise SteimError("Invalid control value, expected 2|3 but received {}, value:{}", control, value)
        else:
            raise ValueError


class Steim1Bucket(SteimBucket):
    """A simple bucket data structure to pack numbers according
    to Steim 1 algorithm.  The bucket has no use outside of Steim.
    The 3 major operations for this class is put, pack and unpack.
    When packing, you get a control, values and number of packed samples.
    Control values describes how to unpack the number in accordance with the table below:
    control = 00 -> no data.
    control = 01 -> four ints that fits in 1 bytes each: -127 <= num <= 128
              ex: 1, 1, 1, 1 [00000001 00000001 00000001 00000001]
    control = 10 -> two ints that fits in 2 bytes each: -32768 <= num <= 32767
              ex: 1, 1 [00000000 00000001 00000000 00000001]
    control = 11 -> one int, 4 bytes -2,147,483,648 <= num <= 2,147,483,647
              ex: 1 [00000000 00000000 00000000 00000001]
    """

    def __init__(self):
        super().__init__(4)

    def put(self, num: int) -> bool:
        if self._is_full():
            return False
        slot_size = 32
        if 127 >= num >= -128:
            slot_size = 8
        elif 32767 >= num >= -32768:
            slot_size = 16

        if slot_size < self._span:
            slot_size = self._span

        if slot_size * (len(self) + 1) > 32:
            return False

        self._array[self._index] = num
        self._index += 1
        self._span = slot_size
        return True

    def pack(self, reset: bool = True) -> (int, [], int):
        if self._index == 1:
            control = 3
            num = 1
            value = _pack_1(self._array[0])
        elif self._index == 2:
            control = 2
            num = 2
            value = _pack_2(self._array[0], self._array[1])
        elif self._index == 3:
            value = _pack_2(self._array[0], self._array[1])
            control = 2
            if reset:
                # just in case, this applies only to 3 bytes if found
                self._array[0] = self._array[2]
                self._index = 1
            num = 2
            return control, [value], num
        elif self._index == 4:
            control = 1
            num = 4
            value = _pack_4(self._array[0], self._array[1], self._array[2], self._array[3])
        else:
            raise SteimError("Error packing bits {}", self._index)
        if reset:
            self.reset()
        return control, [value], num

    def _is_full(self):
        if self._index >= len(self._array):
            return True
        return self._index * self._span >= 32

    @classmethod
    def fill(cls, control: int = None, value: int = None) -> 'Steim1Bucket':
        if control is None:
            raise ValueError('control is required!')
        if value is None:
            raise ValueError('value is required!')
        bucket = cls()
        if control == 0:
            return bucket
        elif control == 1:
            if not bucket.put(fix_sign((value >> 24) & 0xff, 8)) \
                    or not bucket.put(fix_sign((value >> 16) & 0xff, 8)) \
                    or not bucket.put(fix_sign((value >> 8) & 0xff, 8)) \
                    or not bucket.put(fix_sign(value & 0xff, 8)):
                raise ValueError
            return bucket
        elif control == 2:
            # return -(value & 0x8000) | (value & 0x7fff)
            # return [value >> 16, value & 0x7fff]
            if not bucket.put(fix_sign((value >> 16), 16)) \
                    or not bucket.put(fix_sign((value & 0x7fff), 16)):
                raise ValueError
            return bucket
        elif control == 3:
            if not bucket.put(fix_sign(value, 32)):
                raise ValueError
            return bucket
        else:
            raise SteimError(f"Invalid Steim: control value {control}")


class Steim2Bucket(SteimBucket):
    """A simple bucket data structure to pack numbers according
        to Steim 2 algorithm.  The bucket has no use outside of Steim.
        The 3 major operations for this class is put, pack and unpack.
        When packing, you get a control, values and number of packed samples.
        Control values describes how to unpack the number in accordance with the table below:
        control = 00 -> no data.
        control = 01 -> four ints that fits in 1 bytes each: -127 <= num <= 128
                  ex: 1, 1, 1, 1 [00000001 00000001 00000001 00000001]
        control = 10 -> two ints that fits in 2 bytes each: -32768 <= num <= 32767
                  ex: 1, 1 [00000000 00000001 00000000 00000001]
        control = 11 -> one int, 4 bytes -2,147,483,648 <= num <= 2,147,483,647
                  ex: 1 [00000000 00000000 00000000 00000001]
        """

    def __init__(self):
        super().__init__(7)

    def put_list(self, nums: list[int]) -> bool:
        for num in nums:
            if not self.put(num):
                return False
        return True

    def put(self, num: int) -> bool:
        if self._is_full():
            return False
        slot_size = size(num)
        if slot_size < self._span:
            slot_size = self._span

        width = slot_size * (len(self) + 1)
        if slot_size == 4:
            if width > 28:
                return False
        elif slot_size == 8:
            if width > 32:
                return False
        elif slot_size in [5, 6, 10, 15, 30]:
            if width > 30:
                return False
        else:
            raise SteimError("slotSize:{}, width:{}", slot_size, width)

        self._array[self._index] = num
        self._index += 1
        self._span = slot_size
        return True

    def pack(self, reset: bool = True) -> (int, [], int):
        if self._index == 7:
            control = 3
            value = _pack_2_7(self._array[0], self._array[1], self._array[2], self._array[3],
                              self._array[4], self._array[5], self._array[6])
            num = 7
        elif self._index == 6:
            control = 3
            value = _pack_2_6(self._array[0], self._array[1], self._array[2], self._array[3],
                              self._array[4], self._array[5])
            num = 6
        elif self._index == 5:
            control = 3
            value = _pack_2_5(self._array[0], self._array[1], self._array[2], self._array[3], self._array[4])
            num = 5
        elif self._index == 4:
            control = 1
            value = _pack_4(self._array[0], self._array[1], self._array[2], self._array[3])
            num = 4
        elif self._index == 3:
            control = 2
            value = _pack_2_3(self._array[0], self._array[1], self._array[2])
            num = 3
        elif self._index == 2:
            control = 2
            value = _pack_2(self._array[0], self._array[1])
            num = 2
        elif self._index == 1:
            control = 2
            value = _pack_2_1(self._array[0])
            num = 1
        else:
            raise SteimError("Error packing bits {}", self._index)
        if reset:
            self.reset()
        return control, [value], num

    def _is_full(self):
        if self._index >= len(self._array):
            return True
        width = self.index * self._span
        if self._span == 4:
            return width >= 28
        elif self._span == 8:
            return width >= 32
        else:
            return width >= 30

    @classmethod
    def fill(cls, control: int, value: int) -> 'Steim2Bucket':
        if control is None:
            raise ValueError('control is required!')
        if value is None:
            raise ValueError('value is required!')
        bucket = cls()

        c = (value >> 30) & 0x03
        if control == 1:
            nums = unpack_steim_2(value=value, mask=255, shift_from=24, width=8, expected_list_size=4)
            if len(nums) != 4:
                raise SteimError(
                    f'Steim2Bucket(control:{control}:{c}, [4(8bits) -255<=num<=255], value:{value}, bucket:{bucket})')
            if not bucket.put_list(nums):
                raise SteimError(
                    f'Steim2Bucket(control:{control}:{c}, [4(8bits) -255<=num<=255], list:{nums}, value:{value}, bucket:{bucket})')
        elif control == 2:
            if c == 1:
                nums = unpack_steim_2(value=value, mask=1073741823, shift_from=0, width=30, expected_list_size=1)
                if len(nums) != 1:
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [2(15bits) -32767<=num<=32767], value:{value}, list:{list}, bucket:{bucket})')
                if not bucket.put_list(nums):
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [1(30bits) -1073741823<=num<=1073741823], value:{value}, bucket:{bucket})')
            elif c == 2:
                nums = unpack_steim_2(value=value, mask=32767, shift_from=15, width=15, expected_list_size=2)
                if len(nums) != 2:
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [2(15bits) -32767<=num<=32767], value:{value}, bucket:{bucket})')
                if not bucket.put_list(nums):
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [2(15bits) -32767<=num<=32767], value:{value}, bucket:{bucket})')
            elif c == 3:
                nums = unpack_steim_2(value=value, mask=1023, shift_from=20, width=10, expected_list_size=3)
                if len(nums) != 3:
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [2(15bits) -32767<=num<=32767], value:{value}, bucket:{bucket})')
                if not bucket.put_list(nums):
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [3(10bits) -1023<=num<=1023], value:{value}, bucket:{bucket})')
            else:
                raise SteimError("Invalid control value, expected 2:1|2|3 but received 2:{}, value:{}", c, value)
        elif control == 3:
            if c == 0:
                nums = unpack_steim_2(value=value, mask=63, shift_from=24, width=6, expected_list_size=5)
                if not bucket.put_list(nums):
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [5(6bits) -31<=num<=31], value:{value}, bucket:{bucket})')
            elif c == 1:
                nums = unpack_steim_2(value=value, mask=31, shift_from=25, width=5, expected_list_size=6)
                if not bucket.put_list(nums):
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [6(5bits) -15<=num<=15], value:{value}, bucket:{bucket})')
            elif c == 2:
                nums = unpack_steim_2(value=value, mask=15, shift_from=24, width=4, expected_list_size=7)
                if not bucket.put_list(nums):
                    raise SteimError(
                        f'Steim2Bucket(control:{control}:{c}, [7(4bits) -7<=num<=7], value:{value}, bucket:{bucket})')
            else:
                raise SteimError("Invalid control value, expected 0|1|2 but received {}", c)
        else:
            raise SteimError("Invalid control value, expected 2|3 but received {}, value:{}", control, value)
        return bucket


class EncodedRecord(ABC):
    def __init__(self, encoding_format: EncodingFormat = None, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        if encoding_format is None:
            raise ValueError
        if byte_order is None:
            raise ValueError
        self._encoding_format = encoding_format
        self._byte_order = byte_order
        self._number_of_samples = 0

    @property
    def encoding_format(self) -> EncodingFormat:
        return self._encoding_format

    @property
    def byte_order(self) -> ByteOrder:
        return self._byte_order

    @property
    def number_of_samples(self) -> Optional[int]:
        return self._number_of_samples

    @abstractmethod
    def to_byte_array(self) -> bytearray:
        pass

    def __str__(self):
        return f"EncodedRecord: number_of_encoded_samples = {self.number_of_samples} "


class SteimRecord(EncodedRecord):

    def __init__(self, int_array: IntArray, encoding_format: EncodingFormat = None,
                 byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(SteimRecord, self).__init__(encoding_format=encoding_format, byte_order=byte_order)
        if int_array is None:
            raise ValueError
        self._frames: IntArray = int_array
        pair = self._frames.shape
        rows = pair[0]
        columns = rows
        if len(pair) == 1:
            rows = 1

        if len(pair) == 1:
            if columns > 16:
                rows = math.ceil(len(self._frames) / 16)
                self._frames.reshape(rows, 16)
        else:
            columns = pair[1]
            if columns != 16:
                raise ValueError()
        self._capacity = rows * columns
        self._index: int = 0
        self._number_of_samples = 0

    @property
    def shape(self) -> (int, int):
        return self._frames.shape

    def number_of_frames(self) -> int:
        return self.shape[0]

    def frame(self, index: int):
        return self._frames[index]

    @property
    def forward_integration_factor(self) -> Optional[int]:
        return self._frames[0][1]

    @forward_integration_factor.setter
    def forward_integration_factor(self, value: int) -> None:
        if value is None:
            raise ValueError
        self._frames[0][1] = value

    @property
    def reverse_integration_factor(self) -> Optional[int]:
        return self._frames[0][2]

    @reverse_integration_factor.setter
    def reverse_integration_factor(self, value: int) -> None:
        if value is None:
            raise ValueError
        self._frames[0][2] = value

    def append(self, bucket: SteimBucket) -> bool:
        if bucket is None:
            raise ValueError
        first_sample: int = bucket[0]
        last_sample: int = bucket[-1]
        control, values, number_of_samples = bucket.pack()
        if self._index == 0:
            self._frames[0][1] = first_sample
            self._index = 3

        row, column = divmod(self._index, 16)
        if column == 0:
            column = 1
            self._index += 1
        cs = ControlSequence(value=self._frames[row][0])
        cs[column] = control
        self._frames[row][0] = int(cs)
        self._frames[row][column] = values[0]
        self._index += 1
        self._number_of_samples += number_of_samples
        self.reverse_integration_factor = last_sample
        return True

    def is_full(self):
        return self._index >= self._capacity

    def to_byte_array(self) -> bytearray:
        return self._frames.to_bytes()

    def __len__(self):
        return len(self._frames)

    def __getitem__(self, item):
        return self._frames[item]

    @classmethod
    def wrap_ints(cls, steim_ints: (bytes, bytearray), encoding_format: EncodingFormat = None,
                  byte_order: ByteOrder = ByteOrder.BIG_ENDIAN) -> 'SteimRecord':
        if steim_ints is None or len(steim_ints) == 0:
            raise ValueError

        instance = cls(IntArray.wrap_ints(steim_ints, byte_order=byte_order, rows=math.ceil(len(steim_ints) / 16),
                                          columns=16), encoding_format=encoding_format,
                       byte_order=byte_order)
        instance._index = instance._capacity
        return instance

    @classmethod
    def wrap_bytes(cls, steim_bytes: (bytes, bytearray), encoding_format: EncodingFormat = None,
                   byte_order: ByteOrder = ByteOrder.BIG_ENDIAN) -> 'SteimRecord':
        if steim_bytes is None or len(steim_bytes) == 0:
            raise ValueError

        instance = cls(IntArray.wrap_bytes(steim_bytes, rows=math.ceil(len(steim_bytes) / 16),
                                           columns=16, byte_order=byte_order), encoding_format=encoding_format,
                       byte_order=byte_order)
        instance._index = instance._capacity
        return instance

    @classmethod
    def allocate(cls, number_of_frames: int, encoding_format: EncodingFormat,
                 byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        return cls(IntArray.allocate(number_of_frames, 16, byte_order), encoding_format)


class Encoder(ABC):
    def __init__(self, encoding_format: EncodingFormat, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        self.encoding_format = encoding_format
        self.byte_order = byte_order

    def byte_order(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        if not byte_order:
            raise
        return self

    @abstractmethod
    def encode(self, samples, offset: int = 0, **kwargs) -> EncodedRecord:
        pass


class Decoder:
    def __init__(self, encoding_format: EncodingFormat, byte_order: ByteOrder):
        if encoding_format is None:
            raise ValueError
        if byte_order is None:
            raise ValueError
        self._encoding_format = encoding_format
        self._byte_order = byte_order

    @property
    def encoding_format(self):
        return self._encoding_format

    @property
    def byte_order(self):
        return self._byte_order

    @abstractmethod
    def decode(self, data: bytes, **kwargs) -> array:
        pass


class SteimDecoder(Decoder, ABC):
    def __init__(self, encoding_format: EncodingFormat, byte_order: ByteOrder):
        super(SteimDecoder, self).__init__(encoding_format, byte_order)

    def decode(self, data, **kwargs) -> array:
        if data is None:
            raise ValueError
        record = SteimRecord.wrap_bytes(steim_bytes=data, encoding_format=self.encoding_format,
                                        byte_order=self.byte_order)

        expected_number_of_samples = kwargs.get('expected_number_of_samples')
        previous = kwargs.get('carry_over')
        if previous is None:
            previous = record.forward_integration_factor

        exit_loop: bool = False
        cnt: int = 0
        #nums = list()
        nums = array.array('i')
        x: int = 0
        for i in range(0, record.number_of_frames()):
            frame = record.frame(i)
            control_sequence = ControlSequence(frame[0])
            start: int = 1
            if i == 0:
                start = 3
                forward_integration_factor = frame[1]
                reverse_integration_factor = frame[2]
            for bucket_index in range(start, 16):
                control: int = control_sequence[bucket_index]
                if control == 0:
                    continue
                value = frame[bucket_index]
                deltas = SteimBucket.unpack_by_control(encoding_format=record.encoding_format, control=control,
                                                       value=value)
                # deltas = unpack(control=control, value=value)
                if len(deltas) == 0:
                    raise SteimError('fill: {}, {} {}', control, value, deltas)
                for delta in deltas:
                    num: int = previous + delta
                    if cnt == 0:
                        cnt += 1
                        if num != record.forward_integration_factor:
                            num = record.forward_integration_factor
                    nums.append(num)
                    x += 1
                    previous = num
                if expected_number_of_samples and len(nums) >= expected_number_of_samples:
                    exit_loop = True
                    break
            if exit_loop:
                break
        if expected_number_of_samples and expected_number_of_samples != len(nums):
            raise RuntimeWarning(f'{expected_number_of_samples}, {len(nums)}')
        if nums[-1] != record.reverse_integration_factor:
            raise SteimError(
                'Last sample does not match reverse_integration_factor, expected {} but received {}',
                record.reverse_integration_factor, nums[-1])
        return nums

    def decode_1(self, data: bytes, **kwargs) -> array:
        if data is None:
            raise ValueError

        record = SteimRecord.wrap_bytes(steim_bytes=data, encoding_format=self.encoding_format,
                                        byte_order=self.byte_order)

        nums = array.array('i')
        expected_number_of_samples = kwargs.get('expected_number_of_samples')
        previous = kwargs.get('carry_over')
        if previous is None:
            previous = record.forward_integration_factor

        exit_loop: bool = False
        cnt: int = 0
        for frame_idx, frame in enumerate(record):
            cs = ControlSequence(frame[0][1])
            for bucket_idx, item in enumerate(frame):
                if bucket_idx == 0:
                    continue
                if frame_idx == 0:
                    if bucket_idx < 3:
                        continue
                control, value = item
                if control == 0:
                    continue
                bucket = SteimBucket.fill(encoding_format=self.encoding_format, control=control, value=value)
                deltas = bucket.unpack()
                if len(deltas) == 0:
                    raise SteimError('fill: {}, {} {} {}', control, value, bucket, deltas)
                # print(f'forward_integration_factor:{record.forward_integration_factor}, control_sequence:{frame[0]}:{cs}, previous:{previous}, control:{control}, value:{value}  {deltas}')
                for delta in deltas:
                    num: int = previous + delta
                    if cnt == 0:
                        cnt += 1
                        if num != record.forward_integration_factor:
                            num = record.forward_integration_factor
                    nums.append(num)
                    # print(f'{len(nums)}, {num}')
                    previous = num
                if expected_number_of_samples and len(nums) >= expected_number_of_samples:
                    exit_loop = True
                    break
            if exit_loop:
                break
        if expected_number_of_samples and expected_number_of_samples != len(nums):
            raise RuntimeWarning
        if nums[-1] != record.reverse_integration_factor:
            raise SteimError('Last sample does not match reverse_integration_factor, expected {} but received {}',
                             record.reverse_integration_factor, nums[-1])
        return nums


class Steim1Decoder(SteimDecoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim1Decoder, self).__init__(EncodingFormat.STEIM_1, byte_order)


class Steim2Decoder(SteimDecoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim2Decoder, self).__init__(EncodingFormat.STEIM_2, byte_order)


class Steim3Decoder(SteimDecoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim3Decoder, self).__init__(EncodingFormat.STEIM_3, byte_order)


class SteimEncoder(Encoder, ABC):
    def __init__(self, encoding_format: EncodingFormat = EncodingFormat.STEIM_2,
                 byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(SteimEncoder, self).__init__(encoding_format, byte_order)

    def encode(self, samples, offset: int = 0, **kwargs) -> EncodedRecord:
        if not samples:
            raise ValueError
        number_of_frames = kwargs.get('number_of_frames')
        if not number_of_frames or number_of_frames < 1:
            raise ValueError

        carry_over = kwargs.get('carry_over')
        previous = 0
        if carry_over is not None:
            previous = carry_over

        record = SteimRecord.allocate(encoding_format=self.encoding_format, number_of_frames=number_of_frames,
                                      byte_order=self.byte_order)
        record.forward_integration_factor = samples[offset]
        reusable_bucket = SteimBucket.instance(self.encoding_format)
        for sample in samples:
            if record.is_full():
                break
            delta = sample - previous
            if not reusable_bucket.put(delta):
                if not record.append(reusable_bucket):
                    raise RuntimeError
                if not reusable_bucket.put(delta):
                    raise RuntimeError
            previous = sample
        if not record.is_full() and not reusable_bucket.is_empty():
            record.append(reusable_bucket)
        return record


class Steim1Encoder(SteimEncoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim1Encoder, self).__init__(EncodingFormat.STEIM_1, byte_order)


class Steim2Encoder(SteimEncoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim2Encoder, self).__init__(EncodingFormat.STEIM_2, byte_order)


class Steim3Encoder(SteimEncoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim3Encoder, self).__init__(EncodingFormat.STEIM_3, byte_order)


def get_encoder(encoding_format: EncodingFormat, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN) -> Encoder:
    if not encoding_format:
        raise ValueError
    elif encoding_format == EncodingFormat.STEIM_1:
        return Steim1Encoder(byte_order=byte_order)
    elif encoding_format == EncodingFormat.STEIM_2:
        return Steim2Encoder(byte_order=byte_order)
    elif encoding_format == EncodingFormat.STEIM_3:
        return Steim3Encoder(byte_order=byte_order)
    else:
        raise ValueError


def get_decoder(encoding_format: EncodingFormat, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN) -> Decoder:
    if not encoding_format:
        raise ValueError
    elif encoding_format == EncodingFormat.STEIM_1:
        return Steim1Decoder(byte_order=byte_order)
    elif encoding_format == EncodingFormat.STEIM_2:
        return Steim2Decoder(byte_order=byte_order)
    elif encoding_format == EncodingFormat.STEIM_3:
        return Steim3Decoder(byte_order=byte_order)
    else:
        raise ValueError


def unpack_steim_2(value: int, mask: int, shift_from: int, width: int, expected_list_size: int):
    shift: int = shift_from
    nums = list()
    max_value = 2 ** (width - 1)
    for i in range(0, expected_list_size):
        num = (value >> shift) & mask
        if num >= max_value:
            num = num - (1 << width)
        nums.append(num)
        shift -= width
    return nums


lib = pathlib.Path().absolute() / "steim.so"
steim = ctypes.CDLL(lib)

c_unpack = steim.unpack
c_unpack.restype = _ctypes.c_void_p
c_unpack.argtypes = [
    _ctypes.c_int,
    _ctypes.c_int,
    _ctypes.POINTER(_ctypes.c_int32)]

c_unpack_1 = steim.unpack_1
c_unpack_1.restype = _ctypes.c_void_p
c_unpack_1.argtypes = [
    _ctypes.c_int,
    _ctypes.POINTER(_ctypes.c_int32)]

c_unpack_2 = steim.unpack_2
c_unpack_2.restype = _ctypes.c_void_p
c_unpack_2.argtypes = [
    _ctypes.c_int,
    _ctypes.POINTER(_ctypes.c_int32)]

c_unpack_3 = steim.unpack_3
c_unpack_3.restype = _ctypes.c_void_p
c_unpack_3.argtypes = [
    _ctypes.c_int,
    _ctypes.POINTER(_ctypes.c_int32)]

c_unpack_4 = steim.unpack_4
c_unpack_4.restype = _ctypes.c_void_p
c_unpack_4.argtypes = [
    _ctypes.c_int,
    _ctypes.POINTER(_ctypes.c_int32)]

c_unpack_5 = steim.unpack_5
c_unpack_5.restype = _ctypes.c_void_p
c_unpack_5.argtypes = [
    _ctypes.c_int,
    _ctypes.POINTER(_ctypes.c_int32)]

c_unpack_6 = steim.unpack_6
c_unpack_6.restype = _ctypes.c_void_p
c_unpack_6.argtypes = [
    _ctypes.c_int,
    _ctypes.POINTER(_ctypes.c_int32)]

c_unpack_7 = steim.unpack_7
c_unpack_7.restype = _ctypes.c_void_p
c_unpack_7.argtypes = [
    _ctypes.c_int,
    _ctypes.POINTER(_ctypes.c_int32)]

c_get_control = steim.get_control
c_get_control.restype = ctypes.c_int


def get_control(value: int):
    return c_get_control(ctypes.c_int(value))


def unpack(control: int, value: int):
    res = (_ctypes.POINTER(_ctypes.c_int) * 7)
    c_unpack(_ctypes.c_int32(control), _ctypes.c_int32(value), res)
    return res


def unpack_1(value: int):
    res = (_ctypes.c_int32 * 1)()
    c_unpack_1(_ctypes.c_int32(value), res)
    return res


def unpack_2(value: int):
    res = (_ctypes.c_int32 * 2)()
    c_unpack_2(_ctypes.c_int32(value), res)
    return res


def unpack_3(value: int):
    res = (_ctypes.c_int32 * 3)()
    c_unpack_3(_ctypes.c_int32(value), res)
    return res


def unpack_4(value: int):
    res = (_ctypes.c_int32 * 4)()
    c_unpack_4(_ctypes.c_int32(value), res)
    return res


def unpack_5(value: int):
    res = (_ctypes.c_int32 * 5)()
    c_unpack_5(_ctypes.c_int32(value), res)
    return res


def unpack_6(value: int):
    res = (_ctypes.c_int32 * 6)()
    c_unpack_6(_ctypes.c_int32(value), res)
    return res


def unpack_7(value: int):
    res = (_ctypes.c_int32 * 7)()
    c_unpack_7(_ctypes.c_int32(value), res)
    return res
