"""
This program segments an image usign the region growing algorithm
with automatically found seeds.
"""
import argparse
import cv2
import json
import statistics

from core_lib.video_feed import VideoFeed
from core_lib.seeds import get_seeds
from core_lib.segmentation import region_expander
from core_lib.drawing import draw_region_characteristics
from core_lib.drawing import draw_results_ui
from core_lib.drawing import draw_training_space
from core_lib.region_identifier import identify_region

# object_names = {
#     "1": "martillo",
#     "2": "llave",
#     "3": "tuerca",
#     "4": "cinta",
#     "5": "UNKNOWN"
# }


def read_training_params():
    with open("train_parameters.txt") as json_file:
        training_params = json.load(json_file)
    return training_params


# def print_object_names(objects):
#     for obj in objects:
#         print("id = ", object_names[obj[0]], "\ttheta = ", obj[1], "\n")


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

    training_params = read_training_params()

    with VideoFeed(camera_index=0, width=450) as feed:
        while True:
            _, image = feed.read()
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            seeds = get_seeds(image)

            result_image, found_regions = region_expander(
                gray_image, seeds, int(args.intensity_threshold)
            )
            detected_figures = identify_region(training_params, found_regions)
            draw_results_ui(detected_figures)
            draw_training_space(training_params, found_regions)
            # print_object_names (detected_figures)

            for region in found_regions:
                draw_region_characteristics(result_image, region)

            cv2.imshow("Input", image)
            cv2.imshow("Output", result_image)

            # End the loop when "q" is pressed.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
