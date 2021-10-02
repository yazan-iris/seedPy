import unittest
import importlib.resources

from Seed import SeedFormat


class TestVolume(unittest.TestCase):

    def test_version(self):
        with importlib.resources.path('Tests', 'fdsnws-dataselect_2020-03-28t21_11_14z.mseed') as file:
            parser = SeedFormat.parse(file)

    def test_version_2(self):
        with importlib.resources.path('Tests', 'fdsnws-dataselect_2020-03-28t21_11_14z.mseed') as file:
            seed_format = SeedFormat.version2().parse(file)

    def test_version_3(self):
        with importlib.resources.path('Tests', 'fdsnws-dataselect_2020-03-28t21_11_14z.mseed') as file, \
                SeedFormat.version3().parse(file) as parser:
            print('hello')
