import math
import networkx as nx
from copy import deepcopy

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
                weight,
                index
            )
        )
        inventory = station_inventory.get(station_map[origin], None)
        if inventory is None:
            station_inventory[station_map[origin]] = {name: {
                'drop_time': 0,
                'index': index
            }}
        else:
            station_inventory[station_map[origin]][name] = {
                'drop_time': 0,
                'index': index
            }

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
    shortest_paths[right_node][left_node] = time_cost, path[::-1]


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


def retrieve_station_inventory(station, station_inventory):
    inventory = station_inventory.get(station, None)
    if inventory is None:
        return False
    return inventory


def pop_station_inventory(package, station_inventory):
    inventory = station_inventory.get(package.origin(), None)
    if inventory is None:
        raise ValueError('MISSING_INVENTORY_AT_ORIGIN')
    if package.name() not in inventory:
        raise ValueError('MISSING_PACKAGE_AT_ORIGIN_INVENTORY')

    station_inventory[package.origin()].pop(package.name())


def load_package(
    package,
    train,
    station,
    station_inventory,
    package_collections,
    shortest_paths,
    future_path
):
    inventory = retrieve_station_inventory(station, station_inventory)
    if not inventory or len(inventory) == 0:
        return False

    packages_to_load = list()
    destinations = list()
    for package_name in inventory:
        package_index = inventory[package_name]['index']
        inventory_package = package_collections[package_index]

        if inventory_package.status() == STATUS['delivered']:
            continue

        if package_index == package.index():
            packages_to_load.append(package)
            destinations.append(package.destination())
            continue

        drop_time = inventory[package_name]['drop_time']
        if drop_time > train.elapsed_time():
            continue

        if not train.check_package(inventory_package, package.weight()):
            continue

        _, delivery_path = get_shortest_path_info(
            inventory_package.origin(),
            inventory_package.destination(),
            shortest_paths
        )
        for index in range(len(delivery_path) - 1, 0, -1):
            if delivery_path[index] in future_path:
                packages_to_load.append(inventory_package)
                destinations.append(delivery_path[index])
                break

    if len(packages_to_load) == 0:
        return False

    for package_to_load, destination in zip(packages_to_load, destinations):
        pop_station_inventory(package_to_load, station_inventory)
        train.load_package(package_to_load, destination)
        package_to_load.load()

    return [package.name() for package in packages_to_load]


def push_station_inventory(
    package,
    package_index,
    station,
    drop_time,
    station_inventory
):
    packages = station_inventory.get(station, None)
    if packages is None:
        station_inventory[station] = {
            package.name(): {'drop_time': drop_time, 'index': package_index}
        }
    else:
        station_inventory[station][package.name()] = {
            'drop_time': drop_time,
            'index': package_index
        }


def drop_package(train, station, station_inventory, package_collections):
    packages_to_drop = deepcopy(train.packages_to_drop())
    if packages_to_drop is None or len(packages_to_drop) == 0:
        return False
    for package_name in packages_to_drop:
        package_index = packages_to_drop[package_name]['index']
        package = package_collections[package_index]

        train.drop_package(package)
        package.drop(station)
        push_station_inventory(
            package,
            package_index,
            station,
            train.elapsed_time(),
            station_inventory
        )
    return list(packages_to_drop.keys())


def get_route_time_cost(left_node, right_node, train_network):
    return train_network[left_node][right_node]['weight']


def get_route_name(left_node, right_node, train_network):
    return train_network[left_node][right_node]['name']


def get_station_name(station, train_network):
    return train_network.nodes[station]['name']


def route_package_train(stations, routes, deliveries, trains):
    validate_input(stations, routes, deliveries, trains)

    train_network, station_map = construct_train_network(stations, routes)
    no_of_station = len(station_map)

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
        _, delivery_path = get_shortest_path_info(
            package.origin(),
            package.destination(),
            shortest_paths
        )
        journey_path = combine_paths(pickup_path, delivery_path)
        journey_length = len(journey_path)

        for index in range(journey_length):
            loaded_packages = list()
            dropped_packages = list()

            dropped_inventory = drop_package(
                train,
                journey_path[index],
                station_inventory,
                package_collections
            )
            if dropped_inventory:
                dropped_packages.extend(dropped_inventory)

            loaded_inventory = load_package(
                package,
                train,
                journey_path[index],
                station_inventory,
                package_collections,
                shortest_paths,
                journey_path[index+1:]
            )
            if loaded_inventory:
                loaded_packages.extend(loaded_inventory)

            if index <= journey_length - 2:
                next_route_duration = get_route_time_cost(
                    journey_path[index],
                    journey_path[index + 1],
                    train_network
                )
                train.record_log(
                    get_station_name(journey_path[index], train_network),
                    get_station_name(journey_path[index + 1], train_network),
                    get_route_name(
                        journey_path[index],
                        journey_path[index + 1],
                        train_network
                    ),
                    next_route_duration,
                    loaded_packages,
                    dropped_packages
                )
                train.move(journey_path[index + 1], next_route_duration)
            else:
                train.record_log(
                    get_station_name(journey_path[index], train_network),
                    None,
                    None,
                    None,
                    loaded_packages,
                    dropped_packages
                )

    logs = list()
    for train in train_collections:
        logs.extend(train.retrieve_log())

    logs.sort(key = lambda x: x['time'])
    print('Chronological train schedule')
    for log in logs:
        print(log)
