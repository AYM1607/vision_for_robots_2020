import cv2
import numpy as np

from core_lib.core import save_config_value, get_config_value
from core_lib.image_processing import filter_by_color, dilate

rectangles = []
rectangle = {}
points_counter = 0


def mouse_callback(event, x, y, _flags, _params):
    global rectangles, rectangle, points_counter

    if event == cv2.EVENT_LBUTTONUP:
        if points_counter == 0:
            rectangle["corner_1"] = (x, y)
            points_counter += 1
        elif points_counter == 1:
            rectangle["corner_2"] = (x, y)
            points_counter += 1
        elif points_counter == 2:
            rectangle["real_center"] = (x, y)
            points_counter += 1
        elif points_counter == 3:
            rectangle["algorithm_center"] = (x, y)
            rectangles.append(rectangle)
            points_counter = 0
            rectangle = {}


def main():
    global rectangle, rectangles
    base_image = cv2.imread("core_lib/media/parking_base.jpg")
    cv2.namedWindow("parking")
    cv2.setMouseCallback("parking", mouse_callback)

    while True:
        for rect in rectangles:
            cv2.rectangle(
                base_image, rect["corner_1"], rect["corner_2"], (0, 0, 255), 2
            )
            cv2.circle(base_image, rect["real_center"], 2, (255, 0, 0), 4)
            cv2.circle(base_image, rect["algorithm_center"], 2, (0, 255, 0), 4)
        cv2.imshow("parking", base_image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.imwrite("./core_lib/media/free_parking_spaces.jpg", base_image)
    print("Done!")
    print("saving rectangles to the config file")
    save_config_value("free_parking_spaces", rectangles)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
