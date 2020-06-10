"""
Upgrading this later...
"""
import math

import cv2
import numpy
from PIL import Image

from core import get_config_value

# this two variables will be provided by some other module
points = [(8,233),(12,233),(16,233),(20,233),(24,233),(28,233),(28,220),(28,215),(28,207),(28,195),(24,195),(20,195),(16,195),(16,207),(16,215),(16,222),(16,233)]
points_2 = [(300,22),(295,22),(290,22),(285,22),(285,27),(285,33),(285,40),(285,44),(275,44),(270,44),(265,44),(260,44)]
initial_direction = 270 # [N, E, S, W] = [0, 45, 180, 270]

parking_base = Image.open('media/parking_base.jpg') # width: 328, height: 260
car = Image.open('media/car_resized.jpg')

def initial_position(entrance):
    '''
    Changes the angle of the car depending the initial position (if the car starts on entrance 4, the angle remains as the origial)
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
    '''
    Gets the angle between the two points
    '''
    delta_x = destination[0] - origin[0]
    delta_y = destination[1] - origin[1]

    degrees = math.atan2(delta_x, delta_y)/math.pi*180

    if degrees < 0:
        degrees = 360 + degrees

    return degrees

def main(coordinates, initial_direction):
    global parking_base, car
    initial_position(coordinates[0])
    
    current_direction = initial_direction
    for i in range(len(coordinates)):
        if i > 0:
            degrees = get_direction(coordinates[i-1], coordinates[i])
            car = car.rotate(degrees-current_direction, expand=1) # rotates the car depending on the angle
            current_direction = degrees

        back_im = parking_base.copy()
        back_im.paste(car, coordinates[i])
        opencv_image = cv2.cvtColor(numpy.array(back_im), cv2.COLOR_RGB2BGR)

        cv2.imshow('image_results', opencv_image)

        cv2.waitKey(500)

    cv2.destroyAllWindows()

main(points_2,  initial_direction)
