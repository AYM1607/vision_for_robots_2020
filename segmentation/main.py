"""
This program segments an image usign the region growing algorithm
with manually provided seeds.
"""
import time
import math
import argparse
from random import randint
import numpy as np
import cv2

from video_feed import VideoFeed

# Seed colors. Arranged in BGR order to match opencv.
COLOR_1 = [115, 80, 155]
COLOR_2 = [0, 95, 165]


def mouse_callback(event, x_coordinate, y_coordinate, _flags, _params):
    """
    Adds the coordinates of a given mouse click event to the
    global coordinates list.
    """

    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse positioned in {x_coordinate},{y_coordinate}")
        seed_coordinates_list.append((x_coordinate, y_coordinate))


def get_random_color():
    """
    Creates a random rgb color represented as a tuple.

    Returns:
        Tuple -- Colors arranged in BGR order.
    """

    return randint(0, 255), randint(0, 255), randint(0, 255)


def get_neighbours(point, image, visited):
    """
    Get the valid unvisited neighbours for a given point.

    Arguments:
        point {tuple} -- point representation, elements order: x, y, intensity.
        image {np.array} -- the original image.
        visited {np.array} -- visited matrix (booleans).

    Returns:
        Array - includes all the valid unvisited neighbours, can be empty.
    """

    coordinate_differences = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    valid_neighbours = []
    base_x, base_y, _ = point
    height = len(image)
    width = len(image[0])

    for x_offset, y_offset in coordinate_differences:
        new_x = base_x + x_offset
        new_y = base_y + y_offset

        if 0 <= new_x < width and 0 <= new_y < height:
            if visited[new_y][new_x]:
                continue
            valid_neighbours.append((new_x, new_y, image[new_y][new_x]))
            visited[new_y][new_x] = True

    return valid_neighbours


def update_moments(moments_object, point):
    """
    Updates moments given a point.
    Initializes the object if empty.

    Arguments:
        moments_object {dictionary} -- Includes all raw moments.
        point {tuple} -- order of the elements: x, y, intensity
    """

    if len(moments_object.keys()) == 0:
        moments_object.update(
            {"00": 0, "10": 0, "01": 0, "11": 0, "20": 0, "02": 0,}
        )

    x_coordinate, y_coordinate, _ = point

    moments_object["00"] += 1
    moments_object["10"] += x_coordinate
    moments_object["01"] += y_coordinate
    moments_object["11"] += x_coordinate * y_coordinate
    moments_object["20"] += x_coordinate * x_coordinate
    moments_object["02"] += y_coordinate * y_coordinate


def get_region_characteristics(moments):
    """
    Calculate the characteristics of a region given its moments.

    Arguments:
        moments {dictionary} -- Contains all the ordinary moments.

    Returns:
        Dictionary -- Contains:
            x_center: x coordinate of the centroid.
            y_center: y coordinate of the controid.
            theta: The orientation of the region.
            phi_1: First Hu moment.
            phi_2: Second Hu moment.
    """

    # Location of the region.
    x_center = int(moments["10"] / moments["00"])
    y_center = int(moments["01"] / moments["00"])

    # Centralized moments.
    mu_11 = moments["11"] - y_center * moments["10"]
    mu_20 = moments["20"] - x_center * moments["10"]
    mu_02 = moments["02"] - y_center * moments["01"]

    # Orientation.
    theta = math.atan2(2 * mu_11, mu_20 - mu_02) / 2

    # Normalized moments.
    nu_11 = mu_11 / moments["00"] ** 2
    nu_20 = mu_20 / moments["00"] ** 2
    nu_02 = mu_02 / moments["00"] ** 2

    # Hu moments.
    phi_1 = nu_20 + nu_02
    phi_2 = (nu_20 - nu_02) ** 2 - 4 * nu_11 ** 2

    return {
        "x_center": x_center,
        "y_center": y_center,
        "theta": theta,
        "phi_1": phi_1,
        "phi_2": phi_2,
    }


def region_expander(image, seed_coordinates_list, intensity_threshold):
    """
    Expands regions given a grayscale image, a threshold and a list of seeds.

    Arguments:
        image {np.array} -- the original image in grayscale.
        intensity_threshold {number} -- the maximum intensity difference of the seed
            and any neighbour pixel.

    Returns:
        np.array -- An image with the found regions marked in random colors and
            the centroids of those images in bright green.
    """

    height = len(image)
    width = len(image[0])

    # Generate a visited list with the same dimensions as the original image.
    visited = np.full((height, width), False)

    # Create resulting image (BGR) with all black colors.
    result_image = np.zeros((height, width, 3), np.uint8)

    for seed_coordinates in seed_coordinates_list:
        pending_points = []
        region_color = get_random_color()
        region_moments = {}

        x_seed, y_seed = seed_coordinates
        seed_intensity = image[y_seed][x_seed]

        pending_points.append((x_seed, y_seed, seed_intensity))

        while len(pending_points) > 0:
            current_point = pending_points.pop(0)
            current_x, current_y, _ = current_point

            update_moments(region_moments, current_point)

            result_image[current_y][current_x] = region_color

            for neighbour in get_neighbours(current_point, image, visited):
                intensity = neighbour[2]
                distance = abs(int(seed_intensity) - int(intensity))
                if distance <= intensity_threshold:
                    pending_points.append(neighbour)

        region_characteristics = get_region_characteristics(region_moments)
        print(region_characteristics)

        cv2.circle(
            result_image,
            (region_characteristics["x_center"], region_characteristics["y_center"]),
            3,
            (0, 255, 0),
            6,
        )

    return result_image


def get_seeds_helper(
    image, lower_height_limit, upper_height_limit, data, count_to_update
):
    """
    Get the possible seeds of an image based on the 2 colors defined on the global scope.
    The name of the colors must be COLOR_1 and COLOR_2 and be in BGR order.
    Analyzes the row in the middle of lower_height_limit and upper_height_limit and
    recursively calls the same function for the images that the middle cuts in half.
    In order to keep the algorithm fast, it stops at 20 iterations and considers there's no
    seeds in this image, it also starts when the 2 seeds are found.

    Arguments:
        image {np.array} -- The image to traverse
        lower_height_limit {integer}
        upper_height_limit {integer}
        data {dictionary} -- Pre-existing data, can contain:
            seed_1: The coordiantes for the seed_1
            seed_2: The coordiantes for seed_2
            count: The total iterations counts

    Returns:
        Dictionary -- The updated data dictionary
    """

    if ("seed_1" in data and "seed_2" in data) or data[count_to_update] == 10:
        return None

    middle_height = int(
        lower_height_limit + (upper_height_limit - lower_height_limit) / 2
    )

    for x in range(0, len(image[0])):
        pixel = image[middle_height][x]
        if (
            COLOR_1[0] - 20 <= pixel[0] <= COLOR_1[0] + 20
            and COLOR_1[1] - 20 <= pixel[1] <= COLOR_1[1] + 20
            and COLOR_1[2] - 20 <= pixel[2] <= COLOR_1[2] + 20
        ):
            data["seed_1"] = (x, middle_height)

        if (
            COLOR_2[0] - 20 <= pixel[0] <= COLOR_2[0] + 20
            and COLOR_2[1] - 20 <= pixel[1] <= COLOR_2[1] + 20
            and COLOR_2[2] - 20 <= pixel[2] <= COLOR_2[2] + 20
        ):
            data["seed_2"] = (x, middle_height)

    data[count_to_update] += 1

    get_seeds_helper(image, lower_height_limit, middle_height, data, count_to_update)
    get_seeds_helper(image, middle_height, upper_height_limit, data, count_to_update)


def get_seeds(image):
    """
    Gets the seeds of an image.
    For this method to work COLOR_1 and COLOR_2 must be in scope.

    Arguments:
        image {np.array} -- The image to traverse.
    """

    data = {"upper_count": 0, "lower_count": 0}

    middle_height = int(len(image) / 2)

    for x in range(0, len(image[0])):
        pixel = image[middle_height][x]
        if (
            COLOR_1[0] - 20 <= pixel[0] <= COLOR_1[0] + 20
            and COLOR_1[1] - 20 <= pixel[1] <= COLOR_1[1] + 20
            and COLOR_1[2] - 20 <= pixel[2] <= COLOR_1[2] + 20
        ):
            data["seed_1"] = (x, middle_height)

        if (
            COLOR_2[0] - 20 <= pixel[0] <= COLOR_2[0] + 20
            and COLOR_2[1] - 20 <= pixel[1] <= COLOR_2[1] + 20
            and COLOR_2[2] - 20 <= pixel[2] <= COLOR_2[2] + 20
        ):
            data["seed_2"] = (x, middle_height)

    get_seeds_helper(image, 0, middle_height, data, "lower_count")
    get_seeds_helper(image, middle_height, len(image), data, "upper_count")

    return data


def main():
    """
    Performs the seeded region growing algorithm for image segmentation.
    Accepts the image filename as an argument as long as the intensity threshold.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--intensity-threshold",
        default=10,
        help="The maximum distance for 2 pixels to be considered in the same region",
    )
    args = parser.parse_args()

    # Create 2 named windows for the input and output image.
    cv2.namedWindow("Input")
    cv2.namedWindow("Output")

    # Set the mouse callback to get seeds from clicks.
    cv2.setMouseCallback("Input", mouse_callback, 0)

    with VideoFeed(camera_index=1, width=350) as feed:
        while True:
            start = time.time()
            _, image = feed.read()
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            seeds_data = get_seeds(image)
            seed_coordinates_list = []

            if "seed_1" in seeds_data:
                seed_coordinates_list.append(seeds_data["seed_1"])
            if "seed_2" in seeds_data:
                seed_coordinates_list.append(seeds_data["seed_2"])

            result_image = region_expander(
                gray_image, seed_coordinates_list, int(args.intensity_threshold)
            )
            cv2.imshow("Input", image)
            cv2.imshow("Output", result_image)
            end = time.time()
            print(f"Frame processing took: {end - start} seconds")

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()
    return


if __name__ == "__main__":
    main()
