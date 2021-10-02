```python
#does not make sense
parser = SeedFormat.parse('/path/to/file.mseed')
```

```python
#does not make sense
SeedFormat.version(3).writer('/path/to/file.mseed').write(records)
```

```python
record_header = SeedFile.open('/path/to/file.mseed').read(sequence=3, header_only=True)
```

```python
with file = SeedFile.open(''):
    while record= file.read():
        print(record)
```
```python
        with importlib.resources.path('Tests', 'fdsnws-dataselect_2020-03-28t21_11_14z.mseed') as file, \
                RecordIO.iterate(file) as iterator:
            for record in iterator:
                print(record)
                print(len(record.data))
                blockettes = record.blockettes
                for blockette in blockettes:
                    print(blockette)
```
```python
encoder = encoders.get(EncodingFormat.STEIM_1, byte_order=ByteOrder.BIG_ENDIAN)
```