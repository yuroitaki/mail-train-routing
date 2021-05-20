STATUS = {
    'pending': 'PENDING',
    'shipping': 'SHIPPING',
    'delivered': 'DELIVERED'
}


class Package:

    def __init__(self, name, origin, destination, weight):
        self._name = name
        self._origin = origin
        self._destination = destination
        self._weight = weight

        if origin == destination:
            self._status = STATUS['delivered']
        else:
            self._status = STATUS['pending']

    def name(self):
        return self._name

    def origin(self):
        return self._origin

    def destination(self):
        return self._destination

    def weight(self):
        return self._weight

    def status(self):
        return self._status

    def load(self):
        self._status = STATUS['shipping']

    def drop(self, station):
        if station != self._destination:
            self._origin = station
        else:
            self._status = STATUS['delivered']
