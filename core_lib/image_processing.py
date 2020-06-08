import math
import cv2
import numpy as np


def filter_by_color(image, color, threshold=30):
    """
    Filters an image by color.
    The pixels that match the color are black on the result image and white otherwise.
    """
    height = len(image)
    width = len(image[0])

    new_image = image.copy()

    for y in range(height):
        for x in range(width):
            point = image[y][x]
            if (
                color[0] - threshold <= point[0] <= color[0] + threshold
                and color[1] - threshold <= point[1] <= color[1] + threshold
                and color[2] - threshold <= point[2] <= color[2] + threshold
            ):
                new_image[y][x] = (0, 0, 0)
            else:
                new_image[y][x] = (255, 255, 255)

    return new_image


def generate_circular_kernel(diameter):
    """
    Generate a ciruclar given its diameter.

    Parameters:
        diameter {integer}

    Returns:
        np.array
    """

    kernel = np.zeros((diameter, diameter), np.uint8)

    center = int(math.floor(diameter / 2))
    radius = center  # diameter / 2

    for i in range(diameter):
        for j in range(diameter):
            if (center - i) ** 2 + (center - j) ** 2 <= radius ** 2:
                kernel[i][j] = 1

    return kernel


def dilate(image, kernel_size=3):
    """
    Dilates and image with a circular kernel.

    Parameters:
        image {np.array} --- the image to be dilated.
        kernel_size {integer} --- the size of the kernel to be used.

    Returns:
        np.array --- the dilated image.
    """

    if kernel_size < 1 or kernel_size % 2 == 0:
        raise Exception("The kernel size must be odd and greater than 0")

    kernel = generate_circular_kernel(kernel_size)
    return cv2.dilate(image, kernel)
