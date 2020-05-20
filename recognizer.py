"""
This program segments an image usign the region growing algorithm
with automatically found seeds.
"""
import argparse
import cv2

from core_lib.video_feed import VideoFeed
from core_lib.seeds import get_seeds
from core_lib.segmentation import region_expander
from core_lib.drawing import draw_region_characteristics


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

    with VideoFeed(camera_index=1, width=450) as feed:
        while True:
            _, image = feed.read()
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            seeds = get_seeds(image)

            result_image, found_regions = region_expander(
                gray_image, seeds, int(args.intensity_threshold)
            )

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
