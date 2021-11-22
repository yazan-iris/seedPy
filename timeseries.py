import datetime
from collections import MutableSequence
from typing import Union

import array
import matplotlib.pyplot as plt

import math
import numpy
from pint import Unit

from model import DecompressedRecord
from objectidentitier import ObjectIdentifier
from units import ureg


class Epoch:
    def __init__(self, start_time: datetime, end_time: datetime):
        self._start_time: datetime = start_time
        self._end_time: datetime = end_time

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def duration(self) -> datetime.timedelta:
        return self.end_time - self._start_time

    def is_before(self, other: 'Epoch'):
        if other is None:
            raise ValueError
        return self.start_time < other.start_time

    def is_before_or_equal(self, other: 'Epoch'):
        if other is None:
            raise ValueError
        return self.start_time <= other.start_time

    def is_after(self, other: 'Epoch'):
        if other is None:
            raise ValueError
        return self._end_time > other.end_time

    def is_after_or_equal(self, other: 'Epoch'):
        if other is None:
            raise ValueError
        return self._end_time >= other.end_time

    def overlap(self, other: 'Epoch'):
        if other is None:
            raise ValueError
        return not self._start_time > other.end_time and not self.end_time < other.start_time

    def __lt__(self, other):
        return self.is_before(other)

    def __le__(self, other):
        return self.is_before_or_equal(other)

    def __gt__(self, other):
        return self.is_after(other)

    def __ge__(self, other):
        return self.is_after_or_equal(other)


class Segment(Epoch):
    def __init__(self, start_time: datetime, sample_rate: int, samples: Union[list[int], MutableSequence[int]]):
        if start_time is None:
            raise ValueError
        if sample_rate is None:
            raise ValueError
        if samples is None:
            raise ValueError
        length: int = len(samples)
        milli_seconds = ((length - 1) / sample_rate) * 1000
        end_time: datetime = start_time + datetime.timedelta(milliseconds=milli_seconds)
        super(Segment, self).__init__(start_time=start_time, end_time=end_time)
        self._sample_rate: int = sample_rate
        self._samples = samples

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def samples(self) -> list[int]:
        return self._samples

    def merge(self, other: 'Segment'):
        if other is None:
            raise ValueError
        if self.overlap(other):
            if self <= other:
                duration = other.start_time - self.start_time
                index: int = math.floor(duration.total_seconds() * self.sample_rate)
                new_list = self.samples[0:index]
                new_list += other.samples
                self._samples = new_list
                #self._end_time = other.end_time
            else:
                duration = self.start_time - other.start_time
                index: int = duration * self.sample_rate
                new_list = other.samples[0:index]
                new_list += self.samples[len(other.samples) - index:len(self)]
                self._samples = new_list
                #self._start_time = other.start_time
        elif self <= other:
            self._samples += other.samples
            self._end_time = other.end_time
        else:
            #self._samples = other.samples.extend(self._samples)
            self._samples = other.samples + self._samples
            self._start_time = other.start_time

    def index(self, time: datetime.datetime) -> int:
        if time is None:
            raise ValueError
        if self._start_time <= time:
            duration = time - self._start_time
        else:
            duration = self._start_time - time
        return math.ceil(duration.total_seconds() * self.sample_rate)

    def can_tolerable(self, other: 'Segment') -> bool:
        if other is None:
            raise ValueError
        return abs(1.0 - (self.sample_rate / other.sample_rate)) < 0.0001

    def __getitem__(self, item):
        if self._samples is None:
            return IndexError
        if isinstance(item, slice):
            result = []
            if item.stop is not None and item.stop > len(self):
                raise IndexError
            return self._samples[item.start:item.stop:item.step]
        else:
            return self._samples[item]

    def __len__(self):
        if self._samples is None:
            return 0
        return len(self._samples)

    def __str__(self):
        return f'start_time:{self.start_time.isoformat()} <> end_time:{self.end_time.isoformat()}, number_of_samples:{len(self)}'


class Trace:

    def __init__(self, object_identifier: ObjectIdentifier = None):
        if object_identifier:
            self._object_identifier = object_identifier
        else:
            self._object_identifier = None
        self._quality: str = None
        self._segments = list()

    @property
    def object_identifier(self) -> ObjectIdentifier:
        return self._object_identifier

    @property
    def network(self) -> str:
        return self._object_identifier.network

    @property
    def station(self) -> str:
        return self._object_identifier.station

    @property
    def location(self) -> str:
        return self._object_identifier.location

    @property
    def channel(self) -> str:
        return self._object_identifier.channel

    @property
    def start_time(self) -> datetime:
        if self._segments is None or len(self._segments) == 0:
            return None
        return self._segments[0].start_time

    @property
    def end_time(self) -> datetime:
        if self._segments is None or len(self._segments) == 0:
            return None
        return self._segments[-1].end_time

    @property
    def segments(self) -> list[Segment]:
        return self._segments

    @property
    def number_of_samples(self) -> int:
        if len(self) == 0:
            return 0
        else:
            number_of_samples = 0
            for segment in self._segments:
                number_of_samples += len(segment)
            return number_of_samples

    @property
    def x(self) -> []:
        # {'date': np.array([datetime.datetime(2020, 1, i + 1) for i in range(12)]
        time: datetime.datetime = self.start_time
        time_list = []
        # arr = array.array(self.number_of_samples)
        # a = array.array('I', (0 for i in range(0, self.number_of_samples)))
        for segment in self._segments:
            delta: float = 1 / segment.sample_rate
            time_delta = datetime.timedelta(seconds=delta)
            for i in range(len(segment)):
                time_list.append(time)
                time += time_delta
        return time_list

    @property
    def y(self) -> []:
        samples = []
        arr = array.array('I', (0 for i in range(0, self.number_of_samples)))
        index: int = 0
        for segment in self._segments:
            samples.extend(segment.samples)
            # arr[index:index+len(segment)] = segment[0:len(segment)]
            index += len(segment)
        return samples

    def add(self, record: DecompressedRecord):
        if record is None or not isinstance(record, DecompressedRecord):
            raise ValueError
        if self._object_identifier is None:
            self._object_identifier = ObjectIdentifier(network=record.network_code, station=record.station_code,
                                                       location=record.channel_location_code,
                                                       channel=record.channel_code)
        else:
            if self._object_identifier != ObjectIdentifier(network=record.network_code, station=record.station_code,
                                                           location=record.channel_location_code,
                                                           channel=record.channel_code):
                raise ValueError
        new_segment = Segment(start_time=record.start_time, sample_rate=record.sample_rate,
                              samples=record.samples)
        sample_rate: int = new_segment.sample_rate
        if sample_rate is None:
            raise ValueError

        half_period_in_milli_seconds: float = ((1 / sample_rate) / 2) * 1000
        if self._segments and len(self._segments) > 0:
            for segment in self._segments:
                segment.merge(new_segment)
        else:
            self._segments.append(new_segment)
        if not self._quality:
            self._quality = record.record_type
        elif self._quality != record.record_type:
            self._quality = 'M'

    def plot(self, title: str = None, unit: Unit = None, color: str = 'blue', show_grid: bool = True,
             line_width: float = 0.5):
        kind, unit, convert = get_converter(unit)
        y = convert(self.x, self.y)
        fig, axs = plt.subplots(1, 1, squeeze=False)
        if not title:
            title = f'{str(self.object_identifier)}:{kind}'

        axs[0, 0].title.set_text(title)
        axs[0, 0].set_ylabel(unit)
        if color is None:
            color = 'blue'
        if not line_width or line_width < 0.1:
            line_width = 0.5
        axs[0, 0].grid(show_grid)
        plt.plot(self.x, y, color=color, linewidth=line_width)
        plt.show()

    def __len__(self):
        if self._segments:
            return len(self._segments)
        else:
            return 0

    def __str__(self):
        if self._object_identifier:
            return f"{str(self._object_identifier)}" \
                   f": start_time={self.start_time.strftime('%m/%d/%Y, %H:%M:%S') if self.start_time else ''}" \
                   f", end_time={self.end_time.strftime('%m/%d/%Y, %H:%M:%S') if self.start_time else ''}" \
                   f", number_of_samples={self.number_of_samples}"
        else:
            return 'Trace:'

    @classmethod
    def with_identifier(cls, object_identifier: ObjectIdentifier = None) -> 'Trace':
        return cls(object_identifier)

    @classmethod
    def with_network_station_location_channel(cls, network: str, station: str, location: str, channel: str) -> 'Trace':
        return cls(ObjectIdentifier(network=network, station=station, location=location, channel=channel))


def derive(x, y, sample_rate):
    return fft_deriv(x, y, sample_rate)


def fft_deriv(x, y, sample_rate):
    n = len(y)
    micro_secs_per_sample = (1000 / sample_rate)
    L = 6283185.307179586 / n * micro_secs_per_sample
    fhat = numpy.fft.fft(y)
    kappa = (2 * numpy.pi / L) * numpy.arange(-n / 2, n / 2)
    kappa = numpy.fft.fftshift(kappa)
    dfhat = kappa * fhat * (1j)
    return numpy.real(numpy.fft.ifft(dfhat))


velocity = ureg.meter / ureg.second
acceleration = ureg.meter / (ureg.second * ureg.second)


def is_displacement(unit) -> bool:
    if unit is None or not isinstance(unit, Unit):
        raise ValueError
    return unit.is_compatible_with(ureg.meter)


def is_velocity(unit: Unit) -> bool:
    if unit is None or not isinstance(unit, Unit):
        raise ValueError
    return unit.is_compatible_with(velocity)


def is_acceleration(unit) -> bool:
    if unit is None or not isinstance(unit, Unit):
        raise ValueError
    return unit.is_compatible_with(acceleration)


def get_converter(target_unit: Unit):
    if not target_unit:
        raise ValueError

    def to_displacement(x, y: list):
        return y

    def to_velocity(x, y: list):
        return derive(x, y, 1)

    def to_acceleration(x, y: list):
        return derive(x, y, 2)

    if is_displacement(target_unit):
        return 'displacement', target_unit, to_displacement
    elif is_velocity(target_unit):
        return 'velocity', target_unit / ureg.second, to_velocity
    elif is_acceleration(target_unit):
        return 'acceleration', target_unit / (ureg.second * ureg.second), to_acceleration
    else:
        raise ValueError('unsupported conversion type!')


class Timeseries:
    def __init__(self, network: str, station: str, location: str, channel: str):
        if network is None or station is None or location is None or channel is None:
            raise ValueError
        self._object_identifier = ObjectIdentifier(network=network, station=station, location=location, channel=channel)
        self._quality: str = None
        self._traces = {}

    def __len__(self):
        number_of_samples: int = 0
        if self._segments is None:
            return number_of_samples

        for segment in self._segments:
            number_of_samples += segment.number_of_samples
        return number_of_samples

    def __getitem__(self, item):
        if self._segments is None:
            raise IndexError

    def __getattr__(self, attr):
        return self._traces[attr]

    def __setattr__(self, attr, value):
        raise NotImplementedError
