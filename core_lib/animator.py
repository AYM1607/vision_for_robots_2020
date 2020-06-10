"""
Upgrading this later...
"""
import math

import cv2
import numpy
from PIL import Image

from core import get_config_value

# this two variables will be provided by some other module
points = [(8,233),(12,233),(16,233),(20,233),(24,233),(28,233),(28,220),(28,215),(28,207),(28,195),(24,195),(20,195),(16,195)]
initial_direction = 90 # []

parking_base = Image.open('media/parking_base.jpg') # width: 328, height: 260
car = Image.open('media/car_resized.jpg')

def initial_position(entrance):
    '''
    Changes the angle of the car depending the initial position (if the car starts on entrance 2, the angle remains as the origial)
    '''
    global parking_base, car

    car = car.rotate(-90, expand=1)
    
    if entrance == tuple(get_config_value("entrance_1")):
        car = car.rotate(180, expand=1)
    if entrance == tuple(get_config_value("entrance_2")):
        car = car.rotate(90, expand=1)
    if entrance == tuple(get_config_value("entrance_3")):
        car = car.rotate(270, expand=1)

def get_direction(origin, destination):
    delta_x = destination[0] - origin[0]
    delta_y = destination[1] - origin[1]

    degrees = math.atan2(delta_x, delta_y)/math.pi*180

    if degrees < 0:
        degrees = 360 + degrees

    return degrees

def main(coordinates, initial_direction):
    global parking_base, car
    initial_position(points[0])
    
    current_direction = initial_direction
    for i in range(len(points)):
        if i > 0:
            degrees = get_direction(points[i-1], points[i])
            car = car.rotate(degrees-current_direction, expand=1)
            current_direction = degrees

        back_im = parking_base.copy()
        back_im.paste(car, points[i])
        opencv_image = cv2.cvtColor(numpy.array(back_im), cv2.COLOR_RGB2BGR)

        cv2.imshow('image_results', opencv_image)

        cv2.waitKey(500)

    cv2.destroyAllWindows()

main(points,  initial_direction)
print(get_direction(points[4], points[5]))