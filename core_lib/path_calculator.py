import cv2
import numpy as np
from .parking import get_parking_poles_structure
from .core import get_config_value
from .parking import get_initial_coordinates_and_direction


def get_neighbours(point, image, visited):
    """
    Get the valid unvisited neighbours for a given point.
    Arguments:
        point {tuple} -- point representation, elements order: x, y.
        image {np.array} -- the original image.
        visited {np.array} -- visited matrix (booleans).
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

        if 0 <= new_x < width and 0 <= new_y < height:
            if visited[new_y][new_x]:
                continue
            valid_neighbours.append((new_x, new_y))
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

    # Enqueue initial point.
    queue = [initial_point]
    distance = 0
    
    # BFS expansion, distances calculation.
    while len(queue) > 0:
        aux_queue = queue
        for curr_point in aux_queue:
            queue.pop(0)
            x, y = curr_point
            if poles[y][x] > -1:
                poles[y][x] = distance
            queue.extend(get_neighbours(curr_point, poles, visited))
        distance += 1

    return poles
    
def calculate_path():
    intial_conditions = get_initial_coordinates_and_direction()
    if intial_conditions:
        x_initial, y_initial, direction = intial_conditions
        quadrant = get_config_value("initial_quadrant")
        