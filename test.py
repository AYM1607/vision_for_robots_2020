import cv2
import numpy as np

from core_lib.core import save_config_value, get_config_value
from core_lib.image_processing import filter_by_color, dilate

# points = []


# def mouse_callback(event, x, y, _flags, _params):
#    global points, base_image
#
#    if event == cv2.EVENT_LBUTTONUP:
#        points.append(base_image[y][x])
#        print("Point appended")


# def maybe_save_average_color():
#    global points
#    if len(points) < 1:
#        return
#    result = [0, 0, 0]
#    for point in points:
#        for i in range(3):
#            result[i] += point[i]
#    result = list(map(lambda x: int(round(x / len(points))), result))
#    save_config_value("pavement_color", result)


def main():
    global points, base_image
    base_image = cv2.imread("core_lib/media/parking_base.jpg")
    cv2.namedWindow("parking")
    cv2.imshow("parking", base_image)
    result_image = filter_by_color(base_image, get_config_value("pavement_color"), 40)
    result_image = cv2.medianBlur(result_image, 3)

    cv2.imshow("filtered", result_image)
    result_image = dilate(result_image, 9)
    cv2.imshow("dilated", result_image)

    cv2.waitKey()
    cv2.destroyAllWindows()
    print("Works")


if __name__ == "__main__":
    main()
