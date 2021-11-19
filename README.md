Simple API for reading and writing seed data records.

```python
import seed
seed.get_record_length('/path/to/file.mseed')
seed.count('/path/to/file.mseed')
```
```python
with seed.iterate('/path/to/file.mseed') as iterator:
    for record in iterator:
        print(record.header)
```
```python
seed.print('/path/to/file.mseed')
```
```python
records = seed.read('/path/to/file.mseed')
for record in records:
    print(record.header)
```
```python
seed.trace('/path/to/file.mseed')
```
```python
seed.plot('/path/to/file.mseed')
```
```python
seed.reformat('/path/to/file.mseed')
```
```python
seed.write('/path/to/file.mseed')
```
```python
seed.fetch('/path/to/file.mseed')
```
```python
seed.convert('/path/to/file.mseed')
```

