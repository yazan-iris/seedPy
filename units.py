from pint import UnitRegistry, Quantity, Unit

ureg = UnitRegistry()


class GroundMotion:
    def __init__(self):
        super().__init__()

    @staticmethod
    def is_displacement(value) -> bool:
        if value is None:
            raise ValueError
        if isinstance(value, Quantity):
            value = value.units
        if not isinstance(value, Unit):
            raise ValueError
        dimensionality = value.dimensionality
        for dim in dimensionality:
            print(f'{dim}  {type(dim)}')
        print(type(dimensionality))

    @staticmethod
    def is_velocity(value) -> bool:
        if value is None:
            raise ValueError

    @staticmethod
    def is_acceleration(value) -> bool:
        if value is None:
            raise ValueError


class Displacement(Quantity):
    def __init__(self, value, units=None):
        super(Displacement, self).__init__(value=value, unit=units)


class Velocity(Quantity):
    def __init__(self, value, units=None):
        super(Velocity, self).__init__(value=value, unit=units)


class Acceleration(Quantity):
    def __init__(self, value, units=None):
        super(Acceleration, self).__init__(value=value, unit=units)


class SI:
    METER = ureg.meter
    SECOND = ureg.second
    #MOLE = u_reg.register(BaseUnit('mol', 'Mole', AmountDimension()), 'mol', ['mole', 'moles'])
    #AMPERE = u_reg.register(BaseUnit('A', 'Ampere', ElectricCurrentDimension()), 'A',
                            #['amp', 'amps', 'ampere', 'amperes'])
    #KELVIN = u_reg.register(BaseUnit('K', 'Kelvin', TemperatureDimension()), 'k', ['kelvin', 'kelvins'])
    #CANDELA = u_reg.register(BaseUnit('cd', 'Candela', LuminousIntensityDimension()), 'Kg',
                             #['candela', 'candelas', 'cd'])
    #KILOGRAM = u_reg.register(BaseUnit('Kg', 'Kilogram', MassDimension()), 'Kg', ['kilogram', 'kilograms'])
