import cv2
import json
import numpy as np
import math
import statistics


from os import path
from core_lib.core import (
    get_config_value,
    read_training_params,
    save_config_value,
    Direction,
    Figure,
    clear_terminal,
)
from core_lib.video_feed import VideoFeed
from core_lib.seeds import get_seeds
from core_lib.segmentation import region_expander
from core_lib.region_identifier import identify_region
from core_lib.drawing import draw_results_ui


def get_final_mapped_points(x, y):
    """
    Gets final coordinates given a list of free parking spices and real coordinates

    Returns:
    parking dict --- dict with the scaled data of a parking spot
    """
    free_parking_spaces = get_config_value("free_parking_spaces")

    for space in free_parking_spaces:
        corner_1 = space["corner_1"]
        corner_2 = space["corner_2"]
        if (x >= corner_1[0] and x <= corner_2[0]) and (
            y >= corner_1[1] and y <= corner_2[1]
        ):
            x_scale, y_scale = get_scaling_factor()

            x = int(round(space["algorithm_center"][0] * x_scale))
            y = int(round(space["algorithm_center"][1] * y_scale))
            return x, y


def save_final_mapped_points(event, x, y, flags, param):
    """
    Click callback to map final coordinates.
    """
    if event == cv2.EVENT_LBUTTONDOWN:
        coords = get_final_mapped_points(x, y)
        if coords:
            clear_terminal()
            print(
                "ESTACIONAMIENTO LIBRE, presione 'q' para continuar o seleccione uno nuevo"
            )
            print(coords)

            save_config_value("initial_coordinates", coords)
        else:
            clear_terminal()
            print("NO ES ESTACIONAMIENTO, INTENTE DE NUEVO")


def get_final_parking_space_coordinates():
    """
    Routine to get final parking space coordinates given a click.
    """
    print("CONFIGURACION DE PUNTO DE LLEGADA")
    print("Hacer click en el espacio libre de estacionamiento que sea el punto final.")
    print("Presiona 'q' para finalizar.")

    input_image = cv2.imread(
        path.join(path.dirname(__file__), "media", "parking_base.jpg")
    )

    cv2.namedWindow("input image")
    cv2.setMouseCallback("input image", save_final_mapped_points)

    while True:
        initial_coordinates = get_config_value("initial_coordinates")

        cv2.imshow("input image", input_image)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cv2.destroyAllWindows()
    return get_config_value("initial_coordinates")


def get_initial_coordinates_and_direction():
    """
    Gets initial coordinates and direction based the initial quadrant.

    Returns:
    tuple --- the order is center coordinates and initial direction
    """
    initial_quadrant = get_config_value("initial_quadrant")
    initial_direction = get_config_value("initial_direction")

    parking_entrances = get_config_value("parking_entrances")

    x_scale, y_scale = get_scaling_factor()

    for entrance in parking_entrances:
        if entrance["quadrant"] == initial_quadrant:
            center = entrance["center_coordinates"]
            return (
                (int(round(center[0] * x_scale)), int(round(center[1] * y_scale))),
                initial_direction,
            )

    return None


def get_initial_quadrant_and_direction(intensity_threshold=35):
    """
    Gets initial quadrant and direction based on the rules of the project.
    TODO(eskr): Esplain rules
    """

    # Create 2 named windows for the input and output image.
    cv2.namedWindow("Input")

    training_params = read_training_params()

    print("CONFIGURACION PUNTO DE PARTIDA")
    print("Mostrar un objeto compacto y uno largo por favor ...")
    print("Presiona 'q' para finalizar.")

    quadrant = None
    direction = None

    with VideoFeed(camera_index=0, width=450) as feed:
        while True:
            _, image = feed.read()
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            seeds = get_seeds(image)

            _, found_regions = region_expander(gray_image, seeds, intensity_threshold)
            detected_figures = identify_region(training_params, found_regions)
            draw_results_ui(detected_figures)

            figures_list = []
            new_quadrant = None
            new_direction = None
            angle = None

            for figure, figure_angle in detected_figures:
                figures_list.append(figure)
                if figure_angle:
                    angle = figure_angle

            if Figure.COMPACT_1 in figures_list:
                if Figure.LONG_1 in figures_list:
                    new_quadrant = Direction.NORTH_WEST
                    if (0 <= angle <= math.pi / 2) or (
                        -math.pi <= angle <= -math.pi / 2
                    ):
                        new_direction = Direction.EAST
                    else:
                        new_direction = Direction.SOUTH
                elif Figure.LONG_2 in figures_list:
                    new_quadrant = Direction.NORTH_EAST
                    if (0 <= angle <= math.pi / 2) or (
                        -math.pi <= angle <= -math.pi / 2
                    ):
                        new_direction = Direction.SOUTH
                    else:
                        new_direction = Direction.WEST
            elif Figure.COMPACT_2 in figures_list:
                if Figure.LONG_1 in figures_list:
                    new_quadrant = Direction.SOUTH_WEST
                    if (0 <= angle <= math.pi / 2) or (
                        -math.pi <= angle <= -math.pi / 2
                    ):
                        new_direction = Direction.NORTH
                    else:
                        new_direction = Direction.EAST
                elif Figure.LONG_2 in figures_list:
                    new_quadrant = Direction.SOUTH_EAST
                    if (0 <= angle <= math.pi / 2) or (
                        -math.pi <= angle <= -math.pi / 2
                    ):
                        new_direction = Direction.WEST
                    else:
                        new_direction = Direction.NORTH

            if new_direction not in (None, direction):
                direction = new_direction
                clear_terminal()
                print("Cuadrante inicial: ", new_quadrant.name)
                print("Direccion inicial: ", new_direction.name)

            if new_quadrant not in (None, quadrant):
                quadrant = new_quadrant
                clear_terminal()
                print("Cuadrante inicial: ", new_quadrant.name)
                print("Direccion inicial: ", new_direction.name)

            # for region in found_regions:
            #     draw_region_characteristics(result_image, region)

            cv2.imshow("Input", image)
            # cv2.imshow("Output", result_image)

            # End the loop when "q" is pressed.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cv2.destroyAllWindows()

    print("Quadrante: ", quadrant.name)
    print("Direccion: ", direction.name)

    save_config_value("initial_quadrant", quadrant.value)
    save_config_value("initial_direction", direction.value)

    return quadrant, direction


def get_parking_poles_structure():
    """
    Returns a representation of the free space in the parking space.
    The returned structure represents free space as 0 and space occupied
    by an obstacle as -1.

    Returns:
        np.array
    """
    mesh = cv2.imread(path.join(path.dirname(__file__), "media", "route_planner.jpg"))
    poles_structure = np.full((len(mesh), len(mesh[0])), -1)

    for i in range(0, len(mesh)):
        for j in range(0, len(mesh[0])):
            if mesh[i][j][0] < 40 and mesh[i][j][1] < 40 and mesh[i][j][2] < 40:
                poles_structure[i][j] = 0

    return poles_structure


def get_scaling_factor():
    """
    Indicates by how much the parking poles structure was
    scaled with respect to the original image.

    Returns:
        tuple --- the order is x_scale then y_scale
    """

    return get_config_value("x_scale"), get_config_value("y_scale")


def get_available_spots_regions():
    """
    Returns the regions on which there are available spots.
    Each spot is a dictionary that contains the following keys:
     - corner_1
     - corner_2
     - real_center
     - algorithm_center

    Each one of the keys contains a 2 element array that represents a coordinate.

    Returns:
        tuple --- a 2 element tuple, each element is an array of spots.
            The first element contains the coordinates
            based on the original image dimensions, the second elements contains the
            coordinates scaled with the same factor as the poles structure.
    """

    return (
        get_config_value("free_parking_spaces"),
        get_config_value("free_parking_spaces_scaled"),
    )
