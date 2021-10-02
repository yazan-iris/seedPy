from abc import ABC, abstractmethod
from enum import Enum

from buffer import ByteOrder


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


class EncodedRecord(ABC):
    def __init__(self):
        self.number_of_samples = 0

    @abstractmethod
    def get_date(self) -> list:
        pass

    def __str__(self):
        # return f"data length = {0 if not self.data else len(self.data)}, number_of_encoded_samples = {self.number_of_encoded_samples} "
        return f"EncodedRecord: number_of_encoded_samples = {self.number_of_samples} "


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
    def __init__(self):
        pass



