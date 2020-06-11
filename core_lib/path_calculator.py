import sys
import csv
import numpy as np
from core_lib.parking import (
    get_parking_poles_structure,
    get_initial_coordinates_and_direction,
)
from core_lib.core import get_config_value, save_config_value, Direction
from core_lib.drawing import draw_path


def parking_slot_matcher(point):
    if point[0] == 77:
        if point[1] == 45:
            return "p1"
        else:
            return "p3"
    elif point[0] == 86:
        if point[1] == 45:
            return "p2"
        else:
            return "p4"
    return None


def adpat_configuration(config):
    if config == "NORTH_WEST>SOUTH":
        return "NORTH_WEST>EAST"
    elif config == "NORTH_WEST>EAST":
        return "NORTH_WEST>SOUTH"
    elif config == "NORTH_EAST>SOUTH":
        return "NORTH_EAST>WEST"
    elif config == "NORTH_EAST>WEST":
        return "NORTH_EAST>SOUTH"
    if config == "SOUTH_WEST>NORTH":
        return "SOUTH_WEST>EAST"
    elif config == "SOUTH_WEST>EAST":
        return "SOUTH_WEST>NORTH"
    elif config == "SOUTH_EAST>NORTH":
        return "SOUTH_EAST>WEST"
    elif config == "SOUTH_EAST>WEST":
        return "SOUTH_EAST>NORTH"


def get_neighbours(point, image, visited, config):
    """
    Get the valid unvisited neighbours for a given point.
    Arguments:
        point {tuple} -- point representation, elements order: x, y.
        image {np.array} -- the original image.
        visited {np.array} -- visited matrix (booleans).
        config {string | None} -- key for the virtual blocks given a coinfiguration.
    Returns:
        Array - includes all the valid unvisited neighbours, can be empty.
    """

    coordinate_differences = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    valid_neighbours = []
    base_x, base_y = point
    height = len(image)
    width = len(image[0])

    for x_offset, y_offset in coordinate_differences:
        new_x = base_x + x_offset
        new_y = base_y + y_offset

        if 0 <= new_x < width and 0 <= new_y < height and image[new_y][new_x] > -1:
            if visited[new_y][new_x]:
                continue
            valid_neighbours.append((new_x, new_y))
            if config is None:
                visited[new_y][new_x] = True

    return valid_neighbours


def block_image(image, config, slot_coords):
    """
    Fills with -1 the areas to be blocked. This is aimed to force the route 
    to follow a specific path. Receives the original image and returns a blocked one.
    Arguments:
        image {np.array} -- the original image.
        config {string | None} -- key for the virtual blocks given a coinfiguration.
    Returns:
        np.array
    """
    barriers = [config, "p1", "p2", "p3", "p4"]
    special_slot = parking_slot_matcher(slot_coords)
    if special_slot is not None:
        barriers.remove(special_slot)
    for barrier in barriers:
        block = get_config_value("barriers")[barrier]
        x_corner_1, y_corner_1 = block["corner_1"]
        x_corner_2, y_corner_2 = block["corner_2"]
        for i in range(y_corner_1, y_corner_2):
            for j in range(x_corner_1, x_corner_2):
                image[i][j] = -1

    return image


def calculate_distances(initial_point, config):
    """
    Returns a representation of the distances from the provided point
    to any free space in the image. If the point is an obstacle, a distance
    of -1 will be assigned.

    Arguments:
        initial_point {tuple} -- Coordinates of inital point (x, y)
        config {string} -- Entrance configuration.

    Returns:
        np.array
    """
    # Get downsampled image.
    poles = get_parking_poles_structure()
    poles = block_image(poles, config, initial_point)
    # Create matrix of visited nodes.
    height = len(poles)
    width = len(poles[0])
    visited = np.full((height, width), False)
    visited[initial_point[1]][initial_point[0]] = True
    # Enqueue initial point.
    queue = [initial_point]
    distance = 0
    # BFS expansion, distances calculation.
    while len(queue) > 0:
        temp_size = len(queue)
        for i in range(temp_size):
            x, y = queue.pop(0)
            poles[y][x] = distance
            valid_neighbours = get_neighbours((x, y), poles, visited, None)
            queue.extend(valid_neighbours)
        distance += 1

    return poles


def get_next_neighbour(curr_node, distances, config, visited):
    """
    Returns the valid neighbour that has the smalles distance.

    Arguments:
        curr_node {tuple} -- Coordinates of a point (x, y).
        distances {np.array} -- Matrix that contains the distances.
        config {string} -- String representing the configuration.
        visited {np.array} -- Matrix of booleans that represent visited nodes.

    Returns:
        tuple
    """
    neighbours = get_neighbours(curr_node, distances, visited, config)
    if len(neighbours) == 0:
        return None
    min_dist = sys.maxsize
    next_node = (0, 0)
    for x, y in neighbours:
        if distances[y][x] < min_dist:
            min_dist = distances[y][x]
            next_node = (x, y)
    return next_node


def calculate_path(initial_point, distances, config, visited):
    """
    Returns the path from the initial point to the parking slot.

    Arguments:
        curr_node {tuple} -- Coordinates of a point (x, y).
        distances {np.array} -- Matrix that contains the distances.
        config {string} -- String representing the configuration.
        visited {np.array} -- Matrix of booleans that represent visited nodes.

    Returns:
        array
    """
    path = [initial_point]
    x_curr, y_curr = initial_point
    # Mark the initial point as visited.
    visited[y_curr][x_curr] = True
    while distances[y_curr][x_curr] > 0:
        next_node = get_next_neighbour((x_curr, y_curr), distances, config, visited)
        if next_node is None:
            print(f"There was an error calculating the path! :( len = {len(path)}")
            return []
        # print(f'x = {next_node[0]}\ty = {next_node[1]}')
        x_curr, y_curr = next_node
        visited[y_curr][x_curr] = True
        path.append(next_node)
    return path


def write_csv(mat, name):
    with open(name, "w", newline="") as file:
        writer = csv.writer(file)
        for i in range(len(mat)):
            writer.writerow(mat[i])


def build_path():
    """
    Gets the information necessary to calculate and build the path and invokes the function.
    Returns an array of points to be traveled.

    Returns:
        array
    """
    (x_initial, y_initial), direction = get_initial_coordinates_and_direction()
    parking_coords = get_config_value("initial_coordinates")

    # Build key to query for blocks coordinates
    quadrant = get_config_value("initial_quadrant")
    config = adpat_configuration(
        Direction(quadrant).name + ">" + Direction(direction).name
    )

    # Build matrix with distances
    distances = calculate_distances(parking_coords, config)

    # Create matrix of visited nodes.
    height = len(distances)
    width = len(distances[0])

    visited = np.full((height, width), False)
    path = calculate_path((x_initial, y_initial), distances, config, visited)
    write_csv(path, "output.csv")
    draw_path(path)
    return path


def test():
    possible_confs = [
        {"quadrant": 5, "direction": 2},
        {"quadrant": 5, "direction": 4},
        {"quadrant": 6, "direction": 2},
        {"quadrant": 6, "direction": 3},
        {"quadrant": 7, "direction": 1},
        {"quadrant": 7, "direction": 4},
        {"quadrant": 8, "direction": 1},
        {"quadrant": 8, "direction": 3},
    ]
    for conf in possible_confs:
        save_config_value("initial_quadrant", conf["quadrant"])
        save_config_value("initial_direction", conf["direction"])
        free_parking_spaces_scaled = get_config_value("free_parking_spaces_scaled")
        quadrant = get_config_value("initial_quadrant")
        direction = get_config_value("initial_direction")
        for slot in free_parking_spaces_scaled:
            save_config_value("initial_coordinates", slot["algorithm_center"])
            if len(build_path()) == 0:
                print(f'Error using coordinates ({slot["algorithm_center"]})')
            else:
                print(f'Success for slot = {slot["algorithm_center"]}')
            print(
                f"Success for quadrant = {Direction(quadrant).name}  direction = {Direction(direction).name}"
            )
