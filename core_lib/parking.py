import cv2
import numpy as np

from os import path
from core_lib.core import get_config_value


def get_parking_poles_structure():
    """
    Returns a representation of the free space in the parking space.
    The returned structure represents free space as 0 and space occupied
    by an obstacle as -1.

    Returns:
        np.array
    """
    mesh = cv2.imread(path.join(path.dirname(__file__), "media", "route_planner.jpg"))
    poles_structure = np.full((len(mesh), len(mesh[0])), -1)

    for i in range(0, len(mesh)):
        for j in range(0, len(mesh[0])):
            if mesh[i][j][0] < 40 and mesh[i][j][1] < 40 and mesh[i][j][2] < 40:
                poles_structure[i][j] = 0

    return poles_structure


def get_scaling_factor():
    """
    Indicates by how much the parking poles structure was
    scaled with respect to the original image.

    Returns:
        tuple --- the order is x_scale then y_scale
    """

    return get_config_value("x_scale"), get_config_value("y_scale")


def get_available_spots_regions():
    """
    Returns the regions on which there are available spots.
    Each spot is a dictionary that contains the following keys:
     - corner_1
     - corner_2
     - real_center
     - algorithm_center

    Each one of the keys contains a 2 element array that represents a coordinate.

    Returns:
        tuple --- a 2 element tuple, each element is an array of spots.
            The first element contains the coordinates
            based on the original image dimensions, the second elements contains the
            coordinates scaled with the same factor as the poles structure.
    """

    return (
        get_config_value("free_parking_spaces"),
        get_config_value("free_parking_spaces_scaled"),
    )
