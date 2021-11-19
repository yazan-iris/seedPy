import datetime
import importlib.resources
import unittest

import array
from matplotlib import pyplot as plt, pyplot

from model import DataHeader, DecompressedRecord
from seed import iterate
from timeseries import Trace
from units import ureg


class TestTrace(unittest.TestCase):
    # df = pd.DataFrame({'date': np.array([datetime.datetime(2020, 1, i+1) for i in range(12)]),

    def test_r(self):
        trace = Trace()
        start_time: datetime.datetime = datetime.datetime(year=2010, month=7, day=12, hour=11, minute=11, second=11)
        header: DataHeader = DataHeader(sequence_number=1, record_type='M', network_code='IU',
                                        station_identifier_code='ANMO',
                                        location_identifier='00', channel_identifier='BHZ',
                                        record_start_time=start_time)

        samples = array.array("i", range(0, 1500))
        record: DecompressedRecord = DecompressedRecord(header=header, sample_rate=20,
                                                        samples=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        trace.add(record)

        start_time: datetime.datetime = datetime.datetime(year=2010, month=7, day=12, hour=11, minute=11, second=15)
        header.record_start_time = start_time
        record: DecompressedRecord = DecompressedRecord(header=header, sample_rate=20,
                                                        samples=[10, 11, 12, 13, 14, 15, 16, 17, 18, 19])
        print('===========')
        trace.add(record)
        print('===========22222')

        start_time: datetime.datetime = datetime.datetime(year=2010, month=7, day=12, hour=11, minute=11, second=8)
        header.record_start_time = start_time
        record: DecompressedRecord = DecompressedRecord(header=header, sample_rate=20,
                                                        samples=[-1, -2, -3, -4, -5, -6, -7, -8, -9])
        print('===========')
        trace.add(record)

        start_time: datetime.datetime = datetime.datetime(year=2010, month=7, day=12, hour=11, minute=11, second=10)
        header.record_start_time = start_time
        record: DecompressedRecord = DecompressedRecord(header=header, sample_rate=20,
                                                        samples=[100, 200, 300, 400, 500, 600, 700, 800, 900])
        print('===========')
        trace.add(record)
        print('===========22222')

        self.assertEqual(1, len(trace.segments))
        print(trace.x)
        print(trace.y)

        pyplot.plot(trace.x, trace.y)
        pyplot.show()

    def test_r_1(self):
        trace = Trace()
        start_time: datetime.datetime = datetime.datetime(year=2010, month=7, day=12, hour=11, minute=11, second=11)
        header: DataHeader = DataHeader(sequence_number=1, record_type='M', network_code='IU',
                                        station_identifier_code='ANMO',
                                        location_identifier='00', channel_identifier='BHZ',
                                        record_start_time=start_time)

        samples = array.array("i", range(0, 1500))
        record: DecompressedRecord = DecompressedRecord(header=header, sample_rate=20, samples=samples)
        trace.add(record)
        self.assertEqual(1, len(trace.segments))
        print(trace.x)
        print(trace.y)

        pyplot.plot(trace.x, trace.y)
        pyplot.show()

    def test_trace(self):
        with importlib.resources.path('tests',
                                      'fdsnws-dataselect_IU_ANMO_00_BHZ_2020-02-27t06:30:00.000_2020-02-27t10:30:00.000.mseed') as file, \
                iterate(file, decompress=True) as iterator:
            trace: Trace = None
            for record in iterator:
                if trace is None:
                    trace = Trace.with_network_station_location_channel(record.network_code, record.station_code,
                                                                        record.channel_location_code,
                                                                        record.channel_code)
                trace.add(record=record)
                # pairs = record.ts_pairs()
                # print(pairs)
                # break
            if trace is None:
                raise RuntimeError
            plt.plot(trace.x, trace.y)
            plt.ylabel('some numbers')
            plt.title('Sales by Date')
            plt.xlabel('Date')
            plt.ylabel('Sales')
            plt.show()

    def test_plot(self):
        with importlib.resources.path('tests',
                                      'fdsnws-dataselect_IU_ANMO_00_BHZ_2020-02-27t06:30:00.000_2020-02-27t10:30:00.000.mseed') as file, \
                iterate(file, decompress=True) as iterator:
            trace: Trace = None
            for record in iterator:
                if trace is None:
                    trace = Trace.with_network_station_location_channel(record.network_code, record.station_code,
                                                                        record.channel_location_code,
                                                                        record.channel_code)
                trace.add(record=record)
                # pairs = record.ts_pairs()
                # print(pairs)
                # break
            if trace is None:
                raise RuntimeError

            trace.plot(unit=ureg.meter / ureg.second, color='green')
