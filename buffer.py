import logging as log
import struct
from enum import Enum

import array
from math import floor


class ByteOrder(str, Enum):
    LITTLE_ENDIAN = 'little-endian'
    BIG_ENDIAN = 'big-endian'


class ByteBuffer:

    def __init__(self, data: bytearray):
        if not data:
            raise ValueError
        if type(data) == bytearray:
            self._buffer = data
        elif type(data) == bytes:
            self._buffer = bytearray(data)
        else:
            raise ValueError
        self._byte_order = ByteOrder.BIG_ENDIAN
        self._position = 0

    def length(self):
        return len(self._buffer)

    def set_byte_order(self, byte_order: ByteOrder) -> 'ByteBuffer':
        self._byte_order = byte_order
        return self

    def get_byte_order(self) -> ByteOrder:
        return self._byte_order

    def position(self, position: int) -> 'ByteBuffer':
        if position < 0 or position >= len(self._buffer):
            raise ValueError(position)
        self._position = position
        return self

    def get_position(self):
        return self._position

    def get(self, signed: bool = True) -> b'':
        """

        :param signed:
        :return:
        """
        if self._position >= self.length():
            raise IndexError
        temp = self._position
        self._position += 1
        if signed:
            return struct.unpack_from('>b', self._buffer, temp)[0]
        else:
            return struct.unpack_from('>B', self._buffer, temp)[0]

    def put(self, value, signed: bool = True):
        if self._position >= self.length():
            raise IndexError(self._position)
        destination = self._position
        self._position += 1
        if signed:
            struct.pack_into('>b', self._buffer, destination, value)
        else:
            struct.pack_into('>B', self._buffer, destination, value)

    def get_int(self, signed: bool = True, index: int = None) -> int:
        log.debug(f'ByteBuffer: get_int(self, signed: bool = True, index: int = None) -> signed={signed}, index={index}')
        old_position = None
        if index is not None:
            old_position = self._position
            self._position = index
        value = None
        if self._byte_order == ByteOrder.BIG_ENDIAN:
            value = self.get_int_big(signed)
        else:
            value = self.get_int_little(signed)

        if old_position:
            self._position = old_position
        return value

    def get_int_little(self, signed: bool = True) -> int:
        if self._position + 4 > self.length():
            raise IndexError
        pos = self._position
        self._position += 4
        if signed:
            return struct.unpack_from('<i', self._buffer, pos)[0]
        else:
            return struct.unpack_from('<I', self._buffer, pos)[0]

    def get_int_big(self, signed: bool = True) -> int:
        if self._position + 4 > self.length():
            raise IndexError
        pos = self._position
        self._position += 4
        if signed:
            return struct.unpack_from('>i', self._buffer, pos)[0]
        else:
            return struct.unpack_from('>I', self._buffer, pos)[0]

    def put_int(self, value, position: int = None, signed: bool = True) -> 'ByteBuffer':
        log.debug(f'ByteBuffer: put_int(self, value, position: int = None, signed: bool = True) -> value={value}, '
                  f'position={position}, signed={signed}')
        if position is not None:
            self._position = position
        if self._byte_order == ByteOrder.BIG_ENDIAN:
            return self.put_int_big(value, signed)
        else:
            return self.put_int_little(value, signed)

    def put_int_little(self, value, signed: bool = True) -> 'ByteBuffer':
        if self._position + 4 > self.length():
            raise IndexError
        destination = self._position
        self._position += 4
        if signed:
            struct.pack_into('<i', self._buffer, destination, value)
        else:
            struct.pack_into('<I', self._buffer, destination, value)
        return self

    def put_int_big(self, value, signed: bool = True) -> 'Buffer':
        if self._position >= self.length():
            raise IndexError(self._position + 4)
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
        if start is None or start < 0 or start > self.length():
            raise IndexError
        if end is None:
            pass
        else:
            if end < start:
                raise IndexError
            if end > self.length():
                raise IndexError

    def available(self) -> int:
        return len(self._buffer) - self._position

    def array(self) -> []:
        return self._buffer

    def int_array(self) -> []:
        for i in range(0, floor(len(self) / 4)):
            yield self.get_int()

    def __iter__(self):
        for val in self.array():
            yield val

    def __len__(self):
        return len(self._buffer)

    @staticmethod
    def allocate(n):
        if n < 0:
            raise ValueError(n)
        return ByteBuffer(bytearray(n))

    @staticmethod
    def wrap(data: [], offset: int = 0, length: int = None):
        if length is None:
            length = len(data) - offset
        return ByteBuffer(data)


class IntBuffer:
    def __init__(self, capacity: int, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        if capacity is None:
            raise ValueError(capacity)
        if capacity < 1:
            raise ValueError(capacity)
        self._capacity = capacity
        self._position = 0
        self._byte_buffer = ByteBuffer.allocate(self.capacity * 4).set_byte_order(byte_order)

    @property
    def byte_order(self) -> ByteOrder:
        return self._byte_buffer.get_byte_order()

    @property
    def capacity(self) -> int:
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        self._capacity = value

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, value):
        if value is None:
            raise ValueError(value)
        if value < 0 or value >= self._capacity:
            raise IndexError(value)
        self._position = value
        self._byte_buffer.position(self._position * 4)

    @property
    def remaining(self) -> int:
        return self._capacity - self._position

    def put(self, value: int, index: int = None):
        log.debug(f'IntBuffer: put(self, value: int, index: int = None) -> value={value}, index={index}')
        if value is None:
            raise ValueError
        if index is None:
            self._byte_buffer.put_int(value)
            self._position += 1
        else:
            if index < 0 or index >= self._capacity:
                raise IndexError(index)
            # old_position = self._byte_buffer.get_position()
            # self._byte_buffer.position(index * 4)
            self._byte_buffer.put_int(value=value, position=index * 4)
            # self._byte_buffer.position(old_position)

    def is_full(self) -> bool:
        return self._position >= self._capacity

    def is_empty(self) -> bool:
        return self._position == 0

    def __getitem__(self, item):
        log.debug(f'IntBuffer: __getitem__(self, item) -> item={item}')
        if item is None:
            return self._byte_buffer.get_int()
        else:
            return self._byte_buffer.get_int(index=item*4)

    def __str__(self):
        return " ".join(str(x) for x in self.to_array())

    def to_array(self):
        arr = array.array('i')
        for i in range(0, self._capacity):
            arr.append(self[i])
        return arr

    def to_byte_array(self):
        return self._byte_buffer.array()

    @staticmethod
    def allocate(capacity: int, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN) -> 'IntBuffer':
        return IntBuffer(capacity, byte_order)
