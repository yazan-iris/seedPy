import csv
import unittest
from io import StringIO

import requests

from fdsn import HttpClient
from objectidentitier import ObjectIdentifier


class TestObjectIdentifier(unittest.TestCase):

    def test_object_identifier(self):
        oi = ObjectIdentifier(network='IU', station='ANMO', location='00', channel='BHZ')
        print(oi)

        print(oi.to_dictionary())
        params = oi.to_dictionary()
        params['start'] = '2012-01-01T10:00:00'
        params['end'] = '2012-04-01T10:00:00'
        params['level'] = 'cha'
        params['format'] = 'text'

        networks = HttpClient('service.iris.edu').fetch(params)
        for network in networks:
            for station in network.stations:
                for channel in station.channels:
                    print(channel)
