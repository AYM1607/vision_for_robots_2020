import cv2
import numpy as np

from core_lib.core import save_config_value, get_config_value
from core_lib.image_processing import filter_by_color, dilate

rectangles = []
rectangle = {}
points_counter = 0


# def mouse_callback(event, x, y, _flags, _params):
#     global rectangles, rectangle, points_counter
#
#     if event == cv2.EVENT_LBUTTONUP:
#         if points_counter == 0:
#             rectangle["corner_1"] = (x, y)
#             points_counter += 1
#         elif points_counter == 1:
#             rectangle["corner_2"] = (x, y)
#             points_counter += 1
#         elif points_counter == 2:
#             rectangle["real_center"] = (x, y)
#             points_counter += 1
#         elif points_counter == 3:
#             rectangle["algorithm_center"] = (x, y)
#             rectangles.append(rectangle)
#             points_counter = 0
#             rectangle = {}


def main():
    global rectangle, rectangles
    expanded = cv2.imread("core_lib/media/expanded.jpg")
    cv2.namedWindow("parking")

    height = int(round(len(expanded) / 3))
    width = int(round(len(expanded[0]) / 3))

    cv2.imshow("original", expanded)

    expanded = cv2.resize(expanded, (width, height))

    parking_spaces = get_config_value("free_parking_spaces")
    print(parking_spaces)
    scaled_spaces = []
    for space in parking_spaces:
        space["corner_1"] = [
            int(round(space["corner_1"][0] / 3)),
            int(round(space["corner_1"][1] / 3)),
        ]
        space["corner_2"] = [
            int(round(space["corner_2"][0] / 3)),
            int(round(space["corner_2"][1] / 3)),
        ]
        space["real_center"] = [
            int(round(space["real_center"][0] / 3)),
            int(round(space["real_center"][1] / 3)),
        ]
        space["algorithm_center"] = [
            int(round(space["algorithm_center"][0] / 3)),
            int(round(space["algorithm_center"][1] / 3)),
        ]
        scaled_spaces.append(space)

    for space in scaled_spaces:
        print(space)
        cv2.rectangle(
            expanded,
            (int(space["corner_1"][0]), int(space["corner_1"][1])),
            (int(space["corner_2"][0]), int(space["corner_2"][1])),
            (0, 0, 0),
            -1,
        )
    cv2.imwrite("core_lib/media/route_planner_structure.jpg", expanded)
    save_config_value("free_parking_spaces_scaled", scaled_spaces)
    cv2.imshow("parking", expanded)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
