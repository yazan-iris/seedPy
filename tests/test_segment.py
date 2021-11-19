import datetime
import unittest

import array

from timeseries import Segment


class TestSegment(unittest.TestCase):

    def test_samples(self):
        start_time: datetime.datetime = datetime.datetime(year=2019, month=5, day=18, hour=15, minute=17, second=22,
                                                          tzinfo=datetime.timezone.utc)
        samples = array.array("i", range(0, 1500))
        segment: Segment = Segment(start_time=start_time, sample_rate=20, samples=samples)
        self.assertSequenceEqual(samples, segment.samples)

    def test_time(self):
        now: datetime = datetime.datetime.now()

        then = datetime.datetime.fromisocalendar(year=2021, week=23, day=3)
        print(f'{now}    {then}')
        duration = now - then
        print(duration.microseconds)
        print(duration.seconds)
        print(duration.total_seconds())

        start_time: datetime.datetime = datetime.datetime(year=2019, month=5, day=18, hour=15, minute=17, second=22,
                                                          tzinfo=datetime.timezone.utc)

        samples = array.array("i", range(0, 1500))

        seg1 = Segment(start_time=start_time, sample_rate=20, samples=samples)
        print(seg1)
        print(seg1.duration)

        seg1.overlap()
        seg1.is_before_or_equal()
        seg1.merge()
        seg1.samples
