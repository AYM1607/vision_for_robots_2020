import math
import numpy as np


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


def update_region_data(region_data, point):
    """
    Updates moments given a point.
    Initializes the object if empty.

    Arguments:
        moments_object {dictionary} -- Includes all raw moments.
        point {tuple} -- order of the elements: x, y, intensity
    """

    if len(region_data.keys()) == 0:
        region_data.update(
            {
                "00": 0,
                "10": 0,
                "01": 0,
                "11": 0,
                "20": 0,
                "02": 0,
                "min_x": float("inf"),
                "max_x": float("-inf"),
                "min_y": float("inf"),
                "max_y": float("-inf"),
            }
        )

    x_coordinate, y_coordinate, _ = point

    region_data["00"] += 1
    region_data["10"] += x_coordinate
    region_data["01"] += y_coordinate
    region_data["11"] += x_coordinate * y_coordinate
    region_data["20"] += x_coordinate * x_coordinate
    region_data["02"] += y_coordinate * y_coordinate
    region_data["min_x"] = min(region_data["min_x"], x_coordinate)
    region_data["max_x"] = max(region_data["max_x"], x_coordinate)
    region_data["min_y"] = min(region_data["min_y"], y_coordinate)
    region_data["max_y"] = max(region_data["max_y"], y_coordinate)


def get_region_characteristics(region_data):
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
    x_center = int(region_data["10"] / region_data["00"])
    y_center = int(region_data["01"] / region_data["00"])

    # Centralized moments.
    mu_11 = region_data["11"] - y_center * region_data["10"]
    mu_20 = region_data["20"] - x_center * region_data["10"]
    mu_02 = region_data["02"] - y_center * region_data["01"]

    # Orientation.
    theta = math.atan2(2 * mu_11, mu_20 - mu_02) / 2

    # Normalized moments.
    nu_11 = mu_11 / region_data["00"] ** 2
    nu_20 = mu_20 / region_data["00"] ** 2
    nu_02 = mu_02 / region_data["00"] ** 2

    # Hu moments.
    phi_1 = nu_20 + nu_02
    phi_2 = ((nu_20 - nu_02) ** 2) + (4 * (nu_11 ** 2))

    return {
        "x_center": x_center,
        "y_center": y_center,
        "theta": theta,
        "phi_1": phi_1,
        "phi_2": phi_2,
        "width": region_data["max_x"] - region_data["min_x"],
        "height": region_data["max_y"] - region_data["min_y"],
    }


def region_expander(image, seed_coordinates_list, intensity_threshold):
    """
    Expands regions given a grayscale image, a threshold and a list of seeds.

    Arguments:
        image {np.array} -- the original image in grayscale.
        intensity_threshold {number} -- the maximum intensity difference of the seed
            and any neighbour pixel.

    Returns:
        Tuple -- Contains:
            result_image: An image with the found regions marked with white.
            found_regions: An array of dictionaries containing the characteristics
                of the fount regions.

    """

    height = len(image)
    width = len(image[0])
    region_color = (255, 255, 255)

    # Generate a visited list with the same dimensions as the original image.
    visited = np.full((height, width), False)

    # Generate a blank image to draw the points on.
    result_image = np.zeros((height, width, 3), np.uint8)

    found_regions = []

    for seed_coordinates in seed_coordinates_list:
        pending_points = []
        region_data = {}

        x_seed, y_seed = seed_coordinates
        seed_intensity = image[y_seed][x_seed]

        pending_points.append((x_seed, y_seed, seed_intensity))

        while len(pending_points) > 0:
            current_point = pending_points.pop(0)
            current_x, current_y, _ = current_point

            result_image[current_y][current_x] = region_color
            update_region_data(region_data, current_point)

            for neighbour in get_neighbours(current_point, image, visited):
                intensity = neighbour[2]
                distance = abs(int(seed_intensity) - int(intensity))
                if distance <= intensity_threshold:
                    pending_points.append(neighbour)

        # Ignore small regions which are most likely noise.
        if region_data["00"] < 100:
            continue

        found_regions.append(get_region_characteristics(region_data))

    return result_image, found_regions
