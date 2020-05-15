import argparse
from random import randint
import numpy as np
import cv2

seed_coordinates_list = []


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


def region_expander(image, intensity_threshold):
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

        print("Moments: ")
        print(region_moments)

        x_center = int(region_moments["10"] / region_moments["00"])
        y_center = int(region_moments["01"] / region_moments["00"])

        cv2.circle(result_image, (x_center, y_center), 3, (0, 255, 0), 6)

    return result_image


def main():
    """
    Performs the seeded region growing algorithm for image segmentation.
    Accepts the image filename as an argument as long as the intensity threshold.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--filename",
        required=True,
        help="The name of the image file to be processed",
    )
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

    # Read image input.
    image = cv2.imread(args.filename, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (500, 500))

    # Transform the original image to grayscale.
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Input", image)
    print(
        "Click on the input image to specify seeds. Each click is an independent seed."
    )

    # Wait for the user to click.
    cv2.waitKey()

    print("Starting algorithm")
    cv2.imshow(
        "Output", region_expander(image_gray, args.intensity_threshold),
    )

    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
