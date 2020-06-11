import cv2
from core_lib.parking import (
    get_initial_quadrant_and_direction,
    get_final_parking_space_coordinates,
    get_available_spots_regions,
)
from core_lib.path_calculator import build_path
from core_lib.drawing import draw_path
from core_lib.animator import animator


def main():
    get_initial_quadrant_and_direction()
    get_final_parking_space_coordinates()
    points = build_path()
    draw_path(points)

    cv2.imshow("Route", cv2.imread("core_lib/media/output_image.jpg"))
    animator(points)
    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
