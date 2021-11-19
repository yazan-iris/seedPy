import datetime
import re
import struct
from abc import ABC
from typing import Optional

from array import array

__version__ = "1.0.0"

import math

from buffer import ByteOrder
from codec import EncodingFormat


class DataHeader:
    def __init__(self, sequence_number: int = 0, record_type=None, station_identifier_code=None,
                 location_identifier=None,
                 channel_identifier=None,
                 network_code=None, record_start_time=None, number_of_samples=None, sample_rate_factor=None,
                 sample_rate_multiplier=None, activity_flags=None, io_and_clock_flags=None, data_quality_flags=None,
                 number_of_blockettes_that_follow=None, time_correction=None, beginning_of_data=None,
                 first_blockette=0):
        self.sequence_number = sequence_number
        self.record_type = record_type
        self.station_identifier_code = station_identifier_code
        self.location_identifier = location_identifier
        self.channel_identifier = channel_identifier
        self.network_code = network_code
        self.record_start_time = record_start_time
        self.number_of_samples = number_of_samples
        self.sample_rate_factor = sample_rate_factor
        self.sample_rate_multiplier = sample_rate_multiplier
        self.activity_flags = activity_flags
        self.io_and_clock_flags = io_and_clock_flags
        self.data_quality_flags = data_quality_flags
        self.number_of_blockettes_that_follow = number_of_blockettes_that_follow
        self.time_correction = time_correction
        self.beginning_of_data = beginning_of_data
        self.first_blockette = first_blockette
        self.byte_order = ByteOrder.BIG_ENDIAN

    def __str__(self) -> str:
        return 'sequence number:{}, record type:{}, ByteOrder: {}, ' \
               'station_identifier_code:{}, ' \
               'location_identifier:{}, ' \
               'channel_identifier:{}, ' \
               'network_code:{}, ' \
               'record_start_time:{},' \
               'number_of_samples:{}, ' \
               'sample_rate_factor:{}, ' \
               'sample_rate_multiplier:{}, ' \
               'activity_flags:{}, ' \
               'io_and_clock_flags:{}, ' \
               'data_quality_flags:{}, ' \
               'number_of_blockettes_that_follow:{}, ' \
               'time_correction:{}, ' \
               'beginning_of_data:{}, ' \
               'first_blockette:{}'.format(self.sequence_number,
                                           self.record_type,
                                           self.byte_order,
                                           self.station_identifier_code,
                                           self.location_identifier,
                                           self.channel_identifier,
                                           self.network_code,
                                           self.record_start_time,
                                           self.number_of_samples,
                                           self.sample_rate_factor,
                                           self.sample_rate_multiplier,
                                           self.activity_flags,
                                           self.io_and_clock_flags,
                                           self.data_quality_flags,
                                           self.number_of_blockettes_that_follow,
                                           self.time_correction,
                                           self.beginning_of_data,
                                           self.first_blockette)

    @staticmethod
    def from_bytes(s_bytes: bytes, byte_order: ByteOrder = None) -> "DataHeader":
        if s_bytes is None:
            raise ValueError
        if not isinstance(s_bytes, bytes):
            raise ValueError
        if len(s_bytes) < 48:
            raise ValueError
        dh = DataHeader()
        dh.sequence_number = s_bytes[0:6].decode('ascii')
        dh.record_type = s_bytes[6:7].decode('ascii')
        dh.station_identifier_code = s_bytes[8:13].decode('ascii').strip()
        dh.location_identifier = s_bytes[13:15].decode('ascii')
        dh.channel_identifier = s_bytes[15:18].decode('ascii').strip()
        dh.network_code = s_bytes[18:20].decode('ascii').strip()

        val = s_bytes[20:30]

        if byte_order is None:
            year, day, hour, minute, second, unused, fraction = struct.unpack('>hhbbbbh', val)
            min = 1900
            max = 2600
            if min < year < max:
                dh.byte_order = ByteOrder.BIG_ENDIAN
            else:
                year, day, hour, minute, second, unused, fraction = struct.unpack('<hhbbbbh', val)
                if min < year < max:
                    dh.byte_order = ByteOrder.LITTLE_ENDIAN
                else:
                    raise ValueError
        else:
            dh.byte_order = byte_order
            if byte_order is ByteOrder.BIG_ENDIAN:
                year, day, hour, minute, second, unused, fraction = struct.unpack('>hhbbbbh', val)
            else:
                year, day, hour, minute, second, unused, fraction = struct.unpack('<hhbbbbh', val)
        start_time = datetime.datetime(year, 1, 1, hour, minute, second)
        start_time += datetime.timedelta(days=day)
        dh.record_start_time = start_time
        if dh.byte_order is ByteOrder.BIG_ENDIAN:
            dh.number_of_samples, dh.sample_rate_factor, dh.sample_rate_multiplier, dh.activity_flags, dh.io_and_clock_flags, \
            dh.data_quality_flags, dh.number_of_blockettes_that_follow, dh.time_correction, dh.beginning_of_data, \
            dh.first_blockette = struct.unpack_from('>hhhbbbbihh', s_bytes[30:49])
        else:
            dh.number_of_samples, dh.sample_rate_factor, dh.sample_rate_multiplier, dh.activity_flags, dh.io_and_clock_flags, \
            dh.data_quality_flags, dh.number_of_blockettes_that_follow, dh.time_correction, dh.beginning_of_data, \
            dh.first_blockette = struct.unpack_from('<hhhbbbbihh', s_bytes[30:49])
        return dh


class SeedObject(ABC):
    def __init__(self) -> None:
        if type(self) is SeedObject:
            raise Exception('SeedObject is an abstract class and cannot be instantiated directly')


class Blockette(SeedObject):
    def __init__(self, b_type: int, size: int = None):
        super().__init__()
        if type(self) is Blockette:
            raise Exception('Blockette is an abstract class and cannot be instantiated directly')
        self._b_type = b_type

    def get_type(self):
        return self._b_type

    def get_metadata(self):
        return self.__dataclass_fields__

    def describe(self, attribute_name):
        if attribute_name is None:
            raise ValueError
        return self.__dataclass_fields__[attribute_name]

    def __str__(self) -> str:
        return None


class DataBlockette(Blockette, ABC):

    def __init__(self, b_type: int, size: int = 0, next_blockette_byte_number=0) -> None:
        Blockette.__init__(self, b_type, size)
        self.next_blockette_byte_number = next_blockette_byte_number
        self._size = size


class B100(DataBlockette):
    def __init__(self, next_blockette_byte_number: int = 0,
                 actual_sample_rate=None
                 , flags=None
                 , reserved_byte=None
                 ) -> None:
        super().__init__(100, 12, next_blockette_byte_number)
        self.actual_sample_rate = actual_sample_rate
        self.flags = flags
        self.reserved_byte = reserved_byte

    def validate(self):
        pass


class B1000(DataBlockette):

    def __init__(self, next_blockette_byte_number: int = 0,
                 encoding_format=None
                 , word_order=None
                 , data_record_length=None
                 , reserved=None
                 ) -> None:
        super().__init__(1000, 8, next_blockette_byte_number)
        if isinstance(encoding_format, EncodingFormat):
            self.encoding_format = encoding_format
        elif isinstance(encoding_format, int):
            self.encoding_format = EncodingFormat(encoding_format)

        self.word_order = word_order
        self.data_record_length = data_record_length
        self.reserved = reserved

    def validate(self):
        pass

    def __str__(self):
        return 'type:{}, next_blockette_byte_number:{}, encoding_format:{}, word_order:{},' \
               ' data_record_length:{}, reserved:{}'.format(self._b_type, self.next_blockette_byte_number,
                                                            self.encoding_format, self.word_order,
                                                            self.data_record_length, self.reserved)

    @staticmethod
    def size() -> (int, int):
        return 8, 8


class B1001(DataBlockette):
    def __init__(self, next_blockette_byte_number: int = 0,
                 timing_quality=None
                 , microseconds=None
                 , reserved=None
                 , frame_count=None
                 ) -> None:
        super().__init__(1001, 8, next_blockette_byte_number)
        self.timing_quality = timing_quality
        self.microseconds = microseconds
        self.reserved = reserved
        self.frame_count = frame_count

    def __str__(self):
        return 'type:{}, next_blockette_byte_number:{}, timing_quality:{}, microseconds:{},' \
               ' reserved:{}, frame_count:{}'.format(self._b_type, self.next_blockette_byte_number,
                                                     self.timing_quality, self.microseconds,
                                                     self.reserved, self.frame_count)

    def validate(self):
        pass


class DataRecord:
    def __init__(self, header: DataHeader):
        self._header = header
        self._blockettes = dict()
        self._data: bytearray = None

    @property
    def header(self) -> DataHeader:
        return self._header

    @property
    def network_code(self) -> Optional[str]:
        if self._header:
            return self._header.network_code
        return None

    @property
    def station_code(self) -> Optional[str]:
        if self._header:
            return self._header.station_identifier_code
        return None

    @property
    def channel_location_code(self) -> Optional[str]:
        if self._header:
            return self._header.location_identifier
        return None

    @property
    def channel_code(self) -> Optional[str]:
        if self._header:
            return self._header.channel_identifier
        return None

    @property
    def record_type(self):
        return self._header.record_type

    @property
    def byte_order(self) -> Optional[ByteOrder]:
        if self.header is None:
            return None
        return self.header.byte_order

    @property
    def encoding_format(self) -> Optional[EncodingFormat]:
        b1000 = self.blockette(1000)
        if b1000 is None:
            return None
        if isinstance(b1000, B1000):
            return b1000.encoding_format
        else:
            raise RuntimeError

    @property
    def number_of_samples(self) -> int:
        if self.header is None:
            return 0
        return self.header.number_of_samples

    @property
    def actual_sample_rate(self) -> Optional[int]:
        if 100 in self.blockettes:
            b100 = self.blockette(100)
            if not b100:
                return None
            if not isinstance(b100, B100):
                raise RuntimeError
            return b100.actual_sample_rate
        else:
            return None

    @property
    def sample_rate_factor(self) -> Optional[int]:
        if self.header is None:
            return 0
        return self.header.sample_rate_factor

    @property
    def sample_rate(self) -> [int]:
        sample_rate = self.actual_sample_rate
        if sample_rate is None:
            sample_rate = self.calculate_sample_rate()
        return sample_rate

    @property
    def sample_rate_multiplier(self) -> Optional[int]:
        if self.header is None:
            return 0
        return self.header.sample_rate_multiplier

    @property
    def start_time(self) -> Optional[datetime.datetime]:
        if self.header is None:
            return None
        return self.header.record_start_time

    @property
    def b1000(self) -> Optional[B1000]:
        b1000 = self.blockette(1000)
        if b1000 is None:
            return None
        if isinstance(b1000, B1000):
            return b1000
        else:
            raise RuntimeError

    @property
    def b100(self) -> Optional[B100]:
        b100 = self.blockette(100)
        if b100 is None:
            return None
        if isinstance(b100, B100):
            return b100
        else:
            raise RuntimeError

    @property
    def blockettes(self) -> list[DataBlockette]:
        return list(self._blockettes.values())

    def blockette(self, number: int) -> Optional[DataBlockette]:
        if not self._blockettes or len(self._blockettes) == 0:
            return None
        return self._blockettes[number]

    @property
    def data(self) -> bytearray:
        return self._data

    @data.setter
    def data(self, data: array):
        self._data = data

    def to_int_array(self) -> list[int]:
        struct.unpack_from()
        arr = list()
        if self._data is None:
            return arr
        for i in range(0, len(self._data), 4):
            arr.append(int.from_bytes(self._data[i:i + 4],
                                      byteorder='big' if self._header.byte_order == ByteOrder.BIG_ENDIAN else 'little',
                                      signed=True))
        return arr

    def calculate_sample_rate(self) -> float:
        sample_rate_factor = self.sample_rate_factor
        sample_rate_multiplier = self.sample_rate_multiplier
        if sample_rate_multiplier is None or sample_rate_factor is None:
            return 0
        sample_rate_factor_multiplier = sample_rate_factor * sample_rate_multiplier
        sample_rate_factor = abs(sample_rate_factor)
        if sample_rate_factor_multiplier != 0:
            return math.pow(abs(sample_rate_factor), sample_rate_factor / abs(sample_rate_factor)) * \
                   math.pow(abs(sample_rate_multiplier), sample_rate_multiplier) / abs(
                sample_rate_multiplier)
        else:
            return 0

    def append(self, blockette: DataBlockette):
        if not blockette:
            raise ValueError
        b_type = blockette.get_type()
        if b_type == 100 and not isinstance(blockette, B100):
            raise ValueError(f'Expected B100 but received {type(blockette)}')
        elif b_type == 1000 and not isinstance(blockette, B1000):
            raise ValueError(f'Expected B1000 but received {type(blockette)}')
        self._blockettes[blockette.get_type()] = blockette

    def __getitem__(self, item):
        if item is None:
            raise IndexError
        length: int = len(self._data)
        if isinstance(item, slice):
            start, stop, step = item.start, item.stop, item.step
            start = start * 4 if start is not None else 0
            stop = stop * 4 if stop is not None else math.floor(length / 4)
            step = step * 4 if step is not None else 4

            result = []
            if item.stop is not None and item.stop > length:
                raise IndexError
            for i in range(start, stop, step):
                result.append(int.from_bytes(self._data[i:i + 4],
                                             byteorder='big' if self.byte_order == ByteOrder.BIG_ENDIAN else 'little',
                                             signed=True))
            return result
        elif isinstance(item, int):
            if item < 0:
                item = length + (item * 4)
            if item < 0 or item >= len(self._data):
                raise IndexError
            return int.from_bytes(self._data[item:item + 4],
                                  byteorder='big' if self.byte_order == ByteOrder.BIG_ENDIAN else 'little', signed=True)
        else:
            raise ValueError

    def __str__(self) -> str:
        return str(self.header)


class DecompressedRecord(DataRecord):
    def __init__(self, header: DataHeader, sample_rate: int = None, samples=None):
        super(DecompressedRecord, self).__init__(header=header)
        self._samples: list[int] = samples
        self._sample_rate = sample_rate

    @property
    def samples(self) -> list[int]:
        return self._samples

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    def ts_pairs(self) -> [datetime, int]:
        # df = pd.DataFrame({'date': np.array([datetime.datetime(2020, 1, i+1) for i in range(12)]),
        time: datetime = self.start_time
        time_list = []
        delta: float = 1 / self.sample_rate
        for sample in self._samples:
            time_list.append(time)
            time += datetime.timedelta(seconds=delta)
        return [time_list, self._samples]

    def __getitem__(self, item):
        if item is None:
            raise IndexError
        length: int = len(self._samples)
        if isinstance(item, slice):
            start, stop, step = item.start, item.stop, item.step
            if item.stop is not None and item.stop > length:
                raise IndexError
            return self._samples[item.start:item.stop:item.step]
        elif isinstance(item, int):
            if item < 0:
                item = length + item
            if item < 0 or item >= len(self._data):
                raise IndexError
            return self._samples[item]
        else:
            raise ValueError


class BlocketteFactory:

    @staticmethod
    def create(b_bytes: bytes, byte_order: ByteOrder, offset: int) -> DataBlockette:
        if b_bytes is None:
            raise IOError('expected 4 bytes but received none')
        if len(b_bytes) < 4:
            raise IOError('expected at least 4 bytes but received {}'.format(len(b_bytes)))
        if byte_order is ByteOrder.BIG_ENDIAN:
            b_type, next_blockette = struct.unpack('>hh', b_bytes[offset:offset + 4])
        else:
            b_type, next_blockette = struct.unpack('<hh', b_bytes[offset:offset + 4])
        if b_type == 100:
            return B100.from_bytes(b_bytes, byte_order, offset)
        elif b_type == 1000:
            b_type, next_blockette_byte_number, encoding_format, word_order, data_record_length, reserved \
                = struct.unpack('<hhbbbb' if byte_order is ByteOrder.LITTLE_ENDIAN else '>hhbbbb',
                                b_bytes[offset:offset + 8])
            if b_type != 1000:
                raise ValueError
            return B1000(next_blockette_byte_number=next_blockette_byte_number, encoding_format=encoding_format,
                         word_order=word_order, data_record_length=data_record_length, reserved=reserved)
        elif b_type == 1001:
            b_type, next_blockette_byte_number, encoding_format, word_order, data_record_length, reserved \
                = struct.unpack('<hhbbbb' if byte_order is ByteOrder.LITTLE_ENDIAN else '>hhbbbb',
                                b_bytes[offset:offset + 8])
            if b_type != 1001:
                raise ValueError
            return B1001(next_blockette_byte_number=next_blockette_byte_number, timing_quality=encoding_format,
                         microseconds=word_order, reserved=data_record_length, frame_count=reserved)
        else:
            raise ValueError


class Format(ABC):
    def __init__(self):
        pass


class SeedFormat(Format):
    def __init__(self, version: str):
        super().__init__()
        self._version = version

    def get_version(self):
        return self._version

    @staticmethod
    def version2():
        return SeedFormatV2()

    @staticmethod
    def version3():
        return SeedFormatV3()


class SeedFormatV2(SeedFormat):
    RECORD_HEADER = re.compile(r'^\d{6}[VASTDRQM]')

    def __init__(self):
        super().__init__("2.4")


class SeedFormatV3(SeedFormat):

    def __init__(self):
        super().__init__("3.0")
