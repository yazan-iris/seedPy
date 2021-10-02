from abc import ABC, abstractmethod

from Codec import EncodingFormat
from Codec.Steim.errors import SteimError


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


class SteimBucket(ABC):
    def __init__(self, capacity: int):
        self._array = [0] * capacity
        self._index = 0
        self._span = 0
        self.__totalSize = 0

    def is_empty(self) -> bool:
        return self._index == 0

    def reset(self):
        self._index = 0
        self.__totalSize = 0

    def clear(self):
        self.reset()
        self._array = [None] * len(self._array)

    def index(self):
        return self._index

    def size(self):
        return self.index()

    @abstractmethod
    def is_full(self):
        raise NotImplemented

    @abstractmethod
    def put(self, num: int):
        pass

    @abstractmethod
    def pack(self, reset: bool = True) -> (int, [], int):
        raise NotImplemented

    @abstractmethod
    def unpack(self, control: int, encoded: int) -> []:
        raise NotImplemented

    @staticmethod
    def instance(encoding_format: EncodingFormat, control: int = None, value: int = None):
        if EncodingFormat.STEIM_1 == encoding_format:
            return Steim1Bucket(control, value)
        elif EncodingFormat.STEIM_2 == encoding_format:
            return Steim2Bucket(control, value)
        else:
            raise ValueError


class Steim1Bucket(SteimBucket):
    def __init__(self, control: int = None, num: int = None):
        super().__init__(4)
        if control is not None and num is not None:
            values = self.unpack(control, num)
            for value in values:
                if not self.put(value):
                    raise SteimError
        else:
            if control or num:
                raise ValueError

    def put(self, num: int) -> bool:
        if self.is_full():
            return False
        slot_size = 32
        if 127 >= num >= -128:
            slot_size = 8
        elif 32767 >= num >= -32768:
            slot_size = 16

        if slot_size < self._span:
            slot_size = self._span

        if slot_size * (self.size() + 1) > 32:
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

    def unpack(self, control: int = None, value: int = None) -> []:
        if control is None and value is None:
            control, values, num = self.pack()
            if values is None:
                raise SteimError
            value = values[0]
        if control is None:
            raise ValueError
        if value is None:
            raise ValueError
        if control == 0:
            return []
        elif control == 1:
            # return num.to_bytes(4, 'little')
            return [(value >> 24) & 0xff, (value >> 16) & 0xff, (value >> 8) & 0xff, (value & 0xff)]
        elif control == 2:
            # return -(value & 0x8000) | (value & 0x7fff)
            return [value >> 16, value & 0x7fff]
        elif control == 3:
            return [value]
        else:
            raise SteimError("Invalid Steim: control value " + control)

    def is_full(self):
        if self._index >= len(self._array):
            return True
        return self._index * self._span >= 32


class Steim2Bucket(SteimBucket):
    def __init__(self, control: int = None, num: int = None):
        super().__init__(7)
        if control is not None and num is not None:
            values = self.unpack(control, num)
            for value in values:
                if not self.put(value):
                    raise SteimError
        else:
            if control or num:
                raise ValueError

    def put(self, num: int) -> bool:
        if self.is_full():
            return False

        slot_size = size(num)
        if slot_size < self._span:
            slot_size = self._span

        width = slot_size * (self.size() + 1)
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

    def unpack(self, control: int, encoded: int) -> []:
        if control is None:
            packed_integer = self.pack()
            control = packed_integer.control
            encoded = packed_integer.values[0]

        c = (encoded >> 30) & 0x03
        if control == 1:
            pass
        elif control == 2:
            pass
        elif control == 3:
            pass
        else:
            raise SteimError("Invalid control value, expected 2|3 but received {}", control)

    def is_full(self):
        if self._index >= len(self._array):
            return True
        width = self.size() * self._span
        if self._span == 4:
            return width >= 28
        elif self._span == 8:
            return width >= 32
        else:
            return width >= 30
