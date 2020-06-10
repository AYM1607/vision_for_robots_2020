"""
Upgrading this later...
"""
import cv2
import numpy

from PIL import Image, ImageOps

def main():
    global car
    parking_base = Image.open('media/parking_base.jpg') # width: 328, height: 260
    car = Image.open('media/car_resized.jpg')
    car = car.transpose(Image.ROTATE_180)

    points = [(8,233),(10,233),(12,233),(14,233),(16,233),(18,233)]

    for point in points:
        back_im = parking_base.copy()
        back_im.paste(car, point)
        opencv_image = cv2.cvtColor(numpy.array(back_im), cv2.COLOR_RGB2BGR)

        cv2.imshow('image_results', opencv_image)

        cv2.waitKey(1000)

    cv2.destroyAllWindows()

main()

