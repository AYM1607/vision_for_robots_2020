import sys
import csv
import numpy as np
from parking import get_parking_poles_structure
from core import get_config_value
from parking import get_initial_coordinates_and_direction
from core import Direction


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
            if visited[new_y][new_x] or is_point_blocked((new_x, new_y), config):
                continue
            valid_neighbours.append((new_x, new_y))
            if config is None:
                visited[new_y][new_x] = True

    return valid_neighbours

def calculate_distances(initial_point):
    """
    Returns a representation of the distances from the provided point
    to any free space in the image. If the point is an obstacle, a distance
    of -1 will be assigned.

    Arguments:
        initial_point {tuple} -- Coordinates of inital point (x, y)

    Returns:
        np.array
    """
    # Get downsampled image.
    poles = get_parking_poles_structure()
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


def is_point_blocked(point, config):
    """
   Defines if a point is inside a virtual block given a configuration => quadrant > direction.

    Arguments:
        point {tuple} -- Coordinates of a point (x, y).
        config {string} -- String representing the configuration.

    Returns:
        boolean
    """
    if config is None:
        return False
    x, y = point
    block_obj = get_config_value("barriers")[config]
    return block_obj["corner_1"][0] <= x <= block_obj["corner_2"][0] and block_obj["corner_1"][1] <= y <= block_obj["corner_2"][1]

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
            print(f'There was an error calculating the path! :( len = {len(path)}')
            return []
        print(f'x = {next_node[0]}\ty = {next_node[1]}')
        x_curr, y_curr = next_node
        visited[y_curr][x_curr] = True
        path.append(next_node)
    return path
    

def write_csv(mat, name):
    with open(name, 'w', newline='') as file:
        writer = csv.writer(file)
        for i in range(len(mat)):
            writer.writerow(mat[i])

def init():
    """
    Gets the information necessary to calculate the path and invokes the function.
    """
    (x_initial, y_initial), direction = get_initial_coordinates_and_direction()
    print(f'x_initial = {x_initial}\ty_initial = {y_initial}')
    parking_coords = get_config_value("initial_coordinates")
    print(f'parking_coords =  {parking_coords}')
    # Build key to query for blocks coordinates
    quadrant = get_config_value("initial_quadrant")
    config = Direction(quadrant).name + ">" + Direction(direction).name
    print(f'config = {config}')
    # Build matrix with distances
    distances = calculate_distances(parking_coords)
    #write_csv(distances, "output.csv")
    # Create matrix of visited nodes.
    height = len(distances)
    width = len(distances[0])
    print(f'Downsampled Image Dimensions => height = {height}  twidth = {width}')
    visited = np.full((height, width), False)
    path = calculate_path((x_initial, y_initial), distances, config, visited)
    print(f'pathLen = {len(path)}')
    
init()
