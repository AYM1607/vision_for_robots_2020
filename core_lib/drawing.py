"""
Util drawing functions.
"""
import math
import cv2


def draw_region_characteristics(image, characteristics):
    """
    Draws the centorid and the orientation of a region given
    its characteristics.
    """

    center = characteristics["x_center"], characteristics["y_center"]

    # Draw the centroid.
    cv2.circle(image, center, 2, (0, 255, 0), 4)

    theta = characteristics["theta"]

    # Get the coordinates for the 2 ends of the line.
    hyp = (characteristics["height"] / 2) / math.sin(theta)
    x_1 = int(characteristics["x_center"] + (hyp * math.cos(theta)))
    y_1 = int(characteristics["y_center"] + characteristics["height"] / 2)
    # Mirror the angle to get the opposite coordinate.
    theta = theta + math.pi if theta < 0 else theta - math.pi
    x_2 = int(characteristics["x_center"] + (hyp * math.cos(theta)))
    y_2 = int(characteristics["y_center"] - characteristics["height"] / 2)

    cv2.line(image, (x_1, y_1), (x_2, y_2), (0, 255, 0), 2)
