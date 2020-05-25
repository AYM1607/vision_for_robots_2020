import json


def get_seeds_helper(
    image,
    lower_height_limit,
    upper_height_limit,
    data,
    count_to_update,
    COLOR_1,
    COLOR_2,
):
    """
    Get the possible seeds of an image based on the 2 colors defined on the global scope.
    The name of the colors must be COLOR_1 and COLOR_2 and be in BGR order.
    Analyzes the row in the middle of lower_height_limit and upper_height_limit and
    recursively calls the same function for the images that the middle cuts in half.
    In order to keep the algorithm fast, it stops at 20 iterations and considers there's no
    seeds in this image, it also starts when the 2 seeds are found.

    Arguments:
        image {np.array} -- The image to traverse
        lower_height_limit {integer}
        upper_height_limit {integer}
        data {dictionary} -- Pre-existing data, can contain:
            seed_1: The coordiantes for the seed_1
            seed_2: The coordiantes for seed_2
            count: The total iterations counts

    Returns:
        Dictionary -- The updated data dictionary
    """

    if ("seed_1" in data and "seed_2" in data) or data[count_to_update] == 10:
        return None

    middle_height = int(
        lower_height_limit + (upper_height_limit - lower_height_limit) / 2
    )

    # TODO: Get rid of this repeated code.
    for x in range(0, len(image[0])):
        pixel = image[middle_height][x]
        if (
            COLOR_1[0] - 20 <= pixel[0] <= COLOR_1[0] + 20
            and COLOR_1[1] - 20 <= pixel[1] <= COLOR_1[1] + 20
            and COLOR_1[2] - 20 <= pixel[2] <= COLOR_1[2] + 20
        ):
            data["seed_1"] = (x, middle_height)

        if (
            COLOR_2[0] - 20 <= pixel[0] <= COLOR_2[0] + 20
            and COLOR_2[1] - 20 <= pixel[1] <= COLOR_2[1] + 20
            and COLOR_2[2] - 20 <= pixel[2] <= COLOR_2[2] + 20
        ):
            data["seed_2"] = (x, middle_height)

    data[count_to_update] += 1

    get_seeds_helper(
        image,
        lower_height_limit,
        middle_height,
        data,
        count_to_update,
        COLOR_1,
        COLOR_2,
    )
    get_seeds_helper(
        image,
        middle_height,
        upper_height_limit,
        data,
        count_to_update,
        COLOR_1,
        COLOR_2,
    )


def get_seeds(image):
    """
    Gets the seeds of an image.

    Arguments:
        image {np.array} -- The image to traverse.
    """

    # Get colors from configuration file
    try:
        with open("colors.json") as json_file:
            colors = json.load(json_file)
    except:
        raise Exception("FAILURE: no colors.json configuration file, calibrate first")

    if "COLOR_1" in colors.keys():
        COLOR_1 = colors["COLOR_1"]
    else:
        raise Exception("FAILURE: configuration file is missing COLOR_1")

    if "COLOR_2" in colors.keys():
        COLOR_2 = colors["COLOR_2"]
    else:
        raise Exception("FAILURE: configuration file is missing COLOR_2")

    data = {"upper_count": 0, "lower_count": 0}

    middle_height = int(len(image) / 2)

    for x in range(0, len(image[0])):
        pixel = image[middle_height][x]
        if (
            COLOR_1[0] - 20 <= pixel[0] <= COLOR_1[0] + 20
            and COLOR_1[1] - 20 <= pixel[1] <= COLOR_1[1] + 20
            and COLOR_1[2] - 20 <= pixel[2] <= COLOR_1[2] + 20
        ):
            data["seed_1"] = (x, middle_height)

        if (
            COLOR_2[0] - 20 <= pixel[0] <= COLOR_2[0] + 20
            and COLOR_2[1] - 20 <= pixel[1] <= COLOR_2[1] + 20
            and COLOR_2[2] - 20 <= pixel[2] <= COLOR_2[2] + 20
        ):
            data["seed_2"] = (x, middle_height)

    get_seeds_helper(image, 0, middle_height, data, "lower_count", COLOR_1, COLOR_2)
    get_seeds_helper(
        image, middle_height, len(image), data, "upper_count", COLOR_1, COLOR_2
    )

    result = []

    if "seed_1" in data:
        result.append(data["seed_1"])
    if "seed_2" in data:
        result.append(data["seed_2"])

    return result
