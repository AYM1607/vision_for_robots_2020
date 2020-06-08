"""
Util drawing functions.
"""
import math
import cv2
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

from core_lib.core import Figure

training_dataset = None


def draw_diameter(image, center, angle, radius):
    """
    Draw the diameter of a circle given its center, radius and
    the angle at which the diameter is to be drawn.
    """
    x_center, y_center = center

    x_1 = int(x_center + (radius * math.cos(angle)))
    y_1 = int(y_center + (radius * math.sin(angle)))

    angle = angle + math.pi if angle < 0 else angle - math.pi

    x_2 = int(x_center + (radius * math.cos(angle)))
    y_2 = int(y_center + (radius * math.sin(angle)))

    cv2.line(image, (x_1, y_1), (x_2, y_2), (0, 255, 0), 2)


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

    draw_diameter(image, center, theta, hyp)


def draw_filled_semicircle_from_figures(image, figures_list, center, radius):
    """
    Draws a filled semicirle in the given image based on the provided figures.
    The quarter to be filled will depend on which figures are passed.
    For the method to draw something at least one compact figure and one long
    figure must be provided.

    Arguments:
        image {np.array} -- The image to draw the semicirle on.
        figures_list {List<Figure>} --- A list of `Figure` instances.
        center {Tuple<integer>} --- Coordiantes of the center.
        radius {integer} --- Radius of the semicircle.
    """
    start_angle = 0
    end_angle = 0

    if Figure.COMPACT_1 in figures_list:
        if Figure.LONG_1 in figures_list:
            start_angle = 180
            end_angle = 270
        elif Figure.LONG_2 in figures_list:
            start_angle = 270
            end_angle = 360
    elif Figure.COMPACT_2 in figures_list:
        if Figure.LONG_1 in figures_list:
            start_angle = 90
            end_angle = 180
        elif Figure.LONG_2 in figures_list:
            start_angle = 0
            end_angle = 90

    cv2.ellipse(
        image,
        center,
        (radius, radius),
        0,
        start_angle,
        end_angle,
        (255, 255, 255),
        cv2.FILLED,
    )


def draw_training_space(training_params, found_regions):
    global training_dataset

    if not training_dataset:
        training_dataset = []
        for training_object in training_params:
            x = []
            y = []
            for point in training_object["points"]:
                x.append(point["phi_1"])
                y.append(point["phi_2"])
            training_dataset.append((x, y))
        plt.scatter([], [])
        plt.show(False)

    colors = ["b", "g", "r", "c", "m"]

    plt.cla()
    for i, dataset in enumerate(training_dataset):
        x, y = dataset
        plt.scatter(x, y, color=colors[i])

    for region in found_regions:
        plt.scatter([region["phi_1"]], [region["phi_2"]], color=colors[-1])

    plt.draw()


def draw_results_ui(detected_figures):
    """
    Draws the appropriate UI to represent the detected figures.

    Arguments:
        detected_figures { list } --- Each element is a tuple that
            contains a `Figure` and its angle.
    """

    figures_list = []
    angle = None
    result_circle_radius = 80

    for figure, figure_angle in detected_figures:
        figures_list.append(figure)
        if figure_angle:
            angle = figure_angle

    # Make sure the window for the results exists.
    cv2.namedWindow("Results UI")

    results_image = np.zeros((300, 300, 3), np.uint8)

    # Draw main UI.
    cv2.circle(results_image, (150, 150), result_circle_radius, (255, 255, 255), 2)
    cv2.line(results_image, (150, 50), (150, 250), (255, 255, 255), 2)
    cv2.line(results_image, (50, 150), (250, 150), (255, 255, 255), 2)

    cv2.putText(
        results_image, "L1", (5, 160), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255)
    )
    cv2.putText(
        results_image, "L2", (260, 160), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255)
    )
    cv2.putText(
        results_image, "C1", (130, 30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255)
    )
    cv2.putText(
        results_image, "C2", (130, 284), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255)
    )

    draw_filled_semicircle_from_figures(
        results_image, figures_list, (150, 150), result_circle_radius
    )

    if angle:
        # Draw the orientation of the long figure if found
        draw_diameter(results_image, (150, 150), angle, 100)

    cv2.imshow("Results UI", results_image)


def draw_parkin_slot(image, slot):
    """
    Draws a parking slot on the provided image.
    """
    cv2.rectangle(image, slot["corner_1"], slot["corner_2"], (0, 0, 255), 2)
    cv2.circle(image, slot["real_center"], 2, (255, 0, 0), 4)
    cv2.circle(image, slot["algorithm_center"], 2, (0, 255, 0), 4)
