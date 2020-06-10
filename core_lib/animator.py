"""
Upgrading this later...
"""
import math

import cv2
import numpy
from PIL import Image

from core import get_config_value

parking_base = Image.open('media/parking_base.jpg') # width: 328, height: 260
car = Image.open('media/car_resized.jpg')

def get_direction(origin, destination):
    delta_x = destination[0] - origin[0]
    delta_y = destination[1] - origin[1]

    degrees = math.atan2(delta_x, delta_y)/math.pi*180

    if degrees < 0:
        degrees = 360 + degrees

    return degrees

def animator(coordinates):
    global parking_base, car

    rescaled_coordinates = []

    # invert scaled values
    for point in coordinates:
        rescaled_coordinates.append((point[0]/get_config_value('x_scale'), point[1]/get_config_value('y_scale')))

    # initial car position 
    current_direction = get_direction(rescaled_coordinates[0],rescaled_coordinates[1])
    car = car.rotate(current_direction+90, expand=1)

    for i in range(len(rescaled_coordinates)):
        if i > 0:
            degrees = get_direction(rescaled_coordinates[i-1], rescaled_coordinates[i])
            car = car.rotate(degrees-current_direction, expand=1) # rotates the car depending on the angle
            current_direction = degrees

        back_im = parking_base.copy()
        back_im.paste(car, rescaled_coordinates[i])
        opencv_image = cv2.cvtColor(numpy.array(back_im), cv2.COLOR_RGB2BGR)

        cv2.imshow('image_results', opencv_image)

        cv2.waitKey(500)

    cv2.destroyAllWindows()
