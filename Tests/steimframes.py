import unittest

import array

from Codec.Steim import SteimFrame


class TestFrames(unittest.TestCase):

    def test_frame_len(self):
        frame = SteimFrame()
        self.assertEqual(0, len(frame))
        frame.append(0, 2)
        self.assertEqual(1, len(frame))

    def test_frame_is_empty(self):
        frame = SteimFrame()
        self.assertTrue(frame.is_empty())

    def test_frame_is_full(self):
        frame = SteimFrame()
        self.assertTrue(frame.is_empty())
