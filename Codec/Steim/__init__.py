from abc import ABC, abstractmethod

import array

from Codec import Encoder, EncodingFormat, EncodedRecord
from Codec.Steim.buckets import SteimBucket
from Codec.Steim.controls import ControlSequence
from Codec.Steim.frames import SteimFrame, SteimHeaderFrame
from buffer import ByteOrder


class SteimRecord(EncodedRecord):

    def __init__(self, number_of_frames: int, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(SteimRecord, self).__init__()
        if number_of_frames is None:
            raise ValueError
        self._number_of_frames = number_of_frames
        self._byte_order = byte_order
        self._frames = list()
        self._control_sequence = ControlSequence()

    @property
    def forward_integration_factor(self):
        return self._frames[0].forward_integration_factor

    @forward_integration_factor.setter
    def forward_integration_factor(self, value: int):
        if value is None:
            raise ValueError
        if self.is_empty():
            self._frames.append(SteimHeaderFrame(byte_order=self._byte_order))
        self._frames[0].forward_integration_factor = value

    @property
    def reverse_integration_factor(self):
        return self._frames[0].reverse_integration_factor

    @reverse_integration_factor.setter
    def reverse_integration_factor(self, value: int):
        if value is None:
            raise ValueError
        if self.is_empty():
            self._frames.append(SteimHeaderFrame(byte_order=self._byte_order))
        self._frames[0].reverse_integration_factor = value

    def append(self, bucket: SteimBucket) -> bool:
        if bucket is None:
            raise ValueError
        if self.is_full():
            return False
        if self.is_empty():
            self._frames.append(SteimHeaderFrame(byte_order=self._byte_order))

        control, values, number_of_samples = bucket.pack()
        if not self._frames[-1].append(control, values):
            if self.is_full():
                return False
            self._frames.append(SteimFrame(byte_order=self._byte_order))
            if not self._frames[-1].append(control, values):
                raise RuntimeError
        self.number_of_samples += number_of_samples
        return True

    def size(self) -> int:
        if not self._frames:
            return 0
        return len(self._frames)

    def is_full(self) -> bool:
        return self.size() == self._number_of_frames and self._frames[-1].is_full()

    def is_empty(self) -> bool:
        return self.size() == 0

    def get_date(self) -> list:
        pass

    def __getitem__(self, item):
        return self._frames[item]

    def __iter__(self):
        return iter(self._frames)


class SteimEncoder(Encoder, ABC):
    def __init__(self, encoding_format: EncodingFormat = EncodingFormat.STEIM_2,
                 byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(SteimEncoder, self).__init__(encoding_format, byte_order)

    def encode(self, samples, offset: int = 0, **kwargs) -> EncodedRecord:
        if not samples:
            raise ValueError
        if isinstance(samples, list):
            print('it is a list')
        elif isinstance(samples, array.array):
            print('it is a array')
        else:
            raise ValueError

        number_of_frames = kwargs.get('number_of_frames')
        if not number_of_frames or number_of_frames < 1:
            raise ValueError

        carry_over = kwargs.get('carry_over')
        previous = 0
        if carry_over is not None:
            previous = carry_over

        record = SteimRecord(number_of_frames=number_of_frames)
        record.forward_integration_factor = samples[offset]
        bucket = SteimBucket.instance(self.encoding_format)
        last_sample = None
        for sample in samples:
            if record.is_full():
                break
            delta = sample - previous
            if not bucket.put(delta):
                record.append(bucket)
                bucket.reset()
                bucket.put(delta)
            last_sample = sample
            previous = sample
        record.reverse_integration_factor = last_sample
        if bucket and not bucket.is_empty():
            record.append(bucket)
        return record

    @abstractmethod
    def get(self):
        pass

    @staticmethod
    def with_format(encoding_format: EncodingFormat) -> "SteimEncoder":
        if not encoding_format:
            raise ValueError

        if encoding_format == EncodingFormat.STEIM_1:
            return Steim1Encoder()
        elif encoding_format == EncodingFormat.STEIM_2:
            return Steim2Encoder()
        elif encoding_format == EncodingFormat.STEIM_3:
            return Steim3Encoder()
        else:
            raise ValueError(encoding_format)


class Steim1Encoder(SteimEncoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim1Encoder, self).__init__(EncodingFormat.STEIM_1, byte_order)

    def get(self):
        return None


class Steim2Encoder(SteimEncoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim2Encoder, self).__init__(EncodingFormat.STEIM_2, byte_order)

    def get(self):
        return None


class Steim3Encoder(SteimEncoder):
    def __init__(self, byte_order: ByteOrder = ByteOrder.BIG_ENDIAN):
        super(Steim3Encoder, self).__init__(EncodingFormat.STEIM_3, byte_order)

    def get(self):
        return None
