import unittest
from collections import Sequence

from codec import ControlSequence, InvalidControlSequenceError
from codec import SteimError


class TestControl(unittest.TestCase):

    def test_control_sequence(self):
        cs = ControlSequence()
        self.assertEqual(0, int(cs))
        self.assertEqual('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00', str(cs))
        self.assertSequenceEqual(cs, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        cs = ControlSequence(0)
        self.assertEqual(0, int(cs))
        self.assertEqual('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00', str(cs))
        self.assertSequenceEqual(cs, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        cs = ControlSequence([0 for i in range(16)])
        self.assertEqual(0, int(cs))
        self.assertEqual('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00', str(cs))
        self.assertSequenceEqual(cs, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        seq = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        with self.assertRaises(InvalidControlSequenceError):
            cs = ControlSequence(seq)

        seq = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        cs = ControlSequence(seq)
        self.assertEqual(357913941, int(cs))
        self.assertEqual('00 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01', str(cs))

        cs = ControlSequence(357913941)
        self.assertEqual(357913941, int(cs))
        self.assertEqual('00 01 01 01 01 01 01 01 01 01 01 01 01 01 01 01', str(cs))

        seq = [1, 1, 1, 1, 1, 1, 1]
        with self.assertRaises(InvalidControlSequenceError):
            cs = ControlSequence(seq)

        cs = ControlSequence()
        with self.assertRaises(InvalidControlSequenceError):
            cs[0] = 1

        seq = [0, 1, 1, 1, 1, 1, 1]
        cs = ControlSequence(seq)
        self.assertEqual(357826560, int(cs))
        self.assertEqual('00 01 01 01 01 01 01 00 00 00 00 00 00 00 00 00', str(cs))

        cs = ControlSequence(357826560)
        self.assertEqual(357826560, int(cs))
        self.assertEqual('00 01 01 01 01 01 01 00 00 00 00 00 00 00 00 00', str(cs))

        cs = ControlSequence([0, 0, 0, 1, 2, 2, 1, 3])
        self.assertEqual(27721728, int(cs))
        self.assertEqual('00 00 00 01 10 10 01 11 00 00 00 00 00 00 00 00', str(cs))

        cs = ControlSequence()
        cs[0] = 0
        cs[1] = 0
        cs[2] = 0
        cs[3] = 1
        cs[4] = 2
        cs[5] = 2
        cs[6] = 1
        cs[7] = 3

        self.assertEqual(27721728, int(cs))
        self.assertEqual('00 00 00 01 10 10 01 11 00 00 00 00 00 00 00 00', str(cs))

        with self.assertRaises(SteimError):
            cs[8] = 4
        self.assertEqual(27721728, int(cs))
        self.assertEqual('00 00 00 01 10 10 01 11 00 00 00 00 00 00 00 00', str(cs))
        self.assertSequenceEqual(cs, [0, 0, 0, 1, 2, 2, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0])

        cs[8] = 2
        cs[9] = 1
        cs[10] = 1
        cs[11] = 2
        self.assertEqual(27760128, int(cs))
        self.assertEqual('00 00 00 01 10 10 01 11 10 01 01 10 00 00 00 00', str(cs))
        self.assertSequenceEqual(cs, [0, 0, 0, 1, 2, 2, 1, 3, 2, 1, 1, 2, 0, 0, 0, 0])

        cs[12] = 2
        cs[13] = 2
        cs[14] = 2
        cs[15] = 2
        self.assertEqual(27760298, int(cs))
        self.assertEqual('00 00 00 01 10 10 01 11 10 01 01 10 10 10 10 10', str(cs))
        self.assertSequenceEqual(cs, [0, 0, 0, 1, 2, 2, 1, 3, 2, 1, 1, 2, 2, 2, 2, 2])
        with self.assertRaises(IndexError):
            cs[16] = 4

        with self.assertRaises(IndexError):
            cs[-1] = 4

        cs.reset()
        self.assertEqual(0, int(cs))
        self.assertEqual('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00', str(cs))
        self.assertSequenceEqual(cs, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        cs = ControlSequence(value=22369653)
        print(str(cs))

    def test_iter_sequence(self):
        cs = ControlSequence()
        for num in cs:
            self.assertEqual(0, num)
