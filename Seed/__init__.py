import datetime
import re
import struct
from abc import ABC

from enum import Enum

__version__ = "1.0.0"

from Buffer import ByteOrder
from Codec import EncodingFormat


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
        self.header = header
        self.blockettes = []
        self.data = None

    def append(self, blockette: DataBlockette):
        if not blockette:
            raise ValueError
        self.blockettes.append(blockette)

    def __str__(self) -> str:
        return str(self.header)


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


def open(source, record_length=4096, options=None):
    if options is None:
        raise ValueError
    for c in options:
        if c == 'r':
            pass
        elif c == 'w':
            pass
