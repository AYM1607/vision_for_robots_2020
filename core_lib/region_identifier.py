import math
import json
from core import Figure

threshold = 0.7

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
        region = "5"
        angle = None
        phi_1 = curr_obj["phi_1"]
        phi_2 = curr_obj["phi_2"]
        # print("phi1 = ", phi_1, "\tphi2 = ", phi_2, "\n")
        for figure in trainer_params:
            sigma_phi_1 = figure["sigma_phi_1"]
            sigma_phi_2 = figure["sigma_phi_2"]
            mean_phi_1 = figure["mean_phi_1"]
            mean_phi_2 = figure["mean_phi_2"]
            ind_distance = get_distance(sigma_phi_1, sigma_phi_2, mean_phi_1, mean_phi_2, phi_1, phi_2)
            # print("object = ", figure["object_id"], "\tphi1 = ", mean_phi_1, "\tphi2 = ", mean_phi_2, "\tsigma_phi1 = ", sigma_phi_1, "\tsigma_phi2 = ", sigma_phi_2, "\tdist = ", ind_distance, "\n")
            if  in_range(mean_phi_1, mean_phi_2, phi_1, phi_2) and ind_distance < distance:
                distance = ind_distance
                region = Figure(int(figure["object_id"]))
                # If it is an object of type long, update the angle
                if region == Figure.LONG_1 or region == Figure.LONG_2:
                    angle = curr_obj["theta"]
                else:
                    angle = None
        objects.append((region, angle))
    return objects

def in_range(mean_phi_1, mean_phi_2, phi_1, phi_2):
    """
    Determines if the object is inside a specific region in phi_1 and phi_2 axis.
    Arguments:
        mean_phi_1 {float} - Mean or center of the region in phi_1 axis.
        mean_phi_2 {float} - Mean or center of the region in phi_2 axis.
        phi_1 {float} - Center of the object in phi_1 axis.
        phi_2 {float} - Center of the object in phi_2 axis.
    Returns:
        Boolean -- True = the object falls inside the region. False = the objet is out the region.
    """
    return mean_phi_1 - threshold <= phi_1 <= mean_phi_1 + threshold and mean_phi_2 - threshold <= phi_2 <= mean_phi_2 + threshold


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
    # return ( phi_1 - mean_phi_1 )**2 + ( phi_2 - mean_phi_2 )**2 