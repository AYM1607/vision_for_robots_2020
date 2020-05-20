"""
This program...
"""
import argparse
import cv2

from core_lib.video_feed import VideoFeed
from core_lib.seeds import get_seeds
from core_lib.segmentation import region_expander
from core_lib.drawing import draw_region_characteristics

seed = (0,0)

def mouse_callback(event, x_coordinate, y_coordinate, _flags, _params):
    global seed
    """
    Adds the coordinates of a given mouse click event to the
    global coordinates list.
    """

    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse positioned in {x_coordinate},{y_coordinate}")
        seed = (x_coordinate, y_coordinate)

def main():
    """
    Performs the seeded region growing algorithm for image segmentation.
    Reads images directlty from the webcam.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--intensity-threshold",
        default=30,
        help="The maximum distance for 2 pixels to be considered in the same region",
    )
    args = parser.parse_args()

    # Create 2 named windows for the input and output image.
    cv2.namedWindow("Input")
    cv2.namedWindow("Output")

    cv2.setMouseCallback("Input", mouse_callback, 0)

    with VideoFeed(camera_index=0, width=450) as feed:
        while True:
            _, image = feed.read()
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            seed_coordinates_list = [seed]

            result_image, found_regions = region_expander(
                gray_image, seed_coordinates_list, int(args.intensity_threshold)
            )

            print(found_regions)

            for region in found_regions:
                draw_region_characteristics(result_image, region)
            
            cv2.imshow("Output", result_image)
            cv2.imshow("Input", image)

            # End the loop when "q" is pressed.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
