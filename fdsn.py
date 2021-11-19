import csv
import datetime
from io import StringIO, BytesIO
from typing import List, Dict

import requests

from model import DataRecord
from seedio import RecordIterator
from timeseries import Epoch


class HttpError(Exception):
    def __init__(self, status_code: int, reason: str):
        self.status_code = status_code
        self.reason = reason

    def __str__(self):
        return f'status_code:{self.status_code}, reason:{self.reason}'


class Sensor:
    def __init__(self, name: str = None, description: str = None):
        self.name = name
        self.description = description


class Sensitivity:
    def __init__(self, value: float, frequency: float, unit: str):
        self.value = value
        self.frequency = frequency
        self.unit = unit


class Network:
    def __init__(self, code: str):
        if code is None:
            raise ValueError
        self._code = code
        self._stations = list()

    @property
    def code(self):
        return self._code

    @property
    def stations(self):
        return self._stations

    def add(self, station: 'Station'):
        if station is None:
            raise ValueError
        station._network = self
        self._stations.append(station)

    def get_station(self, station_code: str) -> 'Station':
        for station in self._stations:
            if station.code == station_code:
                return station
        return None

    def __str__(self):
        return self._code


class Station:
    def __init__(self, code: str):
        if code is None:
            raise ValueError
        self._code = code
        self._channels = list()
        self._network = None

    @property
    def code(self):
        return self._code

    @property
    def channels(self):
        return self._channels

    def add(self, channel: 'Channel'):
        if channel is None:
            raise ValueError
        channel.station = self
        self._channels.append(channel)

    def __str__(self):
        return self._code


class Channel(Epoch):
    def __init__(self, location_code: str, code: str, latitude: float, longitude: float, elevation: float, depth: float,
                 azimuth: float, dip: float, sample_rate: float,
                 start_time: datetime.datetime, end_time: datetime.datetime):
        super().__init__(start_time, end_time)
        if code is None:
            raise ValueError
        self._station = None
        self.location_code = location_code
        self.code = code
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.depth = depth
        self.azimuth = azimuth
        self.dip = dip
        self.depth = depth
        self.sample_rate = sample_rate
        self.sensor = None
        self.sensitivity = None

    @property
    def station(self) -> Station:
        return self._station

    @station.setter
    def station(self, station: Station):
        if station is None:
            raise ValueError
        self._station = station

    def __str__(self):
        return f'network= {self._station._network}, station={str(self._station)}, code={self.code}, location_code={self.location_code}'


def parse_time(time: str) -> datetime.datetime:
    if time is None:
        return None
    fmt = '%Y-%m-%dT%H:%M:%S.%f'
    # 'YYYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]]'
    # return datetime.datetime.fromisoformat(time)
    return datetime.datetime.strptime(time, fmt)


class HttpClient:
    def __init__(self, host: str):
        self._host = host

    @property
    def url(self):
        return 'http://' + self._host + '/fdsnws/station/1/query'

    def fetch(self, params) -> List[Network]:
        with requests.get(url=self.url, params=params) as response:
            if 200 == response.status_code:
                with StringIO(response.text) as csvfile:
                    header = [h.strip() for h in csvfile.readline().replace('#', '').split('|')]
                    reader = csv.DictReader(csvfile, fieldnames=header, delimiter='|')
                    # reader = csv.reader(csvfile, delimiter='|')
                    networks = dict()
                    for row in reader:
                        network_code = row['Network']
                        if network_code in networks:
                            network = networks[network_code]
                        else:
                            network = Network(network_code)
                            networks[network_code] = network
                        station = network.get_station(row['Station'])
                        if station is None:
                            station = Station(row['Station'])
                            network.add(station)
                        start_time: datetime.datetime = parse_time(row['StartTime'])
                        end_time: datetime.datetime = parse_time(row['EndTime'])
                        channel = Channel(location_code=row['Location'], code=row['Channel'], latitude=row['Latitude'],
                                          longitude=row['Longitude'], elevation=row['Elevation'], depth=row['Depth'],
                                          dip=row['Dip'], azimuth=row['Azimuth'],
                                          sample_rate=row['SampleRate'],
                                          start_time=start_time, end_time=end_time)
                        channel.sensitivity = Sensitivity(value=row['Scale'], frequency=row['ScaleFreq']
                                                          , unit=row['ScaleUnits'])
                        station.add(channel)
                        channel.sensor = Sensor(description=row['SensorDescription'])
                    return list(networks.values())
            else:
                raise HttpError(response.status_code, response.reason)


def fetch(url: str, params: dict = None):
    from urllib.parse import urlparse
    if url is None:
        raise ValueError
    u = urlparse(url)
    if u.query.find('dataselect'):
        return fetch_data_select(url, params)
    elif u.query.find('dataselect'):
        return fetch_station(url, params)
    else:
        raise NotImplementedError(url)


def fetch_data_select(url: str, params: dict = None) -> List[DataRecord]:
    with requests.get(url=url, params=params) as response:
        if 200 == response.status_code:
            records = list()
            with RecordIterator(BytesIO(response.content)) as it:
                for record in it:
                    records.append(record)
            return records

        else:
            raise HttpError(response.status_code, response.reason)


def fetch_station(url: str, params: dict = None) -> List[Network]:
    with requests.get(url=url, params=params) as response:
        if 200 == response.status_code:
            with StringIO(response.text) as csvfile:
                header = [h.strip() for h in csvfile.readline().replace('#', '').split('|')]
                reader = csv.DictReader(csvfile, fieldnames=header, delimiter='|')
                # reader = csv.reader(csvfile, delimiter='|')
                networks = dict()
                for row in reader:
                    network_code = row['Network']
                    if network_code in networks:
                        network = networks[network_code]
                    else:
                        network = Network(network_code)
                        networks[network_code] = network
                    station = network.get_station(row['Station'])
                    if station is None:
                        station = Station(row['Station'])
                        network.add(station)
                    start_time: datetime.datetime = parse_time(row['StartTime'])
                    end_time: datetime.datetime = parse_time(row['EndTime'])
                    channel = Channel(location_code=row['Location'], code=row['Channel'], latitude=row['Latitude'],
                                      longitude=row['Longitude'], elevation=row['Elevation'], depth=row['Depth'],
                                      dip=row['Dip'], azimuth=row['Azimuth'],
                                      sample_rate=row['SampleRate'],
                                      start_time=start_time, end_time=end_time)
                    channel.sensitivity = Sensitivity(value=row['Scale'], frequency=row['ScaleFreq']
                                                      , unit=row['ScaleUnits'])
                    station.add(channel)
                    channel.sensor = Sensor(description=row['SensorDescription'])
                return list(networks.values())
        else:
            raise HttpError(response.status_code, response.reason)
