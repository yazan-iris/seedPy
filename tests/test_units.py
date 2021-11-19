import unittest

from pint import UnitRegistry, Quantity

from units import SI, Velocity, Displacement, GroundMotion


class TestUnits(unittest.TestCase):

    def test_pine(self):
        ureg = UnitRegistry()
        print(ureg.meter)
        u = SI.METER

        print(type(ureg.meter))



        print(u.dimensionality)

        distance = 1 * SI.METER

        time = 1 * SI.SECOND
        velocity = distance / time
        print(velocity)
        print(f"xxx: {velocity.check('[length]')}")
        print(f"xxx: {velocity.check('[time]')}")
        self.assertTrue(GroundMotion.is_displacement(velocity))

