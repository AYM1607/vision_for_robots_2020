import cv2
import json
from enum import Enum
from os import path, system, name as os_name


class Figure(Enum):
    LONG_1 = 1
    LONG_2 = 2
    COMPACT_1 = 3
    COMPACT_2 = 4
    UNKNOWN = 5


class Direction(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4
    NORTH_EAST = 5
    NORTH_WEST = 6
    SOUTH_EAST = 7
    SOUTH_WEST = 8


def clear_terminal():
    """
    Clears all the text on the terminal.
    """
    system("cls" if os_name == "nt" else "clear")


def read_training_params():

    """
    Gets the training params from the file.

    Returns:
        Array --- all training params.
    """

    with open(
        path.join(path.dirname(__file__), "config", "training_params.json")
    ) as file:
        return json.load(file)


def get_config():
    """
    Gets the whole config file.

    Returns:
        dictionary --- all config values.
    """

    with open(path.join(path.dirname(__file__), "config", "config.json")) as file:
        return json.load(file)


def get_config_value(key):
    """
    Gets a single value from the configuration file.

    Parameters:
        key {any} --- the name of the value to retrieve

    Returns:
        any --- the value stored on config or None if it doesn't exist.
    """

    return get_config().get(key)


def save_config(config_dict):
    """
    Saves a dictionary as the new config file.

    Parameters:
        config_dict {dictionary} --- The data to be saved as the new config.
    """

    with open(path.join(path.dirname(__file__), "config", "config.json"), "w") as file:
        json.dump(config_dict, file)


def save_config_value(key, value):
    """
    Save a single value to the existing config file.

    Parameters:
        key {any} --- the name of the value to be stored.
        value {any} --- the value to be stored under the key.
    """

    config = get_config()
    config[key] = value
    save_config(config)
