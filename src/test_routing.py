import pytest
from src.routing import route_package_train


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


def test_invalid_route():
    stations = ['A', 'F']
    routes = [
        ('E2', 'A', 'F', 3),
        ('E1', 'A', 'A', 3)
    ]
    deliveries = [
        ('P1', 'A', 'F', 5),
    ]
    trains = [
        ('Q1', 'A', 6)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_repeated_station():
    stations = ['A', 'A']
    routes = [
        ('E1', 'A', 'C', 3)
    ]
    deliveries = [
        ('P1', 'A', 'C', 5),
    ]
    trains = [
        ('Q1', 'A', 6)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_repeated_route():
    stations = ['A', 'E', 'C']
    routes = [
        ('E1', 'A', 'C', 3),
        ('E1', 'A', 'E', 3)
    ]
    deliveries = [
        ('P1', 'A', 'C', 5),
    ]
    trains = [
        ('Q1', 'A', 6)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_repeated_delivery():
    stations = ['A', 'E', 'C']
    routes = [
        ('E1', 'A', 'C', 3),
        ('E2', 'A', 'E', 3)
    ]
    deliveries = [
        ('P1', 'A', 'C', 5),
        ('P1', 'A', 'E', 3),
    ]
    trains = [
        ('Q1', 'A', 6)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_repeated_train():
    stations = ['A', 'Z', 'C']
    routes = [
        ('E1', 'A', 'C', 3),
        ('E2', 'A', 'Z', 3)
    ]
    deliveries = [
        ('P1', 'A', 'C', 5),
        ('P2', 'A', 'Z', 3),
    ]
    trains = [
        ('Q1', 'A', 6),
        ('Q1', 'A', 6)
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


def test_invalid_pickup_path():
    stations = ['A', 'Q', 'C']
    routes = [
        ('E1', 'A', 'Q', 3)
    ]
    deliveries = [
        ('P1', 'A', 'Q', 5),
    ]
    trains = [
        ('Q1', 'C', 6)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_invalid_pickup_weight():
    stations = ['A', 'D', 'C']
    routes = [
        ('E1', 'A', 'D', 3),
        ('E2', 'C', 'D', 2)
    ]
    deliveries = [
        ('P1', 'A', 'C', 5),
    ]
    trains = [
        ('Q1', 'C', 3),
        ('Q2', 'D', 2)
    ]
    with pytest.raises(ValueError):
        route_package_train(stations, routes, deliveries, trains)


def test_ground_scenario():
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


def test_inventory():
    stations = ['A', 'B', 'C']
    routes = [
        ('E1', 'A', 'B', 3),
        ('E2', 'B', 'C', 1)
    ]
    deliveries = [
        ('P1', 'A', 'C', 5),
        ('P2', 'A', 'B', 3)
    ]
    trains = [
        ('Q1', 'B', 6),
        ('Q2', 'C', 5)
    ]
    route_package_train(stations, routes, deliveries, trains)


def test_hitchhike():
    stations = ['A', 'B', 'C', 'D']
    routes = [
        ('E1', 'A', 'B', 5),
        ('E2', 'A', 'C', 1),
        ('E3', 'A', 'D', 2)
    ]
    deliveries = [
        ('P1', 'D', 'B', 1),
        ('P2', 'D', 'C', 2),
        ('P3', 'B', 'C', 6)
    ]
    trains = [
        ('Q1', 'D', 3),
        ('Q2', 'C', 6)
    ]
    route_package_train(stations, routes, deliveries, trains)


def test_disconnected_graph():
    stations = ['A', 'B', 'C', 'E', 'F', 'G']
    routes = [
        ('E1', 'A', 'B', 5),
        ('E2', 'A', 'C', 2),
        ('E3', 'E', 'F', 8),
        ('E4', 'G', 'F', 3)
    ]
    deliveries = [
        ('P1', 'B', 'C', 1),
        ('P2', 'A', 'C', 4),
        ('P3', 'G', 'G', 3),
        ('P4', 'F', 'G', 8)
    ]
    trains = [
        ('Q1', 'B', 6),
        ('Q2', 'C', 4),
        ('Q3', 'G', 11),
        ('Q4', 'F', 8),
    ]
    route_package_train(stations, routes, deliveries, trains)


def test_10_node_graph():
    stations = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'L', 'M']
    routes = [
        ('E1', 'A', 'B', 1),
        ('E2', 'A', 'C', 1),
        ('E3', 'A', 'G', 2),
        ('E4', 'B', 'C', 1),
        ('E5', 'B', 'D', 2),
        ('E6', 'C', 'E', 3),
        ('E7', 'C', 'D', 2),
        ('E8', 'D', 'E', 4),
        ('E9', 'E', 'F', 2),
        ('E10', 'F', 'H', 100),
        ('E11', 'F', 'J', 4),
        ('E12', 'H', 'L', 5),
        ('E13', 'L', 'M', 2),
    ]
    deliveries = [
        ('P1', 'A', 'C', 1),
        ('P2', 'G', 'D', 3),
        ('P3', 'G', 'E', 10),
        ('P4', 'A', 'L', 20),
        ('P5', 'C', 'G', 6),
        ('P6', 'C', 'B', 1),
        ('P7', 'F', 'B', 1),
        ('P8', 'L', 'M', 1),
        ('P9', 'H', 'M', 2),
        ('P10', 'C', 'J', 4)
    ]
    trains = [
        ('Q1', 'G', 3),
        ('Q2', 'D', 100),
        ('Q3', 'C', 5),
        ('Q4', 'J', 7),
        ('Q5', 'J', 3),
        ('Q6', 'J', 5),
    ]
    route_package_train(stations, routes, deliveries, trains)


if __name__ == '__main__':
    # test_ground_scenario()
    # test_inventory()
    # test_hitchhike()
    # test_disconnected_graph()
    test_10_node_graph()
