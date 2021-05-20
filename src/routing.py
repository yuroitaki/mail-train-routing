import math
import networkx as nx

from src.package import Package, STATUS
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
        if len(set(stations)) != len(stations):
            raise ValueError('DUPLICATED_STATION_NAME')

        route_names = list()
        for i in range(len(routes)):
            route_name, left_station, right_station, time_cost = routes[i]

            if left_station == right_station:
                raise ValueError('INVALID_ROUTE_CONNECTING_A_STATION_TO_ITSELF')

            if route_name in route_names:
                raise ValueError('DUPLICATED_ROUTE_NAME')
            route_names.append(route_name)

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

        package_names = list()
        for i in range(len(deliveries)):
            package_name, origin, destination, package_weight = deliveries[i]

            if package_name in package_names:
                raise ValueError('DUPLICATED_PACKAGE_NAME')
            package_names.append(package_name)

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

        train_names = list()
        for i in range(len(trains)):
            train_name, train_station, train_max_capacity = trains[i]

            if train_name in train_names:
                raise ValueError('DUPLICATE_TRAIN_NAME')
            train_names.append(train_name)

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
    for index, delivery in enumerate(deliveries):
        name, origin, destination, weight = delivery
        package_collections.append(
            Package(
                name,
                station_map[origin],
                station_map[destination],
                weight
            )
        )
        inventory = station_inventory.get(station_map[origin], None)
        if inventory is None:
            station_inventory[station_map[origin]] = {name: index}
        else:
            station_inventory[station_map[origin]][name] = index

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
        if package.status() == STATUS['delivered']:
            continue
        compute_shortest_path(
            package.origin(),
            package.destination(),
            shortest_paths,
            train_network
        )


def find_best_delivery_train(
    package,
    train_collections,
    shortest_paths,
    train_network
):
    delivery_train = None
    delivery_train_pickup_path = None
    delivery_train_pickup_cost = math.inf

    for train in train_collections:
        if train.max_capacity() < package.weight():
            continue

        try:
            pickup_time_cost, pickup_path = compute_shortest_path(
                train.locate(),
                package.origin(),
                shortest_paths,
                train_network
            )
        except ValueError as _e:
            continue

        pickup_cost = pickup_time_cost + train.elapsed_time()
        if pickup_cost < delivery_train_pickup_cost:
            delivery_train = train
            delivery_train_pickup_path = pickup_path
            delivery_train_pickup_cost = pickup_cost

    if delivery_train is None:
        raise ValueError('PACKAGE_CANNOT_BE_DELIVERED_BY_ANY_TRAIN')

    return delivery_train, delivery_train_pickup_cost, delivery_train_pickup_path


def combine_paths(left_path, right_path):
    combined_path = list()
    combined_path.extend(left_path)
    combined_path.extend(right_path[1:])
    return combined_path


def pop_station_inventory(package, station_inventory):
    inventory = station_inventory.get(package.origin(), None)
    if inventory is None:
        raise ValueError('MISSING_INVENTORY_AT_ORIGIN')
    if package.name() not in inventory:
        raise ValueError('MISSING_PACKAGE_AT_ORIGIN_INVENTORY')
    station_inventory[package.origin()].pop(package.name())


def load_package(package, train, destination, station_inventory):
    loading_result = train.load_package(package, destination)
    if not loading_result:
        return False
    package.load()
    pop_station_inventory(package, station_inventory)

    return True


def push_station_inventory(package, package_index, station, station_inventory):
    packages = station_inventory.get(station, None)
    if packages is None:
        station_inventory[station] = {package.name(): package_index}
    else:
        station_inventory[station][package.name()] = package_index


def drop_package(train, station, station_inventory, package_collections):
    packages_to_drop = train.packages_to_drop()
    if packages_to_drop is None or len(packages_to_drop) == 0:
        return False
    for package_name in packages_to_drop:
        package_index = packages_to_drop[package_name]
        package = package_collections[package_index]

        train.drop_package(package)
        package.drop(station)
        push_station_inventory(
            package,
            package_index,
            station,
            station_inventory
        )
    return list(packages_to_drop.keys())


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
    shortest_paths = [[None for _i in range(no_of_station)] for _j in range(no_of_station)]
    compute_delivery_shortest_paths(
        package_collections,
        shortest_paths,
        train_network
    )

    for package in package_collections:
        if package.status() == STATUS['delivered']:
            continue

        train, pickup_cost, pickup_path = find_best_delivery_train(
            package,
            train_collections,
            shortest_paths,
            train_network
        )
        load_package(package, train, package.destination(), station_inventory)

        _, delivery_path = get_shortest_path_info(
            package.origin(),
            package.destination(),
            shortest_paths
        )
        journey_path = combine_paths(pickup_path, delivery_path)
        journey_length = len(journey_path)
        for position in range(journey_length):
            loaded_packages = list()
            dropped_packages = list()

            dropped_inventory = drop_package(
                train,
                journey_path[position],
                station_inventory,
                package_collections
            )

            if dropped_inventory:
                dropped_packages.extend(dropped_inventory)

            # if position < journey_path - 2:
            #     train.move(
            #         journey_path[position + 1],
            #     )