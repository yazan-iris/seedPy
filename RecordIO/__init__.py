import os
import re
from io import BufferedReader, BytesIO
from pathlib import PosixPath

from Seed import SeedFormatV2, SeedFormatV3, SeedFormat, DataRecord, DataHeader, BlocketteFactory


class RecordIterator:
    def __init__(self, source):
        if not source:
            raise ValueError()
        if type(source) is str and os.path.isfile(source):
            source = open(source, "rb")
        elif isinstance(source, PosixPath):
            source = open(source, "rb")
        elif isinstance(source, bytes):
            source = BufferedReader(BytesIO(source))
        elif isinstance(source, BytesIO):
            source = BufferedReader(source)
        else:
            raise ValueError("Incorrect source parameters: must be path to file or io.BufferedReader {}", type(source))

        if isinstance(source, BufferedReader):
            reader = source
        else:
            reader = BufferedReader(source)

        chunk = reader.read(8)
        source.seek(0)
        if SeedFormatV2.RECORD_HEADER.match(chunk.decode('ascii')):
            self.parser = Parser(SeedFormatV2(), reader)
        elif SeedFormatV3.RECORD_HEADER.match(chunk.decode('ascii')):
            self.parser = Parser(SeedFormatV3(), reader)
        else:
            raise ValueError("Invalid Seed format")
        self._closed = False

    def close(self):
        if self.parser:
            try:
                self.parser.close()
            except:
                pass
        self._closed = True

    def __iter__(self):
        return self

    def __next__(self):
        if not self.parser or self._closed:
            return None
        record = self.parser.next_record()
        if not record:
            raise StopIteration
        return record

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Parser:

    def __init__(self, seed_format: SeedFormat, reader: BufferedReader):
        if seed_format is None:
            raise ValueError
        if reader is None:
            raise ValueError
        self.seed_format = seed_format
        self.reader = reader
        self.closed = False
        self.record_length = get_record_length(reader)

    def byte_offset(self):
        return self.reader.tell()

    def next_record(self) -> DataRecord:
        b_bytes = self.reader.read(self.record_length)
        if b_bytes is None or len(b_bytes) == 0:
            return None
        print(len(b_bytes))
        header = DataHeader.from_bytes(b_bytes)
        record = DataRecord(header)
        offset = header.first_blockette
        for i in range(0, header.number_of_blockettes_that_follow):
            blockette = BlocketteFactory.create(b_bytes, header.byte_order, offset)
            offset += blockette.next_blockette_byte_number
            record.append(blockette)
        record.data = b_bytes[header.beginning_of_data: self.record_length]
        return record

    def close(self):
        if self.reader:
            try:
                self.reader.close()
            except:
                pass
        self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def parse(source, seed_format: SeedFormat):
    if not source:
        raise ValueError()
    if type(source) is str and os.path.isfile(source):
        source = open(source, "rb")
    elif isinstance(source, PosixPath):
        source = open(source, "rb")
    elif isinstance(source, bytes):
        source = BufferedReader(BytesIO(source))
    elif isinstance(source, BytesIO):
        source = BufferedReader(source)
    else:
        print(type(source))
        raise ValueError("Incorrect source parameters: must be path to file or io.BufferedReader {}", type(source))

    if isinstance(source, BufferedReader):
        reader = source
    else:
        reader = BufferedReader(source)
    chunk = reader.read(8)
    source.seek(0)
    if SeedFormatV2.RECORD_HEADER.match(chunk.decode('ascii')):
        return Parser(SeedFormatV2(), reader)
    elif SeedFormatV2.RECORD_HEADER.match(chunk.decode('ascii')):
        return Parser(SeedFormatV3(), reader)
    else:
        raise ValueError("Invalid Seed format")


def iterate(source) -> RecordIterator:
    return RecordIterator(source)


record_header = re.compile(r'^\d{6}[VASTDRQM]')
record_minimum_length = 2 ** 8
record_preferred_length = 2 ** 12
record_maximum_length = 2 ** 15


def get_record_length(source, **kwargs) -> int:
    if not source:
        raise ValueError('source cannot be None')
    close_source = False
    if kwargs.get('close'):
        close_source = True

    if not hasattr(source, "read"):
        close_source = True
        source = open(source, "rb")
    record_size = 256
    chunk_size = 8
    source.seek(0)
    chunk = source.read(chunk_size)
    if not chunk:
        raise SyntaxError('Could not determine record size!')
    if not record_header.match(chunk.decode('ascii')):
        raise SyntaxError('Invalid seed file! [{}]'.format(chunk.decode('ascii')))
    try:
        while True:
            source.seek(record_size)
            chunk = source.read(8)
            if not chunk:
                pos = source.tell()
                '''we have reached end of file, it seems we only have one record,
                check the size (is power of 2) to confirm'''
                if (pos & (pos - 1) == 0) and pos != 0:
                    if record_minimum_length <= pos <= record_maximum_length:
                        return pos
                    else:
                        raise SyntaxError('could not determine record size!')
                else:
                    raise SyntaxError('could not determine record size!')
            try:
                if record_header.match(chunk.decode('ascii')):
                    return record_size
            except UnicodeDecodeError:
                pass
            record_size *= 2
    finally:
        if source is not None:
            source.seek(0)
            if close_source:
                try:
                    source.close()
                except:
                    pass
