import csv
import os
from typing import Iterable, Any, List, Dict

from timeseries import Trace


class GeoCSVField:
    def __init__(self, field_name: str, field_type, field_unit):
        self._field_name = field_name
        self._field_type = field_type
        self._field_unit = field_unit

    @property
    def field_name(self):
        return self._field_name

    @property
    def field_type(self):
        return self._field_type

    @property
    def field_unit(self):
        return self._field_unit

    def __str__(self):
        return self._field_name + self._field_type + self.field_unit


class GeoCSVHeader:
    def __init__(self, parameters: Dict):
        if parameters:
            self._parameters = parameters
        else:
            self._parameters = dict()
        self._fields: Iterable[Iterable[GeoCSVField]] = list()

    @property
    def parameters(self) -> Dict:
        return self._parameters

    @parameters.setter
    def parameters(self, parameters: Dict):
        self._parameters = parameters

    @property
    def fields(self) -> Iterable[Iterable[GeoCSVField]]:
        return self._fields

    @fields.setter
    def fields(self, fields: Iterable[Iterable[GeoCSVField]]):
        self._fields = fields


class GeoCSVFormat:
    def __init__(self, delimiter=' '):
        if not delimiter:
            raise ValueError
        self._delimiter = delimiter

    @property
    def delimiter(self) -> str:
        return self._delimiter


class GeoCSV:
    def __init__(self, csv_file, geo_csv_format: GeoCSVFormat = GeoCSVFormat(','), header: GeoCSVHeader = None):
        if geo_csv_format:
            self._formatter = geo_csv_format
        else:
            self._formatter = GeoCSVFormat()

        if not hasattr(csv_file, 'write'):
            csv_file = open(csv_file, 'w')
        self._csv_file = csv_file
        self._csv = csv.writer(csv_file, delimiter=self._formatter.delimiter,
                                  quotechar='|', quoting=csv.QUOTE_MINIMAL)

        self._header = header
        self.write_header()

    def write_header(self):
        self.write_header_parameter('dataset', 'GeoCSV 2.0')
        self.write_header_parameter('delimiter', self._formatter.delimiter)
        if not self._header:
            return
        for key, value in self._header.parameters.items():
            self.write_header_parameter(key, value)
        self.write_fields()

    def write_comment(self, comment: str):
        pass

    def writerows(self, rows: Iterable[Iterable[Any]]) -> None:
        self._csv.writerows(rows)

    def writerow(self, row: Iterable[Any]) -> Any:
        self._csv.writerow(row)

    def write_header_parameter(self, key: str, value):
        self.write_line(f'# {key}: {value}')

    def write_fields(self):
        names = list()
        for field in self._header.fields:
            names.append(field.field_name)
            self.write_header_parameter('field_unit', field.field_unit)
            self.write_header_parameter('field_type', field.field_type)
        self.write_line(self._formatter.delimiter.join(names))

    def write_line(self, line: str):
        self._csv_file.write(f'{line}{os.linesep}')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._csv_file and not self._csv_file.closed:
            self._csv_file.close()


class SeedGeoCSV(GeoCSV):
    def __init__(self, csv_file, geo_csv_format: GeoCSVFormat = GeoCSVFormat(','), header: GeoCSVHeader = None):
        super(SeedGeoCSV, self).__init__(csv_file=csv_file, geo_csv_format=geo_csv_format, header=header)

    def write_trace(self, trace: Trace):
        if trace is None:
            raise ValueError
        x = trace.x
        y = trace.y
        length: int = len(x)
        if length != len(y):
            raise ValueError
        print(f'printing.......{length}')
        for i in range(0, length):
            self.write_row(x[i], y[i])

    def write_row(self, time, sample: int):
        self.write_line(f'{time}{self._formatter.delimiter}{sample}')


def write_trace(file, trace: Trace):
    if trace is None:
        raise ValueError
