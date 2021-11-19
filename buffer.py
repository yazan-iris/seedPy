import logging as log
import struct
import sys
from enum import Enum
from typing import Union, Sequence, overload, List

import array
import numpy
from math import floor

st_big_signed = struct.Struct(">di")


class ByteOrder(str, Enum):
    LITTLE_ENDIAN = 'little'
    BIG_ENDIAN = 'big'


class ByteBuffer(Sequence):

    @overload
    def __init__(self, capacity: int = None, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        ...

    @overload
    def __init__(self, values: Union[bytearray, bytes] = None, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN,
                 offset: int = 0,
                 length: int = None):
        ...

    def __init__(self, capacity: int = None, values: Union[bytearray, bytes] = None,
                 byte_order: ByteOrder = ByteOrder.BIG_ENDIAN, offset: int = 0,
                 length: int = None):
        if byte_order is None:
            raise ValueError
        if capacity is not None:
            self._buffer = bytearray(b'\x00') * capacity
            self._position: int = 0
        else:
            if values is None:
                raise ValueError
            if byte_order is None:
                raise ValueError
            if type(values) == bytearray:
                self._buffer = values
            elif type(values) == bytes:
                self._buffer = bytearray(values)
                self._buffer = bytearray(values)
            elif type(values) == list:
                self._buffer = bytearray()
                for num in values:
                    self._buffer.extend(
                        num.to_bytes(4, byteorder='big' if byte_order == ByteOrder.BIG_ENDIAN else 'little'))
                    # int.from_bytes(num, byteorder='big' if byte_order == ByteOrder.BIG_ENDIAN else 'little'))
            else:
                raise ValueError(type(values))
            self._position: int = len(self._buffer)
        self._byte_order = byte_order
        self._capacity = len(self._buffer)

    @property
    def byte_order(self):
        return self._byte_order

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, new_position: int):
        if new_position < 0 or new_position >= len(self._buffer):
            raise ValueError(new_position)
        self._position = new_position

    @property
    def remaining(self) -> int:
        return self._capacity - self._position

    def __len__(self):
        return self.capacity

    def __getitem__(self, item):
        return self._buffer[item]

    def __setitem__(self, key, value):
        self._buffer[key] = value
        if self._position <= key:
            self._position = key + 1

    def __str__(self):
        return str(self.to_byte_array())

    def get(self, signed: bool = True) -> b'':
        """

        :param signed:
        :return:
        """
        if self._position >= self._capacity:
            raise IndexError
        temp = self._position
        self._position += 1
        if signed:
            return struct.unpack_from('>b', self._buffer, temp)[0]
        else:
            return struct.unpack_from('>B', self._buffer, temp)[0]

    def put(self, value, signed: bool = True) -> None:
        """
        put the value at the current index and advance the index by one
        :param value:
        :param signed:
        :return: None
        """
        if self._position >= len(self):
            raise IndexError(self._position)
        destination = self._position
        if signed:
            struct.pack_into('>b', self._buffer, destination, value)
        else:
            struct.pack_into('>B', self._buffer, destination, value)
        self._position += 1

    def get_int(self, signed: bool = True, index: int = None) -> int:
        old_position = None
        if index is not None:
            old_position = self._position
            self._position = index
        if self._byte_order == ByteOrder.BIG_ENDIAN:
            value = self.get_int_big(signed)
        else:
            value = self.get_int_little(signed)

        if old_position:
            self._position = old_position
        return value

    def get_int_little(self, signed: bool = True) -> int:
        if self._position + 4 > self.capacity:
            raise IndexError
        pos = self._position
        self._position += 4
        if signed:
            # return struct.unpack_from('<i', self._buffer, pos)[0]
            return st_big_signed.unpack_from(self._buffer, pos)[0]
        else:
            return struct.unpack_from('<I', self._buffer, pos)[0]

    def get_int_big(self, signed: bool = True) -> int:
        if self._position + 4 > self.capacity:
            raise IndexError
        pos = self._position
        if signed:
            temp: int = struct.unpack_from('>i', self._buffer, pos)[0]
            # temp: int = st_big_signed.unpack_from(self._buffer, pos)[0]
        else:
            temp: int = struct.unpack_from('>I', self._buffer, pos)[0]
        self._position += 4
        return temp

    def put_int(self, value, position: int = None, signed: bool = True) -> 'ByteBuffer':
        log.debug(f'ByteBuffer: put_int(self, value, position: int = None, signed: bool = True) -> value={value}, '
                  f'position={position}, signed={signed}')

        old_position: int = None
        if position is not None:
            old_position = self._position
            self._position = position
        if self._byte_order == ByteOrder.BIG_ENDIAN:
            self.put_int_big(value, signed)
        else:
            self.put_int_little(value, signed)
        if old_position is not None:
            self._position = old_position
        return self

    def put_int_little(self, value, signed: bool = True) -> 'ByteBuffer':
        if self._position + 4 > self.capacity:
            raise IndexError
        destination = self._position
        if signed:
            struct.pack_into('<i', self._buffer, destination, value)
        else:
            struct.pack_into('<I', self._buffer, destination, value)
        self._position += 4
        return self

    def put_int_big(self, value, signed: bool = True) -> 'ByteBuffer':
        if self._position >= len(self):
            raise IndexError(self._position)
        destination = self._position
        self._position += 4
        if signed:
            struct.pack_into('>i', self._buffer, destination, value)
        else:
            struct.pack_into('>I', self._buffer, destination, value)
        return self

    def unpack_int(self):
        end = self._position + 4
        self._check_bounds(self._position, end)
        tup = struct.unpack('{}bbbb'.format('<' if self._byte_order is ByteOrder.LITTLE_ENDIAN else '>'),
                            self._buffer[self._position:end])
        self._position += 4
        return tup

    def unpack_short(self):
        end = self._position + 4
        tup = struct.unpack('{}hh'.format('<' if self._byte_order is ByteOrder.LITTLE_ENDIAN else '>'),
                            self._buffer[self._position:end])
        self._position += 4
        return tup

    def read(self) -> int:
        return self.read_little() if self._byte_order is ByteOrder.LITTLE_ENDIAN else self.read_big()

    def read_little(self) -> int:
        self._check_bounds(self._position, self._position + 4)
        val = int.from_bytes(self._buffer[self._position:self._position + 4], 'little', True)
        self._position += 4
        return val

    def read_big(self) -> int:
        self._check_bounds(self._position, self._position + 4)
        val = int.from_bytes(self._buffer[self._position:self._position + 4], byteorder='big', signed=True)
        self._position += 4
        return val

    def _fix_sign(self, value: int, width: int):
        max = 2 ** (width - 1)
        if value >= max:
            value = value - 2 ** width
            return value

        return value

    def _check_bounds(self, start: int, end: int = None):
        if self._buffer is None:
            raise IndexError
        if start is None or start < 0 or start > self.capacity:
            raise IndexError
        if end is None:
            pass
        else:
            if end < start:
                raise IndexError
            if end > self.capacity:
                raise IndexError

    def to_byte_array(self) -> bytearray:
        return self._buffer

    def to_int_array(self) -> []:
        if self.byte_order == ByteOrder.BIG_ENDIAN:
            fmt = ">%di" % (len(self._buffer) // 4)
        else:
            fmt = "<%di" % (len(self._buffer) // 4)
        # return list(struct.unpack(fmt, self._buffer))
        return list(st_big_signed.unpack(self._buffer))

    @classmethod
    def wrap_bytes(cls, values: [], byte_order: ByteOrder = ByteOrder.BIG_ENDIAN, offset: int = 0, length: int = None):
        if offset < 0:
            raise ValueError
        if values is None:
            raise ValueError
        if length is None:
            length = len(values) - offset
        if isinstance(values, (bytes, bytearray)):
            return ByteBuffer(values=values, byte_order=byte_order, offset=offset, length=length)
        else:
            return ByteBuffer(values=bytes(values), byte_order=byte_order, offset=offset, length=length)

    @classmethod
    def wrap_ints(cls, values: [], byte_order: ByteOrder = ByteOrder.BIG_ENDIAN, offset: int = 0, length: int = None):
        if offset < 0:
            raise ValueError
        if values is None:
            raise ValueError
        if length is None:
            length = len(values) - offset
        instance = ByteBuffer(byte_order=byte_order)
        for value in values:
            instance.put_int(value)
        return instance

    @classmethod
    def allocate(cls, capacity: int, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        if not capacity or capacity < 1:
            raise ValueError
        if byte_order is None:
            raise ValueError
        return cls(capacity=capacity, byte_order=byte_order)


class IntBuffer(Sequence):

    def __init__(self, capacity: int = None, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(IntBuffer, self).__init__()
        if capacity is None or capacity < 1:
            raise ValueError
        if byte_order is None:
            raise ValueError
        # self._byte_buffer = ByteBuffer(capacity=capacity * 4, byte_order=byte_order)
        self._buffer = array.array('i', [0]) * capacity
        if byte_order.value != sys.byteorder:
            self._buffer.byteswap()

        self._capacity = capacity  # floor(self._buffer.capacity / 4)
        self._byte_order = byte_order
        self._position = 0

    @property
    def byte_order(self) -> ByteOrder:
        return self._byte_order

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def position(self) -> int:
        return self._position

    @property
    def remaining(self) -> int:
        return self._capacity - self._position

    def put(self, value: (int, list), index: int = None):
        if value is None:
            raise ValueError
        if index is None:
            if type(value) == int:
                self._buffer[self._position] = value
                self._position += 1
            elif type(value) == list:
                for val in value:
                    self._buffer[self._position] = val
                    self._position += 1
            else:
                raise ValueError(type(value))
        else:
            if type(value) == int:
                self._buffer[index] = value
            elif type(value) == list:
                for val in value:
                    self._buffer[index] = val
                    index += 1
            else:
                raise ValueError(type(value))

    def __len__(self):
        return self._capacity

    def __getitem__(self, item):
        return self._buffer[item]

    def __setitem__(self, key, value):
        if key is None or value is None:
            raise ValueError
        if key < 0 or key >= self.capacity:
            raise IndexError(key)
        self._buffer[key] = value

    def __str__(self):
        return "IntBuffer(" + ", ".join(str(x) for x in self) + ")"

    def to_byte_array(self) -> bytearray:
        return bytearray(self._buffer.tobytes())

    @classmethod
    def wrap_ints(cls, values: list, byte_order: ByteOrder = None):
        instance = cls(capacity=len(values), byte_order=byte_order)
        instance._buffer = array.array('i', values)
        return instance

    @classmethod
    def wrap_bytes(cls, values: Union[bytes, bytearray], byte_order: ByteOrder = None):
        if values is None:
            raise ValueError
        length = len(values)
        if length == 0 or length % 4 != 0:
            raise ValueError
        if byte_order is None:
            raise ValueError
        instance = cls(capacity=length, byte_order=byte_order)

        for i in range(0, length, 4):
            num: [] = values[i:i + 4]
            instance.put(
                int.from_bytes(num, byteorder='big' if byte_order == ByteOrder.BIG_ENDIAN else 'little'))
        return instance


class IntArray(Sequence):
    def __init__(self, int_array, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(IntArray, self).__init__()
        if int_array is None:
            raise ValueError
        self._int_array: numpy.ndarray = int_array
        self._index: int = 0

    @property
    def array(self):
        return self._int_array

    @property
    def shape(self) -> (int, int):
        return self._int_array.shape

    def __getitem__(self, item):
        return self._int_array[item]

    def __setitem__(self, key, value):
        if value is None:
            raise ValueError
        if isinstance(value, int):
            self._int_array[key] = numpy.int32(value)
        elif isinstance(value, numpy.int32):
            self._int_array[key] = value
        else:
            raise ValueError(f'type: {type(value)}, value: {value}')

    def __len__(self):
        return len(self._int_array)

    def append(self, value):
        self._int_array[self._index] = value
        self._index += 1

    def reshape(self, rows: int, columns: int):
        self._int_array = self._int_array.reshape(rows, columns)

    def to_bytes(self, order=None):
        if order:
            return self._int_array.tobytes(order=order)
        else:
            return self._int_array.tobytes()

    @classmethod
    def wrap_bytes(cls, values: (bytes, bytearray),
                   byte_order: ByteOrder = ByteOrder.BIG_ENDIAN) -> 'IntArray':
        if values is None or len(values) == 0:
            raise ValueError
        int_array = numpy.frombuffer(values, dtype='>i' if byte_order == ByteOrder.BIG_ENDIAN else '<i')
        return cls(int_array, byte_order=byte_order)

    @classmethod
    def allocate(cls, rows: int, columns: int,
                 byte_order: ByteOrder = ByteOrder.BIG_ENDIAN) -> 'IntArray':
        return cls(numpy.zeros((rows, columns), dtype='>i' if byte_order == ByteOrder.BIG_ENDIAN else '<i'),
                   byte_order=byte_order)


