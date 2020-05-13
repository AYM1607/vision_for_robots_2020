import cv2
import numpy as np
import argparse

seed_coordinates = None
width = None
height = None
visited = None
intensity_threshold = None


def mouse_callback(event, x, y, flags, params):
    global seed_coordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse positioned in {x},{y}")
        seed_coordinates = y, x


def get_neighbours(point, image):
    coordinate_differences = [(-1, 0), (0, -1), (1, 0), (0, 1)]

    valid_neighbours = []
    x, y, _ = point

    for x_offset, y_offset in coordinate_differences:
        new_x = x + x_offset
        new_y = y + y_offset

        if 0 <= new_x < height and 0 <= new_y < width:
            if visited[new_x][new_y]:
                continue
            else:
                valid_neighbours.append((new_x, new_y, image[new_x][new_y]))
                visited[new_x][new_y] = True

    return valid_neighbours


def region_expander(image):
    global intensity_threshold, seed_coordinates, visited
    result_image = np.full((height, width, 1), 255, np.uint8)
    pending_points = []
    region_area = 0

    x_seed, y_seed = seed_coordinates
    seed_intensity = image[x_seed][y_seed]

    pending_points.append((x_seed, y_seed, seed_intensity))

    while len(pending_points) > 0:
        current_point = pending_points.pop(0)
        region_area += 1

        for neighbour in get_neighbours(current_point, image):
            distance = abs(int(seed_intensity) - int(neighbour[2]))
            if distance <= intensity_threshold:
                result_image[neighbour[0]][neighbour[1]] = 0
                pending_points.append(neighbour)
    print(f"The area of the selected region is: {region_area}")

    return result_image


def main():
    global visited, width, height, intensity_threshold

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
    intensity_threshold = args.intensity_threshold

    # Read image in greyscale.
    input_image = cv2.imread(args.filename, 0)
    height = len(input_image)
    width = len(input_image[0])
    # Generate a visited list with the same dimensions as the original image.
    # The tuple on each field represents if the pixel was already visited and,
    # If it is part of the region that's being explored.
    visited = [[False for j in range(width)] for i in range(height)]

    cv2.namedWindow("Input image")
    cv2.setMouseCallback("Input image", mouse_callback, 0)
    cv2.imshow("Input image", input_image)
    cv2.waitKey()

    print("Starting algorithm")
    cv2.imshow("Input image", region_expander(input_image))

    cv2.waitKey()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
