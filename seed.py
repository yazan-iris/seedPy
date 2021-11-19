import datetime
import profile

import h5py
import pyarrow.parquet as pq
import pyarrow as pa
import xarray as xarray

import seedio
from geocsv import GeoCSVHeader, GeoCSVField, SeedGeoCSV
from seedio import RecordIterator
from timeseries import Trace
import fdsn

get_record_length = seedio.get_record_length


def count(source) -> int:
    with RecordIterator(source, header_only=True) as iterator:
        cnt: int = 0
        for record in iterator:
            cnt += 1
        return cnt


def iterate(source, decompress: bool = False):
    return RecordIterator(source, decompress=decompress)


def read(source, decompress: bool = False):
    with iterate(source, decompress) as iterator:
        records = list()
        for record in iterator:
            records.append(record)
        return records


def trace(source, decompress: bool = False) -> Trace:
    if source is None:
        raise ValueError
    with iterate(source, decompress=decompress) as iterator:
        t: Trace = None
        for record in iterator:
            if t is None:
                t = Trace.with_network_station_location_channel(record.network_code, record.station_code,
                                                                record.channel_location_code,
                                                                record.channel_code)
            t.add(record=record)
        if trace is None:
            raise RuntimeError
        return t


def convert(source, destination, data_format: str = None):
    if data_format == 'parquet':
        to_parquet(source, destination)
    elif data_format == 'geocsv':
        to_geocsv(source, destination)
    elif data_format == 'hdf5':
        to_hdf5(source, destination)
    elif data_format == 'netcdf':
        to_netcdf(source, destination)
    else:
        raise NotImplementedError(data_format)


def to_geocsv(source, destination):
    t = trace(source=source, decompress=True)
    if t:
        params = t.object_identifier.to_dictionary()
        params['start'] = '2012-01-01T10:00:00'
        params['end'] = '2012-04-01T10:00:00'
        params['level'] = 'cha'
        params['format'] = 'text'
        networks = fdsn.HttpClient('service.iris.edu').fetch(params)
        if not networks or len(networks) == 0:
            raise RuntimeError
        network: fdsn.Network = networks[0]
        station: fdsn.Station = network.stations[0]
        channel: fdsn.Channel = station.channels[0] if len(station.channels) > 0 else None
        if channel is None:
            raise RuntimeError
        header = GeoCSVHeader(parameters={'sample_count': t.number_of_samples, 'sample_rate_hz': 20,
                                          'start_time': t.start_time, 'latitude_deg': channel.latitude,
                                          'longitude_deg': channel.longitude,
                                          'elevation_m': channel.elevation, 'depth_m': channel.depth,
                                          'azimuth_deg': channel.azimuth, 'dip_deg': channel.dip,
                                          'instrument': channel.sensor.description,
                                          'scale_factor': channel.sensitivity.value,
                                          'scale_frequency_hz': channel.sensitivity.frequency,
                                          'scale_units': channel.sensitivity.unit})

        header.fields = [GeoCSVField(field_name='time', field_type=datetime.datetime, field_unit='utc'),
                         GeoCSVField(field_name='Count', field_type=int, field_unit='integer')]
        with SeedGeoCSV(destination, header=header) as geo_csv:
            geo_csv.write_trace(t)
    else:
        raise IOError


def to_parquet(source, destination):
    if source is None or destination is None:
        raise ValueError
    t = trace(source=source, decompress=True)
    if t:
        x = pa.array(t.x)
        y = pa.array(t.y)
        table = pa.Table.from_arrays([x, y],
                                     schema=pa.schema(
                                         [pa.field('timestamp', pa.timestamp(unit='ms')), pa.field('sample',
                                                                                                   type=pa.int32())]))
        pq.write_table(table, destination)
    else:
        raise IOError


def to_hdf5(source, destination):
    if source is None or destination is None:
        raise ValueError
    t = trace(source=source, decompress=True)
    if t:
        with h5py.File(destination, 'w') as h5f:
            data_set = h5f.create_dataset(str(t.object_identifier), dtype=('int64', 'int64'),
                                          data=[t.get_x(dtype='int'), t.y],
                                          compression='gzip', chunks=True)
    else:
        raise IOError


def to_netcdf(source, destination):
    if source is None or destination is None:
        raise ValueError
    t = trace(source=source, decompress=True)
    if t:
        #dates = [datetime.datetime(2001, 1, 1, 15) + datetime.timedelta(hours=i) for i in range(len(t.x))]
        scheme = {
            "name": "the name",
            "data": t.y,
            "dims": "time",
            "coords": {"time": {"dims": "time", "data": t.x}},
            'attrs': dict(
                title='the title',
                description=str(t.object_identifier),
                units="the unit")
        }
        xarray.DataArray.from_dict(scheme).to_netcdf(destination)
    else:
        raise IOError


fetch = fdsn.fetch
