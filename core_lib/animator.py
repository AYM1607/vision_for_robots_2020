import math

import cv2
import numpy
from PIL import Image

from core_lib.core import get_config_value

parking_base = Image.open("core_lib/media/parking_base.jpg")  # width: 328, height: 260
car = Image.open("core_lib/media/car_resized.jpg")


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
        rescaled_coordinates.append(
            (int(point[0] / x_scale) - offset[0], int(point[1] / y_scale) - offset[1])
        )

    # initial car position
    current_direction = get_direction(rescaled_coordinates[0], rescaled_coordinates[1])
    car = car.rotate(current_direction + 90, expand=1)

    for i in range(len(rescaled_coordinates)):
        if i > 0:
            degrees = get_direction(
                rescaled_coordinates[i - 1], rescaled_coordinates[i]
            )
            car = car.rotate(
                degrees - current_direction, expand=1
            )  # rotates the car depending on the angle
            current_direction = degrees

        back_im = parking_base.copy()
        back_im.paste(car, rescaled_coordinates[i])
        opencv_image = cv2.cvtColor(numpy.array(back_im), cv2.COLOR_RGB2BGR)

        cv2.imshow("car_trajectory", opencv_image)

        cv2.waitKey(100)
