from collections import Sequence

from Codec.Steim.errors import SteimError


class ControlSequence:
    def __init__(self, value: int = 0):
        self._index = 0
        self.value = value
        self.__length = 16

    def append(self, value: int):
        if value is None:
            raise ValueError
        if self._index >= self.__length:
            raise IndexError
        self[self._index] = value
        self._index += 1

    def __on(self, shift: int):
        self.value |= 1 << shift

    def __off(self, shift: int):
        self.value &= ~(1 << shift)

    def is_empty(self):
        return self.value == 0

    def __int__(self):
        return self.value

    def __invert__(self):
        return ControlSequence(~self.value)

    def __eq__(self, other):
        try:
            return self.value == other.value
        except Exception:
            return self.value == other

    def __repr__(self):
        return str(self)

    def __iter__(self):
        """Iterates over the values in the controlsequence."""
        # [1::2]
        for idx in range(16):
            yield (self.value >> (30 - idx * 2)) & 0x03

    def __getitem__(self, subscript):
        if subscript is None:
            raise ValueError
        if isinstance(subscript, slice):
            result = []
            print(subscript.step)
            if subscript.stop is not None and subscript.stop > len(self):
                raise IndexError
            for i in range(subscript.start if subscript.start is not None else 0,
                           subscript.stop if not None else len(self),
                           subscript.step if subscript.step is not None else 1):
                result.append((self.value >> (30 - i * 2)) & 0x03)
            return result
        else:
            return (self.value >> (30 - subscript * 2)) & 0x03

    def __setitem__(self, key, value):
        if key is None:
            raise ValueError
        if value is None:
            raise ValueError

        if key < 0 or key > 15:
            raise IndexError
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
            raise SteimError("Invalid control value {}", value)

    def __len__(self):
        """Returns the length of the bitset."""
        return self.__length

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

    @classmethod
    def from_binary_sequence(cls, sequence):
        if sequence is None:
            raise ValueError
        if not isinstance(sequence, Sequence):
            raise ValueError
        if len(sequence) > 32:
            raise ValueError
        n = 0
        for index, value in enumerate(sequence):
            n += 2 ** index * bool(int(value))
        return ControlSequence(value=n)
