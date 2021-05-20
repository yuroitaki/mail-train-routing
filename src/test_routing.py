import pytest
from src.routing import route_package_train


def test_simplest_scenario():
    stations = ['A', 'B', 'C']
    routes = [
        ('E1', 'A', 'B', 3),
        ('E2', 'B', 'C', 1)
    ]
    deliveries = [
        ('P1', 'A', 'C', 5),
        ('P2', 'B', 'C', 3)
    ]
    trains = [
        ('Q1', 'B', 6),
        ('Q2', 'C', 5)
    ]
    route_package_train(stations, routes, deliveries, trains)


def test_invalid_input_dictionary():
    stations = []
    routes = {}
    deliveries = []
    trains = []
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_invalid_input_empty():
    stations = []
    routes = []
    deliveries = []
    trains = []
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_invalid_station():
    stations = ['A', 'B']
    routes = [
        ('E1', 'A', 'C', 3)
    ]
    deliveries = [
        ('P1', 'A', 'C', 5),
    ]
    trains = [
        ('Q1', 'B', 6)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_invalid_weight():
    stations = ['A', 'C']
    routes = [
        ('E1', 'A', 'C', 3)
    ]
    deliveries = [
        ('P1', 'A', 'C', -5),
    ]
    trains = [
        ('Q1', 'A', 6)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_invalid_delivery_path():
    stations = ['A', 'D', 'C']
    routes = [
        ('E1', 'A', 'C', 3)
    ]
    deliveries = [
        ('P1', 'A', 'D', 5),
    ]
    trains = [
        ('Q1', 'C', 6)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


if __name__ == '__main__':
    test_simplest_scenario()
