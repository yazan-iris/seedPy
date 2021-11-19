import cProfile
import datetime
import logging
import pstats
import struct
import unittest
from io import StringIO

import h5py
import numpy as np
import obspy as obspy
import pandas as pd
import xarray
from pandas import DatetimeIndex
from pip._internal import commands
from xarray import cftime_range

import seed
import test_util


class TestSeedFile(unittest.TestCase):

    def test_get_record_length(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        record_length = seed.get_record_length(source)
        self.assertEqual(512, record_length)

    def test_count(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        logging.info(f'test_iterate: source={source} ')
        count = seed.count(source)
        self.assertEqual(1243, count)

    def test_iterate(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        logging.info(f'test_iterate: source={source} ')
        with seed.iterate(source) as iterator:
            for record in iterator:
                print(record.header)
                print(record.data)

    def test_read(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        logging.info(f'test_iterate: source={source} ')
        records = seed.read(source)
        for record in records:
            print(record.header)

    def test_trace(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        logging.info(f'test_iterate: source={source} ')
        trace = seed.trace(source)
        self.assertIsNotNone(trace)

    def test_plot(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        logging.info(f'test_iterate: source={source} ')
        records = seed.read(source)
        for record in records:
            print(record.header)

    def test_fetch(self):
        records = seed.fetch(
            'http://service.iris.edu/fdsnws/dataselect/1/query?net=IU&sta=ANMO&loc=00&cha=BHZ&start=2010-01-01T10:12:23&end=2010-01-01T10:24:23')
        self.assertIsNotNone(records)
        for record in records:
            print(record.header)

    def test_write(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        logging.info(f'test_iterate: source={source} ')
        records = seed.read(source)
        for record in records:
            print(record.header)

    def test_resize(self):
        pass

    def test_print(self):
        pass

    def test_convert_to_geocsv(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        seed.convert(source, f'{test_util.current_directory()}/converted_fdsnws-dataselect_2021-10-16t19_00_21z.csv',
                     data_format='geocsv')

    def test_convert_to_parquet(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        seed.convert(source,
                     f'{test_util.current_directory()}/converted_fdsnws-dataselect_2021-10-16t19_00_21z.parquet',
                     data_format='parquet')

    def test_convert_to_hdf5_exmple(self):
        with h5py.File('/Users/yazan/Downloads/hello.hdf5', 'w') as h5f:
            x = [datetime.datetime.now().timestamp(), datetime.datetime.now().timestamp()]
            y = [1, 2]
            h5f.create_dataset('Hello', data=[x, y], dtype=('int64', 'int64'), compression='gzip', chunks=True)

    def test_convert_to_hdf5(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        seed.convert(source, f'{test_util.current_directory()}/converted_fdsnws-dataselect_2021-10-16t19_00_21z.hdf5',
                     data_format='hdf5')

    def test_convert_to_netcdf(self):
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        seed.convert(source, f'{test_util.current_directory()}/netcdf_fdsnws-dataselect_2021-10-16t19_00_21z.hdf5',
                     data_format='netcdf')

    def test_pro(self):
        int_list = [0, 1, 258, 32768]
        fmt = "<%dI" % len(int_list)
        data = struct.pack(fmt, *int_list)
        nums = list(struct.unpack(fmt, data))
        print(type(nums))
        print(nums)
        #cProfile.run("test_convert_to_netcdf()")

    def test_obspy(self):
        #st = obspy.read('http://examples.obspy.org/RJOB_061005_072159.ehz.new')
        source = test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')
        st = obspy.read(source)
        print(st[0])
        print(st[0].data)


    def test_xarray(self):
        # times = pd.date_range(start='2000-01-01', freq='1H', periods=6)
        # xarray.cftime_range(start='2000-01-01', end=None, periods=None, freq='D', normalize=False, name=None,
        #                   closed=None,
        #                  calendar='standard')
        # times = cftime_range(start='2000-01-01', periods=6, freq='1H',
        # calendar='standard')
        time = [datetime.datetime.now()]
        samples = [1]
        ds = xarray.Dataset(data_vars=dict(
            samples=(["samples", "time"], samples)),
            coords=dict(
                lon=(["x"], [22]),
                lat=(["x"], [33]),
                time=time),
            attrs=dict(description="Weather related data."))
        print(ds)

    def test_xarray(self):
        coords = {'time': [datetime.datetime(2017, 1, n + 1) for n in range(2)],
                  'freq': [0.05, 0.1],
                  'dir': np.arange(0, 360, 120)}
        efth = xarray.DataArray(data=np.random.rand(2, 2, 3),
                                coords=coords,
                                dims=('time', 'freq', 'dir'),
                                name='efth')
        print(efth)

        coords = {'time': [datetime.datetime(2017, 1, n + 1) for n in range(2)],
                  'dir': np.arange(0, 360, 120)}
        efth = xarray.DataArray(data=np.random.rand(2, 2, 3),
                                coords=coords,
                                dims=('time', 'dir'),
                                name='efth')
        print(efth)

    def test_arr(self):
        N = 4
        data = range(N)
        dates = [datetime.datetime(2001, 1, 1, 15) + datetime.timedelta(hours=i) for i in range(N)]
        # time variable is called the same as time dimension: works
        scheme1 = {
            "dims": "t",
            "coords": {"t": {"dims": "t", "data": dates}},
            "data": data
        }
        # time variable is called differently from the time dimension: does not work
        scheme2 = {
            "dims": "t",
            "coords": {"time": {"dims": "t", "data": dates}},
            "data": data
        }
        a1 = xarray.DataArray.from_dict(scheme1).to_netcdf('test')
        print(a1)



    def test_numpy22(self):
        class DateTimeArray:
            def __init__(self, start: datetime.datetime = None, freq: str = None, periods: int = None):
                self._start = start
                self._freq = freq
                self._periods = periods

            def __getitem__(self, key):
                return self.__dict__[key]

            def __len__(self):
                return self._periods

        print(pd.date_range(start=datetime.datetime.now(), freq='0.005S', periods=4))
        now = datetime.datetime.now()
        delta = datetime.timedelta(0, 3)
        dti = DatetimeIndex([now, now + delta])
        print(dti)
        print(type(dti))


    def test_numpy1(self):
        print(np.random.rand(4, 3))
        print(pd.date_range("2000-01-01", periods=4))

        print(np.random.rand(4, 1))
        print(pd.date_range("2000-01-01", periods=4))

        data = np.random.rand(4, 1)
        location = ["IA"]
        time = pd.date_range("2000-01-01", periods=4)

        foo = xarray.DataArray(data, coords=[time, location], dims=["time", "location"])
        data = [1, 2, 3, 4]
        time = [datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now(), datetime.datetime.now()]
        foo = xarray.DataArray(data, coords=[time, location], dims=["time", "location"])
        print(foo)

    def test_numpy(self):
        print(np.random.rand(4, 3))
        arr = np.array([[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]], dtype='int')
        print(arr)
        print(type(arr))
        print(arr[1][2])

        arr = np.empty(2, dtype='int')
        print(arr)
        print(arr[1])

        arr = np.zeros(2, dtype='int')
        print(arr)
        print(arr[1])

        arr = np.zeros(2, dtype=np.int32)
        print(arr)
        print(arr[1])

        arr = xarray.DataArray(data=arr, dims={'x'})
        print(f'ooooooooo:{arr}')

        arr = np.zeros((2, 2), dtype=np.int32)
        print(arr)
        print(arr[1])

        arr = xarray.DataArray(data=arr, dims={'x', 'y'}, coords={'x': 22, 'y': 33})
        print(f'ooooooooo:{arr}')

        arr = xarray.DataArray(data=arr, coords={
            'x': arr,
            'lat': 22,
            'lon': 22})
        print(f'arrrrr:{arr}')
