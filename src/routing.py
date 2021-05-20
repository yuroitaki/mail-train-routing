import networkx as nx

from src.package import Package
from src.train import Train


def validate_input(stations, routes, deliveries, trains):
    if not isinstance(stations, list):
        raise ValueError('STATIONS_MUST_BE_A_LIST')
    if not isinstance(routes, list):
        raise ValueError('ROUTES_MUST_BE_A_LIST')
    if not isinstance(deliveries, list):
        raise ValueError('DELIVERIES_MUST_BE_A_LIST')
    if not isinstance(trains, list):
        raise ValueError('TRAINS_MUST_BE_A_LIST')

    if len(stations) == 0:
        raise ValueError('NO_STATION_DEFINED')
    if len(routes) == 0:
        raise ValueError('NO_ROUTE_DEFINED_BETWEEN_STATION')
    if len(deliveries) == 0:
        raise ValueError('NO_DELIVERIES_TO_BE_MADE')
    if len(trains) == 0:
        raise ValueError('NO_TRAIN_TO_DELIVER')

    try:
        stations = [str(station) for station in stations]
        for i in range(len(routes)):
            route_name, left_station, right_station, time_cost = routes[i]
            if int(time_cost) <= 0:
                raise ValueError('ROUTE_TIME_COST_MUST_BE_BIGGER_THAN_ZERO')
            if str(left_station) not in stations or str(right_station) not in stations:
                raise ValueError('MISSING_STATION_IN_STATIONS')
            routes[i] = (
                str(route_name),
                str(left_station),
                str(right_station),
                int(time_cost)
            )
        for i in range(len(deliveries)):
            package_name, origin, destination, package_weight = deliveries[i]
            if int(package_weight) <= 0:
                raise ValueError('PACKAGE_WEIGHT_MUST_BE_BIGGER_THAN_ZERO')
            if str(origin) not in stations or str(destination) not in stations:
                raise ValueError('MISSING_STATION_IN_STATIONS')
            deliveries[i] = (
                str(package_name),
                str(origin),
                str(destination),
                int(package_weight)
            )
        for i in range(len(trains)):
            train_name, train_station, train_max_capacity = trains[i]
            if int(train_max_capacity) <= 0:
                raise ValueError('TRAIN_MAX_CAPACITY_MUST_BE_BIGGER_THAN_ZERO')
            if str(train_station) not in stations:
                raise ValueError('MISSING_STATION_IN_STATIONS')
            trains[i] = (
                str(train_name),
                str(train_station),
                int(train_max_capacity)
            )
    except Exception as e:
        raise e


def construct_train_network(stations, routes):
    station_map = dict()
    train_network = nx.Graph()
    for position, name in enumerate(stations):
        station_map[name] = position
        train_network.add_node(position, name=name)

    for route in routes:
        route_name, left_station, right_station, time_cost = route
        train_network.add_edge(
            station_map[left_station],
            station_map[right_station],
            weight=time_cost,
            name=route_name
        )
    return train_network, station_map


def construct_packages(deliveries, station_map):
    package_collections = list()
    station_inventory = dict()
    for delivery in deliveries:
        name, origin, destination, weight = delivery
        package_collections.append(
            Package(
                name,
                station_map[origin],
                station_map[destination],
                weight
            )
        )
        station_inventory[station_map[origin]] = {name: None}
    return package_collections, station_inventory


def construct_trains(trains, station_map):
    train_collections = list()
    for train in trains:
        name, station, max_capacity = train
        train_collections.append(
            Train(
                name,
                station_map[station],
                max_capacity
            )
        )
    return train_collections


def get_shortest_path_info(left_node, right_node, shortest_paths):
    try:
        time_cost, path = shortest_paths[left_node][right_node]
        return time_cost, path
    except TypeError as _e:
        return None, None


def set_shortest_path_info(
    left_node,
    right_node,
    time_cost,
    path,
    shortest_paths
):
    shortest_paths[left_node][right_node] = time_cost, path
    shortest_paths[right_node][left_node] = time_cost, path


def compute_shortest_path(
    left_node,
    right_node,
    shortest_paths,
    train_network
):
    time_cost, path = get_shortest_path_info(
        left_node,
        right_node,
        shortest_paths
    )
    if time_cost is None or path is None:
        try:
            time_cost = nx.dijkstra_path_length(
                train_network,
                left_node,
                right_node
            )
            path = nx.dijkstra_path(
                train_network,
                left_node,
                right_node
            )
            set_shortest_path_info(
                left_node,
                right_node,
                time_cost,
                path,
                shortest_paths
            )
        except nx.NetworkXNoPath as _e:
            raise ValueError('NO_PATH_TO_DELIVER_PACKAGE')

    return time_cost, path


def compute_delivery_shortest_paths(
    package_collections,
    shortest_paths,
    train_network
):
    for package in package_collections:
        compute_shortest_path(
            package.origin(),
            package.destination(),
            shortest_paths,
            train_network
        )


def route_package_train(stations, routes, deliveries, trains):
    validate_input(stations, routes, deliveries, trains)

    train_network, station_map = construct_train_network(stations, routes)
    no_of_station = len(station_map)

    # print('train network', train_network[0])
    # print('train_node', train_network.nodes[0]['name'])
    # print('train_edge', train_network[0][1]['name'])
    # print('station_map', station_map)

    train_collections = construct_trains(trains, station_map)
    package_collections, station_inventory = construct_packages(
        deliveries,
        station_map
    )
    shortest_paths = [[None for i in range(no_of_station)] for j in range(no_of_station)]
    compute_delivery_shortest_paths(
        package_collections,
        shortest_paths,
        train_network
    )
    pass
