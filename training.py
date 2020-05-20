"""
This program...
"""
import argparse
import cv2
import json
import statistics

from core_lib.video_feed import VideoFeed
from core_lib.seeds import get_seeds
from core_lib.segmentation import region_expander
from core_lib.drawing import draw_region_characteristics

seed = (0,0)
points = []

def mouse_callback(event, x_coordinate, y_coordinate, _flags, _params):
    global seed
    """
    Adds the coordinates of a given mouse click event to the
    global coordinates list.
    """

    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse positioned in {x_coordinate},{y_coordinate}")
        seed = (x_coordinate, y_coordinate)
        print(found_regions)
        points.append(
            {
                "phi_1": found_regions[0]["phi_1"],
                "phi_2": found_regions[0]["phi_2"]
            }
        )

def calculate_parameters():
    phi_1_acum = []
    phi_2_acum = []

    points.pop(0)

    for point in points:
        phi_1_acum.append(point["phi_1"])
        phi_2_acum.append(point["phi_2"])

    return {
        "sigma_phi_1": statistics.stdev(phi_1_acum),
        "sigma_phi_2": statistics.stdev(phi_2_acum),
        "mean_phi_1": statistics.mean(phi_1_acum),
        "mean_phi_2": statistics.mean(phi_2_acum)
    }

def main():
    """
    Performs the seeded region growing algorithm for image segmentation.
    Reads images directlty from the webcam.
    """

    global found_regions, points

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--intensity-threshold",
        default=30,
        help="The maximum distance for 2 pixels to be considered in the same region",
    )
    parser.add_argument(
        "-o",
        "--objects",
        default=4,
        help="The number of objects that will be trained",
    )
    parser.add_argument(
        "-s",
        "--samples",
        default=10,
        help="The number of samples per object that will be taken",
    )
    args = parser.parse_args()

    # Create 2 named windows for the input and output image.
    cv2.namedWindow("Input")
    cv2.namedWindow("Output")

    cv2.setMouseCallback("Input", mouse_callback, 0)

    regions = []

    for _ in range(int(args.objects)):
        object_id = input("Enter object id: ")
        with VideoFeed(camera_index=0, width=450) as feed:
            while True:
                _, image = feed.read()
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                seed_coordinates_list = [seed]

                result_image, found_regions = region_expander(
                    gray_image, seed_coordinates_list, int(args.intensity_threshold)
                )

                for region in found_regions:
                    draw_region_characteristics(result_image, region)
                
                cv2.imshow("Output", result_image)
                cv2.imshow("Input", image)

                # End the loop when "q" is pressed.
                if cv2.waitKey(1) & 0xFF == ord("q") or len(points) > int(args.samples):
                    break

        calculated_params = calculate_parameters()

        region = {
            "object_id": object_id,
            "points": points,
            "sigma_phi_1": calculated_params["sigma_phi_1"],
            "sigma_phi_2": calculated_params["sigma_phi_2"],
            "mean_phi_1": calculated_params["mean_phi_1"],
            "mean_phi_2": calculated_params["mean_phi_2"]
        }

        regions.append(region)

        points = []

    print(json.dumps(regions, indent=4))
    with open('train_parameters.txt', 'w') as outfile:
        json.dump(regions, outfile)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
