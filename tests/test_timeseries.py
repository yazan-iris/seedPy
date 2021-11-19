import importlib.resources
import unittest

from matplotlib import pyplot

import seedfile
from seedio import iterate
from timeseries import Timeseries


class TestTimeseries(unittest.TestCase):

    def test_samples(self):
        with importlib.resources.path('tests',
                                      'fdsnws-dataselect_IU_ANMO_00_BHZ_2020-02-27t06:30:00.000_2020-02-27t10:30:00.000.mseed') as file, \
                iterate(file) as iterator:
            for record in iterator:
                print(record)

    def test_plot(self):
        class ObjDict(dict):
            def __getattr__(self, attr):
                return self[attr]

            def __setattr__(self, attr, value):
                self[attr] = value

        self.group = ObjDict(a=1, b=2, c=3)
        print(self.group.a)

        #d = {'a': 1, 'b': 2, 'c': 3}
        series = seedfile.series('')
        pyplot.plot(series)
        pyplot.show()
