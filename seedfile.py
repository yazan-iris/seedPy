from seed import DataRecord
from seedio import RecordIterator
from timeseries import Timeseries


class SeedError(Exception):
    """Base exception."""
    pass


class ExtractError(SeedError):
    """General exception for extract errors."""
    pass


class ReadError(SeedError):
    """Exception for unreadable tar archives."""
    pass


class CompressionError(SeedError):
    """Exception for unavailable compression methods."""
    pass


class SeedFile(object):
    def __init__(self, name=None, mode="r", fileobj=None, format=None,
                 tarinfo=None, dereference=None, ignore_zeros=None, encoding=None,
                 errors="surrogateescape", pax_headers=None, debug=None,
                 error_level=None, copybufsize=None):
        self._file = None
        self._position: int = 0
        self._closed: bool = False
        self._iterator = RecordIterator(fileobj)
        self._record_length = self._iterator.record_length

    def read_records(self) -> list[DataRecord]:
        records = list()
        for record in self._iterator:
            records.append(record)
        return records

    def read_record(self, record_number: int = None) -> DataRecord:
        if record_number is None:
            return self._iterator.__next__()
        else:
            if record_number < 0:
                raise ValueError(f'Expected a value >= 0 but received {record_number}')
            position: int = self._record_length * record_number

    def tell(self):
        """Return the stream's file pointer position.
        """
        return self._position

    def __iter__(self):
        return self

    def __next__(self):
        self._iterator.__next__()

    def close(self):
        """Close the _Stream object. No operation should be
           done on it afterwards.
        """
        if self._closed:
            return

        try:
            pass
        finally:
            self._iterator.close()
            self._file.close()
            self._closed = True

    @classmethod
    def open(cls, name, mode="r", fileobj=None, **kwargs):
        """Open uncompressed tar archive name for reading or writing.
        """
        if mode not in ("r", "a", "w", "x"):
            raise ValueError("mode must be 'r', 'a', 'w' or 'x'")
        return cls(name, mode, fileobj, **kwargs)


def is_seed_file(name):
    """Return True if name points to a seed file that we
       are able to handle, else return False.

       'name' should be a string, file, or file-like object.
    """
    try:
        if hasattr(name, "read"):
            t = open(fileobj=name)
        else:
            t = open(name)
        return True
    except SeedError:
        return False
    finally:
        t.close()


def open_as_series() -> Timeseries:
    pass


open = SeedFile.open

series = open_as_series()
