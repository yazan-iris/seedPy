import importlib.resources
import unittest

import seed
import test_util
from model import DataRecord


class TestSeedFile(unittest.TestCase):

    def test_iterate(self):
        with seed.iterate(test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')) as iterator:
            for record in iterator:
                print(record.header)

    def test_read(self):
        with seed.read(test_util.path('fdsnws-dataselect_2021-10-16t19_00_21z.mseed')) as seed_file:
            records: list[DataRecord] = seed_file.read()
            for record in records:
                print(record.header)

    def test_read_record_by_seek(self):
        with seedfile.open('') as seed_file:
            record: DataRecord = seed_file.read(record_number=12)
            records: list[DataRecord] = seed_file.read(record_number=slice(12, 15))

    def test_read_as_timeseries(self):
        seedfile.series()
        with importlib.resources.path('tests',
                                      'fdsnws-dataselect_IU_ANMO_00_BHZ_2020-02-27t06:30:00.000_2020-02-27t10:30:00.000.mseed') as file, \
                seedfile.open(file) as seed_file:
            record: DataRecord = seed_file.read(record_number=12)
            records: list[DataRecord] = seed_file.read(record_number=slice(12, 15))

    def test_convert(self):
        with importlib.resources.path('tests',
                                      'fdsnws-dataselect_IU_ANMO_00_BHZ_2020-02-27t06:30:00.000_2020-02-27t10:30:00.000.mseed') as input,\
                                        open('/Users/yazan/Downloads/pairs.csv', 'w') as output:
            seedfile.convert(input=input, output=output, format='geocsv')

    def test_resize(self):
        with importlib.resources.path('tests',
                                      'fdsnws-dataselect_IU_ANMO_00_BHZ_2020-02-27t06:30:00.000_2020-02-27t10:30:00.000.mseed') as input,\
                                        open('/Users/yazan/Downloads/pairs.csv', 'w') as output:
            seedfile.convert(input=input, output=output, format='geocsv')

    def test_plot(self):
        pass
