import math

import cv2
import numpy
from PIL import Image

from core_lib.core import get_config_value
from core_lib.parking import get_available_spots_regions

parking_base = Image.open("core_lib/media/parking_base.jpg")  # width: 328, height: 260
base_car = Image.open("core_lib/media/car_resized.jpg")


def get_direction(origin, destination):
    """
    Gets the angle between the two points.

    Parameters:
        origin {tuple} --- initial point (x,y).
        destination {tuple} --- final point (x,y).

    Returns:
        float --- angle/degrees between the two points.
    """
    delta_x = destination[0] - origin[0]
    delta_y = destination[1] - origin[1]

    degrees = math.atan2(delta_x, delta_y) / math.pi * 180

    if degrees < 0:
        degrees = 360 + degrees

    return degrees


def is_vertical(angle):
    return -0.0001 < math.sin(angle * math.pi / 180) < 0.0001


def animator(coordinates):
    """
    Animates a car trajectory in a parking lot, given a set of points.

    Paremeters:
        coordinates {list} --- a list of tuples in which each tuple represents a coordinate of the trajectory
    """
    global parking_base, car

    rescaled_coordinates = []
    x_scale = get_config_value("x_scale")
    y_scale = get_config_value("y_scale")
    offset = (5, 11)  # car size is (10,24)
    # invert scaled values and place pixel at car's center
    for point in coordinates:
        rescaled_coordinates.append((int(point[0] / x_scale), int(point[1] / y_scale)))

    # initial car position
    direction = get_direction(rescaled_coordinates[0], rescaled_coordinates[1])
    car = base_car.rotate(direction + 90, expand=1)

    for i in range(len(rescaled_coordinates)):
        if i > 0:
            direction = get_direction(
                rescaled_coordinates[i - 1], rescaled_coordinates[i]
            )
            car = base_car.rotate(
                direction + 90, expand=1
            )  # rotates the car depending on the angle

        back_im = parking_base.copy()
        offset = (5, 11) if is_vertical(direction) else (11, 5)
        x, y = (
            rescaled_coordinates[i][0] - offset[0],
            rescaled_coordinates[i][1] - offset[1],
        )
        back_im.paste(car, (x, y))
        opencv_image = cv2.cvtColor(numpy.array(back_im), cv2.COLOR_RGB2BGR)

        cv2.imshow("car_trajectory", opencv_image)

        cv2.waitKey(100)
