import logging as log

import array

from Codec.Steim import ControlSequence
from buffer import IntBuffer, ByteOrder


class SteimFrame:

    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        self._control_sequence = ControlSequence()
        self._buffer = IntBuffer.allocate(capacity=16, byte_order=byte_order)

    def control(self) -> int:
        if self.position == 0:
            return None
        return self[0]

    def append(self, control: int, values: []) -> bool:
        if control is None:
            raise ValueError(f'control is required and cannot be None!')
        if values is None or len(values) == 0:
            raise ValueError(f'values is required and cannot be None or empty!')
        if self.is_full():
            return False
        self._control_sequence.set(index=self.position, value=control)
        for value in values:
            self._buffer.put(value)
        return True

    def is_full(self) -> bool:
        return self._buffer.is_full()

    def is_empty(self) -> bool:
        return self._buffer.is_empty()

    @property
    def byte_order(self) -> ByteOrder:
        return self._buffer.byte_order

    @property
    def position(self) -> int:
        """Return the number of ints this frame takes.
        Remember a Steim frame reserve slot 0 for control sequences, so
        capacity is always total capacity=16 - 1.
        """
        return self._buffer.position + 1

    @property
    def capacity(self) -> int:
        """Return the number of ints this frame takes.
        Remember a Steim frame reserve slot 0 for control sequences, so
        capacity is always total capacity=16 - 1.
        """
        return self._buffer.capacity - 1

    @property
    def remaining(self) -> int:
        """Return the remaining empty slots count as int in the array.
         Remember a Steim frame reserve slot 0 for control sequences, so
         the remaining slots count is always (capacity - position - 1).
         """
        return self._buffer.remaining - 1

    def to_array(self):
        return self._buffer.to_array()

    def __getitem__(self, item):
        if item is None:
            raise ValueError
        if item < 0 or item >= self._buffer.capacity:
            raise IndexError
        return self._buffer[item]

    def __str__(self):
        return " ".join(str(x) for x in self.to_array())


class SteimHeaderFrame(SteimFrame):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(SteimHeaderFrame, self).__init__(byte_order)

    @property
    def forward_integration_factor(self) -> int:
        log.debug(f'forward_integration_factor(self)')
        return self._buffer[1]

    @forward_integration_factor.setter
    def forward_integration_factor(self, value: int):
        self._buffer.put(value=value, index=1)

    @property
    def reverse_integration_factor(self) -> int:
        log.debug(f'reverse_integration_factor(self)')
        return self._buffer[2]

    @reverse_integration_factor.setter
    def reverse_integration_factor(self, value: int) -> int:
        self._buffer.put(value=value, index=2)

    @property
    def capacity(self) -> int:
        """Return the number of ints this frame takes.
        Remember a Steim header frame reserve slots:
         0 for control sequences
         1 for forward_integration_factor
         2 for reverse_integration_factor
         so capacity is always total capacity=16 - 3.
        """
        return self._buffer.capacity - 3

    @property
    def remaining(self) -> int:
        """Return the remaining empty slots count as int in the array.
         0 for control sequences
         1 for forward_integration_factor
         2 for reverse_integration_factor
         so capacity is always total capacity=16 - 3.
         the remaining slots count is always (capacity - position - 3).
         """
        return self._buffer.remaining - 3

    @property
    def position(self) -> int:
        """Return the number of ints this frame takes.
        Remember a Steim frame reserve slot 0 for control sequences, so
        capacity is always total capacity=16 - 1.
        """
        return self._buffer.position + 3
