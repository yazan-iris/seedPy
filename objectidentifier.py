from typing import Dict


class ObjectIdentifier:
    def __init__(self, network: str, station: str, location: str, channel: str):
        if network is None or station is None or location is None or channel is None:
            raise ValueError
        self._network = network
        self._station = station
        self._location = location
        self._channel = channel
        self._segments = list()

    @property
    def network(self) -> str:
        return self._network

    @property
    def station(self) -> str:
        return self._station

    @property
    def location(self) -> str:
        return self._location

    @property
    def channel(self) -> str:
        return self._channel

    def __eq__(self, other):
        if other is None or not isinstance(other, ObjectIdentifier):
            return True
        if self._network != other._network or self._network != other._network or self._network != other._network \
                or self._channel != other.channel:
            return False
        return True

    # def __hash__(self):
    #   return hash(self._network, self.station, self.location, self.channel)

    def __str__(self):
        return self._network + '/' + self._station + '/' + self._location + '/' + self._channel

    def __repr__(self):
        return type(
            self).__name__ + '(' + self._network + ',' + self._station + ',' + self._location + ',' + self._channel + ',' + ')'

    def to_dictionary(self) -> Dict:
        return {'network': self._network, 'station': self._station, 'location': self._location,
                'channel': self._channel}
