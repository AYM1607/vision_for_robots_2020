import math
from .core import Figure

def identify_region(trainer_params, potential_objects):
    """
    Matches an object being detected in real time with a specific type of object previously defined.
    Arguments:
        trainer_params {dictionary} - Training data that characterizes each region.
        potential_objects {array} - Objects to be matched with a region.
    Returns:
        Array -- Array of pairs representing the corresponding region and, if a long object, its angle, otherwise the angle is None.
    """
    objects = []
    for curr_obj in potential_objects:
        distance = math.inf
        region = Figure.UNKNOWN
        angle = None
        for figure in trainer_params:
            sigma_phi_1 = figure["sigma_phi_1"]
            sigma_phi_2 = figure["sigma_phi_2"]
            mean_phi_1 = figure["mean_phi_1"]
            mean_phi_2 = figure["mean_phi_2"]
            phi_1 = curr_obj["phi_1"]
            phi_2 = curr_obj["phi_2"]
            # If the object is inside the precalculated region.
            if in_range(sigma_phi_1 / 2, sigma_phi_2 / 2, mean_phi_1, mean_phi_2, phi_1, phi_2):
                # If the distance to that region is less than the others.
                if  get_distance( sigma_phi_1, sigma_phi_2, mean_phi_1, mean_phi_2, phi_1, phi_2) < distance:
                    region = figure["name"]
                    # If it is an object of type long, update the angle
                    if figure["name"] == Figure.LONG_1 or figure["name"] == Figure.LONG_2:
                        angle = curr_obj["theta"]
        objects.append((region, angle))
    return objects

def get_distance(sigma_phi_1, sigma_phi_2, mean_phi_1, mean_phi_2, phi_1, phi_2):
    """
    Returns the "distance" that an object has relative to a specific region in terms of phi_1 and phi_2 considering the standar deviation.
    Arguments:
        sigma_phi_1 {float} - Standard deviation in phi_1 axis.
        sigma_phi_2 {float} - Standard deviation in phi_2 axis.
        mean_phi_1 {float} - Mean or center of the region in phi_1 axis.
        mean_phi_2 {float} - Mean or center of the region in phi_2 axis.
        phi_1 {float} - Center of the object in phi_1 axis.
        phi_2 {float} - Center of the object in phi_2 axis.
    Returns:
        Float -- Distance between the center of the object and the center of the region.
    """
    return ( ( phi_1 - mean_phi_1 ) / sigma_phi_1 )**2 + ( ( phi_2 - mean_phi_2 ) / sigma_phi_2 )**2 

def in_range(delta_phi_1, delta_phi_2, mean_phi_1, mean_phi_2, phi_1, center_phi_2):
    """
    Determines if the object is inside a specific region in phi_1 and phi_2 axis.
    Arguments:
        sigma_phi_1 {float} - Standard deviation in phi_1 axis.
        sigma_phi_2 {float} - Standard deviation in phi_2 axis.
        mean_phi_1 {float} - Mean or center of the region in phi_1 axis.
        mean_phi_2 {float} - Mean or center of the region in phi_2 axis.
        phi_1 {float} - Center of the object in phi_1 axis.
        phi_2 {float} - Center of the object in phi_2 axis.
    Returns:
        Boolean -- True = the object falls inside the region. False = the objet is out the region.
    """
    return mean_phi_1 - delta_phi_1 <= phi_1 <= mean_phi_1 + delta_phi_1 and mean_phi_2 - delta_phi_2 <= center_phi_2 <= mean_phi_2 + delta_phi_2