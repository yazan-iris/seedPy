import csv
import datetime
import importlib.resources
import sys
import unittest

import requests

from fdsn import HttpClient, Channel, Network, Station
from geocsv import GeoCSV, GeoCSVField, GeoCSVFormat, GeoCSVHeader, SeedGeoCSV
from seedio import iterate
from timeseries import Trace


class TestGeoCSV(unittest.TestCase):

    def test_write(self):
        header = GeoCSVHeader()
        header.parameters = {'sample_count': 2, 'sample_rate_hz': 20,
                             'start_time': datetime.datetime.now(), 'latitude_deg': -29.011, 'longitude_deg': -70.7005,
                             'elevation_m': 2274.0, 'depth_m': 0.0, 'azimuth_deg': 0.0, 'dip_deg': -90,
                             'instrument': 'Streckeisen STS-1VBB w/E300', 'scale_factor': 5.45769E9,
                             'scale_frequency_hz': 0.02, 'scale_units': 'm/s'}

        header.fields = [GeoCSVField(field_name='time', field_type=datetime.datetime, field_unit='utc'),
                         GeoCSVField(field_name='Count', field_type=int, field_unit='integer')]

        rows = [[datetime.datetime.now(), 4]]
        # sys.stdout.write(str(99) + '\n')
        # '/Users/yazan/Downloads/pairs.csv'
        GeoCSV(sys.stdout, header=header).writerows(rows)

    def test_geocsv_write(self):
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

            params = trace.object_identifier.to_dictionary()
            params['start'] = '2012-01-01T10:00:00'
            params['end'] = '2012-04-01T10:00:00'
            params['level'] = 'cha'
            params['format'] = 'text'
            networks = HttpClient('service.iris.edu').fetch(params)
            if not networks or len(networks) == 0:
                raise RuntimeError
            network: Network = networks[0]
            station: Station = network.stations[0]
            channel: Channel = station.channels[0] if len(station.channels) > 0 else None
            if channel is None:
                raise RuntimeError
            header = GeoCSVHeader(parameters={'sample_count': trace.number_of_samples, 'sample_rate_hz': 20,
                                              'start_time': trace.start_time, 'latitude_deg': channel.latitude,
                                              'longitude_deg': channel.longitude,
                                              'elevation_m': channel.elevation, 'depth_m': channel.depth,
                                              'azimuth_deg': channel.azimuth, 'dip_deg': channel.dip,
                                              'instrument': channel.sensor.description,
                                              'scale_factor': channel.sensitivity.value,
                                              'scale_frequency_hz': channel.sensitivity.frequency,
                                              'scale_units': channel.sensitivity.unit})

            header.fields = [GeoCSVField(field_name='time', field_type=datetime.datetime, field_unit='utc'),
                             GeoCSVField(field_name='Count', field_type=int, field_unit='integer')]

            with SeedGeoCSV('/Users/yazan/Downloads/pairs.csv', header=header) as geo_csv:
                geo_csv.write_trace(trace)
