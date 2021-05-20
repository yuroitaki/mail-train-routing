class Train:

    def __init__(self, name, station, max_capacity):
        self._name = name
        self._station = station
        self._max_capacity = max_capacity

        self._capacity = self.max_capacity
        self._packages = dict()

        self._elapsed_time = 0
        self._log = list()

    def locate(self):
        return self._station

    def move(self, next_station, journey_duration):
        self._station = next_station
        self._elapsed_time += journey_duration

    def load_package(self, package, destination):
        if self._capacity < package.weight():
            return False
        self._packages[destination] = { package.name(): None }
        self._capacity -= package.weight()
        return True

    def drop_package(self, package):
        packages_to_drop = self._packages.get(self._station, None)
        if packages_to_drop is None:
            raise ValueError('NO_PACKAGE_TO_DROP_AT_THIS_STATION')
        if package.name() not in packages_to_drop:
            raise ValueError('CANNOT_FIND_SELECTED_PACKAGE_TO_DROP')
        self._packages[self._station].pop(package.name())
        self._capacity += package.weight()

    def record_log(
        self,
        station_name,
        next_station_name,
        route_name,
        journey_duration,
        loaded_packages,
        dropped_packages
    ):
        self._log.append({
            'time': self._elapsed_time,
            'train': self._name,
            'station': station_name,
            'loaded_packages': loaded_packages,
            'dropped_packages': dropped_packages,
            'next_station': next_station_name
            'next_route': route_name,
            'next_journey_duration': journey_duration
        })

    def retrieve_log(self):
        return self._log