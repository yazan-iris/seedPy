import unittest

from Codec.Steim import ControlSequence


class TestControl(unittest.TestCase):

    def test_control_sequence(self):
        control = ControlSequence()
        self.assertEqual(0, control)
        self.assertEqual('00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00', str(control))
        self.assertEqual(0, control[0])

        control[0] = 2
        control[1] = 1
        control[2] = 2

        val = control[2]
        self.assertEqual(2, control[2])
        self.assertEqual(2550136832, int(control))

        for c in control:
            print(c)

        cs = ControlSequence(value=2550136832)
        print(str(cs))
        self.assertEqual(2, control[0])
        self.assertEqual(1, control[1])
        self.assertEqual(2, control[2])
        # ControlSequence.from_binary_sequence()
        # ControlSequence.get()
        # ControlSequence.is_empty()
        # ControlSequence.set()
